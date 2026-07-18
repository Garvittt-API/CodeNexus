"""Search API routes."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ...core.exceptions import SearchError
from ...services.search import search_code, search_and_explain, search_and_explain_stream
from ...infrastructure.database import get_db

router = APIRouter(tags=["search"])


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000)
    repo_id: Optional[str] = None
    top_k: int = Field(default=20, ge=1, le=100)
    rerank: bool = Field(default=True)


class SearchItem(BaseModel):
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
    query: str
    repo_id: Optional[str] = None
    results: list[SearchItem]
    total_results: int
    search_time_ms: float


class ExplainResponse(BaseModel):
    query: str
    repo_id: Optional[str] = None
    results: list[SearchItem]
    explanation: str
    total_results: int
    search_time_ms: float


class IndexingStatusRequest(BaseModel):
    task_id: str


class IndexingStatusResponse(BaseModel):
    id: str
    repo_id: str
    status: str
    progress: float
    total_files: int
    processed_files: int
    current_file: Optional[str] = None
    error_message: Optional[str] = None


@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """Search code semantically across repositories."""
    if request.repo_id:
        db = get_db()
        repo = db.get_repository(request.repo_id)
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")

    try:
        result = search_code(
            query=request.query,
            repo_id=request.repo_id,
            top_k=request.top_k,
            rerank=request.rerank,
        )
        return SearchResponse(
            query=result["query"],
            repo_id=result["repo_id"],
            results=[SearchItem(**r) for r in result["results"]],
            total_results=result["total_results"],
            search_time_ms=result["search_time_ms"],
        )
    except SearchError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/explain", response_model=ExplainResponse)
async def search_explain(request: SearchRequest):
    """Search code and generate an AI explanation."""
    if request.repo_id:
        db = get_db()
        repo = db.get_repository(request.repo_id)
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")

    try:
        result = await search_and_explain(
            query=request.query,
            repo_id=request.repo_id,
            top_k=request.top_k,
        )
        return ExplainResponse(
            query=result["query"],
            repo_id=result["repo_id"],
            results=[SearchItem(**r) for r in result["results"]],
            explanation=result["explanation"],
            total_results=result["total_results"],
            search_time_ms=result["search_time_ms"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/explain/stream")
async def search_explain_stream(request: SearchRequest):
    """Search code and stream the AI explanation as SSE."""
    return StreamingResponse(
        search_and_explain_stream(
            query=request.query,
            repo_id=request.repo_id,
            top_k=request.top_k,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/indexing/{task_id}/status", response_model=IndexingStatusResponse)
async def indexing_status(task_id: str):
    """Get indexing task status."""
    from ...services.indexing import get_indexing_status

    status = get_indexing_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return IndexingStatusResponse(**status)
