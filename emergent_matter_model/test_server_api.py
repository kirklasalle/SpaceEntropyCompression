import pytest

from emrf_version import __version__
from server import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def valid_payload():
    return {
        "n": 4,
        "weights": [0.3, 0.3, 0.2, 0.2],
        "X_grid": [
            [-1, 0, 1],
            [-1, 0, 1],
            [-1, 0, 1],
            [0, 0.5, 1.0],
        ],
        "k": 1.0,
        "alpha": 1.0,
        "C0": 1.0,
    }


def test_simulate_success(client):
    response = client.post("/api/v1/simulate", json=valid_payload())
    assert response.status_code == 200
    body = response.get_json()
    assert "M" in body
    assert len(body["M"]) == 3


def test_legacy_route_parity(client):
    payload = valid_payload()
    response_v1 = client.post("/api/v1/simulate", json=payload)
    response_legacy = client.post("/simulate", json=payload)

    assert response_v1.status_code == 200
    assert response_legacy.status_code == 200
    assert response_v1.get_json() == response_legacy.get_json()


def test_missing_required_field(client):
    payload = valid_payload()
    payload.pop("n")
    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 400
    assert "Missing required field" in response.get_json()["error"]


def test_non_json_body(client):
    response = client.post("/api/v1/simulate", data="not json", content_type="text/plain")
    assert response.status_code == 400
    assert "valid JSON" in response.get_json()["error"]


def test_n_must_be_integer(client):
    payload = valid_payload()
    payload["n"] = 4.5
    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 400
    assert "n must be an integer" in response.get_json()["error"]


def test_n_must_be_positive(client):
    payload = valid_payload()
    payload["n"] = 0
    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 400
    assert "n must be >= 1" in response.get_json()["error"]


def test_weights_length_must_match_n(client):
    payload = valid_payload()
    payload["weights"] = [1.0, 1.0]
    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 400
    assert "weights must be a list of length" in response.get_json()["error"]


def test_weights_must_be_finite_numeric(client):
    payload = valid_payload()
    payload["weights"] = [0.3, 0.3, float("inf"), 0.2]
    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 400
    assert "weights must contain only finite numeric values" in response.get_json()["error"]


def test_weights_sum_not_zero(client):
    payload = valid_payload()
    payload["weights"] = [0.0, 0.0, 0.0, 0.0]
    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 400
    assert "weights must not sum to zero" in response.get_json()["error"]


def test_x_grid_length_must_match_n(client):
    payload = valid_payload()
    payload["X_grid"] = [[0], [1], [2]]
    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 400
    assert "X_grid must be a list of" in response.get_json()["error"]


def test_x_grid_axis_not_empty(client):
    payload = valid_payload()
    payload["X_grid"][2] = []
    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 400
    assert "must not be empty" in response.get_json()["error"]


def test_x_grid_axis_must_be_numeric(client):
    payload = valid_payload()
    payload["X_grid"][1] = [0, "bad", 1]
    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 400
    assert "must contain only finite numeric values" in response.get_json()["error"]


def test_optional_params_must_be_finite(client):
    payload = valid_payload()
    payload["alpha"] = "bad"
    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 400
    assert "alpha must be a finite numeric value" in response.get_json()["error"]


def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "emergent-matter-model"
    assert data["version"] == __version__


def test_rate_limiting_triggered(client):
    import time
    from server import _RATE_LIMIT_MAX_REQUESTS, _request_records
    test_ip = "192.168.1.99"
    now = time.time()
    # Pre-populate IP request timestamps with current time to exceed limit
    _request_records[test_ip] = [now] * (_RATE_LIMIT_MAX_REQUESTS + 1)

    # Send request with this IP
    response = client.post(
        "/api/v1/simulate",
        json=valid_payload(),
        environ_base={"REMOTE_ADDR": test_ip}
    )
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.get_json()["error"]
    # Clean up test IP
    del _request_records[test_ip]


def test_visualizer_endpoint(client):
    response = client.get("/visualizer")
    assert response.status_code == 200
    assert "text/html" in response.content_type
    assert "EMRF Interactive Multidimensional Perspective" in response.get_data(as_text=True)


def test_v1_security_headers_auth_path_confinement_and_child_env(client, monkeypatch, tmp_path):
    health_resp = client.get("/api/v1/health")
    assert health_resp.headers["X-Content-Type-Options"] == "nosniff"
    assert health_resp.headers["X-Frame-Options"] == "DENY"
    assert health_resp.headers["Deprecation"] == "true"

    monkeypatch.setenv("EMRF_DATA_WRITE_ALLOW", "1")
    monkeypatch.setenv("EMRF_API_ALLOW_DATA_WRITE", "1")
    bad_backup = client.post(
        "/api/v1/recovery/backups",
        json={"destination": "../../outside-v1-escape"},
    )
    assert bad_backup.status_code == 400

    monkeypatch.setenv("EMRF_API_V1_TOKEN", "v1-secret-token")
    unauth = client.post("/api/v1/recovery/backups", json={"destination": str(tmp_path)})
    assert unauth.status_code == 401

    monkeypatch.setenv("EMRF_API_V2_TOKEN", "v2-secret-token")
    import emrf_registry as reg

    child_env = reg._child_process_env()
    assert "EMRF_API_V1_TOKEN" not in child_env
    assert "EMRF_API_V2_TOKEN" not in child_env

    bad_sim = client.post(
        "/api/v1/simulate",
        json={"n": 9, "weights": [1.0] * 9, "X_grid": [[0.0]] * 9},
    )
    assert bad_sim.status_code == 400
