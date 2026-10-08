"""Fit an uncalibrated flat-LCDM baseline to authentic Pantheon+ full-covariance data."""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.linalg import cholesky, solve_triangular
from scipy.optimize import brentq, minimize_scalar

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from emergent_matter_model.fetch_real_data import download, sha256_of

RELEASE = "c447f0fea703fcd0fff57de5000947b5ca81286b"
BASE = f"https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/{RELEASE}/Pantheon%2B_Data/"
COVARIANCE_SYMMETRY_TOLERANCE = 5e-8


def read_covariance(path: Path, expected_rows: int) -> tuple[np.ndarray, float]:
    with path.open(encoding="utf-8") as handle:
        n = int(handle.readline())
        values = np.loadtxt(handle)
    if n != expected_rows or values.size != n*n:
        raise ValueError("Covariance dimension does not match the measurement row order")
    covariance = values.reshape(n, n)
    if not np.isfinite(covariance).all() or np.any(np.diag(covariance) <= 0):
        raise ValueError("Covariance has non-finite entries or nonpositive diagonal")
    asymmetry = float(np.max(np.abs(covariance - covariance.T)))
    if asymmetry > COVARIANCE_SYMMETRY_TOLERANCE:
        raise ValueError("Covariance asymmetry exceeds the declared serialization tolerance")
    return .5*(covariance + covariance.T), asymmetry


def dimensionless_magnitudes(z_hd: np.ndarray, z_hel: np.ndarray,
                             omega_m: float, nodes: int = 64) -> np.ndarray:
    if (not 0 < omega_m < 1 or np.any(z_hd <= 0) or np.any(z_hel <= -1)
            or not np.isfinite(z_hd).all() or not np.isfinite(z_hel).all()):
        raise ValueError("Invalid redshift or matter density")
    x, weights = np.polynomial.legendre.leggauss(nodes)
    redshift = z_hd[:, None]*(x + 1)/2
    integral = z_hd/2 * ((1/np.sqrt(omega_m*(1+redshift)**3 + 1-omega_m)) @ weights)
    return 5*np.log10((1+z_hel)*integral)


def profile_offset(observed: np.ndarray, prediction: np.ndarray,
                   chol: np.ndarray) -> tuple[float, float]:
    residual = solve_triangular(chol, observed-prediction, lower=True, check_finite=True)
    constant = solve_triangular(chol, np.ones(len(observed)), lower=True)
    offset = float(constant @ residual / (constant @ constant))
    adjusted = residual - offset*constant
    return float(adjusted @ adjusted), offset


def fit_baseline(table: np.ndarray, covariance: np.ndarray) -> dict:
    required = {"zHD", "zHEL", "m_b_corr", "CID"}
    if not required <= set(table.dtype.names or ()):
        raise ValueError("Missing required Pantheon+ measurement columns")
    if covariance.shape != (len(table), len(table)):
        raise ValueError("Covariance dimension mismatch")
    mask = table["zHD"] > .01
    sample = table[mask]
    if len(sample) < 3:
        raise ValueError("Insufficient Hubble-flow rows")
    cov = covariance[np.ix_(mask, mask)]
    chol = cholesky(cov, lower=True, check_finite=True)
    observed = np.asarray(sample["m_b_corr"], dtype=float)

    def objective(omega_m: float, nodes: int = 64) -> tuple[float, float]:
        prediction = dimensionless_magnitudes(sample["zHD"], sample["zHEL"], omega_m, nodes)
        return profile_offset(observed, prediction, chol)

    optimum = minimize_scalar(lambda om: objective(om)[0], bounds=(.05, .6), method="bounded",
                              options={"xatol": 1e-10})
    if not optimum.success or not np.isfinite(optimum.fun):
        raise RuntimeError("Supernova baseline optimizer did not converge")
    omega_m = float(optimum.x)
    chi2, offset = objective(omega_m)
    interval: list[float | None] = []
    for edge in (.05, .6):
        if objective(edge)[0] - chi2 < 1:
            interval.append(None)
        else:
            lo, hi = sorted((edge, omega_m))
            interval.append(float(brentq(lambda om: objective(om)[0]-chi2-1, lo, hi)))
    quadrature_delta = abs(objective(omega_m, nodes=128)[0] - chi2)
    if quadrature_delta > 1e-6:
        raise RuntimeError("Magnitude integration did not converge at the required tolerance")
    negative_two_log_l = chi2 + 2*np.log(np.diag(chol)).sum() + len(sample)*np.log(2*np.pi)
    return {
        "model": "flat LCDM, free uncalibrated magnitude offset, negligible late-time radiation",
        "evidence_grade": "baseline_only_not_EMRF",
        "selection": "zHD > 0.01; preserve official row order; no independent Cepheid likelihood",
        "input_rows": len(table), "selected_rows": len(sample),
        "distinct_CID": len(np.unique(sample["CID"])),
        "selected_row_indices_zero_based": np.flatnonzero(mask).tolist(),
        "omega_m": omega_m, "omega_m_delta_chi2_1_interval": interval,
        "interval_kind": "conditional Gaussian data-likelihood profile with fixed supplied covariance",
        "magnitude_offset": offset,
        "magnitude_offset_definition": "M + 25 + 5 log10[(c/H0)/Mpc]",
        "H0_inferred": False, "H0_reason": "Absolute SN magnitude and H0 are degenerate",
        "chi2": chi2, "degrees_of_freedom": len(sample)-2,
        "chi2_reduced_descriptive": chi2/(len(sample)-2),
        "covariance_used": "STAT+SYS full selected submatrix",
        "integration_check_absolute_delta_chi2": quadrature_delta,
        "negative_two_log_likelihood": float(negative_two_log_l),
        "BIC": float(negative_two_log_l + 2*np.log(len(sample))),
        "BIC_note": "single regular Gaussian baseline; no EMRF model preference",
        "boundary_minimum": bool(omega_m < .0501 or omega_m > .5999),
        "limitations": ["not an EMRF prediction", "not a SH0ES H0 measurement",
                        "published covariance held fixed; no raw photometry refit",
                        "no joint SN/BAO inference or all-regime theory validation"],
    }


