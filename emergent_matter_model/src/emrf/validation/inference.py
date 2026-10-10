"""Deterministic injection-recovery and interval-calibration checks."""

from __future__ import annotations

import math
from dataclasses import replace
from functools import lru_cache
from typing import TypedDict

import numpy as np

try:
    from fit_sparc import (
        A0_CRITICAL,
        SPARCDataPoint,
        compute_baryonic_velocity,
        compute_emrf_entropic_velocity,
        fit_sparc_points,
    )
    from pantheon_inference import dimensionless_magnitudes, fit_baseline
except ImportError:
    from emergent_matter_model.fit_sparc import (
        A0_CRITICAL,
        SPARCDataPoint,
        compute_baryonic_velocity,
        compute_emrf_entropic_velocity,
        fit_sparc_points,
    )
    from emergent_matter_model.pantheon_inference import (
        dimensionless_magnitudes,
        fit_baseline,
    )


class InferenceCheck(TypedDict):
    name: str
    metric: str
    measured: float
    expected: float
    lower_bound: float
    upper_bound: float
    passed: bool
    reference: str
    evidence_class: str
    limitation: str


class InferenceValidationReport(TypedDict):
    evidence_class: str
    all_passed: bool
    realizations: int
    random_seed: int
    checks: list[InferenceCheck]
    truths: dict[str, float]
    limitations: list[str]


_DEFAULT_REALIZATIONS = 64
_DEFAULT_SEED = 20261010
_NOMINAL_ONE_SIGMA_COVERAGE = 0.682689492


def _sparc_design() -> tuple[list[SPARCDataPoint], float, float]:
    radii = np.geomspace(0.3, 35.0, 48)
    gas = 25.0 + 18.0 * (1.0 - np.exp(-radii / 6.0))
    disk = 100.0 * (radii / 3.0) * np.exp(1.0 - radii / 3.0)
    bulge = 30.0 * np.exp(-radii / 1.5)
    errors = np.full(len(radii), 3.0)
    truth_upsilon = 0.65
    truth_a_entropy = 1.5 * A0_CRITICAL
    points = [
        SPARCDataPoint(
            radius_kpc=float(radius),
            v_obs_kms=0.0,
            v_obs_err_kms=float(error),
            v_gas_kms=float(v_gas),
            v_disk_kms=float(v_disk),
            v_bulge_kms=float(v_bulge),
        )
        for radius, error, v_gas, v_disk, v_bulge in zip(
            radii,
            errors,
            gas,
            disk,
            bulge,
            strict=True,
        )
    ]
    return points, truth_upsilon, truth_a_entropy


def _sparc_prediction(
    points: list[SPARCDataPoint],
    upsilon_disk: float,
    a_entropy: float,
) -> np.ndarray:
    return np.asarray(
        [
            compute_emrf_entropic_velocity(
                compute_baryonic_velocity(point, upsilon_disk),
                point.radius_kpc,
                a_entropy,
            )
            for point in points
        ]
    )


def _add_check(
    checks: list[InferenceCheck],
    *,
    name: str,
    metric: str,
    measured: float,
    expected: float,
    lower_bound: float,
    upper_bound: float,
    reference: str,
    limitation: str,
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
            "reference": reference,
            "evidence_class": "synthetic",
            "limitation": limitation,
        }
    )


