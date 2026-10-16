"""Check Candidate B's extended tests: the Higgs-rate likelihood and the CMS ZZ comparison."""
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, module)
    spec.loader.exec_module(module)
    return module


PREP = _load("prepare_candidate_b_test")
CONTOUR = _load("evaluate_candidate_b_atlas_contour")
RATE = _load("evaluate_candidate_b_higgs_rate_likelihood")
CMS = _load("evaluate_candidate_b_cms_resonance")
EXTRACT = _load("extract_candidate_b_theory_inputs")
PARENT = json.loads(PREP.PREREGISTRATION.read_text(encoding="utf-8"))
EXTENDED = json.loads(RATE.PREREGISTRATION.read_text(encoding="utf-8"))
CONSTANTS = PREP.constants_from_preregistration(PARENT)
THEORY = CMS.load_theory(CONSTANTS)
_ATLAS_ENTRY = next(entry for entry in PREP.load_json(PREP.CATALOG)["datasets"]
                    if entry["id"] == PREP.DATASET_IDS[0])
# The evaluator verifies every ATLAS holding, so a partial download must skip, not fail.
HAVE_ATLAS_DATA = all((ROOT / holding["path"]).is_file() for holding in _ATLAS_ENTRY["holdings"])
HAVE_CMS_DATA = CMS.CMS_ZIP.is_file()
HAVE_HXSWG_DATA = EXTRACT.BSM_PAGE.is_file() and EXTRACT.BR_PAGE.is_file()


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parabola(mu_hat, sigma, start=0.8, stop=1.3, step=0.001):
    mu = np.round(np.arange(start, stop + step / 2, step), 6)
    return mu, ((mu - mu_hat) / sigma) ** 2


def _table(masses, observed, expected=None):
    masses = np.array(masses, dtype=float)
    observed = np.array(observed, dtype=float)
    return {"mass": masses, "observed": observed,
            "expected": observed if expected is None else np.array(expected, dtype=float)}


# --- frozen inputs ------------------------------------------------------------

def test_extended_preregistration_and_theory_inputs_are_frozen():
    assert _sha(RATE.PREREGISTRATION) == RATE.FROZEN_PREREGISTRATION_SHA256
    assert CMS.FROZEN_PREREGISTRATION_SHA256 == RATE.FROZEN_PREREGISTRATION_SHA256
    assert _sha(PREP.PREREGISTRATION) == CONTOUR.FROZEN_PREREGISTRATION_SHA256
    assert EXTENDED["parent_preregistration"]["sha256"] == CONTOUR.FROZEN_PREREGISTRATION_SHA256
    assert EXTENDED["theory_inputs"]["sha256"] == CMS.THEORY_INPUTS_SHA256
    assert _sha(CMS.THEORY_INPUTS) == CMS.THEORY_INPUTS_SHA256


def test_frozen_files_keep_exact_bytes_in_git():
    attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
    assert "knowledgebase/candidate_b_*.json -text" in attributes


def test_theory_table_rows_and_spot_values():
    table = json.loads(CMS.THEORY_INPUTS.read_text(encoding="utf-8"))
    assert (len(table["ggF"]), len(table["VBF"]), len(table["sm_width"])) == (114, 114, 321)
    assert table["dataset"] == EXTRACT.DATASET_ID
    assert [h["topic_revision"] for h in table["holdings"]] == ["r30", "r16"]
    by_mass = {row[0]: row for row in table["sm_width"]}
    assert by_mass[200.0][3] == pytest.approx(1.43)
    assert by_mass[1000.0][2] == pytest.approx(0.311)
    assert CMS.sm_like_cross_section(440.0, THEORY, "ggF") == pytest.approx(7.301)
    assert CMS.sm_like_cross_section(300.0, THEORY, "VBF") == pytest.approx(1.256)
    assert math.isnan(CMS.sm_like_cross_section(3001.0, THEORY, "ggF"))
    assert CMS.sm_like_cross_section(440.0, THEORY, "ggF", low=True) < 7.30


