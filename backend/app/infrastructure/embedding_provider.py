"""Embedding provider with sentence-transformers."""

from __future__ import annotations

import logging
from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

from ..core.config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingProvider:
    """Local embedding model provider."""

    def __init__(self, model_name: Optional[str] = None):
        settings = get_settings()
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.batch_size = settings.EMBEDDING_BATCH_SIZE
        self._model: Optional[SentenceTransformer] = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            logger.info("Loading embedding model: %s", self.model_name)
            self._model = SentenceTransformer(self.model_name)
            logger.info(
                "Embedding model loaded. Dimension: %d",
                self._model.get_sentence_embedding_dimension(),
            )
        return self._model

    @property
    def dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()

    def embed(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.array([], dtype=np.float32)

        logger.info(
            "Embedding %d texts with batch_size=%d", len(texts), self.batch_size
        )

        if len(texts) <= self.batch_size:
            embeddings = self.model.encode(
                texts,
                show_progress_bar=False,
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
            return np.array(embeddings, dtype=np.float32)

        all_embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            batch_embeddings = self.model.encode(
                batch,
                show_progress_bar=False,
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
            all_embeddings.append(batch_embeddings)
            logger.debug(
                "Embedded batch %d/%d",
                i // self.batch_size + 1,
                (len(texts) + self.batch_size - 1) // self.batch_size,
            )

        return np.vstack(all_embeddings).astype(np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        return self.embed([query])[0]


_provider: Optional[EmbeddingProvider] = None


def get_embedding_provider(model_name: Optional[str] = None) -> EmbeddingProvider:
    global _provider
    if _provider is None or (model_name and model_name != _provider.model_name):
        _provider = EmbeddingProvider(model_name)
    return _provider
