"""Unit tests for EmergentMatterModel.

Covers:
  - Construction & validation
  - Curvature computation
  - Matter computation
  - Edge cases (C0=0, negative curvature, alpha != 1)
  - Grid simulation (brute-force and vectorised)
  - Convenience constructor
  - Backward-compatibility alias
"""

import numpy as np
import pytest

from model import EmergentMatterModel


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestConstruction:
    def test_basic(self):
        m = EmergentMatterModel(4, [1, 1, 1, 1])
        assert m.n_total == 4
        np.testing.assert_allclose(m.weights.sum(), 1.0)

    def test_weights_normalised(self):
        m = EmergentMatterModel(3, [2, 3, 5])
        np.testing.assert_allclose(m.weights, [0.2, 0.3, 0.5])

    def test_mismatched_weights_raises(self):
        with pytest.raises(ValueError, match="must equal n_total"):
            EmergentMatterModel(3, [1, 1])

    def test_from_spatial_and_entropy(self):
        m = EmergentMatterModel.from_spatial_and_entropy(
            3, [0.3, 0.4, 0.3], entropy_weight=0.2, k=2.0
        )
        assert m.n_total == 4
        assert m.k == 2.0
        np.testing.assert_allclose(m.weights.sum(), 1.0)

    def test_n_alias(self):
        m = EmergentMatterModel(4, [1, 1, 1, 1])
        assert m.n == m.n_total

    def test_repr(self):
        m = EmergentMatterModel(2, [1, 1])
        r = repr(m)
        assert "EmergentMatterModel" in r
        assert "n_total=2" in r


# ---------------------------------------------------------------------------
# Curvature
# ---------------------------------------------------------------------------

class TestCurvature:
    def test_uniform_weights_identity_funcs(self):
        """With equal weights and identity C_i(x)=x, curvature = mean(X)."""
        m = EmergentMatterModel(3, [1, 1, 1])
        c_funcs = [lambda x: x] * 3
        X = [1.0, 2.0, 3.0]
        result = m.curvature(X, c_funcs)
        np.testing.assert_allclose(result, 2.0)  # mean of 1,2,3

    def test_weighted(self):
        m = EmergentMatterModel(2, [3, 1])  # normalises to [0.75, 0.25]
        c_funcs = [lambda x: x, lambda x: x]
        result = m.curvature([4.0, 8.0], c_funcs)
        expected = 0.75 * 4.0 + 0.25 * 8.0  # 5.0
        np.testing.assert_allclose(result, expected)

    def test_nonlinear_funcs(self):
        m = EmergentMatterModel(2, [1, 1])
        c_funcs = [lambda x: x ** 2, lambda x: np.sin(x)]
        X = [3.0, 0.0]
        result = m.curvature(X, c_funcs)
        np.testing.assert_allclose(result, 0.5 * 9.0 + 0.5 * 0.0)


# ---------------------------------------------------------------------------
# Matter
# ---------------------------------------------------------------------------

class TestMatter:
    def test_basic(self):
        m = EmergentMatterModel(2, [1, 1], k=1.0, alpha=1.0, C0=1.0)
        c_funcs = [lambda x: x, lambda x: x]
        result = m.matter([2.0, 4.0], c_funcs)
        np.testing.assert_allclose(result, 3.0)  # curvature=3, k*(3/1)^1

    def test_k_scaling(self):
        m = EmergentMatterModel(2, [1, 1], k=5.0, alpha=1.0, C0=1.0)
        c_funcs = [lambda x: x, lambda x: x]
        result = m.matter([2.0, 2.0], c_funcs)
        np.testing.assert_allclose(result, 10.0)

    def test_alpha_power(self):
        m = EmergentMatterModel(2, [1, 1], k=1.0, alpha=2.0, C0=1.0)
        c_funcs = [lambda x: x, lambda x: x]
        result = m.matter([3.0, 3.0], c_funcs)
        np.testing.assert_allclose(result, 9.0)  # (3/1)^2

    def test_C0_normalisation(self):
        m = EmergentMatterModel(2, [1, 1], k=1.0, alpha=1.0, C0=2.0)
        c_funcs = [lambda x: x, lambda x: x]
        result = m.matter([4.0, 4.0], c_funcs)
        np.testing.assert_allclose(result, 2.0)  # 4/2 = 2

    def test_C0_zero_returns_nan(self):
        m = EmergentMatterModel(2, [1, 1], k=1.0, alpha=1.0, C0=0.0)
        c_funcs = [lambda x: x, lambda x: x]
        result = m.matter([1.0, 1.0], c_funcs)
        assert np.isnan(result)

    def test_negative_curvature_odd_alpha(self):
        """Negative curvature with alpha=1 → negative matter."""
        m = EmergentMatterModel(2, [1, 1], k=1.0, alpha=1.0, C0=1.0)
        c_funcs = [lambda x: x, lambda x: x]
        result = m.matter([-2.0, -4.0], c_funcs)
        np.testing.assert_allclose(result, -3.0)


