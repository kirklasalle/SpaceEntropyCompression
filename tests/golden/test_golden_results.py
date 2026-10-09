from __future__ import annotations

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
    assert errors == ["stable: expected 1.0, got 1.00000001 (rtol=1e-10)"]


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
    assert all(case.rtol == golden.DEFAULT_RTOL for case in golden.CASES)
    assert dict(
        next(
            case for case in golden.CASES if case.command == "sparc-real-analysis"
        ).rtol_overrides
    ) == {
        "isothermal_halo.bic": 1e-7,
        "isothermal_halo.chi2": 1e-7,
    }


@pytest.mark.golden
@pytest.mark.skipif(
    os.environ.get("EMRF_RUN_GOLDEN") != "1",
    reason="set EMRF_RUN_GOLDEN=1 to execute expensive real-data regressions",
)
def test_real_data_pipelines_match_golden_results() -> None:
    golden.run([case.command for case in golden.CASES])
