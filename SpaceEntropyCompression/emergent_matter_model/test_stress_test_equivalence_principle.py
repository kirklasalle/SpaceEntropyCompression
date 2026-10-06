"""
Unit test suite for Equivalence Principle and MICROSCOPE stress tests.
"""

import pytest
from stress_test_equivalence_principle import (
    EP_BENCHMARKS,
    compute_eotvos_parameter,
    evaluate_all_ep_benchmarks,
    generate_ep_stress_test_report,
)


class TestEquivalencePrincipleBenchmarks:
    def test_benchmarks_catalog_complete(self):
        assert len(EP_BENCHMARKS) == 3
        names = [b.name for b in EP_BENCHMARKS]
        assert "MICROSCOPE Satellite" in names
        assert "Lunar Laser Ranging (LLR)" in names
        assert "Eöt-Wash Torsion Balance" in names

    def test_emrf_and_gr_obey_wep_identically(self):
        eta_gr = compute_eotvos_parameter("gr")
        eta_emrf = compute_eotvos_parameter("emrf")

        assert eta_gr == 0.0
        assert eta_emrf == 0.0

    def test_unscreened_scalar_tensor_fails_microscope(self):
        eta_unscreened = compute_eotvos_parameter("scalar_tensor_unscreened")
        microscope_limit = 1.0e-15

        # Unscreened scalar tensor violates MICROSCOPE by ~10^10
        assert eta_unscreened > microscope_limit * 1.0e8

    def test_all_benchmarks_evaluation_status(self):
        results = evaluate_all_ep_benchmarks()

        # EMRF and GR must pass all 3 benchmarks
        for bm_name in results:
            assert results[bm_name]["gr"]["passes"] is True
            assert results[bm_name]["emrf"]["passes"] is True
            assert results[bm_name]["scalar_tensor_unscreened"]["passes"] is False

    def test_ep_report_generation(self):
        report = generate_ep_stress_test_report()
        assert "MICROSCOPE Satellite" in report
        assert "EMRF (Space Entropy Compression)" in report
        assert "PASSED (Identical)" in report
        assert "Universal Conformal Metric" in report
