"""Pytest fixtures for CodeNexus tests."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

# Set test environment before importing app
os.environ["DATA_DIR"] = tempfile.mkdtemp()
os.environ["REPOS_DIR"] = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["EMBEDDING_MODEL"] = "BAAI/bge-small-en-v1.5"
os.environ["DEBUG"] = "true"


@pytest.fixture(scope="session")
def sample_repo(tmp_path_factory) -> Path:
    """Create a sample repository for testing."""
    repo_dir = tmp_path_factory.mktemp("sample_repo")

    # Python file
    (repo_dir / "utils.py").write_text(
        '''"""Utility functions."""


def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


class Calculator:
    """A simple calculator class."""

    def __init__(self):
        self.history = []

    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result

    def subtract(self, a: float, b: float) -> float:
        """Subtract two numbers."""
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result

    def get_history(self) -> list:
        """Get calculation history."""
        return self.history
'''
    )

    # Another Python file
    (repo_dir / "models.py").write_text(
        '''"""Data models."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """User model."""
    id: int
    name: str
    email: str
    age: Optional[int] = None

    def greet(self) -> str:
        """Return a greeting message."""
        return f"Hello, I am {self.name}!"


@dataclass
class Product:
    """Product model."""
    id: int
    name: str
    price: float
    description: Optional[str] = None

    def is_expensive(self, threshold: float = 100.0) -> bool:
        """Check if product is expensive."""
        return self.price > threshold
'''
    )

    # JavaScript file
    (repo_dir / "app.js").write_text(
        """/**
 * Main application module.
 */

function greet(name) {
    return `Hello, ${name}!`;
}

function calculateSum(numbers) {
    return numbers.reduce((sum, n) => sum + n, 0);
}

class EventEmitter {
    constructor() {
        this.listeners = {};
    }

    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    emit(event, data) {
        const callbacks = this.listeners[event] || [];
        callbacks.forEach(cb => cb(data));
    }
}

module.exports = { greet, calculateSum, EventEmitter };
"""
    )

    # README
    (repo_dir / "README.md").write_text(
        "# Sample Repository\n\nThis is a sample repository for testing CodeNexus.\n"
    )

    return repo_dir


@pytest.fixture
def client() -> Generator:
    """Create a FastAPI test client."""
    from app.main import app

    with TestClient(app) as c:
        yield c
