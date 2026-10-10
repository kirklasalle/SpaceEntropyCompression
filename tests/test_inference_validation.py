"""Tests for deterministic inference injection-recovery certification."""

from __future__ import annotations

import pytest

from emergent_matter_model.emrf_validation_access import inference_validation_report
from emergent_matter_model.fit_sparc import A0_CRITICAL


@pytest.fixture(scope="module")
def report():
    return inference_validation_report()


def test_inference_certificate_passes_declared_synthetic_checks(report):
    assert report["all_passed"]
    assert report["evidence_class"] == "synthetic"
    assert report["realizations"] == 64
    assert report["random_seed"] == 20261010
    assert len(report["checks"]) == 14
    assert all(check["evidence_class"] == "synthetic" for check in report["checks"])
    assert all(check["passed"] for check in report["checks"])
    assert report["truths"]["sparc_a_entropy_m_per_s2"] == pytest.approx(
        1.5 * A0_CRITICAL
    )


def test_inference_certificate_calibrates_bias_coverage_and_residuals(report):
    checks = {check["name"]: check for check in report["checks"]}
    assert checks["SPARC disk mass-to-light ratio interval coverage"][
        "measured"
    ] == pytest.approx(0.640625)
    assert checks["SPARC entropy acceleration interval coverage"][
        "measured"
    ] == pytest.approx(0.765625)
    assert checks["Pantheon delta-chi-square interval coverage"][
        "measured"
    ] == pytest.approx(0.703125)
    assert checks["SPARC repeated-start agreement"]["measured"] < 1e-7
    assert 0.8 < checks["SPARC posterior predictive residual scale"]["measured"] < 1.2
    assert 0.8 < checks["Pantheon posterior predictive residual scale"]["measured"] < 1.2


def test_inference_certificate_states_observational_limitations(report):
    limitations = " ".join(report["limitations"]).lower()
    assert "synthetic" in limitations
    assert "does not constitute observational evidence" in limitations
    assert "larger real-survey systematics" in limitations
