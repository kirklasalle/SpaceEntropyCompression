"""Density-only implementation of the frozen option-3 primary reconstruction.

Never use load_sparc here: its selection consumes observed velocities.
The frozen all-option evaluator is deliberately unchanged.
"""

from __future__ import annotations

import json
import math
import zipfile
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import quad

from tools.evaluate_candidate_a_all_options import optional_number, positive, sha256

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "knowledgebase" / "candidate_a_option3_reconstruction_protocol.json"
PROTOCOL_SHA256 = "cd9687ddac497025e709fccc0c6baf3d40ae5bce92166b8c23fefeec16270518"
G = 4.30091e-3
FloatArray = NDArray[np.float64]
Envelope = Literal["low", "high"]


def verify_inputs(root: Path = ROOT) -> dict[str, Any]:
    path = root / PROTOCOL.relative_to(ROOT)
    if sha256(path) != PROTOCOL_SHA256:
        raise ValueError("Option-3 protocol differs from its frozen SHA-256")
    protocol: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    parent = protocol["parent_protocol"]
    if sha256(root / parent["path"]) != parent["sha256"]:
        raise ValueError("Parent protocol differs from its frozen SHA-256")
    data = protocol["data"]
    holdings = [
        {**h, "path": str(Path(data["leroy2008"]["directory"]) / h["name"])}
        for h in data["leroy2008"]["holdings"]
    ] + data["sparc"]["holdings"]
    for holding in holdings:
        source = root / holding["path"]
        if (not source.is_file() or source.stat().st_size != holding["bytes"]
                or sha256(source) != holding["sha256"]):
            raise ValueError(f"Missing or modified pinned input: {holding['path']}")
    return protocol


@dataclass(frozen=True)
class Geometry:
    distance_mpc: float
    inclination_deg: float

    def __post_init__(self) -> None:
        positive(self.distance_mpc, "distance")
        if not math.isfinite(self.inclination_deg) or not 0 <= self.inclination_deg < 90:
            raise ValueError("Source inclination must be finite in [0, 90) degrees")


@dataclass(frozen=True)
class Ring:
    radius_pc: float
    hi: float | None
    hi_error: float | None
    h2: float | None
    stars: float


@dataclass(frozen=True)
class Profile:
    name: str
    geometry: Geometry
    scale_pc: float
    co_scale_pc: float | None
    log_h2_mass: float | None
    h2_mass_is_limit: bool
    rings: tuple[Ring, ...]


def required_number(line: str, start: int, end: int, label: str) -> float:
    number = optional_number(line, start, end)
    if number is None:
        raise ValueError(f"Missing required {label}")
    return number


def parse_rings(text: str, names: set[str]) -> dict[str, tuple[Ring, ...]]:
    grouped: dict[str, list[Ring]] = {name: [] for name in names}
    for line in text.splitlines():
        name = "".join(line[:8].split())
        if name not in names:
            continue
        hi = optional_number(line, 19, 24)
        hi_error = optional_number(line, 25, 28)
        h2 = optional_number(line, 29, 35)
        stars = required_number(line, 41, 48, "stellar surface density")
        radius = 1000 * required_number(line, 9, 13, "ring radius")
        if hi is None and hi_error != 1.0:
            raise ValueError(f"{name}: missing HI without the frozen sensitivity flag")
        if radius <= 0 or any(v < 0 for v in (hi, hi_error, h2, stars) if v is not None):
            raise ValueError(f"{name}: invalid radius or negative density/error")
        grouped[name].append(Ring(radius, hi, hi_error, h2, stars))
    for name, rings in grouped.items():
        radii = [row.radius_pc for row in rings]
        if len(radii) < 3 or np.any(np.diff(radii) <= 0):
            raise ValueError(f"{name}: require at least three ordered distinct rings")
    return {name: tuple(rings) for name, rings in grouped.items()}


