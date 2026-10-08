"""Offline tests for sparc_tension_diagnostics.py (in-memory toy galaxies; no real data)."""

import numpy as np
import pytest

from sparc_real_analysis import Galaxy, g_newton
from sparc_tension_diagnostics import (A0_REF, DEEP_FRACTION, MIN_POINTS, build_subsets, deep_point_mask,
                                       has_bulge, local_gas_point_mask, subset_points, tension)


def _gal(name, v_gas, v_disk, v_bul, m_hi, lum):
    r = np.linspace(1.0, 30.0, len(v_gas))
    return Galaxy(name, 10.0, 60.0, 1, r, np.full_like(r, 100.0), np.full_like(r, 3.0),
                  np.asarray(v_gas, float), np.asarray(v_disk, float), np.asarray(v_bul, float),
                  e_distance_mpc=1.0, e_inclination_deg=3.0, luminosity_36=lum, m_hi=m_hi)


def test_bulge_flag():
    assert has_bulge(_gal("B", [10] * 5, [50] * 5, [0, 20, 0, 0, 0], 1, 1))
    assert not has_bulge(_gal("N", [10] * 5, [50] * 5, [0] * 5, 1, 1))


def test_deep_mask_matches_threshold():
    g = _gal("D", np.linspace(5, 40, 8), np.linspace(120, 20, 8), [0] * 8, 1, 1)
    m = deep_point_mask(g)
    assert np.array_equal(m, g_newton(g, 0.5) < DEEP_FRACTION * A0_REF)
    assert m[-1] and not m[0]


def test_local_gas_mask():
    g = _gal("L", [10, 50, 80], [100, 50, 20], [0, 0, 0], 1, 1)
    # gas^2 vs 0.5*disk^2: 100 vs 5000 ; 2500 vs 1250 ; 6400 vs 200
    assert local_gas_point_mask(g).tolist() == [False, True, True]


def test_subset_points_drops_short_galaxies():
    g = _gal("S", [10] * 6, [50] * 6, [0] * 6, 1, 1)
    keep = np.array([True] * MIN_POINTS + [False] * (6 - MIN_POINTS))
    assert subset_points(g, keep).n == MIN_POINTS
    assert subset_points(g, np.array([True] * (MIN_POINTS - 1) + [False] * (7 - MIN_POINTS))) is None


def test_build_subsets_partitions_gas_and_star():
    gas_rich = _gal("G", [60] * 6, [20] * 6, [0] * 6, m_hi=5.0, lum=1.0)
    star_rich = _gal("S", [10] * 6, [150] * 6, [30] * 6, m_hi=0.1, lum=20.0)
    s = build_subsets([gas_rich, star_rich])
    assert [g.name for g in s["gas_dominated"]] == ["G"]
    assert [g.name for g in s["star_dominated"]] == ["S"]
    assert s["star_bulgeless"] == []
    assert [g.name for g in s["star_bulge"]] == ["S"]


def test_tension_formula():
    a = {"a0": 1.2e-10, "sigma_total": 0.03e-10}
    b = {"a0": 1.0e-10, "sigma_total": 0.04e-10}
    assert tension(a, b) == pytest.approx(4.0)
