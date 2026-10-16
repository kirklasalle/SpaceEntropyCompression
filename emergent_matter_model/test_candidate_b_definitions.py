"""Check Candidate B benchmark algebra and the limits of its claims."""
import hashlib
import importlib.util
import json
import math
import re
from pathlib import Path, PureWindowsPath
from urllib.parse import unquote

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools" / "check_candidate_b_definitions.py"
SPEC = importlib.util.spec_from_file_location("candidate_b_checks", PATH)
CHECKS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKS)

R, M5, CUTOFF = 1 / 1000.0, 400.0, 5000.0


@pytest.fixture(scope="module")
def report():
    return CHECKS.build_report()


def test_local_cell_units_and_reduction_need_a_declared_measure():
    units = CHECKS.local_cell_units()
    density = units["energy_density_u_C_V_C_u_th_u_drive_J"]
    assert units["kinetic_I_C_xidot2"] == density
    assert units["damping_force_Gamma_C_xidot"] == density
    assert units["Q_C_Gamma_C_xidot2"] == (1, -1, -3, 0)
    assert units["entropy_production_Q_C_over_T"] == (1, -1, -3, -1)
    for d in (4, 5, 7):
        reduced = CHECKS.reduced_density_units(d)
        assert reduced["bulk_density"] != reduced["observed_3d_density"]
        assert reduced["after_integrating_extra_lengths"] == reduced["observed_3d_density"]


def test_local_cell_ledgers_close_and_entropy_sign_is_conditional():
    dissipative = CHECKS.integrate_local_cell(2.0, 0.3, 5.0, 0.8, 1.3, 300.0,
                                              t_end=10.0, steps=5000)
    assert dissipative["relative_ledger_drift"] < 1e-10
    assert dissipative["min_entropy_production_rate"] >= 0
    assert dissipative["final_u_th_J_m3"] > 0
    negative = CHECKS.integrate_local_cell(2.0, -0.05, 5.0, 0.8, 1.3, 300.0,
                                           t_end=10.0, steps=5000)
    assert negative["relative_ledger_drift"] < 1e-10
    assert negative["min_entropy_production_rate"] < 0


@pytest.mark.parametrize("dimension", [3, 4, 5, 6, 9, 11])
def test_portal_mass_dimensions_hold_for_every_dimension(dimension):
    dims = CHECKS.portal_mass_dimensions(dimension)
    assert dims["kinetic_term"] == dims["bulk_lagrangian"]
    assert dims["mu"] == CHECKS.Fraction(5 - dimension, 2)
    assert dims["g_xi"] == 2
    assert dims["mu_4_after_volume_reduction"] == 1
    assert dims["phi_zero_mode_4d"] == 1


def test_circle_modes_and_projection_do_not_confuse_bulk_points():
    modes = CHECKS.circle_mode_checks(radius=0.7, max_level=6, samples=64)
    assert modes["max_gram_deviation_from_identity"] < 1e-12
    assert modes["sine_modes_at_brane_max_abs"] < 1e-15
    assert modes["cosine_to_zero_mode_brane_ratio"] == pytest.approx([math.sqrt(2)] * 6)
    projection = CHECKS.projection_checks()
    assert projection["same_projected_point"] is True
    assert projection["same_bulk_point"] is False
    assert projection["sine_profile_off_brane_value"] != 0
    assert projection["sine_profile_brane_overlap_energy"] == 0
    assert projection["overlap_signs_for_h_minus_and_plus"] == [-1.0, 1.0]


def test_schur_stability_envelope_is_exact_for_truncated_matrix():
    levels = CHECKS.validate_benchmark_domain(R, M5, CUTOFF)
    assert levels == 4
    bound = CHECKS.stability_bound_mu4(R, M5, levels)
    assert np.linalg.eigvalsh(CHECKS.mass_matrix(R, M5, levels, 0.999 * bound))[0] > 0
    assert np.linalg.eigvalsh(CHECKS.mass_matrix(R, M5, levels, 1.001 * bound))[0] < 0


def test_zero_mode_rotation_and_global_boundedness_match_tree_level():
    mu_4 = 20.0
    matrix = CHECKS.mass_matrix(R, M5, 0, mu_4)
    _, vectors = np.linalg.eigh(matrix)
    theta = 0.5 * math.atan(2 * mu_4 * CHECKS.PROBE_V_GEV
                            / (CHECKS.PROBE_MH_GEV**2 - M5**2))
    assert np.max(np.abs(vectors[0])) == pytest.approx(math.cos(theta), rel=1e-12)
    for coupling in (10.0, 150.0, 300.0, 500.0):
        tree = (coupling * CHECKS.PROBE_V_GEV)**2 < (CHECKS.PROBE_MH_GEV * M5)**2
        assert CHECKS.zero_mode_bounded_below(M5, coupling) is tree


