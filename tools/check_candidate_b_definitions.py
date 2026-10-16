"""Benchmark diagnostics for Candidate B, not an empirical test or a selection.

This executes the conditional algebra recorded in the Candidate B model
contract on stipulated benchmark inputs: the fixed-volume local cell, the
mass dimensions of the brane Higgs portal, the one-circle Kaluza-Klein
reduction, its stability and mixing envelopes, and the paired reversible
energy exchange. No observational data are read, no likelihood is evaluated,
and no parameter value is selected or measured.
"""
from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Callable, Sequence
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = "docs/engineering/CANDIDATE_B_MODEL_CONTRACT_DRAFT_2026-10-13.md"

# Rounded natural-unit probe scales (GeV). They exercise the algebra only; the
# unmixed Higgs parameter is not the observed eigenmass and nothing is fitted.
PROBE_V_GEV = 246.0
PROBE_MH_GEV = 125.0
CMS_4L_WINDOW_GEV = (130.0, 3000.0)

# SI dimension exponents in the order (kg, m, s, K).
Dim = tuple[int, int, int, int]
JOULE: Dim = (1, 2, -2, 0)


def _dim(*factors: tuple[Dim, int]) -> Dim:
    total = [0, 0, 0, 0]
    for dimension, power in factors:
        for index, exponent in enumerate(dimension):
            total[index] += exponent * power
    return (total[0], total[1], total[2], total[3])


METRE: Dim = (0, 1, 0, 0)
SECOND: Dim = (0, 0, 1, 0)
KELVIN: Dim = (0, 0, 0, 1)


def _finite(value: float, name: str) -> None:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")


def _finite_positive(value: float, name: str) -> None:
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")


# ---------------------------------------------------------------------------
# Section 8: fixed-volume three-dimensional local cell
# ---------------------------------------------------------------------------

def local_cell_units() -> dict[str, Dim]:
    """Units implied by the contract's per-3-volume conventions."""
    energy_density = _dim((JOULE, 1), (METRE, -3))
    inertia = _dim((energy_density, 1), (SECOND, 2))
    damping = _dim((energy_density, 1), (SECOND, 1))
    return {
        "xi": (0, 0, 0, 0),
        "energy_density_u_C_V_C_u_th_u_drive_J": energy_density,
        "I_C": inertia,
        "Gamma_C": damping,
        "kinetic_I_C_xidot2": _dim((inertia, 1), (SECOND, -2)),
        "inertial_force_I_C_xiddot": _dim((inertia, 1), (SECOND, -2)),
        "damping_force_Gamma_C_xidot": _dim((damping, 1), (SECOND, -1)),
        "Q_C_Gamma_C_xidot2": _dim((damping, 1), (SECOND, -2)),
        "entropy_production_Q_C_over_T": _dim((damping, 1), (SECOND, -2), (KELVIN, -1)),
    }


def reduced_density_units(spatial_dimensions: int) -> dict[str, Dim]:
    """Integrating a D-volume density over compact extra lengths gives a 3D density."""
    if spatial_dimensions < 3:
        raise ValueError("spatial dimension D must be at least 3")
    extra = spatial_dimensions - 3
    bulk = _dim((JOULE, 1), (METRE, -spatial_dimensions))
    return {
        "bulk_density": bulk,
        "after_integrating_extra_lengths": _dim((bulk, 1), (METRE, extra)),
        "observed_3d_density": _dim((JOULE, 1), (METRE, -3)),
    }


def local_entropy_production_rate(damping: float, xi_rate: float, temperature: float) -> float:
    """Conditional thermal entropy-production density Gamma_C xi_dot^2 / T."""
    _finite(damping, "damping")
    _finite(xi_rate, "xi rate")
    _finite_positive(temperature, "temperature")
    return damping * xi_rate**2 / temperature


def _rk4(rhs: Callable[[float, np.ndarray], np.ndarray], state: np.ndarray,
         t_end: float, steps: int) -> list[tuple[float, np.ndarray]]:
    dt = t_end / steps
    t = 0.0
    history = [(t, state.copy())]
    for _ in range(steps):
        k1 = rhs(t, state)
        k2 = rhs(t + dt / 2, state + dt / 2 * k1)
        k3 = rhs(t + dt / 2, state + dt / 2 * k2)
        k4 = rhs(t + dt, state + dt * k3)
        state = state + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        t += dt
        history.append((t, state.copy()))
    return history


