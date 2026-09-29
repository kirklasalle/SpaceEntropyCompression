import pytest

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
