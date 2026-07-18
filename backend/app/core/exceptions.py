"""Custom exception classes for CodeNexus."""

from __future__ import annotations


class CodeNexusError(Exception):
    """Base exception for CodeNexus."""

    def __init__(self, message: str = "An unexpected error occurred"):
        self.message = message
        super().__init__(self.message)


class RepositoryNotFoundError(CodeNexusError):
    """Raised when a repository is not found."""

    def __init__(self, repo_id: str):
        super().__init__(f"Repository '{repo_id}' not found")


class RepositoryImportError(CodeNexusError):
    """Raised when repository import fails."""

    def __init__(self, detail: str = "Failed to import repository"):
        super().__init__(detail)


class IndexingError(CodeNexusError):
    """Raised when indexing fails."""

    def __init__(self, detail: str = "Indexing failed"):
        super().__init__(detail)


class SearchError(CodeNexusError):
    """Raised when search fails."""

    def __init__(self, detail: str = "Search failed"):
        super().__init__(detail)


class EmbeddingError(CodeNexusError):
    """Raised when embedding generation fails."""

    def __init__(self, detail: str = "Embedding generation failed"):
        super().__init__(detail)


class LLMError(CodeNexusError):
    """Raised when LLM call fails."""

    def __init__(self, detail: str = "LLM call failed"):
        super().__init__(detail)


class PathTraversalError(CodeNexusError):
    """Raised when a path traversal attack is detected."""

    def __init__(self, path: str):
        super().__init__(f"Path traversal detected: {path}")


class ValidationError(CodeNexusError):
    """Raised when input validation fails."""

    def __init__(self, detail: str = "Input validation failed"):
        super().__init__(detail)
