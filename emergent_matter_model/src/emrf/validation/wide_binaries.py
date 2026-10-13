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


@dataclass(frozen=True)
class MassComponents:
    primary_a: np.ndarray
    companion_a: np.ndarray
    primary_b: np.ndarray
    companion_b: np.ndarray

    @property
    def total_a(self) -> np.ndarray:
        return self.primary_a + self.companion_a

    @property
    def total_b(self) -> np.ndarray:
        return self.primary_b + self.companion_b


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


def assign_multiplicity(
    rows: np.ndarray,
    *,
    mass_magnitude_coefficients: np.ndarray,
    fraction: float,
    rng: np.random.Generator,
) -> MassComponents:
    if not 0 <= fraction <= 1:
        raise ValueError("Multiplicity fraction must be between zero and one")
    coefficients = np.asarray(mass_magnitude_coefficients, dtype=float)
    if coefficients.shape != (11,) or not np.all(np.isfinite(coefficients)):
        raise ValueError("Mass-magnitude coefficients must contain 11 finite values")

    magnitude_a = rows["MagG1"] - rows["A_G_Amag"]
    magnitude_b = rows["MagG2"] - rows["A_G_Bmag"]
    primary_a = _mass_from_magnitude(magnitude_a, coefficients)
    primary_b = _mass_from_magnitude(magnitude_b, coefficients)
    companion_a = np.zeros(len(rows), dtype=float)
    companion_b = np.zeros(len(rows), dtype=float)

    multiple = rng.random(len(rows)) <= fraction
    option = rng.random(len(rows))
    has_a = multiple & ((option > 0.6) | (option <= 0.3))
    has_b = multiple & (option <= 0.6)
    primary_a, companion_a = _split_unresolved_mass(
        magnitude_a,
        primary_a,
        has_a,
        coefficients,
        rng,
    )
    primary_b, companion_b = _split_unresolved_mass(
        magnitude_b,
        primary_b,
        has_b,
        coefficients,
        rng,
    )
    return MassComponents(primary_a, companion_a, primary_b, companion_b)


