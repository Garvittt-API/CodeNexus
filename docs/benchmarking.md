# Benchmarking Guide

## Overview

CodeNexus includes benchmarking scripts to measure:
- Indexing speed (files/sec, chunks/sec)
- Search latency (ms)
- Memory usage (MB)

## Running Benchmarks

### Full Benchmark

```bash
cd backend
python -m tests.benchmark
```

### Custom Benchmark

```python
import time
import numpy as np
from app.infrastructure.embedding_provider import get_embedding_provider
from app.infrastructure.vector_db import get_vector_db

# Benchmark embedding
provider = get_embedding_provider()
texts = ["def hello(): pass"] * 1000

start = time.time()
embeddings = provider.embed(texts)
elapsed = time.time() - start

print(f"Embedded {len(texts)} texts in {elapsed:.2f}s")
print(f"Speed: {len(texts)/elapsed:.1f} texts/sec")
print(f"Embedding shape: {embeddings.shape}")

# Benchmark search
vector_db = get_vector_db(dimension=provider.dimension)
vector_db.add_embeddings(embeddings, [{"id": i} for i in range(len(embeddings))])

query = provider.embed_query("function definition")
start = time.time()
results = vector_db.search(query, top_k=10)
elapsed = time.time() - start

print(f"Search latency: {elapsed*1000:.1f}ms")
print(f"Results: {len(results)}")
```

## Metrics

### Indexing Performance

| Metric | Description |
|--------|-------------|
| Files/sec | Number of files processed per second |
| Chunks/sec | Number of code chunks created per second |
| Embeddings/sec | Number of embeddings generated per second |
| Total time | End-to-end indexing time |

### Search Performance

| Metric | Description |
|--------|-------------|
| ANN latency | FAISS nearest neighbor search time |
| Re-rank time | Cross-encoder re-ranking time |
| Total latency | End-to-end search time |
| Throughput | Queries per second |

### Memory Usage

| Metric | Description |
|--------|-------------|
| Embedding model | Memory used by sentence-transformers |
| FAISS index | Memory used by vector index |
| SQLite | Disk usage for metadata |
| Total RSS | Process resident set size |

## Scaling Considerations

### Small repos (< 10k files)
- IndexFlatIP is sufficient
- Single-threaded embedding is fine
- In-memory search

### Medium repos (10k-100k files)
- Consider IndexIVFFlat for faster search
- Use batch embeddings with parallel threads
- Background indexing recommended

### Large repos (> 100k files)
- IndexIVFFlat or IndexIVFPQ
- Distributed embedding generation
- External vector DB (PostgreSQL pgvector, Weaviate, Qdrant)
- Celery task queue for indexing
