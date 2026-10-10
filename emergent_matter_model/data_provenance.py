"""Data provenance helpers.

Every file under ``data/synthetic/`` starts with a ``# SYNTHETIC DATA`` banner.
Those files are code-testing fixtures, not observations. Pipelines call
:func:`provenance_banner` so that any result computed from them is clearly
labelled when printed.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Iterator
from pathlib import Path

try:
    from emrf_paths import app_root, data_root
except ModuleNotFoundError:  # package-qualified legacy import
    from emergent_matter_model.emrf_paths import app_root, data_root

SYNTHETIC_MARKER = "SYNTHETIC DATA"

REPO_ROOT = app_root()
SYNTHETIC_DIR = data_root() / "synthetic"


def is_synthetic(path: str | Path) -> bool:
    """Return True if the file carries the synthetic-data banner in its header."""
    p = Path(path)
    if not p.is_file():
        return False
    with open(p, encoding="utf-8") as f:
        for _ in range(10):
            line = f.readline()
            if not line:
                break
            if SYNTHETIC_MARKER in line:
                return True
    return False


def verify_observation_file(path: str | Path, entry: dict) -> str:
    """Fail closed on missing source metadata, synthetic files or changed bytes."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(p)
    if SYNTHETIC_DIR in p.resolve().parents:
        raise ValueError("Synthetic fixtures are not observations")
    if not entry.get("url", "").startswith("https://") or not entry.get("citation"):
        raise ValueError("Missing source URL or citation")
    expected = entry.get("sha256", "")
    if len(expected) != 64:
        raise ValueError("Missing SHA-256 provenance")
    data = p.read_bytes()
    if SYNTHETIC_MARKER.encode() in data[:4096]:
        raise ValueError("Synthetic marker in observational input")
    digest = hashlib.sha256(data).hexdigest()
    if digest != expected or len(data) != entry.get("bytes"):
        raise ValueError(f"Provenance mismatch: {p.name}")
    return digest


def skip_comment_lines(lines: Iterable[str]) -> Iterator[str]:
    """Yield lines that are not ``#`` comments (for use with csv.DictReader)."""
    for line in lines:
        if not line.lstrip().startswith("#"):
            yield line


def provenance_banner(*paths: str | Path) -> str:
    """Return a loud warning if any input is synthetic, else an empty string."""
    synthetic = [str(Path(p)) for p in paths if is_synthetic(p)]
    if not synthetic:
        return ""
    bar = "!" * 78
    listing = "\n".join(f"!!   {s}" for s in synthetic)
    return (
        f"{bar}\n"
        "!! SYNTHETIC INPUT DATA -- the numbers below are a CODE DEMONSTRATION ONLY.\n"
        "!! They are not observations and must not be reported as scientific results.\n"
        f"{listing}\n"
        f"{bar}"
    )
