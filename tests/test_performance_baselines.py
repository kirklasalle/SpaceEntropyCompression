from __future__ import annotations

import json
from pathlib import Path

import emrf_cli
import pytest
import server
from emrf import performance
from emrf.interfaces.api_v2 import API_V2_TOKEN_ENV, create_app
from emrf.performance import PerformanceBaselineRunner
from emrf.sdk import EMRFClient, InvalidRequestError, OperationResult
from fastapi.testclient import TestClient


def _report(*, passed: bool = True) -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "baseline_version": "2026.10.1",
        "profile": "test",
        "repeats": 1,
        "platform": {
            "python": "3.12.0",
            "implementation": "CPython",
            "system": "test",
            "machine": "test",
        },
        "baseline_sha256": "a" * 64,
        "scientific_outputs_preserved": True,
        "passed": passed,
        "workloads": [],
    }


def test_test_profile_measures_all_workloads_and_preserves_invariants() -> None:
    report = PerformanceBaselineRunner().run(profile="test")

    assert report["passed"] is True
    assert report["scientific_outputs_preserved"] is True
    assert [row["name"] for row in report["workloads"]] == [
        "covariance",
        "catalog",
        "run_artifacts",
        "knowledge",
    ]
    assert all(row["invariants"]["passed"] for row in report["workloads"])
    assert all(row["measurements"]["median_seconds"] >= 0 for row in report["workloads"])
    assert all(row["measurements"]["peak_python_bytes"] > 0 for row in report["workloads"])


def test_baseline_failure_names_threshold_without_changing_result(
    tmp_path: Path,
) -> None:
    source = (
        Path(__file__).parents[1]
        / "emergent_matter_model"
        / "src"
        / "emrf"
        / "performance_baselines.json"
    )
    baseline = json.loads(source.read_text(encoding="utf-8"))
    threshold = baseline["profiles"]["test"]["workloads"]["covariance"]["thresholds"]
    threshold["max_fixture_bytes"] = 1
    path = tmp_path / "baseline.json"
    path.write_text(json.dumps(baseline), encoding="utf-8")

    report = PerformanceBaselineRunner(path).run(
        profile="test",
        repeats=1,
        workloads=("covariance",),
    )

    assert report["passed"] is False
    assert report["scientific_outputs_preserved"] is True
    assert report["workloads"][0]["violations"] == ["fixture_bytes"]


def test_scientific_invariant_failure_cannot_pass_performance_gate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        performance,
        "_prepare_workload",
        lambda name, dimensions, workspace: (
            lambda: {"observable": 2},
            1,
            {"observable": 1},
        ),
    )

    report = PerformanceBaselineRunner().run(
        profile="test",
        repeats=1,
        workloads=("covariance",),
    )

    assert report["passed"] is False
    assert report["scientific_outputs_preserved"] is False
    assert report["workloads"][0]["violations"] == ["scientific_invariants"]


def test_sdk_validates_performance_requests() -> None:
    result = EMRFClient().run_performance_baseline(
        profile="test",
        repeats=1,
        workloads=("covariance",),
    )

    assert result.to_dict()["passed"] is True
    with pytest.raises(InvalidRequestError, match="unique values"):
        EMRFClient().run_performance_baseline(
            profile="test",
            workloads=("covariance", "covariance"),
        )


def test_cli_run_and_check_have_stable_exit_semantics(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    calls: list[dict[str, object]] = []

    def run(**kwargs: object) -> OperationResult:
        calls.append(kwargs)
        return OperationResult(_report(passed=len(calls) == 1))

    monkeypatch.setattr(emrf_cli.sdk, "run_performance_baseline", run)

    assert emrf_cli.main(
        [
            "performance",
            "run",
            "--profile",
            "test",
            "--workload",
            "covariance",
        ]
    ) == 0
    assert json.loads(capsys.readouterr().out)["passed"] is True
    assert emrf_cli.main(["performance", "check", "--profile", "test"]) == 1
    assert json.loads(capsys.readouterr().out)["passed"] is False
    assert calls[0]["workloads"] == ("covariance",)


def test_flask_performance_route_is_gated_and_routes_through_sdk(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(server.RUN_ENV_FLAG, raising=False)
    denied = server.app.test_client().post(
        "/api/v1/performance/baselines",
        json={"profile": "test"},
    )
    assert denied.status_code == 403

    monkeypatch.setenv(server.RUN_ENV_FLAG, "1")
    monkeypatch.setattr(
        server.sdk,
        "run_performance_baseline",
        lambda **kwargs: OperationResult(_report()),
    )
    response = server.app.test_client().post(
        "/api/v1/performance/baselines",
        json={"profile": "test", "repeats": 1, "workloads": ["covariance"]},
    )

    assert response.status_code == 200
    assert response.get_json()["passed"] is True


def test_v2_performance_route_requires_token_and_routes_through_sdk(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(API_V2_TOKEN_ENV, "performance-token")
    monkeypatch.setattr(
        EMRFClient,
        "run_performance_baseline",
        lambda self, **kwargs: OperationResult(_report()),
    )
    client = TestClient(create_app())

    denied = client.post(
        "/api/v2/performance/baselines",
        json={"profile": "test"},
    )
    response = client.post(
        "/api/v2/performance/baselines",
        headers={"Authorization": "Bearer performance-token"},
        json={"profile": "test", "repeats": 1, "workloads": ["covariance"]},
    )

    assert denied.status_code == 401
    assert response.status_code == 200
    assert response.json()["passed"] is True


def test_ci_enforces_standard_performance_profile() -> None:
    workflow = (
        Path(__file__).parents[1] / ".github" / "workflows" / "ci.yml"
    ).read_text(encoding="utf-8")

    assert "Performance baselines / Ubuntu / Python 3.12" in workflow
    assert "performance check" in workflow
    assert "--profile standard --repeats 2" in workflow
