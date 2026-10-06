"""Unit tests for Gaia DR3 Wide Binary Stars & External Field Effect (EFE) Stress Test."""

import pytest
import numpy as np
from stress_test_wide_binaries import (
    GAIA_WIDE_BINARY_BENCHMARKS,
    calculate_isolated_modified_velocity,
    calculate_emrf_efe_velocity,
    evaluate_wide_binary_stress_test,
)


class TestWideBinaryPhysics:
    def test_benchmark_bins_completeness(self):
        """All 4 Gaia DR3 separation bins must be defined."""
        assert len(GAIA_WIDE_BINARY_BENCHMARKS) == 4
        assert GAIA_WIDE_BINARY_BENCHMARKS[0].separation_au == 800.0
        assert GAIA_WIDE_BINARY_BENCHMARKS[-1].separation_au == 20000.0

    def test_newtonian_velocity_decreases_with_separation(self):
        """Keplerian circular velocity v_N = sqrt(GM/r) must decrease monotonically."""
        vels = [b.newtonian_velocity for b in GAIA_WIDE_BINARY_BENCHMARKS]
        for i in range(len(vels) - 1):
            assert vels[i] > vels[i + 1]

    def test_efe_caps_runaway_boost_at_large_separation(self):
        """The External Field Effect must cap velocity boost below isolated modified gravity."""
        ultra_wide_bin = GAIA_WIDE_BINARY_BENCHMARKS[-1]  # 20,000 AU
        v_iso = calculate_isolated_modified_velocity(ultra_wide_bin)
        v_efe = calculate_emrf_efe_velocity(ultra_wide_bin)
        assert v_efe < v_iso
        # EFE boost ratio should be roughly 1.20 - 1.35
        v_ratio_efe = v_efe / ultra_wide_bin.newtonian_velocity
        assert 1.15 < v_ratio_efe < 1.35

    def test_emrf_efe_decisively_preferred_over_newton(self):
        """Bayesian Delta-BIC must decisively favor EMRF+EFE over Newtonian gravity."""
        report = evaluate_wide_binary_stress_test()
        assert report["delta_bic_emrf_vs_newton"] < -10.0
        assert report["total_chi2_emrf_efe"] < report["total_chi2_newton"]
