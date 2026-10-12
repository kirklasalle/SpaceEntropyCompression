from __future__ import annotations

import hashlib
import json
from pathlib import Path

from emrf.validation.preregistration import verify_json_prediction

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "research" / "preregistrations" / "sparc_q3_holdout_v1.json"
COMMITMENTS = ROOT / "research" / "commitments"
TRAINING = ROOT / "results" / "real_data_v1" / "sparc_profile_validation.json"


def test_sparc_q3_contract_is_bound_to_certified_inputs() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    assert contract["status"] == "preregistered-before-holdout-fit"
    assert contract["population"]["include"][0] == (
        "SPARC catalogue quality flag Q equals 3"
    )
    assert contract["population"]["exclusions"].startswith(
        "No galaxy satisfying every frozen rule"
    )
    assert contract["training_reference"]["sha256"] == hashlib.sha256(
        TRAINING.read_bytes()
    ).hexdigest()
    assert [hypothesis["law"] for hypothesis in contract["hypotheses"]] == [
        "emrf_sqrt",
        "rar_exponential",
    ]
    assert contract["numerical_gate"][
        "maximum_forward_reverse_total_q_difference"
    ] == 0.1
    assert "changing thresholds after viewing Q=3 outcomes" in contract[
        "reporting"
    ]["forbidden"]


def test_sparc_q3_contract_matches_public_commitment() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    records = list(COMMITMENTS.glob("*.json"))

    assert len(records) == 1
    record = json.loads(records[0].read_text(encoding="utf-8"))
    assert record["label"] == "SPARC Q3 holdout v1"
    verification = verify_json_prediction(
        record["commitment_id"],
        contract,
        root=COMMITMENTS,
    )
    assert verification["matches"] is True
