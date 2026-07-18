"""Tests for code parsing service."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from app.services.parsing import (
    count_tokens_approximate,
    detect_language,
    extract_code_entities,
    scan_repository,
    should_ignore,
)


class TestDetectLanguage:
    def test_python_file(self):
        assert detect_language("test.py") == "python"

    def test_javascript_file(self):
        assert detect_language("app.js") == "javascript"
        assert detect_language("component.jsx") == "javascript"

    def test_typescript_file(self):
        assert detect_language("index.ts") == "typescript"
        assert detect_language("component.tsx") == "typescript"

    def test_java_file(self):
        assert detect_language("Main.java") == "java"

    def test_rust_file(self):
        assert detect_language("main.rs") == "rust"

    def test_go_file(self):
        assert detect_language("main.go") == "go"

    def test_dockerfile(self):
        assert detect_language("Dockerfile") == "dockerfile"

    def test_unknown_file(self):
        assert detect_language("unknown.xyz") == "text"


class TestShouldIgnore:
    def test_git_directory(self):
        assert should_ignore(".git/config", [".git"]) is True

    def test_node_modules(self):
        assert should_ignore("node_modules/package/index.js", ["node_modules"]) is True

    def test_pyc_file(self):
        assert should_ignore("module/__pycache__/test.cpython-311.pyc", ["__pycache__", "*.pyc"]) is True

    def test_normal_file(self):
        assert should_ignore("src/main.py", [".git", "node_modules"]) is False

    def test_nested_ignore(self):
        assert should_ignore("src/node_modules/package/index.js", ["node_modules"]) is True


class TestScanRepository:
    def test_scan_local_repo(self, sample_repo):
        files = scan_repository(str(sample_repo))
        assert len(files) >= 3
        paths = [f["path"] for f in files]
        assert "utils.py" in paths
        assert "app.js" in paths

    def test_scan_respects_ignore(self, sample_repo):
        (sample_repo / "node_modules").mkdir()
        (sample_repo / "node_modules" / "pkg.js").write_text("module.exports = {};")
        files = scan_repository(str(sample_repo))
        paths = [f["path"] for f in files]
        assert "node_modules/pkg.js" not in paths

    def test_scan_empty_repo(self, tmp_path):
        files = scan_repository(str(tmp_path))
        assert len(files) == 0


class TestExtractCodeEntities:
    def test_extract_python_functions(self):
        code = '''def hello():
    """Say hello."""
    return "hello"

def world():
    return "world"
'''
        blocks, stats = extract_code_entities(code, "python", "test.py")
        assert stats["functions"] >= 1
        func_names = [b["name"] for b in blocks if b["type"] == "function"]
        assert "hello" in func_names

    def test_extract_python_class(self):
        code = '''class MyClass:
    """My class."""
    def __init__(self):
        self.x = 1

    def method(self):
        return self.x
'''
        blocks, stats = extract_code_entities(code, "python", "test.py")
        assert stats["classes"] >= 1

    def test_extract_empty_code(self):
        blocks, stats = extract_code_entities("", "python", "empty.py")
        assert len(blocks) == 0

    def test_extract_unsupported_language(self):
        code = "some random text without structure"
        blocks, stats = extract_code_entities(code, "unknown", "file.txt")
        assert len(blocks) >= 0


class TestCountTokensApproximate:
    def test_empty_string(self):
        assert count_tokens_approximate("") == 0

    def test_simple_text(self):
        assert count_tokens_approximate("hello world") > 0

    def test_code_text(self):
        code = "def hello():\n    return 'world'"
        assert count_tokens_approximate(code) > 0
