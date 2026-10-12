"""Deterministic performance and resource regression baselines."""

from __future__ import annotations

import gc
import hashlib
import json
import math
import platform
import statistics
import tempfile
import time
import tracemalloc
from collections.abc import Callable, Mapping, Sequence
from copy import deepcopy
from importlib.resources import files
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from emrf.data.catalog import DataCatalog
from emrf.knowledge import KnowledgeStore
from emrf.runs.artifacts import scan_artifacts

_SCHEMA_VERSION = "1.0.0"
_WORKLOADS = ("covariance", "catalog", "run_artifacts", "knowledge")
_DIMENSIONS = {
    "covariance": {"matrix_size"},
    "catalog": {"datasets"},
    "run_artifacts": {"artifacts", "artifact_bytes"},
    "knowledge": {"nodes"},
}


class PerformanceBaselineRunner:
    """Execute reproducible workloads against versioned regression budgets."""

    def __init__(self, baseline_path: str | Path | None = None) -> None:
        self.baseline_path = (
            Path(baseline_path)
            if baseline_path is not None
            else Path(str(files("emrf").joinpath("performance_baselines.json")))
        )
        self._baseline = _read_baseline(self.baseline_path)

    def run(
        self,
        *,
        profile: str = "standard",
        repeats: int | None = None,
        workloads: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        profiles = self._baseline["profiles"]
        if profile not in profiles:
            raise ValueError(f"Unknown performance profile: {profile}")
        profile_config = profiles[profile]
        selected = tuple(workloads or _WORKLOADS)
        if (
            not selected
            or len(selected) != len(set(selected))
            or any(name not in _WORKLOADS for name in selected)
        ):
            raise ValueError(
                "workloads must contain unique values from: "
                + ", ".join(_WORKLOADS)
            )
        run_repeats = profile_config["default_repeats"] if repeats is None else repeats
        if isinstance(run_repeats, bool) or not isinstance(run_repeats, int):
            raise TypeError("repeats must be an integer")
        if run_repeats < 1 or run_repeats > 10:
            raise ValueError("repeats must be between 1 and 10")

        reports: list[dict[str, Any]] = []
        for name in selected:
            config = profile_config["workloads"][name]
            reports.append(
                self._run_workload(
                    name,
                    config["dimensions"],
                    config["thresholds"],
                    run_repeats,
                )
            )
        passed = all(report["passed"] for report in reports)
        return {
            "schema_version": _SCHEMA_VERSION,
            "baseline_version": self._baseline["baseline_version"],
            "profile": profile,
            "repeats": run_repeats,
            "platform": {
                "python": platform.python_version(),
                "implementation": platform.python_implementation(),
                "system": platform.system(),
                "machine": platform.machine(),
            },
            "baseline_sha256": hashlib.sha256(
                self.baseline_path.read_bytes()
            ).hexdigest(),
            "scientific_outputs_preserved": all(
                report["invariants"]["passed"] for report in reports
            ),
            "passed": passed,
            "workloads": reports,
        }

    def _run_workload(
        self,
        name: str,
        dimensions: Mapping[str, int],
        thresholds: Mapping[str, float | int],
        repeats: int,
    ) -> dict[str, Any]:
        with tempfile.TemporaryDirectory(prefix=f"emrf-performance-{name}-") as raw:
            workspace = Path(raw)
            operation, fixture_bytes, expected = _prepare_workload(
                name,
                dimensions,
                workspace,
            )
            measurements, result = _measure(operation, repeats)
        invariants = _compare_results(result, expected)
        violations: list[str] = []
        if measurements["median_seconds"] > thresholds["max_median_seconds"]:
            violations.append("median_seconds")
        if measurements["peak_python_bytes"] > thresholds["max_peak_python_bytes"]:
            violations.append("peak_python_bytes")
        if fixture_bytes > thresholds["max_fixture_bytes"]:
            violations.append("fixture_bytes")
        if not invariants["passed"]:
            violations.append("scientific_invariants")
        return {
            "name": name,
            "dimensions": dict(dimensions),
            "measurements": {
                **measurements,
                "fixture_bytes": fixture_bytes,
            },
            "thresholds": dict(thresholds),
            "invariants": invariants,
            "passed": not violations,
            "violations": violations,
        }


def _measure(
    operation: Callable[[], dict[str, Any]],
    repeats: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    durations: list[float] = []
    peaks: list[int] = []
    results: list[dict[str, Any]] = []
    for _ in range(repeats):
        gc.collect()
        tracemalloc.start()
        started = time.perf_counter()
        try:
            result = operation()
        finally:
            duration = time.perf_counter() - started
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
        durations.append(duration)
        peaks.append(peak)
        results.append(result)
    canonical = {
        json.dumps(result, sort_keys=True, separators=(",", ":"))
        for result in results
    }
    if len(canonical) != 1:
        raise RuntimeError("Performance workload produced nondeterministic results")
    return (
        {
            "median_seconds": statistics.median(durations),
            "min_seconds": min(durations),
            "max_seconds": max(durations),
            "peak_python_bytes": max(peaks),
        },
        results[-1],
    )


def _prepare_workload(
    name: str,
    dimensions: Mapping[str, int],
    workspace: Path,
) -> tuple[Callable[[], dict[str, Any]], int, dict[str, Any]]:
    if name == "covariance":
        return _prepare_covariance(dimensions)
    if name == "catalog":
        return _prepare_catalog(dimensions, workspace)
    if name == "run_artifacts":
        return _prepare_artifacts(dimensions, workspace)
    if name == "knowledge":
        return _prepare_knowledge(dimensions, workspace)
    raise ValueError(f"Unknown performance workload: {name}")


def _prepare_covariance(
    dimensions: Mapping[str, int],
) -> tuple[Callable[[], dict[str, Any]], int, dict[str, Any]]:
    size = dimensions["matrix_size"]
    matrix = np.eye(size, dtype=np.float64) * 2.0
    adjacent = np.arange(size - 1)
    matrix[adjacent, adjacent + 1] = 0.25
    matrix[adjacent + 1, adjacent] = 0.25
    expected_solution: NDArray[np.float64] = np.ones(size, dtype=np.float64)
    right_hand_side = matrix @ expected_solution

    def solve() -> dict[str, Any]:
        solution = np.linalg.solve(matrix, right_hand_side)
        residual = matrix @ solution - right_hand_side
        return {
            "solution_size": int(solution.size),
            "max_solution_error": float(
                np.max(np.abs(solution - expected_solution))
            ),
            "max_residual": float(np.max(np.abs(residual))),
        }

    expected = {
        "solution_size": size,
        "max_solution_error": {"maximum": 1e-10},
        "max_residual": {"maximum": 1e-10},
    }
    fixture_bytes = matrix.nbytes + right_hand_side.nbytes + expected_solution.nbytes
    return solve, fixture_bytes, expected


def _prepare_catalog(
    dimensions: Mapping[str, int],
    workspace: Path,
) -> tuple[Callable[[], dict[str, Any]], int, dict[str, Any]]:
    count = dimensions["datasets"]
    path = workspace / "data_catalog.json"
    payload = {
        "schema_version": "1.0.0",
        "datasets": [
            {
                "id": f"synthetic-catalog-{index:06d}",
                "title": f"Synthetic catalog fixture {index}",
                "status": "planned",
                "priority": "low",
                "url": f"https://example.invalid/datasets/{index}",
                "citation": "Deterministic performance fixture",
                "redistribution": "fixture-only",
                "holdings": [],
            }
            for index in range(count)
        ],
    }
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )

    def load_catalog() -> dict[str, Any]:
        datasets = DataCatalog(path).list()
        return {
            "datasets": len(datasets),
            "first_id": datasets[0].dataset_id,
            "last_id": datasets[-1].dataset_id,
        }

    expected = {
        "datasets": count,
        "first_id": "synthetic-catalog-000000",
        "last_id": f"synthetic-catalog-{count - 1:06d}",
    }
    return load_catalog, path.stat().st_size, expected


def _prepare_artifacts(
    dimensions: Mapping[str, int],
    workspace: Path,
) -> tuple[Callable[[], dict[str, Any]], int, dict[str, Any]]:
    count = dimensions["artifacts"]
    artifact_bytes = dimensions["artifact_bytes"]
    root = workspace / "run"
    payload = b"x" * artifact_bytes
    for index in range(count):
        path = root / f"group-{index % 20:02d}" / f"artifact-{index:06d}.bin"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)

    def scan() -> dict[str, Any]:
        artifacts = scan_artifacts(root)
        return {
            "artifacts": len(artifacts),
            "total_bytes": sum(record.bytes for record in artifacts),
            "first_path": artifacts[0].path,
            "last_path": artifacts[-1].path,
        }

    ordered = scan_artifacts(root)
    expected = {
        "artifacts": count,
        "total_bytes": count * artifact_bytes,
        "first_path": ordered[0].path,
        "last_path": ordered[-1].path,
    }
    return scan, count * artifact_bytes, expected


