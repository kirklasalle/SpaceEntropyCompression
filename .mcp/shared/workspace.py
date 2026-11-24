"""Workspace root and confined path resolution for EMRF MCP servers."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


def resolve_workspace_root(default: Optional[Path] = None) -> Path:
    """Return an existing workspace directory, honoring MCP_WORKSPACE_ROOT."""
    configured = os.environ.get("MCP_WORKSPACE_ROOT")
    root = Path(configured).expanduser() if configured else (default or Path.cwd())
    try:
        resolved = root.resolve(strict=True)
    except OSError as exc:
        raise ValueError(f"MCP workspace root does not exist: {root}") from exc
    if not resolved.is_dir():
        raise ValueError(f"MCP workspace root is not a directory: {resolved}")
    return resolved


def resolve_workspace_path(root: Path, relative_path: str) -> Path:
    """Resolve a path inside ``root``, rejecting traversal and symlink escapes."""
    if not isinstance(relative_path, str) or not relative_path.strip():
        raise ValueError("path must be non-empty text")
    if "\x00" in relative_path:
        raise ValueError("path must not contain NUL bytes")
    candidate_raw = Path(relative_path)
    if candidate_raw.is_absolute():
        raise ValueError("absolute paths are not permitted; pass a workspace-relative path")
    root_resolved = root.resolve(strict=True)
    resolved = (root_resolved / candidate_raw).resolve()
    if resolved != root_resolved and root_resolved not in resolved.parents:
        raise ValueError("path escapes workspace root")
    return resolved
