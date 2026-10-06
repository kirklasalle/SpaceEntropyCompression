"""Unit and integration tests for astrometry projection, fitting, and Bayesian model evaluation."""

from __future__ import annotations

import math
from pathlib import Path
import pytest
import numpy as np

from fit_astrometry import (
    SgrAOrbitalParameters,
    S2_BENCHMARK_PARAMS,
    S301_BENCHMARK_PARAMS,
    solve_kepler_anomaly,
    compute_true_anomaly,
    project_orbital_position_to_sky,
    load_astrometry_csv,
    compute_residuals_and_chi2,
    compute_information_criteria,
    evaluate_astrometry_bifurcation,
    evaluate_multi_star_bifurcation
)


class TestKeplerAndTrueAnomaly:
    """Tests for Kepler's equation solver and true anomaly calculation."""

    def test_zero_mean_anomaly(self):
        e = 0.5
        ecc_anom = solve_kepler_anomaly(0.0, e)
        assert abs(ecc_anom) < 1e-12

    def test_pi_mean_anomaly(self):
        e = 0.88466
        ecc_anom = solve_kepler_anomaly(math.pi, e)
        assert abs(ecc_anom - math.pi) < 1e-10

    def test_array_convergence(self):
        m_arr = np.linspace(0.0, 2.0 * math.pi, 50)
        e = 0.95
        e_arr = solve_kepler_anomaly(m_arr, e)
        # Verify residual M = E - e*sin(E)
        residuals = np.abs(e_arr - e * np.sin(e_arr) - m_arr)
        assert np.max(residuals) < 1e-10

    def test_true_anomaly_boundary_conditions(self):
        # At pericenter E=0 -> nu=0
        nu_peri = compute_true_anomaly(0.0, 0.5)
        assert abs(nu_peri) < 1e-12

        # At apoapsis E=pi -> nu=pi
        nu_apo = compute_true_anomaly(math.pi, 0.5)
        assert abs(nu_apo - math.pi) < 1e-10


class TestSkyPlaneProjection:
    """Tests for 3D orbital dynamics projection onto the sky plane."""

    def test_distance_inverse_scaling(self):
        epochs = np.array([2018.379])
        p1 = S2_BENCHMARK_PARAMS
        p2 = SgrAOrbitalParameters(
            name="S2_Far",
            mass_bh=p1.mass_bh,
            distance_pc=p1.distance_pc * 2.0,  # Twice as far
            semi_major_axis_au=p1.semi_major_axis_au,
            eccentricity=p1.eccentricity,
            period_yr=p1.period_yr,
            inclination_deg=p1.inclination_deg,
            omega_node_deg=p1.omega_node_deg,
            arg_peri_deg=p1.arg_peri_deg,
            t_peri_epoch=p1.t_peri_epoch
        )

        res1 = project_orbital_position_to_sky(p1, epochs, model_type="newtonian")
        res2 = project_orbital_position_to_sky(p2, epochs, model_type="newtonian")

        # Angular offset must be halved when distance is doubled
        sep1 = math.hypot(res1["ra_mas"][0], res1["dec_mas"][0])
        sep2 = math.hypot(res2["ra_mas"][0], res2["dec_mas"][0])
        assert abs(sep1 / sep2 - 2.0) < 1e-5

    def test_relativistic_redshift_positivity(self):
        epochs = np.array([2018.379])  # Pericenter
        res_newton = project_orbital_position_to_sky(S2_BENCHMARK_PARAMS, epochs, model_type="newtonian")
        res_gr = project_orbital_position_to_sky(S2_BENCHMARK_PARAMS, epochs, model_type="gr_1pn")

        # Relativistic Doppler + gravitational redshift increases perceived radial velocity (positive shift)
        delta_vr = res_gr["vr_kms"][0] - res_newton["vr_kms"][0]
        assert delta_vr > 0.0
        # At pericenter of S2, Delta v_rel ~ 200 km/s
        assert 100.0 < delta_vr < 300.0


