"""Cross-encoder re-ranker for search results."""

from __future__ import annotations

import logging
from typing import List, Optional, Tuple

import numpy as np
from sentence_transformers import CrossEncoder

from ..core.config import get_settings

logger = logging.getLogger(__name__)


class Reranker:
    """Cross-encoder re-ranker using sentence-transformers."""

    def __init__(self, model_name: Optional[str] = None):
        settings = get_settings()
        self.model_name = model_name or settings.RERANKER_MODEL
        self._model: Optional[CrossEncoder] = None

    @property
    def model(self) -> CrossEncoder:
        if self._model is None:
            logger.info("Loading reranker model: %s", self.model_name)
            self._model = CrossEncoder(self.model_name)
            logger.info("Reranker model loaded")
        return self._model

    def rerank(
        self,
        query: str,
        documents: List[str],
        top_k: int = 20,
    ) -> List[Tuple[int, float]]:
        """Rerank documents against query. Returns (index, score) tuples sorted by score desc."""
        if not documents:
            return []

        pairs = [[query, doc] for doc in documents]
        scores = self.model.predict(pairs, show_progress_bar=False)
        scores = np.array(scores)

        top_k = min(top_k, len(documents))
        top_indices = np.argsort(scores)[::-1][:top_k]

        return [(int(idx), float(scores[idx])) for idx in top_indices]


_reranker: Optional[Reranker] = None


def get_reranker(model_name: Optional[str] = None) -> Reranker:
    global _reranker
    if _reranker is None:
        _reranker = Reranker(model_name)
    return _reranker
