"""Cross-engine deterministic verification and synthetic calibration."""

from __future__ import annotations

import math
from dataclasses import replace
from functools import lru_cache
from typing import TypedDict

import numpy as np

try:
    from fit_astrometry import (
        S2_BENCHMARK_PARAMS,
        fit_emrf_beta,
        project_orbital_position_to_sky,
    )
    from fit_jwst import (
        HighZGalaxyRecord,
        critical_acceleration_z,
        fit_high_z_acceleration_scale,
        predict_flat_velocity_kms,
    )
    from lensing_engine import (
        calculate_deflection_angle_profile,
        integrate_softened_isothermal_deflection,
    )
    from model import EmergentMatterModel
    from quantum_vibrational_compression import (
        PARTICLE_BENCHMARKS,
        QuantumVibrationalEngine,
    )
except ImportError:
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
    from emergent_matter_model.lensing_engine import (
        calculate_deflection_angle_profile,
        integrate_softened_isothermal_deflection,
    )
    from emergent_matter_model.model import EmergentMatterModel
    from emergent_matter_model.quantum_vibrational_compression import (
        PARTICLE_BENCHMARKS,
        QuantumVibrationalEngine,
    )


class EngineCheck(TypedDict):
    name: str
    metric: str
    measured: float
    expected: float
    lower_bound: float
    upper_bound: float
    passed: bool
    evidence_class: str
    reference: str
    limitation: str | None


class EngineValidationReport(TypedDict):
    evidence_class: str
    all_passed: bool
    checks: list[EngineCheck]
    limitations: list[str]


def _add_check(
    checks: list[EngineCheck],
    *,
    name: str,
    metric: str,
    measured: float,
    expected: float,
    lower_bound: float,
    upper_bound: float,
    evidence_class: str,
    reference: str,
    limitation: str | None = None,
) -> None:
    finite = all(
        math.isfinite(value)
        for value in (measured, expected, lower_bound, upper_bound)
    )
    checks.append(
        {
            "name": name,
            "metric": metric,
            "measured": float(measured),
            "expected": float(expected),
            "lower_bound": float(lower_bound),
            "upper_bound": float(upper_bound),
            "passed": bool(finite and lower_bound <= measured <= upper_bound),
            "evidence_class": evidence_class,
            "reference": reference,
            "limitation": limitation,
        }
    )


def _distributed_lens_checks(checks: list[EngineCheck]) -> None:
    impact = 5.0
    velocity = 220.0
    core = 1.2
    exact = float(
        calculate_deflection_angle_profile(
            np.array([impact]),
            v_circ_kms=velocity,
            r_core_kpc=core,
        )[0]
    )
    errors = [
        abs(
            integrate_softened_isothermal_deflection(
                impact,
                v_circ_kms=velocity,
                r_core_kpc=core,
                intervals=intervals,
            )
            - exact
        )
        for intervals in (128, 256, 512)
    ]
    order = min(math.log2(errors[index] / errors[index + 1]) for index in range(2))
    measured = integrate_softened_isothermal_deflection(
        impact,
        v_circ_kms=velocity,
        r_core_kpc=core,
        intervals=2048,
    )
    relative_error = abs(measured - exact) / exact
    _add_check(
        checks,
        name="distributed softened-isothermal lens profile",
        metric="relative error against analytical projected-mass profile",
        measured=relative_error,
        expected=0.0,
        lower_bound=0.0,
        upper_bound=2e-7,
        evidence_class="software",
        reference="Independent numerical projected-mass integral",
    )
    _add_check(
        checks,
        name="distributed lens integration convergence",
        metric="minimum measured refinement order",
        measured=order,
        expected=2.0,
        lower_bound=1.99,
        upper_bound=2.01,
        evidence_class="software",
        reference="Composite trapezoidal integration under step halving",
    )