def integrate_local_cell(inertia: float, damping: float, stiffness: float,
                         drive_amplitude: float, drive_frequency: float,
                         temperature: float, t_end: float = 40.0,
                         steps: int = 40_000) -> dict:
    """Integrate I xi'' + Gamma xi' + V'(xi) = J with paired transfer ledgers.

    V_C = stiffness (xi - 1)^2 / 2 and J = drive_amplitude sin(omega t). The
    state is augmented with u_th and u_drive so that every ledger uses the same
    integrator stages; the remaining drift measures numerical error only.
    """
    _finite_positive(inertia, "inertia")
    _finite_positive(stiffness, "stiffness")
    _finite_positive(temperature, "temperature")
    for value, name in ((damping, "damping"), (drive_amplitude, "drive amplitude"),
                        (drive_frequency, "drive frequency")):
        _finite(value, name)

    def drive(t: float) -> float:
        return drive_amplitude * math.sin(drive_frequency * t)

    def rhs(t: float, y: np.ndarray) -> np.ndarray:
        xi, rate = y[0], y[1]
        force = drive(t) - damping * rate - stiffness * (xi - 1.0)
        return np.array([rate, force / inertia, damping * rate**2,
                         -drive(t) * rate, damping * rate**2 / temperature])

    history = _rk4(rhs, np.array([1.2, 0.0, 0.0, 0.0, 0.0]), t_end, steps)

    def total(y: np.ndarray) -> float:
        u_c = 0.5 * inertia * y[1]**2 + 0.5 * stiffness * (y[0] - 1.0)**2
        return float(u_c + y[2] + y[3])

    initial = total(history[0][1])
    drift = max(abs(total(y) - initial) for _, y in history)
    scale = max(abs(initial), max(abs(y[2]) + abs(y[3]) for _, y in history))
    rates = [local_entropy_production_rate(damping, float(y[1]), temperature)
             for _, y in history]
    return {
        "max_abs_ledger_drift_J_m3": drift,
        "relative_ledger_drift": drift / scale,
        "final_u_th_J_m3": float(history[-1][1][2]),
        "final_u_drive_J_m3": float(history[-1][1][3]),
        "integrated_entropy_production_J_m3_K": float(history[-1][1][4]),
        "min_entropy_production_rate": min(rates) + 0.0,
        "max_entropy_production_rate": max(rates) + 0.0,
    }


# ---------------------------------------------------------------------------
# Section 7.1: natural-unit mass dimensions of the brane Higgs portal
# ---------------------------------------------------------------------------

def portal_mass_dimensions(spatial_dimensions: int) -> dict[str, Fraction]:
    """Canonical mass dimensions for a bulk scalar in D+1 and a 3+1 brane."""
    if spatial_dimensions < 3:
        raise ValueError("spatial dimension D must be at least 3")
    bulk = Fraction(spatial_dimensions + 1)
    phi = (bulk - 2) / 2
    operator = Fraction(2)
    mu = 4 - phi - operator
    extra = spatial_dimensions - 3
    return {
        "bulk_lagrangian": bulk,
        "kinetic_term": 2 * phi + 2,
        "phi": phi,
        "f_phi": phi,
        "O_H": operator,
        "mu": mu,
        "g_xi": mu + phi,
        "mu_4_after_volume_reduction": mu + Fraction(extra, 2),
        "phi_zero_mode_4d": phi - Fraction(extra, 2),
    }


# ---------------------------------------------------------------------------
# Sections 5 and 10: one-circle geometry, projection and brane sampling
# ---------------------------------------------------------------------------

def circle_mode_values(radius: float, max_level: int, y: np.ndarray) -> dict[str, np.ndarray]:
    """Canonically normalized real Fourier modes on y ~ y + 2 pi R."""
    _finite_positive(radius, "radius")
    norm = 1.0 / math.sqrt(2 * math.pi * radius)
    modes = {"zero": np.full_like(y, norm, dtype=float)}
    for n in range(1, max_level + 1):
        modes[f"cos_{n}"] = math.sqrt(2) * norm * np.cos(n * y / radius)
        modes[f"sin_{n}"] = math.sqrt(2) * norm * np.sin(n * y / radius)
    return modes