# ---------------------------------------------------------------------------
# Grid simulation
# ---------------------------------------------------------------------------

class TestSimulateGrid:
    def test_shape(self):
        m = EmergentMatterModel(3, [1, 1, 1])
        X_grid = [np.linspace(0, 1, 5), np.linspace(0, 1, 6), np.linspace(0, 1, 3)]
        c_funcs = [lambda x: x] * 3
        M = m.simulate_grid(X_grid, c_funcs)
        assert M.shape == (5, 6, 3)

    def test_mismatched_grid_raises(self):
        m = EmergentMatterModel(3, [1, 1, 1])
        X_grid = [np.linspace(0, 1, 5), np.linspace(0, 1, 6)]  # only 2
        c_funcs = [lambda x: x] * 3
        with pytest.raises(ValueError, match="must equal n_total"):
            m.simulate_grid(X_grid, c_funcs)

    def test_values_match_pointwise(self):
        """Grid result at a specific index should match pointwise matter()."""
        m = EmergentMatterModel(2, [1, 1], k=2.0, alpha=1.5, C0=0.5)
        x = np.array([1.0, 2.0, 3.0])
        s = np.array([0.0, 0.5])
        c_funcs = [lambda x: x ** 2, lambda x: x + 1]
        M = m.simulate_grid([x, s], c_funcs)
        # Check (i=1, j=0) → X=[2.0, 0.0]
        expected = m.matter([2.0, 0.0], c_funcs)
        np.testing.assert_allclose(M[1, 0], expected)


class TestSimulateGridVectorized3D:
    def test_shape(self):
        m = EmergentMatterModel(4, [1, 1, 1, 1])
        grids = [np.linspace(-1, 1, 10)] * 4
        c_funcs = [lambda x: x] * 4
        M = m.simulate_grid_vectorized_3d(grids, c_funcs)
        assert M.shape == (10, 10, 10, 10)

    def test_matches_brute_force(self):
        """Vectorised path must produce identical results to brute force."""
        m = EmergentMatterModel(4, [0.3, 0.3, 0.2, 0.2], k=1.5, alpha=1.2, C0=0.8)
        x = np.linspace(-1, 1, 5)
        y = np.linspace(-1, 1, 6)
        z = np.linspace(-1, 1, 4)
        s = np.linspace(0, 1, 3)
        c_funcs = [
            lambda v: np.sin(v),
            lambda v: v ** 2,
            lambda v: np.cos(v),
            lambda v: v,
        ]
        M_vec = m.simulate_grid_vectorized_3d([x, y, z, s], c_funcs)
        M_brute = m.simulate_grid([x, y, z, s], c_funcs)
        np.testing.assert_allclose(M_vec, M_brute, atol=1e-12)

    def test_fallback_for_non4d(self):
        """When n_total != 4, should fall back to brute-force."""
        m = EmergentMatterModel(3, [1, 1, 1])
        grids = [np.linspace(0, 1, 4)] * 3
        c_funcs = [lambda x: x] * 3
        M = m.simulate_grid_vectorized_3d(grids, c_funcs)
        assert M.shape == (4, 4, 4)


# ---------------------------------------------------------------------------
# Entropy-specific tests
# ---------------------------------------------------------------------------