def load_profiles(root: Path, names: set[str]) -> dict[str, Profile]:
    directory = root / "data" / "external" / "candidate_a" / "leroy2008"
    rings = parse_rings((directory / "table7.dat").read_text(encoding="ascii"), names)
    result = {}
    for line in (directory / "table4.dat").read_text(encoding="ascii").splitlines():
        name = "".join(line[:8].split())
        if name not in names:
            continue
        # Do not parse the vflat/lflat fields in this table.
        scale = 1000 * required_number(line, 69, 72, "stellar scale length")
        positive(scale, "stellar scale length")
        co_scale = line[77:80].strip()
        mass = line[58:61].strip()
        result[name] = Profile(
            name,
            Geometry(required_number(line, 9, 13, "distance"),
                     required_number(line, 14, 16, "inclination")),
            scale, None if not co_scale.strip("-") else 1000 * float(co_scale),
            None if not mass.strip("-") else float(mass),
            line[56:58].strip() == "<=", rings[name],
        )
    if set(result) != names:
        raise ValueError("Missing selected galaxy metadata")
    return result


def load_geometry(root: Path, names: set[str]) -> dict[str, Geometry]:
    path = root / "data" / "external" / "sparc" / "SPARC_Lelli2016c.mrt"
    result = {}
    for line in path.read_text(encoding="ascii").splitlines():
        fields = line.split()
        if not fields or fields[0] not in names:
            continue
        if len(fields) < 18:
            raise ValueError("Malformed selected SPARC metadata row")
        if int(fields[17]) > 2 or float(fields[5]) < 30:
            raise ValueError(f"{fields[0]} does not meet the frozen metadata selection")
        # Other columns, including Vflat, are deliberately never converted.
        result[fields[0]] = Geometry(float(fields[2]), float(fields[5]))
    if set(result) != names:
        raise ValueError("Missing selected SPARC geometry")
    return result


def parse_model_columns(text: str) -> FloatArray:
    """Return radius, gas, disc, bulge only, leaving Vobs and errV unparsed."""
    rows = []
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        fields = line.split()
        if len(fields) < 6:
            raise ValueError("Malformed SPARC component row")
        rows.append([float(fields[i]) for i in (0, 3, 4, 5)])
    data = np.asarray(rows, dtype=np.float64).reshape(-1, 4)
    if not len(data) or not np.isfinite(data).all():
        raise ValueError("Missing or non-finite SPARC model components")
    return data[data[:, 0] > 0]


def load_model_columns(root: Path, name: str) -> FloatArray:
    archive_path = root / "data" / "external" / "sparc" / "Rotmod_LTG.zip"
    with zipfile.ZipFile(archive_path) as archive:
        matches = [f for f in archive.namelist()
                   if Path(f).name == f"{name}_rotmod.dat"]
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one pinned rotmod member for {name}")
        return parse_model_columns(archive.read(matches[0]).decode("ascii"))


def radial_values(r: Any, radii: Any, values: Any, cutoff: float,
                  xp: ModuleType = np, *,
                  linear: bool = False,
                  inner_exponential_scale_pc: float | None = None,
                  outer_log_slope_per_pc: float | None = None) -> Any:
    index = xp.clip(xp.searchsorted(radii, r, side="right") - 1, 0, len(radii) - 2)
    fraction = xp.clip((r - radii[index]) / (radii[index + 1] - radii[index]), 0, 1)
    left, right = values[index], values[index + 1]
    if linear:
        interpolated = left + fraction * (right - left)
    else:
        log_left = xp.log(xp.where(left > 0, left, 1.0))
        log_right = xp.log(xp.where(right > 0, right, 1.0))
        interpolated = xp.where(
            (left > 0) & (right > 0),
            xp.exp(log_left + fraction * (log_right - log_left)),
            left + fraction * (right - left),
        )
    if inner_exponential_scale_pc is not None:
        interpolated = xp.where(
            r < radii[0],
            values[0] * xp.exp((radii[0] - r) / inner_exponential_scale_pc),
            interpolated,
        )
    if outer_log_slope_per_pc is not None:
        interpolated = xp.where(
            r > radii[-1],
            values[-1] * xp.exp(outer_log_slope_per_pc * (r - radii[-1])),
            interpolated,
        )
        return interpolated
    return xp.where(r <= cutoff, interpolated, 0.0)


@dataclass(frozen=True)
class SensitivityVariant:
    name: str
    delta_q: float = 0.0
    hi_hwhm_pc: float = 202.0
    h2_hwhm_pc: float = 64.0
    hydrostatic_flaring: bool = False
    inner_stellar_exponential: bool = False
    outer_exponential_tails: bool = False
    spherical_inner_bulge: bool = False
    use_leroy_geometry: bool = False
    f_star: float = 1.0


