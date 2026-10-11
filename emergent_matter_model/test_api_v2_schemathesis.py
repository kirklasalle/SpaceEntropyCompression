"""Safe, read-only Schemathesis checks for the v1 and v2 API contracts."""

from __future__ import annotations

from pathlib import Path

import schemathesis
import yaml
from fastapi.testclient import TestClient

import server
from emrf_api_v2_access import app

v2_schema = schemathesis.openapi.from_asgi("/api/v2/openapi.json", app)
v2_document = v2_schema.raw_schema
v2_document["openapi"] = "3.0.3"
v2_schema = schemathesis.openapi.from_dict(v2_document).include(path_regex=r"/api/v2/health")
v2_schema.app = app
v1_document = yaml.safe_load((Path(__file__).parent / "openapi.yaml").read_text(encoding="utf-8"))
v1_schema = schemathesis.openapi.from_dict(v1_document).include(path_regex=r"/api/v1/health")
v1_schema.app = server.app


@v2_schema.parametrize()
def test_generated_v2_health_contract(case) -> None:
    response = case.call()
    case.validate_response(response)


@v1_schema.parametrize()
def test_documented_v1_health_contract(case) -> None:
    response = case.call()
    case.validate_response(response)


def test_v2_method_not_allowed_preserves_allow_header() -> None:
    response = TestClient(app).request("TRACE", "/api/v2/health")

    assert response.status_code == 405
    assert "GET" in response.headers["allow"]


def test_v1_method_not_allowed_preserves_allow_header() -> None:
    response = server.app.test_client().trace("/api/v1/health")

    assert response.status_code == 405
    assert {"GET", "HEAD"}.issubset(response.headers["Allow"].replace(" ", "").split(","))
