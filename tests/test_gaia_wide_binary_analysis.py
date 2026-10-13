from __future__ import annotations

import numpy as np
import pytest
from emrf.validation.wide_binaries import (
    REQUIRED_COLUMNS,
    _project_orbital_velocity,
    assign_multiplicity,
    perturbed_projected_velocity_km_s,
    sample_newtonian_control_velocity_km_s,
)


def _rows(count: int = 64) -> np.ndarray:
    rows = np.zeros(count, dtype=[(name, "f8") for name in REQUIRED_COLUMNS])
    rows["source_id1"] = np.arange(1, count + 1)
    rows["source_id2"] = np.arange(101, 101 + count)
    rows["skau"] = np.linspace(0.5, 20, count)
    rows["d1pc"] = 100
    rows["d2pc"] = 100.1
    rows["d1_errpc"] = 0.2
    rows["d2_errpc"] = 0.3
    rows["MagG1"] = 8
    rows["MagG2"] = 9
    rows["mu1ramasyr"] = 10
    rows["mu2ramasyr"] = 9
    rows["mu1decmasyr"] = 5
    rows["mu2decmasyr"] = 4
    for name in (
        "mu1ra_errmasyr",
        "mu2ra_errmasyr",
        "mu1dec_errmasyr",
        "mu2dec_errmasyr",
    ):
        rows[name] = 0.01
    rows["e"] = 0.6
    rows["e0"] = 0.3
    rows["e1"] = 0.9
    return rows


def test_multiplicity_and_newtonian_control_are_deterministic() -> None:
    rows = _rows()
    coefficients = np.zeros(11)
    coefficients[0] = 0.0
    first_components = assign_multiplicity(
        rows,
        mass_magnitude_coefficients=coefficients,
        fraction=0.5,
        rng=np.random.default_rng(1),
    )
    second_components = assign_multiplicity(
        rows,
        mass_magnitude_coefficients=coefficients,
        fraction=0.5,
        rng=np.random.default_rng(1),
    )

    np.testing.assert_array_equal(
        first_components.total_a,
        second_components.total_a,
    )
    np.testing.assert_array_equal(
        first_components.total_b,
        second_components.total_b,
    )

    def control() -> np.ndarray:
        return sample_newtonian_control_velocity_km_s(
            rows,
            first_components,
            orbit_rng=np.random.default_rng(2),
            companion_rng=np.random.default_rng(3),
            proper_motion_rng=np.random.default_rng(4),
        )

    np.testing.assert_array_equal(control(), control())
    assert np.all(np.isfinite(control()))
    assert np.all(control() > 0)


def test_observational_velocity_perturbation_is_deterministic() -> None:
    rows = _rows()

    first = perturbed_projected_velocity_km_s(rows, np.random.default_rng(5))
    second = perturbed_projected_velocity_km_s(rows, np.random.default_rng(5))

    np.testing.assert_array_equal(first, second)
    assert np.all(first > 0)


def test_projected_orbital_velocity_retains_eccentric_direction() -> None:
    velocity_x, velocity_y = _project_orbital_velocity(
        speed=np.array([1.0]),
        phase=np.array([np.pi / 2]),
        inclination=np.array([0.0]),
        eccentricity=np.array([0.8]),
        periapsis=np.array([0.0]),
    )

    assert velocity_x[0] < 0
    assert velocity_y[0] > 0
    assert np.hypot(velocity_x[0], velocity_y[0]) == pytest.approx(1.0)
