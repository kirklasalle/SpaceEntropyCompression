"""Packaging script for the First Use Case Academic Paper (LaSalle Spatial Ontology)."""

from __future__ import annotations

import hashlib
import tarfile
import zipfile
from pathlib import Path


def compute_sha256(filepath: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    paper_dir = Path(__file__).resolve().parent
    print("=" * 70)
    print(" PACKAGING FIRST USE CASE PAPER: LASALLE SPATIAL ONTOLOGY")
    print("=" * 70)
    
    files_to_pack = [
        paper_dir / "use_case_lasalle_ontology.tex",
        paper_dir / "references.bib",
    ]
    figures = [
        paper_dir / "figures" / "fig14_jwst_cosmic_dawn.png",
        paper_dir / "figures" / "fig15_black_hole_horizon_entropy.png",
        paper_dir / "figures" / "fig16_quantum_vibrational_solitons.png",
    ]
    
    tar_path = paper_dir / "use_case_submission.tar.gz"
    zip_path = paper_dir / "use_case_submission.zip"
    
    # Build tar.gz
    with tarfile.open(tar_path, "w:gz") as tar:
        for f in files_to_pack:
            tar.add(f, arcname=f.name)
        for fig in figures:
            tar.add(fig, arcname=f"figures/{fig.name}")
            
    # Build zip
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files_to_pack:
            zf.write(f, arcname=f.name)
        for fig in figures:
            zf.write(fig, arcname=f"figures/{fig.name}")
            
    print("Use Case Submission Packages Built Successfully:")
    print(f"  - tar.gz: {tar_path.name} ({tar_path.stat().st_size:,} bytes)")
    print(f"    SHA-256: {compute_sha256(tar_path)}")
    print(f"  - zip:    {zip_path.name} ({zip_path.stat().st_size:,} bytes)")
    print(f"    SHA-256: {compute_sha256(zip_path)}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    main()
