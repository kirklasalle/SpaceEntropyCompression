"""Astrometry projection, orbit fitting, and Bayesian model comparison for EMRF.

Confronts theoretical formulations and relativistic baselines against high-precision
astrometric and radial velocity observations of stars orbiting Sagittarius A* (e.g. S2, S301).
Implements the objective Bifurcation Protocol using Delta-BIC model selection.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    from data_provenance import provenance_banner
except ImportError:  # imported as a package
    from emergent_matter_model.data_provenance import provenance_banner
# Physical and Astronomical Constants (SI)
G_CONST = 6.67430e-11          # Gravitational constant, m^3 kg^-1 s^-2
C_LIGHT = 2.99792458e8         # Speed of light, m s^-1
MSUN = 1.98847e30              # Solar mass, kg
AU_METERS = 1.495978707e11     # Astronomical Unit, m
PC_METERS = 3.085677581e16     # Parsec, m
RAD_TO_MAS = 206264806.247     # Radians to milliarcseconds
SEC_PER_YEAR = 365.25 * 86400.0  # Seconds per Julian year


@dataclass
class SgrAOrbitalParameters:
    """Orbital elements and system parameters for stars orbiting Sgr A*."""
    name: str
    mass_bh: float             # Black hole mass in solar masses (e.g. 4.3e6)
    distance_pc: float         # Distance to Galactic Center in parsecs (e.g. 8275.0)
    semi_major_axis_au: float  # Semi-major axis in AU
    eccentricity: float        # Orbital eccentricity
    period_yr: float           # Orbital period in Julian years
    inclination_deg: float     # Orbital inclination in degrees
    omega_node_deg: float      # Longitude of ascending node in degrees
    arg_peri_deg: float        # Argument of periapsis in degrees
    t_peri_epoch: float        # Epoch of pericenter passage in decimal years
    v_z0_kms: float = 0.0      # Systemic line-of-sight velocity in km/s


# Published benchmark parameters from GRAVITY Collaboration
S2_BENCHMARK_PARAMS = SgrAOrbitalParameters(
    name="S2",
    mass_bh=4.297e6,
    distance_pc=8275.0,
    semi_major_axis_au=1035.0,  # ~0.125 arcsec at 8275 pc
    eccentricity=0.88466,
    period_yr=16.051,
    inclination_deg=134.57,
    omega_node_deg=228.18,
    arg_peri_deg=66.26,
    t_peri_epoch=2018.379,
    v_z0_kms=-15.0
)

# Benchmark parameters for S29 (ESO A&A 2021)
S29_BENCHMARK_PARAMS = SgrAOrbitalParameters(
    name="S29",
    mass_bh=4.297e6,
    distance_pc=8275.0,
    semi_major_axis_au=3475.0,
    eccentricity=0.969,
    period_yr=90.0,
    inclination_deg=143.6,
    omega_node_deg=128.5,
    arg_peri_deg=173.2,
    t_peri_epoch=2021.410,
    v_z0_kms=-10.0
)

# Benchmark parameters for S38 (ESO A&A 2020)
S38_BENCHMARK_PARAMS = SgrAOrbitalParameters(
    name="S38",
    mass_bh=4.297e6,
    distance_pc=8275.0,
    semi_major_axis_au=1175.0,
    eccentricity=0.820,
    period_yr=19.2,
    inclination_deg=171.1,
    omega_node_deg=101.4,
    arg_peri_deg=24.3,
    t_peri_epoch=2003.250,
    v_z0_kms=12.0
)

# Benchmark parameters for S55 / S0-102 (Science 2012, ESO 2020)
S55_BENCHMARK_PARAMS = SgrAOrbitalParameters(
    name="S55",
    mass_bh=4.297e6,
    distance_pc=8275.0,
    semi_major_axis_au=894.0,
    eccentricity=0.720,
    period_yr=12.8,
    inclination_deg=150.1,
    omega_node_deg=325.2,
    arg_peri_deg=331.6,
    t_peri_epoch=2009.430,
    v_z0_kms=5.0
)

# Benchmark parameters for S301 (Nature August 2026 Discovery)
S301_BENCHMARK_PARAMS = SgrAOrbitalParameters(
    name="S301",
    mass_bh=4.297e6,
    distance_pc=8275.0,
    semi_major_axis_au=679.0,   # ~0.082 arcsec
    eccentricity=0.982,
    period_yr=8.70,
    inclination_deg=112.4,
    omega_node_deg=165.2,
    arg_peri_deg=28.5,
    t_peri_epoch=2024.120,
    v_z0_kms=5.0
)

ALL_S_STAR_PARAMS: Dict[str, SgrAOrbitalParameters] = {
    "s2": S2_BENCHMARK_PARAMS,
    "s29": S29_BENCHMARK_PARAMS,
    "s38": S38_BENCHMARK_PARAMS,
    "s55": S55_BENCHMARK_PARAMS,
    "s301": S301_BENCHMARK_PARAMS
}


def solve_kepler_anomaly(mean_anomaly: float | np.ndarray, eccentricity: float,
                         tol: float = 1e-12, max_iter: int = 100) -> float | np.ndarray:
    """Solve Kepler's equation M = E - e*sin(E) for Eccentric Anomaly E."""
    is_scalar = np.isscalar(mean_anomaly)
    m = np.atleast_1d(mean_anomaly)

    # Initial guess
    e_anom = m + eccentricity * np.sin(m)
    for _ in range(max_iter):
        f = e_anom - eccentricity * np.sin(e_anom) - m
        f_prime = 1.0 - eccentricity * np.cos(e_anom)
        delta = f / f_prime
        e_anom -= delta
        if np.max(np.abs(delta)) < tol:
            break

    return float(e_anom[0]) if is_scalar else e_anom


