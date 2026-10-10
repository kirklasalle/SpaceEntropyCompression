"""Reusable full-covariance inference for an uncalibrated Pantheon-like sample."""

from __future__ import annotations

import math

import numpy as np
from scipy.integrate import quad
from scipy.linalg import cholesky, solve_triangular
from scipy.optimize import brentq, minimize_scalar
from scipy.special import ndtr
from scipy.stats import chi2 as chi2_distribution

COVARIANCE_SYMMETRY_TOLERANCE = 5e-8


def read_covariance(path, expected_rows: int) -> tuple[np.ndarray, float]:
    with path.open(encoding="utf-8") as handle:
        n = int(handle.readline())
        values = np.loadtxt(handle)
    if n != expected_rows or values.size != n * n:
        raise ValueError("Covariance dimension does not match the measurement row order")
    covariance = values.reshape(n, n)
    if not np.isfinite(covariance).all() or np.any(np.diag(covariance) <= 0):
        raise ValueError("Covariance has non-finite entries or nonpositive diagonal")
    asymmetry = float(np.max(np.abs(covariance - covariance.T)))
    if asymmetry > COVARIANCE_SYMMETRY_TOLERANCE:
        raise ValueError("Covariance asymmetry exceeds the declared serialization tolerance")
    return 0.5 * (covariance + covariance.T), asymmetry


def dimensionless_magnitudes(
    z_hd: np.ndarray,
    z_hel: np.ndarray,
    omega_m: float,
    nodes: int = 64,
) -> np.ndarray:
    if (
        not 0 < omega_m < 1
        or np.any(z_hd <= 0)
        or np.any(z_hel <= -1)
        or not np.isfinite(z_hd).all()
        or not np.isfinite(z_hel).all()
    ):
        raise ValueError("Invalid redshift or matter density")
    x, weights = np.polynomial.legendre.leggauss(nodes)
    redshift = z_hd[:, None] * (x + 1) / 2
    integral = z_hd / 2 * (
        (1 / np.sqrt(omega_m * (1 + redshift) ** 3 + 1 - omega_m)) @ weights
    )
    return 5 * np.log10((1 + z_hel) * integral)


def profile_offset(
    observed: np.ndarray,
    prediction: np.ndarray,
    chol: np.ndarray,
) -> tuple[float, float]:
    residual = solve_triangular(
        chol,
        observed - prediction,
        lower=True,
        check_finite=True,
    )
    constant = solve_triangular(chol, np.ones(len(observed)), lower=True)
    offset = float(constant @ residual / (constant @ constant))
    adjusted = residual - offset * constant
    return float(adjusted @ adjusted), offset


