from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.baselines import (
    build_prediction_rows,
    compute_eigenslang_direction,
    compute_mean_offset,
    eigenslang_retrieval,
    embed_split,
    evaluate_rankings,
    fit_backend,
    gold_label,
    mean_offset_retrieval,
    raw_retrieval,
    tune_alpha,
    validate_representation_mode,
)
from src.dataset import load_examples, save_splits, split_examples
from src.embeddings import create_backend
from src.evaluate import write_metrics_table, write_prediction_table


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run retrieval baselines for the Eigenslang project.")
    parser.add_argument(
        "--input",
        default="data/processed/slang_examples_clean.csv",
        help="Path to the dataset CSV.",
    )
    parser.add_argument(
        "--splits-dir",
        default="data/splits",
        help="Directory to write train/validation/test CSV files.",
    )
    parser.add_argument(
        "--results-dir",
        default="results/tables",
        help="Directory to write metrics and prediction tables.",
    )
    parser.add_argument(
        "--backend",
        default="tfidf",
        choices=["tfidf", "sentence-transformer"],
        help="Embedding backend to use.",
    )
    parser.add_argument(
        "--model",
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Model name for sentence-transformer backend.",
    )
    parser.add_argument(
        "--representation-mode",
        default="contextual_sentence",
        choices=["contextual_sentence", "term_paraphrase"],
        help="How to construct slang and neutral embeddings.",
    )
    return parser.parse_args()


def slugify_backend_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def main() -> None:
    args = parse_args()
    validate_representation_mode(args.representation_mode)
    dataset = load_examples(args.input)
    split = split_examples(dataset)
    save_splits(split, args.splits_dir)

    candidate_labels = sorted(
        {
            gold_label(row, args.representation_mode)
            for row in dataset.to_dict("records")
        }
    )
    backend = create_backend(args.backend, args.model)
    backend = fit_backend(split.train, candidate_labels, backend, args.representation_mode)

    train_artifacts = embed_split(split.train, candidate_labels, backend, args.representation_mode)
    validation_artifacts = embed_split(split.validation, candidate_labels, backend, args.representation_mode)
    test_artifacts = embed_split(split.test, candidate_labels, backend, args.representation_mode)

    mean_offset = compute_mean_offset(train_artifacts)
    eigenslang_direction = compute_eigenslang_direction(train_artifacts)

    best_mean_alpha = tune_alpha(
        validation_df=split.validation,
        validation_artifacts=validation_artifacts,
        retrieval_fn=mean_offset_retrieval,
        transform=mean_offset,
    )
    best_eigenslang_alpha = tune_alpha(
        validation_df=split.validation,
        validation_artifacts=validation_artifacts,
        retrieval_fn=eigenslang_retrieval,
        transform=eigenslang_direction,
    )

    split_map = {
        "train": (split.train, train_artifacts),
        "validation": (split.validation, validation_artifacts),
        "test": (split.test, test_artifacts),
    }

    metrics_rows: list[dict[str, object]] = []
    prediction_rows: list[dict[str, object]] = []

    for split_name, (split_df, artifacts) in split_map.items():
        raw_predictions = raw_retrieval(artifacts)
        mean_predictions = mean_offset_retrieval(artifacts, mean_offset, best_mean_alpha)
        eigenslang_predictions = eigenslang_retrieval(
            artifacts,
            eigenslang_direction,
            best_eigenslang_alpha,
        )

        for method_name, predictions, alpha in [
            ("raw", raw_predictions, None),
            ("mean_offset", mean_predictions, best_mean_alpha),
            ("eigenslang_pca", eigenslang_predictions, best_eigenslang_alpha),
        ]:
            metrics = evaluate_rankings(
                split_df,
                predictions,
                representation_mode=args.representation_mode,
            )
            row = {
                "split": split_name,
                "method": method_name,
                "backend": backend.name,
                "representation_mode": args.representation_mode,
                "top_1_accuracy": round(metrics["top_1_accuracy"], 4),
                "top_3_accuracy": round(metrics["top_3_accuracy"], 4),
            }
            if alpha is not None:
                row["alpha"] = alpha
            metrics_rows.append(row)

            prediction_rows.extend(
                build_prediction_rows(
                    split_name=split_name,
                    method=method_name,
                    split_df=split_df,
                    ranked_predictions=predictions,
                    representation_mode=args.representation_mode,
                )
            )

    results_dir = Path(args.results_dir)
    backend_slug = slugify_backend_name(backend.name)
    mode_slug = slugify_backend_name(args.representation_mode)
    metrics_path = results_dir / f"baseline_metrics_{backend_slug}_{mode_slug}.csv"
    predictions_path = results_dir / f"baseline_predictions_{backend_slug}_{mode_slug}.csv"
    write_metrics_table(metrics_rows, metrics_path)
    write_prediction_table(prediction_rows, predictions_path)

    print("Saved splits to:", Path(args.splits_dir).resolve())
    print("Saved metrics to:", metrics_path.resolve())
    print("Saved predictions to:", predictions_path.resolve())
    print(f"Backend: {backend.name}")
    print(f"Representation mode: {args.representation_mode}")
    print(f"Best mean-offset alpha: {best_mean_alpha}")
    print(f"Best eigenslang alpha: {best_eigenslang_alpha}")


if __name__ == "__main__":
    main()