class TestAstrometryCSVDataset:
    """Tests for empirical astrometry dataset loading and validation."""

    def test_load_s2_csv(self):
        base_dir = Path(__file__).resolve().parent.parent
        csv_path = base_dir / "data" / "astrometry" / "s2_gravity_vlti.csv"
        data = load_astrometry_csv(csv_path)

        assert len(data["epoch"]) == 21
        assert "epoch" in data and "ra_mas" in data and "dec_mas" in data and "vr_kms" in data
        assert np.all(data["ra_err_mas"] > 0)
        assert np.all(data["dec_err_mas"] > 0)
        assert np.all(data["vr_err_kms"] > 0)

    def test_load_s301_csv(self):
        base_dir = Path(__file__).resolve().parent.parent
        csv_path = base_dir / "data" / "astrometry" / "s301_nature_2026.csv"
        data = load_astrometry_csv(csv_path)

        assert len(data["epoch"]) == 15
        assert np.max(data["vr_kms"]) > 20000.0  # Ultra-fast star reaches ~24,000 km/s

    def test_missing_csv_raises_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_astrometry_csv("non_existent_dataset.csv")


class TestBayesianModelEvaluation:
    """Tests for residual calculation, BIC, and Bifurcation protocol."""

    def test_zero_residuals_perfect_fit(self):
        dummy_obs = {
            "epoch": np.array([2020.0, 2021.0]),
            "ra_mas": np.array([10.0, 15.0]),
            "ra_err_mas": np.array([0.1, 0.1]),
            "dec_mas": np.array([-20.0, -25.0]),
            "dec_err_mas": np.array([0.1, 0.1]),
            "vr_kms": np.array([500.0, 600.0]),
            "vr_err_kms": np.array([5.0, 5.0])
        }
        total_chi2, _, n_pts, _ = compute_residuals_and_chi2(dummy_obs, dummy_obs)
        assert total_chi2 == 0.0
        assert n_pts == 6

        ln_l, aic, bic = compute_information_criteria(total_chi2, n_pts, n_free_params=4)
        assert ln_l == 0.0
        assert aic == 8.0
        assert bic == 4.0 * math.log(6)

    def test_s2_bifurcation_evaluation(self):
        base_dir = Path(__file__).resolve().parent.parent
        csv_path = base_dir / "data" / "astrometry" / "s2_gravity_vlti.csv"
        report = evaluate_astrometry_bifurcation(csv_path, S2_BENCHMARK_PARAMS, candidate_emrf_beta=0.005)

        assert report["target_star"] == "S2"
        assert "delta_bic" in report["model_selection"]
        assert report["model_selection"]["bifurcation_decision"] in (
            "Branch A: Geometric Collapse",
            "Branch B: Novel Extension",
            "Inconclusive / Indistinguishable"
        )

    def test_load_all_secondary_s_stars(self):
        base_dir = Path(__file__).resolve().parent.parent
        data_dir = base_dir / "data" / "astrometry"

        data_s29 = load_astrometry_csv(data_dir / "s29_gravity_vlti.csv")
        data_s38 = load_astrometry_csv(data_dir / "s38_gravity_vlti.csv")
        data_s55 = load_astrometry_csv(data_dir / "s55_gravity_vlti.csv")

        assert len(data_s29["epoch"]) == 12
        assert len(data_s38["epoch"]) == 9
        assert len(data_s55["epoch"]) == 10
        assert np.all(data_s29["vr_err_kms"] > 0)
        assert np.all(data_s38["vr_err_kms"] > 0)
        assert np.all(data_s55["vr_err_kms"] > 0)

    def test_multi_star_joint_bifurcation_evaluation(self):
        base_dir = Path(__file__).resolve().parent.parent
        report = evaluate_multi_star_bifurcation(
            star_names=["s2", "s29", "s38", "s55", "s301"],
            data_dir=base_dir / "data" / "astrometry",
            candidate_emrf_beta=0.005
        )

        assert report["n_stars"] == 5
        assert report["total_data_points"] == 201
        assert "S2" in report["per_star_reports"]
        assert "S301" in report["per_star_reports"]
        assert report["model_selection"]["bifurcation_decision"] == "Branch A: Geometric Collapse"
        assert report["model_selection"]["delta_bic"] > 10.0

    def test_unknown_star_raises_key_error(self):
        with pytest.raises(KeyError):
            evaluate_multi_star_bifurcation(star_names=["unknown_star_x"])

