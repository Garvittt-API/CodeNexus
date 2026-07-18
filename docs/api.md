# CodeNexus API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication required. Rate limiting is enforced at 60 requests/minute per IP.

## Endpoints

### Health Check

```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "embedding_model": "BAAI/bge-small-en-v1.5",
  "llm_provider": "ollama"
}
```

---

### Import Repository

```
POST /api/repos/import
```

**Request:**
```json
{
  "source": "/path/to/repo",
  "source_type": "local"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| source | string | Yes | Local path, GitHub URL, or Git URL |
| source_type | string | No | `local`, `github`, or `git` (default: `local`) |

**Response:**
```json
{
  "id": "uuid",
  "name": "repo-name",
  "source": "/path/to/repo",
  "source_type": "local",
  "status": "pending",
  "message": "Repository imported. Call POST /repos/{id}/index to start indexing."
}
```

---

### List Repositories

```
GET /api/repos
```

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "repo-name",
    "source": "/path/to/repo",
    "source_type": "local",
    "status": "completed",
    "total_files": 150,
    "total_lines": 12000,
    "total_chunks": 350,
    "languages": {"python": 80, "javascript": 40},
    "functions": 200,
    "classes": 30,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:05:00Z"
  }
]
```

---

### Delete Repository

```
DELETE /api/repos/{repo_id}
```

**Response:**
```json
{
  "message": "Repository deleted"
}
```

---

### Start Indexing

```
POST /api/repos/{repo_id}/index
```

**Response:**
```json
{
  "task_id": "uuid",
  "repo_id": "uuid",
  "message": "Indexing started"
}
```

---

### Get Indexing Status

```
GET /api/indexing/{task_id}/status
```

**Response:**
```json
{
  "id": "task-uuid",
  "repo_id": "repo-uuid",
  "status": "running",
  "progress": 0.65,
  "total_files": 150,
  "processed_files": 97,
  "current_file": "src/utils/helpers.py",
  "error_message": null
}
```

---

### Search Code

```
POST /api/search
```

**Request:**
```json
{
  "query": "How does authentication work?",
  "repo_id": "optional-repo-uuid",
  "top_k": 20,
  "rerank": true
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| query | string | required | Natural language query |
| repo_id | string | null | Filter to specific repository |
| top_k | int | 20 | Number of results (1-100) |
| rerank | bool | true | Enable cross-encoder re-ranking |

**Response:**
```json
{
  "query": "How does authentication work?",
  "repo_id": null,
  "results": [
    {
      "chunk_id": "uuid",
      "file_path": "src/auth/login.py",
      "language": "python",
      "content": "def authenticate(username, password):...",
      "start_line": 15,
      "end_line": 42,
      "chunk_type": "function",
      "name": "authenticate",
      "score": 0.9234,
      "rank": 1
    }
  ],
  "total_results": 12,
  "search_time_ms": 156.7
}
```

---

### Search with Explanation

```
POST /api/search/explain
```

**Request:** Same as `/api/search`

**Response:**
```json
{
  "query": "How does authentication work?",
  "results": [...],
  "explanation": "The authentication system in this codebase uses...",
  "total_results": 12,
  "search_time_ms": 2340.5
}
```

---

### Stream Explanation (SSE)

```
POST /api/search/explain/stream
```

**Request:** Same as `/api/search`

**Response (SSE):**
```
data: {"type": "results", "results": [...], "total": 12}

data: {"type": "explanation_chunk", "content": "The "}

data: {"type": "explanation_chunk", "content": "authentication "}

data: {"type": "explanation_chunk", "content": "system..."}

data: [DONE]
```

## Error Responses

All error responses follow:

```json
{
  "detail": "Error message"
}
```

| Status | Description |
|--------|-------------|
| 400 | Bad request / validation error |
| 404 | Resource not found |
| 422 | Request validation failed |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