def _astrometry_checks(checks: list[EngineCheck]) -> None:
    realizations = 32
    truth = 0.03
    epochs = np.linspace(2002.0, 2022.0, 32)
    prediction = project_orbital_position_to_sky(
        S2_BENCHMARK_PARAMS,
        epochs,
        model_type="emrf",
        emrf_beta=truth,
    )
    errors = {
        "ra_err_mas": np.full(len(epochs), 0.25),
        "dec_err_mas": np.full(len(epochs), 0.25),
        "vr_err_kms": np.full(len(epochs), 20.0),
    }
    estimates = np.empty(realizations)
    standard_errors = np.empty(realizations)
    reduced_chi2 = np.empty(realizations)
    for seed in range(realizations):
        generator = np.random.default_rng(seed)
        observation = {
            "epoch": epochs,
            **errors,
            "ra_mas": prediction["ra_mas"]
            + generator.normal(0.0, errors["ra_err_mas"]),
            "dec_mas": prediction["dec_mas"]
            + generator.normal(0.0, errors["dec_err_mas"]),
            "vr_kms": prediction["vr_kms"]
            + generator.normal(0.0, errors["vr_err_kms"]),
        }
        result = fit_emrf_beta(observation, S2_BENCHMARK_PARAMS)
        estimates[seed] = result["best_beta"]
        standard_errors[seed] = result["beta_standard_error"]
        reduced_chi2[seed] = result["reduced_chi2"]
    standardized_bias = abs(float(estimates.mean()) - truth) / estimates.std(ddof=1)
    coverage = float(np.mean(np.abs(estimates - truth) <= standard_errors))
    _add_check(
        checks,
        name="astrometry coupling recovery bias",
        metric="absolute ensemble bias / empirical standard deviation",
        measured=standardized_bias,
        expected=0.0,
        lower_bound=0.0,
        upper_bound=0.4,
        evidence_class="synthetic",
        reference="32 deterministic S2-like astrometry and spectroscopy injections",
        limitation="Fixed orbital elements; this is not a real Galactic-centre measurement.",
    )
    _add_check(
        checks,
        name="astrometry coupling interval coverage",
        metric="fraction of local 68.27% intervals containing injected truth",
        measured=coverage,
        expected=0.682689492,
        lower_bound=0.45,
        upper_bound=0.85,
        evidence_class="synthetic",
        reference="Finite-ensemble calibration of the production coupling fitter",
        limitation="Fixed orbital elements under independent Gaussian errors.",
    )
    _add_check(
        checks,
        name="astrometry posterior predictive residual scale",
        metric="mean reduced chi-square",
        measured=float(reduced_chi2.mean()),
        expected=1.0,
        lower_bound=0.8,
        upper_bound=1.2,
        evidence_class="synthetic",
        reference="Known injected astrometric and radial-velocity uncertainties",
        limitation="Instrument correlations and orbital-element uncertainty are not injected.",
    )


def _jwst_design() -> list[HighZGalaxyRecord]:
    catalog = []
    for index, redshift in enumerate(np.linspace(0.5, 6.0, 40)):
        log_mass = 9.2 + 1.2 * index / 39
        catalog.append(
            HighZGalaxyRecord(
                galaxy_id=f"SYNTHETIC-{index}",
                redshift_z=float(redshift),
                log_m_bar_solar=float(log_mass),
                log_m_bar_err=0.08,
                v_rot_kms=predict_flat_velocity_kms(
                    10.0**log_mass,
                    critical_acceleration_z(float(redshift), 1.4e-10),
                ),
                v_rot_err_kms=8.0,
                r_half_light_kpc=2.0,
                survey="synthetic",
                reference="deterministic injection",
            )
        )
    return catalog