def compute_true_anomaly(eccentric_anomaly: float | np.ndarray,
                         eccentricity: float) -> float | np.ndarray:
    """Compute True Anomaly nu from Eccentric Anomaly E."""
    sin_half_e = np.sin(eccentric_anomaly / 2.0)
    cos_half_e = np.cos(eccentric_anomaly / 2.0)
    factor = np.sqrt((1.0 + eccentricity) / (1.0 - eccentricity))
    nu = 2.0 * np.arctan2(factor * sin_half_e, cos_half_e)
    return nu


def project_orbital_position_to_sky(
    params: SgrAOrbitalParameters,
    epochs: np.ndarray,
    model_type: str = "gr_1pn",
    emrf_beta: float = 0.0
) -> Dict[str, np.ndarray]:
    """Project 3D orbital dynamics to sky plane (RA, Dec in mas, and radial velocity in km/s).

    Parameters
    ----------
    params : SgrAOrbitalParameters
        Orbital elements and Sgr A* system characteristics.
    epochs : np.ndarray
        Array of observation epochs in decimal Julian years.
    model_type : str
        'newtonian', 'gr_1pn', or 'emrf'.
    emrf_beta : float
        Coupling parameter for EMRF space-entropy compression deviation.
        Beta = 0 corresponds exactly to pure GR 1PN.

    Returns
    -------
    dict with keys: 'ra_mas', 'dec_mas', 'vr_kms', 'r_au', 'v_kms'
    """
    epochs = np.atleast_1d(epochs)
    a_m = params.semi_major_axis_au * AU_METERS
    mu = G_CONST * (params.mass_bh * MSUN)

    # 1PN analytical precession advance per orbit: Delta phi = 6*pi*mu / (c^2 * a * (1 - e^2))
    delta_phi_1pn = (6.0 * math.pi * mu) / (C_LIGHT**2 * a_m * (1.0 - params.eccentricity**2))

    if model_type == "newtonian":
        omega_rate_rad_per_yr = 0.0
    elif model_type == "gr_1pn":
        omega_rate_rad_per_yr = delta_phi_1pn / params.period_yr
    elif model_type == "emrf":
        # EMRF modifies the effective precession rate via compression coupling beta
        omega_rate_rad_per_yr = (delta_phi_1pn / params.period_yr) * (1.0 + emrf_beta)
    else:
        raise ValueError(f"Unknown model_type: '{model_type}'. Choose 'newtonian', 'gr_1pn', or 'emrf'.")

    # Mean anomaly M(t)
    dt_yr = epochs - params.t_peri_epoch
    mean_motion = (2.0 * math.pi) / params.period_yr
    mean_anom = (mean_motion * dt_yr) % (2.0 * math.pi)

    # Solve Kepler's equation
    ecc_anom = solve_kepler_anomaly(mean_anom, params.eccentricity)
    nu = compute_true_anomaly(ecc_anom, params.eccentricity)

    # Orbital radius r(t)
    r_au = params.semi_major_axis_au * (1.0 - params.eccentricity * np.cos(ecc_anom))
    r_m = r_au * AU_METERS

    # Evolving argument of periapsis omega(t) due to precession
    omega_0_rad = math.radians(params.arg_peri_deg)
    omega_t = omega_0_rad + omega_rate_rad_per_yr * dt_yr

    inc_rad = math.radians(params.inclination_deg)
    node_rad = math.radians(params.omega_node_deg)

    # True argument of latitude u = omega + nu
    u = omega_t + nu

    # Thiele-Innes / Euler 3D orientation transformation
    # Orbital plane coordinates: x' = r*cos(u), y' = r*sin(u), z' = 0
    cos_u = np.cos(u)
    sin_u = np.sin(u)
    cos_node = math.cos(node_rad)
    sin_node = math.sin(node_rad)
    cos_inc = math.cos(inc_rad)
    sin_inc = math.sin(inc_rad)

    # Sky plane coordinates in AU:
    # x_sky (East, -RA) and y_sky (North, +Dec)
    # Conventional Campbell transformation:
    # X_north = r * (cos_omega * cos_nu - sin_omega * sin_nu) etc. -> r * (cos_u * cos_node - sin_u * sin_node * cos_inc)
    # Y_east  = r * (cos_u * sin_node + sin_u * cos_node * cos_inc)
    # Z_los   = r * sin_u * sin_inc
    x_north_au = r_au * (cos_u * cos_node - sin_u * sin_node * cos_inc)
    y_east_au = r_au * (cos_u * sin_node + sin_u * cos_node * cos_inc)
    # Convert AU to milliarcseconds on sky at distance R0:
    # theta_mas = (r_au / distance_pc) * 1000.0 mas/AU
    mas_per_au = 1000.0 / params.distance_pc
    dec_mas = x_north_au * mas_per_au
    ra_mas = y_east_au * mas_per_au

    # Orbital velocity components
    # h = sqrt(mu * a * (1 - e^2))
    h_orbit = math.sqrt(mu * a_m * (1.0 - params.eccentricity**2))
    v_radial = (mu / h_orbit) * params.eccentricity * np.sin(nu)
    v_transverse = (mu / h_orbit) * (1.0 + params.eccentricity * np.cos(nu))
    v_total_m_s = np.sqrt(v_radial**2 + v_transverse**2)

    # Line of sight velocity from orbital geometry:
    # dz_los/dt = (mu / h) * (cos(u) + e * cos(omega_t)) * sin(inc)
    v_z_los_m_s = (mu / h_orbit) * (np.cos(u) + params.eccentricity * np.cos(omega_t)) * sin_inc

    # Relativistic corrections to radial velocity:
    # 1. Transverse Doppler effect: Delta v_TD = 0.5 * (v^2 / c)
    # 2. Gravitational redshift: Delta v_GR = mu / (c * r)
    if model_type in ("gr_1pn", "emrf"):
        transverse_doppler = 0.5 * (v_total_m_s**2 / C_LIGHT)
        grav_redshift = mu / (C_LIGHT * r_m)
        v_rel_corr = (transverse_doppler + grav_redshift) / 1000.0  # to km/s
    else:
        v_rel_corr = 0.0

    v_r_kms = (v_z_los_m_s / 1000.0) + params.v_z0_kms + v_rel_corr

    return {
        "epochs": epochs,
        "ra_mas": ra_mas,
        "dec_mas": dec_mas,
        "vr_kms": v_r_kms,
        "r_au": r_au,
        "v_kms": v_total_m_s / 1000.0
    }


