"""Load layered physics verification from source checkouts and installed wheels."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any, TypedDict, cast


class PhysicsCheck(TypedDict):
    name: str
    measured: float
    expected: float
    unit: str
    relative_error: float
    relative_tolerance: float
    passed: bool
    reference: str
    evidence_class: str
    limitation: str | None


class PhysicsVerificationReport(TypedDict):
    evidence_class: str
    constants_reference: str
    all_passed: bool
    checks: list[PhysicsCheck]


def _load_verification() -> Any:
    try:
        return importlib.import_module("emrf.physics.verification")
    except ModuleNotFoundError as exc:
        if exc.name not in {"emrf", "emrf.physics", "emrf.physics.verification"}:
            raise
        source_root = Path(__file__).resolve().parent / "src"
        if not source_root.is_dir():
            raise
        source_text = str(source_root)
        if source_text not in sys.path:
            sys.path.insert(0, source_text)
        return importlib.import_module("emrf.physics.verification")


def known_limit_report() -> PhysicsVerificationReport:
    return cast(PhysicsVerificationReport, _load_verification().known_limit_report())
