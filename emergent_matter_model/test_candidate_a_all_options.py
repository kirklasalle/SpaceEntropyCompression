"""Full-density physics checks and explicit gates, never synthetic observations."""

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pytest

from tools import evaluate_candidate_a_all_options as tool

ROOT = Path(__file__).resolve().parents[1]


def test_protocol_is_frozen_and_authorized_for_all_options():
    protocol = tool.verify_protocol()
    assert protocol["author_direction"]["clarification"] == "full_density"
    assert protocol["option_2"]["protocol_sha256"] == tool.a2.FROZEN_PREREGISTRATION_SHA256
    assert "NOT a new blind observational" in protocol["registration_scope"]
    assert "never" in protocol["option_3"]["density_order"].lower()


def test_density_catalog_is_mirrored_and_matches_frozen_inputs():
    source = ROOT / "knowledgebase" / "library" / "data_catalog.json"
    packaged = ROOT / "emergent_matter_model" / "src" / "emrf" / "data" / "data_catalog.json"
    assert source.read_bytes() == packaged.read_bytes()
    catalog = json.loads(source.read_text())
    entry = next(row for row in catalog["datasets"] if row["id"] == "leroy-2008-density-profiles")
    expected = tool.verify_protocol()["new_data"]["holdings"]
    assert [(Path(h["path"]).name, h["bytes"], h["sha256"]) for h in entry["holdings"]] == [
        (h["name"], h["bytes"], h["sha256"]) for h in expected]


def test_modified_protocol_stops_before_fetch(tmp_path, monkeypatch):
    modified = tmp_path / "protocol.json"
    modified.write_bytes(tool.PROTOCOL.read_bytes() + b" ")
    monkeypatch.setattr(tool, "PROTOCOL", modified)
    monkeypatch.setattr(tool, "verify_density_data",
                        lambda *_: pytest.fail("fetched after refusal"))
    report = tool.run()
    assert report["outcome"] == "incomplete"
    assert "frozen SHA-256" in report["incomplete_reason"]
    assert "option_1" not in report


def test_density_inversion_and_units():
    rho = np.array([0, 0.001, 0.1, 1, 50])
    for alpha in (0.25, 0.5, 1, 2, 4):
        eff = tool.effective_density(rho, alpha, 0.2)
        assert np.allclose(0.2 * (eff / 0.2)**alpha, rho, rtol=1e-12, atol=0)
        assert np.allclose(tool.effective_density(rho * 1e9, alpha, 0.2 * 1e9),
                           eff * 1e9, rtol=1e-12, atol=0)
        assert eff[0] == 0
    assert np.array_equal(tool.effective_density(rho, 1, 1e-30), rho)
    assert np.array_equal(tool.effective_density(rho, 1, 1e30), rho)


@pytest.mark.parametrize("alpha,rho0", [(0, 1), (-1, 1), (math.nan, 1),
                                      (math.inf, 1), (1, 0), (1, math.nan)])
def test_density_invalid_parameters_fail_explicitly(alpha, rho0):
    with pytest.raises(ValueError, match="finite and positive"):
        tool.effective_density(np.array([1.0]), alpha, rho0)


@pytest.mark.parametrize("rho", [[-1], [math.nan], [math.inf]])
def test_density_invalid_inputs_fail_explicitly(rho):
    with pytest.raises(ValueError, match="finite and nonnegative"):
        tool.effective_density(np.array(rho), 2, 1)


def test_source_components_must_be_summed_before_nonlinear_map():
    a, b = np.array([0.2, 2.0]), np.array([0.3, 3.0])
    for alpha in (0.5, 2, 4):
        assert not np.allclose(tool.effective_density(a + b, alpha, 1),
                               tool.effective_density(a, alpha, 1)
                               + tool.effective_density(b, alpha, 1))
        values = np.array([0.1, 10.0])
        excess = tool.effective_density(values, alpha, 1) - values
        assert excess[0] * excess[1] < 0


def test_option1_observer_and_equation_of_state_sweep():
    report = tool.check_option1()
    assert report["fluid_observer_normalization_cases"] == 81
    assert report["max_relative_identity_error"] < 1e-12
    assert report["independent_observational_confirmation"] is False


def test_full_density_solver_meets_exact_frozen_thresholds():
    report = tool.check_option3()
    errors = report["poisson_benchmark"]["relative_errors"]
    assert all(value < 0.005 for value in errors.values())
    assert all(row["coarse_vs_fine_relative_error"] < 0.005
               for row in report["nonlinear_disc_benchmarks"])
    assert report["observational_fit_performed"] is False


def test_solver_newtonian_linearity_and_units():
    radii = np.array([0.5, 1, 4])
    baseline = tool.axisymmetric_v2(tool.miyamoto_nagai_density, radii, order=64)
    heavier = tool.axisymmetric_v2(lambda r, z: 3 * tool.miyamoto_nagai_density(r, z),
                                  radii, order=64, gravitational_constant=2)
    assert np.allclose(heavier, 6 * baseline, rtol=1e-12)
    scale = 7
    rescaled = tool.axisymmetric_v2(
        lambda r, z: tool.miyamoto_nagai_density(r / scale, z / scale) / scale**3,
        radii * scale, order=64, r_scale=scale, z_scale=scale * 0.2)
    assert np.allclose(rescaled, baseline / scale, rtol=1e-10)


