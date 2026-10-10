"""Unit-aware independent reference calculations for physics verification."""

from __future__ import annotations

import math
from typing import TypedDict

import astropy.units as u
import numpy as np
from astropy.constants import M_sun, R_sun
from astropy.cosmology import FlatLambdaCDM
from astropy.units import Quantity, UnitConversionError
from scipy.integrate import quad

from emrf.core.errors import NumericalError, UnitError

from .constants import (
    BOLTZMANN_CONSTANT,
    GRAVITATIONAL_CONSTANT,
    HBAR,
    SPEED_OF_LIGHT,
)


class KnownLimitCheck(TypedDict):
    name: str
    measured: float
    expected: float
    unit: str
    relative_error: float
    relative_tolerance: float
    passed: bool
    reference: str
    evidence_class: str
    limitation: str | None


class KnownLimitReport(TypedDict):
    evidence_class: str
    constants_reference: str
    all_passed: bool
    checks: list[KnownLimitCheck]


def _positive_quantity(value: Quantity, unit: u.UnitBase, name: str) -> Quantity:
    if not isinstance(value, Quantity):
        raise UnitError(f"{name} must be an astropy Quantity")
    try:
        converted = value.to(unit)
    except UnitConversionError as exc:
        raise UnitError(f"{name} must be convertible to {unit}") from exc
    values = np.asarray(converted.value)
    if not np.all(np.isfinite(values)) or np.any(values <= 0):
        raise NumericalError(f"{name} must contain finite positive values")
    return converted


def schwarzschild_radius(mass: Quantity) -> Quantity:
    """Return ``2GM/c^2`` with a checked mass boundary."""
    checked_mass = _positive_quantity(mass, u.kg, "mass")
    radius = (
        2.0
        * GRAVITATIONAL_CONSTANT.quantity
        * checked_mass
        / SPEED_OF_LIGHT.quantity**2
    )
    return radius.to(u.m)


def ppn_light_deflection(
    mass: Quantity,
    impact_parameter: Quantity,
    *,
    gamma: float = 1.0,
) -> Quantity:
    """Return the first-order PPN deflection ``2(1+gamma)GM/(c^2 b)``."""
    checked_mass = _positive_quantity(mass, u.kg, "mass")
    checked_impact = _positive_quantity(impact_parameter, u.m, "impact_parameter")
    if not math.isfinite(gamma):
        raise NumericalError("gamma must be finite")
    angle = (
        2.0
        * (1.0 + gamma)
        * GRAVITATIONAL_CONSTANT.quantity
        * checked_mass
        / (SPEED_OF_LIGHT.quantity**2 * checked_impact)
    )
    return angle.to(u.rad, equivalencies=u.dimensionless_angles())


def bekenstein_hawking_entropy(mass: Quantity) -> Quantity:
    """Return the standard Bekenstein-Hawking entropy in joules per kelvin."""
    radius = schwarzschild_radius(mass)
    area = 4.0 * np.pi * radius**2
    entropy = (
        BOLTZMANN_CONSTANT.quantity
        * SPEED_OF_LIGHT.quantity**3
        * area
        / (4.0 * GRAVITATIONAL_CONSTANT.quantity * HBAR)
    )
    return entropy.to(u.J / u.K)


def flat_lcdm_luminosity_distance(
    redshift: float,
    hubble_constant: Quantity,
    omega_m: float,
) -> Quantity:
    """Compute a radiation-free flat-LCDM luminosity distance independently."""
    if (
        isinstance(redshift, bool)
        or not isinstance(redshift, (int, float))
        or not math.isfinite(redshift)
        or redshift < 0
    ):
        raise NumericalError("redshift must be finite and non-negative")
    if (
        isinstance(omega_m, bool)
        or not isinstance(omega_m, (int, float))
        or not math.isfinite(omega_m)
        or not 0.0 <= omega_m <= 1.0
    ):
        raise NumericalError("omega_m must be finite and in [0, 1]")
    checked_h0 = _positive_quantity(
        hubble_constant,
        u.km / (u.s * u.Mpc),
        "hubble_constant",
    )
    omega_lambda = 1.0 - omega_m

    def inverse_expansion(z_value: float) -> float:
        return 1.0 / math.sqrt(
            omega_m * (1.0 + z_value) ** 3 + omega_lambda
        )

    integral, error = quad(inverse_expansion, 0.0, float(redshift), epsabs=1e-12)
    if not math.isfinite(integral) or not math.isfinite(error):
        raise NumericalError("flat-LCDM distance integration produced a non-finite result")
    distance = (
        (1.0 + redshift)
        * SPEED_OF_LIGHT.quantity.to(u.km / u.s)
        / checked_h0
        * integral
    )
    return distance.to(u.Mpc)


