"""Offline tests for sparc_bulge_test.py (in-memory toy galaxies; no real data)."""

import math

import numpy as np
import pytest

from sparc_bulge_test import FreeBulgeGalaxy, ScaledBulgeGalaxy, classify, required_ratio
from sparc_real_analysis import ACC, Galaxy, nu_rar_exponential


def _bulge_galaxy(a0, ups_disk, ups_bulge):
    r = np.linspace(0.5, 25.0, 30)
    vd = 110.0 * np.sqrt(r / 4.0) * np.exp(-r / 8.0) + 1e-3
    vb = 150.0 * np.sqrt(r / (r + 1.0)) / np.sqrt(1.0 + r / 2.0)
    vg = 20.0 * (1 - np.exp(-r / 6.0))
    g_bar = (vg**2 + ups_disk * vd**2 + ups_bulge * vb**2) / r * ACC
    v = np.sqrt(g_bar * nu_rar_exponential(g_bar / a0) / ACC * r)
    return Galaxy("B", 10.0, 60.0, 1, r, v, np.full_like(r, 2.0), vg, vd, vb,
                  e_distance_mpc=1.0, e_inclination_deg=3.0, luminosity_36=10.0, m_hi=0.5)


def test_classify_thresholds():
    assert classify(0.7) == "plausible"
    assert classify(1.2) == "stretched"
    assert classify(0.4) == "stretched"
    assert classify(2.0) == "implausible"
    assert classify(0.2) == "implausible"


def test_required_ratio_interpolation():
    scan = [{"ratio": 1.0, "a0": 2.0e-10}, {"ratio": 2.0, "a0": 1.4e-10}, {"ratio": 4.0, "a0": 0.8e-10}]
    assert required_ratio(scan, 1.1e-10) == pytest.approx(3.0)
    assert required_ratio(scan, 0.5e-10) is None


def test_scaled_bulge_reproduces_standard_model():
    gal = _bulge_galaxy(1.0e-10, 0.5, 0.7)
    mg = ScaledBulgeGalaxy(gal, 1.4)
    assert mg.chi2(np.array([math.log10(0.5), 1.0, 60.0]), nu_rar_exponential, 1.0e-10) < 1e-12


def test_free_bulge_recovers_heavy_bulge():
    gal = _bulge_galaxy(1.0e-10, 0.5, 1.8)
    fit = FreeBulgeGalaxy(gal).fit_free(nu_rar_exponential, 1.0e-10)
    assert fit["ups_bulge"] == pytest.approx(1.8, rel=0.05)
    assert classify(fit["ups_bulge"]) == "implausible"
