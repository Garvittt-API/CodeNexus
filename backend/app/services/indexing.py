"""Repository indexing service."""

from __future__ import annotations

import logging
import shutil
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.config import get_settings
from ..core.exceptions import IndexingError, RepositoryImportError, PathTraversalError
from ..core.security import is_safe_git_url, run_git_command, validate_path
from ..infrastructure.database import get_db
from ..infrastructure.embedding_provider import get_embedding_provider
from ..infrastructure.vector_db import get_vector_db
from .parsing import (
    count_tokens_approximate,
    extract_code_entities,
    scan_repository,
)

logger = logging.getLogger(__name__)


def import_repository(source: str, source_type: str = "local") -> Dict[str, Any]:
    """Import a repository from local path, GitHub URL, or Git URL."""
    settings = get_settings()
    db = get_db()
    repo_id = str(uuid.uuid4())
    repo_name = ""

    if source_type == "local":
        local_path = Path(source).resolve()
        if not local_path.exists():
            raise RepositoryImportError(f"Path does not exist: {source}")
        if not local_path.is_dir():
            raise RepositoryImportError(f"Path is not a directory: {source}")
        repo_name = local_path.name
        indexed_path = str(settings.REPOS_DIR / repo_id)
        settings.REPOS_DIR.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copytree(str(local_path), indexed_path, dirs_exist_ok=True, ignore=shutil.ignore_patterns(*settings.IGNORE_PATTERNS))
        except Exception as e:
            raise RepositoryImportError(f"Failed to copy repository: {e}")

    elif source_type in ("github", "git"):
        if not is_safe_git_url(source):
            raise RepositoryImportError("Invalid or unsafe Git URL")
        repo_name = source.rstrip("/").split("/")[-1].replace(".git", "")
        indexed_path = str(settings.REPOS_DIR / repo_id)
        settings.REPOS_DIR.mkdir(parents=True, exist_ok=True)
        result = run_git_command(["clone", "--depth", "1", source, indexed_path], cwd=settings.REPOS_DIR)
        if result.returncode != 0:
            raise RepositoryImportError(f"Git clone failed: {result.stderr}")

    else:
        raise RepositoryImportError(f"Unknown source type: {source_type}")

    repo_data = {
        "id": repo_id,
        "name": repo_name,
        "source": source,
        "source_type": source_type,
        "status": "pending",
        "total_files": 0,
        "total_lines": 0,
        "total_chunks": 0,
        "languages": {},
        "functions": 0,
        "classes": 0,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "error_message": None,
        "indexed_path": indexed_path,
    }
    db.store_repository(repo_data)
    return repo_data


def start_indexing(repo_id: str, task_id: Optional[str] = None) -> str:
    """Start indexing a repository. Returns task_id."""
    db = get_db()
    repo = db.get_repository(repo_id)
    if not repo:
        raise IndexingError(f"Repository {repo_id} not found")

    if task_id is None:
        task_id = str(uuid.uuid4())

    task_data = {
        "id": task_id,
        "repo_id": repo_id,
        "status": "running",
        "progress": 0.0,
        "total_files": 0,
        "processed_files": 0,
        "current_file": None,
        "error_message": None,
        "started_at": datetime.now(timezone.utc),
        "completed_at": None,
    }
    db.store_task(task_data)
    db.update_repository(repo_id, status="indexing")

    try:
        _run_indexing(repo_id, task_id)
    except Exception as e:
        logger.error("Indexing failed for %s: %s", repo_id, e)
        db.update_task(task_id, status="failed", error_message=str(e))
        db.update_repository(repo_id, status="failed", error_message=str(e))

    return task_id


