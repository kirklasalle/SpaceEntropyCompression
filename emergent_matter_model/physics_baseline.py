"""Relativistic and celestial mechanics baseline module for EMRF.

Provides standard General Relativity and Newtonian gravity benchmarks:
1. Keplerian 2-body orbital solver (analytical Newtonian baseline).
2. First Post-Newtonian (1PN) Schwarzschild geodesic equations of motion.
3. Analytical Schwarzschild pericenter precession calculation.
4. Exact Kretschmann scalar curvature invariant K(r) = 48 G^2 M^2 / (c^4 r^6).

These baseline functions serve as the ground truth against which any
compression-to-matter model M(X,t) = k [C(X,t)/C0]^alpha is benchmarked
and falsified.
"""

from __future__ import annotations

import numpy as np

try:
    from emrf_error_access import emrf_errors
except ModuleNotFoundError as exc:
    if exc.name != "emrf_error_access":
        raise
    from emergent_matter_model.emrf_error_access import emrf_errors

ConvergenceError = emrf_errors().ConvergenceError
NumericalError = emrf_errors().NumericalError

# Standard Astronomical & Physical Constants (SI Units)
G: float = 6.67430e-11          # Gravitational constant [m^3 kg^-1 s^-2]
C_LIGHT: float = 299792458.0    # Speed of light [m s^-1]
SOLAR_MASS: float = 1.98847e30  # Solar mass [kg]
AU: float = 1.495978707e11      # Astronomical Unit [m]
YEAR_SEC: float = 31557600.0    # Julian year in seconds (365.25 days)

# Sgr A* Nominal Reference Parameters (GRAVITY Collaboration 2022/2026)
SGR_A_MASS: float = 4.297e6 * SOLAR_MASS   # ~4.3 million solar masses [kg]
SGR_A_DISTANCE: float = 8275.0 * 3.085677581e16  # 8.275 kpc in meters


def solve_kepler(
    mean_anomaly: float,
    eccentricity: float,
    tol: float = 1e-12,
    max_iter: int = 100,
) -> float:
    """Solve Kepler's equation M = E - e*sin(E) for Eccentric Anomaly E via Newton-Raphson.

    Parameters
    ----------
    mean_anomaly : float
        Mean anomaly in radians.
    eccentricity : float
        Orbital eccentricity (0 <= e < 1).
    tol : float, optional
        Convergence tolerance, default 1e-12.
    max_iter : int, optional
        Maximum iterations, default 100.

    Returns
    -------
    float
        Eccentric anomaly E in radians.
    """
    if not np.isfinite(mean_anomaly):
        raise NumericalError("Mean anomaly must be finite")
    if not np.isfinite(eccentricity) or not (0.0 <= eccentricity < 1.0):
        raise ValueError(f"Eccentricity must be in [0, 1), got {eccentricity}")
    if not np.isfinite(tol) or tol <= 0:
        raise ValueError("Tolerance must be finite and positive")
    if isinstance(max_iter, bool) or not isinstance(max_iter, int) or max_iter < 1:
        raise ValueError("max_iter must be a positive integer")

    # Standard starting estimate
    m = mean_anomaly % (2.0 * np.pi)
    e_curr = m if eccentricity < 0.8 else np.pi if m != 0 else 0.0

    for _ in range(max_iter):
        f = e_curr - eccentricity * np.sin(e_curr) - m
        f_prime = 1.0 - eccentricity * np.cos(e_curr)
        delta = f / f_prime
        e_curr -= delta
        if abs(delta) < tol:
            return float(e_curr)

    raise ConvergenceError(
        f"Kepler solver did not converge after {max_iter} iterations"
    )


