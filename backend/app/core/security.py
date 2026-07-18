"""Security utilities: path validation, input sanitization."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import List

from .exceptions import PathTraversalError


def validate_path(path: str | Path, base_dir: Path) -> Path:
    """Validate and resolve a path, ensuring it stays within base_dir."""
    resolved = Path(path).resolve()
    base_resolved = base_dir.resolve()
    if not str(resolved).startswith(str(base_resolved)):
        raise PathTraversalError(str(path))
    return resolved


def sanitize_input(text: str, max_length: int = 10000) -> str:
    """Sanitize string input."""
    text = text.strip()
    if len(text) > max_length:
        text = text[:max_length]
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    return text


def is_safe_git_url(url: str) -> bool:
    """Check if a Git URL is safe to clone."""
    url = url.strip()
    safe_patterns = [
        r"^https://github\.com/[\w\-\.]+/[\w\-\.]+(\.git)?$",
        r"^https://gitlab\.com/[\w\-\.]+/[\w\-\.]+(\.git)?$",
        r"^https://bitbucket\.org/[\w\-\.]+/[\w\-\.]+(\.git)?$",
        r"^git@github\.com:[\w\-\.]+/[\w\-\.]+(\.git)?$",
        r"^git@gitlab\.com:[\w\-\.]+/[\w\-\.]+(\.git)?$",
    ]
    return any(re.match(p, url) for p in safe_patterns)


def run_git_command(args: List[str], cwd: Path, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run a Git command safely with shell=False."""
    cmd = ["git"] + args
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
        shell=False,
    )


def is_git_available() -> bool:
    """Check if git is installed."""
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            shell=False,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_default_branch(repo_path: Path) -> str:
    """Get the default branch of a git repository."""
    result = run_git_command(["symbolic-ref", "refs/remotes/origin/HEAD", "--short"], cwd=repo_path)
    if result.returncode == 0:
        return result.stdout.strip().replace("origin/", "")
    return "main"
