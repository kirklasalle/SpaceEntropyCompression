"""Fail-closed provenance and conditional profile intervals."""
import hashlib
import importlib.util
from pathlib import Path

import numpy as np
import pytest

from data_provenance import verify_observation_file


def test_provenance_rejects_unmarked_and_modified_files(tmp_path):
    path = tmp_path / "measurement.txt"
    path.write_bytes(b"observed table\n")
    with pytest.raises(ValueError, match="source"):
        verify_observation_file(path, {})
    record = {"url": "https://example.org/data", "citation": "Test software fixture",
              "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size}
    assert verify_observation_file(path, record) == record["sha256"]
    path.write_bytes(b"changed")
    with pytest.raises(ValueError, match="mismatch"):
        verify_observation_file(path, record)


def test_synthetic_marker_cannot_be_authenticated(tmp_path):
    path = tmp_path / "data.txt"
    path.write_bytes(b"# SYNTHETIC DATA\n")
    record = {"url": "https://example.org/data", "citation": "Fixture",
              "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size}
    with pytest.raises(ValueError, match="Synthetic"):
        verify_observation_file(path, record)


def test_missing_file_cannot_be_authenticated(tmp_path):
    with pytest.raises(FileNotFoundError):
        verify_observation_file(tmp_path / "missing", {})


def test_profile_boundary_is_not_fabricated_interval():
    path = Path(__file__).resolve().parents[1] / "tools" / "run_sparc_profile_validation.py"
    spec = importlib.util.spec_from_file_location("profile_validation", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.profile_interval(np.array([1., 2., 3.]), np.array([0., .5, 2.]))
    assert result["at_grid_edge"]
    assert result["delta_Q_1_interval"][0] is None
    assert result["delta_Q_1_interval"][1] == pytest.approx(2 + 1/3)
    assert "not calibrated" in result["interval_kind"]


def test_gauntlet_has_all_cases_without_declaring_passes():
    path = Path(__file__).resolve().parents[1] / "tools" / "run_real_data_gauntlet.py"
    spec = importlib.util.spec_from_file_location("gauntlet_validation", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    ids = [case[0] for case in module.CASES]
    assert len(ids) == len(set(ids)) == 13
    assert set(ids) == {f"R{i:02}" for i in range(1, 11)} | {"H01", "H02", "H03"}
    assert all(case[4] for case in module.CASES)


def test_residual_likelihood_matches_original_coordinates():
    path = Path(__file__).resolve().parents[1] / "tools" / "run_sparc_profile_validation.py"
    spec = importlib.util.spec_from_file_location("profile_validation", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    galaxy = module.load_sparc()[0]
    mg = module.MarginalizedGalaxy(galaxy)
    nu = module.LAWS["rar_exponential"][1]
    x = np.array([np.log10(.6), 1.03, galaxy.inclination_deg - 2])
    residual = module.residual_vector(x, mg, nu, 1.2e-10, .5)
    assert residual @ residual == pytest.approx(
        mg.chi2(x, nu, 1.2e-10) + mg.prior(x, .5), rel=1e-12)
    grid = np.array([.9e-10, 1.2e-10, 1.5e-10])
    forward, _ = module.scan([galaxy], grid)
    reverse, _ = module.scan([galaxy], grid, reverse=True)
    np.testing.assert_allclose(forward, reverse, atol=.01, rtol=0)
    with pytest.raises(ValueError, match="finite"):
        module.profile_interval(grid, np.array([1., np.nan, 2.]))
    for _, law in module.LAWS.values():
        analytic = module.residual_jacobian(x, mg, law, 1.2e-10, .5)
        numeric = np.column_stack([
            (module.residual_vector(x + np.eye(3)[j]*1e-5, mg, law, 1.2e-10, .5)
             - module.residual_vector(x - np.eye(3)[j]*1e-5, mg, law, 1.2e-10, .5))/2e-5
            for j in range(3)])
        np.testing.assert_allclose(analytic, numeric, rtol=1e-5, atol=1e-6)


def test_signed_gas_floor_branches_are_searched():
    path = Path(__file__).resolve().parents[1] / "tools" / "run_sparc_profile_validation.py"
    spec = importlib.util.spec_from_file_location("profile_validation", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    galaxy = next(g for g in module.load_sparc() if g.name == "UGC07577")
    grid = np.array([.7e-10, .75e-10, .8e-10])
    forward, _ = module.scan([galaxy], grid)
    reverse, _ = module.scan([galaxy], grid, reverse=True)
    assert forward[1, 0] < 51.182
    np.testing.assert_allclose(forward, reverse, atol=1e-5, rtol=0)


def test_desi_baseline_uses_observed_covariance_and_is_not_emrf():
    path = Path(__file__).resolve().parents[1] / "tools" / "run_real_data_gauntlet.py"
    spec = importlib.util.spec_from_file_location("gauntlet_validation", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cache = path.parents[1] / "data" / "external" / "real_data_v1"
    if not (cache / "desi_2024_gaussian_bao_ALL_GCcomb_mean.txt").exists():
        pytest.skip("Run real-data gauntlet to retrieve the pinned DESI likelihood")
    result = module.desi_baseline(cache)
    assert result["n"] == 12
    assert result["degrees_of_freedom"] == 10
    assert result["covariance_used"]
    assert result["evidence_grade"] == "baseline_only_not_EMRF"
    assert result["chi2"] == pytest.approx(12.7405324, abs=1e-5)
