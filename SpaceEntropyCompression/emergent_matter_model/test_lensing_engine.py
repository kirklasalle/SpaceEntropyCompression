"""Unit tests for Relativistic Gravitational Lensing & Geodesic Ray-Tracing Engine."""

import pytest
import numpy as np
from lensing_engine import (
    SLACS_BENCHMARKS,
    angular_diameter_distance_flat_lcdm,
    angular_diameter_distance_ratio,
    compute_einstein_radius_sis,
    calculate_deflection_angle_profile,
    trace_null_geodesics_2d,
    evaluate_slacs_sample,
    summarize_lensing_results,
)


class TestCosmologicalDistances:
    def test_distance_increases_with_redshift(self):
        """Angular diameter distance should initially increase with redshift."""
        d1 = angular_diameter_distance_flat_lcdm(0.2)
        d2 = angular_diameter_distance_flat_lcdm(0.5)
        assert d2 > d1 > 0.0

    def test_distance_ratio_physical_bounds(self):
        """Ratio D_LS / D_S must be between 0 and 1 for z_source > z_lens."""
        ratio = angular_diameter_distance_ratio(0.2, 0.8)
        assert 0.0 < ratio < 1.0

    def test_distance_ratio_zero_if_source_behind_lens(self):
        """If source is at or in front of lens, ratio must be 0."""
        assert angular_diameter_distance_ratio(0.5, 0.2) == 0.0


class TestLensingDeflectionAndRays:
    def test_einstein_radius_scaling_with_dispersion(self):
        """Einstein radius must scale as sigma_v^2."""
        d_ratio = 0.5
        theta1 = compute_einstein_radius_sis(150.0, d_ratio)
        theta2 = compute_einstein_radius_sis(300.0, d_ratio)
        assert pytest.approx(theta2 / theta1, rel=1e-3) == 4.0

    def test_deflection_angle_profile_flat_asymptote(self):
        """At large impact parameter, isothermal deflection angle approaches constant."""
        b_large = np.array([50.0, 100.0, 200.0])
        alpha = calculate_deflection_angle_profile(b_large, v_circ_kms=220.0, r_core_kpc=0.5)
        assert abs(alpha[2] - alpha[1]) / alpha[1] < 0.02

    def test_trace_null_geodesics_mapping(self):
        """Ray tracer maps lens plane grid to deflected source plane."""
        grid = np.array([[-1.0, 1.0], [0.0, 0.0]])
        sx, sy = trace_null_geodesics_2d(grid, theta_ein_kpc=1.0)
        assert sx.shape == (2,)
        # At r = 1.0, deflection cancels position (critical curve / caustic map)
        assert abs(sx[0] - 0.0) < 1e-10
        assert abs(sx[1] - 0.0) < 1e-10


class TestSLACSSampleEvaluation:
    def test_slacs_benchmarks_consistency(self):
        """All SLACS benchmark lenses evaluate with physical predicted Einstein radii."""
        summary = summarize_lensing_results()
        assert summary["n_lenses"] == len(SLACS_BENCHMARKS)
        assert summary["total_chi2"] > 0.0
        for name, data in summary["evaluations"].items():
            assert 0.5 < data["theta_pred_arcsec"] < 2.0
            assert data["residual_arcsec"] < 0.35
