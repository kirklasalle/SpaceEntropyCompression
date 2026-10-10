"""Core model for emergent matter from multidimensional space-entropy compression.

Foundational Principle (Clarified by Kirk LaSalle, 2026-10-05, 2026-10-07)
--------------------------------------------------------------------------
Space is multidimensional: X = (x, y, z, d_0, d_1, d_2, …) ∈ M^D.
Neither entropy (S) nor time (t) is a spatial coordinate axis.

Time t parameterizes the progression of dynamical change.

Entropy S(X,t) is a thermodynamic state field that characterizes the
organization and compression of energy-momentum within spatial degrees of freedom.
Entropy is the arrow: physical change is oriented in the direction of
increasing entropy (Second Law). Entropy couples into the effective compression
functional as a state variable:

  C(X,S,t) = F(E, S, geometry, t)

For the phenomenological model, we evaluate C over a grid of entropy values.
The last grid entry is a set of entropy state snapshots, not a spatial axis.

Mathematical formulation
------------------------
Let X = (x_1, …, x_n) be the coordinate axes of the D-dimensional spatial
manifold (e.g., standard 3D space plus extra topological/spatial degrees
of freedom d_0, d_1, …).

  C(X, S) = Σ_i w_i · C_i(x_i) + w_S · C_S(S)    effective compression
  M(X, S) = k · ( C(X, S) / C₀ )^α                emergent matter density

Each spatial C_i is a function of coordinate (x_i); C_S is the entropy
coupling evaluated at state S(X,t).

Supports brute-force grid simulation over all n dimensions and an
optimised vectorised path when n_total == 4 (e.g. 3D space + d_0 plus entropy state).
"""

from collections.abc import Callable, Sequence

import numpy as np


class EmergentMatterModel:
    """Model for emergent matter from compressed space-entropy.

    Parameters
    ----------
    n_total : int
        Total number of spatial/topological dimensions (excluding entropy state axis).
        For 3-D space + d_0, pass ``n_total=4``. Entropy states are evaluated
        as a separate parameter sweep; see ``from_spatial_and_entropy``.
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
    Entropy is a thermodynamic state variable, not a spatial coordinate.
    When simulating over a range of entropy values, use ``from_spatial_and_entropy``
    to construct grids with shape (n_spatial_1, …, n_spatial_D, n_entropy_states).
    Each output slice M[…, j] is the matter distribution at entropy state S_j.
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
        """Alias — total dimension count (spatial + topological)."""
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
        """Create a model with n_spatial space dimensions and entropy state sweep.

        Parameters
        ----------
        n_spatial : int
            Number of spatial/topological coordinate axes (e.g., 3 for 3D space).
        spatial_weights : sequence of float
            Weight for each spatial dimension.
        entropy_weight : float
            Weight parameter for entropy coupling (does not change n_total).
            Entropy is not a coordinate; this weight regulates how S(X,t)
            couples into the effective compression C(X,S,t).
        **kwargs
            Additional arguments passed to the constructor (k, alpha, C0, etc.).

        Returns
        -------
        EmergentMatterModel
            Model with n_total = n_spatial + 1, ready to simulate
            over a grid of entropy state values.

        Example
        -------
        >>> m = EmergentMatterModel.from_spatial_and_entropy(
        ...     3, [0.3, 0.4, 0.3], entropy_weight=0.2, k=1.0)
        """
        weights = list(spatial_weights) + [entropy_weight]
        return cls(n_total=n_spatial + 1, weights=weights, **kwargs)

    # -- core math -------------------------------------------------------
    def curvature(
        self,
        X: Sequence[float],
        c_funcs: list[Callable[[float], float]],
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
        c_funcs: list[Callable[[float], float]],
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
        X_grid: list[np.ndarray],
        c_funcs: list[Callable[[float], float]],
    ) -> np.ndarray:
        """Brute-force simulation over a (spatial + entropy state) grid.

        Parameters
        ----------
        X_grid : list of 1-D arrays, length n_total
            One array per dimension.  The **last** array is the entropy
            state grid (S values); all others are spatial/topological axes.
        c_funcs : list of callables, length n_total
            ``c_funcs[i](x_i) -> float`` — curvature in dimension *i*.

        Returns
        -------
        M : ndarray of shape ``(len(X_grid[0]), …, len(X_grid[-1]))``
            Emergent matter values over the full grid. The last index
            ranges over entropy states: M[…, j] is matter at state S_j.
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
        X_grid: list[np.ndarray],
        c_funcs: list[Callable[[float], float]],
    ) -> np.ndarray:
        """Vectorised simulation for 3 spatial + entropy state evaluation.

        Produces M[x, y, z, S] by evaluating over 3D space for each
        entropy state in the sweep. Falls back to ``simulate_grid`` when
        ``n_total != 4``.

        Parameters
        ----------
        X_grid : list of 4 arrays — [x, y, z, S_states]
            The last array is entropy state values (not a spatial axis).
        c_funcs : list of 4 callables — [Cx, Cy, Cz, Cs]
        """
        if self.n_total != 4:
            return self.simulate_grid(X_grid, c_funcs)

        x, y, z, S_vals = X_grid
        ns = len(S_vals)
        M = np.empty((len(x), len(y), len(z), ns), dtype=float)

        for si, S in enumerate(S_vals):
            # Spatial curvature components (broadcast to 3-D)
            c_total = np.zeros((len(x), len(y), len(z)), dtype=float)
            for axis_idx, (grid_1d, w) in enumerate(
                zip([x, y, z], self.weights[:3], strict=True)
            ):
                ci_vals = np.array([c_funcs[axis_idx](val) for val in grid_1d])
                if axis_idx == 0:
                    ci_full = ci_vals[:, None, None]
                elif axis_idx == 1:
                    ci_full = ci_vals[None, :, None]
                else:
                    ci_full = ci_vals[None, None, :]
                c_total += w * ci_full

            # Entropy curvature component (scalar, broadcast everywhere)
            c_total += self.weights[3] * c_funcs[3](S)

            if self.C0 == 0:
                M[..., si] = np.nan
            else:
                with np.errstate(invalid="ignore"):
                    M[..., si] = self.k * np.power(c_total / self.C0, self.alpha)
        return M

    # -- EMRF Theoretical Formulations (CG, CE, CS, CGSE) ----------------
    @classmethod
    def geometry_formulation(
        cls,
        n_spatial: int = 3,
        spatial_weights: Sequence[float] | None = None,
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
        spatial_weights: Sequence[float] | None = None,
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
        spatial_weights: Sequence[float] | None = None,
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
        # Delta BIC <= -6 is treated as strong candidate evidence over GR.
        if delta_bic <= threshold_delta_bic:
            classification = "Branch B: Novel Physical Extension (C(X,t) ≢ f(G_μν))"
            verdict = (
                "Statistical evidence exceeds GR baseline; candidate requires "
                "independent physical and observational validation."
            )
        else:
            classification = "Branch A: Geometric Collapse (C(X,t) ≡ f(G_μν))"
            verdict = "Compression reduces to gravitational geometry. No novel force detected."
        return {
            "classification": classification,
            "verdict": verdict,
            "verdict_deprecated": True,
            "evidence_class": "software",
            "limitation": (
                "Information-criterion classification is a software result until "
                "applied to independently validated observational likelihoods."
            ),
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