def sensitivity_variants() -> tuple[SensitivityVariant, ...]:
    return (
        SensitivityVariant("primary"),
        SensitivityVariant("delta_q_minus_0.19", delta_q=-0.19),
        SensitivityVariant("delta_q_plus_0.19", delta_q=0.19),
        SensitivityVariant("gas_hwhm_minus_1sigma", hi_hwhm_pc=174, h2_hwhm_pc=52),
        SensitivityVariant("gas_hwhm_plus_1sigma", hi_hwhm_pc=230, h2_hwhm_pc=76),
        SensitivityVariant("hydrostatic_gas_flaring", hydrostatic_flaring=True),
        SensitivityVariant("inward_stellar_exponential", inner_stellar_exponential=True),
        SensitivityVariant("outer_exponential_tails", outer_exponential_tails=True),
        SensitivityVariant("spherical_inner_bulge", spherical_inner_bulge=True),
        SensitivityVariant("leroy_geometry", use_leroy_geometry=True),
        SensitivityVariant("t1_upsilon_k_0.4", f_star=0.8),
        SensitivityVariant("t1_upsilon_k_0.6", f_star=1.2),
    )


def outer_log_slope(radii: FloatArray, values: FloatArray) -> float | None:
    if values[-1] <= 0:
        return None
    positive_indices = np.flatnonzero(values > 0)
    if len(positive_indices) < 2:
        return None
    selected = positive_indices[-3:]
    if len(selected) < 2:
        return None
    slopes = np.diff(np.log(values[selected])) / np.diff(radii[selected])
    mean_slope = float(np.mean(slopes))
    if mean_slope >= 0:
        raise ValueError("Outer exponential tail is not decaying and has no finite source mass")
    return mean_slope


def spherical_bulge_profile(radii: FloatArray, sigma: FloatArray, scale_pc: float,
                            cutoff_pc: float) -> tuple[
                                FloatArray, FloatArray, FloatArray, FloatArray
                            ]:
    """Abel-deproject the clipped inner excess over the anchored exponential disc."""
    end = min(2 * scale_pc, cutoff_pc)
    surface_radii: FloatArray = np.asarray(np.unique(np.r_[
        np.linspace(0.0, end, 4097),
        radii[(radii > 0) & (radii < end)],
        end,
    ]), dtype=np.float64)
    surface_total = np.asarray(radial_values(
        surface_radii, radii, sigma, cutoff_pc), dtype=np.float64)
    anchor = float(radial_values(2 * scale_pc, radii, sigma, math.inf))
    disc = anchor * np.exp(-(surface_radii - 2 * scale_pc) / scale_pc)
    bulge_surface = np.maximum(surface_total - disc, 0.0)
    bulge_surface[surface_radii >= 2 * scale_pc] = 0.0
    if cutoff_pc < 2 * scale_pc:
        bulge_surface[-1] = 0.0
    if not np.any(bulge_surface > 0):
        return (
            surface_radii, np.zeros_like(surface_radii),
            np.linspace(0.0, end, 4097, dtype=np.float64),
            np.zeros(4097, dtype=np.float64),
        )

    slopes = np.diff(bulge_surface) / np.diff(surface_radii)
    lower, upper = surface_radii[:-1], surface_radii[1:]
    density_radii: FloatArray = np.linspace(0.0, end, 4097, dtype=np.float64)
    density = np.zeros_like(density_radii)
    for start in range(1, len(density_radii) - 1, 64):
        stop = min(start + 64, len(density_radii) - 1)
        rr = density_radii[start:stop, None]
        active = upper[None, :] > rr
        hi = np.broadcast_to(upper[None, :], active.shape)
        lo = np.maximum(lower[None, :], rr)
        hi_ratio = np.maximum(hi / rr, 1.0)
        lo_ratio = np.maximum(lo / rr, 1.0)
        intervals = np.where(active, np.arccosh(hi_ratio) - np.arccosh(lo_ratio), 0.0)
        density[start:stop] = -intervals @ slopes / math.pi
    density[0] = density[1]
    density[-1] = 0.0
    if not np.isfinite(density).all():
        raise ArithmeticError("Spherical bulge Abel inversion is non-finite")
    return surface_radii, bulge_surface, density_radii, density


