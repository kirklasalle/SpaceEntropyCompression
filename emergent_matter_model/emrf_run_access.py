"""Load the layered run store from source checkouts and installed wheels."""

from __future__ import annotations

import importlib
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


def _load_runs() -> Any:
    try:
        return importlib.import_module("emrf.runs")
    except ModuleNotFoundError as exc:
        if exc.name not in {"emrf", "emrf.runs"}:
            raise
        source_root = Path(__file__).resolve().parent / "src"
        if not source_root.is_dir():
            raise
        source_text = str(source_root)
        if source_text not in sys.path:
            sys.path.insert(0, source_text)
        return importlib.import_module("emrf.runs")


def run_store(root: str | Path | None = None) -> Any:
    return _load_runs().RunStore(root)


def public_record(record: Any) -> dict[str, Any]:
    if not is_dataclass(record):
        raise TypeError("record must be a dataclass")
    value = asdict(record)
    value.pop("path", None)
    return value


def run_errors() -> Any:
    _load_runs()
    return importlib.import_module("emrf.core.errors")