def test_infinite_tower_limit_and_massless_zero_mode():
    radius, m5 = 1 / 50.0, 100.0
    closed = CHECKS.stability_sum_infinite(radius, m5)
    errors = [abs(CHECKS.stability_sum(radius, m5, n) - closed) / closed
              for n in (100, 1000, 20000)]
    assert errors[0] > errors[1] > errors[2]
    assert errors[2] < 1e-4
    mu4 = CHECKS.stability_bound_mu4(radius, m5, None)
    mu5 = CHECKS.PROBE_MH_GEV / CHECKS.PROBE_V_GEV * math.sqrt(
        2 * m5 * math.tanh(math.pi * m5 * radius))
    assert math.sqrt(2 * math.pi * radius) * mu4 == pytest.approx(mu5, rel=1e-13)
    bounds = [CHECKS.stability_bound_mu4(radius, m, None) for m in (1.0, 1e-3, 1e-6)]
    assert bounds[0] > bounds[1] > bounds[2] and bounds[2] < 1e-5


def test_low_energy_operator_matches_tower_elimination():
    coefficient = CHECKS.low_energy_operator_coefficient(R, M5, 4, 37.0)
    assert coefficient["matrix_elimination"] == pytest.approx(
        coefficient["closed_form_finite"], rel=1e-13)
    radius, m5 = 1 / 50.0, 100.0
    mu5 = 3.0
    mu4 = mu5 / math.sqrt(2 * math.pi * radius)
    formal = 0.5 * mu4**2 * CHECKS.stability_sum_infinite(radius, m5)
    expected = mu5**2 / (4 * m5) / math.tanh(math.pi * m5 * radius)
    assert formal == pytest.approx(expected, rel=1e-13)


def test_perturbative_mixing_is_bounded_to_weak_domain():
    mu_4 = 5.0
    exact = CHECKS.exact_mixing(R, M5, 4, mu_4)
    assert exact["kappa_squared_sum_rule"] == pytest.approx(1.0, abs=1e-12)
    assert CHECKS.weak_mixing_ratio(R, M5, 4, mu_4) < 0.1
    assert CHECKS.perturbative_kappa_v(R, M5, 4, mu_4) == pytest.approx(
        exact["higgs_like_kappa_v"], abs=1e-6)
    with pytest.raises(ValueError, match="weak-mixing"):
        CHECKS.perturbative_kappa_v(R, 126.0, 4, 1.0)
    forced = CHECKS.perturbative_kappa_v(R, 126.0, 4, 1.0, max_ratio=math.inf)
    degenerate = CHECKS.exact_mixing(R, 126.0, 4, 1.0)
    assert abs(forced - degenerate["higgs_like_kappa_v"]) > 0.1
    assert degenerate["largest_two_kappa_squared"][0] > 0.2


def test_kappa_min_envelope_inverts_perturbative_formula():
    for kappa_min in (0.9, 0.99, 0.999):
        mu_4 = CHECKS.kappa_min_envelope(R, M5, 4, kappa_min)
        kappa = CHECKS.perturbative_kappa_v(R, M5, 4, mu_4, max_ratio=math.inf)
        assert kappa == pytest.approx(kappa_min, rel=1e-13)


def test_cms_window_is_unmixed_preselection_only():
    assert CHECKS.cms_window_levels(R, M5, 4) == [0, 1, 2]
    assert CHECKS.cms_window_levels(R, 100.0, 0) == []


def test_portal_exchange_is_paired_conserved_and_reversible():
    mu_4 = 0.3 * CHECKS.stability_bound_mu4(R, M5, 0)
    result = CHECKS.integrate_portal_exchange(M5, mu_4, 5.0, periods=8.0,
                                              steps_per_period=300)
    scale = result["initial_total_energy_GeV4"]
    assert result["relative_total_drift"] < 1e-7
    assert result["max_brane_ledger_error_GeV4"] / scale < 1e-7
    assert result["max_scalar_ledger_error_GeV4"] / scale < 1e-7
    assert result["max_energy_delivered_to_brane_GeV4"] > 1e-3 * scale
    assert result["exchange_direction_reversals"] > 10
    assert result["time_reversal_return_error_GeV"] < 1e-5
    assert result["bounded_below_for_zero_mode_truncation"] is True


