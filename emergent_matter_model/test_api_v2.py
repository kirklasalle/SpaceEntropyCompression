"""Contract, authentication, and SDK parity tests for REST API v2."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import emrf_registry
import server
from emrf.runs import RunStore
from emrf.sdk import EMRFClient
from emrf_api_v2_access import API_V2_TOKEN_ENV, app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


def test_v2_health_and_generated_openapi(client: TestClient):
    health = client.get("/api/v2/health")
    assert health.status_code == 200
    assert health.json()["api_version"] == "v2"

    response = client.get("/api/v2/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["openapi"].startswith("3.")
    assert schema["info"]["title"] == "Emergent Matter Research Framework API"
    assert {
        "/api/v2/health",
        "/api/v2/commands",
        "/api/v2/commands/{name}",
        "/api/v2/commands/{name}/runs",
        "/api/v2/runs",
        "/api/v2/runs/{run_id}",
        "/api/v2/verification/physics",
        "/api/v2/verification/inference",
        "/api/v2/verification/engines",
    } <= set(schema["paths"])
    assert {
        "CommandInfo",
        "CommandListResponse",
        "ErrorResponse",
        "RunInfo",
        "RunRequest",
        "RunResult",
        "VerificationReport",
    } <= set(schema["components"]["schemas"])


def test_v2_command_discovery_matches_sdk(client: TestClient):
    direct = [
        command.to_dict()
        for command in EMRFClient().list_commands("analysis").commands
    ]
    response = client.get("/api/v2/commands", params={"category": "analysis"})

    assert response.status_code == 200
    assert response.json()["commands"] == direct
    assert response.json()["execution_enabled"] is False
    assert client.get("/api/v2/commands/fit-sparc").json()["category"] == "analysis"


def test_v2_command_errors_are_structured(client: TestClient):
    category = client.get("/api/v2/commands", params={"category": "unknown"})
    missing = client.get("/api/v2/commands/does-not-exist")

    assert category.status_code == 400
    assert category.json()["code"] == "invalid_request"
    assert "categories" in category.json()["details"]
    assert missing.status_code == 404
    assert missing.json() == {
        "code": "not_found",
        "message": "Unknown command: 'does-not-exist'",
        "details": {"resource": "command", "name": "does-not-exist"},
    }


def test_v2_execution_requires_configured_bearer_token(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.delenv(API_V2_TOKEN_ENV, raising=False)
    disabled = client.post(
        "/api/v2/commands/compare-schwarzschild/runs",
        json={"args": ["--help"]},
    )
    assert disabled.status_code == 403
    assert disabled.json()["code"] == "execution_disabled"

    monkeypatch.setenv(API_V2_TOKEN_ENV, "secret-token")
    missing = client.post(
        "/api/v2/commands/compare-schwarzschild/runs",
        json={"args": ["--help"]},
    )
    invalid = client.post(
        "/api/v2/commands/compare-schwarzschild/runs",
        headers={"Authorization": "Bearer wrong-token"},
        json={"args": ["--help"]},
    )
    assert missing.status_code == 401
    assert invalid.status_code == 401
    assert invalid.headers["www-authenticate"] == "Bearer"


def test_v2_durable_execution_and_run_reads_match_sdk(
    client: TestClient,
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
):
    store = RunStore(tmp_path)
    monkeypatch.setattr("emrf_run_access.run_store", lambda: store)
    monkeypatch.setenv(API_V2_TOKEN_ENV, "secret-token")

    response = client.post(
        "/api/v2/commands/compare-schwarzschild/runs",
        headers={"Authorization": "Bearer secret-token"},
        json={
            "args": ["--help"],
            "timeout": 120,
            "evidence_class": "software",
            "inputs": {},
            "seeds": {},
        },
    )
    result = response.json()
    record = store.get(result["run_id"])

    assert response.status_code == 200
    assert result["returncode"] == 0
    assert "Schwarzschild" in result["stdout"]
    assert record.status == "succeeded"
    assert record.args == ("--help",)

    direct = EMRFClient().get_run(record.run_id).to_dict()
    assert client.get(f"/api/v2/runs/{record.run_id}").json() == direct
    assert client.get("/api/v2/runs").json()["runs"] == [direct]


def test_v2_rejects_unsafe_or_invalid_execution(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv(API_V2_TOKEN_ENV, "secret-token")
    headers = {"Authorization": "Bearer secret-token"}

    interactive = client.post(
        "/api/v2/commands/viz3d/runs",
        headers=headers,
        json={},
    )
    invalid = client.post(
        "/api/v2/commands/compare-schwarzschild/runs",
        headers=headers,
        json={"timeout": 0, "unexpected": True},
    )

    assert interactive.status_code == 400
    assert interactive.json()["code"] == "invalid_request"
    assert invalid.status_code == 422
    assert invalid.json()["code"] == "validation_error"


def test_v2_physics_verification_matches_sdk(client: TestClient):
    direct = EMRFClient().verify_physics()
    expected = {
        "evidence_class": direct.evidence_class,
        "all_passed": direct.all_passed,
        "checks": [dict(check) for check in direct.checks],
        "metadata": dict(direct.metadata),
    }

    response = client.get("/api/v2/verification/physics")
    assert response.status_code == 200
    assert response.json() == expected


def test_v1_flask_application_remains_separate_and_healthy():
    server.app.config["TESTING"] = True
    response = server.app.test_client().get("/api/v1/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"
    assert "/api/v2/health" not in {rule.rule for rule in server.app.url_map.iter_rules()}


def test_doctor_tracks_api_v2_dependencies():
    report = emrf_registry.environment_report()

    assert report["core_dependencies"]["fastapi"]
    assert report["core_dependencies"]["pydantic"]
    assert report["optional_dependencies"]["httpx"]
    assert report["optional_dependencies"]["uvicorn"]
