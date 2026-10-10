"""Load validation certificates from source checkouts and installed wheels."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any, TypedDict, cast


class ValidationCheck(TypedDict):
    name: str
    metric: str
    measured: float
    expected: float
    lower_bound: float
    upper_bound: float
    passed: bool
    reference: str
    evidence_class: str
    limitation: str | None


class InferenceValidationReport(TypedDict):
    evidence_class: str
    all_passed: bool
    realizations: int
    random_seed: int
    checks: list[ValidationCheck]
    truths: dict[str, float]
    limitations: list[str]


class EngineValidationReport(TypedDict):
    evidence_class: str
    all_passed: bool
    checks: list[ValidationCheck]
    limitations: list[str]


def _load_validation() -> Any:
    try:
        return importlib.import_module("emrf.validation")
    except ModuleNotFoundError as exc:
        if exc.name not in {"emrf", "emrf.validation", "emrf.validation.inference"}:
            raise
        source_root = Path(__file__).resolve().parent / "src"
        if not source_root.is_dir():
            raise
        source_text = str(source_root)
        if source_text not in sys.path:
            sys.path.insert(0, source_text)
        return importlib.import_module("emrf.validation")


def inference_validation_report() -> InferenceValidationReport:
    return cast(
        InferenceValidationReport,
        _load_validation().inference_validation_report(),
    )


def engine_validation_report() -> EngineValidationReport:
    return cast(
        EngineValidationReport,
        _load_validation().engine_validation_report(),
    )
