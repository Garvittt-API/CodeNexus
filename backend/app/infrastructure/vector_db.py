"""Vector database abstraction and FAISS implementation."""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import faiss
import numpy as np


class BaseVectorDB(ABC):
    """Abstract base class for vector databases."""

    @abstractmethod
    def add_embeddings(
        self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]
    ) -> List[int]:
        pass

    @abstractmethod
    def search(
        self, query_embedding: np.ndarray, top_k: int = 10
    ) -> List[Tuple[int, float, Dict[str, Any]]]:
        pass

    @abstractmethod
    def save(self, path: str | Path) -> None:
        pass

    @abstractmethod
    def load(self, path: str | Path) -> None:
        pass

    @abstractmethod
    def delete_by_prefix(self, prefix: str) -> int:
        pass

    @abstractmethod
    def count(self) -> int:
        pass


class FAISSVectorDB(BaseVectorDB):
    """FAISS-based vector database with metadata storage."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.metadata: List[Dict[str, Any]] = []
        self.id_counter: int = 0

    def add_embeddings(
        self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]
    ) -> List[int]:
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-10)
        normalized = embeddings / norms

        start_id = self.id_counter
        ids = list(range(start_id, start_id + len(embeddings)))
        self.index.add(normalized.astype(np.float32))

        for i, meta in enumerate(metadata):
            meta_copy = dict(meta)
            meta_copy["faiss_id"] = ids[i]
            self.metadata.append(meta_copy)

        self.id_counter += len(embeddings)
        return ids

    def search(
        self, query_embedding: np.ndarray, top_k: int = 10
    ) -> List[Tuple[int, float, Dict[str, Any]]]:
        if self.index.ntotal == 0:
            return []

        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        norm = np.linalg.norm(query_embedding, axis=1, keepdims=True)
        norm = np.maximum(norm, 1e-10)
        query_normalized = query_embedding / norm

        actual_k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_normalized.astype(np.float32), actual_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            results.append((int(idx), float(score), self.metadata[idx]))

        return results

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(path / "index.faiss"))
        with open(path / "metadata.json", "w") as f:
            json.dump(
                {"metadata": self.metadata, "id_counter": self.id_counter, "dimension": self.dimension},
                f,
            )

    def load(self, path: str | Path) -> None:
        path = Path(path)
        index_file = path / "index.faiss"
        meta_file = path / "metadata.json"

        if not index_file.exists():
            return

        self.index = faiss.read_index(str(index_file))

        if meta_file.exists():
            with open(meta_file, "r") as f:
                data = json.load(f)
            self.metadata = data.get("metadata", [])
            self.id_counter = data.get("id_counter", 0)
            self.dimension = data.get("dimension", self.dimension)

    def delete_by_prefix(self, prefix: str) -> int:
        indices_to_remove = []
        for i, meta in enumerate(self.metadata):
            file_path = meta.get("file_path", "")
            if file_path.startswith(prefix):
                indices_to_remove.append(i)

        if not indices_to_remove:
            return 0

        keep_mask = np.ones(len(self.metadata), dtype=bool)
        keep_mask[indices_to_remove] = False

        remaining_meta = [self.metadata[i] for i in range(len(self.metadata)) if keep_mask[i]]

        if remaining_meta:
            embeddings = []
            for i in range(self.index.ntotal):
                vec = np.array([self.index.reconstruct(i)])
                embeddings.append(vec)
            all_embeddings = np.vstack(embeddings)
            kept_embeddings = all_embeddings[keep_mask]

            self.index = faiss.IndexFlatIP(self.dimension)
            if len(kept_embeddings) > 0:
                self.add_embeddings(kept_embeddings, remaining_meta)
            else:
                self.metadata = []
                self.id_counter = 0
        else:
            self.index = faiss.IndexFlatIP(self.dimension)
            self.metadata = []
            self.id_counter = 0

        return len(indices_to_remove)

    def count(self) -> int:
        return self.index.ntotal


_vector_db: Optional[FAISSVectorDB] = None


def get_vector_db(dimension: int = 384) -> FAISSVectorDB:
    global _vector_db
    if _vector_db is None:
        _vector_db = FAISSVectorDB(dimension=dimension)
    return _vector_db


def load_vector_db(path: str | Path, dimension: int = 384) -> FAISSVectorDB:
    global _vector_db
    _vector_db = FAISSVectorDB(dimension=dimension)
    _vector_db.load(path)
    return _vector_db