def _sparc_checks(
    checks: list[InferenceCheck],
    realizations: int,
    seed: int,
) -> tuple[float, float]:
    points, truth_upsilon, truth_a_entropy = _sparc_design()
    prediction = _sparc_prediction(points, truth_upsilon, truth_a_entropy)
    estimates = np.empty((realizations, 2))
    standard_errors = np.empty((realizations, 2))
    reduced_chi2 = np.empty(realizations)
    active_bound_count = 0
    seed_sequence = np.random.SeedSequence(seed).spawn(realizations)
    for index, child_seed in enumerate(seed_sequence):
        noise = np.random.default_rng(child_seed).normal(
            0.0,
            [point.v_obs_err_kms for point in points],
        )
        injected = [
            replace(point, v_obs_kms=float(value))
            for point, value in zip(points, prediction + noise, strict=True)
        ]
        result = fit_sparc_points(
            injected,
            galaxy_name="SYNTHETIC_INJECTION",
            fit_upsilon_disk=True,
            fit_a_entropy=True,
        )
        estimates[index] = (
            result["best_upsilon_disk"],
            result["best_a_entropy"],
        )
        errors = result["parameter_standard_errors"]
        standard_errors[index] = (errors["upsilon_disk"], errors["a_entropy"])
        reduced_chi2[index] = result["reduced_chi2"]
        active_bound_count += len(result["active_bounds"])

    truths = np.array([truth_upsilon, truth_a_entropy])
    empirical_std = estimates.std(axis=0, ddof=1)
    standardized_bias = np.abs(estimates.mean(axis=0) - truths) / empirical_std
    coverage = np.mean(np.abs(estimates - truths) <= standard_errors, axis=0)
    for index, parameter in enumerate(("disk mass-to-light ratio", "entropy acceleration")):
        _add_check(
            checks,
            name=f"SPARC {parameter} recovery bias",
            metric="absolute ensemble bias / empirical standard deviation",
            measured=float(standardized_bias[index]),
            expected=0.0,
            lower_bound=0.0,
            upper_bound=0.35,
            reference="64 deterministic Gaussian-noise injections through the production fitter",
            limitation="Representative synthetic rotation curve; not an observational EMRF test.",
        )
        _add_check(
            checks,
            name=f"SPARC {parameter} interval coverage",
            metric="fraction of local 68.27% intervals containing injected truth",
            measured=float(coverage[index]),
            expected=_NOMINAL_ONE_SIGMA_COVERAGE,
            lower_bound=0.50,
            upper_bound=0.85,
            reference="Observed coverage with finite-ensemble binomial acceptance bounds",
            limitation=(
                "Local Jacobian intervals are checked only for this bounded synthetic design."
            ),
        )
    _add_check(
        checks,
        name="SPARC posterior predictive residual scale",
        metric="mean reduced chi-square",
        measured=float(reduced_chi2.mean()),
        expected=1.0,
        lower_bound=0.80,
        upper_bound=1.20,
        reference="Known Gaussian velocity errors used for injection and fitting",
        limitation="Does not include real SPARC distance, inclination, or calibration systematics.",
    )
    _add_check(
        checks,
        name="SPARC optimizer boundary avoidance",
        metric="active parameter bounds across all fits",
        measured=float(active_bound_count),
        expected=0.0,
        lower_bound=0.0,
        upper_bound=0.0,
        reference="Trust-region reflective active-bound diagnostics",
        limitation="Passing is specific to the declared injected parameter point.",
    )

    starts = ((0.2, 0.5), (0.5, 1.0), (1.0, 2.5), (1.5, 4.0))
    noiseless = [
        replace(point, v_obs_kms=float(value))
        for point, value in zip(points, prediction, strict=True)
    ]
    repeated = np.array(
        [
            (
                result["best_upsilon_disk"],
                result["best_a_entropy"] / A0_CRITICAL,
            )
            for start_upsilon, start_a0_units in starts
            for result in [
                fit_sparc_points(
                    noiseless,
                    galaxy_name="SYNTHETIC_REPEATED_START",
                    fit_upsilon_disk=True,
                    fit_a_entropy=True,
                    initial_upsilon=start_upsilon,
                    initial_a_entropy=start_a0_units * A0_CRITICAL,
                )
            ]
        ]
    )
    relative_spread = float(
        np.max(np.ptp(repeated, axis=0) / np.mean(repeated, axis=0))
    )
    _add_check(
        checks,
        name="SPARC repeated-start agreement",
        metric="maximum relative fitted-parameter spread",
        measured=relative_spread,
        expected=0.0,
        lower_bound=0.0,
        upper_bound=1e-7,
        reference="Four dispersed starts spanning both fitted parameter bounds",
        limitation=(
            "Noiseless representative design; real-data multimodality remains a separate check."
        ),
    )
    return truth_upsilon, truth_a_entropy


