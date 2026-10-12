"""Safe, deterministic run-artifact discovery."""

from __future__ import annotations

import mimetypes
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ArtifactRecord:
    path: str
    bytes: int
    media_type: str


def scan_artifacts(root: Path) -> tuple[ArtifactRecord, ...]:
    """Return regular files contained by a resolved run directory."""
    resolved_root = root.resolve()
    artifacts: list[ArtifactRecord] = []
    for path in sorted(resolved_root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        resolved = path.resolve()
        if resolved_root not in resolved.parents:
            continue
        artifacts.append(
            ArtifactRecord(
                path=path.relative_to(resolved_root).as_posix(),
                bytes=path.stat().st_size,
                media_type=mimetypes.guess_type(path.name)[0]
                or "application/octet-stream",
            )
        )
    return tuple(artifacts)


__all__ = ["ArtifactRecord", "scan_artifacts"]
