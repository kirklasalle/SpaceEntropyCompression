"""Download and cache REAL public datasets with provenance checksums.

Files are cached under ``data/external/`` (git-ignored) and never redistributed.
Each download is recorded with its URL, size and SHA-256 so analyses can state
exactly which bytes they used.

Usage
-----
    python emergent_matter_model/fetch_real_data.py --sparc
"""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXTERNAL_DIR = REPO_ROOT / "data" / "external"
MANIFEST = EXTERNAL_DIR / "download_manifest.json"

SPARC_BASE = "https://astroweb.case.edu/SPARC"
SPARC_FILES = {
    "Rotmod_LTG.zip": f"{SPARC_BASE}/Rotmod_LTG.zip",
    "SPARC_Lelli2016c.mrt": f"{SPARC_BASE}/SPARC_Lelli2016c.mrt",
}
SPARC_CITATION = "Lelli, F., McGaugh, S. S. & Schombert, J. M. (2016), AJ 152, 157"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _record(name: str, url: str, path: Path, citation: str) -> dict:
    entry = {
        "file": str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "url": url,
        "citation": citation,
        "bytes": path.stat().st_size,
        "sha256": sha256_of(path),
        "retrieved_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.is_file() else {}
    manifest[name] = entry
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return entry


def download(url: str, dest: Path, timeout: float = 180.0) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(url, timeout=timeout) as r, open(tmp, "wb") as f:
        f.write(r.read())
    tmp.replace(dest)
    return dest


def sparc_dir() -> Path:
    return EXTERNAL_DIR / "sparc"


def fetch_sparc(force: bool = False) -> Path:
    """Ensure the official SPARC rotation curves and galaxy table are cached; return the folder."""
    out = sparc_dir()
    for name, url in SPARC_FILES.items():
        dest = out / name
        if force or not dest.is_file():
            print(f"Downloading {url}")
            download(url, dest)
            _record(f"sparc/{name}", url, dest, SPARC_CITATION)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for name, url in SPARC_FILES.items():
        entry = manifest.get(f"sparc/{name}", {})
        if (entry.get("url") != url or entry.get("sha256") != sha256_of(out / name)
                or entry.get("bytes") != (out / name).stat().st_size):
            raise ValueError(f"Unverified or modified SPARC cache: {name}; use --force")
    rot_dir = out / "Rotmod_LTG"
    rot_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out / "Rotmod_LTG.zip") as z:
        expected = set()
        for member in z.namelist():
            if member.endswith("_rotmod.dat"):
                dest = rot_dir / Path(member).name
                expected.add(dest.name)
                raw = z.read(member)
                if not dest.exists() or force:
                    dest.write_bytes(raw)
                elif dest.read_bytes() != raw:
                    raise ValueError(f"Extracted SPARC file differs from archive: {dest.name}")
        if {p.name for p in rot_dir.glob("*_rotmod.dat")} != expected:
            raise ValueError("Unexpected rotation files in SPARC cache")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--sparc", action="store_true", help="download the SPARC database (Lelli+2016)")
    ap.add_argument("--force", action="store_true", help="re-download even if cached")
    args = ap.parse_args()
    if not args.sparc:
        ap.print_help()
        return 0
    path = fetch_sparc(force=args.force)
    n = len(list((path / "Rotmod_LTG").glob("*_rotmod.dat")))
    print(f"SPARC cached in {path} ({n} rotation curves)")
    if MANIFEST.is_file():
        print(MANIFEST.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