def _run_indexing(repo_id: str, task_id: str) -> None:
    """Run the full indexing pipeline."""
    settings = get_settings()
    db = get_db()
    repo = db.get_repository(repo_id)
    repo_path = repo["indexed_path"]

    if not repo_path or not Path(repo_path).exists():
        raise IndexingError("Repository path does not exist")

    logger.info("Starting indexing for repo %s at %s", repo_id, repo_path)

    files = scan_repository(repo_path, settings.IGNORE_PATTERNS)
    db.update_task(task_id, total_files=len(files))

    all_chunks: List[Dict[str, Any]] = []
    total_functions = 0
    total_classes = 0
    languages: Dict[str, int] = {}
    total_lines = 0

    for i, file_info in enumerate(files):
        db.update_task(
            task_id,
            processed_files=i,
            current_file=file_info["path"],
            progress=(i / max(len(files), 1)) * 0.7,
        )

        try:
            abs_path = file_info["absolute_path"]
            validated_path = validate_path(abs_path, Path(repo_path))

            with open(validated_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            total_lines += file_info["lines"]
            lang = file_info["language"]
            languages[lang] = languages.get(lang, 0) + 1

            blocks, stats = extract_code_entities(content, lang, file_info["path"])
            total_functions += stats["functions"]
            total_classes += stats["classes"]

            for block in blocks:
                chunk_id = str(uuid.uuid4())
                chunk = {
                    "id": chunk_id,
                    "repo_id": repo_id,
                    "file_path": file_info["path"],
                    "language": lang,
                    "content": block["content"],
                    "start_line": block["start_line"],
                    "end_line": block["end_line"],
                    "chunk_type": block["type"],
                    "name": block.get("name"),
                    "docstring": block.get("docstring"),
                    "imports": stats.get("imports", []),
                    "tokens": count_tokens_approximate(block["content"]),
                    "embedding_id": None,
                }
                all_chunks.append(chunk)

        except PathTraversalError:
            logger.warning("Path traversal attempt detected: %s", file_info["path"])
            continue
        except Exception as e:
            logger.warning("Failed to process file %s: %s", file_info["path"], e)
            continue

    logger.info(
        "Extracted %d chunks from %d files (functions=%d, classes=%d)",
        len(all_chunks), len(files), total_functions, total_classes,
    )

    db.update_task(task_id, progress=0.7, current_file="Generating embeddings...")

    embedding_provider = get_embedding_provider()
    vector_db = get_vector_db(dimension=embedding_provider.dimension)

    texts = [c["content"] for c in all_chunks]
    if texts:
        batch_size = settings.EMBEDDING_BATCH_SIZE
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            batch_embeddings = embedding_provider.embed(batch)
            all_embeddings.append(batch_embeddings)
            progress = 0.7 + 0.2 * ((i + len(batch)) / len(texts))
            db.update_task(task_id, progress=progress, current_file=f"Embedding {i + len(batch)}/{len(texts)}...")

        import numpy as np
        embeddings = np.vstack(all_embeddings)

        metadata_list = [
            {
                "chunk_id": c["id"],
                "file_path": c["file_path"],
                "language": c["language"],
                "chunk_type": c["chunk_type"],
                "name": c.get("name"),
                "start_line": c["start_line"],
                "end_line": c["end_line"],
            }
            for c in all_chunks
        ]

        embedding_ids = vector_db.add_embeddings(embeddings, metadata_list)

        for i, chunk in enumerate(all_chunks):
            chunk["embedding_id"] = int(embedding_ids[i])

        index_dir = settings.DATA_DIR / "indices" / repo_id
        vector_db.save(str(index_dir))

    db.update_task(task_id, progress=0.95, current_file="Saving to database...")

    db.store_chunks(all_chunks)

    db.update_repository(
        repo_id,
        status="completed",
        total_files=len(files),
        total_lines=total_lines,
        total_chunks=len(all_chunks),
        languages=languages,
        functions=total_functions,
        classes=total_classes,
    )

    db.update_task(
        task_id,
        status="completed",
        progress=1.0,
        processed_files=len(files),
        completed_at=datetime.now(timezone.utc),
    )

    logger.info("Indexing completed for repo %s: %d files, %d chunks", repo_id, len(files), len(all_chunks))


def get_indexing_status(task_id: str) -> Optional[Dict[str, Any]]:
    """Get indexing task status."""
    db = get_db()
    return db.get_task(task_id)


def delete_repository(repo_id: str) -> bool:
    """Delete a repository and its index."""
    settings = get_settings()
    db = get_db()
    repo = db.get_repository(repo_id)
    if not repo:
        return False

    if repo.get("indexed_path") and Path(repo["indexed_path"]).exists():
        shutil.rmtree(repo["indexed_path"], ignore_errors=True)

    index_dir = settings.DATA_DIR / "indices" / repo_id
    if index_dir.exists():
        shutil.rmtree(index_dir, ignore_errors=True)

    db.delete_repository(repo_id)
    return True