@pytest.mark.skipif(not HAVE_HXSWG_DATA, reason="HXSWG pages not downloaded")
def test_theory_table_reproduces_from_pinned_pages():
    stored = json.loads(CMS.THEORY_INPUTS.read_text(encoding="utf-8"))
    assert EXTRACT.build_table() == stored


def test_theory_table_serialization_reproduces_frozen_bytes_on_every_platform():
    frozen = CMS.THEORY_INPUTS.read_bytes()
    assert EXTRACT.serialize(json.loads(frozen.decode("utf-8"))) == frozen


# --- test A: Higgs-rate likelihood ----------------------------------------------

def test_crossing_below_interpolates_linearly():
    mu = np.array([0.8, 0.9, 1.0])
    nll = np.array([4.0, 2.0, 0.0])
    assert RATE.crossing_below(mu, nll, 1.0, 3.0) == pytest.approx(0.85)
    assert RATE.crossing_below(mu, nll, 0.95, 1.5) == pytest.approx(0.925)
    assert RATE.crossing_below(mu, nll, 1.0, 5.0) is None


def test_analyse_scan_on_synthetic_parabola_above_one():
    mu, nll = _parabola(1.05, 0.05)
    scan = RATE.analyse_scan(mu, nll)
    assert scan["mu_hat"] == pytest.approx(1.05)
    assert scan["mu_ref"] == 1.0
    assert scan["q_family"] == pytest.approx(1.0)
    assert scan["mu_lo_primary"] == pytest.approx(1.05 - 0.05 * math.sqrt(3.706), abs=1e-5)
    assert scan["mu_lo_unbounded_one_sided"] == pytest.approx(1.05 - 0.05 * math.sqrt(2.706),
                                                              abs=1e-5)
    assert scan["mu_lo_two_sided"] == pytest.approx(1.05 - 0.05 * math.sqrt(3.841), abs=1e-5)
    assert RATE.classify(scan) == "compatible_with_limit"


def test_analyse_scan_below_one_uses_the_best_fit_as_reference():
    mu, nll = _parabola(0.95, 0.05)
    scan = RATE.analyse_scan(mu, nll)
    assert scan["mu_ref"] == pytest.approx(0.95) and scan["q_family"] == 0.0
    assert scan["mu_lo_primary"] == pytest.approx(0.95 - 0.05 * math.sqrt(2.706), abs=1e-5)


def test_classification_rules():
    far = RATE.analyse_scan(*_parabola(1.2, 0.05))
    assert far["q_family"] > 2.706 and RATE.classify(far) == "incompatible"
    short = RATE.analyse_scan(*_parabola(1.05, 0.05, start=0.97))
    assert RATE.classify(short) == "not_determinable"
    sparse = RATE.analyse_scan(np.array([0.99, 1.05, 1.1]), np.array([3.0, 0.0, 1.0]))
    assert RATE.classify(sparse) == "ambiguous_data"


def test_likelihood_artifact_is_current_and_claims_only_a_bound():
    report = json.loads(RATE.OUTPUT.read_text(encoding="utf-8"))
    assert report["source_sha256"] == _sha(ROOT / "tools" /
                                           "evaluate_candidate_b_higgs_rate_likelihood.py")
    assert report["model_source_sha256"] == _sha(ROOT / "tools" / "prepare_candidate_b_test.py")
    assert report["preregistration_sha256"] == RATE.FROZEN_PREREGISTRATION_SHA256
    assert report["parent_preregistration_sha256"] == CONTOUR.FROZEN_PREREGISTRATION_SHA256
    assert report["candidate_b_confirmed"] is False
    assert report["outcome"] == "compatible_with_limit"
    assert report["kappa_lo"] == pytest.approx(math.sqrt(report["mu_lo"]))
    assert report["primary_scan"]["q_family"] <= 2.706
    assert report["sensitivity_scans"]["statistical_only"]["outcome"] == "incompatible"
    assert "never the result" in report["sensitivity_note"]
    for row in report["grid"]:
        assert row["mu4_max_GeV"] == pytest.approx(PREP.mu4_for_kappa(
            report["kappa_lo"], 1 / row["inverse_radius_GeV"], row["m5_GeV"],
            row["cutoff_GeV"], CONSTANTS))
        assert row["stronger_rate_bound"] in {"contour", "likelihood"}