def _pantheon_checks(
    checks: list[InferenceCheck],
    realizations: int,
    seed: int,
) -> float:
    rows = 48
    z_hd = np.linspace(0.02, 1.5, rows)
    z_hel = z_hd + 1e-4 * np.sin(np.arange(rows))
    table = np.zeros(
        rows,
        dtype=[("zHD", "f8"), ("zHEL", "f8"), ("m_b_corr", "f8"), ("CID", "U12")],
    )
    table["zHD"] = z_hd
    table["zHEL"] = z_hel
    table["CID"] = [f"SYNTHETIC-{index}" for index in range(rows)]
    sigma = 0.1
    correlation = 0.12
    covariance = sigma**2 * (
        (1.0 - correlation) * np.eye(rows) + correlation * np.ones((rows, rows))
    )
    cholesky_factor = np.linalg.cholesky(covariance)
    truth_omega_m = 0.31
    prediction = dimensionless_magnitudes(z_hd, z_hel, truth_omega_m) + 23.8
    estimates = np.empty(realizations)
    reduced_chi2 = np.empty(realizations)
    covered = np.zeros(realizations, dtype=bool)
    boundary_count = 0
    seed_sequence = np.random.SeedSequence(seed).spawn(realizations)
    for index, child_seed in enumerate(seed_sequence):
        standard_noise = np.random.default_rng(child_seed).normal(size=rows)
        table["m_b_corr"] = prediction + cholesky_factor @ standard_noise
        result = fit_baseline(table, covariance)
        estimates[index] = result["omega_m"]
        reduced_chi2[index] = result["chi2_reduced_descriptive"]
        interval = result["omega_m_delta_chi2_1_interval"]
        if interval[0] is None or interval[1] is None:
            boundary_count += 1
        else:
            covered[index] = interval[0] <= truth_omega_m <= interval[1]

    empirical_std = float(estimates.std(ddof=1))
    standardized_bias = abs(float(estimates.mean()) - truth_omega_m) / empirical_std
    coverage = float(covered.mean())
    _add_check(
        checks,
        name="Pantheon full-covariance omega_m recovery bias",
        metric="absolute ensemble bias / empirical standard deviation",
        measured=standardized_bias,
        expected=0.0,
        lower_bound=0.0,
        upper_bound=0.35,
        reference="64 deterministic correlated-noise injections through the production fitter",
        limitation="Synthetic Pantheon-like design; not an EMRF prediction or an H0 measurement.",
    )
    _add_check(
        checks,
        name="Pantheon delta-chi-square interval coverage",
        metric="fraction of profile 68.27% intervals containing injected truth",
        measured=coverage,
        expected=_NOMINAL_ONE_SIGMA_COVERAGE,
        lower_bound=0.50,
        upper_bound=0.85,
        reference="Full supplied covariance and profiled magnitude offset",
        limitation="Fixed covariance Gaussian experiment; no selection or covariance uncertainty.",
    )
    _add_check(
        checks,
        name="Pantheon posterior predictive residual scale",
        metric="mean reduced chi-square",
        measured=float(reduced_chi2.mean()),
        expected=1.0,
        lower_bound=0.80,
        upper_bound=1.20,
        reference="Known multivariate Gaussian covariance used for injection and fitting",
        limitation=(
            "Does not reproduce the real survey selection function or non-Gaussian systematics."
        ),
    )
    _add_check(
        checks,
        name="Pantheon profile boundary avoidance",
        metric="unbounded delta-chi-square intervals across all fits",
        measured=float(boundary_count),
        expected=0.0,
        lower_bound=0.0,
        upper_bound=0.0,
        reference="Declared omega_m fit domain [0.05, 0.6]",
        limitation="Passing is specific to the declared injected cosmology and redshift design.",
    )
    return truth_omega_m


@lru_cache(maxsize=4)
def inference_validation_report(
    realizations: int = _DEFAULT_REALIZATIONS,
    random_seed: int = _DEFAULT_SEED,
) -> InferenceValidationReport:
    """Run deterministic recovery, coverage, residual, and optimizer checks."""
    if isinstance(realizations, bool) or not isinstance(realizations, int) or realizations < 16:
        raise ValueError("realizations must be an integer of at least 16")
    if isinstance(random_seed, bool) or not isinstance(random_seed, int) or random_seed < 0:
        raise ValueError("random_seed must be a non-negative integer")
    checks: list[InferenceCheck] = []
    truth_upsilon, truth_a_entropy = _sparc_checks(
        checks,
        realizations,
        random_seed,
    )
    truth_omega_m = _pantheon_checks(
        checks,
        realizations,
        random_seed + 1,
    )
    return {
        "evidence_class": "synthetic",
        "all_passed": all(check["passed"] for check in checks),
        "realizations": realizations,
        "random_seed": random_seed,
        "checks": checks,
        "truths": {
            "sparc_upsilon_disk": truth_upsilon,
            "sparc_a_entropy_m_per_s2": truth_a_entropy,
            "pantheon_omega_m": truth_omega_m,
        },
        "limitations": [
            "This certificate validates inference software with synthetic injections.",
            "It does not constitute observational evidence for EMRF.",
            (
                "Real SPARC nuisance-parameter SBC and real-survey posterior predictive "
                "checks remain pending."
            ),
        ],
    }


__all__ = [
    "InferenceCheck",
    "InferenceValidationReport",
    "inference_validation_report",
]
