"""Tests for immutable prediction hash commitments."""

from __future__ import annotations

import json

import pytest

from emergent_matter_model.emrf_prediction_access import (
    commit_json_prediction,
    commit_prediction,
    get_commitment,
    verify_json_prediction,
    verify_prediction,
)


def test_binary_prediction_commitment_stores_metadata_only(tmp_path):
    content = b"prediction before data access"
    record = commit_prediction(
        content,
        label="Blind lens prediction",
        source_name=r"C:\private\prediction.txt",
        root=tmp_path,
    )
    assert record["content_stored"] is False
    assert record["source_name"] == "prediction.txt"
    assert get_commitment(record["commitment_id"], root=tmp_path) == record
    assert verify_prediction(record["commitment_id"], content, root=tmp_path)["matches"]
    assert not verify_prediction(
        record["commitment_id"],
        b"changed",
        root=tmp_path,
    )["matches"]
    stored = json.loads(next(tmp_path.glob("*.json")).read_text())
    assert "prediction before data access" not in json.dumps(stored)


def test_json_commitment_is_canonical_and_order_independent(tmp_path):
    record = commit_json_prediction(
        {"omega_m": 0.31, "peaks": [220, 536, 813]},
        label="CMB preregistration",
        root=tmp_path,
    )
    verified = verify_json_prediction(
        record["commitment_id"],
        {"peaks": [220, 536, 813], "omega_m": 0.31},
        root=tmp_path,
    )
    assert verified["matches"]


@pytest.mark.parametrize("label", ["", "../unsafe", "x" * 101])
def test_invalid_commitment_labels_are_rejected(tmp_path, label):
    with pytest.raises(ValueError, match="label"):
        commit_prediction(b"prediction", label=label, root=tmp_path)
