"""Load shared typed EMRF errors from source checkouts and installed wheels."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any


def emrf_errors() -> Any:
    try:
        return importlib.import_module("emrf.core.errors")
    except ModuleNotFoundError as exc:
        if exc.name not in {"emrf", "emrf.core", "emrf.core.errors"}:
            raise
        source_root = Path(__file__).resolve().parent / "src"
        if not source_root.is_dir():
            raise
        source_text = str(source_root)
        if source_text not in sys.path:
            sys.path.insert(0, source_text)
        return importlib.import_module("emrf.core.errors")