def _jwst_checks(checks: list[EngineCheck]) -> None:
    realizations = 64
    truth = 1.4e-10
    design = _jwst_design()
    estimates = np.empty(realizations)
    standard_errors = np.empty(realizations)
    reduced_chi2 = np.empty(realizations)
    for seed in range(realizations):
        generator = np.random.default_rng(seed)
        injected = []
        for galaxy in design:
            measured_mass = galaxy.log_m_bar_solar + generator.normal(
                0.0,
                galaxy.log_m_bar_err,
            )
            measured_velocity = galaxy.v_rot_kms + generator.normal(
                0.0,
                galaxy.v_rot_err_kms,
            )
            injected.append(
                replace(
                    galaxy,
                    log_m_bar_solar=measured_mass,
                    v_rot_kms=measured_velocity,
                )
            )
        result = fit_high_z_acceleration_scale(injected)
        estimates[seed] = result["best_a0_zero"]
        standard_errors[seed] = result["a0_standard_error"]
        reduced_chi2[seed] = result["reduced_chi2"]
    standardized_bias = abs(float(estimates.mean()) - truth) / estimates.std(ddof=1)
    coverage = float(np.mean(np.abs(estimates - truth) <= standard_errors))
    _add_check(
        checks,
        name="JWST-like acceleration-scale recovery bias",
        metric="absolute ensemble bias / empirical standard deviation",
        measured=standardized_bias,
        expected=0.0,
        lower_bound=0.0,
        upper_bound=0.35,
        evidence_class="synthetic",
        reference="64 deterministic high-redshift mass and velocity injections",
        limitation="Synthetic catalogue; no real JWST or ALMA inference is claimed.",
    )
    _add_check(
        checks,
        name="JWST-like acceleration-scale interval coverage",
        metric="fraction of local 68.27% intervals containing injected truth",
        measured=coverage,
        expected=0.682689492,
        lower_bound=0.5,
        upper_bound=0.85,
        evidence_class="synthetic",
        reference="Production fitter with propagated baryonic-mass uncertainty",
        limitation="Selection effects and correlated galaxy systematics are not represented.",
    )
    _add_check(
        checks,
        name="JWST-like posterior predictive residual scale",
        metric="mean reduced chi-square",
        measured=float(reduced_chi2.mean()),
        expected=1.0,
        lower_bound=0.75,
        upper_bound=1.15,
        evidence_class="synthetic",
        reference="Known injected velocity and log-mass uncertainties",
        limitation="The synthetic Gaussian design is not observational evidence.",
    )


def _quantum_and_core_checks(checks: list[EngineCheck]) -> None:
    engine = QuantumVibrationalEngine()
    identity_errors = [
        abs(
            engine.compton_frequency(particle.rest_mass_kg)
            * engine.compton_wavelength(particle.rest_mass_kg)
            / engine.C
            - 1.0
        )
        for particle in PARTICLE_BENCHMARKS
    ]
    benchmark_errors = [
        abs(
            2.0
            * math.pi
            * engine.compton_wavelength(particle.rest_mass_kg)
            / particle.compton_wavelength_m
            - 1.0
        )
        for particle in PARTICLE_BENCHMARKS
    ]
    _add_check(
        checks,
        name="quantum Compton frequency-wavelength identity",
        metric="maximum relative identity error",
        measured=max(identity_errors),
        expected=0.0,
        lower_bound=0.0,
        upper_bound=3e-15,
        evidence_class="software",
        reference="Independent identity omega_C times reduced lambda_C = c",
        limitation="Does not validate the proposed nonlinear soliton dynamics.",
    )
    _add_check(
        checks,
        name="quantum particle Compton benchmarks",
        metric="maximum relative error of unreduced benchmark wavelength",
        measured=max(benchmark_errors),
        expected=0.0,
        lower_bound=0.0,
        upper_bound=2e-3,
        evidence_class="illustrative",
        reference="Electron, proton and Higgs benchmark masses and h/(mc)",
        limitation="The particle table is a benchmark, not evidence for matter emergence.",
    )

    coordinates = [0.2, 0.7, 1.1]
    functions = [lambda value: value**2, lambda value: 2.0 * value, math.exp]
    first = EmergentMatterModel(3, [2.0, 3.0, 5.0]).matter(coordinates, functions)
    scaled = EmergentMatterModel(3, [20.0, 30.0, 50.0]).matter(
        coordinates,
        functions,
    )
    relative_error = abs(first - scaled) / abs(first)
    _add_check(
        checks,
        name="core model weight-scale invariance",
        metric="relative output change under common weight scaling",
        measured=relative_error,
        expected=0.0,
        lower_bound=0.0,
        upper_bound=2e-15,
        evidence_class="software",
        reference="Normalized weighted-curvature definition",
        limitation="Phenomenological invariant; no physical conservation law is implied.",
    )


@lru_cache(maxsize=1)
def engine_validation_report() -> EngineValidationReport:
    """Return deterministic verification for remaining Phase 5 engine families."""
    checks: list[EngineCheck] = []
    _distributed_lens_checks(checks)
    _astrometry_checks(checks)
    _jwst_checks(checks)
    _quantum_and_core_checks(checks)
    return {
        "evidence_class": "mixed",
        "all_passed": all(check["passed"] for check in checks),
        "checks": checks,
        "limitations": [
            "Software and synthetic checks do not constitute observational confirmation.",
            "The CMB and quantum templates remain illustrative rather than derived predictions.",
        ],
    }


__all__ = ["EngineCheck", "EngineValidationReport", "engine_validation_report"]
