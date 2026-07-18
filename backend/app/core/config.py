"""Application configuration using Pydantic Settings."""

from __future__ import annotations

import os
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings


class LLMProvider(str, Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    MISTRAL = "mistral"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # General
    PROJECT_NAME: str = "CodeNexus"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    SECRET_KEY: str = "change-me-to-a-random-secret-key"

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    DATA_DIR: Path = Path("data")
    REPOS_DIR: Path = Path("repos")

    # Database
    DATABASE_URL: str = "sqlite:///./data/codenexus.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Embedding
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_BATCH_SIZE: int = 32

    # Re-ranker
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # LLM
    LLM_PROVIDER: LLMProvider = LLMProvider.OLLAMA
    LLM_MODEL: str = "llama3"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 2048

    # API Keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    MISTRAL_API_KEY: str = ""

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Search
    SEARCH_TOP_K: int = 100
    RERANK_TOP_K: int = 20
    EXPLAIN_TOP_K: int = 3

    # Chunking
    MAX_CHUNK_TOKENS: int = 512
    OVERLAP_TOKENS: int = 64
    MAX_FILE_SIZE_MB: int = 1

    # Ignore patterns
    IGNORE_PATTERNS: List[str] = [
        ".git", "node_modules", "venv", "dist", "build",
        ".cache", "target", "coverage", "__pycache__",
    ]

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    @field_validator("DATA_DIR", "REPOS_DIR", mode="before")
    @classmethod
    def resolve_path(cls, v: str | Path) -> Path:
        return Path(v)

    def ensure_dirs(self) -> None:
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.REPOS_DIR.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
