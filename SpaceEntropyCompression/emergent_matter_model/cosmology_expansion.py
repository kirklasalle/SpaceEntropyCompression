"""Cosmological expansion engine for Emergent Matter Research Framework (EMRF).

Models late-time cosmic acceleration H(z) via spatial metric compression C(t)
and thermodynamic horizon entropy growth S(a), benchmarking against:
  1. Pantheon+ Type Ia Supernova Hubble Diagram (N=1,701, z in [0.001, 2.26])
  2. DESI 2024 Baryon Acoustic Oscillation (BAO) measurements (z in [0.29, 2.33])

Equations:
  rho_C = 1/2 A(S) \\dot{C}^2 + V(C,S)
  p_C   = 1/2 A(S) \\dot{C}^2 - V(C,S)
  w(z)  = w_0 + w_a * z / (1 + z)   [Chevallier-Polarski-Linder / DESI 2024]
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import os
import numpy as np
from scipy import integrate, optimize

C_LIGHT_KM_S = 299792.458  # Speed of light in km/s


@dataclass
class EMRFCosmologyParams:
    """Cosmological parameters for EMRF background expansion.

    In EMRF, spatial metric compression operates in two cosmological regimes:
      1. Clustered compression around matter structures (galaxies, halos):
         Omega_C_matter ~ 0.266, contributing to effective matter density Omega_m = Omega_b + Omega_C_matter ~ 0.315.
      2. Unclustered void compression (dark energy):
         Omega_C_void = 1 - Omega_m - Omega_r ~ 0.685, driving late-time acceleration with w(z) = w0 + wa * z / (1+z).
    """
    H0: float = 70.0               # km/s/Mpc
    Omega_b: float = 0.049         # Baryon matter density
    Omega_C_matter: float = 0.266  # Clustered geometric compression density
    Omega_r: float = 9.0e-5        # Radiation density
    w0: float = -0.99              # Present equation of state in cosmic voids
    wa: float = -0.14              # Dynamical entropy-growth evolution (DESI 2024)
    rd_Mpc: float = 147.5          # Sound horizon at drag epoch in Mpc

    @property
    def Omega_m(self) -> float:
        """Total effective non-relativistic matter density."""
        return self.Omega_b + self.Omega_C_matter

    @property
    def Omega_C_void(self) -> float:
        """Void spatial compression dark energy density parameter."""
        return max(0.0, 1.0 - self.Omega_m - self.Omega_r)

    @property
    def Omega_C(self) -> float:
        """Total geometric spatial compression (clustered + void)."""
        return self.Omega_C_matter + self.Omega_C_void


def E_z(z: np.ndarray, params: EMRFCosmologyParams) -> np.ndarray:
    """Dimensionless expansion rate E(z) = H(z) / H0.

    Dark energy density evolves as:
      f_DE(z) = (1 + z)^{3*(1 + w0 + wa)} * exp(-3 * wa * z / (1 + z))
    """
    z_arr = np.asarray(z, dtype=float)
    zp1 = 1.0 + z_arr
    
    # Radiation and Total Matter scaling (Baryons + Clustered Compression)
    rad_term = params.Omega_r * (zp1 ** 4)
    matter_term = params.Omega_m * (zp1 ** 3)
    
    # Void spatial compression dark energy density evolution
    exp_factor = np.exp(-3.0 * params.wa * (z_arr / zp1))
    de_term = params.Omega_C_void * (zp1 ** (3.0 * (1.0 + params.w0 + params.wa))) * exp_factor
    
    E2 = rad_term + matter_term + de_term
    return np.sqrt(np.maximum(E2, 1e-12))


def H_z(z: np.ndarray, params: EMRFCosmologyParams) -> np.ndarray:
    """Hubble parameter H(z) in km/s/Mpc."""
    return params.H0 * E_z(z, params)


def comoving_distance_Mpc(z: float, params: EMRFCosmologyParams) -> float:
    """Line-of-sight comoving distance chi(z) in Mpc."""
    if z <= 0.0:
        return 0.0
    
    def integrand(zp: float) -> float:
        return 1.0 / E_z(np.array([zp]), params)[0]

    val, _ = integrate.quad(integrand, 0.0, z, limit=100)
    return (C_LIGHT_KM_S / params.H0) * val


def luminosity_distance_Mpc(z: float, params: EMRFCosmologyParams) -> float:
    """Luminosity distance d_L(z) = (1 + z) * chi(z) in Mpc."""
    return (1.0 + z) * comoving_distance_Mpc(z, params)


def distance_modulus(z: float, params: EMRFCosmologyParams) -> float:
    """Theoretical distance modulus mu(z) = 5 * log10(d_L / 10 pc)."""
    dL = luminosity_distance_Mpc(z, params)
    if dL <= 0.0:
        return 0.0
    return 5.0 * np.log10(dL) + 25.0


def bao_observables(z: float, params: EMRFCosmologyParams) -> Dict[str, float]:
    """Compute BAO distance metrics at effective redshift z:

    - DM / rd: Comoving angular diameter distance over sound horizon
    - DH / rd: Hubble distance c / H(z) over sound horizon
    - DV / rd: Spherically averaged distance [z * DM^2 * DH]^(1/3) over sound horizon
    """
    chi = comoving_distance_Mpc(z, params)
    Ez = E_z(np.array([z]), params)[0]
    c_over_H = C_LIGHT_KM_S / (params.H0 * Ez)
    
    DM_over_rd = chi / params.rd_Mpc
    DH_over_rd = c_over_H / params.rd_Mpc
    DV = (z * (chi ** 2) * c_over_H) ** (1.0 / 3.0)
    DV_over_rd = DV / params.rd_Mpc
    
    return {
        "DM_over_rd": DM_over_rd,
        "DH_over_rd": DH_over_rd,
        "DV_over_rd": DV_over_rd,
    }


from pathlib import Path


def _resolve_cosmo_path(filepath: str) -> str:
    """Resolve file path relative to current dir, parent, or repo root."""
    if os.path.exists(filepath):
        return filepath
    parent = os.path.join("..", filepath)
    if os.path.exists(parent):
        return parent
    repo_root = Path(__file__).resolve().parent.parent
    candidate = repo_root / filepath
    if candidate.exists():
        return str(candidate)
    return filepath


def evaluate_pantheon_plus(
    params: EMRFCosmologyParams,
    filepath: str
) -> Dict[str, float]:
    """Evaluate chi2 and residuals against Pantheon+ Supernova sample."""
    filepath = _resolve_cosmo_path(filepath)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Pantheon+ data not found at {filepath}")
    
    data = []
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("z_hd"):
                continue
            parts = line.split(",")
            data.append((float(parts[0]), float(parts[1]), float(parts[2])))
    
    z_vals = [d[0] for d in data]
    mu_obs = np.array([d[1] for d in data])
    mu_err = np.array([d[2] for d in data])
    
    mu_model = np.array([distance_modulus(z, params) for z in z_vals])
    residuals = mu_obs - mu_model
    chi2 = float(np.sum((residuals / mu_err) ** 2))
    dof = len(data) - 4  # 4 free parameters (H0, Omega_b, w0, wa)
    chi2_red = chi2 / max(1, dof)
    rms_resid = float(np.sqrt(np.mean(residuals ** 2)))
    
    return {
        "n_points": len(data),
        "chi2": chi2,
        "dof": dof,
        "chi2_reduced": chi2_red,
        "rms_residual_mag": rms_resid,
    }


def evaluate_desi_bao(
    params: EMRFCosmologyParams,
    filepath: str
) -> Dict[str, float]:
    """Evaluate chi2 against DESI 2024 BAO measurements."""
    filepath = _resolve_cosmo_path(filepath)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"DESI BAO data not found at {filepath}")
    
    measurements = []
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("tracer"):
                continue
            parts = line.split(",")
            measurements.append({
                "tracer": parts[0],
                "z_eff": float(parts[1]),
                "observable": parts[2],
                "value": float(parts[3]),
                "error": float(parts[4]),
            })
    
    chi2 = 0.0
    for m in measurements:
        theo = bao_observables(m["z_eff"], params)
        obs_name = m["observable"]
        if obs_name in theo:
            val_theo = theo[obs_name]
            diff = (val_theo - m["value"]) / m["error"]
            chi2 += diff ** 2
    
    dof = len(measurements) - 2  # w0, wa
    chi2_red = chi2 / max(1, dof)
    
    return {
        "n_points": len(measurements),
        "chi2": float(chi2),
        "dof": dof,
        "chi2_reduced": float(chi2_red),
    }


def fit_joint_cosmology(
    pantheon_path: str,
    desi_path: str
) -> Tuple[EMRFCosmologyParams, Dict[str, float]]:
    """Jointly fit (H0, Omega_m, w0, wa) against Pantheon+ and DESI 2024."""
    def objective(x: np.ndarray) -> float:
        h0, om_m, w0, wa = x
        om_c_mat = max(0.0, om_m - 0.049)
        p = EMRFCosmologyParams(H0=h0, Omega_b=0.049, Omega_C_matter=om_c_mat, w0=w0, wa=wa)
        res_pan = evaluate_pantheon_plus(p, pantheon_path)
        res_desi = evaluate_desi_bao(p, desi_path)
        return res_pan["chi2"] + res_desi["chi2"]

    init_guess = [70.0, 0.315, -0.99, -0.14]
    bounds = [(65.0, 75.0), (0.25, 0.36), (-1.2, -0.8), (-0.5, 0.2)]
    
    opt = optimize.minimize(
        objective,
        init_guess,
        bounds=bounds,
        method="L-BFGS-B"
    )
    
    best_om_m = float(opt.x[1])
    best_params = EMRFCosmologyParams(
        H0=float(opt.x[0]),
        Omega_b=0.049,
        Omega_C_matter=max(0.0, best_om_m - 0.049),
        w0=float(opt.x[2]),
        wa=float(opt.x[3])
    )
    
    res_pan = evaluate_pantheon_plus(best_params, pantheon_path)
    res_desi = evaluate_desi_bao(best_params, desi_path)
    total_chi2 = res_pan["chi2"] + res_desi["chi2"]
    total_n = res_pan["n_points"] + res_desi["n_points"]
    dof = total_n - 4
    
    # Information criteria compared to fiducial flat LCDM (k=2 free params: H0, Om)
    aic = total_chi2 + 2.0 * 4
    bic = total_chi2 + np.log(total_n) * 4
    
    stats = {
        "total_chi2": total_chi2,
        "dof": dof,
        "chi2_reduced": total_chi2 / max(1, dof),
        "pantheon_chi2_red": res_pan["chi2_reduced"],
        "desi_chi2_red": res_desi["chi2_reduced"],
        "AIC": aic,
        "BIC": bic,
    }
    return best_params, stats
