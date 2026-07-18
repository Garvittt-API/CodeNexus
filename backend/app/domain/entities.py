"""Domain entities for CodeNexus."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RepoStatus(str, Enum):
    PENDING = "pending"
    INDEXING = "indexing"
    COMPLETED = "completed"
    FAILED = "failed"


class Repository(BaseModel):
    """A code repository."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    source: str  # local path, GitHub URL, or Git URL
    source_type: str  # local | github | git
    status: RepoStatus = RepoStatus.PENDING
    total_files: int = 0
    total_lines: int = 0
    total_chunks: int = 0
    languages: Dict[str, int] = Field(default_factory=dict)
    functions: int = 0
    classes: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error_message: Optional[str] = None
    indexed_path: Optional[str] = None


class CodeChunk(BaseModel):
    """A chunk of code with metadata."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    repo_id: str
    file_path: str
    language: str
    content: str
    start_line: int
    end_line: int
    chunk_type: str  # function | class | method | block | file
    name: Optional[str] = None  # function/class name
    docstring: Optional[str] = None
    imports: List[str] = Field(default_factory=list)
    tokens: int = 0
    embedding_id: Optional[int] = None  # index in FAISS


class SearchResult(BaseModel):
    """A search result."""

    chunk_id: str
    file_path: str
    language: str
    content: str
    start_line: int
    end_line: int
    chunk_type: str
    name: Optional[str] = None
    score: float
    rank: int


class SearchResponse(BaseModel):
    """API search response."""

    query: str
    repo_id: Optional[str] = None
    results: List[SearchResult]
    total_results: int
    search_time_ms: float


class ExplainResponse(BaseModel):
    """API explain response with LLM explanation."""

    query: str
    repo_id: Optional[str] = None
    results: List[SearchResult]
    explanation: str
    total_results: int
    search_time_ms: float


class IndexingTask(BaseModel):
    """An indexing task."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    repo_id: str
    status: str = "pending"
    progress: float = 0.0
    total_files: int = 0
    processed_files: int = 0
    current_file: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class RepoStats(BaseModel):
    """Repository statistics."""

    total_files: int = 0
    total_lines: int = 0
    total_chunks: int = 0
    languages: Dict[str, int] = Field(default_factory=dict)
    functions: int = 0
    classes: int = 0
