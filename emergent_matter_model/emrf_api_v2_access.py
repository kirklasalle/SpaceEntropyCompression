"""Load the FastAPI v2 application from source checkouts and installed wheels."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any


def _load_api_v2() -> Any:
    try:
        return importlib.import_module("emrf.interfaces.api_v2")
    except ModuleNotFoundError as exc:
        if exc.name not in {"emrf", "emrf.interfaces", "emrf.interfaces.api_v2"}:
            raise
        source_root = Path(__file__).resolve().parent / "src"
        if not source_root.is_dir():
            raise
        source_text = str(source_root)
        if source_text not in sys.path:
            sys.path.insert(0, source_text)
        return importlib.import_module("emrf.interfaces.api_v2")


_api_v2 = _load_api_v2()
API_V2_TOKEN_ENV = _api_v2.API_V2_TOKEN_ENV
app = _api_v2.app
create_app = _api_v2.create_app

__all__ = ["API_V2_TOKEN_ENV", "app", "create_app"]
