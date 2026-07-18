"""API dependencies."""

from __future__ import annotations

from ..infrastructure.database import Database, get_db


def get_database() -> Database:
    return get_db()