def known_limit_report() -> KnownLimitReport:
    """Return a machine-readable certificate for the foundational known limits."""
    checks: list[KnownLimitCheck] = []

    def add_check(
        name: str,
        measured: float,
        expected: float,
        relative_tolerance: float,
        unit: str,
        reference: str,
        *,
        evidence_class: str = "software",
        limitation: str | None = None,
    ) -> None:
        measured = float(measured)
        expected = float(expected)
        relative_tolerance = float(relative_tolerance)
        relative_error = float(abs(measured - expected) / abs(expected))
        checks.append(
            {
                "name": name,
                "measured": measured,
                "expected": expected,
                "unit": unit,
                "relative_error": relative_error,
                "relative_tolerance": relative_tolerance,
                "passed": bool(relative_error <= relative_tolerance),
                "reference": reference,
                "evidence_class": evidence_class,
                "limitation": limitation,
            }
        )

    add_check(
        "solar Schwarzschild radius",
        schwarzschild_radius(M_sun).to_value(u.km),
        2.95325,
        2e-5,
        "km",
        "Schwarzschild solution, r_s = 2GM/c^2",
    )
    add_check(
        "solar-limb PPN light deflection",
        ppn_light_deflection(M_sun, R_sun).to_value(u.arcsec),
        1.7512,
        5e-4,
        "arcsec",
        "General relativity PPN gamma=1, first-order solar-limb limit",
    )
    add_check(
        "solar-mass Bekenstein-Hawking entropy",
        bekenstein_hawking_entropy(M_sun).to_value(u.J / u.K),
        1.44815e54,
        2e-6,
        "J/K",
        "Bekenstein-Hawking area law, S=k_B c^3 A/(4 G hbar)",
    )
    h0 = 70.0 * u.km / (u.s * u.Mpc)
    astropy_distance = FlatLambdaCDM(
        H0=h0,
        Om0=0.3,
        Tcmb0=0.0 * u.K,
    ).luminosity_distance(1.0)
    add_check(
        "flat-LCDM luminosity distance at z=1",
        flat_lcdm_luminosity_distance(1.0, h0, 0.3).to_value(u.Mpc),
        astropy_distance.to_value(u.Mpc),
        2e-11,
        "Mpc",
        "Astropy 6.1 FlatLambdaCDM independent implementation",
    )
    from cmb_acoustic_engine import EMRFCMBParams, acoustic_angular_scale, compute_acoustic_peaks
    from lensing_engine import (
        finite_path_point_mass_deflection,
        integrate_point_mass_deflection,
        point_mass_deflection_angle,
    )

    impact = R_sun.to_value(u.m)
    mass = M_sun.to_value(u.kg)
    add_check(
        "lensing point-mass deflection",
        point_mass_deflection_angle(mass, impact),
        ppn_light_deflection(M_sun, R_sun).to_value(u.rad),
        2e-15,
        "rad",
        "Independent unit-aware PPN gamma=1 reference",
    )
    limit = 20.0 * impact
    exact_finite_path = finite_path_point_mass_deflection(mass, impact, limit)
    ray_errors = [
        abs(
            integrate_point_mass_deflection(
                mass,
                impact,
                line_of_sight_limit_m=limit,
                intervals=intervals,
            )
            - exact_finite_path
        )
        for intervals in (256, 512, 1024)
    ]
    ray_orders = [
        math.log2(ray_errors[index] / ray_errors[index + 1])
        for index in range(2)
    ]
    add_check(
        "lensing ray integration convergence order",
        min(ray_orders),
        2.0,
        0.03,
        "order",
        "Composite trapezoidal rule second-order finite-path solution",
    )

    cmb_params = EMRFCMBParams()
    theta_star, _ = acoustic_angular_scale(cmb_params)
    cmb_peaks = compute_acoustic_peaks(cmb_params)
    add_check(
        "CMB acoustic angular scale against CAMB",
        100.0 * theta_star,
        1.0424541939952765,
        1.5e-3,
        "100 theta_star",
        "CAMB 1.6.0, flat Planck-like cosmology, generated 2026-10-10",
        evidence_class="illustrative",
        limitation=(
            "The EMRF acoustic engine is calibrated to Planck-scale values; "
            "agreement is a template consistency check, not an independent prediction."
        ),
    )
    for index, expected in enumerate((220.0, 536.0, 813.0), start=1):
        add_check(
            f"CMB TT peak {index} against CAMB",
            float(cmb_peaks[f"l_{index}"]),
            expected,
            4e-3,
            "multipole",
            "CAMB 1.6.0 unlensed scalar TT peak extraction",
            evidence_class="illustrative",
            limitation=(
                "Peak phase shifts are Planck-calibrated in the EMRF template; "
                "this is not a Boltzmann-equation derivation."
            ),
        )
    return {
        "evidence_class": "mixed",
        "constants_reference": "NIST CODATA 2022",
        "all_passed": all(bool(check["passed"]) for check in checks),
        "checks": checks,
    }


__all__ = [
    "bekenstein_hawking_entropy",
    "flat_lcdm_luminosity_distance",
    "known_limit_report",
    "ppn_light_deflection",
    "schwarzschild_radius",
]
