"""Unit and regression tests for Solar System Precision & Cassini Screening Stress Test."""

import pytest
import numpy as np
from stress_test_solar_system import (
    SOLAR_SYSTEM_BENCHMARKS,
    A0_NOMINAL,
    acceleration_unscreened_naive,
    acceleration_standard_screened,
    acceleration_emrf_geometric_screened,
    evaluate_solar_system_residuals,
    summarize_solar_system_stress_test,
)


class TestSolarSystemBenchmarks:
    def test_benchmark_catalog_completeness(self):
        """Ensure all 9 major solar system benchmarks are populated."""
        assert len(SOLAR_SYSTEM_BENCHMARKS) == 9
        names = [p.name for p in SOLAR_SYSTEM_BENCHMARKS]
        assert "Mercury" in names
        assert "Saturn (Cassini)" in names
        assert "Voyager 1 (Heliosphere)" in names

    def test_newtonian_acceleration_monotonic_falloff(self):
        """Accelerations must strictly decrease with distance from Sun."""
        accels = [p.newtonian_acceleration for p in SOLAR_SYSTEM_BENCHMARKS]
        for i in range(len(accels) - 1):
            assert accels[i] > accels[i + 1]


class TestScreeningMechanisms:
    def test_unscreened_violates_cassini_and_llr(self):
        """Unscreened naive models must decisively fail Cassini and LLR."""
        saturn = next(p for p in SOLAR_SYSTEM_BENCHMARKS if "Saturn" in p.name)
        a_n = saturn.newtonian_acceleration
        a_unscreened = acceleration_unscreened_naive(a_n, A0_NOMINAL)
        delta_a = abs(a_unscreened - a_n)
        # Should be order of 0.5 * a0 = 6e-11, which dwarfs Cassini's 3.2e-14
        assert delta_a > 1e-11
        assert delta_a > saturn.acceleration_tolerance_ms2 * 1000.0

    def test_standard_screened_passes_all_benchmarks(self):
        """Standard transition function must pass all solar system tolerances."""
        res = evaluate_solar_system_residuals("standard_screened", A0_NOMINAL)
        for name, data in res.items():
            assert data["passes"], f"{name} failed with delta_a={data['delta_a_ms2']:.3e} > {data['tolerance_ms2']:.3e}"

    def test_emrf_geometric_screening_passes_and_freezes_to_gr(self):
        """EMRF geometric compression screening must freeze to GR with zero violation."""
        res = evaluate_solar_system_residuals("emrf_screened", A0_NOMINAL)
        saturn = res["Saturn (Cassini)"]
        assert saturn["passes"]
        assert saturn["delta_a_ms2"] < 1e-15

    def test_summary_stress_test_comparison(self):
        """Full comparative report confirms unscreened is falsified and screened passes."""
        summary = summarize_solar_system_stress_test()
        assert not summary["unscreened_naive"]["all_passed"]
        assert summary["standard_screened"]["all_passed"]
        assert summary["emrf_screened"]["all_passed"]
        assert summary["gr_baseline"]["all_passed"]
