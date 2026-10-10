"""Audited physical constants used at EMRF scientific boundaries."""

from __future__ import annotations

import math
from dataclasses import dataclass

import astropy.units as u
from astropy.units import Quantity


@dataclass(frozen=True)
class ScientificConstant:
    symbol: str
    value: float
    unit: u.UnitBase
    uncertainty: float
    reference: str
    exact: bool

    @property
    def quantity(self) -> Quantity:
        return self.value * self.unit


CODATA_2022_REFERENCE = (
    "NIST CODATA 2022, https://physics.nist.gov/cuu/Constants/"
)

SPEED_OF_LIGHT = ScientificConstant(
    "c",
    299_792_458.0,
    u.m / u.s,
    0.0,
    CODATA_2022_REFERENCE,
    True,
)
GRAVITATIONAL_CONSTANT = ScientificConstant(
    "G",
    6.67430e-11,
    u.m**3 / (u.kg * u.s**2),
    0.00015e-11,
    CODATA_2022_REFERENCE,
    False,
)
PLANCK_CONSTANT = ScientificConstant(
    "h",
    6.62607015e-34,
    u.J * u.s,
    0.0,
    CODATA_2022_REFERENCE,
    True,
)
BOLTZMANN_CONSTANT = ScientificConstant(
    "k_B",
    1.380649e-23,
    u.J / u.K,
    0.0,
    CODATA_2022_REFERENCE,
    True,
)

HBAR = (PLANCK_CONSTANT.quantity / (2.0 * math.pi)).to(u.J * u.s)

CODATA_2022 = {
    item.symbol: item
    for item in (
        SPEED_OF_LIGHT,
        GRAVITATIONAL_CONSTANT,
        PLANCK_CONSTANT,
        BOLTZMANN_CONSTANT,
    )
}

__all__ = [
    "BOLTZMANN_CONSTANT",
    "CODATA_2022",
    "CODATA_2022_REFERENCE",
    "GRAVITATIONAL_CONSTANT",
    "HBAR",
    "PLANCK_CONSTANT",
    "SPEED_OF_LIGHT",
    "ScientificConstant",
]
