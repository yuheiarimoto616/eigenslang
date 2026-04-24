from __future__ import annotations

import os
from pathlib import Path

import pandas as pd


RESULTS_DIR = Path("results/tables")
FIGURES_DIR = Path("results/figures")
MPLCONFIGDIR = Path("results/.matplotlib")


def load_metrics(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def main() -> None:
    MPLCONFIGDIR.mkdir(parents=True, exist_ok=True)
    os.environ["MPLCONFIGDIR"] = str(MPLCONFIGDIR.resolve())

    import matplotlib.pyplot as plt

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    sentence_transformer_files = [
        RESULTS_DIR / "baseline_metrics_sentence_transformers_all_minilm_l6_v2_term_paraphrase_all_candidates.csv",
        RESULTS_DIR / "baseline_metrics_sentence_transformers_all_minilm_l6_v2_term_paraphrase_category_candidates.csv",
        RESULTS_DIR / "baseline_metrics_sentence_transformers_all_minilm_l6_v2_term_paraphrase_balanced_distractors.csv",
        RESULTS_DIR / "baseline_metrics_sentence_transformers_all_minilm_l6_v2_contextual_sentence_all_candidates.csv",
        RESULTS_DIR / "baseline_metrics_sentence_transformers_all_minilm_l6_v2_contextual_sentence_category_candidates.csv",
        RESULTS_DIR / "baseline_metrics_sentence_transformers_all_minilm_l6_v2_contextual_sentence_balanced_distractors.csv",
    ]

    tfidf_files = [
        RESULTS_DIR / "baseline_metrics_tfidf_contextual_sentence.csv",
        RESULTS_DIR / "baseline_metrics_tfidf_term_paraphrase.csv",
        RESULTS_DIR / "baseline_metrics_tfidf_term_paraphrase_category_candidates.csv",
        RESULTS_DIR / "baseline_metrics_tfidf_term_paraphrase_balanced_distractors.csv",
    ]

    frames = [load_metrics(str(path)) for path in sentence_transformer_files + tfidf_files if path.exists()]
    all_metrics = pd.concat(frames, ignore_index=True)

    test_metrics = all_metrics[all_metrics["split"] == "test"].copy()

    # Compact report table: sentence-transformer settings plus TF-IDF all-candidate baselines.
    report_table = test_metrics[
        (
            test_metrics["backend"].eq("sentence-transformers/all-MiniLM-L6-v2")
            & test_metrics["candidate_mode"].isin(["all_candidates", "category_candidates", "balanced_distractors"])
        )
        |
        (
            test_metrics["backend"].eq("tfidf")
            & test_metrics["candidate_mode"].fillna("all_candidates").eq("all_candidates")
        )
    ].copy()

    report_table["candidate_mode"] = report_table["candidate_mode"].fillna("all_candidates")
    report_table = report_table.sort_values(
        by=["backend", "representation_mode", "candidate_mode", "method"]
    )

    report_table_path = RESULTS_DIR / "report_summary_test_metrics.csv"
    report_table.to_csv(report_table_path, index=False)

    # Figure: sentence-transformer test Top-1 by candidate mode and representation.
    st_test = test_metrics[
        test_metrics["backend"] == "sentence-transformers/all-MiniLM-L6-v2"
    ].copy()
    mode_order = ["all_candidates", "category_candidates", "balanced_distractors"]
    method_order = ["raw", "mean_offset", "eigenslang_pca"]
    rep_order = ["term_paraphrase", "contextual_sentence"]
    display_names = {
        "raw": "Raw",
        "mean_offset": "Mean Offset",
        "eigenslang_pca": "PCA Eigenslang",
        "term_paraphrase": "Term/Paraphrase",
        "contextual_sentence": "Contextual Sentence",
    }

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    colors = {
        "raw": "#1b4965",
        "mean_offset": "#5fa8d3",
        "eigenslang_pca": "#ca6702",
    }

    for ax, representation_mode in zip(axes, rep_order):
        subset = st_test[st_test["representation_mode"] == representation_mode].copy()
        x = range(len(mode_order))
        width = 0.24

        for index, method in enumerate(method_order):
            method_subset = subset[subset["method"] == method].set_index("candidate_mode")
            values = [method_subset.loc[mode, "top_1_accuracy"] for mode in mode_order]
            offsets = [value + (index - 1) * width for value in x]
            ax.bar(offsets, values, width=width, color=colors[method], label=display_names[method])

        ax.set_xticks(list(x))
        ax.set_xticklabels(["All", "Category", "Balanced"])
        ax.set_title(display_names[representation_mode])
        ax.set_xlabel("Candidate Set")
        ax.set_ylim(0.0, 0.5)
        ax.grid(axis="y", alpha=0.25)

    axes[0].set_ylabel("Test Top-1 Accuracy")
    axes[1].legend(frameon=False, loc="upper right")
    fig.suptitle("Sentence-Transformer Retrieval Across Candidate Settings")
    fig.tight_layout()

    figure_path = FIGURES_DIR / "candidate_mode_comparison_top1.png"
    fig.savefig(figure_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"Wrote summary table to {report_table_path.resolve()}")
    print(f"Wrote figure to {figure_path.resolve()}")


if __name__ == "__main__":
    main()
