from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

from tools import analyze_gaia_wide_binary as analysis


def test_acceleration_bins_use_frozen_open_boundaries() -> None:
    log_newtonian = np.array([-11.5, -11.0, -9.8, -9.0, -8.5, -8.0, -7.5])
    residual = np.arange(len(log_newtonian), dtype=float) / 100
    log_kinematic = log_newtonian + residual * np.sqrt(2)

    medians, counts = analysis._bin_medians(log_newtonian, log_kinematic)

    assert counts.tolist() == [1, 1, 1]
    assert medians.tolist() == pytest.approx([0.01, 0.03, 0.05])


def test_analysis_rejects_unqualified_holdings(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog.csv"
    mass_relation = tmp_path / "mass.dat"
    catalog.write_text("not the catalog", encoding="utf-8")
    mass_relation.write_text("not the relation", encoding="utf-8")

    with pytest.raises(ValueError, match="frozen bytes"):
        analysis.analyze(catalog, mass_relation)


def test_confirmatory_ensemble_size_cannot_change() -> None:
    contract = analysis.json.loads(
        analysis.CONTRACT_PATH.read_text(encoding="utf-8")
    )

    analysis._validate_contract(contract)


def test_non_finite_failure_evidence_serializes_as_null(tmp_path: Path) -> None:
    output = tmp_path / "evidence.json"

    analysis._write_json_atomic(
        output,
        {"status": "incomplete", "failed_statistic": float("nan")},
    )

    assert analysis.json.loads(output.read_text(encoding="utf-8")) == {
        "failed_statistic": None,
        "status": "incomplete",
    }


def test_runner_writes_incomplete_receipt_on_analysis_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "failed.json"
    monkeypatch.setattr(
        analysis,
        "analyze",
        lambda *args, **kwargs: (_ for _ in ()).throw(ValueError("bad holding")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "analyze_gaia_wide_binary.py",
            "--catalog",
            "missing.csv",
            "--mass-relation",
            "missing.dat",
            "--output",
            str(output),
        ],
    )

    assert analysis.main() == 2
    receipt = analysis.json.loads(output.read_text(encoding="utf-8"))
    assert receipt["status"] == "incomplete"
    assert receipt["analysis_complete"] is False
    assert receipt["failure"] == {
        "message": "bad holding",
        "type": "ValueError",
    }
