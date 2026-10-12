"""Run recurring recovery and performance certification on controlled state."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import tempfile
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MODEL_ROOT = ROOT / "emergent_matter_model"
SOURCE_ROOT = MODEL_ROOT / "src"
for source in (MODEL_ROOT, SOURCE_ROOT):
    source_text = str(source)
    if source_text not in sys.path:
        sys.path.insert(0, source_text)

from emrf.data import DataLibrary
from emrf.knowledge import KnowledgeStore
from emrf.performance import PerformanceBaselineRunner
from emrf.recovery import StateRecoveryManager
from emrf.runs import RunStore
from emrf.validation.preregistration import commit_json_prediction
from emrf_version import __version__

_SCHEMA_VERSION = "1.0.0"


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Certification receipt already exists: {path}")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}-",
        suffix=".part",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            json.dump(value, output, indent=2, sort_keys=True, allow_nan=False)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _capture(operation: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        result = operation()
    # This process boundary must retain a receipt for every operational failure.
    except Exception as exc:  # noqa: BLE001
        return {
            "passed": False,
            "error": {
                "type": type(exc).__name__,
                "message": str(exc),
            },
        }
    return {
        "passed": bool(result.get("passed", result.get("status") == "passed")),
        "result": result,
    }


def _prepare_data(workspace: Path) -> DataLibrary:
    library = DataLibrary(root=workspace / "active" / "data")
    stored = library.store.put_bytes(b"EMRF controlled operational observation\n")
    library.store.register_holding(
        "operational-certification",
        "1.0.0",
        "observation.txt",
        stored,
        citation="EMRF controlled operational certification fixture",
        licence="CC0-1.0",
        metadata={"synthetic": True, "purpose": "recovery-certification"},
    )
    return library


def _prepare_state(workspace: Path) -> StateRecoveryManager:
    active = workspace / "active"
    runs = RunStore(active / "runs")
    fixture_hash = hashlib.sha256(b"controlled-operational-probe").hexdigest()
    run = runs.create(
        "operational-certification",
        ["--controlled-probe"],
        inputs={"fixture": fixture_hash},
        seeds={"probe": 20261012},
    )
    (run.path / "result.json").write_text(
        '{"passed":true,"probe":"operational-certification"}\n',
        encoding="utf-8",
    )
    runs.enqueue(
        "operational-certification",
        ["--queued-probe"],
        max_attempts=2,
    )
    predictions = active / "predictions"
    commit_json_prediction(
        {"observable": "controlled-probe", "expected": 1.0},
        label="Operational certification prediction",
        root=predictions,
    )
    knowledge = KnowledgeStore()
    report = knowledge.validate()
    if not report["valid"]:
        raise RuntimeError("Scientific knowledge graph failed validation")
    return StateRecoveryManager(
        runs=runs,
        predictions_root=predictions,
        knowledge=knowledge,
    )


def _run_data_recovery(workspace: Path, evidence: Path) -> dict[str, Any]:
    return _prepare_data(workspace).run_restore_drill(
        receipt=evidence / "data-recovery.json",
        workspace=workspace / "data-recovery-workspace",
    )


def _run_state_recovery(workspace: Path, evidence: Path) -> dict[str, Any]:
    return _prepare_state(workspace).drill(
        evidence / "state-recovery.json",
        workspace=workspace / "state-recovery-workspace",
    )


def run_certification(
    *,
    workspace: Path,
    receipt: Path,
    profile: str,
    repeats: int,
) -> dict[str, Any]:
    if workspace.exists():
        raise FileExistsError(f"Certification workspace already exists: {workspace}")
    workspace.mkdir(parents=True)
    evidence = workspace / "evidence"
    evidence.mkdir()

    checks = {
        "data_recovery": _capture(
            lambda: _run_data_recovery(workspace, evidence)
        ),
        "state_recovery": _capture(
            lambda: _run_state_recovery(workspace, evidence)
        ),
        "performance": _capture(
            lambda: PerformanceBaselineRunner().run(
                profile=profile,
                repeats=repeats,
            )
        ),
    }
    result = {
        "schema_version": _SCHEMA_VERSION,
        "certified_at": datetime.now(timezone.utc).isoformat(),
        "emrf_version": __version__,
        "repository": os.environ.get("GITHUB_REPOSITORY"),
        "commit_sha": os.environ.get("GITHUB_SHA"),
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "platform": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "system": platform.system(),
            "machine": platform.machine(),
        },
        "probe": {
            "observational_objects": 1,
            "observational_holdings": 1,
            "durable_runs": 1,
            "queued_jobs": 1,
            "prediction_commitments": 1,
        },
        "checks": checks,
        "passed": all(check["passed"] for check in checks.values()),
    }
    _atomic_json(receipt, result)
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--profile", choices=("test", "standard"), default="standard")
    parser.add_argument("--repeats", type=int, default=2)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    workspace = args.workspace.expanduser().resolve()
    receipt = args.receipt.expanduser().resolve()
    result = run_certification(
        workspace=workspace,
        receipt=receipt,
        profile=args.profile,
        repeats=args.repeats,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
