"""Check Candidate A's option-2 SPARC test: frozen inputs, model algebra and artifact."""
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


TOOL = _load("evaluate_candidate_a_sparc_baryonic")
from emergent_matter_model.sparc_marginalized_a0 import MarginalizedGalaxy  # noqa: E402
from emergent_matter_model.sparc_real_analysis import Galaxy, nu_newton  # noqa: E402

PREREG = json.loads(TOOL.PREREGISTRATION.read_text(encoding="utf-8"))
SPARC = ROOT / "data" / "external" / "sparc"
HAVE_SPARC = all((SPARC / name).is_file() for name in TOOL.PINNED_DATA)


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _galaxy(halo_s=0.0, name="SYNTH"):
    r = np.linspace(0.5, 15.0, 25)
    v_disk = 120.0 * np.sqrt(r / 3.0) * np.exp(-r / 6.0)
    v_gas = 30.0 * np.sqrt(r / 10.0)
    v_bul = np.zeros_like(r)
    v_bar2 = v_gas * np.abs(v_gas) + 0.5 * v_disk * np.abs(v_disk)
    v_obs = np.sqrt(v_bar2 + TOOL.halo_v2(r, halo_s, math.log10(2.0)))
    return Galaxy(name, 10.0, 60.0, 1, r, v_obs, np.full_like(r, 3.0), v_gas, v_disk, v_bul,
                  e_distance_mpc=1.0, e_inclination_deg=3.0)


# --- frozen inputs ------------------------------------------------------------

def test_preregistration_is_frozen_and_pending_author_confirmation():
    assert _sha(TOOL.PREREGISTRATION) == TOOL.FROZEN_PREREGISTRATION_SHA256
    assert PREREG["operationalization_status"] == "assistant_proposed_pending_author_confirmation"
    assert PREREG["operationalization"]["free_physics_parameters"] == 0
    assert PREREG["outputs"]["tool"] == "tools/evaluate_candidate_a_sparc_baryonic.py"
    assert PREREG["outputs"]["artifact"] == "results/candidate_a_sparc_baryonic_test.json"
    pinned = {Path(h["path"]).name: (h["sha256"], h["bytes"]) for h in PREREG["data"]["holdings"]}
    assert pinned == TOOL.PINNED_DATA
    assert any("not blind" in line or "not discovery" in line
               for line in PREREG["prior_knowledge_disclosure"])


def test_frozen_candidate_a_files_keep_exact_bytes_in_git():
    attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
    assert "knowledgebase/candidate_a_*.json -text" in attributes


def test_modified_preregistration_is_refused(tmp_path, monkeypatch):
    copy = tmp_path / "prereg.json"
    copy.write_bytes(TOOL.PREREGISTRATION.read_bytes() + b" ")
    monkeypatch.setattr(TOOL, "PREREGISTRATION", copy)
    with pytest.raises(TOOL.IncompleteTestError):
        TOOL.verify_preregistration()


def test_unpinned_data_is_refused(tmp_path):
    for name, (_, size) in TOOL.PINNED_DATA.items():
        (tmp_path / name).write_bytes(b"0" * size)
    with pytest.raises(TOOL.IncompleteTestError):
        TOOL.verify_data(tmp_path)


# --- model algebra ------------------------------------------------------------

def test_halo_term_limits():
    r = np.array([1e-4, 1.0, 1e4])
    assert np.allclose(TOOL.halo_v2(r, 0.0, 0.0), 0.0)
    values = TOOL.halo_v2(r, 100.0**2, 0.0)
    assert values[0] == pytest.approx(1e4 * r[0] ** 2 / 3.0, rel=1e-6)
    assert values[2] == pytest.approx(1e4, rel=1e-3)
    assert np.all(np.diff(values) > 0)


def test_a2_matches_certified_pipeline_with_unit_nu():
    mg = MarginalizedGalaxy(_galaxy())
    for params in ([math.log10(0.5), 1.0, 60.0], [-0.1, 1.05, 63.0], [0.4, 0.9, 55.0]):
        assert TOOL.chi2_data(mg, params) == pytest.approx(
            mg.chi2(np.array(params), nu_newton, 1.0), rel=1e-12)


def test_ref_with_zero_halo_equals_a2():
    mg = MarginalizedGalaxy(_galaxy())
    params = [math.log10(0.5), 1.02, 61.0]
    assert np.allclose(TOOL.predicted_velocity(mg, params),
                       TOOL.predicted_velocity(mg, [*params, 0.0, 1.3]))


