"""Check the selected Candidate B restricted model, its data handling and its claims."""
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, module)
    spec.loader.exec_module(module)
    return module


PREP = _load("prepare_candidate_b_test", "prepare_candidate_b_test.py")
EVAL = _load("evaluate_candidate_b_atlas_contour", "evaluate_candidate_b_atlas_contour.py")
PREREG = json.loads(PREP.PREREGISTRATION.read_text(encoding="utf-8"))
CONSTANTS = PREP.constants_from_preregistration(PREREG)
CONTOUR_RESULT = ROOT / "results" / "candidate_b_atlas_contour_test.json"
READINESS_RESULT = ROOT / "results" / "candidate_b_test_readiness.json"
_ATLAS_ENTRY = next(entry for entry in PREP.load_json(PREP.CATALOG)["datasets"]
                    if entry["id"] == PREP.DATASET_IDS[0])
# The evaluator verifies every ATLAS holding, so a partial download must skip, not fail.
HAVE_ATLAS_DATA = all((ROOT / holding["path"]).is_file() for holding in _ATLAS_ENTRY["holdings"])


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _square(lo, hi):
    return np.array([[lo, lo], [hi, lo], [hi, hi], [lo, hi], [lo, lo]], dtype=float)


def test_preregistration_is_frozen_before_the_comparison():
    assert _sha(PREP.PREREGISTRATION) == EVAL.FROZEN_PREREGISTRATION_SHA256
    assert PREREG["constants"]["M_H_GeV"] == 125.09
    assert CONSTANTS.vev == pytest.approx(246.22, abs=0.01)


@pytest.mark.parametrize("inverse_radius,m5", [(1000.0, 300.0), (100.0, 600.0), (10.0, 150.0)])
def test_closed_form_matching_agrees_with_full_diagonalization(inverse_radius, m5):
    radius = 1 / inverse_radius
    mu4 = PREP.mu4_for_kappa(0.95, radius, m5, 3000.0, CONSTANTS)
    spectrum = PREP.diagonalize(mu4, radius, m5, 3000.0, CONSTANTS)
    u = spectrum["vectors"][0]
    assert spectrum["masses"][0] == pytest.approx(CONSTANTS.higgs_mass, abs=1e-8)
    assert u[0] == pytest.approx(0.95, abs=1e-10)
    assert np.sum(u**2) == pytest.approx(1.0, abs=1e-12)
    assert PREP.matched_kappa(mu4, radius, m5, 3000.0, CONSTANTS) == pytest.approx(0.95)
    assert PREP.mu4_for_kappa(1.0, radius, m5, 3000.0, CONSTANTS) == 0.0


def test_tower_and_matching_reject_invalid_inputs():
    levels, masses_sq, weights = PREP.tower(1 / 1000.0, 300.0, 3000.0)
    assert levels == 2
    assert masses_sq.tolist() == pytest.approx([300.0**2, 300.0**2 + 1e6, 300.0**2 + 4e6])
    assert weights.tolist() == [1.0, 2.0, 2.0]
    with pytest.raises(ValueError):
        PREP.tower(1.0, 3000.0, 3000.0)
    with pytest.raises(ValueError):
        PREP.mu4_for_kappa(1.2, 1 / 1000.0, 300.0, 3000.0, CONSTANTS)
    with pytest.raises(ValueError):
        PREP.matched_sums(1 / 1000.0, 100.0, 3000.0, CONSTANTS.higgs_mass)


def test_cubic_slice_matches_brute_force_rotation():
    radius, m5 = 1 / 1000.0, 300.0
    mu4 = PREP.mu4_for_kappa(0.9, radius, m5, 3000.0, CONSTANTS)
    spectrum = PREP.diagonalize(mu4, radius, m5, 3000.0, CONSTANTS)
    vectors, mu = spectrum["vectors"], spectrum["mu"]
    size = len(vectors)
    gauge = np.zeros((size, size, size))
    gauge[0, 0, 0] = 3 * spectrum["mh0_sq"] / CONSTANTS.vev
    for n, coupling in enumerate(mu, start=1):
        gauge[0, 0, n] = gauge[0, n, 0] = gauge[n, 0, 0] = coupling
    rotated = np.einsum("ijk,ia,jb,kc->abc", gauge, vectors, vectors, vectors)
    for state in range(size):
        assert np.allclose(PREP.cubic_tensor_slice(state, vectors, mu, spectrum["mh0_sq"],
                                                   CONSTANTS.vev), rotated[state], atol=1e-9)


def test_two_scalar_width_counts_identical_and_distinct_pairs():
    masses = np.array([1.0, 1.5, 4.0])
    coupling = np.array([[2.0, 3.0, 0.0], [3.0, 0.5, 0.0], [0.0, 0.0, 0.0]])
    big = 4.0
    identical_0 = 4.0 * math.sqrt(1 - 4 / 16) / (32 * math.pi * big)
    identical_1 = 0.25 * math.sqrt(1 - 4 * 2.25 / 16) / (32 * math.pi * big)
    kallen = (1 - 2.5**2 / 16) * (1 - 0.5**2 / 16)
    distinct = 9.0 * math.sqrt(kallen) / (16 * math.pi * big)
    expected = identical_0 + identical_1 + distinct
    assert PREP.two_scalar_width(2, masses, coupling) == pytest.approx(expected)
    assert PREP.two_scalar_width(1, masses, coupling) == 0.0


