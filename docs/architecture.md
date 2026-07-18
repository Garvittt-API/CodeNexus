# CodeNexus Architecture

## Overview

CodeNexus is designed with Clean Architecture principles, separating concerns into distinct layers:

1. **API Layer**: FastAPI routes handling HTTP requests/responses
2. **Service Layer**: Business logic for indexing, searching, and LLM integration
3. **Domain Layer**: Core entities and value objects
4. **Infrastructure Layer**: External integrations (vector DB, embeddings, LLM providers)

## Data Flow

### Indexing Pipeline

```
Repository Import → File Scanning → AST Parsing → Chunk Creation → Embedding → FAISS Index
     ↓                ↓                ↓              ↓              ↓           ↓
  Git Clone      Language         Tree-sitter     Sliding        Sentence    IndexFlatIP
  / Copy Dir     Detection       / Regex Fallback  Window       Transformers  + Metadata
```

### Search Pipeline

```
User Query → Embedding → ANN Search (FAISS) → Re-ranking (Cross-Encoder) → Top-K Results
    ↓            ↓              ↓                      ↓                       ↓
  Natural    Same model    Top-100 candidates     Top-20 ranked           Results with
  Language   as indexing   via inner product       by cross-encoder       metadata + scores
```

### RAG Pipeline

```
Search Results → Context Building → LLM Prompt → LLM Response → Streaming SSE
      ↓               ↓                ↓              ↓              ↓
  Top-3 code      Combine code     Add system     Generate       Token-by-token
  snippets        + metadata       prompt +       explanation    streaming to
                                  context        with citations  frontend
```

## Key Components

### Embedding Provider

- **Model**: BAAI/bge-small-en-v1.5 (384 dimensions)
- **Fallback**: Configurable to e5-large, CodeBERT, Jina, Nomic
- **Batch Processing**: Configurable batch size with progress reporting
- **Normalization**: L2 normalization for inner product search

### Vector Database

- **Implementation**: FAISS IndexFlatIP (Inner Product after L2 normalization)
- **Metadata Storage**: Separate JSON index alongside FAISS
- **Persistence**: Save/load to disk for index reuse
- **Abstraction**: BaseVectorDB interface for future PostgreSQL/Weaviate/Qdrant support

### Re-ranker

- **Model**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Purpose**: Re-rank ANN candidates for precision
- **Input**: (query, code) pairs
- **Output**: Scored and sorted results

### Code Parser

- **Primary**: tree-sitter for AST-based parsing
- **Fallback**: Regex-based extraction for unsupported languages
- **Window**: Sliding window chunking as last resort
- **Chunking**: Split by functions/classes/methods with metadata

### LLM Providers

- **Default**: Ollama with llama3
- **Supported**: OpenAI, Anthropic, Gemini, DeepSeek, Mistral
- **Streaming**: SSE for real-time explanation display
- **Provider Pattern**: Abstract base class with concrete implementations

## Security

- Path traversal prevention via `pathlib` resolution
- Symlink validation (reject outside repo)
- Git URL allowlisting (GitHub, GitLab, Bitbucket only)
- Rate limiting via slowapi
- Input sanitization and length limits
- All API keys from environment variables

## Performance

- Batch embeddings with ThreadPoolExecutor
- Lazy model loading on first use
- In-memory FAISS index for fast search
- Configurable batch sizes for embedding generation
- Query embedding caching (pluggable)
