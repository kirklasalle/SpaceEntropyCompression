"""Resolve EMRF project and writable application paths."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def project_root() -> Path | None:
    """Return the source-checkout root, or ``None`` for an installed wheel."""
    override = os.environ.get("EMRF_PROJECT_ROOT")
    if override:
        root = Path(override).expanduser().resolve()
        if not (root / "emergent_matter_model").is_dir():
            raise ValueError(f"EMRF_PROJECT_ROOT is not a project checkout: {root}")
        return root
    candidate = Path(__file__).resolve().parent.parent
    if (candidate / "emergent_matter_model").is_dir() and (candidate / "data").is_dir():
        return candidate
    return None


def default_app_root() -> Path:
    """Return the platform-appropriate per-user EMRF application directory."""
    override = os.environ.get("EMRF_HOME")
    if override:
        return Path(override).expanduser().resolve()
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "EMRF"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "EMRF"
    base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "emrf"


def app_root() -> Path:
    """Return the checkout root when present, otherwise the user application root."""
    return project_root() or default_app_root()


def data_root() -> Path:
    """Return the observational data root without creating it."""
    override = os.environ.get("EMRF_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve()
    return app_root() / "data"


def resolve_data_path(value: str | Path) -> Path:
    """Resolve a manifest path against the configured data/application root."""
    path = Path(value)
    if path.is_absolute():
        return path
    parts = path.parts
    if parts and parts[0].lower() == "data":
        return data_root().joinpath(*parts[1:])
    return data_root() / path
