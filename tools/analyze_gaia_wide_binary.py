"""Execute the preregistered Gaia wide-binary compatibility analysis."""

from __future__ import annotations

import argparse
import contextlib
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

ROOT = Path(__file__).resolve().parents[1]
MODEL_ROOT = ROOT / "emergent_matter_model"
SOURCE_ROOT = MODEL_ROOT / "src"
for source in (MODEL_ROOT, SOURCE_ROOT):
    source_text = str(source)
    if source_text not in sys.path:
        sys.path.insert(0, source_text)

from emrf.validation.preregistration import verify_json_prediction  # noqa: E402
from emrf.validation.wide_binaries import (  # noqa: E402
    assign_multiplicity,
    load_catalog,
    perturbed_projected_velocity_km_s,
    sample_deprojected_accelerations,
    sample_newtonian_control_velocity_km_s,
    select_population,
)

CONTRACT_PATH = ROOT / "research" / "preregistrations" / "gaia_wide_binary_v1.json"
QUALIFICATION_PATH = (
    ROOT / "results" / "real_data_v1" / "gaia_wide_binary_method_qualification.json"
)
COMMITMENTS_PATH = ROOT / "research" / "commitments"
COMMITMENT_ID = "20261013T152653227562Z-58b1e63993fa"
CATALOG_SHA256 = "0b10a6e66d59bc781c0902a3cd3dc2c37db5ffdc9677113e0cdd54f9c80d6804"
CATALOG_BYTES = 46_642_671
MASS_RELATION_SHA256 = (
    "9dee3bde5356254c028d50e933b2005bd0b6ce7dd4a78a376f100f3cb617ed11"
)
MASS_RELATION_BYTES = 352
BASE_SEED = 2_026_101_301
REALIZATIONS = 2_048
BIN_EDGES = np.array([-11.5, -9.8, -8.5, -7.5])
MULTIPLICITY_FRACTIONS = (0.5, 0.3, 0.7)
COMPARATOR_LOW = 0.1278055783326812
COMPARATOR_MID = 0.012656679930213948


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _verify_holding(
    path: Path,
    *,
    expected_bytes: int,
    expected_sha256: str,
) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"Required Gaia holding does not exist: {path}")
    if path.stat().st_size != expected_bytes or _sha256(path) != expected_sha256:
        raise ValueError(f"Gaia holding does not match its frozen bytes: {path}")


def _revision() -> tuple[str, bool]:
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return revision, bool(status)