@dataclass(frozen=True)
class Source:
    name: str
    envelope: Envelope
    radii_pc: FloatArray
    sigma: FloatArray
    cutoff_pc: float
    scale_pc: float
    z0_pc: float
    hi_sigma_pc: FloatArray
    h2_sigma_pc: FloatArray
    field_radius_scale: float = 1.0
    inner_stellar_exponential: bool = False
    outer_exponential_tails: bool = False
    outer_log_slopes: tuple[float | None, ...] = (None, None, None)
    bulge_surface_radii_pc: FloatArray | None = None
    bulge_surface_sigma: FloatArray | None = None
    bulge_density_radii_pc: FloatArray | None = None
    bulge_density: FloatArray | None = None

    def surface(self, r: Any, xp: ModuleType = np) -> Any:
        rings, sigma = xp.asarray(self.radii_pc), xp.asarray(self.sigma)
        surfaces = [
            radial_values(
                r, rings, sigma[index], self.cutoff_pc, xp,
                inner_exponential_scale_pc=(
                    self.scale_pc if index == 0 and self.inner_stellar_exponential else None
                ),
                outer_log_slope_per_pc=(
                    self.outer_log_slopes[index] if self.outer_exponential_tails else None
                ),
            )
            for index in range(len(sigma))
        ]
        if self.outer_exponential_tails:
            for index, slope in enumerate(self.outer_log_slopes):
                if slope is None:
                    surfaces[index] = radial_values(
                        r, rings, sigma[index], self.cutoff_pc, xp,
                        inner_exponential_scale_pc=(
                            self.scale_pc if index == 0 and self.inner_stellar_exponential
                            else None
                        ),
                    )
        return xp.stack(surfaces)

    def _gas_width(self, r: Any, values: FloatArray, xp: ModuleType) -> Any:
        return radial_values(r, xp.asarray(self.radii_pc), xp.asarray(values),
                             math.inf, xp, linear=True)

    def components(self, r: Any, z: Any, xp: ModuleType = np) -> Any:
        surfaces = self.surface(r, xp)
        if self.bulge_surface_radii_pc is not None:
            if self.bulge_surface_sigma is None or self.bulge_density_radii_pc is None \
                    or self.bulge_density is None:
                raise ValueError("Incomplete spherical bulge profile")
            bulge_surface = radial_values(
                r, xp.asarray(self.bulge_surface_radii_pc),
                xp.asarray(self.bulge_surface_sigma),
                float(self.bulge_surface_radii_pc[-1]), xp, linear=True,
            )
            surfaces = xp.stack((surfaces[0] - bulge_surface, surfaces[1], surfaces[2]))
            spherical_radius = xp.sqrt(xp.asarray(r) ** 2 + xp.asarray(z) ** 2)
            bulge_density = xp.interp(
                spherical_radius,
                xp.asarray(self.bulge_density_radii_pc),
                xp.asarray(self.bulge_density),
                left=float(self.bulge_density[0]),
                right=0.0,
            )
        else:
            bulge_density = 0.0
        tail = xp.exp(-2 * xp.abs(z) / self.z0_pc)
        stars = surfaces[0] * (2 / self.z0_pc) * tail / (1 + tail)**2
        hi_width = self._gas_width(r, self.hi_sigma_pc, xp)
        h2_width = self._gas_width(r, self.h2_sigma_pc, xp)
        hi = surfaces[1] / (math.sqrt(2 * math.pi) * hi_width) * xp.exp(
            -0.5 * (z / hi_width)**2)
        h2 = surfaces[2] / (math.sqrt(2 * math.pi) * h2_width) * xp.exp(
            -0.5 * (z / h2_width)**2)
        stars = stars + bulge_density
        return xp.stack(xp.broadcast_arrays(stars, hi, h2))

    def vertical_scale(self, component: int, r: float) -> float:
        if component == 0:
            return self.z0_pc
        values = self.hi_sigma_pc if component == 1 else self.h2_sigma_pc
        return float(np.interp(r, self.radii_pc, values))

    def density(self, r: Any, z: Any, xp: ModuleType = np) -> Any:
        return xp.sum(self.components(r, z, xp), axis=0)