@pytest.mark.parametrize("radii,order", [([], 64), ([0], 64), ([math.nan], 64),
                                       ([1], 0), ([1], 64.0)])
def test_solver_invalid_domain(radii, order):
    with pytest.raises(ValueError):
        tool.axisymmetric_v2(tool.miyamoto_nagai_density, np.array(radii), order=order)


def test_solver_invalid_density_is_not_clipped():
    with pytest.raises(ValueError, match="Density callback"):
        tool.axisymmetric_v2(lambda r, z: -np.ones_like(r + z), np.array([1]), order=32)


def test_modified_density_cache_is_never_overwritten(tmp_path, monkeypatch):
    monkeypatch.setattr(tool, "DENSITY_DIR", tmp_path)
    (tmp_path / "ReadMe").write_text("modified", encoding="ascii")
    monkeypatch.setattr(tool, "download", lambda *_: pytest.fail("overwrote modified data"))
    with pytest.raises(ValueError, match="modified Leroy"):
        tool.verify_density_data(tool.verify_protocol(), fetch=True)


def test_missing_density_cache_without_fetch_is_explicit(tmp_path, monkeypatch):
    monkeypatch.setattr(tool, "DENSITY_DIR", tmp_path)
    with pytest.raises(ValueError, match="fetch-density-data"):
        tool.verify_density_data(tool.verify_protocol())


def test_fixed_width_missing_values_are_not_zeros():
    assert tool.optional_number("   ", 0, 3) is None
    assert tool.optional_number("0.0", 0, 3) == 0
    with pytest.raises(ValueError, match="Non-finite"):
        tool.optional_number("nan", 0, 3)


def test_comparison_covers_shapes_integers_and_nonfinite_values():
    assert tool.compare_results({"p": [1, 2.0, None]}, {"p": [1, 2.0 + 1e-9, None]}) == 3
    for a, b in (([1], [1, 2]), ({"x": 1}, {"y": 1}), (10**10, 10**10 + 1),
                 (1, True), (math.nan, math.nan), (math.inf, math.inf), (1.0, 1.1)):
        with pytest.raises(ValueError, match="Reproduction"):
            tool.compare_results(a, b)


def test_option2_refuses_incomplete_reproduction():
    with pytest.raises(ValueError, match="input mismatch"):
        tool.reproduce_option2(lambda: {"outcome": "incomplete",
                                       "incomplete_reason": "input mismatch"})


def test_partial_gate_exit_is_nonzero_and_persistent(tmp_path, monkeypatch):
    output = tmp_path / "report.json"
    monkeypatch.setattr(tool, "run", lambda *_: {
        "outcome": "partial_option3_observational_test_blocked"})
    assert tool.main(["--output", str(output)]) == 2
    assert json.loads(output.read_text())["outcome"].startswith("partial")
    monkeypatch.setattr(tool, "run", lambda *_: {
        "outcome": "incomplete", "incomplete_reason": "input mismatch"})
    assert tool.main(["--output", str(output)]) == 1


@pytest.mark.skipif(not (tool.DENSITY_DIR / "table7.dat").exists(),
                    reason="Pinned external density profiles are not downloaded")
def test_real_density_coverage_does_not_claim_full_volume_data():
    tool.verify_density_data(tool.verify_protocol())
    galaxies = tool.a2.load_sparc(tool.a2.fetch_sparc())
    report = tool.audit_density_profiles({g.name for g in galaxies})
    assert report["overlap_galaxies"] == 11
    assert report["galaxies_with_complete_tabulated_components"] == 0
    assert report["missing_measurements_replaced_with_zero"] is False
    assert report["vertical_volume_profiles_supplied"] is False
    assert report["outcome"].startswith("blocked")


@pytest.mark.skipif(not tool.OUTPUT.exists(), reason="All-option artifact not generated")
def test_artifact_provenance_and_honest_outcomes():
    report = json.loads(tool.OUTPUT.read_text(encoding="utf-8"))
    assert report["protocol_sha256"] == tool.PROTOCOL_SHA256
    for source, digest in report["source_sha256"].items():
        assert hashlib.sha256((ROOT / source).read_bytes()).hexdigest() == digest
    assert report["option_2"]["original_artifact_sha256"] == tool.sha256(tool.a2.OUTPUT)
    assert report["option_1"]["outcome"] == "consistency_checks_passed"
    assert report["option_2"]["outcome"] == "rejected"
    assert report["option_2"]["reproduction"] == "passed"
    assert report["option_3"]["observational_fit_performed"] is False
    assert report["candidate_a_confirmed"] is False
    assert report["outcome"] == "partial_option3_observational_test_blocked"