def perturbed_projected_velocity_km_s(
    rows: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    distance = _weighted_distance(rows)
    delta_ra = (
        rows["mu1ramasyr"]
        + rows["mu1ra_errmasyr"] * rng.standard_normal(len(rows))
        - rows["mu2ramasyr"]
        - rows["mu2ra_errmasyr"] * rng.standard_normal(len(rows))
    ) * distance
    delta_dec = (
        rows["mu1decmasyr"]
        + rows["mu1dec_errmasyr"] * rng.standard_normal(len(rows))
        - rows["mu2decmasyr"]
        - rows["mu2dec_errmasyr"] * rng.standard_normal(len(rows))
    ) * distance
    velocity = PM_DISTANCE_TO_KM_S * np.hypot(delta_ra, delta_dec)
    if np.any(~np.isfinite(velocity)) or np.any(velocity <= 0):
        raise RuntimeError("Proper-motion perturbation produced invalid velocity")
    return velocity


def sample_newtonian_control_velocity_km_s(
    rows: np.ndarray,
    components: MassComponents,
    *,
    orbit_rng: np.random.Generator,
    companion_rng: np.random.Generator,
    proper_motion_rng: np.random.Generator,
) -> np.ndarray:
    total_mass = components.total_a + components.total_b
    (
        radius_au,
        semimajor_au,
        phase,
        inclination,
        eccentricity,
        periapsis,
    ) = _sample_orbit(
        rows["skau"] * 1000,
        rows["e"],
        rows["e0"],
        rows["e1"],
        orbit_rng,
    )
    speed_term = 2 / radius_au - 1 / semimajor_au
    if np.any(speed_term <= 0):
        raise RuntimeError("Newtonian control generated an unbound outer orbit")
    speed = 1e-3 * np.sqrt(
        G_SI * M_SUN_KG * total_mass / AU_METERS * speed_term
    )
    velocity_x, velocity_y = _project_orbital_velocity(
        speed,
        phase,
        inclination,
        eccentricity,
        periapsis,
    )

    hidden_a_x, hidden_a_y = _sample_photocenter_velocity(
        components.primary_a,
        components.companion_a,
        semimajor_au,
        _weighted_distance(rows),
        companion_rng,
    )
    hidden_b_x, hidden_b_y = _sample_photocenter_velocity(
        components.primary_b,
        components.companion_b,
        semimajor_au,
        _weighted_distance(rows),
        companion_rng,
    )
    velocity_x += hidden_a_x - hidden_b_x
    velocity_y += hidden_a_y - hidden_b_y

    distance = _weighted_distance(rows)
    noise_x = distance * (
        rows["mu1ra_errmasyr"] * proper_motion_rng.standard_normal(len(rows))
        - rows["mu2ra_errmasyr"] * proper_motion_rng.standard_normal(len(rows))
    )
    noise_y = distance * (
        rows["mu1dec_errmasyr"] * proper_motion_rng.standard_normal(len(rows))
        - rows["mu2dec_errmasyr"] * proper_motion_rng.standard_normal(len(rows))
    )
    velocity_x += PM_DISTANCE_TO_KM_S * noise_x
    velocity_y += PM_DISTANCE_TO_KM_S * noise_y
    velocity = np.hypot(velocity_x, velocity_y)
    if np.any(~np.isfinite(velocity)) or np.any(velocity <= 0):
        raise RuntimeError("Newtonian control produced invalid projected velocity")
    return velocity


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


def _weighted_distance(rows: np.ndarray) -> np.ndarray:
    weights_a = 1 / np.square(rows["d1_errpc"])
    weights_b = 1 / np.square(rows["d2_errpc"])
    return (
        rows["d1pc"] * weights_a + rows["d2pc"] * weights_b
    ) / (weights_a + weights_b)


def _mass_from_magnitude(
    magnitude: np.ndarray,
    coefficients: np.ndarray,
) -> np.ndarray:
    mass = np.power(10.0, np.polynomial.polynomial.polyval(magnitude, coefficients))
    if np.any(~np.isfinite(mass)) or np.any(mass <= 0):
        raise RuntimeError("Mass-magnitude relation produced invalid mass")
    return mass


def _split_unresolved_mass(
    magnitude: np.ndarray,
    unsplit_mass: np.ndarray,
    selected: np.ndarray,
    coefficients: np.ndarray,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    primary = np.array(unsplit_mass, copy=True)
    companion = np.zeros_like(primary)
    count = int(np.count_nonzero(selected))
    if count == 0:
        return primary, companion
    delta_magnitude = 12 * rng.power(0.3, count)
    primary_light = 1 / (1 + np.power(10.0, -0.4 * delta_magnitude))
    primary_magnitude = -2.5 * np.log10(primary_light) + magnitude[selected]
    companion_magnitude = (
        -2.5 * np.log10(np.maximum(1 - primary_light, 1e-20))
        + magnitude[selected]
    )
    primary[selected] = _mass_from_magnitude(primary_magnitude, coefficients)
    companion[selected] = _mass_from_magnitude(companion_magnitude, coefficients)
    return primary, companion


def _sample_orbit(
    projected_separation_au: np.ndarray,
    eccentricity: np.ndarray,
    eccentricity_low: np.ndarray,
    eccentricity_high: np.ndarray,
    rng: np.random.Generator,
) -> tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
]:
    inclination = np.arccos(rng.random(len(projected_separation_au)))
    normal = rng.standard_normal(len(projected_separation_au))
    eccentricity_draw = np.clip(
        eccentricity
        + np.where(
            normal < 0,
            normal * (eccentricity - eccentricity_low),
            normal * (eccentricity_high - eccentricity),
        ),
        0.001,
        0.999,
    )
    mean_anomaly = 2 * np.pi * rng.random(len(projected_separation_au))
    eccentric_anomaly = _solve_kepler(mean_anomaly, eccentricity_draw)
    true_anomaly = 2 * np.arctan2(
        np.sqrt(1 + eccentricity_draw) * np.sin(eccentric_anomaly / 2),
        np.sqrt(1 - eccentricity_draw) * np.cos(eccentric_anomaly / 2),
    )
    periapsis = 2 * np.pi * rng.random(len(projected_separation_au))
    phase = periapsis + true_anomaly
    projection = np.sqrt(
        np.square(np.cos(phase))
        + np.square(np.cos(inclination) * np.sin(phase))
    )
    radius_au = projected_separation_au / projection
    semimajor_au = (
        radius_au
        * (1 + eccentricity_draw * np.cos(true_anomaly))
        / (1 - np.square(eccentricity_draw))
    )
    return (
        radius_au,
        semimajor_au,
        phase,
        inclination,
        eccentricity_draw,
        periapsis,
    )


def _sample_photocenter_velocity(
    primary_mass: np.ndarray,
    companion_mass: np.ndarray,
    outer_semimajor_au: np.ndarray,
    distance_pc: np.ndarray,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    velocity_x = np.zeros_like(primary_mass)
    velocity_y = np.zeros_like(primary_mass)
    selected = companion_mass > 0
    if not np.any(selected):
        return velocity_x, velocity_y

    primary = primary_mass[selected]
    companion = companion_mass[selected]
    maximum = np.minimum(
        distance_pc[selected],
        0.3 * outer_semimajor_au[selected],
    )
    if np.any(maximum <= 0.01):
        raise RuntimeError("Hidden-companion semimajor-axis range is empty")
    semimajor = np.power(
        10.0,
        rng.uniform(np.log10(0.01), np.log10(maximum)),
    )
    eccentricity_shape = np.clip(
        1 - 1.26411333 + 0.85366141 * np.log10(semimajor),
        0.001,
        2.2,
    )
    eccentricity = rng.power(eccentricity_shape)
    mean_anomaly = 2 * np.pi * rng.random(len(primary))
    eccentric_anomaly = _solve_kepler(mean_anomaly, eccentricity)
    true_anomaly = 2 * np.arctan2(
        np.sqrt(1 + eccentricity) * np.sin(eccentric_anomaly / 2),
        np.sqrt(1 - eccentricity) * np.cos(eccentric_anomaly / 2),
    )
    periapsis = 2 * np.pi * rng.random(len(primary))
    phase = periapsis + true_anomaly
    radius = (
        semimajor
        * (1 - np.square(eccentricity))
        / (1 + eccentricity * np.cos(true_anomaly))
    )
    inclination = np.arccos(rng.random(len(primary)))
    period_years = np.sqrt(
        np.power(semimajor, 3) / (primary + companion)
    )
    alpha = 3.5
    photocenter_factor = (
        primary
        * companion
        * (
            np.power(primary, alpha - 1)
            - np.power(companion, alpha - 1)
        )
        / (
            (primary + companion)
            * (np.power(primary, alpha) + np.power(companion, alpha))
        )
    )
    photocenter_factor = np.where(period_years < 3, 0, photocenter_factor)
    speed = photocenter_factor * 1e-3 * np.sqrt(
        G_SI
        * M_SUN_KG
        * (primary + companion)
        / AU_METERS
        * (2 / radius - 1 / semimajor)
    )
    projected_x, projected_y = _project_orbital_velocity(
        speed,
        phase,
        inclination,
        eccentricity,
        periapsis,
    )
    velocity_x[selected] = projected_x
    velocity_y[selected] = projected_y
    return velocity_x, velocity_y


def _project_orbital_velocity(
    speed: np.ndarray,
    phase: np.ndarray,
    inclination: np.ndarray,
    eccentricity: np.ndarray,
    periapsis: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    direction_x = -(np.sin(phase) + eccentricity * np.sin(periapsis))
    direction_y = np.cos(phase) + eccentricity * np.cos(periapsis)
    normalization = np.hypot(direction_x, direction_y)
    return (
        speed * direction_x / normalization,
        speed * np.cos(inclination) * direction_y / normalization,
    )


__all__ = [
    "MassComponents",
    "REQUIRED_COLUMNS",
    "SelectionConfig",
    "assign_multiplicity",
    "load_catalog",
    "phenomenological_external_field_ratio",
    "perturbed_projected_velocity_km_s",
    "projected_velocity_km_s",
    "sample_deprojected_accelerations",
    "sample_newtonian_control_velocity_km_s",
    "select_population",
]
