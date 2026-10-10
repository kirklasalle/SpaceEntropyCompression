"""Fit an uncalibrated flat-LCDM baseline to authentic Pantheon+ full-covariance data."""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from emergent_matter_model import pantheon_inference
from emergent_matter_model.fetch_real_data import download, sha256_of
from emergent_matter_model.pantheon_inference import (
    COVARIANCE_SYMMETRY_TOLERANCE,
    dimensionless_magnitudes,  # noqa: F401 - compatibility export
    fit_baseline,
    profile_offset,  # noqa: F401 - compatibility export
    read_covariance,
)

RELEASE = "c447f0fea703fcd0fff57de5000947b5ca81286b"
BASE = f"https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/{RELEASE}/Pantheon%2B_Data/"
def main() -> None:
    manual = ROOT / "data" / "external"
    cache = manual / "real_data_followup"
    cache.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for source_name, local_name in (
        ("Pantheon%2BSH0ES.dat", "Pantheon+SH0ES.dat.txt"),
        ("Pantheon%2BSH0ES_STAT%2BSYS.cov", "Pantheon+SH0ES_STAT+SYS.cov.txt"),
    ):
        local = manual / local_name
        if not local.is_file():
            raise FileNotFoundError(f"Manual download is missing: {local}")
        url = BASE + "4_DISTANCES_AND_COVAR/" + source_name
        reference = cache / local_name
        download(url, reference)
        digest = sha256_of(reference)
        if sha256_of(local) != digest:
            raise ValueError(f"Manual file differs from the pinned official release: {local.name}")
        manifest[local_name] = {"url": url, "sha256": digest, "bytes": local.stat().st_size,
                                "manual_file": str(local.relative_to(ROOT)),
                                "source_bytes_match": True}
    for label, suffix in (
        ("release_readme", "4_DISTANCES_AND_COVAR/README"),
        ("collaboration_likelihood",
         "5_COSMOLOGY/cosmosis_likelihoods/Pantheon%2B_only_cosmosis_likelihood.py"),
    ):
        path = cache / f"{label}.txt"
        download(BASE + suffix, path)
        manifest[label] = {"url": BASE + suffix, "sha256": sha256_of(path),
                           "bytes": path.stat().st_size}
    table = np.genfromtxt(manual / "Pantheon+SH0ES.dat.txt", names=True, dtype=None,
                          encoding="utf-8")
    covariance, asymmetry = read_covariance(manual / "Pantheon+SH0ES_STAT+SYS.cov.txt", len(table))
    result = fit_baseline(table, covariance, extended_diagnostics=True)
    result.update(
        generated_utc=datetime.now(timezone.utc).isoformat(),
        python=platform.python_version(), numpy=np.__version__, source_manifest=manifest,
        covariance_asymmetry_max=asymmetry,
        covariance_symmetry_rule=f"(C+C.T)/2 only if max asymmetry <= {COVARIANCE_SYMMETRY_TOLERANCE}",
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        inference_source_sha256=hashlib.sha256(
            Path(pantheon_inference.__file__).read_bytes()
        ).hexdigest(),
    )
    output = ROOT / "results" / "real_data_followup" / "pantheon_baseline.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in (
        "selected_rows", "distinct_CID", "omega_m", "omega_m_delta_chi2_1_interval",
        "chi2", "degrees_of_freedom", "integration_check_absolute_delta_chi2")}, indent=2))
    print(f"Saved {output}; baseline only, not an EMRF validation.")


if __name__ == "__main__":
    main()