def circle_mode_checks(radius: float = 1.0, max_level: int = 5, samples: int = 128) -> dict:
    y = np.linspace(0.0, 2 * math.pi * radius, samples, endpoint=False)
    modes = circle_mode_values(radius, max_level, y)
    names = list(modes)
    weight = 2 * math.pi * radius / samples
    gram = np.array([[float(np.sum(modes[a] * modes[b]) * weight) for b in names]
                     for a in names])
    at_brane = circle_mode_values(radius, max_level, np.array([0.0]))
    zero_value = float(at_brane["zero"][0])
    return {
        "max_gram_deviation_from_identity": float(np.max(np.abs(gram - np.eye(len(names))))),
        "sine_modes_at_brane_max_abs": max(abs(float(at_brane[f"sin_{n}"][0]))
                                           for n in range(1, max_level + 1)),
        "cosine_to_zero_mode_brane_ratio": [float(at_brane[f"cos_{n}"][0]) / zero_value
                                            for n in range(1, max_level + 1)],
        "reduced_coupling_factor_times_sqrt_2piR": zero_value * math.sqrt(2 * math.pi * radius),
    }


def brane_overlap_energy_density(mu_5: float, bulk_field: Callable[[float], float],
                                 higgs_operator: float, brane_y: float = 0.0) -> float:
    """Signed u_ov = mu_5 phi(x, y_brane) O_H; it samples the bulk only at the brane."""
    for value, name in ((mu_5, "mu_5"), (higgs_operator, "O_H"), (brane_y, "brane y")):
        _finite(value, name)
    return mu_5 * bulk_field(brane_y) * higgs_operator


def projection_checks(radius: float = 1.0) -> dict:
    x = (0.3, -1.2, 2.5)
    off_brane = (*x, math.pi * radius / 2)
    on_brane = (*x, 0.0)

    def sine_profile(y: float) -> float:
        return math.sin(y / radius)

    def cosine_profile(y: float) -> float:
        return math.cos(y / radius)

    operator = PROBE_V_GEV * 0.5 + 0.5**2 / 2
    return {
        "same_projected_point": off_brane[:3] == on_brane[:3],
        "same_bulk_point": off_brane == on_brane,
        "sine_profile_off_brane_value": sine_profile(off_brane[3]),
        "sine_profile_brane_overlap_energy": brane_overlap_energy_density(
            1.0, sine_profile, operator),
        "cosine_profile_brane_overlap_energy": brane_overlap_energy_density(
            1.0, cosine_profile, operator),
        "overlap_signs_for_h_minus_and_plus": [
            math.copysign(1.0, brane_overlap_energy_density(
                1.0, cosine_profile, PROBE_V_GEV * h + h**2 / 2)) for h in (-1.0, 1.0)],
    }


# ---------------------------------------------------------------------------
# Sections 10-12: KK spectrum, stability and mixing envelopes
# ---------------------------------------------------------------------------

def validate_benchmark_domain(radius: float, m5: float, cutoff: float,
                              higgs_mass: float = PROBE_MH_GEV) -> int:
    """Return N_Lambda after checking R>0, m5>0 and Lambda>=max(m5, m_h)."""
    _finite_positive(radius, "R")
    _finite_positive(m5, "m5")
    _finite_positive(cutoff, "cutoff Lambda")
    _finite_positive(higgs_mass, "m_h")
    if cutoff < max(m5, higgs_mass):
        raise ValueError("cutoff Lambda must satisfy Lambda >= max(m5, m_h)")
    return math.floor(radius * math.sqrt(cutoff**2 - m5**2))


def kk_masses(radius: float, m5: float, levels: int) -> np.ndarray:
    _finite_positive(radius, "R")
    _finite_positive(m5, "m5")
    n = np.arange(levels + 1, dtype=float)
    return np.sqrt(m5**2 + (n / radius) ** 2)


