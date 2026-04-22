from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np
import torch
from sklearn.feature_extraction.text import TfidfVectorizer


class EmbeddingBackend(Protocol):
    name: str

    def fit(self, texts: list[str]) -> None:
        ...

    def encode(self, texts: list[str]) -> np.ndarray:
        ...


@dataclass
class TfidfEmbeddingBackend:
    name: str = "tfidf"
    vectorizer: TfidfVectorizer | None = None

    def fit(self, texts: list[str]) -> None:
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
        )
        self.vectorizer.fit(texts)

    def encode(self, texts: list[str]) -> np.ndarray:
        if self.vectorizer is None:
            raise ValueError("TF-IDF backend must be fit before encoding.")
        return self.vectorizer.transform(texts).toarray()


@dataclass
class SentenceTransformerEmbeddingBackend:
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    device: str | None = None
    normalize_embeddings: bool = True
    local_files_only: bool = True
    _model: object | None = None

    @property
    def name(self) -> str:
        return self.model_name

    def fit(self, texts: list[str]) -> None:
        del texts
        self._ensure_model()

    def encode(self, texts: list[str]) -> np.ndarray:
        model = self._ensure_model()
        return np.asarray(
            model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=self.normalize_embeddings,
                show_progress_bar=False,
            )
        )

    def _ensure_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(
                self.model_name,
                device=self._resolve_device(),
                local_files_only=self.local_files_only,
            )
        return self._model

    def _resolve_device(self) -> str:
        if self.device is not None:
            return self.device
        if torch.backends.mps.is_available():
            return "mps"
        if torch.cuda.is_available():
            return "cuda"
        return "cpu"


def create_backend(name: str, model_name: str | None = None) -> EmbeddingBackend:
    normalized = name.strip().lower()
    if normalized == "tfidf":
        return TfidfEmbeddingBackend()
    if normalized in {"sentence-transformer", "sentence_transformer", "sbert"}:
        return SentenceTransformerEmbeddingBackend(
            model_name=model_name or "sentence-transformers/all-MiniLM-L6-v2"
        )
    raise ValueError(f"Unsupported embedding backend: {name}")
