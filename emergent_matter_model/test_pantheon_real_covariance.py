"""Software checks for covariance parsing and the explicitly non-EMRF baseline."""
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.linalg import cholesky

PATH = Path(__file__).resolve().parents[1] / "tools" / "fit_pantheon_real_covariance.py"
SPEC = importlib.util.spec_from_file_location("pantheon_baseline", PATH)
BASELINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASELINE)


def test_declared_covariance_rounding_and_dimension_checks(tmp_path):
    path = tmp_path / "cov.txt"
    path.write_text("2\n1\n0.10000001\n0.1\n2\n")
    cov, difference = BASELINE.read_covariance(path, 2)
    assert difference == pytest.approx(1e-8)
    np.testing.assert_allclose(cov, cov.T, rtol=0, atol=0)
    with pytest.raises(ValueError, match="dimension"):
        BASELINE.read_covariance(path, 3)
    path.write_text("2\n1\n0.2\n0.1\n2\n")
    with pytest.raises(ValueError, match="asymmetry"):
        BASELINE.read_covariance(path, 2)


def test_nonfinite_covariance_is_rejected(tmp_path):
    path = tmp_path / "cov.txt"
    path.write_text("2\n1\nnan\nnan\n2\n")
    with pytest.raises(ValueError, match="non-finite"):
        BASELINE.read_covariance(path, 2)


def test_magnitude_integral_and_heliocentric_factor():
    zhd = np.array([.02, .5, 2.0])
    zhel = zhd + .001
    actual = BASELINE.dimensionless_magnitudes(zhd, zhel, .3)
    expected = np.array([
        5*np.log10((1+zh)*quad(lambda z: 1/np.sqrt(.3*(1+z)**3+.7), 0, zc)[0])
        for zc, zh in zip(zhd, zhel, strict=True)
    ])
    np.testing.assert_allclose(actual, expected, atol=1e-10, rtol=0)
    with pytest.raises(ValueError, match="Invalid"):
        BASELINE.dimensionless_magnitudes(np.array([0.]), np.array([0.]), .3)


def test_offset_profiles_full_covariance_not_diagonal():
    covariance = np.array([[1., .8], [.8, 2.]])
    observed, prediction = np.array([4., 6.]), np.array([1., 2.])
    chi2, offset = BASELINE.profile_offset(observed, prediction, cholesky(covariance, lower=True))
    inverse = np.linalg.inv(covariance)
    ones = np.ones(2)
    expected = (ones @ inverse @ (observed-prediction)) / (ones @ inverse @ ones)
    residual = observed-prediction-expected
    assert offset == pytest.approx(expected)
    assert chi2 == pytest.approx(residual @ inverse @ residual)
    _, diagonal_offset = BASELINE.profile_offset(
        observed, prediction, cholesky(np.diag(np.diag(covariance)), lower=True))
    assert abs(offset-diagonal_offset) > .1


def test_recorded_real_data_result_is_traceable_and_not_emrf():
    path = PATH.parents[1] / "results" / "real_data_followup" / "pantheon_baseline.json"
    if not path.exists():
        pytest.skip("Run the full-covariance baseline to generate its observed-data artifact")
    result = json.loads(path.read_text())
    assert result["evidence_grade"] == "baseline_only_not_EMRF"
    assert result["H0_inferred"] is False
    assert result["selected_rows"] == 1590
    assert result["distinct_CID"] == 1473
    assert result["chi2"] == pytest.approx(1402.9191283, abs=1e-5)
    assert result["source_sha256"] == hashlib.sha256(PATH.read_bytes()).hexdigest()
    assert result["integration_check_absolute_delta_chi2"] < 1e-6