def kk_couplings(mu_4: float, levels: int) -> np.ndarray:
    _finite(mu_4, "mu_4")
    couplings = np.full(levels + 1, math.sqrt(2) * mu_4)
    couplings[0] = mu_4
    return couplings


def stability_sum(radius: float, m5: float, levels: int) -> float:
    n = np.arange(1, levels + 1, dtype=float)
    return float(1 / m5**2 + 2 * np.sum(1 / (m5**2 + (n / radius) ** 2)))


def stability_sum_infinite(radius: float, m5: float) -> float:
    _finite_positive(radius, "R")
    _finite_positive(m5, "m5")
    x = math.pi * m5 * radius
    return math.pi * radius / (m5 * math.tanh(x))


def stability_bound_mu4(radius: float, m5: float, levels: int | None,
                        higgs_mass: float = PROBE_MH_GEV, vev: float = PROBE_V_GEV) -> float:
    """Internal tree-level envelope |mu_4| < m_h / (v sqrt(S_stab)); levels=None is formal."""
    total = (stability_sum_infinite(radius, m5) if levels is None
             else stability_sum(radius, m5, levels))
    return higgs_mass / (vev * math.sqrt(total))


def mass_matrix(radius: float, m5: float, levels: int, mu_4: float,
                higgs_mass: float = PROBE_MH_GEV, vev: float = PROBE_V_GEV) -> np.ndarray:
    """Basis (h, phi_0, phi_1^c, ..., phi_N^c) with off-diagonal entries v mu_n."""
    masses = kk_masses(radius, m5, levels)
    matrix = np.diag(np.concatenate(([higgs_mass**2], masses**2)))
    matrix[0, 1:] = matrix[1:, 0] = vev * kk_couplings(mu_4, levels)
    return matrix


def low_energy_operator_coefficient(radius: float, m5: float, levels: int,
                                    mu_4: float) -> dict[str, float]:
    """Tree-level elimination of the tower: 0.5 b^T M_phi^-1 b versus 0.5 mu_4^2 S."""
    couplings = kk_couplings(mu_4, levels)
    tower = np.diag(kk_masses(radius, m5, levels) ** 2)
    return {
        "matrix_elimination": float(0.5 * couplings @ np.linalg.solve(tower, couplings)),
        "closed_form_finite": 0.5 * mu_4**2 * stability_sum(radius, m5, levels),
    }


def weak_mixing_ratio(radius: float, m5: float, levels: int, mu_4: float,
                      higgs_mass: float = PROBE_MH_GEV, vev: float = PROBE_V_GEV) -> float:
    gaps = higgs_mass**2 - kk_masses(radius, m5, levels) ** 2
    if np.any(gaps == 0):
        return math.inf
    return float(np.max(np.abs(vev * kk_couplings(mu_4, levels) / gaps)))


def mixing_sum(radius: float, m5: float, levels: int,
               higgs_mass: float = PROBE_MH_GEV) -> float:
    gaps = higgs_mass**2 - kk_masses(radius, m5, levels) ** 2
    if np.any(gaps == 0):
        raise ValueError("exact Higgs-KK degeneracy; use finite-matrix diagonalization")
    weights = np.full(levels + 1, 2.0)
    weights[0] = 1.0
    return float(np.sum(weights / gaps**2))


def perturbative_kappa_v(radius: float, m5: float, levels: int, mu_4: float,
                         max_ratio: float = 0.1, higgs_mass: float = PROBE_MH_GEV,
                         vev: float = PROBE_V_GEV) -> float:
    """(1 + epsilon_KK)^(-1/2), refused outside the declared weak-mixing domain."""
    ratio = weak_mixing_ratio(radius, m5, levels, mu_4, higgs_mass, vev)
    if not ratio < max_ratio:
        raise ValueError("outside weak-mixing domain; use exact finite-matrix diagonalization")
    epsilon = vev**2 * mu_4**2 * mixing_sum(radius, m5, levels, higgs_mass)
    return 1 / math.sqrt(1 + epsilon)


