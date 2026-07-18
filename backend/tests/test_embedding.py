"""Tests for embedding provider."""

from __future__ import annotations

import numpy as np
import pytest

from app.infrastructure.embedding_provider import EmbeddingProvider


class TestEmbeddingProvider:
    @pytest.fixture
    def provider(self):
        return EmbeddingProvider("BAAI/bge-small-en-v1.5")

    def test_embed_single_text(self, provider):
        result = provider.embed(["hello world"])
        assert result.shape[0] == 1
        assert result.shape[1] > 0

    def test_embed_multiple_texts(self, provider):
        texts = ["hello world", "foo bar", "test string"]
        result = provider.embed(texts)
        assert result.shape[0] == 3

    def test_embed_query(self, provider):
        result = provider.embed_query("test query")
        assert result.ndim == 1
        assert result.shape[0] > 0

    def test_empty_input(self, provider):
        result = provider.embed([])
        assert result.shape[0] == 0

    def test_dimension(self, provider):
        assert provider.dimension > 0

    def test_normalized_embeddings(self, provider):
        result = provider.embed(["test text"])
        norms = np.linalg.norm(result, axis=1)
        np.testing.assert_allclose(norms, 1.0, atol=1e-5)
