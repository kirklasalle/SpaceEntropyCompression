"""Physics models and engines exposed through the EMRF package namespace."""

from .model import EmergentMatterModel
from .verification import (
    bekenstein_hawking_entropy,
    flat_lcdm_luminosity_distance,
    known_limit_report,
    ppn_light_deflection,
    schwarzschild_radius,
)

__all__ = [
    "EmergentMatterModel",
    "bekenstein_hawking_entropy",
    "flat_lcdm_luminosity_distance",
    "known_limit_report",
    "ppn_light_deflection",
    "schwarzschild_radius",
]