def exact_mixing(radius: float, m5: float, levels: int, mu_4: float,
                 higgs_mass: float = PROBE_MH_GEV, vev: float = PROBE_V_GEV) -> dict:
    matrix = mass_matrix(radius, m5, levels, mu_4, higgs_mass, vev)
    eigenvalues, vectors = np.linalg.eigh(matrix)
    higgs_components = vectors[0, :]
    index = int(np.argmax(np.abs(higgs_components)))
    return {
        "min_eigenvalue_GeV2": float(eigenvalues[0]),
        "higgs_like_kappa_v": float(abs(higgs_components[index])),
        "higgs_like_eigenmass_GeV": (float(math.sqrt(eigenvalues[index]))
                                     if eigenvalues[index] > 0 else None),
        "kappa_squared_sum_rule": float(np.sum(higgs_components**2)),
        "largest_two_kappa_squared": sorted((higgs_components**2).tolist())[-2:],
    }


def kappa_min_envelope(radius: float, m5: float, levels: int, kappa_min: float,
                       higgs_mass: float = PROBE_MH_GEV, vev: float = PROBE_V_GEV) -> float:
    """Conditional |mu_4| ceiling once a model-specific kappa_min is supplied."""
    if not (math.isfinite(kappa_min) and 0 < kappa_min < 1):
        raise ValueError("kappa_min must lie strictly between 0 and 1")
    return math.sqrt((kappa_min**-2 - 1) / (vev**2 * mixing_sum(radius, m5, levels, higgs_mass)))


def cms_window_levels(radius: float, m5: float, levels: int,
                      window: Sequence[float] = CMS_4L_WINDOW_GEV) -> list[int]:
    """Unmixed-mass preselection only; final applicability needs mixed states and widths."""
    low, high = window
    masses = kk_masses(radius, m5, levels)
    return [n for n, mass in enumerate(masses) if low <= mass <= high]


# ---------------------------------------------------------------------------
# Section 7.3: paired, reversible zero-mode/Higgs exchange (homogeneous toy)
# ---------------------------------------------------------------------------

def higgs_potential(h: float, higgs_mass: float = PROBE_MH_GEV, vev: float = PROBE_V_GEV) -> float:
    """Unitary-gauge V_H = lambda O_H^2 with lambda = m_h^2 / (2 v^2)."""
    operator = vev * h + h**2 / 2
    return higgs_mass**2 / (2 * vev**2) * operator**2


def zero_mode_bounded_below(m5: float, mu_4: float, higgs_mass: float = PROBE_MH_GEV,
                            vev: float = PROBE_V_GEV) -> bool:
    """V = lambda(O + mu_4 phi / 2 lambda)^2 + (m5^2/2 - mu_4^2/4 lambda) phi^2."""
    coupling = higgs_mass**2 / (2 * vev**2)
    return m5**2 / 2 - mu_4**2 / (4 * coupling) >= 0


