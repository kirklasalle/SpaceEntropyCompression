"""Safe, read-only Schemathesis checks for the v1 and v2 API contracts."""

from __future__ import annotations

from pathlib import Path

import schemathesis
import yaml
from fastapi.testclient import TestClient

import server
from emrf_api_v2_access import app

v2_document = TestClient(app).get("/api/v2/openapi.json").json()
v2_document["openapi"] = "3.0.3"
v2_schema = schemathesis.openapi.from_dict(v2_document).include(
    path_regex=r"/api/v2/health"
)
v1_document = yaml.safe_load(
    (Path(__file__).parent / "openapi.yaml").read_text(encoding="utf-8")
)
v1_schema = schemathesis.openapi.from_dict(v1_document).include(
    path_regex=r"/api/v1/health"
)


@v2_schema.parametrize()
def test_generated_v2_health_contract(case) -> None:
    response = case.call_asgi(app=app)
    case.validate_response(response)


@v1_schema.parametrize()
def test_documented_v1_health_contract(case) -> None:
    response = case.call_wsgi(app=server.app)
    case.validate_response(response)