def test_treatments_differ_only_by_the_upsilon_prior():
    mg = MarginalizedGalaxy(_galaxy())
    params = np.array([0.3, 1.0, 60.0, 0.0, 0.0])
    t1 = TOOL.residuals(params, mg, "T1", 0.5)
    t2 = TOOL.residuals(params, mg, "T2", 0.5)
    assert len(t1) == len(t2) + 1
    assert t1[mg.gal.n] == pytest.approx((0.3 - math.log10(0.5)) / 0.1)
    with pytest.raises(ValueError):
        TOOL.residuals(params, mg, "T3", 0.5)


def test_baryonic_synthetic_galaxy_needs_no_unseen_mass():
    for treatment in TOOL.TREATMENTS:
        summary = TOOL.evaluate_population([_galaxy()], treatment)
        assert summary["delta_Q"] < 1e-3
        assert summary["galaxies_requiring_unseen_mass"] == 0
        assert not summary["exceeds_population_threshold"]


def test_halo_synthetic_galaxy_requires_unseen_mass():
    for treatment in TOOL.TREATMENTS:
        summary = TOOL.evaluate_population([_galaxy(halo_s=110.0**2)], treatment)
        row = summary["per_galaxy"][0]
        assert row["delta_Q"] > 100.0
        assert row["requires_unseen_mass"]
        assert row["ref_s_km2_s2"] == pytest.approx(110.0**2, rel=0.05)
        assert summary["exceeds_population_threshold"]


def test_classification_requires_both_treatments():
    yes, no = {"exceeds_population_threshold": True}, {"exceeds_population_threshold": False}
    assert TOOL.classify(yes, yes) == "rejected"
    assert TOOL.classify(yes, no) == "not_rejected"
    assert TOOL.classify(no, yes) == "not_rejected"
    assert pytest.approx(-2.0 * math.log(0.001)) == TOOL.GALAXY_THRESHOLD


# --- result artifact ----------------------------------------------------------

ARTIFACT = TOOL.OUTPUT
REPORT = json.loads(ARTIFACT.read_text(encoding="utf-8")) if ARTIFACT.is_file() else None


@pytest.mark.skipif(REPORT is None, reason="Candidate A SPARC artifact not generated")
def test_artifact_is_current_and_claims_no_confirmation():
    tool_path = ROOT / "tools" / "evaluate_candidate_a_sparc_baryonic.py"
    assert REPORT["source_sha256"] == _sha(tool_path)
    assert REPORT["dependency_sha256"] == {name: _sha(ROOT / name)
                                           for name in TOOL.SOURCE_DEPENDENCIES}
    assert REPORT["preregistration_sha256"] == TOOL.FROZEN_PREREGISTRATION_SHA256
    assert REPORT["operationalization_status"] == "assistant_proposed_pending_author_confirmation"
    assert "not blind" in REPORT["evidence_class"]
    assert REPORT["outcome"] in {"rejected", "not_rejected"}
    assert REPORT["protocol_deviations"] == []
    text = " ".join(REPORT["interpretation"]).lower()
    assert "not blind" in text and "pending" in text
    assert "confirms candidate a" not in text and "evidence for candidate a" not in text
    primary = REPORT["populations"]["primary"]
    for treatment in TOOL.TREATMENTS:
        summary = primary[treatment]
        assert summary["galaxies"] == 153 and summary["points"] == 3168
        assert summary["delta_Q_cons"] == pytest.approx(
            summary["delta_Q"] / summary["inflation_lambda"])
        assert summary["exceeds_population_threshold"] == (
            summary["delta_Q_cons"] > summary["population_threshold"])
        rows = REPORT["per_galaxy_primary"][treatment]
        assert len(rows) == 153 and all(row["delta_Q"] >= 0 for row in rows)
    assert REPORT["outcome"] == TOOL.classify(primary["T1"], primary["T2"])


@pytest.mark.skipif(REPORT is None or not HAVE_SPARC, reason="SPARC data or artifact missing")
def test_artifact_reproduces_for_first_galaxies_from_pinned_data():
    from emergent_matter_model.sparc_real_analysis import load_sparc

    TOOL.verify_data(SPARC)
    galaxies = load_sparc(SPARC)[:4]
    for treatment in TOOL.TREATMENTS:
        rows = TOOL.evaluate_population(galaxies, treatment)["per_galaxy"]
        for fresh, stored in zip(rows, REPORT["per_galaxy_primary"][treatment][:4], strict=True):
            assert fresh["galaxy"] == stored["galaxy"]
            assert fresh["Q_A2"] == pytest.approx(stored["Q_A2"], rel=1e-6, abs=1e-6)
            assert fresh["Q_REF"] == pytest.approx(stored["Q_REF"], rel=1e-6, abs=1e-6)