@pytest.mark.skipif(not HAVE_ATLAS_DATA, reason="ATLAS HEPData record not downloaded")
def test_likelihood_artifact_reproduces_from_pinned_data():
    stored = json.loads(RATE.OUTPUT.read_text(encoding="utf-8"))
    fresh = RATE.build_report()
    assert fresh["outcome"] == stored["outcome"]
    assert fresh["mu_lo"] == pytest.approx(stored["mu_lo"])
    assert fresh["primary_scan"]["q_family"] == pytest.approx(stored["primary_scan"]["q_family"])


# --- test B: CMS direct resonance -----------------------------------------------

def test_bracket_returns_neighbours_exact_matches_and_coverage():
    grid = np.array([130.0, 200.0, 300.0])
    assert CMS.bracket(grid, 250.0) == [1, 2]
    assert CMS.bracket(grid, 200.0) == [1]
    assert CMS.bracket(grid, 130.0) == [0]
    assert CMS.bracket(grid, 129.9) is None and CMS.bracket(grid, 300.1) is None
    assert CMS.bracket(CMS.WIDTH_VALUES, 0.4) == [0, 1]
    assert CMS.bracket(CMS.WIDTH_VALUES, 10.0) == [2]
    assert CMS.bracket(CMS.WIDTH_VALUES, 100.5) is None


def test_limit_envelope_and_log_linear_variant():
    tables = {(key, production): _table([200, 300], [scale * 2.0, scale * 8.0])
              for (key, _), scale in zip(CMS.WIDTH_TABLES, (1.0, 1.5, 3.0, 5.0), strict=True)
              for production, _ in CMS.PRODUCTIONS}
    assert CMS.table_limit(tables[("NWA", "ggF")], 250.0) == 8.0
    assert CMS.table_limit(tables[("NWA", "ggF")], 250.0, mass_rule="log_linear") == \
        pytest.approx(4.0)
    assert CMS.cms_limit(tables, "ggF", 250.0, 0.5) == 1.5 * 8.0
    assert CMS.cms_limit(tables, "ggF", 250.0, 1.0) == 1.5 * 8.0
    assert CMS.cms_limit(tables, "VBF", 250.0, 50.0, mass_rule="log_linear") == \
        pytest.approx(5.0 * 4.0)
    assert CMS.cms_limit(tables, "ggF", 250.0, 150.0) is None
    assert CMS.cms_limit(tables, "ggF", 350.0, 1.0) is None


def test_sm_like_widths_are_continuous_at_the_tabulated_edge():
    total, zz = CMS.sm_like_widths(1000.0, THEORY, CONSTANTS)
    assert total == pytest.approx(647.0) and zz == pytest.approx(647.0 * 0.311)
    above_total, above_zz = CMS.sm_like_widths(1000.0 + 1e-6, THEORY, CONSTANTS)
    assert above_total == pytest.approx(total, rel=1e-6)
    assert above_zz == pytest.approx(zz, rel=1e-6)
    assert CMS.sm_like_widths(2000.0, THEORY, CONSTANTS)[0] > total


@pytest.mark.parametrize("inverse_radius,m5", [(1000.0, 600.0), (100.0, 300.0)])
def test_heavy_states_follow_the_preregistered_scaling(inverse_radius, m5):
    radius = 1 / inverse_radius
    mu4 = PREP.mu4_for_kappa(0.95, radius, m5, 3000.0, CONSTANTS)
    states = CMS.heavy_states(mu4, radius, m5, 3000.0, CONSTANTS, THEORY)
    spectrum = PREP.diagonalize(mu4, radius, m5, 3000.0, CONSTANTS)
    reference = PREP.heavy_state_widths(spectrum, CONSTANTS)
    assert np.allclose(states["scalar_width"], [r["two_scalar_width_GeV"] for r in reference])
    for i, mass in enumerate(states["mass"]):
        u2 = states["higgs_fraction"][i]
        total, zz = CMS.sm_like_widths(mass, THEORY, CONSTANTS)
        assert states["width"][i] == pytest.approx(u2 * total + states["scalar_width"][i])
        assert states["br_zz"][i] == pytest.approx(u2 * zz / states["width"][i])
        assert states["sigma"]["ggF"][i] == pytest.approx(
            u2 * CMS.sm_like_cross_section(mass, THEORY, "ggF"))
        assert states["extrapolated"][i] == (mass > 1000.0)