def _selected_problem(
    table: np.ndarray,
    covariance: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    required = {"zHD", "zHEL", "m_b_corr", "CID"}
    if not required <= set(table.dtype.names or ()):
        raise ValueError("Missing required Pantheon+ measurement columns")
    if covariance.shape != (len(table), len(table)):
        raise ValueError("Covariance dimension mismatch")
    mask = table["zHD"] > 0.01
    sample = table[mask]
    if len(sample) < 3:
        raise ValueError("Insufficient Hubble-flow rows")
    cov = covariance[np.ix_(mask, mask)]
    chol = cholesky(cov, lower=True, check_finite=True)
    observed = np.asarray(sample["m_b_corr"], dtype=float)
    return mask, sample, chol, observed


def pantheon_residual_diagnostics(
    table: np.ndarray,
    covariance: np.ndarray,
    *,
    omega_m: float,
) -> dict:
    """Return full-covariance whitened residual and chi-square diagnostics."""
    _, sample, chol, observed = _selected_problem(table, covariance)
    prediction = dimensionless_magnitudes(
        sample["zHD"],
        sample["zHEL"],
        omega_m,
    )
    transformed = solve_triangular(
        chol,
        observed - prediction,
        lower=True,
        check_finite=True,
    )
    constant = solve_triangular(chol, np.ones(len(observed)), lower=True)
    offset = float(constant @ transformed / (constant @ constant))
    residual = transformed - offset * constant
    chi2 = float(residual @ residual)
    degrees_of_freedom = len(sample) - 2
    lag_one = float(np.corrcoef(residual[:-1], residual[1:])[0, 1])
    return {
        "whitened_residual_mean": float(residual.mean()),
        "whitened_residual_rms": float(np.sqrt(np.mean(residual**2))),
        "whitened_residual_max_abs": float(np.max(np.abs(residual))),
        "whitened_residual_lag1_correlation": lag_one,
        "chi2_survival_probability": float(
            chi2_distribution.sf(chi2, degrees_of_freedom)
        ),
        "degrees_of_freedom": degrees_of_freedom,
        "interpretation": (
            "Full-covariance residual diagnostic; not an EMRF posterior prediction"
        ),
    }


def pantheon_log_evidence(
    table: np.ndarray,
    covariance: np.ndarray,
    *,
    omega_m_prior: tuple[float, float] = (0.05, 0.6),
    magnitude_offset_prior: tuple[float, float] = (-50.0, 50.0),
) -> dict:
    """Marginalize the two-parameter Gaussian baseline under declared priors."""
    _, sample, chol, observed = _selected_problem(table, covariance)
    omega_lower, omega_upper = omega_m_prior
    offset_lower, offset_upper = magnitude_offset_prior
    if not 0 < omega_lower < omega_upper < 1:
        raise ValueError("omega_m prior must be increasing and contained in (0, 1)")
    if not offset_lower < offset_upper:
        raise ValueError("magnitude offset prior must be increasing")
    constant = solve_triangular(chol, np.ones(len(observed)), lower=True)
    offset_information = float(constant @ constant)
    offset_sigma = math.sqrt(1.0 / offset_information)

    def profiled(omega_m: float) -> tuple[float, float]:
        prediction = dimensionless_magnitudes(
            sample["zHD"],
            sample["zHEL"],
            omega_m,
        )
        return profile_offset(observed, prediction, chol)

    optimum = minimize_scalar(
        lambda omega_m: profiled(omega_m)[0],
        bounds=omega_m_prior,
        method="bounded",
        options={"xatol": 1e-10},
    )
    if not optimum.success or not np.isfinite(optimum.fun):
        raise RuntimeError("Evidence reference optimization did not converge")
    minimum_chi2 = float(optimum.fun)
    offset_width = offset_upper - offset_lower

    def relative_integrand(omega_m: float) -> float:
        chi2, offset = profiled(omega_m)
        upper_probability = ndtr((offset_upper - offset) / offset_sigma)
        lower_probability = ndtr((offset_lower - offset) / offset_sigma)
        offset_factor = (
            math.sqrt(2.0 * math.pi) * offset_sigma
            * (upper_probability - lower_probability)
            / offset_width
        )
        return math.exp(-0.5 * (chi2 - minimum_chi2)) * offset_factor

    relative_integral, integration_error = quad(
        relative_integrand,
        omega_lower,
        omega_upper,
        epsabs=1e-12,
        epsrel=1e-10,
    )
    omega_width = omega_upper - omega_lower
    log_normalization = (
        -float(np.log(np.diag(chol)).sum())
        - 0.5 * len(sample) * math.log(2.0 * math.pi)
    )
    log_evidence = (
        log_normalization
        - 0.5 * minimum_chi2
        + math.log(relative_integral / omega_width)
    )
    return {
        "log_evidence": float(log_evidence),
        "method": "deterministic quadrature with analytical offset marginalization",
        "omega_m_uniform_prior": [omega_lower, omega_upper],
        "magnitude_offset_uniform_prior": [offset_lower, offset_upper],
        "integration_absolute_error": float(integration_error),
        "prior_dependent": True,
        "evidence_class": "observational-baseline",
        "limitation": "Flat-LCDM baseline evidence only; no EMRF Bayes factor is implied",
    }


def fit_baseline(
    table: np.ndarray,
    covariance: np.ndarray,
    *,
    extended_diagnostics: bool = False,
) -> dict:
    mask, sample, chol, observed = _selected_problem(table, covariance)

    def objective(omega_m: float, nodes: int = 64) -> tuple[float, float]:
        prediction = dimensionless_magnitudes(
            sample["zHD"],
            sample["zHEL"],
            omega_m,
            nodes,
        )
        return profile_offset(observed, prediction, chol)

    optimum = minimize_scalar(
        lambda om: objective(om)[0],
        bounds=(0.05, 0.6),
        method="bounded",
        options={"xatol": 1e-10},
    )
    if not optimum.success or not np.isfinite(optimum.fun):
        raise RuntimeError("Supernova baseline optimizer did not converge")
    omega_m = float(optimum.x)
    chi2, offset = objective(omega_m)
    interval: list[float | None] = []
    for edge in (0.05, 0.6):
        if objective(edge)[0] - chi2 < 1:
            interval.append(None)
        else:
            lo, hi = sorted((edge, omega_m))
            interval.append(
                float(brentq(lambda om: objective(om)[0] - chi2 - 1, lo, hi))
            )
    quadrature_delta = abs(objective(omega_m, nodes=128)[0] - chi2)
    if quadrature_delta > 1e-6:
        raise RuntimeError("Magnitude integration did not converge at the required tolerance")
    negative_two_log_l = (
        chi2 + 2 * np.log(np.diag(chol)).sum() + len(sample) * np.log(2 * np.pi)
    )
    result = {
        "model": "flat LCDM, free uncalibrated magnitude offset, negligible late-time radiation",
        "evidence_grade": "baseline_only_not_EMRF",
        "selection": "zHD > 0.01; preserve official row order; no independent Cepheid likelihood",
        "input_rows": len(table),
        "selected_rows": len(sample),
        "distinct_CID": len(np.unique(sample["CID"])),
        "selected_row_indices_zero_based": np.flatnonzero(mask).tolist(),
        "omega_m": omega_m,
        "omega_m_delta_chi2_1_interval": interval,
        "interval_kind": (
            "conditional Gaussian data-likelihood profile with fixed supplied covariance"
        ),
        "magnitude_offset": offset,
        "magnitude_offset_definition": "M + 25 + 5 log10[(c/H0)/Mpc]",
        "H0_inferred": False,
        "H0_reason": "Absolute SN magnitude and H0 are degenerate",
        "chi2": chi2,
        "degrees_of_freedom": len(sample) - 2,
        "chi2_reduced_descriptive": chi2 / (len(sample) - 2),
        "covariance_used": "STAT+SYS full selected submatrix",
        "integration_check_absolute_delta_chi2": quadrature_delta,
        "negative_two_log_likelihood": float(negative_two_log_l),
        "BIC": float(negative_two_log_l + 2 * np.log(len(sample))),
        "BIC_note": "single regular Gaussian baseline; no EMRF model preference",
        "boundary_minimum": bool(omega_m < 0.0501 or omega_m > 0.5999),
        "limitations": [
            "not an EMRF prediction",
            "not a SH0ES H0 measurement",
            "published covariance held fixed; no raw photometry refit",
            "no joint SN/BAO inference or all-regime theory validation",
        ],
    }
    if extended_diagnostics:
        result["posterior_predictive_diagnostics"] = pantheon_residual_diagnostics(
            table,
            covariance,
            omega_m=omega_m,
        )
        result["declared_prior_evidence"] = pantheon_log_evidence(table, covariance)
    return result


__all__ = [
    "COVARIANCE_SYMMETRY_TOLERANCE",
    "dimensionless_magnitudes",
    "fit_baseline",
    "pantheon_log_evidence",
    "pantheon_residual_diagnostics",
    "profile_offset",
    "read_covariance",
]
