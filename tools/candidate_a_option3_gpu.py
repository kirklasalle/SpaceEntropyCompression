"""Optional float64 GPU density/reduction with CPU elliptic-kernel construction."""

from __future__ import annotations

import importlib
from types import ModuleType
from typing import Any

import numpy as np
from scipy.special import ellipe, ellipkm1

from tools.candidate_a_option3_quadrature import radial_nodes
from tools.candidate_a_option3_reconstruction import (
    FloatArray,
    G,
    Source,
    mapped_density,
)
from tools.evaluate_candidate_a_all_options import positive, quadrature


def require_gpu() -> ModuleType:
    try:
        cp = importlib.import_module("cupy")
    except ImportError as exc:
        raise RuntimeError("GPU requested but unavailable; install the optional [gpu] extra") from exc
    if cp.cuda.runtime.getDeviceCount() < 1:
        raise RuntimeError("GPU requested but no CUDA device is available")
    return cp


def device_info(cp: ModuleType) -> dict[str, Any]:
    device = cp.cuda.Device()
    props = cp.cuda.runtime.getDeviceProperties(device.id)
    free, total = cp.cuda.runtime.memGetInfo()
    return {
        "device_index": device.id, "name": props["name"].decode(),
        "compute_capability": f"{props['major']}.{props['minor']}",
        "free_bytes_at_probe": free, "total_bytes": total,
        "cupy": cp.__version__, "runtime_api_version": cp.cuda.runtime.runtimeGetVersion(),
        "driver_api_version": cp.cuda.runtime.driverGetVersion(),
        "dtype": "float64", "kernel_construction": "CPU SciPy elliptic functions",
        "device_work": "component densities, summed nonlinear map, weighted reduction",
    }


class DeviceQuadrature:
    """Keep only one field radius on device; no unbounded multi-galaxy batching."""

    def __init__(self, cp: ModuleType, order: int, r_scale: float,
                 z_scale: float = 300.0, gravitational_constant: float = G):
        positive(r_scale, "r_scale")
        positive(z_scale, "z_scale")
        positive(gravitational_constant, "G")
        self.cp = cp
        self.t, self.w = quadrature(order)
        self.r_scale, self.z_scale, self.g = r_scale, z_scale, gravitational_constant

    def evaluate(self, source: Source, radii: FloatArray,
                 alpha: float, rho0: float) -> FloatArray:
        cp = self.cp
        if (radii.ndim != 1 or not len(radii) or np.any(radii <= 0)
                or not np.isfinite(radii).all()):
            raise ValueError("Field radii must be finite, positive and nonempty")
        t, w = self.t, self.w
        z = self.z_scale * t / (1 - t)
        wz = w * self.z_scale / (1 - t)**2
        result = []
        for radius in radii:
            split = radius / (radius + self.r_scale)
            tr = np.r_[t * split, split + t * (1 - split)]
            wr = np.r_[w * split, w * (1 - split)] * self.r_scale / (1 - tr)**2
            r = (self.r_scale * tr / (1 - tr))[:, None]
            zz = z[None, :]
            plus = (radius + r)**2 + zz**2
            minus = (radius - r)**2 + zz**2
            complement = minus / plus
            kernel = (ellipkm1(complement)
                      + (radius**2 - r**2 - zz**2) / minus
                      * ellipe(1 - complement)) / np.sqrt(plus)
            weights = cp.asarray(4 * self.g * kernel * r * wr[:, None] * wz[None, :])
            rho = source.density(cp.asarray(r), cp.asarray(zz), cp)
            effective = mapped_density(rho, alpha, rho0, cp)
            if effective.shape != weights.shape:
                raise ValueError("GPU density callback shape differs from quadrature")
            value = float(cp.sum(weights * effective, dtype=cp.float64).get())
            if not np.isfinite(value):
                raise ArithmeticError("Non-finite GPU Poisson integral")
            result.append(value)
        return np.asarray(result, dtype=np.float64)


class DeviceSegmentedQuadrature(DeviceQuadrature):
    """Experimental profile-knot-aware candidate; not frozen protocol v1."""

    def evaluate(self, source: Source, radii: FloatArray,
                 alpha: float, rho0: float) -> FloatArray:
        cp = self.cp
        if (radii.ndim != 1 or not len(radii) or np.any(radii <= 0)
                or not np.isfinite(radii).all()):
            raise ValueError("Field radii must be finite, positive and nonempty")
        t, w = self.t, self.w
        z = self.z_scale * t / (1 - t)
        wz = w * self.z_scale / (1 - t)**2
        breaks = np.r_[0.0, source.radii_pc]
        if not source.outer_exponential_tails:
            breaks = np.r_[breaks, source.cutoff_pc]
        breaks = np.unique(breaks)
        result = []
        for radius in radii:
            source_r, radial_weights = radial_nodes(
                breaks, float(radius), len(t),
                outer_tail_scale=source.scale_pc if source.outer_exponential_tails else None,
            )
            rr, zz = source_r[:, None], z[None, :]
            plus = (radius + rr)**2 + zz**2
            minus = (radius - rr)**2 + zz**2
            complement = minus / plus
            kernel = (ellipkm1(complement)
                      + (radius**2 - rr**2 - zz**2) / minus
                      * ellipe(1 - complement)) / np.sqrt(plus)
            weights = cp.asarray(
                4 * self.g * kernel * rr * radial_weights[:, None] * wz[None, :]
            )
            density = source.density(cp.asarray(rr), cp.asarray(zz), cp)
            effective = mapped_density(density, alpha, rho0, cp)
            if effective.shape != weights.shape:
                raise ValueError("GPU density callback shape differs from segmented quadrature")
            value = float(cp.sum(weights * effective, dtype=cp.float64).get())
            if not np.isfinite(value):
                raise ArithmeticError("Non-finite segmented GPU Poisson integral")
            result.append(value)
        return np.asarray(result, dtype=np.float64)