def build_source(profile: Profile, geometry: Geometry, envelope: Envelope, *,
                 f_star: float | None = None, delta_q: float | None = None,
                 f_distance: float = 1.0,
                 variant: SensitivityVariant | None = None) -> Source:
    if envelope not in ("low", "high"):
        raise ValueError("Envelope must be low or high")
    variant = variant or SensitivityVariant("primary")
    f_star = variant.f_star if f_star is None else f_star
    delta_q = variant.delta_q if delta_q is None else delta_q
    if not 0.5 <= f_star <= 2 or not -0.38 <= delta_q <= 0.38:
        raise ValueError("Stellar nuisances outside frozen bounds")
    positive(f_distance, "distance nuisance")
    radii = np.array([row.radius_pc for row in profile.rings])
    cutoff = float(radii[-1] + (radii[-1] - radii[-2]) / 2)
    stars = np.array([row.stars for row in profile.rings])
    hi = np.array([row.hi if row.hi is not None else float(envelope == "high")
                   for row in profile.rings])
    detected = [row.h2 for row in profile.rings if row.h2 is not None]
    f_co = 0.7 if envelope == "low" else 1.3
    if detected:
        upper = min(detected)
        h2 = np.array([row.h2 if row.h2 is not None else
                       (upper if envelope == "high" else 0.0) for row in profile.rings])
    else:
        if profile.log_h2_mass is None:
            raise ValueError(f"{profile.name}: no molecular bound; cannot reconstruct")
        scale = profile.scale_pc if profile.h2_mass_is_limit else profile.co_scale_pc
        if scale is None:
            raise ValueError(f"{profile.name}: missing synthetic H2 scale length")
        positive(scale, "synthetic H2 scale length")
        shape = np.exp(-radii / scale)
        # Normalize the frozen radial representation, including its constant end caps.
        integral, error = quad(
            lambda r: 2 * math.pi * r * float(radial_values(r, radii, shape, cutoff)),
            0, cutoff, points=radii.tolist(), epsabs=1e-4, epsrel=1e-11,
            limit=max(100, 2 * len(radii)),
        )
        if integral <= 0 or error / integral > 1e-8:
            raise ArithmeticError("Synthetic H2 normalization failed")
        mass = 1.36 * 10**profile.log_h2_mass
        h2 = shape * (mass / integral if envelope == "high" else 0.0)
    source_geometry = profile.geometry if variant.use_leroy_geometry else geometry
    alignment = source_geometry.distance_mpc / profile.geometry.distance_mpc
    inclination = math.cos(math.radians(source_geometry.inclination_deg)) / math.cos(
        math.radians(profile.geometry.inclination_deg))
    sigma = np.stack((f_star * stars, hi, f_co * h2)) * inclination
    h_nominal = profile.scale_pc * alignment
    q = 10**(0.367 * math.log10(h_nominal / 1000) + 0.708 + delta_q)
    scale_factor = alignment * f_distance
    scaled_radii = radii * scale_factor
    scaled_cutoff = cutoff * scale_factor
    hi_sigma: FloatArray = np.full(
        len(radii), variant.hi_hwhm_pc / math.sqrt(2 * math.log(2)), dtype=np.float64)
    h2_sigma: FloatArray = np.full(
        len(radii), variant.h2_hwhm_pc / math.sqrt(2 * math.log(2)), dtype=np.float64)
    z0 = 2 * h_nominal / q * f_distance
    if variant.hydrostatic_flaring:
        hi_sigma, h2_sigma = hydrostatic_gas_widths(
            scaled_radii, sigma, z0, hi_sigma, h2_sigma)

    component_slopes = []
    for label, row in zip(("stars", "HI", "H2"), sigma, strict=True):
        try:
            slope = None
            if variant.outer_exponential_tails:
                slope = outer_log_slope(scaled_radii, row)
        except ValueError as exc:
            raise ValueError(f"{label}: {exc}") from exc
        component_slopes.append(slope)
    slopes = tuple(component_slopes)
    bulge_radii: FloatArray | None = None
    bulge_surface: FloatArray | None = None
    bulge_density_radii: FloatArray | None = None
    bulge_density_values: FloatArray | None = None
    if variant.spherical_inner_bulge:
        bulge_radii, bulge_surface, bulge_density_radii, bulge_density_values = (
            spherical_bulge_profile(scaled_radii, sigma[0], profile.scale_pc * scale_factor,
                                   scaled_cutoff)
        )
    return Source(
        name=profile.name,
        envelope=envelope,
        radii_pc=scaled_radii,
        sigma=sigma,
        cutoff_pc=scaled_cutoff,
        scale_pc=profile.scale_pc * scale_factor,
        z0_pc=z0,
        hi_sigma_pc=hi_sigma,
        h2_sigma_pc=h2_sigma,
        field_radius_scale=profile.geometry.distance_mpc / source_geometry.distance_mpc,
        inner_stellar_exponential=variant.inner_stellar_exponential,
        outer_exponential_tails=variant.outer_exponential_tails,
        outer_log_slopes=slopes,
        bulge_surface_radii_pc=bulge_radii,
        bulge_surface_sigma=bulge_surface,
        bulge_density_radii_pc=bulge_density_radii,
        bulge_density=bulge_density_values,
    )


