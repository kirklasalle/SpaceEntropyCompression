from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools import run_operational_certification as certification
from tools.run_operational_certification import main, run_certification


def test_controlled_operational_certification_retains_complete_evidence(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    receipt = workspace / "evidence" / "summary.json"

    result = run_certification(
        workspace=workspace,
        receipt=receipt,
        profile="test",
        repeats=1,
    )

    assert result["passed"] is True
    assert result["probe"] == {
        "observational_objects": 1,
        "observational_holdings": 1,
        "durable_runs": 1,
        "queued_jobs": 1,
        "prediction_commitments": 1,
    }
    assert all(check["passed"] for check in result["checks"].values())
    assert json.loads(receipt.read_text(encoding="utf-8")) == result
    data = result["checks"]["data_recovery"]["result"]
    state = result["checks"]["state_recovery"]["result"]
    assert data["objects_verified"] == 1
    assert data["holdings_verified"] == 1
    assert state["components"]["runs"] == 1
    assert state["components"]["jobs"] == 1
    assert state["components"]["prediction_commitments"] == 1
    assert (workspace / "evidence" / "data-recovery.json").is_file()
    assert (workspace / "evidence" / "state-recovery.json").is_file()


def test_operational_certification_is_non_destructive(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    receipt = workspace / "evidence" / "summary.json"
    assert (
        main(
            [
                "--workspace",
                str(workspace),
                "--receipt",
                str(receipt),
                "--profile",
                "test",
                "--repeats",
                "1",
            ]
        )
        == 0
    )

    with pytest.raises(FileExistsError, match="workspace already exists"):
        run_certification(
            workspace=workspace,
            receipt=receipt,
            profile="test",
            repeats=1,
        )


def test_operational_certification_retains_failure_and_continues_checks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = tmp_path / "workspace"
    receipt = workspace / "evidence" / "summary.json"

    def fail_data_setup(workspace: Path) -> object:
        del workspace
        raise OSError("injected data setup failure")

    monkeypatch.setattr(certification, "_prepare_data", fail_data_setup)

    result = run_certification(
        workspace=workspace,
        receipt=receipt,
        profile="test",
        repeats=1,
    )

    assert result["passed"] is False
    assert result["checks"]["data_recovery"] == {
        "passed": False,
        "error": {
            "type": "OSError",
            "message": "injected data setup failure",
        },
    }
    assert result["checks"]["state_recovery"]["passed"] is True
    assert result["checks"]["performance"]["passed"] is True
    assert json.loads(receipt.read_text(encoding="utf-8")) == result
