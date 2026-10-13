"""Outcome-blind qualification primitives for the Gaia wide-binary study."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import numpy as np

G_SI: Final = 6.6743e-11
M_SUN_KG: Final = 1.9884e30
AU_METERS: Final = 1.496e11
PM_DISTANCE_TO_KM_S: Final = 1e-3 * (1 / 206265) * 3.086e13 / 3.154e7

REQUIRED_COLUMNS: Final = (
    "source_id1",
    "source_id2",
    "R_chance",
    "skau",
    "d1pc",
    "d1_errpc",
    "d2pc",
    "d2_errpc",
    "MagG1",
    "MagG2",
    "mu1ramasyr",
    "mu1ra_errmasyr",
    "mu1decmasyr",
    "mu1dec_errmasyr",
    "mu2ramasyr",
    "mu2ra_errmasyr",
    "mu2decmasyr",
    "mu2dec_errmasyr",
    "bp_rp1",
    "bp_rp2",
    "DEC1deg",
    "e",
    "e0",
    "e1",
    "A_G_Amag",
    "A_G_Bmag",
)


@dataclass(frozen=True)
class SelectionConfig:
    chance_alignment_max: float = 0.01
    projected_separation_min_kau: float = 0.2
    projected_separation_max_kau: float = 30.0
    distance_min_pc: float = 0.0
    distance_max_pc: float = 200.0
    absolute_g_min: float = 4.0
    absolute_g_max: float = 14.0
    declination_min_deg: float = -28.0
    proper_motion_relative_error_max: float = 0.005
    distance_match_sigma: float = 3.0


def load_catalog(path: str | Path) -> np.ndarray:
    rows = np.genfromtxt(
        Path(path),
        delimiter=",",
        names=True,
        dtype=None,
        encoding=None,
    )
    missing = sorted(set(REQUIRED_COLUMNS) - set(rows.dtype.names or ()))
    if missing:
        raise ValueError(f"Gaia wide-binary catalog is missing columns: {missing}")
    if rows.ndim != 1 or len(rows) == 0:
        raise ValueError("Gaia wide-binary catalog must contain rows")
    return rows


def select_population(
    rows: np.ndarray,
    config: SelectionConfig | None = None,
) -> tuple[np.ndarray, dict[str, int | str]]:
    if config is None:
        config = SelectionConfig()
    names = set(rows.dtype.names or ())
    missing = sorted(set(REQUIRED_COLUMNS) - names)
    if missing:
        raise ValueError(f"Gaia wide-binary rows are missing columns: {missing}")

    mag_a = rows["MagG1"] - rows["A_G_Amag"]
    mag_b = rows["MagG2"] - rows["A_G_Bmag"]
    color_intercept = 4 - 3.6 * 17 / 11.5 + 0.1
    color_slope = 3.6 / 11.5
    source_mask = (
        (rows["R_chance"] < config.chance_alignment_max)
        & (rows["DEC1deg"] > config.declination_min_deg)
        & (mag_a > config.absolute_g_min)
        & (mag_a < config.absolute_g_max)
        & (mag_b > config.absolute_g_min)
        & (mag_b < config.absolute_g_max)
        & (rows["bp_rp1"] > color_intercept + color_slope * mag_a)
        & (rows["bp_rp2"] > color_intercept + color_slope * mag_b)
    )
    candidates = rows[source_mask]

    distance_a = candidates["d1pc"]
    distance_b = candidates["d2pc"]
    error_a = candidates["d1_errpc"]
    error_b = candidates["d2_errpc"]
    weights_a = 1 / np.square(error_a)
    weights_b = 1 / np.square(error_b)
    mean_distance = (
        distance_a * weights_a + distance_b * weights_b
    ) / (weights_a + weights_b)
    distance_difference = np.abs(distance_a - distance_b)
    orbital_distance_allowance = 6 * candidates["skau"] * 1000 / 206265
    maximum_distance_difference = np.sqrt(
        np.square(config.distance_match_sigma * error_a)
        + np.square(config.distance_match_sigma * error_b)
        + np.square(orbital_distance_allowance)
    )
    with np.errstate(divide="ignore", invalid="ignore"):
        proper_motion_error = np.maximum.reduce(
            (
                np.abs(
                    candidates["mu1ra_errmasyr"] / candidates["mu1ramasyr"]
                ),
                np.abs(
                    candidates["mu1dec_errmasyr"] / candidates["mu1decmasyr"]
                ),
                np.abs(
                    candidates["mu2ra_errmasyr"] / candidates["mu2ramasyr"]
                ),
                np.abs(
                    candidates["mu2dec_errmasyr"] / candidates["mu2decmasyr"]
                ),
            )
        )
    final_mask = (
        (candidates["skau"] > config.projected_separation_min_kau)
        & (candidates["skau"] < config.projected_separation_max_kau)
        & (mean_distance > config.distance_min_pc)
        & (mean_distance < config.distance_max_pc)
        & (distance_difference < maximum_distance_difference)
        & (proper_motion_error < config.proper_motion_relative_error_max)
    )
    selected = candidates[final_mask]
    identifiers = "".join(
        f"{int(first)},{int(second)}\n"
        for first, second in zip(
            selected["source_id1"],
            selected["source_id2"],
            strict=True,
        )
    ).encode("ascii")
    audit: dict[str, int | str] = {
        "catalog_rows": int(len(rows)),
        "source_quality_rows": int(np.count_nonzero(source_mask)),
        "selected_rows": int(len(selected)),
        "selected_identifier_sha256": hashlib.sha256(identifiers).hexdigest(),
    }
    return selected, audit


def projected_velocity_km_s(rows: np.ndarray) -> np.ndarray:
    distance_a = rows["d1pc"]
    distance_b = rows["d2pc"]
    error_a = rows["d1_errpc"]
    error_b = rows["d2_errpc"]
    weights_a = 1 / np.square(error_a)
    weights_b = 1 / np.square(error_b)
    distance = (
        distance_a * weights_a + distance_b * weights_b
    ) / (weights_a + weights_b)
    delta_ra = (rows["mu1ramasyr"] - rows["mu2ramasyr"]) * distance
    delta_dec = (rows["mu1decmasyr"] - rows["mu2decmasyr"]) * distance
    return PM_DISTANCE_TO_KM_S * np.hypot(delta_ra, delta_dec)


def sample_deprojected_accelerations(
    *,
    projected_separation_kau: np.ndarray,
    total_mass_msun: np.ndarray,
    projected_velocity_km_s: np.ndarray,
    eccentricity: np.ndarray,
    eccentricity_low: np.ndarray,
    eccentricity_high: np.ndarray,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    arrays = np.broadcast_arrays(
        projected_separation_kau,
        total_mass_msun,
        projected_velocity_km_s,
        eccentricity,
        eccentricity_low,
        eccentricity_high,
    )
    separation, mass, velocity, center, low, high = (
        np.asarray(value, dtype=float) for value in arrays
    )
    if (
        np.any(separation <= 0)
        or np.any(mass <= 0)
        or np.any(velocity <= 0)
        or not all(np.all(np.isfinite(value)) for value in arrays)
    ):
        raise ValueError("Deprojection inputs must be finite and physical")

    inclination = np.arccos(rng.random(separation.shape))
    eccentricity_draw = np.clip(
        center
        + np.where(
            (normal := rng.standard_normal(separation.shape)) < 0,
            normal * (center - low),
            normal * (high - center),
        ),
        0.001,
        0.999,
    )
    mean_anomaly = 2 * np.pi * rng.random(separation.shape)
    eccentric_anomaly = _solve_kepler(mean_anomaly, eccentricity_draw)
    true_anomaly = 2 * np.arctan2(
        np.sqrt(1 + eccentricity_draw) * np.sin(eccentric_anomaly / 2),
        np.sqrt(1 - eccentricity_draw) * np.cos(eccentric_anomaly / 2),
    )
    periapsis = 2 * np.pi * rng.random(separation.shape)
    phase = periapsis + true_anomaly
    projection = np.sqrt(
        np.square(np.cos(phase))
        + np.square(np.cos(inclination) * np.sin(phase))
    )
    radius_kau = separation / projection
    radius_meters = radius_kau * 1000 * AU_METERS
    newtonian = G_SI * mass * M_SUN_KG / np.square(radius_meters)

    velocity_angle = np.arctan2(
        -(np.cos(phase) + eccentricity_draw * np.cos(periapsis)),
        np.sin(phase) + eccentricity_draw * np.sin(periapsis),
    )
    velocity_projection = np.sqrt(
        np.square(np.cos(velocity_angle))
        + np.square(np.cos(inclination) * np.sin(velocity_angle))
    )
    velocity_3d = velocity / velocity_projection
    kinematic = np.square(velocity_3d * 1000) / radius_meters
    log_newtonian = np.log10(newtonian)
    log_kinematic = np.log10(kinematic)
    if not np.all(np.isfinite(log_newtonian)) or not np.all(
        np.isfinite(log_kinematic)
    ):
        raise RuntimeError("Deprojection produced non-finite accelerations")
    return log_newtonian, log_kinematic


def phenomenological_external_field_ratio(
    newtonian_acceleration: np.ndarray | float,
    *,
    a0: float = 1.2e-10,
    external_field: float = 1.2e-10,
) -> np.ndarray:
    acceleration = np.asarray(newtonian_acceleration, dtype=float)
    if (
        np.any(~np.isfinite(acceleration))
        or np.any(acceleration <= 0)
        or not np.isfinite(a0)
        or a0 <= 0
        or not np.isfinite(external_field)
        or external_field < 0
    ):
        raise ValueError("Accelerations must be finite and physical")
    total = np.hypot(acceleration, external_field)
    return 1 / (1 - np.exp(-np.sqrt(total / a0)))


def _solve_kepler(
    mean_anomaly: np.ndarray,
    eccentricity: np.ndarray,
) -> np.ndarray:
    normalized = np.mod(mean_anomaly, 2 * np.pi)
    lower = np.zeros_like(normalized, dtype=float)
    upper = np.full_like(normalized, 2 * np.pi, dtype=float)
    for _ in range(64):
        anomaly = (lower + upper) / 2
        residual = anomaly - eccentricity * np.sin(anomaly) - normalized
        lower = np.where(residual <= 0, anomaly, lower)
        upper = np.where(residual > 0, anomaly, upper)
    return (lower + upper) / 2


__all__ = [
    "REQUIRED_COLUMNS",
    "SelectionConfig",
    "load_catalog",
    "phenomenological_external_field_ratio",
    "projected_velocity_km_s",
    "sample_deprojected_accelerations",
    "select_population",
]
