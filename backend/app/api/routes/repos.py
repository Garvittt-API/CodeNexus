"""Repository management API routes."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from ...core.exceptions import CodeNexusError, RepositoryImportError
from ...services.indexing import (
    delete_repository,
    import_repository,
    start_indexing,
)
from ...infrastructure.database import get_db

router = APIRouter(prefix="/repos", tags=["repositories"])


class ImportRequest(BaseModel):
    source: str = Field(..., min_length=1, max_length=2048)
    source_type: str = Field(default="local", pattern="^(local|github|git)$")


class ImportResponse(BaseModel):
    id: str
    name: str
    source: str
    source_type: str
    status: str
    message: str


class RepoResponse(BaseModel):
    id: str
    name: str
    source: str
    source_type: str
    status: str
    total_files: int
    total_lines: int
    total_chunks: int
    languages: dict
    functions: int
    classes: int
    created_at: str
    updated_at: str
    error_message: Optional[str] = None


class TaskStatusResponse(BaseModel):
    id: str
    repo_id: str
    status: str
    progress: float
    total_files: int
    processed_files: int
    current_file: Optional[str] = None
    error_message: Optional[str] = None


@router.post("/import", response_model=ImportResponse)
async def import_repo(request: ImportRequest, background_tasks: BackgroundTasks):
    """Import a repository from local path, GitHub URL, or Git URL."""
    try:
        repo = import_repository(request.source, request.source_type)
        return ImportResponse(
            id=repo["id"],
            name=repo["name"],
            source=repo["source"],
            source_type=repo["source_type"],
            status="pending",
            message="Repository imported. Call POST /repos/{id}/index to start indexing.",
        )
    except RepositoryImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except CodeNexusError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=list[RepoResponse])
async def list_repos():
    """List all indexed repositories."""
    db = get_db()
    repos = db.list_repositories()
    return [
        RepoResponse(
            id=r["id"],
            name=r["name"],
            source=r["source"],
            source_type=r["source_type"],
            status=r["status"],
            total_files=r["total_files"],
            total_lines=r["total_lines"],
            total_chunks=r["total_chunks"],
            languages=r["languages"],
            functions=r["functions"],
            classes=r["classes"],
            created_at=str(r["created_at"]),
            updated_at=str(r["updated_at"]),
            error_message=r.get("error_message"),
        )
        for r in repos
    ]


@router.delete("/{repo_id}")
async def delete_repo(repo_id: str):
    """Delete a repository and its index."""
    success = delete_repository(repo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Repository not found")
    return {"message": "Repository deleted"}


@router.post("/{repo_id}/index")
async def index_repo(repo_id: str, background_tasks: BackgroundTasks):
    """Start indexing a repository (runs in background)."""
    db = get_db()
    repo = db.get_repository(repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    task_id = str(__import__("uuid").uuid4())
    background_tasks.add_task(start_indexing, repo_id, task_id)

    return {"task_id": task_id, "repo_id": repo_id, "message": "Indexing started"}


@router.get("/{repo_id}/status")
async def repo_status(repo_id: str):
    """Get repository status and stats."""
    db = get_db()
    repo = db.get_repository(repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    return repo
