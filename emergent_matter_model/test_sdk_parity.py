"""Compatibility and parity tests for the typed public SDK foundation."""

from __future__ import annotations

import json

import pytest

import emrf_cli
import server
from emrf.runs import RunStore
from emrf.sdk import (
    DatasetInfo,
    EMRFClient,
    ErrorResponse,
    PredictionCommitment,
    ResourceNotFoundError,
    RunInfo,
    RunRequest,
    VerificationReport,
)


def test_public_sdk_contract_types_are_constructible():
    error = ErrorResponse("invalid_request", "bad input", {"field": "command"})
    dataset = DatasetInfo("sparc", "SPARC", "ok", "high")
    verification = VerificationReport("software", True, ({"passed": True},))
    prediction = PredictionCommitment(
        "20261010T000000000000Z-123456789abc",
        "test",
        "2026-10-10T00:00:00+00:00",
        "0" * 64,
        10,
        None,
        "application/json",
        "preregistered-prediction",
        False,
    )
    run = RunInfo(
        "20261010T000000000000Z-12345678",
        "compare-schwarzschild",
        ("--help",),
        "software",
        "succeeded",
        1,
        "2026-10-10T00:00:00+00:00",
        "2026-10-10T00:00:00+00:00",
        "2026-10-10T00:00:01+00:00",
        0,
        1.0,
        "0" * 64,
        None,
        None,
        {},
        {},
    )

    assert error.to_dict()["details"]["field"] == "command"
    assert dataset.dataset_id == "sparc"
    assert verification.all_passed
    assert not prediction.content_stored
    assert run.args == ("--help",)
    assert prediction.to_dict()["evidence_class"] == "preregistered-prediction"
    assert verification.to_dict()["checks"] == [{"passed": True}]
    assert dataset.to_dict()["dataset_id"] == "sparc"
    assert run.to_dict()["args"] == ["--help"]


def test_sdk_rejects_invalid_requests_with_stable_errors():
    with pytest.raises(ValueError, match="finite positive"):
        RunRequest("compare-schwarzschild", timeout=float("nan"))
    with pytest.raises(ResourceNotFoundError) as exc:
        EMRFClient().get_command("does-not-exist")

    assert str(exc.value) == "Unknown command: 'does-not-exist'"
    assert exc.value.as_response().to_dict() == {
        "code": "not_found",
        "message": "Unknown command: 'does-not-exist'",
        "details": {"resource": "command", "name": "does-not-exist"},
    }


def test_command_discovery_has_sdk_cli_rest_parity(capsys):
    direct = EMRFClient().list_commands("analysis").to_dict()["commands"]

    assert emrf_cli.main(["list", "--category", "analysis", "--json"]) == 0
    cli = json.loads(capsys.readouterr().out)

    server.app.config["TESTING"] = True
    rest_response = server.app.test_client().get(
        "/api/v1/commands?category=analysis"
    )
    rest = rest_response.get_json()["commands"]

    assert rest_response.status_code == 200
    assert cli == direct == rest


def test_durable_analysis_has_sdk_cli_rest_parity(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
    capfd,
):
    store = RunStore(tmp_path)
    monkeypatch.setattr("emrf_run_access.run_store", lambda: store)
    monkeypatch.setenv(server.RUN_ENV_FLAG, "1")
    request = RunRequest("compare-schwarzschild", ("--help",), timeout=120)

    direct = EMRFClient().run(request, capture=True)
    assert emrf_cli.main([
        "run",
        "--timeout",
        "120",
        "compare-schwarzschild",
        "--",
        "--help",
    ]) == 0
    cli_output = capfd.readouterr().out

    server.app.config["TESTING"] = True
    rest_response = server.app.test_client().post(
        "/api/v1/commands/compare-schwarzschild/run",
        json={"args": ["--help"], "timeout": 120},
    )
    rest = rest_response.get_json()
    records = store.list(limit=10)

    assert rest_response.status_code == 200
    assert rest["command"] == direct.command == "compare-schwarzschild"
    assert rest["args"] == list(direct.args) == ["--help"]
    assert rest["returncode"] == direct.returncode == 0
    assert rest["stdout"] == direct.stdout
    assert "Schwarzschild" in cli_output
    assert len(records) == 3
    assert all(record.command == request.command for record in records)
    assert all(record.args == request.args for record in records)
    assert all(record.status == "succeeded" for record in records)


def test_run_inspection_has_sdk_cli_rest_parity(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
    capsys,
):
    store = RunStore(tmp_path)
    monkeypatch.setattr("emrf_run_access.run_store", lambda: store)
    created = store.create("compare-schwarzschild", ["--help"])
    store.begin(created.run_id)
    store.finish(created.run_id, status="succeeded", returncode=0, duration_seconds=0.5)

    direct_detail = EMRFClient().get_run(created.run_id).to_dict()
    direct_list = EMRFClient().list_runs(limit=10).to_dict()["runs"]

    assert emrf_cli.main(["runs", "info", created.run_id]) == 0
    cli_detail = json.loads(capsys.readouterr().out)
    assert emrf_cli.main(["runs", "list", "--limit", "10", "--json"]) == 0
    cli_list = json.loads(capsys.readouterr().out)

    server.app.config["TESTING"] = True
    client = server.app.test_client()
    rest_detail = client.get(f"/api/v1/runs/{created.run_id}").get_json()
    rest_list = client.get("/api/v1/runs?limit=10").get_json()["runs"]

    assert cli_detail == direct_detail == rest_detail
    assert cli_list == direct_list == rest_list
    assert "path" not in direct_detail

    with pytest.raises(ResourceNotFoundError) as exc:
        EMRFClient().get_run("20261010T000000000000Z-00000000")
    assert exc.value.as_response().details["resource"] == "run"


def test_physics_verification_has_sdk_cli_rest_parity(capsys):
    direct = EMRFClient().verify_physics().to_dict()

    assert emrf_cli.main(["verify", "physics", "--json"]) == 0
    cli = json.loads(capsys.readouterr().out)

    server.app.config["TESTING"] = True
    response = server.app.test_client().get("/api/v1/verification/physics")
    rest = response.get_json()

    assert response.status_code == 200
    assert cli == direct == rest
    assert direct["all_passed"]
