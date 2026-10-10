"""Immutable hash commitments for predictions made before data confrontation."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from emrf_paths import default_app_root

_LABEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._-]{0,99}$")
_COMMITMENT_ID = re.compile(r"^\d{8}T\d{12}Z-[0-9a-f]{12}$")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _commitment_id(digest: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return f"{timestamp}-{digest[:12]}"


def _root(root: str | Path | None) -> Path:
    return Path(root) if root is not None else default_app_root() / "predictions"


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}-",
        suffix=".part",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            json.dump(payload, output, indent=2, sort_keys=True, allow_nan=False)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def commit_prediction(
    content: bytes,
    *,
    label: str,
    source_name: str | None = None,
    media_type: str = "application/octet-stream",
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Persist an immutable metadata-only commitment to prediction bytes."""
    if not isinstance(content, bytes) or not content:
        raise ValueError("prediction content must be non-empty bytes")
    if not isinstance(label, str) or not _LABEL.fullmatch(label):
        raise ValueError("label must be 1-100 safe printable characters")
    if source_name is not None:
        source_name = Path(source_name.replace("\\", "/")).name
    digest = hashlib.sha256(content).hexdigest()
    commitment_id = _commitment_id(digest)
    record = {
        "commitment_id": commitment_id,
        "label": label,
        "created_utc": _utc_now(),
        "sha256": digest,
        "bytes": len(content),
        "source_name": source_name,
        "media_type": media_type,
        "evidence_class": "preregistered-prediction",
        "content_stored": False,
    }
    destination = _root(root) / f"{commitment_id}.json"
    if destination.exists():
        raise FileExistsError(f"Prediction commitment already exists: {commitment_id}")
    _atomic_json(destination, record)
    return record


def commit_json_prediction(
    prediction: Any,
    *,
    label: str,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Canonicalize a JSON-compatible prediction and commit only its digest."""
    content = json.dumps(
        prediction,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return commit_prediction(
        content,
        label=label,
        media_type="application/json",
        root=root,
    )


def get_commitment(
    commitment_id: str,
    *,
    root: str | Path | None = None,
) -> dict[str, Any]:
    if not isinstance(commitment_id, str) or not _COMMITMENT_ID.fullmatch(commitment_id):
        raise ValueError("Invalid prediction commitment id")
    path = _root(root) / f"{commitment_id}.json"
    if not path.is_file():
        raise KeyError(f"Unknown prediction commitment: {commitment_id}")
    record = json.loads(path.read_text(encoding="utf-8"))
    if record.get("commitment_id") != commitment_id:
        raise ValueError("Prediction commitment record is inconsistent")
    return record


def verify_prediction(
    commitment_id: str,
    content: bytes,
    *,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Verify revealed bytes against an existing commitment."""
    if not isinstance(content, bytes):
        raise TypeError("prediction content must be bytes")
    record = get_commitment(commitment_id, root=root)
    actual = hashlib.sha256(content).hexdigest()
    return {
        "commitment_id": commitment_id,
        "matches": actual == record["sha256"],
        "expected_sha256": record["sha256"],
        "actual_sha256": actual,
        "bytes": len(content),
    }


def verify_json_prediction(
    commitment_id: str,
    prediction: Any,
    *,
    root: str | Path | None = None,
) -> dict[str, Any]:
    content = json.dumps(
        prediction,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return verify_prediction(commitment_id, content, root=root)


__all__ = [
    "commit_json_prediction",
    "commit_prediction",
    "get_commitment",
    "verify_json_prediction",
    "verify_prediction",
]