def test_compact_writer_round_trips(tmp_path):
    payload = {"scan": {"R": [0.5, None, 1.25e-05, -3], "names": ["a", "b"]},
               "rows": [{"x": [1, 2]}, {"flag": [True, False]}]}
    path = tmp_path / "report.json"
    CMS.write_report(path, payload)
    text = path.read_text(encoding="utf-8")
    assert json.loads(text) == payload
    assert '"R": [0.5, null, 1.25e-05, -3]' in text


def test_cms_artifact_is_current_and_claims_only_bounds():
    report = json.loads(CMS.OUTPUT.read_text(encoding="utf-8"))
    assert report["source_sha256"] == _sha(ROOT / "tools" / "evaluate_candidate_b_cms_resonance.py")
    assert report["model_source_sha256"] == _sha(ROOT / "tools" / "prepare_candidate_b_test.py")
    assert report["preregistration_sha256"] == CMS.FROZEN_PREREGISTRATION_SHA256
    assert report["theory_inputs_sha256"] == CMS.THEORY_INPUTS_SHA256
    assert report["likelihood_evaluated"] is False
    assert report["candidate_b_confirmed"] is False
    assert len(report["data"]["tables"]) == 8
    rules = set(EXTENDED["test_b_cms_direct_resonance"]["outcome_rules_per_grid_point"])
    grid = PARENT["parameter_grid"]
    assert len(report["grid"]) == len(grid["inverse_radius_GeV"]) * len(grid["m5_GeV"])
    for row in report["grid"]:
        assert row["outcome"] in rules
        assert len(row["scan"]["mu4_GeV"]) == CMS.SCAN_STEPS
        assert all(len(values) == CMS.SCAN_STEPS for values in row["scan"]["R"].values())
        rate_bounds = [v for v in row["rate_mu4_max_GeV"].values() if v is not None]
        assert row["combined_mu4_bound_GeV"] <= min(rate_bounds)
        excluded = row["variants"]["primary"]["excluded_scan_steps"]
        if excluded:
            low, high = row["mu4_excl_bisection_bracket_GeV"]
            assert high == row["mu4_excl_min_GeV"] and 0 <= low < high
            assert high <= excluded[0] * row["mu4_scan_top_GeV"] / CMS.SCAN_STEPS
        else:
            assert "mu4_excl_min_GeV" not in row
        if row["outcome"] == "exclusion_within_rate_allowed_region":
            assert row["combined_binding_constraint"] == "cms_direct"


@pytest.mark.skipif(not HAVE_CMS_DATA, reason="CMS HEPData record not downloaded")
def test_cms_tables_load_with_expected_shapes():
    tables = CMS.load_limit_tables()
    counts = {"NWA": 129, "W1": 98, "W10": 60, "W100": 33}
    for (key, _), table in tables.items():
        assert len(table["mass"]) == counts[key]
        assert table["mass"][0] == 130.0 and table["mass"][-1] == 3000.0


@pytest.mark.skipif(not HAVE_CMS_DATA, reason="CMS HEPData record not downloaded")
def test_cms_grid_point_reproduces_from_pinned_data():
    stored = json.loads(CMS.OUTPUT.read_text(encoding="utf-8"))
    row = next(r for r in stored["grid"]
               if r["inverse_radius_GeV"] == 1000.0 and r["m5_GeV"] == 600.0)
    fresh = CMS.grid_point(1000.0, 600.0, row["cutoff_GeV"], CONSTANTS, THEORY,
                           CMS.load_limit_tables(), row["rate_mu4_max_GeV"])
    assert fresh["outcome"] == row["outcome"]
    assert fresh["variants"]["primary"]["excluded_scan_steps"] == \
        row["variants"]["primary"]["excluded_scan_steps"]
    if "mu4_excl_min_GeV" in row:
        assert fresh["mu4_excl_min_GeV"] == pytest.approx(row["mu4_excl_min_GeV"])
