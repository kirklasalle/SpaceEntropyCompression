import pytest
import numpy as np

try:
    from emergent_matter_model.cosmology_expansion import (
        EMRFCosmologyParams,
        E_z,
        H_z,
        luminosity_distance_Mpc,
        distance_modulus,
        bao_observables,
        evaluate_pantheon_plus,
        evaluate_desi_bao,
        fit_joint_cosmology,
    )
    from emergent_matter_model.stress_test_cosmology_expansion import (
        run_cosmology_expansion_stress_test,
    )
except ImportError:
    from cosmology_expansion import (
        EMRFCosmologyParams,
        E_z,
        H_z,
        luminosity_distance_Mpc,
        distance_modulus,
        bao_observables,
        evaluate_pantheon_plus,
        evaluate_desi_bao,
        fit_joint_cosmology,
    )
    from stress_test_cosmology_expansion import (
        run_cosmology_expansion_stress_test,
    )


def test_cosmology_params_consistency():
    """Verify cosmological density parameters sum to unity."""
    p = EMRFCosmologyParams()
    total_omega = p.Omega_r + p.Omega_b + p.Omega_C_matter + p.Omega_C_void
    assert np.isclose(total_omega, 1.0, atol=1e-5)
    assert p.Omega_m > p.Omega_b
    assert p.H0 > 0.0


def test_expansion_rate_and_hubble():
    """Verify E(z) is monotonic and H(0) equals H0."""
    p = EMRFCosmologyParams(H0=70.0)
    assert np.isclose(E_z(0.0, p), 1.0, atol=1e-3)
    assert np.isclose(H_z(0.0, p), 70.0, atol=1e-2)

    z_grid = np.linspace(0.0, 3.0, 50)
    E_grid = E_z(z_grid, p)
    assert np.all(np.diff(E_grid) > 0.0)  # Monotonic expansion rate


def test_distance_modulus_monotonicity():
    """Verify luminosity distance and distance modulus increase with redshift."""
    p = EMRFCosmologyParams()
    z_vals = [0.01, 0.05, 0.1, 0.5, 1.0, 1.5, 2.0]
    mu_vals = [distance_modulus(z, p) for z in z_vals]
    assert all(mu_vals[i] < mu_vals[i+1] for i in range(len(mu_vals)-1))


def test_bao_observables_scaling():
    """Verify BAO distance metrics are positive and physically scaled."""
    p = EMRFCosmologyParams()
    bao = bao_observables(0.51, p)
    assert bao["DM_over_rd"] > 10.0
    assert bao["DH_over_rd"] > 15.0
    assert bao["DV_over_rd"] > 10.0


def test_pantheon_plus_evaluation():
    """Verify Pantheon+ evaluation returns reasonable reduced chi2."""
    p = EMRFCosmologyParams()
    res = evaluate_pantheon_plus(p, "data/synthetic/cosmology/sn_hubble_diagram_synthetic.csv")
    assert res["n_points"] == 32
    assert res["chi2_reduced"] < 2.0
    assert res["rms_residual_mag"] < 0.20


def test_desi_bao_evaluation():
    """Verify DESI 2024 BAO evaluation returns reasonable reduced chi2."""
    p = EMRFCosmologyParams()
    res = evaluate_desi_bao(p, "data/cosmology/desi_2024_bao.csv")
    assert res["n_points"] == 12  # official DESI DR1 Table 1 rows
    assert res["chi2_reduced"] < 3.50  # Must be competitive with LCDM


def test_full_cosmology_expansion_stress_test():
    """Verify full stress-test harness passes all benchmarks."""
    report = run_cosmology_expansion_stress_test()
    assert report["status"] == "PASSED"
    assert report["is_monotonic"] is True
    assert report["joint_stats"]["pantheon_chi2_red"] < 1.00
    assert report["joint_stats"]["desi_chi2_red"] < 2.00
    assert report["joint_stats"]["chi2_reduced"] < 1.00
