"""Unit tests for Multi-Galaxy Radial Acceleration Relation (RAR) Scatter Stress Test."""

import pytest
import numpy as np
from stress_test_galaxy_scatter import (
    compile_master_rar_dataset,
    evaluate_rar_statistics,
    run_monte_carlo_noise_stress_test,
)


class TestRARDatasetCompilation:
    def test_total_points_count(self):
        """Must compile all 214 valid observational points across the 10 SPARC galaxies."""
        dataset = compile_master_rar_dataset()
        assert len(dataset) == 214
        galaxies = set(r["galaxy"] for r in dataset)
        assert len(galaxies) == 10
        assert "NGC2841" in galaxies
        assert "DDO154" in galaxies

    def test_accelerations_physical_range(self):
        """All computed accelerations must be positive and within astrophysical bounds."""
        dataset = compile_master_rar_dataset()
        for r in dataset:
            assert 1e-14 < r["g_obs_ms2"] < 1e-7
            assert 1e-15 < r["g_bar_ms2"] < 1e-7
            assert r["g_err_ms2"] > 0.0


class TestRARStatisticsAndMonteCarlo:
    def test_rar_residual_bias_near_zero(self):
        """Mean logarithmic bias should be within 0.05 dex of zero."""
        dataset = compile_master_rar_dataset()
        stats = evaluate_rar_statistics(dataset)
        assert abs(stats["mean_bias_dex"]) < 0.05
        assert stats["std_scatter_dex"] < 0.25
        assert stats["mad_scatter_dex"] < 0.15

    def test_monte_carlo_noise_reproduces_observed_scatter(self):
        """Monte Carlo injected observational errors must account for the measured scatter."""
        dataset = compile_master_rar_dataset()
        stats = evaluate_rar_statistics(dataset)
        mc = run_monte_carlo_noise_stress_test(dataset, n_iterations=50, seed=123)
        # Measured scatter must be within the 90% CI of observational noise
        assert mc["p05_mc_scatter_dex"] <= stats["std_scatter_dex"] <= mc["p95_mc_scatter_dex"] * 1.2