def hydrostatic_gas_widths(radii_pc: FloatArray, sigma: FloatArray, z0_pc: float,
                           hi_initial_pc: FloatArray,
                           h2_initial_pc: FloatArray) -> tuple[FloatArray, FloatArray]:
    if (sigma.shape != (3, len(radii_pc))
            or hi_initial_pc.shape != radii_pc.shape
            or h2_initial_pc.shape != radii_pc.shape
            or not np.isfinite(radii_pc).all()
            or not np.isfinite(sigma).all()
            or not np.isfinite(hi_initial_pc).all()
            or not np.isfinite(h2_initial_pc).all()
            or np.any(sigma < 0)
            or np.any(hi_initial_pc <= 0)
            or np.any(h2_initial_pc <= 0)):
        raise ValueError("Hydrostatic flaring inputs must be finite, aligned, and nonnegative")
    positive(z0_pc, "stellar scale height")
    hi_width = hi_initial_pc.copy()
    h2_width = h2_initial_pc.copy()
    for _ in range(100):
        stellar_midplane = sigma[0] / (2 * z0_pc)
        hi_midplane = sigma[1] / (math.sqrt(2 * math.pi) * hi_width)
        h2_midplane = sigma[2] / (math.sqrt(2 * math.pi) * h2_width)
        baryonic_midplane = stellar_midplane + hi_midplane + h2_midplane
        if not np.isfinite(baryonic_midplane).all() or np.any(baryonic_midplane <= 0):
            raise ArithmeticError("Hydrostatic flaring requires positive finite midplane density")
        target_hi = 8.9 / np.sqrt(4 * math.pi * G * baryonic_midplane)
        target_h2 = 4.4 / np.sqrt(4 * math.pi * G * baryonic_midplane)
        relative_change = max(
            float(np.max(np.abs(target_hi - hi_width) / np.maximum(target_hi, hi_width))),
            float(np.max(np.abs(target_h2 - h2_width) / np.maximum(target_h2, h2_width))),
        )
        hi_width, h2_width = target_hi, target_h2
        if relative_change < 1e-8:
            return hi_width, h2_width
    raise ArithmeticError("Hydrostatic gas flaring did not converge within 100 iterations")


def mapped_density(rho: Any, alpha: float, rho0: float,
                   xp: ModuleType = np) -> Any:
    """Frozen v1 underflow policy, unlike the historical evaluator's strict policy."""
    positive(alpha, "alpha")
    positive(rho0, "rho0")
    if not bool(xp.all(xp.isfinite(rho))) or bool(xp.any(rho < 0)):
        raise ValueError("Baryonic density must be finite and nonnegative")
    if alpha == 1:
        return rho.copy()
    mask = rho > 0
    result = xp.zeros_like(rho, dtype=xp.float64)
    with np.errstate(over="raise", invalid="raise", under="ignore"):
        result[mask] = xp.exp(math.log(rho0) + (xp.log(rho[mask]) - math.log(rho0)) / alpha)
    if not bool(xp.all(xp.isfinite(result))):
        raise ArithmeticError("Effective-density overflow or non-finite value")
    return result
