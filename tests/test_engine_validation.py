"""Tests for the Phase 5 cross-engine completion certificate."""

from __future__ import annotations

import math

import numpy as np
import pytest

from emergent_matter_model.emrf_validation_access import engine_validation_report
from emergent_matter_model.fit_astrometry import (
    S2_BENCHMARK_PARAMS,
    fit_emrf_beta,
    project_orbital_position_to_sky,
)
from emergent_matter_model.fit_jwst import (
    HighZGalaxyRecord,
    critical_acceleration_z,
    fit_high_z_acceleration_scale,
    predict_flat_velocity_kms,
)
from emergent_matter_model.quantum_vibrational_compression import (
    QuantumVibrationalEngine,
)


def test_engine_completion_certificate_passes_with_honest_evidence_types():
    report = engine_validation_report()
    assert report["all_passed"]
    assert report["evidence_class"] == "mixed"
    assert len(report["checks"]) == 11
    assert {check["evidence_class"] for check in report["checks"]} == {
        "software",
        "synthetic",
        "illustrative",
    }
    assert all(check["passed"] for check in report["checks"])


def test_astrometry_coupling_recovers_noiseless_injection():
    epochs = np.linspace(2002.0, 2022.0, 24)
    truth = 0.04
    prediction = project_orbital_position_to_sky(
        S2_BENCHMARK_PARAMS,
        epochs,
        model_type="emrf",
        emrf_beta=truth,
    )
    observation = {
        "epoch": epochs,
        "ra_mas": prediction["ra_mas"],
        "ra_err_mas": np.full(len(epochs), 0.25),
        "dec_mas": prediction["dec_mas"],
        "dec_err_mas": np.full(len(epochs), 0.25),
        "vr_kms": prediction["vr_kms"],
        "vr_err_kms": np.full(len(epochs), 20.0),
    }
    result = fit_emrf_beta(observation, S2_BENCHMARK_PARAMS)
    assert result["best_beta"] == pytest.approx(truth, abs=1e-10)
    assert result["chi2"] < 1e-16
    assert not result["active_bound"]


def test_jwst_acceleration_scale_recovers_noiseless_injection():
    truth = 1.4e-10
    catalog = []
    for index, redshift in enumerate(np.linspace(0.5, 5.0, 20)):
        log_mass = 9.2 + index / 20
        catalog.append(
            HighZGalaxyRecord(
                galaxy_id=f"SYN-{index}",
                redshift_z=float(redshift),
                log_m_bar_solar=log_mass,
                log_m_bar_err=0.08,
                v_rot_kms=predict_flat_velocity_kms(
                    10.0**log_mass,
                    critical_acceleration_z(float(redshift), truth),
                ),
                v_rot_err_kms=8.0,
                r_half_light_kpc=2.0,
                survey="synthetic",
                reference="test",
            )
        )
    result = fit_high_z_acceleration_scale(catalog)
    assert result["best_a0_zero"] == pytest.approx(truth, rel=1e-10)
    assert result["chi2"] < 1e-16
    assert result["mass_uncertainty_propagated"]


def test_quantum_boundaries_and_compton_identity():
    engine = QuantumVibrationalEngine()
    mass = 9.1093837015e-31
    assert (
        engine.compton_frequency(mass) * engine.compton_wavelength(mass)
    ) == pytest.approx(engine.C, rel=2e-15)
    for invalid in (0.0, -1.0, math.inf, math.nan):
        with pytest.raises(ValueError, match="mass_kg"):
            engine.compton_wavelength(invalid)