@pytest.mark.parametrize(("args", "message"), [
    ((0.0, M5, CUTOFF), "R must be"),
    ((-R, M5, CUTOFF), "R must be"),
    ((float("nan"), M5, CUTOFF), "R must be"),
    ((R, 0.0, CUTOFF), "m5 must be"),
    ((R, M5, float("inf")), "cutoff"),
    ((R, M5, 100.0), "Lambda >= max"),
    ((R, 50.0, 120.0), "Lambda >= max"),
])
def test_benchmark_domain_is_explicit(args, message):
    with pytest.raises(ValueError, match=message):
        CHECKS.validate_benchmark_domain(*args)


def test_other_invalid_inputs_are_explicit():
    with pytest.raises(ValueError, match="temperature"):
        CHECKS.local_entropy_production_rate(0.1, 1.0, 0.0)
    with pytest.raises(ValueError, match="kappa_min"):
        CHECKS.kappa_min_envelope(R, M5, 4, 1.0)
    with pytest.raises(ValueError, match="at least 3"):
        CHECKS.portal_mass_dimensions(2)
    with pytest.raises(ValueError, match="degeneracy"):
        CHECKS.mixing_sum(R, CHECKS.PROBE_MH_GEV, 2)


def test_report_preserves_evidence_boundary(report):
    assert report["evidence_kind"] == "benchmark_algebra_and_toy_integration_not_observations"
    assert report["candidate_b_selected"] is True
    for flag in ("physical_model_implemented",
                 "candidate_a_selection_changed", "parameters_selected_or_measured",
                 "likelihood_evaluated", "observational_data_used"):
        assert report[flag] is False
    assert report["near_degeneracy"]["perturbative_formula_refused"] is True
    assert report["paired_exchange"]["unstable_coupling_bounded_below"] is False


def test_ledger_graph_documents_and_artifact_agree(report):
    ledger = json.loads((ROOT / "knowledgebase" / "thermodynamic_collision_candidates.json")
                        .read_text(encoding="utf-8"))
    parallel = ledger["parallel_exploration"]
    assert parallel["candidate_b_selected"] is True
    assert parallel["candidate_a_selection_changed"] is False
    checks = parallel["executed_checks"]
    assert checks["evidence_kind"] == report["evidence_kind"]
    assert checks["candidate_b_selected"] is True
    for flag in ("parameters_selected_or_measured", "likelihood_evaluated",
                 "observational_data_used"):
        assert checks[flag] is False
    degeneracy = report["near_degeneracy"]
    quoted = f"{degeneracy['perturbative_kappa_if_forced']:.3f} forced versus " \
             f"{degeneracy['exact']['higgs_like_kappa_v']:.3f} exact"
    assert any(quoted in failure for failure in checks["failures_under_stated_assumptions"])
    assert set(parallel["decision_ready_outcome"]) == {
        "succeeds", "fails_under_stated_assumptions", "remains_open", "recommended_next_review"}

    graph = json.loads((ROOT / "knowledgebase" / "GRAPH_MEMORY.json").read_text(encoding="utf-8"))
    nodes = {node["id"]: node for node in graph["nodes"]}
    portal = nodes["definition:candidate_b_brane_higgs_portal"]
    assert portal["status"] == "author_selected_restricted_test_hypothesis"
    diagnostic = nodes["diagnostic:candidate_b_benchmark_checks"]
    assert diagnostic["filePath"] == parallel["diagnostic_artifact"]
    assert diagnostic["use_for_empirical_confirmation"] is False
    review = graph["meta"]["collision_candidate_review"]["candidate_b_parallel_exploration"]
    assert review["candidate_b_selected"] is True

    for document in (parallel["document"], parallel["dimensionality_document"]):
        path = ROOT / document
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if "://" not in target and not target.startswith("#"):
                assert (path.parent / unquote(target.split("#")[0])).exists(), target
    contract = (ROOT / parallel["document"]).read_text(encoding="utf-8")
    assert "## 14. Executed benchmark checks" in contract
    assert "## 15. Decision-ready outcome" in contract
    assert "Both A and B are selected" in contract

    artifact = json.loads((ROOT / parallel["diagnostic_artifact"]).read_text(encoding="utf-8"))
    for path_string, expected in artifact["source_sha256"].items():
        source = ROOT.joinpath(*PureWindowsPath(path_string).parts)
        assert hashlib.sha256(source.read_bytes()).hexdigest() == expected
    assert artifact["conclusions"] == report["conclusions"]
    assert artifact["kk_benchmark"]["stability_bound_mu4_GeV"] == pytest.approx(
        report["kk_benchmark"]["stability_bound_mu4_GeV"], rel=1e-12)
    assert artifact["infinite_tower_limit"]["relative_difference"] == pytest.approx(
        report["infinite_tower_limit"]["relative_difference"], rel=1e-6)
