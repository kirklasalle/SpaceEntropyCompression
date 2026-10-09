from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from tools import run_golden_results as golden

ROOT = Path(__file__).resolve().parents[2]


def test_comparator_uses_exact_integer_and_tolerant_float_comparisons() -> None:
    assert not golden.compare_values(
        {"count": 3, "value": 1.0}, {"count": 3, "value": 1 + 1e-11}
    )
    assert golden.compare_values({"count": 3}, {"count": 4})
    assert golden.compare_values({"value": 0.0}, {"value": 1e-15})


def test_comparator_honors_precise_ignored_paths() -> None:
    expected = {"generated_utc": "old", "nested": {"generated_utc": "preserved"}}
    actual = {"generated_utc": "new", "nested": {"generated_utc": "changed"}}
    errors = golden.compare_values(expected, actual, ignored_paths={"generated_utc"})
    assert errors == ["nested.generated_utc: expected 'preserved', got 'changed'"]


def test_comparator_honors_path_specific_tolerances() -> None:
    expected = {"stable": 1.0, "optimizer": 1.0}
    actual = {"stable": 1.0 + 1e-8, "optimizer": 1.0 + 1e-8}
    errors = golden.compare_values(
        expected,
        actual,
        rtol_overrides={"optimizer": 1e-7},
    )
    assert errors == [
        "stable: expected 1.0, got 1.00000001 (rtol=1e-10, atol=0)"
    ]


def test_comparator_honors_path_specific_absolute_tolerance() -> None:
    errors = golden.compare_values(
        {"roundoff": 1e-12, "signal": 1e-12},
        {"roundoff": 2e-12, "signal": 2e-12},
        atol_overrides={"roundoff": 2e-12},
    )
    assert errors == [
        "signal: expected 1e-12, got 2e-12 (rtol=1e-10, atol=0)"
    ]


def test_gauntlet_sources_are_downloaded_and_verified(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source"
    workspace = tmp_path / "workspace"
    raw = b"pinned observation data"
    record = {
        "url": "https://example.invalid/data",
        "kind": "published_measurement_table",
        "file": r"data\external\real_data_v1\sample.dat",
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }
    manifest = source / "results" / "real_data_v1" / "gauntlet.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(json.dumps({"source_records": [record]}), encoding="utf-8")

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def read(self) -> bytes:
            return raw

    monkeypatch.setattr(golden, "ROOT", source)
    monkeypatch.setattr(golden, "urlopen", lambda *_args, **_kwargs: Response())

    golden._hydrate_gauntlet_sources(workspace)

    downloaded = workspace / "data" / "external" / "real_data_v1" / "sample.dat"
    assert downloaded.read_bytes() == raw


def test_gauntlet_reference_pages_are_not_treated_as_observation_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source"
    workspace = tmp_path / "workspace"
    record = {
        "url": "https://example.invalid/reference",
        "kind": golden.REFERENCE_SOURCE_KIND,
        "file": r"data\external\real_data_v1\reference.html",
        "bytes": 1,
        "sha256": "not-downloaded",
    }
    manifest = source / "results" / "real_data_v1" / "gauntlet.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(json.dumps({"source_records": [record]}), encoding="utf-8")
    monkeypatch.setattr(golden, "ROOT", source)

    golden._hydrate_gauntlet_sources(workspace)

    assert not workspace.exists()


def test_isolated_workspace_has_git_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    for relative in ("emergent_matter_model", "tools", "data", "results"):
        (source / relative).mkdir(parents=True)
    monkeypatch.setattr(golden, "ROOT", source)

    golden._copy_workspace(destination)

    revision = subprocess.run(
        ("git", "rev-parse", "HEAD"),
        cwd=destination,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert len(revision) == 40


@given(st.integers(), st.integers())
def test_comparator_never_applies_float_tolerance_to_integers(
    left: int, right: int
) -> None:
    assert bool(golden.compare_values(left, right)) is (left != right)


def test_every_fixed_real_data_analysis_has_a_golden_case() -> None:
    expected = {
        "sparc-real-analysis",
        "sparc-marginalized-a0",
        "sparc-tension-diagnostics",
        "sparc-bulge-test",
        "fit-pantheon-covariance",
        "sparc-profile-validation",
        "sparc-influence",
        "real-data-gauntlet",
    }
    assert {case.command for case in golden.CASES} == expected
    for case in golden.CASES:
        assert (ROOT / case.script).is_file()
        assert (ROOT / case.output).is_file()
    by_name = {case.command: case for case in golden.CASES}
    optimizer_cases = {
        "sparc-marginalized-a0",
        "sparc-tension-diagnostics",
        "sparc-profile-validation",
        "sparc-influence",
    }
    assert all(by_name[name].rtol == golden.OPTIMIZER_RTOL for name in optimizer_cases)
    assert by_name["sparc-bulge-test"].rtol == golden.BULGE_OPTIMIZER_RTOL
    assert by_name["fit-pantheon-covariance"].rtol == 1e-7
    assert by_name["real-data-gauntlet"].rtol == 1e-7
    assert dict(by_name["fit-pantheon-covariance"].atol_overrides) == {
        "integration_check_absolute_delta_chi2": 1e-11
    }
    assert all(
        case.rtol == golden.DEFAULT_RTOL
        for name, case in by_name.items()
        if name
        not in optimizer_cases
        | {"sparc-bulge-test", "fit-pantheon-covariance", "real-data-gauntlet"}
    )
    assert dict(by_name["sparc-real-analysis"].rtol_overrides) == {
        "isothermal_halo.bic": 1e-7,
        "isothermal_halo.chi2": 1e-7,
    }
    assert {
        "inputs.sparc/Rotmod_LTG.zip.retrieved_utc",
        "inputs.sparc/SPARC_Lelli2016c.mrt.retrieved_utc",
    } <= set(by_name["sparc-profile-validation"].ignored_paths)


@pytest.mark.golden
@pytest.mark.skipif(
    os.environ.get("EMRF_RUN_GOLDEN") != "1",
    reason="set EMRF_RUN_GOLDEN=1 to execute expensive real-data regressions",
)
def test_real_data_pipelines_match_golden_results() -> None:
    golden.run([case.command for case in golden.CASES])
