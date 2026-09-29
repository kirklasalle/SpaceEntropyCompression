"""Core model for emergent matter from compressed space-entropy.

Foundational Principle
----------------------
Entropy (S) is *dimensional*, not parametric.  It is the quantifiable
expression of what is conventionally called "time".  There is no
independent time coordinate — entropy IS the clock.  Matter arises from
the compression of space and entropy together.

The last coordinate of X̃ is always the entropy dimension.  It is treated
symmetrically with the spatial dimensions in the curvature sum; the only
physical distinction is that the second law of thermodynamics constrains
traversal of the entropy axis to be monotonically non-decreasing.

Mathematical formulation
------------------------
Let X̃ = (x_1, …, x_n, S)  — n spatial coordinates plus one entropy
coordinate — giving (n+1) total dimensions.

  C(X̃) = Σ_i  w_i · C_i(x̃_i)          effective curvature
  M(X̃) = k · ( C(X̃) / C₀ )^α          emergent matter

Each C_i is a function of a *single* coordinate (its own dimension).
Cross-coupling terms (C_ij) are reserved for future work.

Supports brute-force grid simulation over all (n+1) dimensions and an
optimised vectorised path when there are exactly 3 spatial + 1 entropy
dimension (n_total == 4).
"""

import numpy as np
from typing import Callable, List, Sequence


