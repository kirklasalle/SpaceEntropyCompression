"""Create a local review bundle and checksum manifest; never upload a release."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    result_dir = ROOT / "results" / "real_data_v1"
    profile = json.loads((result_dir / "sparc_profile_validation.json").read_text())
    if not profile.get("complete") or not profile.get("numerically_verified"):
        raise RuntimeError("Refusing to package incomplete numerical results")
    build = json.loads((result_dir / "manuscript_build.json").read_text())
    if build["returncode"] != 0:
        raise RuntimeError("Refusing to package a failed manuscript build")
    for name, expected in build["source_sha256"].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise RuntimeError(f"Manuscript source changed after compilation: {name}")
    pdf = ROOT / "paper" / "sparc_horizon_test.pdf"
    if hashlib.sha256(pdf.read_bytes()).hexdigest() != build["pdf_sha256"]:
        raise RuntimeError("PDF differs from the recorded manuscript build")
    files = [
        *sorted((ROOT / "docs").glob("REAL_DATA*.md")),
        ROOT / "docs" / "SPARC_HORIZON_TEST_PAPER.md",
        ROOT / "docs" / "SPARC_FRESH_RESULTS.md",
        ROOT / "docs" / "EMRF_COMPRESSION_AND_HORIZONS_AUDIT.md",
        ROOT / "paper" / "sparc_horizon_test.tex",
        ROOT / "paper" / "sparc_horizon_test.pdf",
        ROOT / "paper" / "sparc_horizon_results.tex",
        ROOT / "paper" / "sparc_horizon_references.bib",
        ROOT / "paper" / "figures" / "sparc_fresh_profiles.png",
        *sorted(result_dir.glob("*.json")),
        *[ROOT / "tools" / name for name in (
            "check_compression_claims.py", "run_sparc_profile_validation.py", "check_sparc_influence.py",
            "run_real_data_gauntlet.py", "build_real_data_report.py", "build_sparc_paper.py",
            "package_real_data_release.py")],
        *[ROOT / "emergent_matter_model" / name for name in (
            "data_provenance.py", "fetch_real_data.py", "sparc_real_analysis.py",
            "sparc_marginalized_a0.py", "sparc_tension_diagnostics.py", "sparc_bulge_test.py",
            "black_hole_horizon_entropy.py", "quantum_vibrational_compression.py",
            "test_real_data_validation.py", "test_real_data_paper.py",
            "test_compression_claims_audit.py", "pyproject.toml")],
        ROOT / "data" / "cosmology" / "desi_2024_bao.csv",
    ]
    files = [p for p in files if p.name != "review_manifest.json"]
    manifest = {"purpose": "local research review, not uploaded or peer reviewed",
                "raw_observations": "retrieve from source manifests; not redistributed in bundle",
                "pdf_status": "see manuscript_build.json for executed build evidence",
                "files": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in files}}
    manifest_path = result_dir / "review_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    destination = result_dir / "real_data_review_bundle.zip"
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files + [manifest_path]:
            archive.write(path, str(path.relative_to(ROOT)))
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("Review bundle CRC check failed")
    print(f"Verified local review bundle: {destination}")


if __name__ == "__main__":
    main()
