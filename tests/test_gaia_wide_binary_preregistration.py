from __future__ import annotations

import hashlib
import json
from pathlib import Path

from emrf.validation.preregistration import verify_json_prediction

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "research" / "preregistrations" / "gaia_wide_binary_v1.json"
QUALIFICATION = (
    ROOT / "results" / "real_data_v1" / "gaia_wide_binary_method_qualification.json"
)
COMMITMENTS = ROOT / "research" / "commitments"
COMMITMENT_ID = "20261013T151329957398Z-27f69e8d6ff6"


def test_gaia_contract_is_bound_to_outcome_blind_qualification() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    qualification = json.loads(QUALIFICATION.read_text(encoding="utf-8"))

    assert contract["status"] == "preregistered-before-observational-outcome"
    assert contract["qualification"]["sha256"] == hashlib.sha256(
        QUALIFICATION.read_bytes()
    ).hexdigest()
    assert qualification["outcome_computed"] is False
    assert qualification["dirty"] is False
    assert contract["qualification"]["selected_identifier_sha256"] == qualification[
        "population"
    ]["selected_identifier_sha256"]
    assert contract["analysis"]["sampling"]["realizations"] == 2048
    assert contract["analysis"]["unresolved_multiplicity"][
        "primary_fraction"
    ] == 0.5
    assert contract["analysis"]["acceleration_bin_edges"] == [
        -11.5,
        -9.8,
        -8.5,
        -7.5,
    ]
    assert contract["comparators"][0]["classification"].startswith(
        "phenomenological comparator"
    )
    assert "failed convergence threshold" in contract["numerical_gate"][
        "failure_rule"
    ]


def test_gaia_contract_matches_named_commitment() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    record = json.loads(
        (COMMITMENTS / f"{COMMITMENT_ID}.json").read_text(encoding="utf-8")
    )

    assert record["commitment_id"] == COMMITMENT_ID
    assert record["label"] == "Gaia wide-binary v1 final"
    verification = verify_json_prediction(
        COMMITMENT_ID,
        contract,
        root=COMMITMENTS,
    )
    assert verification["matches"] is True
