"""Load the layered data library from source checkouts and installed wheels."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any


def _load_module(name: str) -> Any:
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError as exc:
        if exc.name not in {"emrf", name}:
            raise
        source_root = Path(__file__).resolve().parent / "src"
        if not source_root.is_dir():
            raise
        source_text = str(source_root)
        if source_text not in sys.path:
            sys.path.insert(0, source_text)
        return importlib.import_module(name)


def data_library() -> Any:
    """Return a data-library service without requiring checkout installation."""
    return _load_module("emrf.data").DataLibrary()


def data_errors() -> Any:
    """Return typed data errors from either supported package layout."""
    return _load_module("emrf.core.errors")
