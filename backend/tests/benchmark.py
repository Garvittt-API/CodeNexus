"""Benchmarking script for CodeNexus."""

from __future__ import annotations

import gc
import os
import sys
import tempfile
import time
from pathlib import Path

import numpy as np


def benchmark_embedding(n_texts: int = 100) -> dict:
    """Benchmark embedding generation speed."""
    from app.infrastructure.embedding_provider import get_embedding_provider

    print(f"\n{'='*60}")
    print(f"Benchmark: Embedding Generation ({n_texts} texts)")
    print(f"{'='*60}")

    provider = get_embedding_provider()
    texts = [f"def function_{i}(): return {i}" for i in range(n_texts)]

    # Warm up
    provider.embed(texts[:1])

    gc.collect()
    start = time.time()
    embeddings = provider.embed(texts)
    elapsed = time.time() - start

    speed = n_texts / elapsed
    print(f"  Model: {provider.model_name}")
    print(f"  Dimension: {provider.dimension}")
    print(f"  Time: {elapsed:.2f}s")
    print(f"  Speed: {speed:.1f} texts/sec")
    print(f"  Shape: {embeddings.shape}")

    return {"n_texts": n_texts, "time": elapsed, "speed": speed, "dimension": provider.dimension}


def benchmark_vector_search(n_vectors: int = 10000, top_k: int = 10) -> dict:
    """Benchmark vector search speed."""
    from app.infrastructure.embedding_provider import get_embedding_provider
    from app.infrastructure.vector_db import FAISSVectorDB

    print(f"\n{'='*60}")
    print(f"Benchmark: Vector Search ({n_vectors} vectors, top_k={top_k})")
    print(f"{'='*60}")

    provider = get_embedding_provider()
    dim = provider.dimension

    # Generate random embeddings
    np.random.seed(42)
    embeddings = np.random.rand(n_vectors, dim).astype(np.float32)
    metadata = [{"chunk_id": str(i), "file_path": f"file_{i}.py"} for i in range(n_vectors)]

    # Build index
    db = FAISSVectorDB(dimension=dim)
    start = time.time()
    db.add_embeddings(embeddings, metadata)
    index_time = time.time() - start
    print(f"  Index build time: {index_time:.2f}s")
    print(f"  Vectors: {db.count()}")

    # Benchmark search
    query = np.random.rand(1, dim).astype(np.float32)
    times = []
    for _ in range(100):
        start = time.time()
        db.search(query, top_k=top_k)
        times.append(time.time() - start)

    avg_time = np.mean(times) * 1000
    p99_time = np.percentile(times, 99) * 1000
    print(f"  Avg search latency: {avg_time:.1f}ms")
    print(f"  P99 search latency: {p99_time:.1f}ms")
    print(f"  Throughput: {1000/avg_time:.0f} queries/sec")

    return {"n_vectors": n_vectors, "index_time": index_time, "avg_latency_ms": avg_time, "p99_latency_ms": p99_time}


def benchmark_search_pipeline(n_vectors: int = 1000) -> dict:
    """Benchmark full search pipeline (embedding + search + rerank)."""
    from app.infrastructure.embedding_provider import get_embedding_provider
    from app.infrastructure.vector_db import FAISSVectorDB

    print(f"\n{'='*60}")
    print(f"Benchmark: Full Search Pipeline ({n_vectors} vectors)")
    print(f"{'='*60}")

    provider = get_embedding_provider()
    dim = provider.dimension

    np.random.seed(42)
    embeddings = np.random.rand(n_vectors, dim).astype(np.float32)
    codes = [f"def func_{i}(): return {i}" for i in range(n_vectors)]
    metadata = [{"chunk_id": str(i), "file_path": f"file_{i}.py"} for i in range(n_vectors)]

    db = FAISSVectorDB(dimension=dim)
    db.add_embeddings(embeddings, metadata)

    # Benchmark embedding query
    query = "How does authentication work?"
    start = time.time()
    query_embedding = provider.embed_query(query)
    embed_time = (time.time() - start) * 1000

    # Benchmark ANN search
    start = time.time()
    candidates = db.search(query_embedding, top_k=20)
    search_time = (time.time() - start) * 1000

    total = embed_time + search_time
    print(f"  Query embedding: {embed_time:.1f}ms")
    print(f"  ANN search: {search_time:.1f}ms")
    print(f"  Total (no rerank): {total:.1f}ms")
    print(f"  Candidates: {len(candidates)}")

    return {"embed_ms": embed_time, "search_ms": search_time, "total_ms": total}


def benchmark_memory() -> dict:
    """Benchmark memory usage."""
    import psutil

    print(f"\n{'='*60}")
    print("Benchmark: Memory Usage")
    print(f"{'='*60}")

    process = psutil.Process(os.getpid())

    gc.collect()
    mem_before = process.memory_info().rss / 1024 / 1024

    from app.infrastructure.embedding_provider import get_embedding_provider
    provider = get_embedding_provider()
    mem_after_model = process.memory_info().rss / 1024 / 1024

    print(f"  Before model load: {mem_before:.1f}MB")
    print(f"  After model load: {mem_after_model:.1f}MB")
    print(f"  Model memory: {mem_after_model - mem_before:.1f}MB")

    return {"before_mb": mem_before, "after_mb": mem_after_model, "model_mb": mem_after_model - mem_before}


def main():
    print("\n" + "=" * 60)
    print("CodeNexus Benchmark Suite")
    print("=" * 60)

    results = {}

    try:
        results["embedding"] = benchmark_embedding(100)
    except Exception as e:
        print(f"  Embedding benchmark failed: {e}")

    try:
        results["vector_search"] = benchmark_vector_search(10000, 10)
    except Exception as e:
        print(f"  Vector search benchmark failed: {e}")

    try:
        results["pipeline"] = benchmark_search_pipeline(1000)
    except Exception as e:
        print(f"  Pipeline benchmark failed: {e}")

    try:
        results["memory"] = benchmark_memory()
    except Exception as e:
        print(f"  Memory benchmark failed: {e}")

    print("\n" + "=" * 60)
    print("Benchmark Complete")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