def _bin_medians(
    log_newtonian: np.ndarray,
    log_kinematic: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    residual = (log_kinematic - log_newtonian) / np.sqrt(2)
    medians = np.empty(3)
    counts = np.empty(3, dtype=int)
    for index, (lower, upper) in enumerate(
        zip(BIN_EDGES[:-1], BIN_EDGES[1:], strict=True)
    ):
        selected = (log_newtonian > lower) & (log_newtonian < upper)
        counts[index] = np.count_nonzero(selected)
        medians[index] = np.median(residual[selected]) if counts[index] else np.nan
    return medians, counts


def _validate_contract(contract: dict[str, Any]) -> None:
    sampling = contract["analysis"]["sampling"]
    nuisance = contract["analysis"]["unresolved_multiplicity"]
    comparators = contract["comparators"][0]
    numerical = contract["numerical_gate"]
    expected = {
        "base_seed": BASE_SEED,
        "realizations": REALIZATIONS,
        "bin_edges": BIN_EDGES.tolist(),
        "primary_fraction": MULTIPLICITY_FRACTIONS[0],
        "sensitivity_fractions": list(MULTIPLICITY_FRACTIONS[1:]),
        "low_comparator": COMPARATOR_LOW,
        "mid_comparator": COMPARATOR_MID,
        "minimum_rows": 100,
        "control_max": 0.01,
        "median_convergence_max": 0.005,
        "interval_convergence_max": 0.01,
    }
    actual = {
        "base_seed": sampling["base_seed"],
        "realizations": sampling["realizations"],
        "bin_edges": contract["analysis"]["acceleration_bin_edges"],
        "primary_fraction": nuisance["primary_fraction"],
        "sensitivity_fractions": nuisance["sensitivity_fractions"],
        "low_comparator": comparators[
            "low_predicted_orthogonal_residual_dex"
        ],
        "mid_comparator": comparators[
            "mid_predicted_orthogonal_residual_dex"
        ],
        "minimum_rows": numerical["minimum_rows_per_bin_per_realization"],
        "control_max": numerical[
            "newtonian_high_control_absolute_median_max_dex"
        ],
        "median_convergence_max": numerical[
            "maximum_convergence_median_difference_dex"
        ],
        "interval_convergence_max": numerical[
            "maximum_convergence_interval_endpoint_difference_dex"
        ],
    }
    if actual != expected:
        raise ValueError("Analyzer constants do not match the committed contract")


def _summarize_scenario(
    observed: np.ndarray,
    control: np.ndarray,
    residual: np.ndarray,
    observed_counts: np.ndarray,
    control_counts: np.ndarray,
) -> dict[str, Any]:
    first = residual[: REALIZATIONS // 2]
    full_median = np.median(residual, axis=0)
    first_median = np.median(first, axis=0)
    full_interval = np.percentile(residual, [2.5, 97.5], axis=0).T
    first_interval = np.percentile(first, [2.5, 97.5], axis=0).T
    return {
        "observed_median_dex": np.median(observed, axis=0).tolist(),
        "control_median_dex": np.median(control, axis=0).tolist(),
        "paired_residual_median_dex": full_median.tolist(),
        "paired_residual_interval_95_dex": full_interval.tolist(),
        "minimum_observed_rows_per_bin": np.min(observed_counts, axis=0).tolist(),
        "minimum_control_rows_per_bin": np.min(control_counts, axis=0).tolist(),
        "convergence": {
            "median_difference_dex": np.abs(full_median - first_median).tolist(),
            "interval_endpoint_difference_dex": np.max(
                np.abs(full_interval - first_interval),
                axis=1,
            ).tolist(),
        },
        "realizations": {
            "observed_median_dex": observed.tolist(),
            "control_median_dex": control.tolist(),
            "paired_residual_dex": residual.tolist(),
            "observed_counts": observed_counts.tolist(),
            "control_counts": control_counts.tolist(),
        },
    }


def analyze(
    catalog_path: str | Path,
    mass_relation_path: str | Path,
    *,
    realizations: int = REALIZATIONS,
) -> dict[str, Any]:
    catalog = Path(catalog_path)
    mass_relation = Path(mass_relation_path)
    _verify_holding(
        catalog,
        expected_bytes=CATALOG_BYTES,
        expected_sha256=CATALOG_SHA256,
    )
    _verify_holding(
        mass_relation,
        expected_bytes=MASS_RELATION_BYTES,
        expected_sha256=MASS_RELATION_SHA256,
    )
    if realizations != REALIZATIONS:
        raise ValueError(f"Confirmatory execution requires {REALIZATIONS} realizations")

    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    _validate_contract(contract)
    commitment = verify_json_prediction(
        COMMITMENT_ID,
        contract,
        root=COMMITMENTS_PATH,
    )
    if not commitment["matches"]:
        raise ValueError("Gaia preregistration does not match its commitment")
    qualification_sha256 = _sha256(QUALIFICATION_PATH)
    if qualification_sha256 != contract["qualification"]["sha256"]:
        raise ValueError("Gaia qualification receipt does not match the contract")

    rows, population = select_population(load_catalog(catalog))
    if population["selected_rows"] != contract["population"]["expected_selected_rows"]:
        raise ValueError("Gaia selected population count changed")
    if (
        population["selected_identifier_sha256"]
        != contract["qualification"]["selected_identifier_sha256"]
    ):
        raise ValueError("Gaia selected population identity changed")

    coefficients = np.loadtxt(
        mass_relation,
        skiprows=1,
        usecols=1,
        dtype=float,
    )
    anchor_magnitudes = np.array([4.0, 4.83, 8.0, 14.0])
    anchor_masses = np.power(
        10.0,
        np.polynomial.polynomial.polyval(anchor_magnitudes, coefficients),
    )
    if (
        coefficients.shape != (11,)
        or not np.all(np.diff(anchor_masses) < 0)
        or not 0.95 <= anchor_masses[1] <= 1.05
        or not 0.05 <= anchor_masses[-1] <= 0.2
    ):
        raise ValueError("Frozen mass-magnitude relation failed physical anchors")
    scenarios: dict[str, Any] = {}
    complete = True
    for scenario_index, fraction in enumerate(MULTIPLICITY_FRACTIONS):
        observed = np.empty((REALIZATIONS, 3))
        control = np.empty((REALIZATIONS, 3))
        observed_counts = np.empty((REALIZATIONS, 3), dtype=int)
        control_counts = np.empty((REALIZATIONS, 3), dtype=int)
        for realization in range(REALIZATIONS):
            streams = np.random.SeedSequence(
                [BASE_SEED, scenario_index, realization]
            ).spawn(6)
            bootstrap_rng = np.random.default_rng(streams[0])
            observed_deprojection_rng = np.random.default_rng(streams[1])
            proper_motion_rng = np.random.default_rng(streams[2])
            multiplicity_rng = np.random.default_rng(streams[3])
            companion_rng = np.random.default_rng(streams[4])
            control_rng = np.random.default_rng(streams[5])

            sampled = rows[bootstrap_rng.integers(0, len(rows), len(rows))]
            components = assign_multiplicity(
                sampled,
                mass_magnitude_coefficients=coefficients,
                fraction=fraction,
                rng=multiplicity_rng,
            )
            total_mass = components.total_a + components.total_b
            observed_velocity = perturbed_projected_velocity_km_s(
                sampled,
                proper_motion_rng,
            )
            control_velocity = sample_newtonian_control_velocity_km_s(
                sampled,
                components,
                orbit_rng=control_rng,
                companion_rng=companion_rng,
                proper_motion_rng=proper_motion_rng,
            )
            observed_accelerations = sample_deprojected_accelerations(
                projected_separation_kau=sampled["skau"],
                total_mass_msun=total_mass,
                projected_velocity_km_s=observed_velocity,
                eccentricity=sampled["e"],
                eccentricity_low=sampled["e0"],
                eccentricity_high=sampled["e1"],
                rng=observed_deprojection_rng,
            )
            control_accelerations = sample_deprojected_accelerations(
                projected_separation_kau=sampled["skau"],
                total_mass_msun=total_mass,
                projected_velocity_km_s=control_velocity,
                eccentricity=sampled["e"],
                eccentricity_low=sampled["e0"],
                eccentricity_high=sampled["e1"],
                rng=control_rng,
            )
            observed[realization], observed_counts[realization] = _bin_medians(
                *observed_accelerations
            )
            control[realization], control_counts[realization] = _bin_medians(
                *control_accelerations
            )

        residual = observed - control
        summary = _summarize_scenario(
            observed,
            control,
            residual,
            observed_counts,
            control_counts,
        )
        scenario_complete = (
            np.all(np.isfinite(residual))
            and np.min(observed_counts) >= 100
            and np.min(control_counts) >= 100
            and abs(summary["control_median_dex"][2]) <= 0.01
            and max(summary["convergence"]["median_difference_dex"]) <= 0.005
            and max(
                summary["convergence"]["interval_endpoint_difference_dex"]
            )
            <= 0.01
        )
        summary["numerical_gate_passed"] = bool(scenario_complete)
        complete = complete and bool(scenario_complete)
        scenarios[str(fraction)] = summary

    revision, dirty = _revision()
    complete = complete and not dirty
    primary = scenarios["0.5"]
    low_interval = primary["paired_residual_interval_95_dex"][0]
    mid_interval = primary["paired_residual_interval_95_dex"][1]

    def outcome(value: float, interval: list[float]) -> str:
        if not complete:
            return "incomplete"
        return "compatible" if interval[0] <= value <= interval[1] else "rejected"

    result = {
        "schema_version": "1.0.0",
        "study_id": "gaia-wide-binary-v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "complete" if complete else "incomplete",
        "analysis_complete": bool(complete),
        "revision": revision,
        "dirty": dirty,
        "inputs": {
            "catalog": {
                "bytes": CATALOG_BYTES,
                "sha256": CATALOG_SHA256,
            },
            "mass_magnitude_relation": {
                "bytes": MASS_RELATION_BYTES,
                "sha256": MASS_RELATION_SHA256,
            },
            "qualification_sha256": qualification_sha256,
            "commitment_id": COMMITMENT_ID,
            "commitment_sha256": commitment["expected_sha256"],
        },
        "population": population,
        "sampling": {
            "base_seed": BASE_SEED,
            "realizations": REALIZATIONS,
            "bin_edges": BIN_EDGES.tolist(),
            "multiplicity_fractions": list(MULTIPLICITY_FRACTIONS),
        },
        "scenarios": scenarios,
        "hypotheses": [
            {
                "id": "H1-low-external-field-compatibility",
                "comparator_dex": COMPARATOR_LOW,
                "interval_95_dex": low_interval,
                "outcome": outcome(COMPARATOR_LOW, low_interval),
            },
            {
                "id": "H2-low-newtonian-compatibility",
                "comparator_dex": 0.0,
                "interval_95_dex": low_interval,
                "outcome": outcome(0.0, low_interval),
            },
            {
                "id": "H3-mid-external-field-compatibility",
                "comparator_dex": COMPARATOR_MID,
                "interval_95_dex": mid_interval,
                "outcome": outcome(COMPARATOR_MID, mid_interval),
            },
        ],
        "protocol_deviations": [],
        "platform": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "system": platform.platform(),
        },
        "limitations": contract["interpretation"]["not_claimed"],
    }
    return result


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(
                _json_safe(payload),
                stream,
                indent=2,
                sort_keys=True,
                allow_nan=False,
            )
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--mass-relation", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    try:
        result = analyze(arguments.catalog, arguments.mass_relation)
    except Exception as exc:
        revision = None
        dirty = None
        with contextlib.suppress(OSError, subprocess.CalledProcessError):
            revision, dirty = _revision()
        result = {
            "schema_version": "1.0.0",
            "study_id": "gaia-wide-binary-v1",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "status": "incomplete",
            "analysis_complete": False,
            "revision": revision,
            "dirty": dirty,
            "failure": {
                "type": type(exc).__name__,
                "message": str(exc),
            },
            "protocol_deviations": [],
        }
        print(f"Gaia analysis failed: {type(exc).__name__}: {exc}", file=sys.stderr)
    _write_json_atomic(arguments.output, result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "analysis_complete": result["analysis_complete"],
                "revision": result["revision"],
                "dirty": result["dirty"],
                "population": result.get("population"),
                "hypotheses": result.get("hypotheses"),
                "failure": result.get("failure"),
                "numerical_gates": {
                    fraction: scenario["numerical_gate_passed"]
                    for fraction, scenario in result.get("scenarios", {}).items()
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if result["analysis_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
