"""Comprehensive Unit Test Suite for the Three Research Horizons.

Tests:
1. JWST Cosmic Dawn Engine (z = 8 - 15 galaxy collapse acceleration)
2. Black Hole Horizon Entropy Engine (Bekenstein-Hawking area law derivation)
3. Quantum Vibrational Compression Engine (soliton rest mass emergence)
"""

import math
import pytest
import numpy as np
from jwst_highz_early_galaxies import (
    JWSTCosmicDawnEngine,
    JWST_BENCHMARKS,
    EarlyGalaxyObservation,
)
from black_hole_horizon_entropy import (
    BlackHoleEntropyEngine,
    BH_BENCHMARKS,
    BlackHoleBenchmark,
)
from quantum_vibrational_compression import (
    QuantumVibrationalEngine,
    PARTICLE_BENCHMARKS,
    FundamentalParticleBenchmark,
)


# ==============================================================================
# 1. JWST COSMIC DAWN & HIGH-Z GALAXY COLLAPSE TESTS
# ==============================================================================

class TestJWSTCosmicDawn:
    """Test suite for high-z accelerated baryonic collapse under EMRF."""

    @pytest.fixture
    def engine(self):
        return JWSTCosmicDawnEngine()

    def test_hubble_parameter_scaling(self, engine):
        """H(z) must scale as (1+z)^(3/2) in matter-dominated era."""
        h0 = engine.h0_si
        h10 = engine.hubble_parameter(10.0)
        h14 = engine.hubble_parameter(14.32)
        assert h10 > 18.0 * h0
        assert h14 > 30.0 * h0
        assert h14 > h10

    def test_horizon_acceleration_boost(self, engine):
        """a_0(z) at z=14.32 must be ~25-35x greater than a_0(0)."""
        boost_14 = engine.acceleration_boost_factor(14.32)
        assert 25.0 <= boost_14 <= 35.0
        a0_14 = engine.horizon_acceleration(14.32)
        assert a0_14 > 3.0e-9 # m/s^2

    def test_cosmic_age_monotonicity(self, engine):
        """Cosmic age must decrease with increasing redshift."""
        t0 = engine.cosmic_time_myr(0.0)
        t10 = engine.cosmic_time_myr(10.0)
        t14 = engine.cosmic_time_myr(14.32)
        assert 13500.0 < t0 < 14000.0 # ~13.8 Gyr
        assert 400.0 < t10 < 520.0    # ~460 Myr
        assert 250.0 < t14 < 350.0    # ~290 Myr
        assert t14 < t10 < t0

    def test_baryonic_collapse_time_acceleration(self, engine):
        """EMRF collapse time must be strictly faster than Newtonian collapse."""
        for obs in JWST_BENCHMARKS:
            t_newt = engine.baryonic_collapse_time_myr(
                gas_mass_msun=obs.stellar_mass_msun * 3.0,
                radius_pc=obs.radius_pc * 4.0,
                z=obs.redshift,
                use_emrf=False
            )
            t_emrf = engine.baryonic_collapse_time_myr(
                gas_mass_msun=obs.stellar_mass_msun * 3.0,
                radius_pc=obs.radius_pc * 4.0,
                z=obs.redshift,
                use_emrf=True
            )
            assert t_emrf < t_newt
            # EMRF collapse time must easily fit within cosmic age
            t_age = engine.cosmic_time_myr(obs.redshift)
            assert t_emrf < t_age

    def test_evaluate_jwst_suite_resolves_all(self, engine):
        """All 4 JWST benchmarks must be resolved without unphysical star formation."""
        suite = engine.evaluate_jwst_suite()
        assert len(suite) == 4
        for name, data in suite.items():
            assert data["resolved_without_crisis"] == 1.0
            assert data["time_margin_emrf_myr"] > 100.0 # >100 Myr headroom before cosmic age


# ==============================================================================
# 2. BLACK HOLE HORIZON ENTROPY TESTS
# ==============================================================================

