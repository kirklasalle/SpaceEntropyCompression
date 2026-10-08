"""Offline tests for sparc_marginalized_a0.py (in-memory toy galaxies only; no real data)."""

import math

import numpy as np
import pytest

from sparc_marginalized_a0 import (MarginalizedGalaxy, a0_lambda, best_a0, implied_h0, profile)
from sparc_real_analysis import ACC, Galaxy, a0_horizon, nu_rar_exponential


def test_implied_h0_inverts_horizon_relation():
    assert implied_h0(a0_horizon(67.4)) == pytest.approx(67.4, rel=1e-9)
    assert implied_h0(1.20e-10) == pytest.approx(77.6, abs=0.1)


def test_lambda_variant_value():
    assert a0_lambda(67.4, 0.685) == pytest.approx(0.8627e-10, rel=2e-3)


def _toy(a0_true, ups_true, f_d_true, inc_true, inc_cat, scale, name):
    """Galaxy whose catalogue distance/inclination are wrong by known amounts."""
    r = np.linspace(0.5, 25.0, 25)
    vd = scale * 110.0 * np.sqrt(r / 3.0) * np.exp(-r / 6.0) + 1e-3
    vg = scale * 45.0 * (1 - np.exp(-r / 4.0))
    vb2 = vg * np.abs(vg) + ups_true * vd * np.abs(vd)
    g_bar = vb2 / r * ACC                       # invariant under the distance rescaling
    g_mod = g_bar * nu_rar_exponential(g_bar / a0_true)
    v_true = np.sqrt(g_mod / ACC * r * f_d_true)
    v_cat = v_true * math.sin(math.radians(inc_true)) / math.sin(math.radians(inc_cat))
    return Galaxy(name, 10.0, inc_cat, 1, r, v_cat, np.full_like(r, 2.0), vg, vd, np.zeros_like(r),
                  e_distance_mpc=1.5, e_inclination_deg=4.0, luminosity_36=1.0, m_hi=1.0)


def test_chi2_is_zero_at_true_nuisance_parameters():
    # Distance and inclination both rescale velocities and can partially cancel, so pick offsets
    # that reinforce: f_D = 1.08 (V up) and a true inclination above the catalogue (V_cat too high).
    gal = _toy(1.1e-10, 0.5, 1.08, 66.0, 62.0, 1.0, "T")
    mg = MarginalizedGalaxy(gal)
    assert mg.chi2(np.array([math.log10(0.5), 1.08, 66.0]), nu_rar_exponential, 1.1e-10) < 1e-12
    assert mg.chi2(np.array([math.log10(0.5), 1.00, 62.0]), nu_rar_exponential, 1.1e-10) > 1.0


GRID = np.arange(0.8e-10, 1.5e-10, 0.02e-10)
SCALES = (0.4, 0.7, 1.0, 1.5, 2.2, 3.0)


def test_profile_recovers_a0_exactly_when_catalogue_is_correct():
    gals = [MarginalizedGalaxy(_toy(1.1e-10, 0.5, 1.0, 60.0, 60.0, s, f"T{k}")) for k, s in enumerate(SCALES)]
    b = best_a0(GRID, profile(gals, nu_rar_exponential, "rar", 0.5, GRID)[:, :, 0].sum(axis=1), 1.0)
    assert b["a0"] == pytest.approx(1.1e-10, rel=0.01)


def test_estimator_is_unbiased_with_wrong_catalogue_distances_and_inclinations():
    """Averaged over realizations of distance/inclination errors drawn from the priors, the fitted a0
    must be unbiased (single realizations scatter by ~7% with only six galaxies)."""
    fits = []
    for seed in range(10):
        rng = np.random.default_rng(seed)
        gals = [MarginalizedGalaxy(_toy(1.1e-10, 0.5, 1.0 + 0.08 * rng.standard_normal(),
                                        60.0 + 3.0 * rng.standard_normal(), 60.0, s, f"T{k}"))
                for k, s in enumerate(SCALES)]
        b = best_a0(GRID, profile(gals, nu_rar_exponential, "rar", 0.5, GRID)[:, :, 0].sum(axis=1), 1.0)
        assert not b["at_grid_edge"]
        fits.append(b["a0"])
    assert np.mean(fits) == pytest.approx(1.1e-10, rel=0.04)


def test_best_a0_parabola_exact_for_quadratic():
    grid = np.linspace(0.8e-10, 1.4e-10, 31)
    obj = ((grid - 1.07e-10) / 0.05e-10) ** 2 + 10.0
    b = best_a0(grid, obj, 1.0)
    assert b["a0"] == pytest.approx(1.07e-10, rel=1e-6)
    assert b["sigma_stat"] == pytest.approx(0.05e-10, rel=1e-6)
