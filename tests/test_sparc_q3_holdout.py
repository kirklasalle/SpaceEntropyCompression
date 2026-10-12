from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import numpy as np

from tools import run_sparc_profile_validation as profile_module
from tools import run_sparc_q3_holdout as holdout_module
from tools.run_sparc_q3_holdout import (
    _evaluate_hypothesis,
    _grid,
    _load_and_verify_contract,
)


def test_holdout_runner_loads_committed_contract_without_observations() -> None:
    contract = _load_and_verify_contract()
    grid = _grid(contract)

    assert contract["study_id"] == "sparc-q3-holdout-v1"
    assert grid[0] == 5e-11
    assert grid[-1] == 2.5e-10
    assert len(grid) == 43


def test_population_selection_reports_frozen_exclusions_and_missing_targets(
    tmp_path: Path,
    monkeypatch,
) -> None:
    (tmp_path / "SPARC_Lelli2016c.mrt").write_text("catalogue", encoding="utf-8")
    rotation_root = tmp_path / "Rotmod_LTG"
    rotation_root.mkdir()
    (rotation_root / "eligible_rotmod.dat").write_text("eligible", encoding="utf-8")
    (rotation_root / "short_rotmod.dat").write_text("short", encoding="utf-8")
    monkeypatch.setattr(
        holdout_module,
        "parse_sparc_table",
        lambda text: {
            "eligible": {"Q": 3, "Inc": 45.0},
            "short": {"Q": 3, "Inc": 45.0},
            "missing": {"Q": 3, "Inc": 45.0},
            "training": {"Q": 2, "Inc": 45.0},
        },
    )
    monkeypatch.setattr(
        holdout_module,
        "parse_rotmod",
        lambda text: np.ones((2 if text == "short" else 3, 6)),
    )
    galaxy = SimpleNamespace(name="eligible", quality=3)
    monkeypatch.setattr(holdout_module, "load_sparc", lambda *args, **kwargs: [galaxy])

    galaxies, excluded, failed = holdout_module._select_population(tmp_path)

    assert galaxies == [galaxy]
    assert excluded == [
        {"galaxy": "short", "reason": "fewer than three valid rows"}
    ]
    assert failed == [
        {"galaxy": "missing", "reason": "missing rotation-curve file"}
    ]


def test_holdout_criterion_is_closed_and_rejects_edges() -> None:
    hypothesis = {
        "id": "test",
        "law": "emrf_sqrt",
        "training_a0_grid_minimum_si": 1.6e-10,
        "training_delta_q_1_interval_si": [1.55e-10, 1.61e-10],
    }

    lower = _evaluate_hypothesis(
        hypothesis,
        {"a0_grid_minimum": 1.55e-10, "at_grid_edge": False},
    )
    edge = _evaluate_hypothesis(
        hypothesis,
        {"a0_grid_minimum": 1.6e-10, "at_grid_edge": True},
    )
    outside = _evaluate_hypothesis(
        hypothesis,
        {"a0_grid_minimum": 1.62e-10, "at_grid_edge": False},
    )

    assert lower["conditional_generalization_supported"] is True
    assert edge["outcome"] == "rejected"
    assert outside["outcome"] == "rejected"


def test_multi_start_diagnostics_count_failed_and_successful_attempts(
    monkeypatch,
) -> None:
    calls = 0

    def fake_least_squares(*args, **kwargs):
        nonlocal calls
        del args, kwargs
        calls += 1
        return SimpleNamespace(
            success=calls != 1,
            cost=float(calls),
            x=np.array([0.0, 1.0, 45.0]),
        )

    monkeypatch.setattr(profile_module, "least_squares", fake_least_squares)
    galaxy = SimpleNamespace(inclination_deg=45.0, name="probe")
    model = SimpleNamespace(
        gal=galaxy,
        sig_fd=0.1,
        sig_i=1.0,
        bounds=[(-1.3, 0.7), (0.5, 1.5), (30.0, 60.0)],
        vb2_disk=np.array([1.0]),
        vb2_star=np.array([1.0]),
        vb2_gas=np.array([1.0]),
        vb2_bul=np.array([0.0]),
        chi2=lambda x, nu, a0: 7.0,
    )
    diagnostics = {"attempts": 0, "successful": 0, "failed": 0, "cells": []}
    context = {
        "law": "emrf_sqrt",
        "direction": "forward",
        "galaxy": "probe",
        "a0": 1e-10,
    }

    objective, chi2, _ = profile_module.fit_one(
        model,
        lambda value: value,
        1e-10,
        0.5,
        diagnostics=diagnostics,
        diagnostic_context=context,
    )

    assert objective == 4.0
    assert chi2 == 7.0
    assert diagnostics == {
        "attempts": 3,
        "successful": 2,
        "failed": 1,
        "cells": [{**context, "successful": 2, "failed": 1}],
    }
