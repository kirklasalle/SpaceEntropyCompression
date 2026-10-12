from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import emrf_cli
import pytest
import server
from emrf.core.errors import IntegrityError
from emrf.interfaces.api_v2 import API_V2_TOKEN_ENV, app
from emrf.knowledge import KnowledgeStore
from emrf.recovery import StateRecoveryManager
from emrf.runs import RunStore
from emrf.sdk import EMRFClient
from emrf.validation.preregistration import commit_json_prediction
from fastapi.testclient import TestClient


def _manager(tmp_path: Path) -> StateRecoveryManager:
    runs = RunStore(tmp_path / "active" / "runs")
    record = runs.create("analysis", ["--value", "1"])
    (record.path / "result.json").write_text('{"value": 1}\n', encoding="utf-8")
    runs.enqueue("analysis", ["--queued"], max_attempts=2)
    predictions = tmp_path / "active" / "predictions"
    commit_json_prediction(
        {"observable": 42},
        label="Recovery prediction",
        root=predictions,
    )
    knowledge = KnowledgeStore(tmp_path / "active" / "knowledge" / "GRAPH_MEMORY.json")
    assert knowledge.validate()["valid"] is True
    return StateRecoveryManager(
        runs=runs,
        predictions_root=predictions,
        knowledge=knowledge,
    )


def test_application_state_backup_restore_and_drill(tmp_path: Path) -> None:
    manager = _manager(tmp_path)
    backup = tmp_path / "backup"

    manifest = manager.create(backup)
    verified = manager.verify(backup)
    restored = manager.restore(backup, tmp_path / "restored")
    receipt = tmp_path / "receipts" / "state-drill.json"
    drill = manager.drill(receipt, workspace=tmp_path / "workspace")

    assert manifest == verified
    assert manifest["components"]["runs"] == 1
    assert manifest["components"]["jobs"] == 1
    assert manifest["components"]["run_files"] >= 3
    assert manifest["components"]["prediction_commitments"] == 1
    assert restored["runs"] == 1
    assert restored["jobs"] == 1
    with sqlite3.connect(
        tmp_path / "restored" / "runs" / "registry.sqlite"
    ) as connection:
        run_path = Path(connection.execute("SELECT run_path FROM runs").fetchone()[0])
    assert run_path.parent == tmp_path / "restored" / "runs"
    assert drill["status"] == "passed"
    assert drill["rpo_met"] is True
    assert drill["rto_met"] is True
    assert drill["source_changed_during_drill"] is False
    assert json.loads(receipt.read_text(encoding="utf-8")) == drill
    assert list((tmp_path / "workspace").iterdir()) == []


def test_application_state_backup_detects_tampering(tmp_path: Path) -> None:
    manager = _manager(tmp_path)
    backup = tmp_path / "backup"
    manager.create(backup)
    artifact = next(
        path
        for path in (backup / "runs").rglob("result.json")
        if path.is_file()
    )
    artifact.write_text('{"value": 2}\n', encoding="utf-8")

    with pytest.raises(IntegrityError, match="hash differs"):
        manager.verify(backup)


def test_application_state_restore_is_non_destructive(tmp_path: Path) -> None:
    manager = _manager(tmp_path)
    backup = tmp_path / "backup"
    manager.create(backup)
    destination = tmp_path / "restored"
    destination.mkdir()

    with pytest.raises(FileExistsError, match="already exists"):
        manager.restore(backup, destination)
    with pytest.raises(ValueError, match="must be isolated"):
        manager.restore(backup, manager.runs.root / "nested-restore")


def test_application_state_backup_fails_if_source_changes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manager = _manager(tmp_path)
    original = manager._copy_predictions

    def copy_with_concurrent_commit(destination: Path) -> None:
        original(destination)
        commit_json_prediction(
            {"observable": 43},
            label="Concurrent prediction",
            root=manager.predictions_root,
        )

    monkeypatch.setattr(manager, "_copy_predictions", copy_with_concurrent_commit)
    destination = tmp_path / "changed-backup"

    with pytest.raises(IntegrityError, match="changed while"):
        manager.create(destination)

    assert not destination.exists()


