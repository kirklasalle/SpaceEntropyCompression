"""Offline unit tests for sparc_real_analysis.py (no network, no real data needed)."""

import math
from types import SimpleNamespace

import numpy as np
import pytest

import sparc_real_analysis as analysis
from emrf.runs import RunStore
from sparc_real_analysis import (
    LAWS,
    Galaxy,
    a0_horizon,
    fit_galaxy,
    g_newton,
    nu_emrf_sqrt,
    nu_rar_exponential,
    nu_simple,
    nu_standard,
    parse_rotmod,
    parse_sparc_table,
    profile_a0,
    solar_system_check,
    v_model,
)

A0 = 1.2e-10


def test_horizon_scale_values():
    assert a0_horizon(67.4) == pytest.approx(1.042e-10, rel=2e-3)
    assert a0_horizon(73.0) == pytest.approx(1.129e-10, rel=2e-3)


@pytest.mark.parametrize("nu", [nu_emrf_sqrt, nu_rar_exponential, nu_simple, nu_standard])
def test_deep_limit_gives_sqrt_a0_gn(nu):
    gn = np.array([1e-15])
    assert gn * nu(gn / A0) == pytest.approx(np.sqrt(A0 * gn), rel=2e-2)


def test_strong_field_offsets():
    gn = np.array([6.46e-5])  # Saturn
    y = gn / A0
    assert float((gn * (nu_emrf_sqrt(y) - 1))[0]) == pytest.approx(A0 / 2, rel=1e-3)
    assert float((gn * (nu_simple(y) - 1))[0]) == pytest.approx(A0, rel=1e-3)
    assert float((gn * (nu_rar_exponential(y) - 1))[0]) < 1e-30
    # standard nu: sqrt(1 + 4/y^2) ~ 1 + 2/y^2  =>  nu ~ 1 + 1/(2 y^2)  =>  delta g = a0^2 / (2 g_N)
    assert float((gn * (nu_standard(y) - 1))[0]) == pytest.approx(A0**2 / (2 * gn[0]), rel=1e-2)


def test_solar_system_verdicts():
    assert not solar_system_check(nu_emrf_sqrt, A0)["passes_generous_bound"]
    assert not solar_system_check(nu_simple, A0)["passes_generous_bound"]
    assert solar_system_check(nu_rar_exponential, A0)["passes_generous_bound"]
    assert solar_system_check(nu_standard, A0)["passes_generous_bound"]


def test_parse_sparc_table_row():
    line = ("    NGC3198  5  13.80  1.40  3 73.0  3.0  38.279   0.212  5.84   178.99  3.14  1602.62  "
            "10.869 35.66 150.1   3.9   1 Da06,Be91,Be87")
    t = parse_sparc_table("Title: header line\n" + line)
    assert t["NGC3198"] == {"T": 5, "D": 13.8, "e_D": 1.4, "f_D": 3, "Inc": 73.0, "e_Inc": 3.0,
                            "L36": 38.279, "MHI": 10.869, "Vflat": 150.1, "Q": 1}


def test_parse_rotmod():
    text = "# Distance = 13.8 Mpc\n# Rad\tVobs\n0.32\t24.40\t35.90\t0.00\t63.28\t0.00\t1084.92\t0.00\n"
    a = parse_rotmod(text)
    assert a.shape == (1, 6)
    assert a[0, 1] == pytest.approx(24.4)


def _toy_galaxy(nu, a0, ups, name, scale):
    """In-memory synthetic galaxy generated from a known law (used only to test the fitter)."""
    r = np.linspace(0.5, 30.0, 30)
    vd = scale * 120.0 * np.sqrt(r / 3.0) * np.exp(-r / 6.0) + 1e-3
    vg = scale * 40.0 * (1 - np.exp(-r / 5.0))
    gal = Galaxy(name, 10.0, 60.0, 1, r, np.ones_like(r), np.full_like(r, 2.0), vg, vd, np.zeros_like(r))
    gal.v_obs = v_model(gal, nu, a0, ups)
    return gal


def test_fit_galaxy_recovers_upsilon():
    gal = _toy_galaxy(nu_rar_exponential, A0, 0.6, "T1", 1.0)
    chi2, _, ups = fit_galaxy(gal, nu_rar_exponential, A0, "free")
    assert ups == pytest.approx(0.6, rel=1e-2)
    assert chi2 < 1e-3


def test_profile_recovers_global_a0():
    gals = [_toy_galaxy(nu_rar_exponential, 1.1e-10, 0.5, f"T{i}", s) for i, s in enumerate((0.5, 1.0, 2.0))]
    prof = profile_a0(gals, nu_rar_exponential, np.linspace(0.8e-10, 1.5e-10, 15), "fixed")
    assert prof["a0_best"] == pytest.approx(1.1e-10, rel=5e-3)


def test_newton_acceleration_units():
    gal = _toy_galaxy(nu_rar_exponential, A0, 0.5, "T", 1.0)
    gn = g_newton(gal, 0.5)
    v2 = gal.v_gas**2 + 0.5 * gal.v_disk**2
    assert gn == pytest.approx(v2 * 1e6 / (gal.r_kpc * 3.085677581e19), rel=1e-6)


def test_law_registry():
    assert set(LAWS) == {"emrf_sqrt", "rar_exponential", "simple", "standard"}
    assert math.isfinite(float(LAWS["emrf_sqrt"][1](np.array([1.0]))[0]))


def test_run_resumes_from_last_completed_law(tmp_path, monkeypatch):
    store = RunStore(tmp_path / "runs")
    record = store.create("sparc-real-analysis", ["--quick", "--no-figures"])
    monkeypatch.setenv("EMRF_RUN_ID", record.run_id)
    monkeypatch.setenv("EMRF_RUN_DIR", str(record.path))
    monkeypatch.setattr(analysis, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(analysis, "RESULTS_DIR", tmp_path / "results")
    monkeypatch.setattr(analysis, "load_sparc", lambda: [SimpleNamespace(n=1)])
    monkeypatch.setattr(analysis, "fit_galaxy", lambda *args: (1.0, 0.0, 0.5))
    monkeypatch.setattr(
        analysis,
        "solar_system_check",
        lambda *args: {"passes_generous_bound": True},
    )

    def first_law(values):
        return values

    def second_law(values):
        return values

    monkeypatch.setattr(
        analysis,
        "LAWS",
        {"first": ("First law", first_law), "second": ("Second law", second_law)},
    )
    calls = {first_law: 0, second_law: 0}
    interrupt_second = True

    def profile(galaxies, law, grid, mode):
        nonlocal interrupt_second
        if law is second_law and mode == "prior" and interrupt_second:
            interrupt_second = False
            raise RuntimeError("injected interruption")
        calls[law] += 1
        return {
            "a0_best": 1.0e-10,
            "chi2_best": 1.0,
            "chi2_reduced": 1.0,
            "n_params": 1,
            "sigma_scaled": 1.0e-12,
            "a0_grid": grid,
            "objective_grid": np.ones_like(grid),
        }

    monkeypatch.setattr(analysis, "profile_a0", profile)
    with pytest.raises(RuntimeError, match="injected interruption"):
        analysis.run(quick=True, make_figures=False)
    first_calls = calls[first_law]

    result = analysis.run(quick=True, make_figures=False)

    assert first_calls == 3
    assert calls[first_law] == first_calls
    assert calls[second_law] == 3
    assert set(result["laws"]) == {"first", "second"}
    assert not list((tmp_path / "results").glob("*.part"))