def test_sm_like_tree_widths_reproduce_heavy_higgs_scaling_and_thresholds():
    heavy = PREP.sm_like_tree_widths(1000.0, CONSTANTS)
    asymptotic = 3 * CONSTANTS.g_fermi * 1000.0**3 / (16 * math.sqrt(2) * math.pi)
    assert heavy["WW"] + heavy["ZZ"] == pytest.approx(asymptotic, rel=0.05)
    assert heavy["WW"] / heavy["ZZ"] == pytest.approx(2.0, rel=0.05)
    assert heavy["ttbar"] > 0
    light = PREP.sm_like_tree_widths(150.0, CONSTANTS)
    assert light == {"WW": 0.0, "ZZ": 0.0, "ttbar": 0.0}


def test_polygon_helpers_on_synthetic_nested_loops():
    inner, outer = _square(0.98, 1.02), _square(0.95, 1.05)
    loops, leftover = PREP.split_closed_loops(np.vstack([inner, outer, [[1.0, 1.0]]]))
    assert len(loops) == 2 and leftover.tolist() == [[1.0, 1.0]]
    assert PREP.polygon_area(outer) == pytest.approx(0.01)
    assert PREP.point_in_polygon(np.array([1.0, 1.0]), outer)
    assert not PREP.point_in_polygon(np.array([0.9, 1.0]), outer)
    bowtie = np.array([[0, 0], [1, 1], [1, 0], [0, 1], [0, 0]], dtype=float)
    assert PREP.self_intersections(bowtie) == 1
    assert PREP.self_intersections(outer) == 0
    result = PREP.identify_contours(np.vstack([inner, outer, [[1.0, 1.0]]]))
    assert result["identified"] and result["outer_loop_index"] == 1
    assert result["area_ratio_outer_to_inner"] == pytest.approx(6.25)
    assert result["unlooped_points_inside_both"] == [True]
    disjoint = PREP.identify_contours(np.vstack([_square(0.0, 0.1), _square(0.5, 0.7)]))
    assert not disjoint["identified"] and disjoint["reason"] == "loops are not nested"


def test_diagonal_intersection_rules():
    inside = EVAL.diagonal_intersection(_square(0.95, 1.05))
    assert inside["inside_intervals"] == [[pytest.approx(0.95), 1.0]]
    assert inside["sm_point_inside"]
    off_diagonal = np.array([[0.9, 1.1], [1.0, 1.1], [1.0, 1.2], [0.9, 1.2], [0.9, 1.1]])
    missed = EVAL.diagonal_intersection(off_diagonal)
    assert missed["inside_intervals"] == [] and not missed["sm_point_inside"]


def test_readiness_artifact_is_current_and_makes_no_comparison():
    report = json.loads(READINESS_RESULT.read_text(encoding="utf-8"))
    assert report["source_sha256"] == _sha(ROOT / "tools" / "prepare_candidate_b_test.py")
    assert report["preregistration_sha256"] == EVAL.FROZEN_PREREGISTRATION_SHA256
    assert report["protocol_sha256"] == _sha(PREP.PROTOCOL)
    assert report["comparison_performed"] is False
    assert report["research_selection"]["active_candidate"] == "candidate-b"
    checks = report["model_self_checks"]
    assert checks["max_lightest_mass_error_GeV"] < 1e-8
    assert checks["max_kappa_error"] < 1e-10


def test_contour_artifact_is_current_and_claims_only_conditional_compatibility():
    report = json.loads(CONTOUR_RESULT.read_text(encoding="utf-8"))
    assert report["source_sha256"] == _sha(ROOT / "tools" / "evaluate_candidate_b_atlas_contour.py")
    assert report["model_source_sha256"] == _sha(ROOT / "tools" / "prepare_candidate_b_test.py")
    assert report["preregistration_sha256"] == EVAL.FROZEN_PREREGISTRATION_SHA256
    assert report["likelihood_evaluated"] is False
    assert report["one_parameter_interval_claimed"] is False
    assert report["candidate_b_confirmed"] is False
    assert report["outcome"] == "compatible_with_limit"
    assert 0.9 < report["kappa_lo"] < 1.0
    assert report["diagonal"]["sm_point_inside"] is True
    grid = PREREG["parameter_grid"]
    assert len(report["grid"]) == len(grid["inverse_radius_GeV"]) * len(grid["m5_GeV"])
    for row in report["grid"]:
        assert row["valid"]
        assert row["mu4_max_GeV"] == pytest.approx(PREP.mu4_for_kappa(
            report["kappa_lo"], 1 / row["inverse_radius_GeV"], row["m5_GeV"],
            row["cutoff_GeV"], CONSTANTS))


@pytest.mark.skipif(not HAVE_ATLAS_DATA, reason="ATLAS Figure 4 raw table not downloaded")
def test_contour_artifact_reproduces_from_pinned_data():
    stored = json.loads(CONTOUR_RESULT.read_text(encoding="utf-8"))
    fresh = EVAL.build_report()
    assert fresh["outcome"] == stored["outcome"]
    assert fresh["kappa_lo"] == pytest.approx(stored["kappa_lo"])
    assert fresh["contour_identification"]["area_ratio_outer_to_inner"] == pytest.approx(
        stored["contour_identification"]["area_ratio_outer_to_inner"])