def integrate_portal_exchange(m5: float, mu_4: float, phi_initial: float,
                              periods: float = 40.0, steps_per_period: int = 400,
                              higgs_mass: float = PROBE_MH_GEV,
                              vev: float = PROBE_V_GEV) -> dict:
    """Homogeneous zero mode phi and Higgs h with S_int = -mu_4 phi O_H.

    E_Sigma includes the portal interaction energy, as in the contract. The
    exchange integral is carried in the integrator state for consistency.
    """
    _finite_positive(m5, "m5")
    _finite(mu_4, "mu_4")
    _finite(phi_initial, "initial phi")
    coupling = higgs_mass**2 / (2 * vev**2)

    def operator(h: float) -> float:
        return vev * h + h**2 / 2

    def rhs(_t: float, y: np.ndarray) -> np.ndarray:
        h, h_rate, phi, phi_rate = y[:4]
        o_h = operator(h)
        h_force = -(2 * coupling * o_h + mu_4 * phi) * (vev + h)
        phi_force = -m5**2 * phi - mu_4 * o_h
        return np.array([h_rate, h_force, phi_rate, phi_force, mu_4 * o_h * phi_rate])

    def energies(y: np.ndarray) -> tuple[float, float]:
        h, h_rate, phi, phi_rate = (float(v) for v in y[:4])
        brane = 0.5 * h_rate**2 + higgs_potential(h, higgs_mass, vev) + mu_4 * phi * operator(h)
        scalar = 0.5 * phi_rate**2 + 0.5 * m5**2 * phi**2
        return brane, scalar

    slow_period = 2 * math.pi / min(m5, higgs_mass)
    fast_period = 2 * math.pi / max(m5, higgs_mass)
    t_end = periods * slow_period
    steps = int(math.ceil(t_end / fast_period * steps_per_period))
    start = np.array([0.0, 0.0, phi_initial, 0.0, 0.0])
    forward = _rk4(rhs, start, t_end, steps)
    brane_0, scalar_0 = energies(start)
    total_0 = brane_0 + scalar_0
    brane_errors, scalar_errors, total_errors, exchange = [], [], [], []
    for _, y in forward:
        brane, scalar = energies(y)
        brane_errors.append(abs(brane - brane_0 - y[4]))
        scalar_errors.append(abs(scalar - scalar_0 + y[4]))
        total_errors.append(abs(brane + scalar - total_0))
        exchange.append(float(y[4]))

    reversed_state = forward[-1][1].copy()
    reversed_state[[1, 3]] *= -1
    reversed_state[4] = 0.0
    backward = _rk4(rhs, reversed_state, t_end, steps)[-1][1]
    signs = np.sign(np.diff(exchange))
    return {
        "initial_total_energy_GeV4": total_0,
        "max_brane_ledger_error_GeV4": max(brane_errors),
        "max_scalar_ledger_error_GeV4": max(scalar_errors),
        "max_total_drift_GeV4": max(total_errors),
        "relative_total_drift": max(total_errors) / abs(total_0),
        "max_energy_delivered_to_brane_GeV4": max(exchange),
        "min_energy_delivered_to_brane_GeV4": min(exchange),
        "exchange_direction_reversals": int(np.count_nonzero(np.diff(signs[signs != 0]))),
        "time_reversal_return_error_GeV": float(np.max(np.abs(backward[[0, 2]] - start[[0, 2]]))),
        "bounded_below_for_zero_mode_truncation": zero_mode_bounded_below(
            m5, mu_4, higgs_mass, vev),
    }


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def _units_text(dimension: Dim) -> str:
    labels = ("kg", "m", "s", "K")
    parts = [f"{label}^{power}" for label, power in zip(labels, dimension, strict=True) if power]
    return " ".join(parts) if parts else "dimensionless"


