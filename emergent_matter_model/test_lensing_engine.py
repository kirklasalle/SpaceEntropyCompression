"""Unit tests for Relativistic Gravitational Lensing & Geodesic Ray-Tracing Engine."""

import math

import numpy as np
import pytest

from lensing_engine import (
    C_LIGHT,
    M_SUN,
    SLACS_BENCHMARKS,
    G,
    angular_diameter_distance_flat_lcdm,
    angular_diameter_distance_ratio,
    calculate_deflection_angle_profile,
    compute_einstein_radius_sis,
    finite_path_point_mass_deflection,
    integrate_point_mass_deflection,
    point_mass_deflection_angle,
    summarize_lensing_results,
    trace_null_geodesics_2d,
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
    def test_point_mass_deflection_recovers_general_relativity_limit(self):
        impact = 6.957e8
        measured = point_mass_deflection_angle(M_SUN, impact)
        expected = 4.0 * G * M_SUN / (C_LIGHT**2 * impact)
        assert measured == pytest.approx(expected, rel=2e-15)
        assert measured * 180.0 * 3600.0 / math.pi == pytest.approx(
            1.7512,
            rel=5e-4,
        )

    def test_point_mass_ray_integration_is_second_order(self):
        impact = 6.957e8
        limit = 20.0 * impact
        expected = finite_path_point_mass_deflection(M_SUN, impact, limit)
        errors = [
            abs(
                integrate_point_mass_deflection(
                    M_SUN,
                    impact,
                    line_of_sight_limit_m=limit,
                    intervals=intervals,
                )
                - expected
            )
            for intervals in (256, 512, 1024)
        ]
        orders = [
            math.log2(errors[index] / errors[index + 1])
            for index in range(2)
        ]
        assert min(orders) == pytest.approx(2.0, rel=0.03)

    @pytest.mark.parametrize(
        "arguments",
        [
            (float("nan"), 1.0),
            (1.0, float("inf")),
            (-1.0, 1.0),
        ],
    )
    def test_point_mass_deflection_rejects_invalid_inputs(self, arguments):
        with pytest.raises(ArithmeticError, match="finite and positive"):
            point_mass_deflection_angle(*arguments)

    def test_point_mass_deflection_rejects_non_finite_result(self):
        with pytest.raises(ArithmeticError, match="non-finite"):
            point_mass_deflection_angle(float.fromhex("0x1.fffffffffffffp+1023"), 1e-300)

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
        for data in summary["evaluations"].values():
            assert 0.5 < data["theta_pred_arcsec"] < 2.0
            assert data["residual_arcsec"] < 0.35
