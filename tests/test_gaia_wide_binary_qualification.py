from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pytest

from tools import qualify_gaia_wide_binary_method as qualification


def test_qualification_rejects_unqualified_catalog_bytes(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog.csv"
    catalog.write_text("not,the,catalog\n", encoding="utf-8")

    with pytest.raises(ValueError, match="do not match"):
        qualification.qualify(catalog)


def test_qualification_never_uses_observational_outcomes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    catalog = tmp_path / "catalog.csv"
    catalog.write_bytes(b"qualified")
    monkeypatch.setattr(qualification, "EXPECTED_CATALOG_BYTES", len(b"qualified"))
    monkeypatch.setattr(
        qualification,
        "EXPECTED_CATALOG_SHA256",
        hashlib.sha256(b"qualified").hexdigest(),
    )
    monkeypatch.setattr(
        qualification,
        "load_catalog",
        lambda path: np.zeros(qualification.EXPECTED_ROWS),
    )
    population = {
        "catalog_rows": qualification.EXPECTED_ROWS,
        "source_quality_rows": qualification.EXPECTED_SOURCE_QUALITY_ROWS,
        "selected_rows": qualification.EXPECTED_SELECTED_ROWS,
        "selected_identifier_sha256": qualification.EXPECTED_IDENTIFIER_SHA256,
    }
    monkeypatch.setattr(
        qualification,
        "select_population",
        lambda rows, config: (rows[: qualification.EXPECTED_SELECTED_ROWS], population),
    )
    monkeypatch.setattr(qualification, "_revision", lambda: ("revision", False))

    result = qualification.qualify(catalog)

    assert result["status"] == "qualified-for-preregistration"
    assert result["outcome_computed"] is False
    assert result["selection"]["observational_velocity_or_acceleration_used"] is False
    assert result["model"]["derived_first_principles_emrf_prediction"] is False
