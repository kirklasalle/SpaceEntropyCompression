"""Qualify the Gaia study population and model without computing its outcome."""

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

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MODEL_ROOT = ROOT / "emergent_matter_model"
SOURCE_ROOT = MODEL_ROOT / "src"
for source in (ROOT, MODEL_ROOT, SOURCE_ROOT):
    source_text = str(source)
    if source_text not in sys.path:
        sys.path.insert(0, source_text)

from emrf.validation.wide_binaries import (  # noqa: E402
    SelectionConfig,
    load_catalog,
    phenomenological_external_field_ratio,
    select_population,
)

EXPECTED_CATALOG_SHA256 = (
    "0b10a6e66d59bc781c0902a3cd3dc2c37db5ffdc9677113e0cdd54f9c80d6804"
)
EXPECTED_CATALOG_BYTES = 46642671
EXPECTED_ROWS = 81880
EXPECTED_SOURCE_QUALITY_ROWS = 45126
EXPECTED_SELECTED_ROWS = 19716
EXPECTED_IDENTIFIER_SHA256 = (
    "b03dc97483efec5c65cc8f392e3a34dca4baf8f0855e93e786fef651fe9415f4"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _revision() -> tuple[str | None, bool | None]:
    try:
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None, None
    return revision, dirty


def qualify(catalog: Path) -> dict:
    catalog = catalog.expanduser().resolve()
    size = catalog.stat().st_size
    digest = _sha256(catalog)
    if size != EXPECTED_CATALOG_BYTES or digest != EXPECTED_CATALOG_SHA256:
        raise ValueError("Gaia catalog bytes do not match the qualified holding")

    rows = load_catalog(catalog)
    _, population = select_population(rows, SelectionConfig())
    expected_population = {
        "catalog_rows": EXPECTED_ROWS,
        "source_quality_rows": EXPECTED_SOURCE_QUALITY_ROWS,
        "selected_rows": EXPECTED_SELECTED_ROWS,
        "selected_identifier_sha256": EXPECTED_IDENTIFIER_SHA256,
    }
    if population != expected_population:
        raise ValueError(
            f"Gaia population does not match qualification: {population}"
        )

    high_acceleration = float(
        phenomenological_external_field_ratio(1e-6)
    )
    reference_accelerations = np.array([1e-8, 10**-8.91, 10**-10.15])
    reference_ratios = phenomenological_external_field_ratio(
        reference_accelerations
    )
    if abs(high_acceleration - 1) > 1e-12:
        raise ValueError("Phenomenological model fails its Newtonian limit")
    if np.any(~np.isfinite(reference_ratios)) or np.any(reference_ratios < 1):
        raise ValueError("Phenomenological model produced an invalid boost")

    revision, dirty = _revision()
    return {
        "schema_version": "1.0.0",
        "qualification_id": "gaia-wide-binary-method-v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "qualified-for-preregistration",
        "outcome_computed": False,
        "input": {
            "dataset_id": "gaia-chae-dr3-wide-binaries",
            "version": "zenodo-8270396",
            "bytes": size,
            "sha256": digest,
        },
        "population": population,
        "selection": {
            "configuration": SelectionConfig().__dict__,
            "observational_velocity_or_acceleration_used": False,
        },
        "model": {
            "classification": "phenomenological-external-field-comparator",
            "formula": (
                "g_model/g_N = 1 / "
                "(1 - exp(-sqrt(hypot(g_N, g_ext) / a0)))"
            ),
            "a0_si": 1.2e-10,
            "external_field_si": 1.2e-10,
            "reference_newtonian_accelerations_si": (
                reference_accelerations.tolist()
            ),
            "predicted_acceleration_ratios": reference_ratios.tolist(),
            "high_acceleration_limit": high_acceleration,
            "derived_first_principles_emrf_prediction": False,
        },
        "method": {
            "deprojection": (
                "Deterministic implementation of isotropic inclination, "
                "published eccentricity uncertainty, uniform mean anomaly, "
                "and Kepler-equation orbital phase."
            ),
            "newtonian_control": (
                "Must be generated locally from frozen seeds; the published "
                "virtual Newtonian CSV is not an input."
            ),
            "unresolved_multiplicity": (
                "Must be frozen as a nuisance sensitivity before outcomes."
            ),
        },
        "revision": revision,
        "dirty": dirty,
        "platform": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "system": platform.platform(),
        },
        "limitations": [
            "No Gaia kinematic acceleration or anomaly was computed.",
            "Population counts use source metadata needed for frozen selection.",
            "The external-field formula is phenomenological, not a derived "
            "first-principles EMRF prediction.",
            "Published Gaia outcomes were known before this qualification.",
        ],
    }


def _write_json_atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    result = qualify(args.catalog)
    _write_json_atomic(args.output.expanduser().resolve(), result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
