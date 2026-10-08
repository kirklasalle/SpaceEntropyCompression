"""arXiv & Journal Preprint Submission Packaging Utility.

Validates manuscript files, verifies bibliography citations, and builds
clean, submission-ready archives (tar.gz and zip) for arXiv and journal upload.
"""

from __future__ import annotations

import hashlib
import re
import shutil
import sys
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


def validate_manuscript(paper_dir: Path) -> bool:
    """Perform pre-flight sanity checks on main.tex and references.bib."""
    main_tex = paper_dir / "main.tex"
    ref_bib = paper_dir / "references.bib"
    
    if not main_tex.is_file() or not ref_bib.is_file():
        print("ERROR: main.tex or references.bib missing in paper directory.")
        return False
        
    tex_text = main_tex.read_text(encoding="utf-8")
    bib_text = ref_bib.read_text(encoding="utf-8")
    
    # Check citations
    raw_cites = re.findall(r"\\cite\{([^}]+)\}", tex_text)
    cited_keys = set()
    for rc in raw_cites:
        for k in rc.split(","):
            cited_keys.add(k.strip())
            
    bib_keys = set(re.findall(r"@\w+\s*\{\s*([a-zA-Z0-9_\-]+)\s*,", bib_text))
    missing = cited_keys - bib_keys
    if missing:
        print(f"ERROR: Missing BibTeX keys for citations: {missing}")
        return False
        
    print(f"PASS: All {len(cited_keys)} citations resolve in references.bib.")
    return True


def build_submission_packages(paper_dir: Path) -> tuple[Path, Path]:
    """Build tar.gz and zip submission packages including figures."""
    files_to_pack = [
        paper_dir / "main.tex",
        paper_dir / "references.bib",
    ]
    fig_dir = paper_dir / "figures"
    tex_text = (paper_dir / "main.tex").read_text(encoding="utf-8")
    referenced = set(re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{figures/([^}]+)\}", tex_text))
    # Only package figures the manuscript uses (older figures were built from synthetic data).
    fig_files = sorted(fig_dir / name for name in referenced if (fig_dir / name).is_file())
    
    tar_path = paper_dir / "arxiv_submission.tar.gz"
    zip_path = paper_dir / "arxiv_submission.zip"
    
    # Build tar.gz
    with tarfile.open(tar_path, "w:gz") as tar:
        for f in files_to_pack:
            tar.add(f, arcname=f.name)
        for fig in fig_files:
            tar.add(fig, arcname=f"figures/{fig.name}")
            
    # Build zip
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files_to_pack:
            zf.write(f, arcname=f.name)
        for fig in fig_files:
            zf.write(fig, arcname=f"figures/{fig.name}")
            
    return tar_path, zip_path


def main() -> int:
    """CLI execution for manuscript packaging."""
    paper_dir = Path(__file__).resolve().parent
    print("=" * 70)
    print(" EMRF ACADEMIC PREPRINT PACKAGING PIPELINE")
    print("=" * 70)
    
    if not validate_manuscript(paper_dir):
        return 1
        
    tar_path, zip_path = build_submission_packages(paper_dir)
    
    print("\nSubmission Packages Built Successfully:")
    print(f"  - tar.gz: {tar_path.name} ({tar_path.stat().st_size:,} bytes)")
    print(f"    SHA-256: {compute_sha256(tar_path)}")
    print(f"  - zip:    {zip_path.name} ({zip_path.stat().st_size:,} bytes)")
    print(f"    SHA-256: {compute_sha256(zip_path)}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
