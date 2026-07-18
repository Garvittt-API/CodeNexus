"""Code parsing service using tree-sitter and fallback strategies."""

from __future__ import annotations

import logging
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..core.config import get_settings
from ..core.security import validate_path

logger = logging.getLogger(__name__)

LANGUAGE_MAP: Dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "c",
    ".h": "c",
    ".hpp": "cpp",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
    ".r": "r",
    ".R": "r",
    ".lua": "lua",
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "zsh",
    ".sql": "sql",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".less": "less",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".xml": "xml",
    ".md": "markdown",
    ".txt": "text",
    ".dockerfile": "dockerfile",
    "Dockerfile": "dockerfile",
    ".env": "env",
    ".tf": "hcl",
    ".hcl": "hcl",
    ".vue": "vue",
    ".svelte": "svelte",
    ".ex": "elixir",
    ".exs": "elixir",
    ".erl": "erlang",
    ".hs": "haskell",
    ".dart": "dart",
    ".zig": "zig",
    ".nim": "nim",
    ".crystal": "crystal",
    ".jl": "julia",
    ".ml": "ocaml",
    ".mli": "ocaml",
}

# Tree-sitter language name mapping
TS_LANGUAGE_MAP: Dict[str, str] = {
    "python": "python",
    "javascript": "javascript",
    "typescript": "typescript",
    "typescriptreact": "typescript",
    "javascriptreact": "javascript",
    "java": "java",
    "cpp": "cpp",
    "c": "c",
    "go": "go",
    "rust": "rust",
    "ruby": "ruby",
    "php": "php",
    "swift": "swift",
    "kotlin": "kotlin",
    "scala": "scala",
    "bash": "bash",
    "html": "html",
    "css": "css",
    "json": "json",
    "yaml": "yaml",
    "toml": "toml",
}

# Node types that represent code blocks in tree-sitter
FUNCTION_NODE_TYPES = {
    "python": ["function_definition", "async_function_definition"],
    "javascript": ["function_declaration", "arrow_function", "method_definition"],
    "typescript": ["function_declaration", "arrow_function", "method_definition", "abstract_method_definition"],
    "java": ["method_declaration", "constructor_declaration"],
    "cpp": ["function_definition", "declaration"],
    "c": ["function_definition", "declaration"],
    "go": ["function_declaration", "method_declaration"],
    "rust": ["function_item", "impl_item"],
    "ruby": ["method", "singleton_method"],
}

CLASS_NODE_TYPES = {
    "python": ["class_definition"],
    "javascript": ["class_declaration"],
    "typescript": ["class_declaration", "abstract_class_declaration"],
    "java": ["class_declaration", "interface_declaration", "enum_declaration"],
    "cpp": ["class_specifier", "struct_specifier"],
    "c": ["struct_specifier"],
    "go": ["type_declaration"],
    "rust": ["impl_item", "struct_item", "enum_item", "trait_item"],
    "ruby": ["class", "module"],
}

IMPORT_NODE_TYPES = {
    "python": ["import_statement", "import_from_statement"],
    "javascript": ["import_statement", "require_statement"],
    "typescript": ["import_statement", "import_alias"],
    "java": ["import_declaration"],
    "go": ["import_declaration"],
    "rust": ["use_declaration"],
    "ruby": ["call"],  # require/include
}


def detect_language(file_path: str) -> str:
    """Detect language from file extension or content."""
    path = Path(file_path)
    ext = path.suffix.lower()
    if ext in LANGUAGE_MAP:
        return LANGUAGE_MAP[ext]
    if path.name in LANGUAGE_MAP:
        return LANGUAGE_MAP[path.name]
    if path.name.lower() == "dockerfile":
        return "dockerfile"
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            first_line = f.readline().strip()
            if first_line.startswith("#!"):
                if "python" in first_line:
                    return "python"
                if "bash" in first_line or "sh" in first_line:
                    return "bash"
                if "node" in first_line:
                    return "javascript"
    except Exception:
        pass
    return "text"


def should_ignore(file_path: str, ignore_patterns: List[str]) -> bool:
    """Check if a file should be ignored based on patterns."""
    path = Path(file_path)
    for part in path.parts:
        for pattern in ignore_patterns:
            if pattern.startswith("*."):
                if part.endswith(pattern[1:]):
                    return True
            elif part == pattern:
                return True
    return False


