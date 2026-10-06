"""JWST High-Redshift Galaxy Kinematics Evaluation Engine.

Evaluates the cosmological evolution of the EMRF cosmic horizon entropy acceleration
floor a_0(z) = c * H(z) / (2 * pi) against kinematic observations of high-redshift
disk galaxies observed by JWST NIRSpec and ALMA (z ~ 1 - 7).

Compares:
1. Static acceleration floor: a_0(z) = a_0(0) = const
2. Cosmological evolving entropic floor: a_0(z) = a_0(0) * sqrt(Omega_m * (1+z)^3 + Omega_Lambda)
3. Pure Newtonian baryonic gravity without dark matter / entropic enhancement
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

# Physical and Cosmological Constants (SI and Astro units)
G_CONST_SI = 6.67430e-11                  # m^3 kg^-1 s^-2
M_SUN_KG = 1.98847e30                     # Solar mass in kg
KMS_TO_MS = 1.0e3                         # 1 km/s in m/s
A0_ZERO_SI = 1.20e-10                     # Local acceleration floor at z=0, m/s^2

# Planck 2018 Cosmological Parameters
OMEGA_M_DEFAULT = 0.315
OMEGA_LAMBDA_DEFAULT = 0.685
H0_DEFAULT_KMS_MPC = 67.4


@dataclass
class HighZGalaxyRecord:
    """Observation record for a high-redshift galaxy."""
    galaxy_id: str
    redshift_z: float
    log_m_bar_solar: float
    log_m_bar_err: float
    v_rot_kms: float
    v_rot_err_kms: float
    r_half_light_kpc: float
    survey: str
    reference: str

    @property
    def m_bar_kg(self) -> float:
        return (10.0 ** self.log_m_bar_solar) * M_SUN_KG


def hubble_expansion_factor(
    z: float,
    omega_m: float = OMEGA_M_DEFAULT,
    omega_lambda: float = OMEGA_LAMBDA_DEFAULT
) -> float:
    """Computes the dimensionless expansion factor E(z) = H(z) / H_0.
    
    Assumes flat FLRW universe: E(z) = sqrt(Omega_m * (1+z)^3 + Omega_Lambda).
    """
    if z < 0.0:
        raise ValueError(f"Redshift z must be >= 0, got {z}")
    return math.sqrt(omega_m * ((1.0 + z) ** 3) + omega_lambda)


def critical_acceleration_z(
    z: float,
    a0_zero: float = A0_ZERO_SI,
    omega_m: float = OMEGA_M_DEFAULT,
    omega_lambda: float = OMEGA_LAMBDA_DEFAULT
) -> float:
    """Computes the evolving cosmic horizon acceleration scale a_0(z) in m/s^2.
    
    In EMRF, a_0(z) = c * H(z) / (2 * pi) = a_0(0) * E(z).
    """
    return a0_zero * hubble_expansion_factor(z, omega_m, omega_lambda)


def predict_flat_velocity_kms(
    m_bar_solar: float,
    a0_m_s2: float
) -> float:
    """Predicts asymptotic flat rotation velocity in km/s via BTFR: V_flat = (G * M * a_0)^(1/4)."""
    m_kg = m_bar_solar * M_SUN_KG
    v_ms = (G_CONST_SI * m_kg * a0_m_s2) ** 0.25
    return v_ms / KMS_TO_MS


def load_high_z_catalog(csv_path: Path | str) -> List[HighZGalaxyRecord]:
    """Load high-redshift galaxy kinematics CSV table."""
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(f"High-Z kinematics catalog not found: {path}")

    records = []
    with open(path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rec = HighZGalaxyRecord(
                galaxy_id=row["galaxy_id"].strip(),
                redshift_z=float(row["redshift_z"]),
                log_m_bar_solar=float(row["log_m_bar_solar"]),
                log_m_bar_err=float(row["log_m_bar_err"]),
                v_rot_kms=float(row["v_rot_kms"]),
                v_rot_err_kms=float(row["v_rot_err_kms"]),
                r_half_light_kpc=float(row["r_half_light_kpc"]),
                survey=row["survey"].strip(),
                reference=row["reference"].strip()
            )
            records.append(rec)
    return records


def evaluate_high_z_kinematics(
    catalog: List[HighZGalaxyRecord],
    a0_zero: float = A0_ZERO_SI,
    omega_m: float = OMEGA_M_DEFAULT,
    omega_lambda: float = OMEGA_LAMBDA_DEFAULT
) -> Dict[str, Any]:
    """Evaluates Static a0 vs. Cosmologically Evolving a0(z) against JWST/ALMA observations."""
    n_galaxies = len(catalog)
    if n_galaxies == 0:
        raise ValueError("Catalog contains no galaxy records.")

    v_obs_list = []
    v_err_list = []
    v_pred_static_list = []
    v_pred_evolving_list = []
    galaxy_reports = []

    chi2_static = 0.0
    chi2_evolving = 0.0

    for gal in catalog:
        m_bar = 10.0 ** gal.log_m_bar_solar
        v_obs = gal.v_rot_kms
        v_err = gal.v_rot_err_kms

        # 1. Static a0 baseline: a0 = a0(0)
        v_pred_static = predict_flat_velocity_kms(m_bar, a0_zero)
        res_static = (v_obs - v_pred_static) / v_err
        chi2_static += res_static ** 2

        # 2. Cosmologically evolving a0(z): a0(z) = a0(0) * E(z)
        a0_z = critical_acceleration_z(gal.redshift_z, a0_zero, omega_m, omega_lambda)
        v_pred_evolving = predict_flat_velocity_kms(m_bar, a0_z)
        res_evolving = (v_obs - v_pred_evolving) / v_err
        chi2_evolving += res_evolving ** 2

        v_obs_list.append(v_obs)
        v_err_list.append(v_err)
        v_pred_static_list.append(v_pred_static)
        v_pred_evolving_list.append(v_pred_evolving)

        galaxy_reports.append({
            "galaxy_id": gal.galaxy_id,
            "redshift_z": gal.redshift_z,
            "e_z": hubble_expansion_factor(gal.redshift_z, omega_m, omega_lambda),
            "v_obs_kms": v_obs,
            "v_obs_err_kms": v_err,
            "v_pred_static_kms": round(v_pred_static, 1),
            "v_pred_evolving_kms": round(v_pred_evolving, 1),
            "residual_static_sigma": round(res_static, 2),
            "residual_evolving_sigma": round(res_evolving, 2),
            "survey": gal.survey
        })

    # Information Criteria (both models have 1 global scale parameter a0_0, so k=1)
    k_params = 1
    bic_static = k_params * math.log(n_galaxies) + chi2_static
    bic_evolving = k_params * math.log(n_galaxies) + chi2_evolving
    delta_bic = bic_evolving - bic_static

    if delta_bic <= -6.0:
        verdict = "Evolving a_0(z) decisively favored over static a_0."
    elif delta_bic >= 6.0:
        verdict = "Static a_0 favored over evolving a_0(z)."
    else:
        verdict = "Inconclusive / both models are statistically competitive at current observational precision."

    return {
        "dataset": "JWST & ALMA High-Redshift Galaxy Kinematics",
        "n_galaxies": n_galaxies,
        "redshift_range": [min(g.redshift_z for g in catalog), max(g.redshift_z for g in catalog)],
        "models": {
            "static_a0": {
                "chi2": float(chi2_static),
                "reduced_chi2": float(chi2_static / max(n_galaxies - 1, 1)),
                "bic": float(bic_static)
            },
            "evolving_a0_z": {
                "chi2": float(chi2_evolving),
                "reduced_chi2": float(chi2_evolving / max(n_galaxies - 1, 1)),
                "bic": float(bic_evolving)
            }
        },
        "model_comparison": {
            "delta_bic": float(delta_bic),
            "delta_chi2": float(chi2_evolving - chi2_static),
            "verdict": verdict
        },
        "galaxy_reports": galaxy_reports
    }


def main():
    """CLI entry point for high-z kinematics evaluation."""
    parser = argparse.ArgumentParser(description="EMRF JWST High-Redshift Kinematics Evaluation Engine")
    parser.add_argument("--catalog", type=str, default=None, help="Path to high-z kinematics CSV table.")
    parser.add_argument("--output", type=str, default=None, help="Optional output JSON path.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    cat_path = Path(args.catalog) if args.catalog else (repo_root / "data" / "jwst" / "jwst_kinematics_sample.csv")

    catalog = load_high_z_catalog(cat_path)
    report = evaluate_high_z_kinematics(catalog)

    print("\n" + "=" * 80)
    print(" EMRF JWST HIGH-REDSHIFT GALAXY KINEMATICS EVALUATION")
    print("=" * 80)
    print(f"Sample Size: {report['n_galaxies']} galaxies (z = {report['redshift_range'][0]:.2f} - {report['redshift_range'][1]:.2f})")
    print("-" * 80)
    print(f"Static a_0(0) Baseline:      Chi2 = {report['models']['static_a0']['chi2']:6.1f} | Red Chi2 = {report['models']['static_a0']['reduced_chi2']:.2f} | BIC = {report['models']['static_a0']['bic']:6.1f}")
    print(f"Evolving a_0(z) Entropic:    Chi2 = {report['models']['evolving_a0_z']['chi2']:6.1f} | Red Chi2 = {report['models']['evolving_a0_z']['reduced_chi2']:.2f} | BIC = {report['models']['evolving_a0_z']['bic']:6.1f}")
    print("-" * 80)
    print(f"Delta-BIC (Evolving vs. Static): {report['model_comparison']['delta_bic']:+.2f}")
    print(f"Delta-Chi2:                      {report['model_comparison']['delta_chi2']:+.2f}")
    print(f"Verdict: {report['model_comparison']['verdict']}")
    print("=" * 80)
    print("\nPer-Galaxy Predictions (V_obs vs. Models):")
    print(f"{'Galaxy':18s} {'z':5s} {'E(z)':5s} {'V_obs (km/s)':14s} {'V_static':10s} {'V_evolv':10s} {'Res(evolv)':10s}")
    print("-" * 80)
    for g in report["galaxy_reports"]:
        print(f"{g['galaxy_id']:18s} {g['redshift_z']:5.2f} {g['e_z']:5.2f} {g['v_obs_kms']:5.1f} ± {g['v_obs_err_kms']:4.1f}   {g['v_pred_static_kms']:7.1f}    {g['v_pred_evolving_kms']:7.1f}    {g['residual_evolving_sigma']:+5.2f} sigma")
    print("=" * 80 + "\n")

    if args.output:
        out_p = Path(args.output)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to: {out_p}")


if __name__ == "__main__":
    main()
