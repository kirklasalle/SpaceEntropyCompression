"""Load the typed SDK from source checkouts and installed wheels."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any


def _load_sdk() -> Any:
    try:
        return importlib.import_module("emrf.sdk")
    except ModuleNotFoundError as exc:
        if exc.name not in {"emrf", "emrf.sdk"}:
            raise
        source_root = Path(__file__).resolve().parent / "src"
        if not source_root.is_dir():
            raise
        source_text = str(source_root)
        if source_text not in sys.path:
            sys.path.insert(0, source_text)
        return importlib.import_module("emrf.sdk")


_sdk = _load_sdk()
EMRFClient = _sdk.EMRFClient
RunRequest = _sdk.RunRequest

__all__ = ["EMRFClient", "RunRequest"]
