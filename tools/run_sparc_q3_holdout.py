"""Execute the protected SPARC Q=3 holdout preregistration."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from emrf.validation.preregistration import verify_json_prediction

from emergent_matter_model.fetch_real_data import fetch_sparc
from emergent_matter_model.sparc_real_analysis import (
    a0_horizon,
    load_sparc,
    parse_rotmod,
    parse_sparc_table,
)
from tools.run_sparc_profile_validation import scan, summarize

CONTRACT_PATH = ROOT / "research" / "preregistrations" / "sparc_q3_holdout_v1.json"
COMMITMENTS_ROOT = ROOT / "research" / "commitments"
COMMITMENT_ID = "20261012T211327324282Z-d6ab49c9b4b7"
_SCHEMA_VERSION = "1.0.0"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}-",
        suffix=".part",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            json.dump(value, output, indent=2, sort_keys=True, allow_nan=False)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _load_and_verify_contract() -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    verification = verify_json_prediction(
        COMMITMENT_ID,
        contract,
        root=COMMITMENTS_ROOT,
    )
    if not verification["matches"]:
        raise ValueError("SPARC Q=3 preregistration does not match its commitment")
    training = ROOT / contract["training_reference"]["path"]
    if _sha256(training) != contract["training_reference"]["sha256"]:
        raise ValueError("Certified SPARC training result hash does not match")
    return contract


def _verify_observations(contract: dict[str, Any]) -> Path:
    sparc_path = fetch_sparc()
    for holding in contract["observations"]["holdings"]:
        path = ROOT / holding["path"]
        if (
            not path.is_file()
            or path.stat().st_size != holding["bytes"]
            or _sha256(path) != holding["sha256"]
        ):
            raise ValueError(f"SPARC holding does not match preregistration: {path}")
    return sparc_path


def _select_population(
    sparc_path: Path,
) -> tuple[list[Any], list[dict[str, str]], list[dict[str, str]]]:
    table = parse_sparc_table(
        (sparc_path / "SPARC_Lelli2016c.mrt").read_text(encoding="utf-8")
    )
    catalogue_candidates = {
        name
        for name, metadata in table.items()
        if metadata["Q"] == 3 and metadata["Inc"] >= 30.0
    }
    expected: set[str] = set()
    excluded: list[dict[str, str]] = []
    failed: list[dict[str, str]] = []
    rotation_root = sparc_path / "Rotmod_LTG"
    for name in sorted(catalogue_candidates):
        path = rotation_root / f"{name}_rotmod.dat"
        if not path.is_file():
            failed.append({"galaxy": name, "reason": "missing rotation-curve file"})
            continue
        values = parse_rotmod(path.read_text(encoding="utf-8"))
        valid = values[(values[:, 0] > 0) & (values[:, 1] > 0)]
        if len(valid) < 3:
            excluded.append(
                {"galaxy": name, "reason": "fewer than three valid rows"}
            )
            continue
        expected.add(name)

    galaxies = [
        galaxy
        for galaxy in load_sparc(
            sparc_path,
            max_quality=3,
            min_inclination=30.0,
        )
        if galaxy.quality == 3
    ]
    loaded = {galaxy.name for galaxy in galaxies}
    for name in sorted(expected - loaded):
        failed.append({"galaxy": name, "reason": "eligible target was not loaded"})
    for name in sorted(loaded - expected):
        failed.append({"galaxy": name, "reason": "loaded target was not independently eligible"})
    return galaxies, excluded, failed


def _grid(contract: dict[str, Any]) -> np.ndarray:
    specification = contract["analysis"]["a0_grid_si"]
    span_in_steps = (
        (specification["stop"] - specification["start"]) / specification["step"]
    )
    count = round(span_in_steps)
    if not np.isclose(span_in_steps, count, rtol=0.0, atol=1e-12):
        raise ValueError("Preregistered acceleration grid does not end on its step")
    regular = np.linspace(specification["start"], specification["stop"], count + 1)
    horizons = [
        a0_horizon(value)
        for value in specification["include_horizon_values_for_h0_km_s_mpc"]
    ]
    return np.unique(np.r_[regular, horizons])


def _evaluate_hypothesis(
    hypothesis: dict[str, Any],
    profile: dict[str, Any],
) -> dict[str, Any]:
    lower, upper = hypothesis["training_delta_q_1_interval_si"]
    minimum = profile["a0_grid_minimum"]
    supported = not profile["at_grid_edge"] and lower <= minimum <= upper
    return {
        "id": hypothesis["id"],
        "law": hypothesis["law"],
        "training_a0_grid_minimum_si": hypothesis["training_a0_grid_minimum_si"],
        "training_delta_q_1_interval_si": [lower, upper],
        "holdout_a0_grid_minimum_si": minimum,
        "holdout_at_grid_edge": profile["at_grid_edge"],
        "conditional_generalization_supported": supported,
        "outcome": "consistent" if supported else "rejected",
        "interpretation": (
            "Conditional same-catalogue generalization screen; not calibrated "
            "significance or independent replication."
        ),
    }


def run_holdout(output: Path) -> dict[str, Any]:
    contract = _load_and_verify_contract()
    sparc_path = _verify_observations(contract)
    galaxies, excluded_targets, failed_targets = _select_population(sparc_path)
    if not galaxies:
        raise ValueError("Preregistered SPARC Q=3 population is empty")
    grid = _grid(contract)
    profiles: dict[str, Any] = {}
    outcomes: list[dict[str, Any]] = []
    maximum_difference = contract["numerical_gate"][
        "maximum_forward_reverse_total_q_difference"
    ]

    for hypothesis in contract["hypotheses"]:
        law = hypothesis["law"]
        forward_diagnostics = {
            "attempts": 0,
            "successful": 0,
            "failed": 0,
            "cells": [],
        }
        reverse_diagnostics = {
            "attempts": 0,
            "successful": 0,
            "failed": 0,
            "cells": [],
        }
        objective, chi = scan(
            galaxies,
            grid,
            law=law,
            diagnostics=forward_diagnostics,
        )
        reverse, _ = scan(
            galaxies,
            grid,
            law=law,
            reverse=True,
            diagnostics=reverse_diagnostics,
        )
        forward_total = objective.sum(axis=1)
        reverse_total = reverse.sum(axis=1)
        scan_differences = np.abs(reverse_total - forward_total)
        scan_difference = float(np.max(scan_differences))
        convergence_gate_passed = all(
            cell["successful"] >= 1
            for diagnostics in (forward_diagnostics, reverse_diagnostics)
            for cell in diagnostics["cells"]
        )
        profile = summarize(galaxies, grid, objective, chi)
        profile.update(
            chi2_data_grid=chi.sum(axis=1).tolist(),
            reverse_objective_grid=reverse_total.tolist(),
            forward_reverse_total_q_differences=scan_differences.tolist(),
            forward_optimizer_attempts=forward_diagnostics,
            reverse_optimizer_attempts=reverse_diagnostics,
            reverse_scan_max_total_q_difference=scan_difference,
            convergence_gate_passed=convergence_gate_passed,
            numerical_gate_passed=(
                convergence_gate_passed and scan_difference <= maximum_difference
            ),
        )
        profiles[law] = profile
        outcomes.append(_evaluate_hypothesis(hypothesis, profile))

    numerical_gate_passed = all(
        profile["numerical_gate_passed"] for profile in profiles.values()
    )
    population_gate_passed = not failed_targets
    analysis_complete = numerical_gate_passed and population_gate_passed
    if not analysis_complete:
        for outcome in outcomes:
            outcome["conditional_generalization_supported"] = None
            outcome["outcome"] = "indeterminate-invalid-run"
    primary = next(
        outcome
        for outcome in outcomes
        if outcome["id"] == "H1-emrf-sqrt-generalization"
    )
    if analysis_complete:
        status = "complete"
    elif not population_gate_passed:
        status = "incomplete-population"
    else:
        status = "invalid-numerical-gate"
    result = {
        "schema_version": _SCHEMA_VERSION,
        "study_id": contract["study_id"],
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "analysis_complete": analysis_complete,
        "evidence_class": contract["evidence_class"],
        "evidence_qualification": (
            "Prospective same-catalogue lower-quality holdout; not blind discovery, "
            "calibrated significance, or independent replication."
        ),
        "preregistration": {
            "path": str(CONTRACT_PATH.relative_to(ROOT)).replace("\\", "/"),
            "commitment_id": COMMITMENT_ID,
            "canonical_sha256": json.loads(
                (COMMITMENTS_ROOT / f"{COMMITMENT_ID}.json").read_text(
                    encoding="utf-8"
                )
            )["sha256"],
        },
        "command": sys.argv,
        "revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT
        ).decode().strip(),
        "dirty": bool(
            subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT)
        ),
        "platform": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "system": platform.system(),
            "machine": platform.machine(),
        },
        "inputs": {
            holding["path"]: {
                "bytes": holding["bytes"],
                "sha256": holding["sha256"],
                "url": holding["url"],
            }
            for holding in contract["observations"]["holdings"]
        },
        "training_reference": contract["training_reference"],
        "population": {
            "quality": 3,
            "minimum_inclination_degrees": 30.0,
            "galaxies": len(galaxies),
            "points": sum(galaxy.n for galaxy in galaxies),
            "names": [galaxy.name for galaxy in galaxies],
            "excluded_by_frozen_rules": excluded_targets,
            "failed_or_missing_targets": failed_targets,
            "population_gate_passed": population_gate_passed,
        },
        "a0_grid_si": grid.tolist(),
        "profiles": profiles,
        "hypotheses": outcomes,
        "primary_claim_supported": primary[
            "conditional_generalization_supported"
        ],
        "BIC": None,
        "BIC_reason": "The objective includes nuisance penalties and is not an unpenalized maximum likelihood.",
        "protocol_deviations": [],
        "limitations": [
            "SPARC radial covariance is unavailable and was not invented.",
            "Q=3 is a lower-quality same-catalogue challenge sample.",
            "Delta-Q=1 intervals are conditional profile summaries, not calibrated confidence intervals.",
            "Passing or failing this screen does not prove or disprove a physical theory.",
        ],
    }
    _write_json_atomic(output, result)
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    output = args.output.expanduser().resolve()
    try:
        result = run_holdout(output)
    except Exception as exc:  # noqa: BLE001
        failure = {
            "schema_version": _SCHEMA_VERSION,
            "study_id": "sparc-q3-holdout-v1",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "status": "incomplete",
            "analysis_complete": False,
            "error": {"type": type(exc).__name__, "message": str(exc)},
        }
        _write_json_atomic(output, failure)
        print(json.dumps(failure, indent=2, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["analysis_complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