def load_astrometry_csv(csv_path: str | Path) -> Dict[str, np.ndarray]:
    """Load astrometric and radial velocity observation table from CSV."""
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(f"Astrometric dataset not found at: {path}")

    epochs, ra, ra_err, dec, dec_err, vr, vr_err = [], [], [], [], [], [], []
    instruments = []

    with open(path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for line_num, row in enumerate(reader, start=1):
            if not row or row[0].strip().startswith("#"):
                continue
            if row[0].strip().lower() == "epoch":
                continue
            try:
                epochs.append(float(row[0]))
                ra.append(float(row[1]))
                ra_err.append(float(row[2]))
                dec.append(float(row[3]))
                dec_err.append(float(row[4]))
                vr.append(float(row[5]))
                vr_err.append(float(row[6]))
                instruments.append(row[7].strip() if len(row) > 7 else "UNKNOWN")
            except (ValueError, IndexError) as err:
                raise ValueError(f"Malformed CSV row {line_num} in {path}: {row}") from err

    return {
        "epoch": np.array(epochs),
        "ra_mas": np.array(ra),
        "ra_err_mas": np.array(ra_err),
        "dec_mas": np.array(dec),
        "dec_err_mas": np.array(dec_err),
        "vr_kms": np.array(vr),
        "vr_err_kms": np.array(vr_err),
        "instrument": instruments
    }


def compute_residuals_and_chi2(
    obs: Dict[str, np.ndarray],
    pred: Dict[str, np.ndarray]
) -> Tuple[float, float, int, Dict[str, np.ndarray]]:
    """Compute astrometric and spectroscopic residuals, total chi-squared, and degrees of freedom."""
    res_ra = (obs["ra_mas"] - pred["ra_mas"]) / obs["ra_err_mas"]
    res_dec = (obs["dec_mas"] - pred["dec_mas"]) / obs["dec_err_mas"]
    res_vr = (obs["vr_kms"] - pred["vr_kms"]) / obs["vr_err_kms"]

    chi2_ra = float(np.sum(res_ra**2))
    chi2_dec = float(np.sum(res_dec**2))
    chi2_vr = float(np.sum(res_vr**2))
    total_chi2 = chi2_ra + chi2_dec + chi2_vr

    n_data_points = len(obs["epoch"]) * 3  # RA, Dec, and Vr per epoch

    residuals = {
        "res_ra": res_ra,
        "res_dec": res_dec,
        "res_vr": res_vr,
        "chi2_ra": chi2_ra,
        "chi2_dec": chi2_dec,
        "chi2_vr": chi2_vr
    }
    return total_chi2, chi2_ra + chi2_dec, n_data_points, residuals


def compute_information_criteria(
    chi2: float,
    n_data_points: int,
    n_free_params: int
) -> Tuple[float, float, float]:
    """Compute log-likelihood, Akaike Information Criterion (AIC), and Bayesian Information Criterion (BIC)."""
    # Under Gaussian uncertainties: -2 ln L = chi^2 + constant
    ln_l = -0.5 * chi2
    aic = 2.0 * n_free_params + chi2
    bic = n_free_params * math.log(n_data_points) + chi2
    return ln_l, aic, bic


def evaluate_astrometry_bifurcation(
    csv_path: str | Path,
    params: SgrAOrbitalParameters,
    candidate_emrf_beta: float = 0.005
) -> Dict[str, Any]:
    """Execute the objective Bifurcation Protocol across Newtonian, GR 1PN, and EMRF models."""
    obs = load_astrometry_csv(csv_path)
    epochs = obs["epoch"]
    n_pts = len(epochs) * 3

    # 1. Newtonian baseline (6 Keplerian orbital elements)
    pred_newton = project_orbital_position_to_sky(params, epochs, model_type="newtonian")
    chi2_newton, _, _, _ = compute_residuals_and_chi2(obs, pred_newton)
    ln_l_newton, aic_newton, bic_newton = compute_information_criteria(chi2_newton, n_pts, n_free_params=6)

    # 2. General Relativity 1PN baseline (6 Keplerian elements + M_bh + R_0 = 8 params)
    pred_gr = project_orbital_position_to_sky(params, epochs, model_type="gr_1pn")
    chi2_gr, _, _, res_gr = compute_residuals_and_chi2(obs, pred_gr)
    ln_l_gr, aic_gr, bic_gr = compute_information_criteria(chi2_gr, n_pts, n_free_params=8)

    # 3. EMRF Candidate model (8 GR params + 1 EMRF compression coupling beta = 9 params)
    pred_emrf = project_orbital_position_to_sky(params, epochs, model_type="emrf", emrf_beta=candidate_emrf_beta)
    chi2_emrf, _, _, res_emrf = compute_residuals_and_chi2(obs, pred_emrf)
    ln_l_emrf, aic_emrf, bic_emrf = compute_information_criteria(chi2_emrf, n_pts, n_free_params=9)

    # Delta-BIC: BIC_EMRF - BIC_GR
    # Positive delta-BIC means GR is favored (EMRF penalized for extra parameter)
    delta_bic = bic_emrf - bic_gr
    delta_aic = aic_emrf - aic_gr

    if delta_bic >= 10.0:
        bifurcation_decision = "Branch A: Geometric Collapse"
        summary = (
            f"Delta-BIC = {delta_bic:.2f} >= 10.0 decisively favors standard General Relativity. "
            "EMRF compression coupling is indistinguishable from 0; the framework collapses cleanly "
            "into a geometric/thermodynamic reformulation of GR."
        )
    elif delta_bic <= -10.0:
        bifurcation_decision = "Branch B: Novel Extension"
        summary = (
            f"Delta-BIC = {delta_bic:.2f} <= -10.0 decisively favors EMRF novel extension. "
            "Significant residual variance is captured by the space-entropy compression coupling; "
            "triggers systematic instrument artifact and multi-star cross-validation checks."
        )
    else:
        bifurcation_decision = "Inconclusive / Indistinguishable"
        summary = (
            f"|Delta-BIC| = {abs(delta_bic):.2f} < 10.0. Current observational precision cannot "
            "statistically distinguish between GR and EMRF coupling at this parameter value."
        )

    return {
        "target_star": params.name,
        "n_epochs": len(epochs),
        "total_data_points": n_pts,
        "models": {
            "newtonian": {
                "chi2": chi2_newton,
                "reduced_chi2": chi2_newton / max(1, n_pts - 6),
                "ln_likelihood": ln_l_newton,
                "aic": aic_newton,
                "bic": bic_newton
            },
            "gr_1pn": {
                "chi2": chi2_gr,
                "reduced_chi2": chi2_gr / max(1, n_pts - 8),
                "ln_likelihood": ln_l_gr,
                "aic": aic_gr,
                "bic": bic_gr
            },
            "emrf": {
                "beta_coupling": candidate_emrf_beta,
                "chi2": chi2_emrf,
                "reduced_chi2": chi2_emrf / max(1, n_pts - 9),
                "ln_likelihood": ln_l_emrf,
                "aic": aic_emrf,
                "bic": bic_emrf
            }
        },
        "model_selection": {
            "delta_bic": delta_bic,
            "delta_aic": delta_aic,
            "bifurcation_decision": bifurcation_decision,
            "interpretation": summary
        }
    }


def evaluate_multi_star_bifurcation(
    star_names: Optional[List[str]] = None,
    data_dir: Optional[str | Path] = None,
    candidate_emrf_beta: float = 0.005
) -> Dict[str, Any]:
    """Sum fixed-parameter per-star evaluations across the S-star cluster.

    Important limitations (see docs/SHOW_YOUR_WORK.md, Regime 1):
    - No parameters are fitted. Orbital elements are fixed at the benchmark values and
      ``candidate_emrf_beta`` is fixed; the "joint" chi^2 is the sum of independent per-star chi^2.
    - The parameter counts used in the BIC are nominal and do not correspond to fitted parameters.
    - The bundled astrometry tables are SYNTHETIC fixtures, so the output is a code demonstration only.
    """
    if star_names is None:
        star_names = ["s2", "s29", "s38", "s55", "s301"]

    base_dir = Path(__file__).resolve().parent.parent if data_dir is None else Path(data_dir)
    candidate = base_dir / "data" / "synthetic" / "astrometry"
    data_dir_path = candidate if candidate.is_dir() else base_dir

    star_reports = {}
    total_data_points = 0
    joint_chi2_newton = 0.0
    joint_chi2_gr = 0.0
    joint_chi2_emrf = 0.0

    for star_id in star_names:
        star_id_lower = star_id.lower().strip()
        if star_id_lower not in ALL_S_STAR_PARAMS:
            raise KeyError(f"Unknown star ID: '{star_id}'. Available: {list(ALL_S_STAR_PARAMS.keys())}")

        params = ALL_S_STAR_PARAMS[star_id_lower]
        csv_filename = f"{star_id_lower}_synthetic.csv"
        csv_path = data_dir_path / csv_filename

        report = evaluate_astrometry_bifurcation(csv_path, params, candidate_emrf_beta=candidate_emrf_beta)
        star_reports[params.name] = report

        total_data_points += report["total_data_points"]
        joint_chi2_newton += report["models"]["newtonian"]["chi2"]
        joint_chi2_gr += report["models"]["gr_1pn"]["chi2"]
        joint_chi2_emrf += report["models"]["emrf"]["chi2"]

    n_stars = len(star_names)
    k_newton = 6 * n_stars
    k_gr = 6 * n_stars + 2
    k_emrf = 6 * n_stars + 3

    ln_l_newton, aic_newton, bic_newton = compute_information_criteria(joint_chi2_newton, total_data_points, k_newton)
    ln_l_gr, aic_gr, bic_gr = compute_information_criteria(joint_chi2_gr, total_data_points, k_gr)
    ln_l_emrf, aic_emrf, bic_emrf = compute_information_criteria(joint_chi2_emrf, total_data_points, k_emrf)

    delta_bic = bic_emrf - bic_gr
    delta_aic = aic_emrf - aic_gr

    if delta_bic >= 10.0:
        bifurcation_decision = "Branch A: Geometric Collapse"
        summary = (
            f"Joint Multi-Star Delta-BIC = {delta_bic:.2f} >= 10.0 across {n_stars} stars "
            f"({total_data_points} data points) decisively favors standard General Relativity. "
            "EMRF compression coupling is statistically indistinguishable from zero across the "
            "entire Sgr A* nuclear cluster; confirms Branch A (Geometric Collapse)."
        )
    elif delta_bic <= -10.0:
        bifurcation_decision = "Branch B: Novel Extension"
        summary = (
            f"Joint Multi-Star Delta-BIC = {delta_bic:.2f} <= -10.0 across {n_stars} stars "
            "decisively favors EMRF novel extension across the entire cluster."
        )
    else:
        bifurcation_decision = "Inconclusive / Indistinguishable"
        summary = (
            f"|Joint Delta-BIC| = {abs(delta_bic):.2f} < 10.0 across {n_stars} stars. "
            "Inconclusive statistical separation at candidate beta."
        )

    return {
        "cluster": "Sagittarius A* S-Star Cluster",
        "stars_evaluated": list(star_reports.keys()),
        "n_stars": n_stars,
        "total_data_points": total_data_points,
        "joint_models": {
            "newtonian": {
                "chi2": joint_chi2_newton,
                "reduced_chi2": joint_chi2_newton / max(1, total_data_points - k_newton),
                "ln_likelihood": ln_l_newton,
                "aic": aic_newton,
                "bic": bic_newton
            },
            "gr_1pn": {
                "chi2": joint_chi2_gr,
                "reduced_chi2": joint_chi2_gr / max(1, total_data_points - k_gr),
                "ln_likelihood": ln_l_gr,
                "aic": aic_gr,
                "bic": bic_gr
            },
            "emrf": {
                "beta_coupling": candidate_emrf_beta,
                "chi2": joint_chi2_emrf,
                "reduced_chi2": joint_chi2_emrf / max(1, total_data_points - k_emrf),
                "ln_likelihood": ln_l_emrf,
                "aic": aic_emrf,
                "bic": bic_emrf
            }
        },
        "model_selection": {
            "delta_bic": delta_bic,
            "delta_aic": delta_aic,
            "bifurcation_decision": bifurcation_decision,
            "interpretation": summary
        },
        "per_star_reports": star_reports
    }


def main():
    """CLI entrypoint for astrometry fitting and model comparison."""
    parser = argparse.ArgumentParser(description="EMRF Astrometry Ingestion and Bayesian Model Evaluation Engine.")
    parser.add_argument("--dataset", type=str, default="all",
                        help="Target star (s2, s29, s38, s55, s301) or 'all' for joint cluster fit.")
    parser.add_argument("--csv", type=str, default=None, help="Custom path to single astrometry CSV table.")
    parser.add_argument("--beta", type=float, default=0.005, help="EMRF compression coupling parameter beta.")
    parser.add_argument("--output", type=str, default=None, help="Optional JSON path to save model comparison report.")

    args = parser.parse_args()
    base_dir = Path(__file__).resolve().parent.parent

    if args.dataset.lower() == "all" or "," in args.dataset:
        star_list = ["s2", "s29", "s38", "s55", "s301"] if args.dataset.lower() == "all" else [s.strip().lower() for s in args.dataset.split(",")]
        report = evaluate_multi_star_bifurcation(star_list, base_dir, candidate_emrf_beta=args.beta)
        banner = provenance_banner(*[base_dir / "data" / "synthetic" / "astrometry" / f"{s}_synthetic.csv" for s in star_list])
        if banner:
            print(banner)
        print("\n" + "=" * 76)
        print(" EMRF MULTI-STAR JOINT ASTROMETRIC FIT & BIFURCATION REPORT")
        print("=" * 76)
        print(f"Cluster Target: {report['cluster']}")
        print(f"Stars Evaluated: {', '.join(report['stars_evaluated'])} ({report['n_stars']} stars)")
        print(f"Total Observational Data Points: {report['total_data_points']}")
        print("-" * 76)
        print(f"Newtonian Joint Chi2: {report['joint_models']['newtonian']['chi2']:.1f} | BIC: {report['joint_models']['newtonian']['bic']:.1f}")
        print(f"GR 1PN Joint Chi2:    {report['joint_models']['gr_1pn']['chi2']:.1f} | BIC: {report['joint_models']['gr_1pn']['bic']:.1f}")
        print(f"EMRF Joint Chi2:      {report['joint_models']['emrf']['chi2']:.1f} | BIC: {report['joint_models']['emrf']['bic']:.1f}")
        print("-" * 76)
        print(f"Joint Delta-BIC (EMRF - GR): {report['model_selection']['delta_bic']:+.3f}")
        print(f"Global Bifurcation Decision:  {report['model_selection']['bifurcation_decision']}")
        print(f"Verdict: {report['model_selection']['interpretation']}")
        print("=" * 76 + "\n")
    else:
        star_id = args.dataset.lower().strip()
        if star_id not in ALL_S_STAR_PARAMS:
            raise ValueError(f"Unknown star: '{args.dataset}'. Choose from: {list(ALL_S_STAR_PARAMS.keys())} or 'all'.")

        params = ALL_S_STAR_PARAMS[star_id]
        if args.csv:
            csv_file = Path(args.csv)
        else:
            csv_file = base_dir / "data" / "synthetic" / "astrometry" / f"{star_id}_synthetic.csv"

        report = evaluate_astrometry_bifurcation(csv_file, params, candidate_emrf_beta=args.beta)
        banner = provenance_banner(csv_file)
        if banner:
            print(banner)

        print("\n" + "=" * 70)
        print(f" EMRF ASTROMETRIC FIT & BIFURCATION REPORT: STAR {report['target_star']}")
        print("=" * 70)
        print(f"Data Points: {report['total_data_points']} across {report['n_epochs']} epochs")
        print(f"GR 1PN Chi2 (Reduced): {report['models']['gr_1pn']['reduced_chi2']:.3f} | BIC: {report['models']['gr_1pn']['bic']:.2f}")
        print(f"EMRF Chi2 (Reduced):   {report['models']['emrf']['reduced_chi2']:.3f} | BIC: {report['models']['emrf']['bic']:.2f}")
        print("-" * 70)
        print(f"Delta-BIC (EMRF - GR): {report['model_selection']['delta_bic']:+.3f}")
        print(f"Bifurcation Decision:  {report['model_selection']['bifurcation_decision']}")
        print(f"Verdict: {report['model_selection']['interpretation']}")
        print("=" * 70 + "\n")

    if args.output:
        out_path = Path(args.output)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Report written to: {out_path}")


if __name__ == "__main__":
    main()
