from __future__ import annotations

from dataclasses import dataclass
import re

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity

from src.embeddings import EmbeddingBackend


def build_query_text(row: pd.Series) -> str:
    return row["context_sentence"]


def build_candidate_text(context_sentence: str, slang_term: str, paraphrase: str) -> str:
    pattern = re.compile(re.escape(slang_term), flags=re.IGNORECASE)
    replaced = pattern.sub(paraphrase, context_sentence, count=1)
    if replaced == context_sentence:
        return f"{context_sentence} meaning: {paraphrase}"
    return replaced


@dataclass
class RetrievalArtifacts:
    backend: EmbeddingBackend
    candidate_labels: list[str]
    examples: list[dict[str, str]]
    query_matrix: np.ndarray
    target_matrix: np.ndarray


def fit_backend(train_df: pd.DataFrame, candidate_labels: list[str], backend: EmbeddingBackend) -> EmbeddingBackend:
    train_texts = train_df.apply(build_query_text, axis=1).tolist()
    candidate_texts: list[str] = []
    for row in train_df.to_dict("records"):
        for label in candidate_labels:
            candidate_texts.append(
                build_candidate_text(
                    context_sentence=row["context_sentence"],
                    slang_term=row["slang_term"],
                    paraphrase=label,
                )
            )

    backend.fit(train_texts + candidate_texts)
    return backend


def embed_split(
    split_df: pd.DataFrame,
    candidate_labels: list[str],
    backend: EmbeddingBackend,
) -> RetrievalArtifacts:
    query_texts = split_df.apply(build_query_text, axis=1).tolist()
    target_texts = [
        build_candidate_text(
            context_sentence=row["context_sentence"],
            slang_term=row["slang_term"],
            paraphrase=row["neutral_paraphrase"],
        )
        for row in split_df.to_dict("records")
    ]

    query_matrix = backend.encode(query_texts)
    target_matrix = backend.encode(target_texts)

    return RetrievalArtifacts(
        backend=backend,
        candidate_labels=candidate_labels,
        examples=split_df.to_dict("records"),
        query_matrix=query_matrix,
        target_matrix=target_matrix,
    )


def _candidate_matrix_for_example(
    example: dict[str, str],
    candidate_labels: list[str],
    backend: EmbeddingBackend,
) -> np.ndarray:
    candidate_texts = [
        build_candidate_text(
            context_sentence=example["context_sentence"],
            slang_term=example["slang_term"],
            paraphrase=label,
        )
        for label in candidate_labels
    ]
    return backend.encode(candidate_texts)


def _rank_candidates(
    query_matrix: np.ndarray,
    artifacts: RetrievalArtifacts,
) -> list[list[str]]:
    ranked_predictions: list[list[str]] = []
    for query_vector, example in zip(query_matrix, artifacts.examples):
        candidate_matrix = _candidate_matrix_for_example(
            example=example,
            candidate_labels=artifacts.candidate_labels,
            backend=artifacts.backend,
        )
        scores = cosine_similarity(query_vector.reshape(1, -1), candidate_matrix)[0]
        ranked_indices = np.argsort(-scores)
        ranked_predictions.append([artifacts.candidate_labels[index] for index in ranked_indices])
    return ranked_predictions


def raw_retrieval(artifacts: RetrievalArtifacts) -> list[list[str]]:
    return _rank_candidates(query_matrix=artifacts.query_matrix, artifacts=artifacts)


def compute_mean_offset(train_artifacts: RetrievalArtifacts) -> np.ndarray:
    differences = train_artifacts.query_matrix - train_artifacts.target_matrix
    return differences.mean(axis=0)


def mean_offset_retrieval(
    artifacts: RetrievalArtifacts,
    offset: np.ndarray,
    alpha: float,
) -> list[list[str]]:
    adjusted_queries = artifacts.query_matrix - (alpha * offset)
    return _rank_candidates(query_matrix=adjusted_queries, artifacts=artifacts)


def compute_eigenslang_direction(train_artifacts: RetrievalArtifacts) -> np.ndarray:
    differences = train_artifacts.query_matrix - train_artifacts.target_matrix
    if len(differences) < 2:
        return differences.mean(axis=0)

    pca = PCA(n_components=1, random_state=440)
    pca.fit(differences)
    return pca.components_[0]


def eigenslang_retrieval(
    artifacts: RetrievalArtifacts,
    direction: np.ndarray,
    alpha: float,
) -> list[list[str]]:
    adjusted_queries = artifacts.query_matrix - (alpha * direction)
    return _rank_candidates(query_matrix=adjusted_queries, artifacts=artifacts)


def evaluate_rankings(
    split_df: pd.DataFrame,
    ranked_predictions: list[list[str]],
    top_k_values: tuple[int, ...] = (1, 3),
) -> dict[str, float]:
    gold = split_df["neutral_paraphrase"].tolist()
    metrics: dict[str, float] = {}

    for top_k in top_k_values:
        correct = 0
        for gold_label, predictions in zip(gold, ranked_predictions):
            if gold_label in predictions[:top_k]:
                correct += 1
        metrics[f"top_{top_k}_accuracy"] = correct / len(gold)

    return metrics


def tune_alpha(
    validation_df: pd.DataFrame,
    validation_artifacts: RetrievalArtifacts,
    retrieval_fn,
    transform: np.ndarray,
    alpha_grid: list[float] | None = None,
) -> float:
    if alpha_grid is None:
        alpha_grid = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]

    best_alpha = alpha_grid[0]
    best_score = -1.0

    for alpha in alpha_grid:
        predictions = retrieval_fn(validation_artifacts, transform, alpha)
        metrics = evaluate_rankings(validation_df, predictions, top_k_values=(1,))
        score = metrics["top_1_accuracy"]
        if score > best_score:
            best_score = score
            best_alpha = alpha

    return best_alpha


def build_prediction_rows(
    split_name: str,
    method: str,
    split_df: pd.DataFrame,
    ranked_predictions: list[list[str]],
    top_n: int = 3,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for example, predictions in zip(split_df.to_dict("records"), ranked_predictions):
        rows.append(
            {
                "split": split_name,
                "method": method,
                "id": example["id"],
                "slang_term": example["slang_term"],
                "context_sentence": example["context_sentence"],
                "gold_paraphrase": example["neutral_paraphrase"],
                "top_predictions": " || ".join(predictions[:top_n]),
            }
        )
    return rows
