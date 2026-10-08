"""The horizon audit must never label an encoded identity as empirical evidence."""

import importlib.util
from pathlib import Path

import pytest


def test_algebra_audit_labels_and_values():
    path = Path(__file__).resolve().parents[1] / "tools" / "check_compression_claims.py"
    spec = importlib.util.spec_from_file_location("compression_audit", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.audit()
    assert result["empirical_validation"] is False
    assert result["evidence_type"] == "software_algebra_diagnostics_not_observations"
    for particle in result["quantum_mass_normalization"]:
        assert particle["reported_mass_kg"] == pytest.approx(particle["input_mass_kg"], abs=0)
        assert "not a prediction" in particle["interpretation"]
    assert result["black_hole_identity"]["coefficient_S_lP2_over_kBA"] == pytest.approx(0.25)
    assert result["temperature_equality"]["a_over_cH"] == 1
    assert result["conditional_density_scaling"]["flat_speed_alpha"] == pytest.approx(2 / 3)
    assert all(len(value) == 64 for value in result["source_sha256"].values())
