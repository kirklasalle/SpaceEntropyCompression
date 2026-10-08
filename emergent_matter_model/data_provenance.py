"""Data provenance helpers.

Every file under ``data/synthetic/`` starts with a ``# SYNTHETIC DATA`` banner.
Those files are code-testing fixtures, not observations. Pipelines call
:func:`provenance_banner` so that any result computed from them is clearly
labelled when printed.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path

SYNTHETIC_MARKER = "SYNTHETIC DATA"

REPO_ROOT = Path(__file__).resolve().parent.parent
SYNTHETIC_DIR = REPO_ROOT / "data" / "synthetic"


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
