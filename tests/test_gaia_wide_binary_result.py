from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "results" / "real_data_v1" / "gaia_wide_binary_v1.json"
RESULT_SHA256 = "c19f828a221000981c08924be2197f238c75b34e7af66469956701f3bc5a6a0a"


def test_gaia_result_preserves_exact_protected_evidence() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    assert hashlib.sha256(RESULT.read_bytes()).hexdigest() == RESULT_SHA256
    assert result["revision"] == "05102abb581b7f5a87c1ec43977c5f53915b0586"
    assert result["dirty"] is False
    assert result["status"] == "incomplete"
    assert result["analysis_complete"] is False
    assert result["population"]["selected_rows"] == 19716
    assert result["population"]["selected_identifier_sha256"] == (
        "b03dc97483efec5c65cc8f392e3a34dca4baf8f0855e93e786fef651fe9415f4"
    )
    assert result["protocol_deviations"] == []
    assert all(
        hypothesis["outcome"] == "incomplete"
        for hypothesis in result["hypotheses"]
    )


def test_gaia_result_statistics_recompute_from_retained_realizations() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    for scenario in result["scenarios"].values():
        realizations = scenario["realizations"]
        observed = np.asarray(realizations["observed_median_dex"])
        control = np.asarray(realizations["control_median_dex"])
        residual = np.asarray(realizations["paired_residual_dex"])
        observed_counts = np.asarray(realizations["observed_counts"])
        control_counts = np.asarray(realizations["control_counts"])

        np.testing.assert_allclose(residual, observed - control, rtol=0, atol=1e-15)
        np.testing.assert_allclose(
            scenario["observed_median_dex"],
            np.median(observed, axis=0),
            rtol=0,
            atol=1e-15,
        )
        np.testing.assert_allclose(
            scenario["control_median_dex"],
            np.median(control, axis=0),
            rtol=0,
            atol=1e-15,
        )
        np.testing.assert_allclose(
            scenario["paired_residual_median_dex"],
            np.median(residual, axis=0),
            rtol=0,
            atol=1e-15,
        )
        np.testing.assert_allclose(
            scenario["paired_residual_interval_95_dex"],
            np.percentile(residual, [2.5, 97.5], axis=0).T,
            rtol=0,
            atol=1e-15,
        )
        assert scenario["minimum_observed_rows_per_bin"] == np.min(
            observed_counts,
            axis=0,
        ).tolist()
        assert scenario["minimum_control_rows_per_bin"] == np.min(
            control_counts,
            axis=0,
        ).tolist()


def test_gaia_result_failed_only_the_frozen_high_control_gate() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    for scenario in result["scenarios"].values():
        assert scenario["numerical_gate_passed"] is False
        assert abs(scenario["control_median_dex"][2]) > 0.01
        assert min(scenario["minimum_observed_rows_per_bin"]) >= 100
        assert min(scenario["minimum_control_rows_per_bin"]) >= 100
        assert max(scenario["convergence"]["median_difference_dex"]) <= 0.005
        assert (
            max(
                scenario["convergence"][
                    "interval_endpoint_difference_dex"
                ]
            )
            <= 0.01
        )
