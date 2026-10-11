"""Privacy-safe diagnostic reports for EMRF support requests."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import uuid
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import emrf_registry
from emrf_paths import default_app_root

SUPPORT_REPORT_SCHEMA = "emrf-support-report/1.0"


def create_support_report(destination: str | Path | None = None) -> dict[str, Any]:
    """Write a diagnostic report that excludes environment variables and user paths."""
    generated = datetime.now(timezone.utc)
    report = build_support_report(generated=generated)
    output = (
        Path(destination).expanduser().resolve()
        if destination is not None
        else default_app_root()
        / "support"
        / f"emrf-doctor-{generated.strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}.json"
    )
    if output.exists():
        raise FileExistsError(f"Support report already exists: {output}")
    _write_private_json(output, report)
    return {
        "path": str(output),
        "sha256": _sha256(output),
        "bytes": output.stat().st_size,
        "healthy": bool(report["environment"]["healthy"]),
        "schema": SUPPORT_REPORT_SCHEMA,
    }


def build_support_report(
    *,
    generated: datetime | None = None,
) -> dict[str, Any]:
    """Build a deterministic-shape report without credentials or personal paths."""
    timestamp = generated or datetime.now(timezone.utc)
    environment = dict(emrf_registry.environment_report())
    environment.pop("executable", None)
    environment["app_root"] = "<app-root>"
    environment["data_root"] = "<data-root>"

    from emrf.knowledge import KnowledgeStore

    knowledge = dict(KnowledgeStore().validate())
    knowledge["graph_path"] = "<knowledge-graph>"
    knowledge_errors = knowledge.pop("errors", [])
    knowledge["error_count"] = len(knowledge_errors)
    knowledge["error_paths"] = sorted(
        {
            str(error.get("path", "$"))
            for error in knowledge_errors
            if isinstance(error, dict)
        }
    )
    return {
        "schema": SUPPORT_REPORT_SCHEMA,
        "generated_utc": timestamp.isoformat().replace("+00:00", "Z"),
        "privacy": {
            "environment_variables_included": False,
            "credentials_included": False,
            "user_paths_redacted": True,
            "run_arguments_included": False,
            "dataset_urls_included": False,
        },
        "environment": environment,
        "knowledge": knowledge,
    }


def _write_private_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    staged: Path | None = None
    descriptor: int | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.",
            suffix=".part",
            dir=path.parent,
        )
        staged = Path(temporary_name)
        os.chmod(staged, 0o600)
        handle = os.fdopen(descriptor, "w", encoding="utf-8", newline="\n")
        descriptor = None
        with handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(staged, path)
        except FileExistsError:
            raise
        except OSError:
            _publish_exclusive_copy(staged, path)
        staged.unlink()
        staged = None
        _fsync_directory(path.parent)
    except Exception:
        if descriptor is not None:
            os.close(descriptor)
        if staged is not None:
            staged.unlink(missing_ok=True)
        raise


def _publish_exclusive_copy(staged: Path, path: Path) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    published = False
    try:
        with os.fdopen(descriptor, "wb") as target, staged.open("rb") as source:
            descriptor = -1
            shutil.copyfileobj(source, target)
            target.flush()
            os.fsync(target.fileno())
        os.chmod(path, 0o600)
        published = True
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if not published:
            path.unlink(missing_ok=True)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fsync_directory(path: Path) -> None:
    try:
        descriptor = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


__all__ = ["SUPPORT_REPORT_SCHEMA", "build_support_report", "create_support_report"]