def main() -> None:
    manual = ROOT / "data" / "external"
    cache = manual / "real_data_followup"
    cache.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for source_name, local_name in (
        ("Pantheon%2BSH0ES.dat", "Pantheon+SH0ES.dat.txt"),
        ("Pantheon%2BSH0ES_STAT%2BSYS.cov", "Pantheon+SH0ES_STAT+SYS.cov.txt"),
    ):
        local = manual / local_name
        if not local.is_file():
            raise FileNotFoundError(f"Manual download is missing: {local}")
        url = BASE + "4_DISTANCES_AND_COVAR/" + source_name
        reference = cache / local_name
        download(url, reference)
        digest = sha256_of(reference)
        if sha256_of(local) != digest:
            raise ValueError(f"Manual file differs from the pinned official release: {local.name}")
        manifest[local_name] = {"url": url, "sha256": digest, "bytes": local.stat().st_size,
                                "manual_file": str(local.relative_to(ROOT)),
                                "source_bytes_match": True}
    for label, suffix in (
        ("release_readme", "4_DISTANCES_AND_COVAR/README"),
        ("collaboration_likelihood",
         "5_COSMOLOGY/cosmosis_likelihoods/Pantheon%2B_only_cosmosis_likelihood.py"),
    ):
        path = cache / f"{label}.txt"
        download(BASE + suffix, path)
        manifest[label] = {"url": BASE + suffix, "sha256": sha256_of(path),
                           "bytes": path.stat().st_size}
    table = np.genfromtxt(manual / "Pantheon+SH0ES.dat.txt", names=True, dtype=None,
                          encoding="utf-8")
    covariance, asymmetry = read_covariance(manual / "Pantheon+SH0ES_STAT+SYS.cov.txt", len(table))
    result = fit_baseline(table, covariance)
    result.update(
        generated_utc=datetime.now(timezone.utc).isoformat(),
        python=platform.python_version(), numpy=np.__version__, source_manifest=manifest,
        covariance_asymmetry_max=asymmetry,
        covariance_symmetry_rule=f"(C+C.T)/2 only if max asymmetry <= {COVARIANCE_SYMMETRY_TOLERANCE}",
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    )
    output = ROOT / "results" / "real_data_followup" / "pantheon_baseline.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in (
        "selected_rows", "distinct_CID", "omega_m", "omega_m_delta_chi2_1_interval",
        "chi2", "degrees_of_freedom", "integration_check_absolute_delta_chi2")}, indent=2))
    print(f"Saved {output}; baseline only, not an EMRF validation.")


if __name__ == "__main__":
    main()
