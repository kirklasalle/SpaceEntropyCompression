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
        "/api/v2/doctor",
        "/api/v2/commands",
        "/api/v2/commands/{name}",
        "/api/v2/commands/{name}/runs",
        "/api/v2/runs",
        "/api/v2/runs/{run_id}",
        "/api/v2/jobs",
        "/api/v2/jobs/{job_id}",
        "/api/v2/jobs/{job_id}/cancel",
        "/api/v2/jobs/worker/run-next",
        "/api/v2/runs/{run_id}/artifacts",
        "/api/v2/runs/{run_id}/artifacts/{relative_path}",
        "/api/v2/datasets",
        "/api/v2/datasets/{dataset_id}",
        "/api/v2/datasets/{dataset_id}/import",
        "/api/v2/datasets/{dataset_id}/fetch",
        "/api/v2/datasets/verify",
        "/api/v2/data/backups",
        "/api/v2/data/backups/offsite",
        "/api/v2/data/backups/verify",
        "/api/v2/data/restores",
        "/api/v2/data/restore-drills",
        "/api/v2/data/gc",
        "/api/v2/predictions/commit",
        "/api/v2/predictions/{commitment_id}",
        "/api/v2/predictions/{commitment_id}/verify",
        "/api/v2/simulations",
        "/api/v2/knowledge",
        "/api/v2/knowledge/validate",
        "/api/v2/knowledge/export",
        "/api/v2/knowledge/sources",
        "/api/v2/knowledge/runs/{run_id}/link",
        "/api/v2/knowledge/{node_id}",
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
    assert set(
        schema["paths"]["/api/v2/datasets/{dataset_id}/fetch"]["post"]["responses"]
    ) == {"201", "400", "401", "403", "404", "422", "503"}
    assert set(
        schema["paths"]["/api/v2/predictions/{commitment_id}"]["get"]["responses"]
    ) == {"200", "400", "404", "422"}
    assert set(
        schema["paths"]["/api/v2/simulations"]["post"]["responses"]
    ) == {"200", "400", "401", "403", "422"}
    fetch_error = schema["paths"]["/api/v2/datasets/{dataset_id}/fetch"]["post"][
        "responses"
    ]["503"]["content"]["application/json"]["schema"]
    assert fetch_error["$ref"].endswith("/ErrorResponse")


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


def test_v2_doctor_matches_public_sdk_report(client: TestClient):
    direct = EMRFClient().environment_report().to_dict()
    response = client.get("/api/v2/doctor")

    assert response.status_code == 200
    assert response.json() == direct
    assert "executable" not in response.json()