class TestEntropyAsDimension:
    def test_entropy_contributes_to_curvature(self):
        """Changing only S (last coordinate) should change curvature."""
        m = EmergentMatterModel(4, [0.25, 0.25, 0.25, 0.25])
        c_funcs = [lambda x: 0.0, lambda x: 0.0, lambda x: 0.0, lambda s: s]
        c_low = m.curvature([0, 0, 0, 0.0], c_funcs)
        c_high = m.curvature([0, 0, 0, 1.0], c_funcs)
        assert c_high > c_low

    def test_entropy_weight_matters(self):
        """Higher entropy weight → entropy has more influence on M."""
        c_funcs = [lambda x: 1.0, lambda s: 10.0]
        m_low = EmergentMatterModel(2, [0.9, 0.1])
        m_high = EmergentMatterModel(2, [0.1, 0.9])
        M_low = m_low.matter([0, 0], c_funcs)
        M_high = m_high.matter([0, 0], c_funcs)
        # Higher entropy weight → closer to 10.0
        assert M_high > M_low

    def test_monotonic_entropy_curvature(self):
        """With C_S(S) = S, matter increases along the entropy axis."""
        m = EmergentMatterModel.from_spatial_and_entropy(
            1, [1.0], entropy_weight=1.0
        )
        c_funcs = [lambda x: 1.0, lambda s: s]  # spatial constant, entropy linear
        s_vals = np.linspace(0.1, 2.0, 20)
        M_vals = [m.matter([0.0, s], c_funcs) for s in s_vals]
        # Should be monotonically increasing
        assert all(M_vals[i] <= M_vals[i + 1] for i in range(len(M_vals) - 1))


# ---------------------------------------------------------------------------
# EMRF Theoretical Formulations (CG, CE, CS) & Bifurcation Tests
# ---------------------------------------------------------------------------

class TestTheoreticalFormulationsAndBifurcation:
    def test_geometry_formulation_cg(self):
        """C_G = f(spacetime geometry) has purely spatial/geometric dimensions."""
        m_cg = EmergentMatterModel.geometry_formulation(n_spatial=3)
        assert m_cg.n_total == 3
        np.testing.assert_allclose(m_cg.weights, [1/3, 1/3, 1/3])

    def test_energy_formulation_ce(self):
        """C_E = f(physically defensible gravitational/energy measures)."""
        m_ce = EmergentMatterModel.energy_formulation(n_spatial=3, spatial_weights=[0.5, 0.3, 0.2])
        assert m_ce.n_total == 3
        np.testing.assert_allclose(m_ce.weights, [0.5, 0.3, 0.2])

    def test_entropy_formulation_cs(self):
        """C_S = f(entropy/information + geometry) includes horizon entropy coupling."""
        m_cs = EmergentMatterModel.entropy_formulation(n_spatial=3, entropy_weight=0.25)
        assert m_cs.n_total == 4  # 3 space + 1 entropy
        assert m_cs.weights.sum() == pytest.approx(1.0)
        assert m_cs.weights[-1] > 0

    def test_bifurcation_branch_a_geometric_collapse(self):
        """Branch A: When delta_bic > -6, candidate collapses to GR."""
        res_gr = np.array([0.01, -0.02, 0.015])
        res_cm = np.array([0.011, -0.019, 0.014])
        # Candidate BIC is worse or indistinguishable (delta_bic >= -6)
        res = EmergentMatterModel.evaluate_bifurcation(res_gr, res_cm, bic_gr=120.0, bic_cm=122.5)
        assert res["collapsed_to_gr"] is True
        assert "Branch A: Geometric Collapse" in res["classification"]
        assert "reduces to gravitational geometry" in res["verdict"]

    def test_bifurcation_branch_b_novel_extension(self):
        """Branch B: When delta_bic <= -6, strong evidence for novel physical extension."""
        res_gr = np.array([0.15, -0.22, 0.18])
        res_cm = np.array([0.005, -0.004, 0.003])
        # Candidate BIC is markedly better (delta_bic = 95 - 120 = -25 <= -6)
        res = EmergentMatterModel.evaluate_bifurcation(res_gr, res_cm, bic_gr=120.0, bic_cm=95.0)
        assert res["collapsed_to_gr"] is False
        assert "Branch B: Novel Physical Extension" in res["classification"]
        assert "exceeds GR baseline" in res["verdict"]