def get_file_size_mb(file_path: str) -> float:
    try:
        return os.path.getsize(file_path) / (1024 * 1024)
    except OSError:
        return 0.0


def scan_repository(repo_path: str, ignore_patterns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Recursively scan a repository and return file information."""
    settings = get_settings()
    if ignore_patterns is None:
        ignore_patterns = settings.IGNORE_PATTERNS

    repo_dir = Path(repo_path)
    files = []

    for root, dirs, filenames in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if d not in ignore_patterns]

        for filename in filenames:
            file_path = Path(root) / filename
            rel_path = file_path.relative_to(repo_dir)

            if should_ignore(str(rel_path), ignore_patterns):
                continue
            if get_file_size_mb(str(file_path)) > settings.MAX_FILE_SIZE_MB:
                continue
            if not file_path.is_file():
                continue
            if file_path.is_symlink():
                try:
                    if not file_path.resolve().is_relative_to(repo_dir.resolve()):
                        continue
                except (OSError, ValueError):
                    continue

            language = detect_language(str(file_path))
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                line_count = content.count("\n") + 1
            except Exception:
                continue

            files.append({
                "path": str(rel_path),
                "absolute_path": str(file_path),
                "language": language,
                "lines": line_count,
                "size": file_path.stat().st_size,
            })

    return files


def extract_code_entities(
    content: str, language: str, file_path: str
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Extract code entities (functions, classes, imports) from source code.

    Returns (blocks, stats) where blocks are parseable code chunks.
    """
    lines = content.split("\n")
    stats = {"functions": 0, "classes": 0, "imports": []}

    blocks = _try_treesitter_parse(content, language, file_path, stats)

    if not blocks:
        blocks = _regex_fallback_parse(lines, language, file_path, stats)

    if not blocks:
        blocks = _sliding_window_parse(lines, file_path)

    return blocks, stats


def _try_treesitter_parse(
    content: str, language: str, file_path: str, stats: dict
) -> List[Dict[str, Any]]:
    """Attempt tree-sitter based parsing."""
    ts_lang = TS_LANGUAGE_MAP.get(language)
    if not ts_lang:
        return []

    try:
        import tree_sitter
        from tree_sitter import Language, Parser

        try:
            language_lib = tree_sitter.language(ts_lang)
        except Exception:
            return []

        parser = Parser(language_lib)
        tree = parser.parse(content.encode("utf-8"))

        blocks = []
        _walk_tree(tree.root_node, content, file_path, language, blocks, stats)
        return blocks

    except ImportError:
        logger.debug("tree-sitter not available, using fallback parsing")
        return []
    except Exception as e:
        logger.debug("tree-sitter parsing failed for %s: %s", file_path, e)
        return []


def _walk_tree(
    node: Any,
    content: str,
    file_path: str,
    language: str,
    blocks: List[Dict[str, Any]],
    stats: dict,
    depth: int = 0,
) -> None:
    """Walk tree-sitter AST and extract code blocks."""
    if depth > 50:
        return

    node_type = node.type
    func_types = FUNCTION_NODE_TYPES.get(language, [])
    class_types = CLASS_NODE_TYPES.get(language, [])
    import_types = IMPORT_NODE_TYPES.get(language, [])

    if node_type in func_types:
        name = _extract_name(node, language)
        docstring = _extract_docstring(node, content, language)
        block_text = node.text.decode("utf-8") if node.text else ""
        blocks.append({
            "type": "function",
            "name": name,
            "content": block_text,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "docstring": docstring,
            "file_path": file_path,
        })
        stats["functions"] += 1

    elif node_type in class_types:
        name = _extract_name(node, language)
        docstring = _extract_docstring(node, content, language)
        block_text = node.text.decode("utf-8") if node.text else ""
        blocks.append({
            "type": "class",
            "name": name,
            "content": block_text,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "docstring": docstring,
            "file_path": file_path,
        })
        stats["classes"] += 1

    elif node_type in import_types:
        import_text = node.text.decode("utf-8") if node.text else ""
        stats["imports"].append(import_text)

    for child in node.children:
        _walk_tree(child, content, file_path, language, blocks, stats, depth + 1)


def _extract_name(node: Any, language: str) -> Optional[str]:
    """Extract the name from a tree-sitter node."""
    for child in node.children:
        if child.type == "identifier":
            return child.text.decode("utf-8") if child.text else None
        if child.type == "name":
            return child.text.decode("utf-8") if child.text else None
    return None


def _extract_docstring(node: Any, content: str, language: str) -> Optional[str]:
    """Extract docstring from a function/class node."""
    if language == "python":
        for child in node.children:
            if child.type == "block":
                for stmt in child.children:
                    if stmt.type == "expression_statement":
                        for expr in stmt.children:
                            if expr.type == "string":
                                text = expr.text.decode("utf-8") if expr.text else ""
                                return text.strip("\"'").strip('"""').strip("'''")
    return None


def _regex_fallback_parse(
    lines: List[str], language: str, file_path: str, stats: dict
) -> List[Dict[str, Any]]:
    """Regex-based fallback parsing for unsupported languages."""
    blocks = []

    if language in ("python",):
        pattern = re.compile(r"^(?:async\s+)?def\s+(\w+)\s*\(", re.MULTILINE)
        for match in pattern.finditer("".join(lines)):
            start = lines[: match.group().count("\n")]
            start_line = len(start) + 1
            end_line = _find_block_end(lines, start_line - 1, language)
            block_content = "\n".join(lines[start_line - 1 : end_line])
            blocks.append({
                "type": "function",
                "name": match.group(1),
                "content": block_content,
                "start_line": start_line,
                "end_line": end_line,
                "docstring": None,
                "file_path": file_path,
            })
            stats["functions"] += 1

        class_pattern = re.compile(r"^class\s+(\w+)", re.MULTILINE)
        for match in class_pattern.finditer("".join(lines)):
            start = lines[: match.group().count("\n")]
            start_line = len(start) + 1
            end_line = _find_block_end(lines, start_line - 1, language)
            block_content = "\n".join(lines[start_line - 1 : end_line])
            blocks.append({
                "type": "class",
                "name": match.group(1),
                "content": block_content,
                "start_line": start_line,
                "end_line": end_line,
                "docstring": None,
                "file_path": file_path,
            })
            stats["classes"] += 1

    elif language in ("javascript", "typescript", "java", "cpp", "c", "go", "rust"):
        func_pattern = re.compile(
            r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\()|(?:public|private|protected|static)?\s*(?:async\s+)?(\w+)\s*\()",
            re.MULTILINE,
        )
        for match in func_pattern.finditer("".join(lines)):
            name = match.group(1) or match.group(2) or match.group(3)
            if not name:
                continue
            start = lines[: match.group().count("\n")]
            start_line = len(start) + 1
            end_line = _find_block_end(lines, start_line - 1, language)
            block_content = "\n".join(lines[start_line - 1 : end_line])
            blocks.append({
                "type": "function",
                "name": name,
                "content": block_content,
                "start_line": start_line,
                "end_line": end_line,
                "docstring": None,
                "file_path": file_path,
            })
            stats["functions"] += 1

    return blocks


def _find_block_end(lines: List[str], start: int, language: str) -> int:
    """Find the end of a code block using indentation tracking."""
    if start >= len(lines):
        return len(lines)

    base_indent = len(lines[start]) - len(lines[start].lstrip())
    for i in range(start + 1, len(lines)):
        line = lines[i].strip()
        if not line:
            continue
        current_indent = len(lines[i]) - len(lines[i].lstrip())
        if current_indent <= base_indent and line:
            return i
    return len(lines)


def _sliding_window_parse(
    lines: List[str], file_path: str, max_tokens: int = 512, overlap_tokens: int = 64
) -> List[Dict[str, Any]]:
    """Parse code using sliding window fallback."""
    settings = get_settings()
    max_tokens = settings.MAX_CHUNK_TOKENS
    overlap_tokens = settings.OVERLAP_TOKENS

    blocks = []
    chunk_size = max_tokens // 4  # approximate tokens per line
    overlap_size = overlap_tokens // 4

    if chunk_size < 10:
        chunk_size = 10
    if overlap_size < 2:
        overlap_size = 2

    i = 0
    while i < len(lines):
        end = min(i + chunk_size, len(lines))
        block_content = "\n".join(lines[i:end])
        if block_content.strip():
            blocks.append({
                "type": "block",
                "name": None,
                "content": block_content,
                "start_line": i + 1,
                "end_line": end,
                "docstring": None,
                "file_path": file_path,
            })
        i += chunk_size - overlap_size

    return blocks


def count_tokens_approximate(text: str) -> int:
    """Approximate token count (roughly 4 chars per token)."""
    return len(text) // 4