def test_v2_simulation_matches_sdk_and_requires_auth(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    payload = {
        "n": 2,
        "weights": [0.5, 0.5],
        "X_grid": [[0.0, 1.0], [0.0, 0.5]],
        "k": 1.0,
        "alpha": 1.0,
        "C0": 1.0,
    }
    assert client.post("/api/v2/simulations", json=payload).status_code == 403

    token = "test-token"
    monkeypatch.setenv(API_V2_TOKEN_ENV, token)
    response = client.post(
        "/api/v2/simulations",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )

    assert response.status_code == 200
    assert response.json()["shape"] == [2, 2]
    assert response.json()["M"] == [[0.5, 1.125], [1.0, 1.625]]


class _FakeDataLibrary:
    def catalog_status(self, *, verify: bool = False):
        return [{"id": "demo", "title": "Demo", "status": "ok", "verified": verify}]

    def info(self, dataset_id: str, *, verify: bool = False):
        return {"catalog": {"id": dataset_id}, "managed": {"verified": verify}}

    def import_dataset(self, dataset_id: str, **kwargs):
        return [{"dataset_id": dataset_id, **kwargs}]

    def fetch_dataset(self, dataset_id: str, **kwargs):
        return [{"dataset_id": dataset_id, **kwargs}]

    def verify(self):
        return {"healthy": True, "failed_datasets": [], "managed_holdings": 1}

    def create_backup(self, destination: str):
        return {"destination": destination, "objects": 1, "holdings": 1}

    def create_offsite_backup(self, destination_root: str | None):
        return {"destination": destination_root, "offsite": True}

    def verify_backup(self, source: str):
        return {"source": source, "objects": 1, "holdings": 1}

    def restore_backup(self, source: str):
        return {"objects": 1, "holdings": 1, "source": source}

    def run_restore_drill(self, **kwargs):
        return {"healthy": True, **kwargs}

    def garbage_collect(self, *, execute: bool):
        return {"executed": execute, "objects": [], "count": 0, "bytes": 0}


def test_v2_data_operations_match_sdk_and_enforce_auth(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    library = _FakeDataLibrary()
    monkeypatch.setattr("emrf_data_access.data_library", lambda: library)

    direct = EMRFClient().list_datasets(verify=True).to_dict()
    assert client.get("/api/v2/datasets?verify=true").json() == direct
    assert client.get("/api/v2/datasets/demo?verify=true").json() == {
        "catalog": {"id": "demo"},
        "managed": {"verified": True},
    }
    assert client.post("/api/v2/datasets/verify").json()["healthy"] is True
    assert client.post(
        "/api/v2/datasets/demo/import",
        json={},
    ).status_code == 403

    token = "test-token"
    monkeypatch.setenv(API_V2_TOKEN_ENV, token)
    headers = {"Authorization": f"Bearer {token}"}
    assert client.post(
        "/api/v2/datasets/demo/import",
        headers=headers,
        json={"logical_name": "sample"},
    ).json()["holdings"][0]["logical_name"] == "sample"
    assert client.post(
        "/api/v2/datasets/demo/fetch",
        headers=headers,
        json={"retries": 2, "timeout": 30},
    ).status_code == 201
    assert client.post(
        "/api/v2/data/backups",
        headers=headers,
        json={"destination": "backup"},
    ).json()["objects"] == 1
    assert client.post(
        "/api/v2/data/backups/offsite",
        headers=headers,
        json={"destination_root": "offsite"},
    ).json()["offsite"] is True
    assert client.post(
        "/api/v2/data/backups/verify",
        headers=headers,
        json={"source": "backup"},
    ).json()["source"] == "backup"
    assert client.post(
        "/api/v2/data/restores",
        headers=headers,
        json={"source": "backup"},
    ).json()["holdings"] == 1
    assert client.post(
        "/api/v2/data/restore-drills",
        headers=headers,
        json={"receipt": "receipt.json"},
    ).json()["healthy"] is True
    assert client.post(
        "/api/v2/data/gc",
        headers=headers,
        json={"execute": False},
    ).json()["count"] == 0


def test_v2_prediction_operations_match_sdk_and_conflict_status(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    record = {
        "commitment_id": "20261011T000000000000Z-123456789abc",
        "label": "test",
        "created_utc": "2026-10-11T00:00:00+00:00",
        "sha256": "1" * 64,
        "bytes": 2,
        "source_name": None,
        "media_type": "application/json",
        "evidence_class": "preregistered-prediction",
        "content_stored": False,
    }
    verification = {
        "commitment_id": record["commitment_id"],
        "matches": False,
        "expected_sha256": "1" * 64,
        "actual_sha256": "2" * 64,
        "bytes": 2,
    }
    monkeypatch.setattr(
        "emrf_prediction_access.commit_json_prediction",
        lambda prediction, label: record,
    )
    monkeypatch.setattr(
        "emrf_prediction_access.get_commitment",
        lambda commitment_id: record,
    )
    monkeypatch.setattr(
        "emrf_prediction_access.verify_json_prediction",
        lambda commitment_id, prediction: verification,
    )

    assert client.post(
        "/api/v2/predictions/commit",
        json={"label": "test", "prediction": {"x": 1}},
    ).status_code == 403
    token = "test-token"
    monkeypatch.setenv(API_V2_TOKEN_ENV, token)
    headers = {"Authorization": f"Bearer {token}"}
    committed = client.post(
        "/api/v2/predictions/commit",
        headers=headers,
        json={"label": "test", "prediction": {"x": 1}},
    )
    assert committed.status_code == 201
    assert committed.json() == record
    assert client.get(
        f"/api/v2/predictions/{record['commitment_id']}"
    ).json() == record
    revealed = client.post(
        f"/api/v2/predictions/{record['commitment_id']}/verify",
        json={"prediction": {"x": 2}},
    )
    assert revealed.status_code == 409
    assert revealed.json() == verification


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


def test_v2_job_lifecycle_and_authenticated_artifacts(
    client: TestClient,
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
):
    store = RunStore(tmp_path)
    monkeypatch.setattr("emrf_run_access.run_store", lambda: store)
    monkeypatch.setenv(API_V2_TOKEN_ENV, "secret-token")
    headers = {"Authorization": "Bearer secret-token"}

    submitted = client.post(
        "/api/v2/jobs",
        headers=headers,
        json={"command": "compare-schwarzschild", "args": ["--help"]},
    )
    assert submitted.status_code == 202
    job_id = submitted.json()["job_id"]
    assert client.get(f"/api/v2/jobs/{job_id}").json()["status"] == "queued"
    assert client.get("/api/v2/jobs").json()["jobs"][0]["job_id"] == job_id
    assert client.post(f"/api/v2/jobs/{job_id}/cancel", headers=headers).json()[
        "status"
    ] == "cancelled"

    executed = client.post(
        "/api/v2/commands/compare-schwarzschild/runs",
        headers=headers,
        json={"args": ["--help"]},
    )
    run_id = executed.json()["run_id"]
    listed = client.get(
        f"/api/v2/runs/{run_id}/artifacts", headers=headers
    )
    assert listed.status_code == 200
    artifact = next(
        item for item in listed.json()["artifacts"] if item["path"].startswith("stdout-")
    )
    downloaded = client.get(
        f"/api/v2/runs/{run_id}/artifacts/{artifact['path']}",
        headers=headers,
    )
    assert downloaded.status_code == 200
    assert "Schwarzschild" in downloaded.text
    assert client.get(
        f"/api/v2/runs/{run_id}/artifacts/../run.json", headers=headers
    ).status_code in {400, 404}
    assert client.get(f"/api/v2/runs/{run_id}/artifacts").status_code == 401


def test_v2_worker_executes_queued_job(
    client: TestClient,
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
):
    store = RunStore(tmp_path)
    monkeypatch.setattr("emrf_run_access.run_store", lambda: store)
    monkeypatch.setenv(API_V2_TOKEN_ENV, "secret-token")
    headers = {"Authorization": "Bearer secret-token"}

    submitted = client.post(
        "/api/v2/jobs",
        headers=headers,
        json={"command": "compare-schwarzschild", "args": ["--help"]},
    )
    completed = client.post(
        "/api/v2/jobs/worker/run-next",
        headers=headers,
        json={"worker_id": "api-test-worker", "lease_seconds": 120},
    )

    assert submitted.status_code == 202
    assert completed.status_code == 200
    assert completed.json()["job_id"] == submitted.json()["job_id"]
    assert completed.json()["status"] == "succeeded"
    assert completed.json()["run_id"]
    assert client.post(
        "/api/v2/jobs/worker/run-next",
        headers=headers,
        json={"worker_id": "api-test-worker"},
    ).json() is None


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
