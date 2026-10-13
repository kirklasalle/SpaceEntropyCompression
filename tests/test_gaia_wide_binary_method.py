from __future__ import annotations

import numpy as np
import pytest

from emrf.validation.wide_binaries import (
    REQUIRED_COLUMNS,
    SelectionConfig,
    phenomenological_external_field_ratio,
    sample_deprojected_accelerations,
    select_population,
)


def _rows(count: int = 2) -> np.ndarray:
    dtype = [(name, "f8") for name in REQUIRED_COLUMNS]
    rows = np.zeros(count, dtype=dtype)
    rows["source_id1"] = np.arange(1, count + 1)
    rows["source_id2"] = np.arange(101, 101 + count)
    rows["R_chance"] = 0.001
    rows["skau"] = 1.0
    rows["d1pc"] = 100.0
    rows["d1_errpc"] = 0.2
    rows["d2pc"] = 100.1
    rows["d2_errpc"] = 0.2
    rows["MagG1"] = 8.0
    rows["MagG2"] = 8.5
    rows["mu1ramasyr"] = 100.0
    rows["mu1ra_errmasyr"] = 0.1
    rows["mu1decmasyr"] = 80.0
    rows["mu1dec_errmasyr"] = 0.1
    rows["mu2ramasyr"] = 99.0
    rows["mu2ra_errmasyr"] = 0.1
    rows["mu2decmasyr"] = 79.0
    rows["mu2dec_errmasyr"] = 0.1
    rows["bp_rp1"] = 2.0
    rows["bp_rp2"] = 2.0
    rows["DEC1deg"] = 10.0
    rows["e"] = 0.5
    rows["e0"] = 0.2
    rows["e1"] = 0.8
    return rows


def test_selection_reports_population_and_identifier_hash() -> None:
    rows = _rows()
    rows["R_chance"][1] = 0.02

    selected, audit = select_population(rows)

    assert selected["source_id1"].tolist() == [1.0]
    assert audit == {
        "catalog_rows": 2,
        "source_quality_rows": 1,
        "selected_rows": 1,
        "selected_identifier_sha256": (
            "8e3388a020038843fd71630a0a9a8976bb50f15406ef7932d4e8e71ab71c5c54"
        ),
    }


def test_selection_uses_open_frozen_boundaries() -> None:
    rows = _rows(3)
    rows["skau"] = [0.2, 30.0, 1.0]

    selected, audit = select_population(rows, SelectionConfig())

    assert selected["source_id1"].tolist() == [3.0]
    assert audit["source_quality_rows"] == 3


def test_deprojection_is_deterministic_and_physical() -> None:
    kwargs = {
        "projected_separation_kau": np.array([1.0, 8.0]),
        "total_mass_msun": np.array([1.5, 1.0]),
        "projected_velocity_km_s": np.array([0.8, 0.2]),
        "eccentricity": np.array([0.5, 0.7]),
        "eccentricity_low": np.array([0.2, 0.4]),
        "eccentricity_high": np.array([0.8, 0.9]),
    }

    first = sample_deprojected_accelerations(
        **kwargs,
        rng=np.random.default_rng(20261013),
    )
    second = sample_deprojected_accelerations(
        **kwargs,
        rng=np.random.default_rng(20261013),
    )

    assert first[0] == pytest.approx(second[0], rel=0, abs=0)
    assert first[1] == pytest.approx(second[1], rel=0, abs=0)
    assert np.all(np.isfinite(first[0]))
    assert np.all(np.isfinite(first[1]))


def test_phenomenological_model_has_newtonian_limit_and_finite_boost() -> None:
    ratios = phenomenological_external_field_ratio(
        np.array([1e-6, 1e-10, 1e-12])
    )

    assert ratios[0] == pytest.approx(1.0, abs=1e-12)
    assert np.all(ratios >= 1)
    assert np.all(np.isfinite(ratios))