def build_report() -> dict:
    units = local_cell_units()
    energy_density = units["energy_density_u_C_V_C_u_th_u_drive_J"]
    for key in ("kinetic_I_C_xidot2", "inertial_force_I_C_xiddot", "damping_force_Gamma_C_xidot"):
        if units[key] != energy_density:
            raise ArithmeticError(f"local-cell unit mismatch for {key}")
    reduced = {d: reduced_density_units(d) for d in (3, 4, 5, 6)}
    if any(r["after_integrating_extra_lengths"] != r["observed_3d_density"]
           for r in reduced.values()):
        raise ArithmeticError("extra-dimensional density reduction failed")

    local = {
        "dissipative": integrate_local_cell(2.0, 0.3, 5.0, 0.8, 1.3, 300.0),
        "conservative_gamma_zero": integrate_local_cell(2.0, 0.0, 5.0, 0.8, 1.3, 300.0),
        "negative_gamma_counterexample": integrate_local_cell(2.0, -0.05, 5.0, 0.8, 1.3, 300.0,
                                                              t_end=10.0, steps=10_000),
    }

    dimensions = {str(d): {k: str(v) for k, v in portal_mass_dimensions(d).items()}
                  for d in (3, 4, 5, 6, 9)}

    radius, m5, cutoff = 1 / 1000.0, 400.0, 5000.0
    levels = validate_benchmark_domain(radius, m5, cutoff)
    bound = stability_bound_mu4(radius, m5, levels)
    below = mass_matrix(radius, m5, levels, 0.99 * bound)
    above = mass_matrix(radius, m5, levels, 1.01 * bound)
    weak_mu4 = 0.05 * bound
    exact_weak = exact_mixing(radius, m5, levels, weak_mu4)
    kappa_probe = 0.99
    envelope = kappa_min_envelope(radius, m5, levels, kappa_probe)
    exact_at_envelope = exact_mixing(radius, m5, levels, envelope)

    conv_radius, conv_m5, conv_cutoff = 1 / 50.0, 100.0, 1.0e6
    conv_levels = validate_benchmark_domain(conv_radius, conv_m5, conv_cutoff)
    finite_sum = stability_sum(conv_radius, conv_m5, conv_levels)
    infinite_sum = stability_sum_infinite(conv_radius, conv_m5)
    mu4_infinite = stability_bound_mu4(conv_radius, conv_m5, None)
    mu5_infinite = PROBE_MH_GEV / PROBE_V_GEV * math.sqrt(
        2 * conv_m5 * math.tanh(math.pi * conv_m5 * conv_radius))

    degenerate_m5, degenerate_mu4 = 126.0, 1.0
    degenerate_levels = validate_benchmark_domain(radius, degenerate_m5, cutoff)
    degenerate_ratio = weak_mixing_ratio(radius, degenerate_m5, degenerate_levels, degenerate_mu4)
    degenerate_exact = exact_mixing(radius, degenerate_m5, degenerate_levels, degenerate_mu4)

    exchange_mu4 = 0.3 * stability_bound_mu4(radius, m5, 0)
    exchange = integrate_portal_exchange(m5, exchange_mu4, phi_initial=5.0)
    unstable_mu4 = 1.01 * m5 * PROBE_MH_GEV / PROBE_V_GEV

    return {
        "evidence_kind": "benchmark_algebra_and_toy_integration_not_observations",
        "contract": CONTRACT,
        "physical_model_implemented": False,
        "candidate_b_selected": True,
        "selection_basis": "Kirk's separate 2026-10-16 decision; not a result of these checks",
        "candidate_a_selection_changed": False,
        "parameters_selected_or_measured": False,
        "likelihood_evaluated": False,
        "observational_data_used": False,
        "assumptions": [
            "Local cell: fixed physical 3-volume, constant I_C, quadratic V_C, prescribed J(t)",
            "Entropy production uses the contract's conditional local-equilibrium identity",
            "Portal: Standard Model on a fixed flat 3+1 brane at y=0; real bulk scalar",
            "Geometry benchmark: flat R^{3,1} x S^1_R, one extra spatial dimension",
            "Natural units hbar=c=1; masses and inverse lengths in GeV",
            "Probe v=246 GeV and unmixed m_h=125 GeV are rounded algebra inputs, not fits",
            "R, m5, Lambda, mu_4 and kappa_min values are stipulated probes, not selections",
            "Exchange toy: spatially homogeneous zero mode and Higgs, no gravity or widths",
        ],
        "local_cell": {
            "units": {k: _units_text(v) for k, v in units.items()},
            "reduced_density_units": {d: {k: _units_text(v) for k, v in r.items()}
                                      for d, r in reduced.items()},
            "integrations": local,
            "conclusion": ("Paired ledgers conserve u_C+u_th+u_drive to integrator error; "
                           "entropy production is nonnegative only when Gamma_C>=0 and T>0"),
        },
        "portal_mass_dimensions": {
            "by_spatial_dimension_D": dimensions,
            "conclusion": ("[mu]=(5-D)/2 and [g_xi]=2 for every D; after volume reduction "
                           "the 4D coupling mu_4 has mass dimension 1"),
        },
        "circle_geometry": {
            "mode_checks": circle_mode_checks(),
            "projection": projection_checks(),
            "conclusion": ("Equal 3D projection is not bulk coincidence; sine modes and "
                           "off-brane support do not enter the y=0 brane coupling"),
        },
        "kk_benchmark": {
            "R_GeV_inverse": radius, "m5_GeV": m5, "Lambda_GeV": cutoff,
            "N_Lambda": levels,
            "unmixed_masses_GeV": kk_masses(radius, m5, levels).tolist(),
            "stability_bound_mu4_GeV": bound,
            "min_eigenvalue_at_0.99_bound_GeV2": float(np.linalg.eigvalsh(below)[0]),
            "min_eigenvalue_at_1.01_bound_GeV2": float(np.linalg.eigvalsh(above)[0]),
            "low_energy_operator": low_energy_operator_coefficient(radius, m5, levels, bound),
            "weak_mixing": {
                "mu4_GeV": weak_mu4,
                "ratio": weak_mixing_ratio(radius, m5, levels, weak_mu4),
                "perturbative_kappa_v": perturbative_kappa_v(radius, m5, levels, weak_mu4),
                "exact": exact_weak,
            },
            "kappa_min_probe": {
                "kappa_min_stipulated": kappa_probe,
                "mu4_envelope_GeV": envelope,
                "weak_mixing_ratio_at_envelope": weak_mixing_ratio(radius, m5, levels, envelope),
                "perturbative_kappa_at_envelope": perturbative_kappa_v(
                    radius, m5, levels, envelope, max_ratio=1.0),
                "exact_at_envelope": exact_at_envelope,
            },
            "cms_4l_window_preselected_levels": cms_window_levels(radius, m5, levels),
        },
        "infinite_tower_limit": {
            "R_GeV_inverse": conv_radius, "m5_GeV": conv_m5, "N_Lambda": conv_levels,
            "finite_S_stab": finite_sum, "closed_form_S_stab": infinite_sum,
            "relative_difference": abs(finite_sum - infinite_sum) / infinite_sum,
            "mu4_bound_GeV": mu4_infinite,
            "mu5_bound_GeV_half": mu5_infinite,
            "mu5_from_mu4_GeV_half": math.sqrt(2 * math.pi * conv_radius) * mu4_infinite,
            "mu4_bound_as_m5_to_zero": [stability_bound_mu4(conv_radius, m, None)
                                        for m in (1.0, 1e-2, 1e-4)],
        },
        "near_degeneracy": {
            "m5_GeV": degenerate_m5, "mu4_GeV": degenerate_mu4,
            "weak_mixing_ratio": degenerate_ratio,
            "perturbative_formula_refused": degenerate_ratio >= 0.1,
            "perturbative_kappa_if_forced": perturbative_kappa_v(
                radius, degenerate_m5, degenerate_levels, degenerate_mu4, max_ratio=math.inf),
            "exact": degenerate_exact,
        },
        "paired_exchange": {
            "m5_GeV": m5, "mu4_GeV": exchange_mu4, "phi_initial_GeV": 5.0,
            **exchange,
            "unstable_coupling_bounded_below": zero_mode_bounded_below(m5, unstable_mu4),
        },
        "conclusions": [
            "The fixed-volume local-cell equations are unit-consistent and conserve their "
            "paired ledgers; the entropy sign is an assumption-dependent identity",
            "A D-volume density becomes a 3D density only after integrating a declared "
            "extra-dimensional measure; changing units alone is not a reduction",
            "Portal mass dimensions are consistent for every D; g_xi always has dimension 2",
            "Projected 3D coincidence does not imply bulk coincidence or brane coupling",
            "The Schur stability envelope is exact for the truncated tree-level mass matrix",
            "The finite KK sum converges to the coth closed form; the bound vanishes as m5->0",
            "Integrating out the tower reproduces the mu_4^2 S_stab O_H^2 / 2 operator",
            "Perturbative kappa_V matches exact diagonalization only in the weak-mixing "
            "domain; near degeneracy it is refused and states share the Higgs component",
            "Mixing shifts the Higgs-like eigenmass away from the unmixed m_h parameter, so "
            "matching the observed 125 GeV state requires solving for that parameter",
            "The portal exchange is paired and reversible: it supplies no Gamma_C, no "
            "entropy production and no energy origin",
            "None of these results selects Candidate B, a parameter value or a coupling limit",
        ],
        "source_sha256": {
            str(Path(__file__).resolve().relative_to(ROOT)):
                hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
    }


def main() -> None:
    report = build_report()
    destination = ROOT / "results" / "candidate_b_definition_checks.json"
    destination.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Saved {destination}: benchmark diagnostics, not empirical evidence")
    print("Local-cell ledgers, portal dimensions, KK envelopes and paired exchange checked.")
    print("B is author-selected; these checks imply no parameter choice or empirical support.")


if __name__ == "__main__":
    main()
