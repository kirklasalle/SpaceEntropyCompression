"""Check standard-background algebra and the limits of Candidate A claims."""
import hashlib
import importlib.util
import json
import math
import re
from pathlib import Path, PureWindowsPath
from urllib.parse import unquote

import pytest

PATH = Path(__file__).resolve().parents[1] / "tools" / "check_candidate_a_definitions.py"
SPEC = importlib.util.spec_from_file_location("candidate_a_checks", PATH)
CHECKS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKS)


def test_ricci_does_not_measure_all_local_energy():
    radiation = CHECKS.perfect_fluid_curvatures(3., 1.)
    assert radiation["ricci_scalar_m_minus2"] == 0.
    assert radiation["einstein_projection_minus_lambda_m_minus2"] > 0.
    assert radiation["observer_energy_mass_density_kg_m3"] > 0.
    vacuum_lambda = CHECKS.perfect_fluid_curvatures(0., 0., 1e-52)
    assert vacuum_lambda["ricci_scalar_m_minus2"] == 4e-52
    assert vacuum_lambda["einstein_projection_minus_lambda_m_minus2"] == 0.


def test_projection_mapping_normalization_is_an_identity():
    for c0 in (1e-10, 1e-20, 1e-50):
        energy = 3e5
        curvature = CHECKS.perfect_fluid_curvatures(energy, energy/4)[
            "einstein_projection_minus_lambda_m_minus2"]
        k = CHECKS.normalization_for_projection(c0)
        assert k*curvature/c0 == pytest.approx(energy/CHECKS.C_LIGHT**2, rel=1e-13, abs=0)


def test_vacuum_curvature_and_quasilocal_definitions_are_distinct():
    mass = 1.98847e30
    rs = 2*CHECKS.G*mass/CHECKS.C_LIGHT**2
    row = CHECKS.schwarzschild_diagnostics(mass, 2*rs)
    assert row["tidal_curvature_sqrtK_m_minus2"] > 0
    assert row["local_stress_energy_mass_density_kg_m3"] == 0
    assert row["brown_york_energy_over_c2_kg"]/mass == pytest.approx(4*(1-math.sqrt(.5)))
    assert row["misner_sharp_mass_kg"] == pytest.approx(mass, rel=1e-13)
    assert row["mass_from_K_and_areal_radius_kg"] == pytest.approx(mass)
    outer = CHECKS.schwarzschild_diagnostics(mass, rs*1e10)
    assert outer["brown_york_energy_over_c2_kg"]/mass == pytest.approx(1., abs=1e-9)


def test_scalar_curvature_does_not_uniquely_determine_mass():
    report = CHECKS.build_report()
    a, b = report["same_K_different_mass_and_radius"]
    assert a["kretschmann_m_minus4"] == pytest.approx(b["kretschmann_m_minus4"], abs=0)
    assert b["mass_input_kg"] == 8*a["mass_input_kg"]
    assert report["physical_model_implemented"] is False
    assert report["evidence_kind"] == "exact_background_algebra_not_observations"


@pytest.mark.parametrize("value", [0., -1., float("nan"), float("inf")])
def test_invalid_normalization_is_explicit(value):
    with pytest.raises(ValueError, match="positive"):
        CHECKS.normalization_for_projection(value)


def test_static_boundary_domain_is_explicit():
    mass = 1e30
    with pytest.raises(ValueError, match="r > r_s"):
        CHECKS.schwarzschild_diagnostics(mass, 2*CHECKS.G*mass/CHECKS.C_LIGHT**2)


def test_document_graph_and_ledger_preserve_review_boundary():
    root = PATH.parents[1]
    ledger_path = root / "knowledgebase" / "thermodynamic_collision_candidates.json"
    ledger = json.loads(ledger_path.read_text())
    comparison = ledger["functional_comparison"]
    assert comparison["author_selected_specific_functional"] is False
    assert comparison["energy_sector_added"] is False
    assert comparison["recommended_local_reference"]["alpha_for_GR_identity"] == 1
    graph = json.loads((root / "knowledgebase" / "GRAPH_MEMORY.json").read_text(encoding="utf-8"))
    node = next(n for n in graph["nodes"] if n["id"] == (
        "definition:candidate_a_local_energy_reference"))
    assert node["status"] == "assistant_recommendation_not_author_selected"
    assert node["use_for_empirical_confirmation"] is False
    path = root / comparison["document"]
    for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
        if "://" not in target and not target.startswith("#"):
            assert (path.parent / unquote(target.split("#")[0])).exists()
    artifact = root / comparison["diagnostic_artifact"]
    result = json.loads(artifact.read_text())
    for path_string, expected in result["source_sha256"].items():
        source = root.joinpath(*PureWindowsPath(path_string).parts)
        assert hashlib.sha256(source.read_bytes()).hexdigest() == expected