def _prepare_knowledge(
    dimensions: Mapping[str, int],
    workspace: Path,
) -> tuple[Callable[[], dict[str, Any]], int, dict[str, Any]]:
    count = dimensions["nodes"]
    seed_path = Path(str(files("emrf.knowledge").joinpath("graph_memory.json")))
    seed = json.loads(seed_path.read_text(encoding="utf-8"))
    template = next(node for node in seed["nodes"] if node.get("kind") == "model")
    nodes = []
    for index in range(count):
        node = deepcopy(template)
        node["id"] = f"model:performance-{index:06d}"
        node["name"] = f"Performance fixture {index}"
        node.pop("evidence_refs", None)
        nodes.append(node)
    graph = {
        "$schema": "GRAPH_MEMORY.schema.json",
        "schema_version": seed["schema_version"],
        "meta": deepcopy(seed["meta"]),
        "nodes": nodes,
        "edges": [],
    }
    path = workspace / "GRAPH_MEMORY.json"
    path.write_text(
        json.dumps(graph, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    store = KnowledgeStore(path)

    def validate() -> dict[str, Any]:
        report = store.validate()
        return {
            "valid": report["valid"],
            "nodes": report["nodes"],
            "edges": report["edges"],
            "errors": len(report["errors"]),
        }

    expected = {
        "valid": True,
        "nodes": count,
        "edges": 0,
        "errors": 0,
    }
    return validate, path.stat().st_size, expected


def _compare_results(
    actual: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for field, requirement in expected.items():
        value = actual.get(field)
        if isinstance(requirement, dict) and "maximum" in requirement:
            passed = (
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and value <= requirement["maximum"]
            )
            expected_value: Any = f"<= {requirement['maximum']}"
        else:
            passed = value == requirement
            expected_value = requirement
        checks.append(
            {
                "field": field,
                "expected": expected_value,
                "actual": value,
                "passed": passed,
            }
        )
    return {"passed": all(check["passed"] for check in checks), "checks": checks}


def _read_baseline(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read performance baseline: {path}") from exc
    if (
        not isinstance(payload, dict)
        or set(payload)
        != {
            "schema_version",
            "baseline_version",
            "reference_observation",
            "profiles",
        }
        or payload.get("schema_version") != _SCHEMA_VERSION
    ):
        raise ValueError("Unsupported performance baseline schema")
    if not isinstance(payload.get("baseline_version"), str):
        raise ValueError("Performance baseline version is invalid")
    profiles = payload.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise ValueError("Performance baseline profiles are invalid")
    reference = payload.get("reference_observation")
    if (
        not isinstance(reference, dict)
        or not isinstance(reference.get("observed_utc"), str)
        or not isinstance(reference.get("platform"), str)
        or isinstance(reference.get("repeats"), bool)
        or not isinstance(reference.get("repeats"), int)
        or not isinstance(reference.get("measurements"), dict)
        or set(reference["measurements"]) != set(_WORKLOADS)
    ):
        raise ValueError("Performance reference observation is invalid")
    for profile in profiles.values():
        _validate_profile(profile)
    return payload


def _validate_profile(profile: object) -> None:
    if not isinstance(profile, dict) or set(profile) != {
        "default_repeats",
        "workloads",
    }:
        raise ValueError("Performance profile is invalid")
    repeats = profile["default_repeats"]
    if isinstance(repeats, bool) or not isinstance(repeats, int) or not 1 <= repeats <= 10:
        raise ValueError("Performance profile repeats are invalid")
    workloads = profile["workloads"]
    if not isinstance(workloads, dict) or set(workloads) != set(_WORKLOADS):
        raise ValueError("Performance profile workloads are invalid")
    for name, config in workloads.items():
        if not isinstance(config, dict) or set(config) != {
            "dimensions",
            "thresholds",
        }:
            raise ValueError("Performance workload configuration is invalid")
        dimensions = config["dimensions"]
        thresholds = config["thresholds"]
        if (
            not isinstance(dimensions, dict)
            or set(dimensions) != _DIMENSIONS[name]
            or any(
                isinstance(value, bool) or not isinstance(value, int) or value < 1
                for value in dimensions.values()
            )
        ):
            raise ValueError("Performance workload dimensions are invalid")
        if (
            not isinstance(thresholds, dict)
            or set(thresholds)
            != {
                "max_median_seconds",
                "max_peak_python_bytes",
                "max_fixture_bytes",
            }
            or any(
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value <= 0
                for value in thresholds.values()
            )
        ):
            raise ValueError("Performance workload thresholds are invalid")


__all__ = ["PerformanceBaselineRunner"]
