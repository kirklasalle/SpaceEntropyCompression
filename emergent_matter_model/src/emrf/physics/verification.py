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
    return {
        "evidence_class": "software",
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
