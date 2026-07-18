"""Tests for vector database."""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pytest

from app.infrastructure.vector_db import FAISSVectorDB


class TestFAISSVectorDB:
    def test_add_and_search(self):
        db = FAISSVectorDB(dimension=4)
        embeddings = np.random.rand(5, 4).astype(np.float32)
        metadata = [{"chunk_id": str(i), "file_path": f"file_{i}.py"} for i in range(5)]

        ids = db.add_embeddings(embeddings, metadata)
        assert len(ids) == 5
        assert db.count() == 5

        query = np.random.rand(1, 4).astype(np.float32)
        results = db.search(query, top_k=3)
        assert len(results) == 3
        assert all(len(r) == 3 for r in results)

    def test_empty_search(self):
        db = FAISSVectorDB(dimension=4)
        query = np.random.rand(1, 4).astype(np.float32)
        results = db.search(query, top_k=5)
        assert len(results) == 0

    def test_single_embedding(self):
        db = FAISSVectorDB(dimension=4)
        embedding = np.random.rand(4).astype(np.float32)
        ids = db.add_embeddings(embedding, [{"chunk_id": "0"}])
        assert len(ids) == 1
        assert db.count() == 1

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = FAISSVectorDB(dimension=4)
            embeddings = np.random.rand(3, 4).astype(np.float32)
            metadata = [{"chunk_id": str(i)} for i in range(3)]
            db.add_embeddings(embeddings, metadata)

            db.save(tmpdir)

            db2 = FAISSVectorDB(dimension=4)
            db2.load(tmpdir)
            assert db2.count() == 3
            assert len(db2.metadata) == 3

    def test_search_returns_sorted_results(self):
        db = FAISSVectorDB(dimension=4)
        embeddings = np.eye(4, dtype=np.float32)
        metadata = [{"chunk_id": str(i)} for i in range(4)]
        db.add_embeddings(embeddings, metadata)

        query = np.array([[1.0, 0.0, 0.0, 0.0]], dtype=np.float32)
        results = db.search(query, top_k=4)
        assert results[0][2]["chunk_id"] == "0"

    def test_delete_by_prefix(self):
        db = FAISSVectorDB(dimension=4)
        embeddings = np.random.rand(5, 4).astype(np.float32)
        metadata = [
            {"chunk_id": "0", "file_path": "src/main.py"},
            {"chunk_id": "1", "file_path": "src/utils.py"},
            {"chunk_id": "2", "file_path": "tests/test.py"},
            {"chunk_id": "3", "file_path": "src/helper.py"},
            {"chunk_id": "4", "file_path": "README.md"},
        ]
        db.add_embeddings(embeddings, metadata)

        deleted = db.delete_by_prefix("src/")
        assert deleted == 3

    def test_count(self):
        db = FAISSVectorDB(dimension=4)
        assert db.count() == 0
        db.add_embeddings(np.random.rand(2, 4).astype(np.float32), [{"a": 1}, {"a": 2}])
        assert db.count() == 2
