"""JWST High-Redshift Cosmic Dawn & Early Massive Galaxy Engine.

Models the accelerated baryonic collapse and early galaxy assembly in the
ultra-early universe (z = 8 - 15) under the LaSalle Spatial Ontology and EMRF.
Demonstrates how the epoch-dependent acceleration floor a_0(z) = c H(z) / (2 pi)
naturally resolves the "Impossible Early Galaxy" crisis (e.g., JADES-GS-z14-0)
without requiring unphysical star formation efficiencies or ad-hoc dark matter halos.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np


@dataclass(frozen=True)
class EarlyGalaxyObservation:
    """Observational parameters for high-redshift JWST galaxies."""
    name: str
    redshift: float
    m_uv: float           # Absolute UV magnitude
    stellar_mass_msun: float  # In solar masses
    radius_pc: float      # Effective radius in parsecs
    log_mass_err: float   # Uncertainty in log10(M_*)


# Observational benchmarks from JWST JADES and NIRSpec surveys
JWST_BENCHMARKS = [
    EarlyGalaxyObservation(
        name="JADES-GS-z14-0",
        redshift=14.32,
        m_uv=-20.80,
        stellar_mass_msun=5.0e8,
        radius_pc=260.0,
        log_mass_err=0.20,
    ),
    EarlyGalaxyObservation(
        name="JADES-GS-z14-1",
        redshift=13.90,
        m_uv=-18.90,
        stellar_mass_msun=1.1e8,
        radius_pc=210.0,
        log_mass_err=0.25,
    ),
    EarlyGalaxyObservation(
        name="GLASS-z12",
        redshift=12.11,
        m_uv=-20.60,
        stellar_mass_msun=1.0e9,
        radius_pc=450.0,
        log_mass_err=0.18,
    ),
    EarlyGalaxyObservation(
        name="GN-z11",
        redshift=10.60,
        m_uv=-21.50,
        stellar_mass_msun=1.3e9,
        radius_pc=600.0,
        log_mass_err=0.15,
    ),
]


class JWSTCosmicDawnEngine:
    """Computes early-universe expansion, horizon acceleration, and gas collapse timescales."""

    # Physical constants (SI units)
    C: float = 2.99792458e8         # Speed of light [m/s]
    G: float = 6.67430e-11          # Gravitational constant [m^3/(kg s^2)]
    M_SUN: float = 1.98847e30       # Solar mass [kg]
    KPC_TO_M: float = 3.08567758e19 # 1 kpc in meters
    PC_TO_M: float = 3.08567758e16  # 1 pc in meters
    MYR_TO_S: float = 3.15576e13    # 1 Myr in seconds

    # Cosmological parameters (Planck 2018 baseline)
    H0_KMSMPC: float = 67.4         # H_0 in km/s/Mpc
    OMEGA_M: float = 0.315          # Matter density parameter
    OMEGA_LAMBDA: float = 0.685     # Dark energy parameter
    OMEGA_B: float = 0.049          # Baryon density parameter

    def __init__(self, a0_0: float = 1.20e-10) -> None:
        """Initialize engine with present-day critical acceleration a_0(0)."""
        self.a0_0 = a0_0
        # Convert H_0 to SI units (s^-1)
        # 1 km/s/Mpc = 1000 m / (3.08567758e22 m) = 3.24077929e-20 s^-1
        self.h0_si = self.H0_KMSMPC * 3.24077929e-20

    def hubble_parameter(self, z: float) -> float:
        """Compute Hubble parameter H(z) in s^-1 at redshift z."""
        ez = math.sqrt(self.OMEGA_M * (1.0 + z)**3 + self.OMEGA_LAMBDA)
        return self.h0_si * ez

    def cosmic_time_myr(self, z: float) -> float:
        """Compute the age of the universe in Myr at redshift z."""
        factor = 2.0 / (3.0 * self.h0_si * math.sqrt(self.OMEGA_LAMBDA))
        arg = math.sqrt(self.OMEGA_LAMBDA / self.OMEGA_M) * (1.0 + z)**(-1.5)
        t_seconds = factor * math.asinh(arg)
        return t_seconds / self.MYR_TO_S

    def horizon_acceleration(self, z: float) -> float:
        """Compute the Gibbons-Hawking horizon acceleration a_0(z) = c H(z) / (2 pi)."""
        hz = self.hubble_parameter(z)
        return (self.C * hz) / (2.0 * math.pi)

    def acceleration_boost_factor(self, z: float) -> float:
        """Compute the ratio a_0(z) / a_0(0)."""
        return self.horizon_acceleration(z) / self.a0_0

    def jeans_mass_ratio_emrf_to_newton(self, z: float, g_bar: float = 1.0e-11) -> float:
        """Compute the Jeans mass suppression factor in the weak-field regime."""
        boost = self.horizon_acceleration(z) / g_bar
        if boost <= 1.0:
            return 1.0
        return float(boost**(-0.75))

    def baryonic_collapse_time_myr(
        self,
        gas_mass_msun: float,
        radius_pc: float,
        z: float,
        use_emrf: bool = True
    ) -> float:
        """Compute the free-fall and dissipation collapse timescale of a pristine baryonic cloud."""
        mass_kg = gas_mass_msun * self.M_SUN
        radius_m = radius_pc * self.PC_TO_M
        
        volume_m3 = (4.0 / 3.0) * math.pi * (radius_m**3)
        rho = mass_kg / volume_m3

        t_ff_newton_s = math.sqrt((3.0 * math.pi) / (32.0 * self.G * rho))
        
        if not use_emrf:
            return t_ff_newton_s / self.MYR_TO_S

        g_bar = (self.G * mass_kg) / (radius_m**2)
        a0_z = self.horizon_acceleration(z)

        g_eff = math.sqrt(g_bar**2 + a0_z * g_bar)
        acceleration_ratio = g_eff / g_bar

        t_ff_emrf_s = t_ff_newton_s / math.sqrt(acceleration_ratio)
        return t_ff_emrf_s / self.MYR_TO_S

    def evaluate_jwst_suite(self) -> Dict[str, Dict[str, float]]:
        """Evaluate all 4 JWST benchmarks under standard LambdaCDM vs EMRF."""
        results = {}
        for obs in JWST_BENCHMARKS:
            t_age = self.cosmic_time_myr(obs.redshift)
            a0_z = self.horizon_acceleration(obs.redshift)
            boost = self.acceleration_boost_factor(obs.redshift)
            
            t_coll_newton = self.baryonic_collapse_time_myr(
                gas_mass_msun=obs.stellar_mass_msun * 3.0,
                radius_pc=obs.radius_pc * 4.0,
                z=obs.redshift,
                use_emrf=False
            )
            t_coll_emrf = self.baryonic_collapse_time_myr(
                gas_mass_msun=obs.stellar_mass_msun * 3.0,
                radius_pc=obs.radius_pc * 4.0,
                z=obs.redshift,
                use_emrf=True
            )
            
            results[obs.name] = {
                "redshift": obs.redshift,
                "cosmic_age_myr": t_age,
                "a0_z_mps2": a0_z,
                "a0_boost_factor": boost,
                "collapse_time_newton_myr": t_coll_newton,
                "collapse_time_emrf_myr": t_coll_emrf,
                "time_margin_emrf_myr": t_age - t_coll_emrf,
                "resolved_without_crisis": float(t_coll_emrf < t_age),
            }
        return results