def test_application_state_backup_rejects_unsafe_manifest_path(
    tmp_path: Path,
) -> None:
    manager = _manager(tmp_path)
    backup = tmp_path / "backup"
    manager.create(backup)
    manifest_path = backup / "state_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files"][0]["path"] = "../escape"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(IntegrityError, match="invalid file metadata"):
        manager.verify(backup)


def test_application_state_drill_retains_failed_rto_receipt(tmp_path: Path) -> None:
    manager = _manager(tmp_path)
    receipt = tmp_path / "failed.json"

    with pytest.raises(IntegrityError, match="recovery objectives"):
        manager.drill(receipt, rto_seconds=1e-12)

    recorded = json.loads(receipt.read_text(encoding="utf-8"))
    assert recorded["status"] == "failed"
    assert recorded["rto_met"] is False


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("rpo_seconds", 0),
        ("rpo_seconds", float("nan")),
        ("rto_seconds", True),
        ("rto_seconds", float("inf")),
    ),
)
def test_application_state_drill_rejects_invalid_objectives(
    tmp_path: Path,
    field: str,
    value: object,
) -> None:
    with pytest.raises(ValueError, match=f"{field} must be positive"):
        _manager(tmp_path).drill(
            tmp_path / "receipt.json",
            **{field: value},
        )


def test_state_recovery_sdk_cli_and_rest_parity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    manager = _manager(tmp_path)
    monkeypatch.setattr(
        "emrf_recovery_access.recovery_manager",
        lambda: manager,
    )
    expected = EMRFClient().create_state_backup(tmp_path / "sdk-backup").to_dict()

    assert emrf_cli.main(
        ["recovery", "backup", str(tmp_path / "cli-backup")]
    ) == 0
    cli_result = json.loads(capsys.readouterr().out)

    monkeypatch.setenv(server.DATA_WRITE_ENV_FLAG, "1")
    with server.app.test_client() as client:
        flask_response = client.post(
            "/api/v1/recovery/backups",
            json={"destination": str(tmp_path / "flask-backup")},
        )
    assert flask_response.status_code == 201

    token = "state-recovery-token"
    monkeypatch.setenv(API_V2_TOKEN_ENV, token)
    with TestClient(app, raise_server_exceptions=False) as client:
        unauthorized = client.post(
            "/api/v2/recovery/backups",
            json={"destination": str(tmp_path / "unauthorized")},
        )
        response = client.post(
            "/api/v2/recovery/backups",
            headers={"Authorization": f"Bearer {token}"},
            json={"destination": str(tmp_path / "v2-backup")},
        )
    assert unauthorized.status_code == 401
    assert response.status_code == 201

    for result in (cli_result, flask_response.get_json(), response.json()):
        assert result["components"] == expected["components"]
        assert result["source_fingerprint"] == expected["source_fingerprint"]


def test_state_recovery_all_operations_route_through_sdk(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manager = _manager(tmp_path)
    monkeypatch.setattr(
        "emrf_recovery_access.recovery_manager",
        lambda: manager,
    )
    client = EMRFClient()
    backup = tmp_path / "backup"

    created = client.create_state_backup(str(backup)).to_dict()
    verified = client.verify_state_backup(str(backup)).to_dict()
    restored = client.restore_state_backup(
        str(backup),
        str(tmp_path / "restored"),
    ).to_dict()
    drilled = client.run_state_restore_drill(
        receipt=str(tmp_path / "receipt.json"),
        workspace=str(tmp_path / "workspace"),
    ).to_dict()

    assert created["source_fingerprint"] == verified["source_fingerprint"]
    assert created["components"] == verified["components"]
    assert restored["runs"] == 1
    assert drilled["status"] == "passed"
