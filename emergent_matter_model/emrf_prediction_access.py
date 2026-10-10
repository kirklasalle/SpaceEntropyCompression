"""Load prediction preregistration from checkouts and installed wheels."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any


def _module() -> Any:
    try:
        return importlib.import_module("emrf.validation.preregistration")
    except ModuleNotFoundError as exc:
        if exc.name not in {
            "emrf",
            "emrf.validation",
            "emrf.validation.preregistration",
        }:
            raise
        source_root = Path(__file__).resolve().parent / "src"
        if not source_root.is_dir():
            raise
        source_text = str(source_root)
        if source_text not in sys.path:
            sys.path.insert(0, source_text)
        return importlib.import_module("emrf.validation.preregistration")


def commit_prediction_file(path: str | Path, *, label: str) -> dict[str, Any]:
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"Prediction file not found: {source}")
    return _module().commit_prediction(
        source.read_bytes(),
        label=label,
        source_name=source.name,
    )


def verify_prediction_file(
    commitment_id: str,
    path: str | Path,
) -> dict[str, Any]:
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"Prediction file not found: {source}")
    return _module().verify_prediction(commitment_id, source.read_bytes())


def commit_json_prediction(
    prediction: Any,
    *,
    label: str,
    root: str | Path | None = None,
) -> dict[str, Any]:
    return _module().commit_json_prediction(prediction, label=label, root=root)


def verify_json_prediction(
    commitment_id: str,
    prediction: Any,
    *,
    root: str | Path | None = None,
) -> dict[str, Any]:
    return _module().verify_json_prediction(commitment_id, prediction, root=root)


def get_commitment(
    commitment_id: str,
    *,
    root: str | Path | None = None,
) -> dict[str, Any]:
    return _module().get_commitment(commitment_id, root=root)


def commit_prediction(
    content: bytes,
    *,
    label: str,
    source_name: str | None = None,
    root: str | Path | None = None,
) -> dict[str, Any]:
    return _module().commit_prediction(
        content,
        label=label,
        source_name=source_name,
        root=root,
    )


def verify_prediction(
    commitment_id: str,
    content: bytes,
    *,
    root: str | Path | None = None,
) -> dict[str, Any]:
    return _module().verify_prediction(commitment_id, content, root=root)
