"""SQLAlchemy database setup and models."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from ..core.config import get_settings


class Base(DeclarativeBase):
    pass


class RepositoryModel(Base):
    __tablename__ = "repositories"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    source = Column(String(1024), nullable=False)
    source_type = Column(String(10), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    total_files = Column(Integer, default=0)
    total_lines = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    languages = Column(Text, default="{}")
    functions = Column(Integer, default=0)
    classes = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    error_message = Column(Text, nullable=True)
    indexed_path = Column(String(1024), nullable=True)


class CodeChunkModel(Base):
    __tablename__ = "code_chunks"

    id = Column(String(36), primary_key=True)
    repo_id = Column(String(36), nullable=False, index=True)
    file_path = Column(String(1024), nullable=False)
    language = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    start_line = Column(Integer, nullable=False)
    end_line = Column(Integer, nullable=False)
    chunk_type = Column(String(20), nullable=False)
    name = Column(String(255), nullable=True)
    docstring = Column(Text, nullable=True)
    imports_json = Column(Text, default="[]")
    tokens = Column(Integer, default=0)
    embedding_id = Column(Integer, nullable=True)


class IndexingTaskModel(Base):
    __tablename__ = "indexing_tasks"

    id = Column(String(36), primary_key=True)
    repo_id = Column(String(36), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="pending")
    progress = Column(Float, default=0.0)
    total_files = Column(Integer, default=0)
    processed_files = Column(Integer, default=0)
    current_file = Column(String(1024), nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)


class Database:
    def __init__(self):
        settings = get_settings()
        db_path = settings.DATA_DIR / "codenexus.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{db_path}", echo=settings.DEBUG)
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        return self.SessionLocal()

    def store_repository(self, repo_data: Dict[str, Any]) -> None:
        with self.get_session() as session:
            model = RepositoryModel(
                id=repo_data["id"],
                name=repo_data["name"],
                source=repo_data["source"],
                source_type=repo_data["source_type"],
                status=repo_data.get("status", "pending"),
                total_files=repo_data.get("total_files", 0),
                total_lines=repo_data.get("total_lines", 0),
                total_chunks=repo_data.get("total_chunks", 0),
                languages=json.dumps(repo_data.get("languages", {})),
                functions=repo_data.get("functions", 0),
                classes=repo_data.get("classes", 0),
                created_at=repo_data.get("created_at", datetime.now(timezone.utc)),
                updated_at=repo_data.get("updated_at", datetime.now(timezone.utc)),
                error_message=repo_data.get("error_message"),
                indexed_path=repo_data.get("indexed_path"),
            )
            session.merge(model)
            session.commit()

    def get_repository(self, repo_id: str) -> Optional[Dict[str, Any]]:
        with self.get_session() as session:
            model = session.query(RepositoryModel).filter(RepositoryModel.id == repo_id).first()
            if not model:
                return None
            return self._repo_to_dict(model)

    def list_repositories(self) -> List[Dict[str, Any]]:
        with self.get_session() as session:
            models = session.query(RepositoryModel).order_by(RepositoryModel.created_at.desc()).all()
            return [self._repo_to_dict(m) for m in models]

    def delete_repository(self, repo_id: str) -> bool:
        with self.get_session() as session:
            repo = session.query(RepositoryModel).filter(RepositoryModel.id == repo_id).first()
            if not repo:
                return False
            session.query(CodeChunkModel).filter(CodeChunkModel.repo_id == repo_id).delete()
            session.query(IndexingTaskModel).filter(IndexingTaskModel.repo_id == repo_id).delete()
            session.delete(repo)
            session.commit()
            return True

    def update_repository(self, repo_id: str, **kwargs: Any) -> None:
        with self.get_session() as session:
            model = session.query(RepositoryModel).filter(RepositoryModel.id == repo_id).first()
            if model:
                for key, value in kwargs.items():
                    if key == "languages" and isinstance(value, dict):
                        value = json.dumps(value)
                    if hasattr(model, key):
                        setattr(model, key, value)
                model.updated_at = datetime.now(timezone.utc)
                session.commit()

    def store_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        with self.get_session() as session:
            for chunk in chunks:
                model = CodeChunkModel(
                    id=chunk["id"],
                    repo_id=chunk["repo_id"],
                    file_path=chunk["file_path"],
                    language=chunk["language"],
                    content=chunk["content"],
                    start_line=chunk["start_line"],
                    end_line=chunk["end_line"],
                    chunk_type=chunk["chunk_type"],
                    name=chunk.get("name"),
                    docstring=chunk.get("docstring"),
                    imports_json=json.dumps(chunk.get("imports", [])),
                    tokens=chunk.get("tokens", 0),
                    embedding_id=chunk.get("embedding_id"),
                )
                session.merge(model)
            session.commit()

    def get_chunks_by_repo(self, repo_id: str) -> List[Dict[str, Any]]:
        with self.get_session() as session:
            models = session.query(CodeChunkModel).filter(CodeChunkModel.repo_id == repo_id).all()
            return [self._chunk_to_dict(m) for m in models]

    def get_chunk(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        with self.get_session() as session:
            model = session.query(CodeChunkModel).filter(CodeChunkModel.id == chunk_id).first()
            if not model:
                return None
            return self._chunk_to_dict(model)

    def store_task(self, task_data: Dict[str, Any]) -> None:
        with self.get_session() as session:
            model = IndexingTaskModel(**task_data)
            session.merge(model)
            session.commit()

    def update_task(self, task_id: str, **kwargs: Any) -> None:
        with self.get_session() as session:
            model = session.query(IndexingTaskModel).filter(IndexingTaskModel.id == task_id).first()
            if model:
                for key, value in kwargs.items():
                    if hasattr(model, key):
                        setattr(model, key, value)
                session.commit()

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        with self.get_session() as session:
            model = session.query(IndexingTaskModel).filter(IndexingTaskModel.id == task_id).first()
            if not model:
                return None
            return {c.key: getattr(model, c.key) for c in IndexingTaskModel.__table__.columns}

    @staticmethod
    def _repo_to_dict(model: RepositoryModel) -> Dict[str, Any]:
        return {
            "id": model.id,
            "name": model.name,
            "source": model.source,
            "source_type": model.source_type,
            "status": model.status,
            "total_files": model.total_files,
            "total_lines": model.total_lines,
            "total_chunks": model.total_chunks,
            "languages": json.loads(model.languages) if model.languages else {},
            "functions": model.functions,
            "classes": model.classes,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
            "error_message": model.error_message,
            "indexed_path": model.indexed_path,
        }

    @staticmethod
    def _chunk_to_dict(model: CodeChunkModel) -> Dict[str, Any]:
        return {
            "id": model.id,
            "repo_id": model.repo_id,
            "file_path": model.file_path,
            "language": model.language,
            "content": model.content,
            "start_line": model.start_line,
            "end_line": model.end_line,
            "chunk_type": model.chunk_type,
            "name": model.name,
            "docstring": model.docstring,
            "imports": json.loads(model.imports_json) if model.imports_json else [],
            "tokens": model.tokens,
            "embedding_id": model.embedding_id,
        }


_db: Optional[Database] = None


def get_db() -> Database:
    global _db
    if _db is None:
        _db = Database()
    return _db
