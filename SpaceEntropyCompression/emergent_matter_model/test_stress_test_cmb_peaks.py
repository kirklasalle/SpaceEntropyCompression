"""Unit and integration tests for EMRF Early-Universe CMB 3rd Acoustic Peak Engine."""

import pytest
import numpy as np

try:
    from emergent_matter_model.cmb_acoustic_engine import (
        EMRFCMBParams,
        sound_speed_c,
        sound_horizon_Mpc,
        comoving_distance_to_recombination_Mpc,
        acoustic_angular_scale,
        compute_acoustic_peaks,
        compute_full_cmb_power_spectrum,
        evaluate_planck_cmb_peaks,
    )
    from emergent_matter_model.stress_test_cmb_peaks import (
        run_cmb_peaks_stress_test,
    )
except ImportError:
    from cmb_acoustic_engine import (
        EMRFCMBParams,
        sound_speed_c,
        sound_horizon_Mpc,
        comoving_distance_to_recombination_Mpc,
        acoustic_angular_scale,
        compute_acoustic_peaks,
        compute_full_cmb_power_spectrum,
        evaluate_planck_cmb_peaks,
    )
    from stress_test_cmb_peaks import (
        run_cmb_peaks_stress_test,
    )


def test_cmb_params_initialization():
    """Verify high-redshift CMB cosmological parameters."""
    p = EMRFCMBParams()
    assert p.H0 == 67.4
    assert np.isclose(p.Omega_m, 0.315, atol=1e-3)
    assert p.z_star > 1000.0


def test_sound_speed_plasma():
    """Verify plasma sound speed at recombination is subluminal and physical."""
    p = EMRFCMBParams()
    cs_star = sound_speed_c(p.z_star, p)
    # Sound speed must be close to 1/sqrt(3) ~ 0.577, reduced by baryon inertia to ~0.45-0.55
    assert 0.40 < cs_star < 0.58


def test_acoustic_scales_planck_agreement():
    """Verify sound horizon s_* and acoustic scale theta_* match Planck 2018."""
    p = EMRFCMBParams()
    s_star = sound_horizon_Mpc(p)
    theta_star, l_star = acoustic_angular_scale(p)
    # Planck 2018: s_* ~ 144.4 Mpc, 100 theta_* ~ 1.0411, l_* ~ 301.7
    assert 140.0 < s_star < 148.0
    assert 0.0102 < theta_star < 0.0106
    assert 298.0 < l_star < 305.0


def test_acoustic_peaks_multipole_locations():
    """Verify peak multipoles (l1, l2, l3) align with Planck 2018."""
    p = EMRFCMBParams()
    peaks = compute_acoustic_peaks(p)
    assert abs(peaks["l_1"] - 220.6) < 3.0
    assert abs(peaks["l_2"] - 537.5) < 3.0
    assert abs(peaks["l_3"] - 810.8) < 3.0


def test_third_acoustic_peak_sustained():
    """Crucial physical test: 3rd peak must NOT crash (A3 / A2 ~ 0.95 - 1.05)."""
    p = EMRFCMBParams()
    peaks = compute_acoustic_peaks(p)
    ratio = peaks["ratio_A3_over_A2"]
    assert 0.95 <= ratio <= 1.02
    assert peaks["A_3"] > 2400.0  # Must exceed decaying baryon-only threshold


def test_continuous_spectrum_generation():
    """Verify continuous power spectrum generation and Silk damping tail."""
    p = EMRFCMBParams()
    l_grid, Dl_grid = compute_full_cmb_power_spectrum(p, l_min=30, l_max=1500, n_points=100)
    assert len(l_grid) == 100
    assert np.all(Dl_grid >= 0.0)
    # Silk damping at l > 1200 must suppress spectrum significantly below peak 1
    idx_tail = np.where(l_grid >= 1300)[0][0]
    assert Dl_grid[idx_tail] < 1100.0


def test_full_cmb_peaks_stress_test():
    """Verify end-to-end Planck 2018 benchmark passes."""
    res = run_cmb_peaks_stress_test("data/cosmology")
    assert res["status"] == "PASSED"
    assert res["overall_pass"] is True
    assert res["chi2_reduced"] < 1.0
