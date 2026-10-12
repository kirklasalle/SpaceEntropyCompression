from __future__ import annotations

import hashlib
import json
from pathlib import Path

from emrf.validation.preregistration import verify_json_prediction

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "research" / "preregistrations" / "sparc_q3_holdout_v1.json"
COMMITMENTS = ROOT / "research" / "commitments"
COMMITMENT_ID = "20261012T211327324282Z-d6ab49c9b4b7"
TRAINING = ROOT / "results" / "real_data_v1" / "sparc_profile_validation.json"
RESULT = ROOT / "results" / "real_data_v1" / "sparc_q3_holdout_v1.json"
RESULT_SHA256 = "87dea72269652bea6e24d03876dfe4c65075d7254031b2852e31a09add55231a"


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
    assert contract["numerical_gate"]["convergence_requirement"].startswith(
        "For every galaxy, acceleration-grid value, scan direction, and law"
    )
    assert "successful and failed start counts must be reported" in contract[
        "numerical_gate"
    ]["convergence_requirement"]
    assert "changing thresholds after viewing Q=3 outcomes" in contract[
        "reporting"
    ]["forbidden"]


def test_sparc_q3_contract_matches_public_commitment() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    record_path = COMMITMENTS / f"{COMMITMENT_ID}.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))

    assert record["commitment_id"] == COMMITMENT_ID
    assert record["label"] == "SPARC Q3 holdout v1"
    verification = verify_json_prediction(
        COMMITMENT_ID,
        contract,
        root=COMMITMENTS,
    )
    assert verification["matches"] is True


def test_sparc_q3_result_preserves_protected_outcome() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    assert hashlib.sha256(RESULT.read_bytes()).hexdigest() == RESULT_SHA256
    assert result["revision"] == "f09633b6bded2b239372dd76630b1e38d92e0992"
    assert result["status"] == "complete"
    assert result["analysis_complete"] is True
    assert result["dirty"] is False
    assert result["population"]["population_gate_passed"] is True
    assert result["population"]["galaxies"] == 10
    assert result["population"]["points"] == 109
    assert result["protocol_deviations"] == []
    assert [hypothesis["outcome"] for hypothesis in result["hypotheses"]] == [
        "rejected",
        "rejected",
    ]
    assert all(
        profile["convergence_gate_passed"] and profile["numerical_gate_passed"]
        for profile in result["profiles"].values()
    )
