"""Integration tests for API endpoints."""

from __future__ import annotations

import os
import shutil
import tempfile

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def setup_test_env(tmp_path):
    """Set up test environment."""
    os.environ["DATA_DIR"] = str(tmp_path / "data")
    os.environ["REPOS_DIR"] = str(tmp_path / "repos")
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.makedirs(tmp_path / "data", exist_ok=True)
    os.makedirs(tmp_path / "repos", exist_ok=True)
    yield


@pytest.fixture
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "CodeNexus"


class TestRepoEndpoints:
    def test_import_local_repo(self, client, sample_repo):
        response = client.post("/api/repos/import", json={
            "source": str(sample_repo),
            "source_type": "local",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "sample_repo"
        assert data["status"] == "pending"

    def test_import_nonexistent_path(self, client):
        response = client.post("/api/repos/import", json={
            "source": "/nonexistent/path",
            "source_type": "local",
        })
        assert response.status_code == 400

    def test_list_repos(self, client):
        response = client.get("/api/repos")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_import_and_delete(self, client, sample_repo):
        import_resp = client.post("/api/repos/import", json={
            "source": str(sample_repo),
            "source_type": "local",
        })
        repo_id = import_resp.json()["id"]

        delete_resp = client.delete(f"/api/repos/{repo_id}")
        assert delete_resp.status_code == 200

        get_resp = client.get(f"/api/repos/{repo_id}/status")
        assert get_resp.status_code == 404

    def test_delete_nonexistent(self, client):
        response = client.delete("/api/repos/nonexistent-id")
        assert response.status_code == 404


class TestSearchEndpoints:
    def test_search_empty_index(self, client):
        response = client.post("/api/search", json={
            "query": "test query",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["results"] == []
        assert data["total_results"] == 0

    def test_search_explain_empty(self, client):
        response = client.post("/api/search/explain", json={
            "query": "test query",
        })
        assert response.status_code == 200
        data = response.json()
        assert "explanation" in data

    def test_indexing_status_nonexistent(self, client):
        response = client.get("/api/indexing/nonexistent/status")
        assert response.status_code == 404


class TestSearchValidation:
    def test_empty_query(self, client):
        response = client.post("/api/search", json={"query": ""})
        assert response.status_code == 422

    def test_invalid_top_k(self, client):
        response = client.post("/api/search", json={"query": "test", "top_k": 0})
        assert response.status_code == 422

    def test_top_k_too_large(self, client):
        response = client.post("/api/search", json={"query": "test", "top_k": 200})
        assert response.status_code == 422