def keplerian_orbit_2d(
    semi_major_axis: float,
    eccentricity: float,
    mass_central: float,
    times: np.ndarray,
    t0: float = 0.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Calculate 2D orbital trajectory under Newtonian 2-body Keplerian dynamics.

    Parameters
    ----------
    semi_major_axis : float
        Semi-major axis in meters (a > 0).
    eccentricity : float
        Orbital eccentricity (0 <= e < 1).
    mass_central : float
        Central mass in kg.
    times : np.ndarray
        Array of evaluation times in seconds.
    t0 : float, optional
        Pericenter passage epoch in seconds, default 0.0.

    Returns
    -------
    tuple of np.ndarray
        (x, y, vx, vy) orbital coordinates and velocities in meters and m/s.
    """
    times = np.asarray(times, dtype=float)
    if not np.isfinite(semi_major_axis) or semi_major_axis <= 0:
        raise ValueError("semi_major_axis must be finite and positive")
    if not np.isfinite(mass_central) or mass_central <= 0:
        raise ValueError("mass_central must be finite and positive")
    if times.ndim != 1 or not np.all(np.isfinite(times)) or not np.isfinite(t0):
        raise NumericalError("times and t0 must be finite")
    if not np.isfinite(eccentricity) or not 0.0 <= eccentricity < 1.0:
        raise ValueError("eccentricity must be finite and in [0, 1)")
    mu = G * mass_central
    mean_motion = np.sqrt(mu / (semi_major_axis ** 3))

    x_arr = np.empty_like(times, dtype=np.float64)
    y_arr = np.empty_like(times, dtype=np.float64)
    vx_arr = np.empty_like(times, dtype=np.float64)
    vy_arr = np.empty_like(times, dtype=np.float64)

    for i, t in enumerate(times):
        m = mean_motion * (t - t0)
        e_anom = solve_kepler(m, eccentricity)

        # True anomaly nu
        sin_nu = (
            np.sqrt(1.0 - eccentricity**2)
            * np.sin(e_anom)
            / (1.0 - eccentricity * np.cos(e_anom))
        )
        cos_nu = (np.cos(e_anom) - eccentricity) / (1.0 - eccentricity * np.cos(e_anom))
        nu = np.arctan2(sin_nu, cos_nu)

        r = semi_major_axis * (1.0 - eccentricity * np.cos(e_anom))

        # Position in orbital plane
        x = r * np.cos(nu)
        y = r * np.sin(nu)

        # Velocity in orbital plane
        h = np.sqrt(mu * semi_major_axis * (1.0 - eccentricity**2))
        vx = - (mu / h) * np.sin(nu)
        vy = (mu / h) * (np.cos(nu) + eccentricity)

        x_arr[i] = x
        y_arr[i] = y
        vx_arr[i] = vx
        vy_arr[i] = vy

    return x_arr, y_arr, vx_arr, vy_arr


def schwarzschild_1pn_acceleration(
    r_vec: np.ndarray,
    v_vec: np.ndarray,
    mass_central: float,
) -> np.ndarray:
    """Compute the 1st Post-Newtonian (1PN) Schwarzschild acceleration vector.

    Parameters
    ----------
    r_vec : np.ndarray
        Position vector [m], shape (2,) or (3,).
    v_vec : np.ndarray
        Velocity vector [m/s], same shape as r_vec.
    mass_central : float
        Central attractor mass in kg.

    Returns
    -------
    np.ndarray
        Acceleration vector [m/s^2] combining Newtonian gravity + 1PN correction.
    """
    r_vec = np.asarray(r_vec, dtype=float)
    v_vec = np.asarray(v_vec, dtype=float)
    if (
        r_vec.ndim != 1
        or r_vec.shape != v_vec.shape
        or r_vec.size not in {2, 3}
        or not np.all(np.isfinite(r_vec))
        or not np.all(np.isfinite(v_vec))
    ):
        raise NumericalError("r_vec and v_vec must be finite matching 2D or 3D vectors")
    if not np.isfinite(mass_central) or mass_central <= 0:
        raise ValueError("mass_central must be finite and positive")
    r = np.linalg.norm(r_vec)
    if r == 0.0:
        raise ZeroDivisionError("Distance r is zero (singularity).")

    mu = G * mass_central
    v2 = float(np.dot(v_vec, v_vec))
    r_dot_v = float(np.dot(r_vec, v_vec))

    # Newtonian acceleration
    a_newt = - (mu / (r ** 3)) * r_vec

    # 1PN Schwarzschild correction (Einstein-Infeld-Hoffmann formulation)
    # Increases attractive radial pull at close distances: - (4 mu^2 / (c^2 r^4)) * r_hat
    c2 = C_LIGHT ** 2
    pn_radial = - (mu / (c2 * (r ** 3))) * (4.0 * mu / r - v2) * r_vec
    pn_velocity = (4.0 * mu * r_dot_v / (c2 * (r ** 3))) * v_vec

    return a_newt + pn_radial + pn_velocity


def integrate_orbit_1pn(
    r0: np.ndarray,
    v0: np.ndarray,
    mass_central: float,
    t_span: tuple[float, float],
    dt: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Integrate 1PN Schwarzschild trajectory using 4th-order Runge-Kutta (RK4).

    Parameters
    ----------
    r0 : np.ndarray
        Initial position vector [m].
    v0 : np.ndarray
        Initial velocity vector [m/s].
    mass_central : float
        Central attractor mass [kg].
    t_span : tuple of float
        (t_start, t_end) in seconds.
    dt : float
        Time step in seconds.

    Returns
    -------
    tuple of np.ndarray
        (times, r_history, v_history) arrays of trajectory states.
    """
    r0 = np.asarray(r0, dtype=float)
    v0 = np.asarray(v0, dtype=float)
    t_start, t_end = t_span
    if (
        r0.ndim != 1
        or r0.shape != v0.shape
        or r0.size not in {2, 3}
        or not np.all(np.isfinite(r0))
        or not np.all(np.isfinite(v0))
    ):
        raise NumericalError("r0 and v0 must be finite matching 2D or 3D vectors")
    if not all(np.isfinite(value) for value in (mass_central, t_start, t_end, dt)):
        raise NumericalError("mass, time span and dt must be finite")
    if mass_central <= 0 or dt <= 0 or t_end <= t_start:
        raise ValueError("mass and dt must be positive and t_end must exceed t_start")
    times = np.arange(t_start, t_end, dt, dtype=float)
    if times.size == 0 or times[-1] != t_end:
        times = np.append(times, t_end)

    dim = len(r0)
    n_steps = len(times)
    r_history = np.zeros((n_steps, dim), dtype=np.float64)
    v_history = np.zeros((n_steps, dim), dtype=np.float64)

    r_curr = np.array(r0, dtype=np.float64)
    v_curr = np.array(v0, dtype=np.float64)

    r_history[0] = r_curr
    v_history[0] = v_curr

    for step in range(1, n_steps):
        step_dt = times[step] - times[step - 1]
        # RK4 step
        k1_r = v_curr
        k1_v = schwarzschild_1pn_acceleration(r_curr, v_curr, mass_central)

        k2_r = v_curr + 0.5 * step_dt * k1_v
        k2_v = schwarzschild_1pn_acceleration(
            r_curr + 0.5 * step_dt * k1_r, k2_r, mass_central
        )

        k3_r = v_curr + 0.5 * step_dt * k2_v
        k3_v = schwarzschild_1pn_acceleration(
            r_curr + 0.5 * step_dt * k2_r, k3_r, mass_central
        )

        k4_r = v_curr + step_dt * k3_v
        k4_v = schwarzschild_1pn_acceleration(
            r_curr + step_dt * k3_r, k4_r, mass_central
        )

        r_curr += (step_dt / 6.0) * (k1_r + 2.0 * k2_r + 2.0 * k3_r + k4_r)
        v_curr += (step_dt / 6.0) * (k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v)

        if not np.all(np.isfinite(r_curr)) or not np.all(np.isfinite(v_curr)):
            raise NumericalError(f"Orbit integration became non-finite at step {step}")

        r_history[step] = r_curr
        v_history[step] = v_curr

    return times, r_history, v_history


def schwarzschild_pericenter_advance_analytical(
    semi_major_axis: float,
    eccentricity: float,
    mass_central: float,
) -> float:
    """Calculate the exact 1PN Schwarzschild pericenter precession angle per revolution.

    Formula: Δφ = 6 π G M / [ c^2 a (1 - e^2) ]

    Parameters
    ----------
    semi_major_axis : float
        Semi-major axis in meters (a > 0).
    eccentricity : float
        Orbital eccentricity (0 <= e < 1).
    mass_central : float
        Central attractor mass in kg.

    Returns
    -------
    float
        Pericenter precession per revolution in radians.
    """
    if not np.isfinite(semi_major_axis) or semi_major_axis <= 0:
        raise ValueError(f"Semi-major axis must be positive, got {semi_major_axis}")
    if not np.isfinite(eccentricity) or not (0.0 <= eccentricity < 1.0):
        raise ValueError(f"Eccentricity must be in [0, 1), got {eccentricity}")
    if not np.isfinite(mass_central) or mass_central <= 0:
        raise ValueError("mass_central must be finite and positive")

    c2 = C_LIGHT ** 2
    delta_phi = (6.0 * np.pi * G * mass_central) / (c2 * semi_major_axis * (1.0 - eccentricity**2))
    return float(delta_phi)


def kretschmann_invariant(
    radial_distance: float | np.ndarray,
    mass_central: float,
) -> float | np.ndarray:
    """Calculate the exact Kretschmann scalar curvature invariant K(r) for Schwarzschild spacetime.

    Formula: K(r) = R^{abcd} R_{abcd} = 48 G^2 M^2 / (c^4 r^6)

    Parameters
    ----------
    radial_distance : float or np.ndarray
        Circumferential radial distance in meters (r > 0).
    mass_central : float
        Schwarzschild central mass in kg.

    Returns
    -------
    float or np.ndarray
        Kretschmann scalar in inverse meters to the fourth power [m^-4].
    """
    r = np.asarray(radial_distance, dtype=np.float64)
    if not np.all(np.isfinite(r)) or np.any(r <= 0):
        raise ValueError("Radial distance must be strictly positive.")
    if not np.isfinite(mass_central) or mass_central <= 0:
        raise ValueError("mass_central must be finite and positive")

    c4 = C_LIGHT ** 4
    k_val = (48.0 * (G ** 2) * (mass_central ** 2)) / (c4 * (r ** 6))
    return k_val if isinstance(radial_distance, np.ndarray) else float(k_val)