class EmergentMatterModel:
    """Model for emergent matter from compressed space-entropy.

    Parameters
    ----------
    n_total : int
        Total number of dimensions **including** the entropy dimension.
        For 3-D space + entropy, pass ``n_total=4``.
    weights : sequence of float, length n_total
        Relative importance of each dimension's curvature.  Automatically
        normalised so that ``sum(weights) == 1``.
    k : float
        Proportionality constant for the matter mapping.
    alpha : float
        Power-law exponent for the matter mapping.
    C0 : float
        Reference curvature (normalisation constant).

    Notes
    -----
    By convention the **last** weight and the **last** entry in any
    coordinate vector correspond to the entropy dimension S.
    """

    def __init__(
        self,
        n_total: int,
        weights: Sequence[float],
        k: float = 1.0,
        alpha: float = 1.0,
        C0: float = 1.0,
    ):
        if len(weights) != n_total:
            raise ValueError(
                f"len(weights)={len(weights)} must equal n_total={n_total}"
            )
        self.n_total = n_total
        self.weights = np.array(weights, dtype=float)
        self.weights /= self.weights.sum()
        self.k = float(k)
        self.alpha = float(alpha)
        self.C0 = float(C0)

    # -- kept for backward compatibility ---------------------------------
    @property
    def n(self) -> int:
        """Alias — total dimension count (spatial + entropy)."""
        return self.n_total

    # -- convenience constructor -----------------------------------------
    @classmethod
    def from_spatial_and_entropy(
        cls,
        n_spatial: int,
        spatial_weights: Sequence[float],
        entropy_weight: float = 1.0,
        **kwargs,
    ) -> "EmergentMatterModel":
        """Create a model with *n_spatial* space dims + 1 entropy dim.

        >>> m = EmergentMatterModel.from_spatial_and_entropy(
        ...     3, [0.3, 0.4, 0.3], entropy_weight=0.2, k=1.0)
        """
        weights = list(spatial_weights) + [entropy_weight]
        return cls(n_total=n_spatial + 1, weights=weights, **kwargs)

    # -- core math -------------------------------------------------------
    def curvature(
        self,
        X: Sequence[float],
        c_funcs: List[Callable[[float], float]],
    ) -> float:
        """Compute effective curvature C(X̃) = Σ_i w_i · C_i(x̃_i).

        Parameters
        ----------
        X : sequence of float, length n_total
            Coordinate vector.  The last element is the entropy state S.
        c_funcs : list of callables, length n_total
            Each ``c_funcs[i](x_i)`` returns the curvature contribution
            for dimension *i* at coordinate value *x_i*.
        """
        return float(
            sum(w * c_funcs[i](X[i]) for i, w in enumerate(self.weights))
        )

    def matter(
        self,
        X: Sequence[float],
        c_funcs: List[Callable[[float], float]],
    ) -> float:
        """Compute emergent matter M(X̃) = k · (C(X̃) / C₀)^α."""
        C = self.curvature(X, c_funcs)
        if self.C0 == 0:
            return np.nan
        with np.errstate(invalid="ignore"):
            value = np.power(C / self.C0, self.alpha)
        return float(self.k * value)

    # -- grid simulation -------------------------------------------------
    def simulate_grid(
        self,
        X_grid: List[np.ndarray],
        c_funcs: List[Callable[[float], float]],
    ) -> np.ndarray:
        """Brute-force simulation over an (n+1)-dimensional grid.

        Parameters
        ----------
        X_grid : list of 1-D arrays, length n_total
            One array per dimension.  The **last** array is the entropy
            grid (S values).  All other arrays are spatial axes.
        c_funcs : list of callables, length n_total
            ``c_funcs[i](x_i) -> float`` — curvature in dimension *i*.

        Returns
        -------
        M : ndarray of shape ``(len(X_grid[0]), …, len(X_grid[-1]))``
            Emergent matter values over the full grid.
        """
        if len(X_grid) != self.n_total:
            raise ValueError(
                f"len(X_grid)={len(X_grid)} must equal n_total={self.n_total}"
            )
        shape = tuple(len(xg) for xg in X_grid)
        M = np.zeros(shape, dtype=float)
        for idx in np.ndindex(*shape):
            X = [X_grid[d][idx[d]] for d in range(self.n_total)]
            M[idx] = self.matter(X, c_funcs)
        return M

    def simulate_grid_vectorized_3d(
        self,
        X_grid: List[np.ndarray],
        c_funcs: List[Callable[[float], float]],
    ) -> np.ndarray:
        """Vectorised simulation for 3 spatial + 1 entropy dimensions.

        Produces M[x, y, z, S].  Falls back to ``simulate_grid`` when
        ``n_total != 4``.

        Parameters
        ----------
        X_grid : list of 4 arrays — [x, y, z, S_grid]
        c_funcs : list of 4 callables — [Cx, Cy, Cz, Cs]
        """
        if self.n_total != 4:
            return self.simulate_grid(X_grid, c_funcs)

        x, y, z, S_vals = X_grid
        Ns = len(S_vals)
        M = np.empty((len(x), len(y), len(z), Ns), dtype=float)

        for si, S in enumerate(S_vals):
            # Spatial curvature components (broadcast to 3-D)
            C_total = np.zeros((len(x), len(y), len(z)), dtype=float)
            for axis_idx, (grid_1d, w) in enumerate(
                zip([x, y, z], self.weights[:3])
            ):
                Ci_vals = np.array([c_funcs[axis_idx](val) for val in grid_1d])
                if axis_idx == 0:
                    Ci_full = Ci_vals[:, None, None]
                elif axis_idx == 1:
                    Ci_full = Ci_vals[None, :, None]
                else:
                    Ci_full = Ci_vals[None, None, :]
                C_total += w * Ci_full

            # Entropy curvature component (scalar, broadcast everywhere)
            C_total += self.weights[3] * c_funcs[3](S)

            if self.C0 == 0:
                M[..., si] = np.nan
            else:
                with np.errstate(invalid="ignore"):
                    M[..., si] = self.k * np.power(C_total / self.C0, self.alpha)
        return M

    # -- EMRF Theoretical Formulations (CG, CE, CS, CGSE) ----------------
    @classmethod
    def geometry_formulation(
        cls,
        n_spatial: int = 3,
        spatial_weights: Sequence[float] = None,
        **kwargs,
    ) -> "EmergentMatterModel":
        """C_G = f(spacetime geometry)
        Pure geometry-dominated compression branch without entropy term.
        """
        if spatial_weights is None:
            spatial_weights = [1.0 / n_spatial] * n_spatial
        return cls(n_total=n_spatial, weights=spatial_weights, **kwargs)

    @classmethod
    def energy_formulation(
        cls,
        n_spatial: int = 3,
        spatial_weights: Sequence[float] = None,
        **kwargs,
    ) -> "EmergentMatterModel":
        """C_E = f(physically defensible gravitational/energy measures)
        Quasi-local energy-bounded compression branch.
        """
        if spatial_weights is None:
            spatial_weights = [1.0 / n_spatial] * n_spatial
        return cls(n_total=n_spatial, weights=spatial_weights, **kwargs)

    @classmethod
    def entropy_formulation(
        cls,
        n_spatial: int = 3,
        spatial_weights: Sequence[float] = None,
        entropy_weight: float = 0.2,
        **kwargs,
    ) -> "EmergentMatterModel":
        """C_S = f(entropy/information + geometry)
        Spacetime geometry coupled with causal horizon/entanglement entropy.
        """
        if spatial_weights is None:
            spatial_weights = [0.8 / n_spatial] * n_spatial
        return cls.from_spatial_and_entropy(
            n_spatial=n_spatial,
            spatial_weights=spatial_weights,
            entropy_weight=entropy_weight,
            **kwargs,
        )

    @staticmethod
    def evaluate_bifurcation(
        residuals_gr: np.ndarray,
        residuals_cm: np.ndarray,
        bic_gr: float,
        bic_cm: float,
        threshold_delta_bic: float = -6.0,
    ) -> dict:
        """Evaluates the decisive theoretical bifurcation:
        Branch A: Geometric Collapse (C(X,t) ≡ f(G_μν)) if difference is non-significant.
        Branch B: Novel Extension (C(X,t) ≢ f(G_μν)) if statistically significant beyond GR.
        """
        delta_bic = float(bic_cm - bic_gr)
        # In Bayesian Information Criterion, delta_bic < -6 represents strong evidence for the candidate model over GR
        if delta_bic <= threshold_delta_bic:
            classification = "Branch B: Novel Physical Extension (C(X,t) ≢ f(G_μν))"
            verdict = "Statistical evidence exceeds GR baseline. Candidate reveals genuine observable extension."
        else:
            classification = "Branch A: Geometric Collapse (C(X,t) ≡ f(G_μν))"
            verdict = "Compression reduces to gravitational geometry. No novel force detected."
        return {
            "classification": classification,
            "verdict": verdict,
            "delta_bic": delta_bic,
            "bic_gr": float(bic_gr),
            "bic_candidate": float(bic_cm),
            "collapsed_to_gr": delta_bic > threshold_delta_bic,
        }

    # -- string representation -------------------------------------------
    def __repr__(self) -> str:
        return (
            f"EmergentMatterModel(n_total={self.n_total}, "
            f"weights={self.weights.tolist()}, k={self.k}, "
            f"alpha={self.alpha}, C0={self.C0})"
        )