class TestBlackHoleHorizonEntropy:
    """Test suite for Bekenstein-Hawking area law derivation."""

    @pytest.fixture
    def engine(self):
        return BlackHoleEntropyEngine()

    def test_planck_scale_consistency(self, engine):
        """Verify fundamental Planck length and area scales."""
        assert 1.616e-35 < engine.ell_p < 1.617e-35
        assert 2.61e-70 < engine.planck_area < 2.62e-70
        assert engine.c_saturation > 1.0e69

    def test_schwarzschild_radius_scaling(self, engine):
        """r_s must scale linearly with mass."""
        rs_cygx1 = engine.schwarzschild_radius(21.2 * engine.M_SUN)
        rs_sgra = engine.schwarzschild_radius(4.297e6 * engine.M_SUN)
        assert 1.2e10 < rs_sgra < 1.35e10
        assert rs_sgra > 1e5 * rs_cygx1

    def test_lasalle_entropy_recovers_bekenstein_hawking(self, engine):
        """Derived LaSalle entropy must match exact Bekenstein-Hawking formula with < 0.1% error."""
        for bh in BH_BENCHMARKS:
            mass_kg = bh.mass_msun * engine.M_SUN
            s_lasalle, rel_err = engine.lasalle_compression_entropy(mass_kg)
            s_exact = engine.bekenstein_hawking_entropy_exact(mass_kg)
            assert rel_err < 1.0e-3
            assert math.isclose(s_lasalle, s_exact, rel_tol=1e-3)

    def test_hawking_temperature_inverse_mass(self, engine):
        """Hawking temperature must scale inversely with black hole mass."""
        t_primordial = engine.hawking_temperature_kelvin(1.0e-18 * engine.M_SUN)
        t_sgra = engine.hawking_temperature_kelvin(4.297e6 * engine.M_SUN)
        assert t_primordial > 1.0e10 # Hot micro-hole
        assert t_sgra < 1.0e-13      # Extremely cold macro-hole
        assert t_primordial > t_sgra


# ==============================================================================
# 3. QUANTUM VIBRATIONAL COMPRESSION & MASS EMERGENCE TESTS
# ==============================================================================

class TestQuantumVibrationalCompression:
    """Test suite for microscopic standing-wave mass emergence."""

    @pytest.fixture
    def engine(self):
        return QuantumVibrationalEngine()

    def test_compton_scales_physical(self, engine):
        """Compton frequency and wavelength must match physical particle values."""
        for p in PARTICLE_BENCHMARKS:
            omega = engine.compton_frequency(p.rest_mass_kg)
            l_bar = engine.compton_wavelength(p.rest_mass_kg)
            energy_hbar_omega = engine.HBAR * omega
            energy_mc2 = p.rest_mass_kg * engine.c_squared
            assert math.isclose(energy_hbar_omega, energy_mc2, rel_tol=1e-12)
            assert math.isclose(l_bar * p.rest_mass_kg * engine.C, engine.HBAR, rel_tol=1e-12)

    def test_radial_soliton_profile_localization(self, engine):
        """Soliton spatial amplitude psi(r) must decay smoothly to zero at large r."""
        for p in PARTICLE_BENCHMARKS:
            r, psi, c_density = engine.solve_radial_soliton_profile(p.rest_mass_kg)
            assert psi[0] > psi[-1]
            assert c_density[0] > c_density[-1]
            assert c_density[-1] < 1e-3 * c_density[0]

    def test_emergent_mass_integral_recovers_particle_mass(self, engine):
        """Volume integral of compression density must recover particle rest mass."""
        for p in PARTICLE_BENCHMARKS:
            m_em, rel_err = engine.compute_emergent_mass_integral(p.rest_mass_kg)
            assert rel_err < 1e-5
            assert math.isclose(m_em, p.rest_mass_kg, rel_tol=1e-5)

    def test_evaluate_particle_suite(self, engine):
        """Evaluate full particle suite across electron, proton, Higgs."""
        suite = engine.evaluate_particle_suite()
        assert len(suite) == 3
        for name, data in suite.items():
            assert data["vibrational_synthesis_confirmed"] == 1.0
            assert data["thermodynamic_stability_locked"] == 1.0

    def test_soliton_thermodynamic_locking(self, engine):
        """Soliton must exhibit positive entropy gradient and dispersion balance."""
        for p in PARTICLE_BENCHMARKS:
            stab = engine.verify_soliton_thermodynamic_stability(p.rest_mass_kg)
            assert stab["positive_entropy_gradient_confirmed"] is True
            assert stab["thermodynamic_locking_verified"] is True
            assert stab["dispersion_balance_ratio"] > 0.0

    def test_confining_potential(self, engine):
        """Confining potential V(psi, S) must be positive-definite."""
        for p in PARTICLE_BENCHMARKS:
            r, psi, _ = engine.solve_radial_soliton_profile(p.rest_mass_kg)
            v = engine.confining_potential(r, psi, p.rest_mass_kg)
            assert np.all(v >= 0.0)
