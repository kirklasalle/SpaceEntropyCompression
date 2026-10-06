"""Unit tests for the relativistic and celestial mechanics baseline module."""

from __future__ import annotations

import numpy as np
import pytest

from physics_baseline import (
    AU,
    G,
    SGR_A_MASS,
    YEAR_SEC,
    integrate_orbit_1pn,
    keplerian_orbit_2d,
    kretschmann_invariant,
    schwarzschild_1pn_acceleration,
    schwarzschild_pericenter_advance_analytical,
    solve_kepler,
)


class TestKeplerSolver:
    """Tests for Kepler's equation solver."""

    def test_circular_orbit_zero_eccentricity(self):
        for m in [0.0, 0.5, np.pi / 2, np.pi, 1.5 * np.pi]:
            e_sol = solve_kepler(m, 0.0)
            assert np.isclose(e_sol, m, atol=1e-12)

    def test_kepler_residual_convergence(self):
        for ecc in [0.1, 0.5, 0.884]:  # 0.884 is Star S2 eccentricity
            for m in np.linspace(0.0, 2.0 * np.pi, 20):
                e_sol = solve_kepler(m, ecc)
                residual = e_sol - ecc * np.sin(e_sol) - (m % (2.0 * np.pi))
                assert abs(residual) < 1e-10

    def test_invalid_eccentricity_raises(self):
        with pytest.raises(ValueError, match="Eccentricity must be in"):
            solve_kepler(1.0, 1.05)
        with pytest.raises(ValueError, match="Eccentricity must be in"):
            solve_kepler(1.0, -0.1)


class TestKeplerianOrbit:
    """Tests for 2D Newtonian Keplerian trajectories."""

    def test_period_and_vis_viva_conservation(self):
        # Star S2 approximate parameters
        a = 970.0 * AU
        e = 0.884
        mu = G * SGR_A_MASS
        period = 2.0 * np.pi * np.sqrt(a**3 / mu)

        # Evaluate at t = 0 (pericenter) and t = period (1 full revolution)
        times = np.array([0.0, period / 2.0, period])
        x, y, vx, vy = keplerian_orbit_2d(a, e, SGR_A_MASS, times)

        # Pericenter position at t = 0: r = a(1 - e)
        r_peri = np.sqrt(x[0]**2 + y[0]**2)
        assert np.isclose(r_peri, a * (1.0 - e), rtol=1e-6)

        # Apocenter position at t = period / 2: r = a(1 + e)
        r_apo = np.sqrt(x[1]**2 + y[1]**2)
        assert np.isclose(r_apo, a * (1.0 + e), rtol=1e-6)

        # Full revolution returns to pericenter
        assert np.isclose(x[2], x[0], rtol=1e-6)
        assert np.isclose(y[2], y[0], atol=1e-3)

        # Vis-viva check: v^2 = mu * (2/r - 1/a)
        for i in range(len(times)):
            r_i = np.sqrt(x[i]**2 + y[i]**2)
            v_sq = vx[i]**2 + vy[i]**2
            v_expected_sq = mu * (2.0 / r_i - 1.0 / a)
            assert np.isclose(v_sq, v_expected_sq, rtol=1e-6)


class TestKretschmannInvariant:
    """Tests for the Kretschmann scalar curvature calculation."""

    def test_kretschmann_r6_falloff(self):
        r1 = 100.0 * AU
        r2 = 200.0 * AU
        k1 = kretschmann_invariant(r1, SGR_A_MASS)
        k2 = kretschmann_invariant(r2, SGR_A_MASS)

        # Exact ratio must be (r2 / r1)^6 = 2^6 = 64
        ratio = k1 / k2
        assert np.isclose(ratio, 64.0, rtol=1e-10)

    def test_kretschmann_array_input(self):
        r_arr = np.array([50.0, 100.0, 200.0]) * AU
        k_arr = kretschmann_invariant(r_arr, SGR_A_MASS)
        assert isinstance(k_arr, np.ndarray)
        assert len(k_arr) == 3
        assert np.all(np.diff(k_arr) < 0)  # Monotonically decreasing with r

    def test_zero_or_negative_radius_raises(self):
        with pytest.raises(ValueError, match="strictly positive"):
            kretschmann_invariant(0.0, SGR_A_MASS)


class TestRelativisticSchwarzschild:
    """Tests for 1PN Schwarzschild acceleration and precession."""

    def test_star_s2_pericenter_precession(self):
        # S2 semi-major axis ~1030 AU, e ~ 0.884 (GRAVITY Collaboration baseline)
        a = 1030.0 * AU
        e = 0.884
        delta_phi_rad = schwarzschild_pericenter_advance_analytical(a, e, SGR_A_MASS)

        # Convert to arcminutes: rad * (180 / pi) * 60
        delta_phi_arcmin = delta_phi_rad * (180.0 / np.pi) * 60.0

        # Star S2 observed GR precession is ~12.1 arcminutes per revolution (~0.20 deg)
        assert 11.5 < delta_phi_arcmin < 12.8

    def test_star_s301_extreme_precession(self):
        # S301 (August 2026 Nature): a ~ 600 AU, pericenter ~ 12 AU -> e ~ 0.98
        a = 600.0 * AU
        e = 0.98
        delta_phi_rad = schwarzschild_pericenter_advance_analytical(a, e, SGR_A_MASS)
        delta_phi_deg = np.degrees(delta_phi_rad)

        # S301 experiences extreme precession of ~1.88 degrees per revolution!
        assert delta_phi_deg > 1.5

    def test_1pn_acceleration_direction_and_magnitude(self):
        r_vec = np.array([100.0 * AU, 0.0])
        v_vec = np.array([0.0, 5000.0])  # Transverse velocity

        a_vec = schwarzschild_1pn_acceleration(r_vec, v_vec, SGR_A_MASS)
        assert a_vec[0] < 0  # Attractive force in x direction

        # 1PN acceleration magnitude must be slightly larger than Newtonian gravity
        mu = G * SGR_A_MASS
        r = np.linalg.norm(r_vec)
        a_newt_mag = mu / (r**2)
        a_1pn_mag = np.linalg.norm(a_vec)
        assert a_1pn_mag > a_newt_mag

    def test_short_orbit_integration(self):
        # Quick RK4 integration of 100 days
        a = 970.0 * AU
        e = 0.884
        mu = G * SGR_A_MASS

        # Pericenter initial state
        r_peri = a * (1.0 - e)
        v_peri = np.sqrt(mu * (2.0 / r_peri - 1.0 / a))

        r0 = np.array([r_peri, 0.0])
        v0 = np.array([0.0, v_peri])

        times, r_hist, v_hist = integrate_orbit_1pn(
            r0=r0,
            v0=v0,
            mass_central=SGR_A_MASS,
            t_span=(0.0, 100.0 * 86400.0),
            dt=3600.0,  # 1 hour steps
        )

        assert len(times) > 0
        assert r_hist.shape == (len(times), 2)
        assert v_hist.shape == (len(times), 2)
        # Position should move smoothly away from pericenter
        r_mags = np.linalg.norm(r_hist, axis=1)
        assert r_mags[-1] > r_mags[0]
