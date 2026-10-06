"""Unit tests for Hamiltonian Ghost Freedom, Ostrogradsky Stability & Sound Speed Stress Test."""

import pytest
import numpy as np
from stress_test_stability_ghosts import (
    compute_quadratic_action_coefficients,
    evaluate_hamiltonian_stability,
)


class TestHamiltonianStability:
    def test_kinetic_coefficient_strictly_positive(self):
        """Kinetic coefficient A must be strictly positive across all regimes (ghost-free)."""
        accels = np.logspace(-14, 8, 100)
        A, _, _ = compute_quadratic_action_coefficients(accels)
        assert np.all(A > 0.0)
        assert np.min(A) > 0.5

    def test_sound_speed_strictly_subluminal_and_real(self):
        """Sound speed squared c_s^2 must be positive (Laplacian stable) and c_s <= c."""
        accels = np.logspace(-14, 8, 100)
        A, B, _ = compute_quadratic_action_coefficients(accels)
        cs_sq = B / A
        assert np.all(cs_sq > 0.0)
        cs = np.sqrt(cs_sq)
        assert np.all(cs <= 299792458.0 * 1.000001)

    def test_effective_mass_non_negative(self):
        """Effective mass squared M_eff^2 must be non-negative (tachyonic stable)."""
        accels = np.logspace(-14, 8, 100)
        _, _, M2 = compute_quadratic_action_coefficients(accels)
        assert np.all(M2 >= 0.0)

    def test_full_hamiltonian_stability_verdict(self):
        """Complete stability audit confirms framework is 100% ghost-free and stable."""
        report = evaluate_hamiltonian_stability()
        assert report["overall_stable"]
        assert report["ghost_free"]
        assert report["laplacian_stable"]
        assert report["causal_subluminal"]
        assert report["tachyonic_stable"]
        assert report["ostrogradsky_free"]
