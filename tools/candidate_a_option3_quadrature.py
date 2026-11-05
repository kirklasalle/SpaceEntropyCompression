"""Experimental model-only quadrature split at finite source-profile boundaries.

This is not authorized by or part of the frozen v1 protocol. It is an
independent numerical candidate to evaluate before proposing an amendment.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from functools import lru_cache

import numpy as np
from numpy.typing import NDArray
from scipy.special import ellipe, ellipkm1

Density = Callable[[NDArray[np.float64], NDArray[np.float64]], NDArray[np.float64]]


@lru_cache(maxsize=8)
def gauss_legendre(order: int) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    if isinstance(order, bool) or not isinstance(order, int) or order < 8:
        raise ValueError("Quadrature order must be an integer >= 8")
    return np.polynomial.legendre.leggauss(order)


def radial_nodes(breakpoints: NDArray[np.float64], field_radius: float,
                 order: int, *,
                 outer_tail_scale: float | None = None
                 ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Build order-point Gauss-Legendre rules per smooth radial subinterval."""
    nodes, weights = gauss_legendre(order)
    if (breakpoints.ndim != 1 or len(breakpoints) < 2
            or not np.isfinite(breakpoints).all()
            or np.any(np.diff(breakpoints) <= 0)
            or breakpoints[0] != 0):
        raise ValueError("Radial breakpoints must increase strictly from zero")
    if not breakpoints[-1] > 0 or not math.isfinite(field_radius) or field_radius <= 0:
        raise ValueError("Cutoff and field radius must be positive and finite")
    split_points = np.unique(np.r_[breakpoints, field_radius])
    split_points = split_points[(split_points >= 0) & (split_points <= breakpoints[-1])]
    if split_points[0] != 0:
        split_points = np.r_[0.0, split_points]
    if split_points[-1] != breakpoints[-1]:
        split_points = np.r_[split_points, breakpoints[-1]]
    left, right = split_points[:-1], split_points[1:]
    mapped_nodes = left[:, None] + (nodes[None, :] + 1) * (right - left)[:, None] / 2
    mapped_weights = weights[None, :] * (right - left)[:, None] / 2
    radial_nodes = mapped_nodes.ravel()
    radial_weights = mapped_weights.ravel()
    if outer_tail_scale is not None:
        if not math.isfinite(outer_tail_scale) or outer_tail_scale <= 0:
            raise ValueError("Outer-tail scale must be finite and positive")
        tail_start = max(float(breakpoints[-1]), field_radius)
        if field_radius > breakpoints[-1]:
            finite_nodes = (breakpoints[-1] + (nodes + 1)
                            * (field_radius - breakpoints[-1]) / 2)
            finite_weights = weights * (field_radius - breakpoints[-1]) / 2
            radial_nodes = np.r_[radial_nodes, finite_nodes]
            radial_weights = np.r_[radial_weights, finite_weights]
        unit_nodes, unit_weights = (nodes + 1) / 2, weights / 2
        tail_nodes = tail_start + outer_tail_scale * unit_nodes / (1 - unit_nodes)
        tail_weights = unit_weights * outer_tail_scale / (1 - unit_nodes)**2
        radial_nodes = np.r_[radial_nodes, tail_nodes]
        radial_weights = np.r_[radial_weights, tail_weights]
    return radial_nodes, radial_weights


def axisymmetric_segmented_v1(
    density: Density,
    radii: NDArray[np.float64],
    *,
    source_breakpoints: NDArray[np.float64],
    order: int,
    r_scale: float,
    z_scale: float = 300.0,
    gravitational_constant: float = 4.30091e-3,
    outer_tail_scale: float | None = None,
) -> NDArray[np.float64]:
    """Integrate a compact radial source with profile-knot-aware finite intervals.

    The vertical half-line retains the frozen rational map. The radial half-line
    is compact because sources are exactly zero after the frozen cutoff.
    """
    for value, name in ((r_scale, "r_scale"), (z_scale, "z_scale"),
                        (gravitational_constant, "G")):
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be finite and positive")
    field = np.asarray(radii, dtype=np.float64)
    breaks = np.asarray(source_breakpoints, dtype=np.float64)
    if (field.ndim != 1 or not len(field) or not np.isfinite(field).all()
            or np.any(field <= 0)):
        raise ValueError("Field radii must be finite, positive and nonempty")
    if (breaks.ndim != 1 or len(breaks) < 2 or not np.isfinite(breaks).all()
            or breaks[0] != 0 or np.any(np.diff(breaks) <= 0)):
        raise ValueError("Source breakpoints must increase strictly from zero")
    t, w = gauss_legendre(order)
    unit_nodes, unit_weights = (t + 1) / 2, w / 2
    source_z = z_scale * unit_nodes / (1 - unit_nodes)
    z_weights = unit_weights * z_scale / (1 - unit_nodes)**2
    values = []
    for radius in field:
        source_r, radial_weights = radial_nodes(
            breaks, float(radius), order, outer_tail_scale=outer_tail_scale)
        rr, zz = source_r[:, None], source_z[None, :]
        plus = (radius + rr)**2 + zz**2
        minus = (radius - rr)**2 + zz**2
        complement = minus / plus
        kernel = (ellipkm1(complement)
                  + (radius**2 - rr**2 - zz**2) / minus
                  * ellipe(1 - complement)) / np.sqrt(plus)
        rho = np.asarray(density(rr, zz), dtype=np.float64)
        if rho.shape != kernel.shape or not np.isfinite(rho).all() or np.any(rho < 0):
            raise ValueError("Density callback must return finite nonnegative volume density")
        value = 4 * gravitational_constant * np.sum(
            kernel * rho * rr * radial_weights[:, None] * z_weights[None, :],
            dtype=np.float64,
        )
        if not math.isfinite(float(value)):
            raise ArithmeticError("Non-finite segmented Poisson integral")
        values.append(float(value))
    return np.asarray(values, dtype=np.float64)
