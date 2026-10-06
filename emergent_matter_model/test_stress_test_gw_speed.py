"""Unit tests for GW170817 & Multi-Messenger Gravitational Wave Speed Stress Test."""

import pytest
from stress_test_gw_speed import (
    GW_BENCHMARKS,
    C_LIGHT,
    GW_SPEED_LOWER_BOUND,
    GW_SPEED_UPPER_BOUND,
    calculate_wave_propagation_speed,
    compute_arrival_time_delay,
    evaluate_gw_speed_stress_test,
)


class TestGWSpeedBenchmarks:
    def test_gw170817_benchmark_present(self):
        """Ensure GW170817 benchmark is defined with correct bounds."""
        assert len(GW_BENCHMARKS) >= 1
        gw170817 = next(b for b in GW_BENCHMARKS if "GW170817" in b.event_name)
        assert gw170817.distance_mpc == 40.0
        assert gw170817.allowed_delta_c_min == -3.0e-15
        assert gw170817.allowed_delta_c_max == +7.0e-16

    def test_emrf_and_gr_have_identical_speed_of_light(self):
        """EMRF tensor perturbation speed must equal c identically."""
        c_gr = calculate_wave_propagation_speed("gr_baseline")
        c_emrf = calculate_wave_propagation_speed("emrf_standard")
        assert c_gr == C_LIGHT
        assert c_emrf == C_LIGHT

    def test_disformal_and_horndeski_fail_gw_speed(self):
        """Disformal and Horndeski models must fail the GW170817 speed constraint."""
        c_horn = calculate_wave_propagation_speed("horndeski_modified")
        c_teves = calculate_wave_propagation_speed("teves_disformal")
        delta_horn = (c_horn - C_LIGHT) / C_LIGHT
        delta_teves = (c_teves - C_LIGHT) / C_LIGHT

        assert not (GW_SPEED_LOWER_BOUND <= delta_horn <= GW_SPEED_UPPER_BOUND)
        assert not (GW_SPEED_LOWER_BOUND <= delta_teves <= GW_SPEED_UPPER_BOUND)

    def test_full_comparative_gw_report(self):
        """Comparative evaluation must pass EMRF/GR and falsify modified disformal models."""
        report = evaluate_gw_speed_stress_test()
        assert report["gr_baseline"]["passes_gw170817"]
        assert report["emrf_standard"]["passes_gw170817"]
        assert not report["horndeski_modified"]["passes_gw170817"]
        assert not report["teves_disformal"]["passes_gw170817"]
        assert report["emrf_standard"]["fractional_delta_c"] == 0.0
