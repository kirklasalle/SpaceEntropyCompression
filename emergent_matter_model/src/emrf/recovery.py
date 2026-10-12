"""Verified backup and isolated recovery for durable EMRF application state."""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import re
import shutil
import sqlite3
import sys
import tempfile
import time
from collections.abc import Generator
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from emrf.core.errors import IntegrityError, StorageError
from emrf.knowledge import KnowledgeStore
from emrf.runs import RunStore
from emrf.validation.preregistration import get_commitment
from emrf_paths import default_app_root
from emrf_version import __version__

_SCHEMA_VERSION = "1.0.0"
_MANIFEST = "state_manifest.json"
_RUN_ID = re.compile(r"^\d{8}T\d{12}Z-[0-9a-f]{8}$")
_COMMITMENT_ID = re.compile(r"^\d{8}T\d{12}Z-[0-9a-f]{12}\.json$")
_DEFAULT_RPO_SECONDS = 3600.0
_DEFAULT_RTO_SECONDS = 14400.0


class StateRecoveryManager:
    """Create, verify, and restore complete durable application-state snapshots."""

    def __init__(
        self,
        *,
        runs: RunStore | None = None,
        predictions_root: str | Path | None = None,
        knowledge: KnowledgeStore | None = None,
    ) -> None:
        self.runs = runs or RunStore()
        self.predictions_root = (
            Path(predictions_root).expanduser().resolve()
            if predictions_root is not None
            else (default_app_root() / "predictions").resolve()
        )
        self.knowledge = knowledge or KnowledgeStore()

    def create(self, destination: str | Path) -> dict[str, Any]:
        target = Path(destination).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        with _destination_lock(target):
            if target.exists():
                raise FileExistsError(
                    f"State backup destination already exists: {target}"
                )
            before = self._source_fingerprint()
            staging = Path(
                tempfile.mkdtemp(prefix=f".{target.name}-", dir=target.parent)
            )
            try:
                self._copy_runs(staging / "runs")
                self._copy_predictions(staging / "predictions")
                self._copy_knowledge(staging / "knowledge")
                after = self._source_fingerprint()
                if before != after:
                    raise IntegrityError(
                        "Application state changed while its backup was created"
                    )
                components = self._component_summary(staging)
                files = _inventory(staging)
                manifest = {
                    "schema_version": _SCHEMA_VERSION,
                    "created_utc": datetime.now(timezone.utc).isoformat(),
                    "source_fingerprint": after,
                    "files": files,
                    "components": components,
                }
                _write_json_exclusive(staging / _MANIFEST, manifest)
                self.verify(staging)
                if target.exists():
                    raise FileExistsError(
                        f"State backup destination already exists: {target}"
                    )
                os.rename(staging, target)
                _fsync_directory(target.parent)
                return manifest
            except Exception:
                shutil.rmtree(staging, ignore_errors=True)
                raise

    def verify(self, source: str | Path) -> dict[str, Any]:
        root, manifest = _read_manifest(source)
        expected_paths: set[str] = set()
        for entry in manifest["files"]:
            relative = _validate_file_entry(entry)
            if relative in expected_paths:
                raise IntegrityError(f"State backup repeats file: {relative}")
            expected_paths.add(relative)
            path = root.joinpath(*relative.split("/"))
            if path.is_symlink() or not path.is_file():
                raise IntegrityError(f"State backup file is missing or unsafe: {relative}")
            if path.stat().st_size != entry["bytes"]:
                raise IntegrityError(f"State backup file size differs: {relative}")
            if _sha256(path) != entry["sha256"]:
                raise IntegrityError(f"State backup file hash differs: {relative}")
        actual_paths = {
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file() and path.name != _MANIFEST
        }
        if actual_paths != expected_paths:
            missing = sorted(expected_paths - actual_paths)
            unexpected = sorted(actual_paths - expected_paths)
            raise IntegrityError(
                "State backup file inventory differs: "
                f"missing={missing}, unexpected={unexpected}"
            )
        _validate_registry(root / "runs")
        _validate_predictions(root / "predictions")
        _validate_knowledge(root / "knowledge")
        if self._component_summary(root) != manifest["components"]:
            raise IntegrityError("State backup component summary differs from its contents")
        if self._backup_fingerprint(root) != manifest["source_fingerprint"]:
            raise IntegrityError("State backup fingerprint differs from its manifest")
        return manifest

    def restore(
        self,
        source: str | Path,
        destination: str | Path,
    ) -> dict[str, Any]:
        backup_root, manifest = _read_manifest(source)
        self.verify(backup_root)
        target = Path(destination).expanduser().resolve()
        protected_roots = {
            backup_root,
            self.runs.root.resolve(),
            self.predictions_root,
            self.knowledge.graph_path.parent.resolve(),
        }
        if any(root == target or root in target.parents for root in protected_roots):
            raise ValueError(
                "State restore destination must be isolated from active and backup state"
            )
        target.parent.mkdir(parents=True, exist_ok=True)
        with _destination_lock(target):
            if target.exists():
                raise FileExistsError(
                    f"State restore destination already exists: {target}"
                )
            staging = Path(
                tempfile.mkdtemp(prefix=f".{target.name}-", dir=target.parent)
            )
            try:
                for entry in manifest["files"]:
                    relative = _validate_file_entry(entry)
                    source_path = backup_root.joinpath(*relative.split("/"))
                    destination_path = staging.joinpath(*relative.split("/"))
                    destination_path.parent.mkdir(parents=True, exist_ok=True)
                    _copy_exclusive(source_path, destination_path)
                _validate_registry(staging / "runs")
                _validate_predictions(staging / "predictions")
                _validate_knowledge(staging / "knowledge")
                if self._backup_fingerprint(staging) != manifest["source_fingerprint"]:
                    raise IntegrityError(
                        "Restored application state differs from its backup"
                    )
                if target.exists():
                    raise FileExistsError(
                        f"State restore destination already exists: {target}"
                    )
                os.rename(staging, target)
                _fsync_directory(target.parent)
                restored_runs = RunStore(target / "runs")
                restored_runs.initialize()
                return {
                    "destination": str(target),
                    **manifest["components"],
                }
            except Exception:
                shutil.rmtree(staging, ignore_errors=True)
                raise

    def drill(
        self,
        receipt: str | Path,
        *,
        workspace: str | Path | None = None,
        rpo_seconds: float = _DEFAULT_RPO_SECONDS,
        rto_seconds: float = _DEFAULT_RTO_SECONDS,
    ) -> dict[str, Any]:
        rpo = _positive_finite(rpo_seconds, "rpo_seconds")
        rto = _positive_finite(rto_seconds, "rto_seconds")
        receipt_path = Path(receipt).expanduser().resolve()
        if receipt_path.exists():
            raise FileExistsError(f"State-drill receipt already exists: {receipt_path}")
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        workspace_path = (
            None
            if workspace is None
            else Path(workspace).expanduser().resolve()
        )
        if workspace_path is not None:
            workspace_path.mkdir(parents=True, exist_ok=True)
        started = datetime.now(timezone.utc)
        counter = time.perf_counter()
        result: dict[str, Any] = {
            "schema_version": _SCHEMA_VERSION,
            "started_utc": started.isoformat(),
            "status": "running",
            "emrf_version": __version__,
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "implementation": sys.implementation.name,
            "recovery_objectives": {
                "rpo_seconds": rpo,
                "rto_seconds": rto,
            },
        }
        try:
            with tempfile.TemporaryDirectory(
                prefix="emrf-state-drill-",
                dir=workspace_path,
            ) as temporary:
                root = Path(temporary)
                backup = root / "backup"
                restored = root / "restored"
                phase = time.perf_counter()
                manifest = self.create(backup)
                backup_seconds = time.perf_counter() - phase
                phase = time.perf_counter()
                self.verify(backup)
                verification_seconds = time.perf_counter() - phase
                phase = time.perf_counter()
                restored_result = self.restore(backup, restored)
                restore_seconds = time.perf_counter() - phase
                source_changed = (
                    self._source_fingerprint() != manifest["source_fingerprint"]
                )
                completed = datetime.now(timezone.utc)
                recovery_point = datetime.fromisoformat(manifest["created_utc"])
                recovery_age = max(
                    0.0,
                    (completed - recovery_point).total_seconds(),
                )
                duration = time.perf_counter() - counter
                result.update(
                    {
                        "backup_created_utc": manifest["created_utc"],
                        "backup_manifest_sha256": _sha256(backup / _MANIFEST),
                        "components": manifest["components"],
                        "restored": restored_result,
                        "phase_seconds": {
                            "backup": backup_seconds,
                            "verification": verification_seconds,
                            "restore": restore_seconds,
                        },
                        "duration_seconds": duration,
                        "recovery_point_age_seconds": recovery_age,
                        "source_changed_during_drill": source_changed,
                        "rpo_met": not source_changed and recovery_age <= rpo,
                        "rto_met": duration <= rto,
                    }
                )
                if not result["rpo_met"] or not result["rto_met"]:
                    raise IntegrityError(
                        "Application-state drill exceeded its recovery objectives"
                    )
            result["status"] = "passed"
        except Exception as exc:
            result.update(
                {
                    "status": "failed",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )
            result.setdefault("duration_seconds", time.perf_counter() - counter)
            result["completed_utc"] = datetime.now(timezone.utc).isoformat()
            _write_json_exclusive(receipt_path, result)
            raise
        result["completed_utc"] = datetime.now(timezone.utc).isoformat()
        _write_json_exclusive(receipt_path, result)
        return result

    @staticmethod
    def default_receipt_path() -> Path:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        return (
            default_app_root()
            / "recovery"
            / "drills"
            / f"state-restore-{timestamp}.json"
        )

    def _validate_sources(self) -> None:
        self.runs.initialize()
        _validate_registry(self.runs.root)
        _validate_predictions(self.predictions_root)
        report = self.knowledge.validate()
        if not report["valid"]:
            raise IntegrityError("Knowledge graph is invalid")

    def _source_fingerprint(self) -> str:
        self._validate_sources()
        payload = {
            "runs": _source_run_inventory(self.runs),
            "predictions": _source_prediction_inventory(self.predictions_root),
            "knowledge": _source_knowledge_inventory(self.knowledge),
        }
        return _json_sha256(payload)

    @staticmethod
    def _backup_fingerprint(root: Path) -> str:
        payload = {
            "runs": _backup_run_inventory(root / "runs"),
            "predictions": _source_prediction_inventory(root / "predictions"),
            "knowledge": _source_knowledge_inventory(
                KnowledgeStore(
                    root / "knowledge" / "GRAPH_MEMORY.json",
                    root / "knowledge" / "graph_memory.schema.json",
                )
            ),
        }
        return _json_sha256(payload)

    def _copy_runs(self, destination: Path) -> None:
        destination.mkdir(parents=True, exist_ok=False)
        for relative, source in _run_files(self.runs.root):
            target = destination.joinpath(*relative.split("/"))
            target.parent.mkdir(parents=True, exist_ok=True)
            _copy_exclusive(source, target)
        with (
            closing(sqlite3.connect(self.runs.registry)) as source_connection,
            closing(
                sqlite3.connect(destination / "registry.sqlite")
            ) as target_connection,
        ):
            source_connection.backup(target_connection)
            target_connection.commit()

    def _copy_predictions(self, destination: Path) -> None:
        destination.mkdir(parents=True, exist_ok=False)
        for path in _prediction_files(self.predictions_root):
            _copy_exclusive(path, destination / path.name)

    def _copy_knowledge(self, destination: Path) -> None:
        destination.mkdir(parents=True, exist_ok=False)
        _copy_exclusive(self.knowledge.graph_path, destination / "GRAPH_MEMORY.json")
        _copy_exclusive(
            self.knowledge.schema_path,
            destination / "graph_memory.schema.json",
        )

    @staticmethod
    def _component_summary(root: Path) -> dict[str, Any]:
        with closing(
            sqlite3.connect(root / "runs" / "registry.sqlite")
        ) as connection:
            runs = connection.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
            jobs = connection.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        graph = KnowledgeStore(
            root / "knowledge" / "GRAPH_MEMORY.json",
            root / "knowledge" / "graph_memory.schema.json",
        ).validate()
        return {
            "runs": runs,
            "jobs": jobs,
            "run_files": len(_run_files(root / "runs")),
            "prediction_commitments": len(_prediction_files(root / "predictions")),
            "knowledge_nodes": graph["nodes"],
            "knowledge_edges": graph["edges"],
        }


def _positive_finite(value: float, name: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value <= 0
    ):
        raise ValueError(f"{name} must be positive")
    return float(value)


def _run_files(root: Path) -> list[tuple[str, Path]]:
    rows: list[tuple[str, Path]] = []
    if not root.exists():
        return rows
    for directory in sorted(root.iterdir()):
        if not directory.is_dir() or directory.is_symlink():
            continue
        if not _RUN_ID.fullmatch(directory.name):
            if directory.name.startswith(".") and directory.name.endswith(".part"):
                continue
            raise IntegrityError(f"Unexpected run-store directory: {directory.name}")
        for path in sorted(directory.rglob("*")):
            if path.is_symlink():
                raise IntegrityError(f"Run state contains a symbolic link: {path}")
            if path.is_file():
                rows.append((path.relative_to(root).as_posix(), path))
    return rows


def _prediction_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    rows: list[Path] = []
    for path in sorted(root.iterdir()):
        if path.is_symlink():
            raise IntegrityError(f"Prediction state contains a symbolic link: {path}")
        if path.name.startswith(".") and path.name.endswith(".part"):
            continue
        if not path.is_file() or not _COMMITMENT_ID.fullmatch(path.name):
            raise IntegrityError(f"Unexpected prediction-state path: {path.name}")
        _validate_commitment(get_commitment(path.stem, root=root), path.stem)
        rows.append(path)
    return rows


def _source_run_inventory(store: RunStore) -> dict[str, Any]:
    files = [
        {"path": relative, "bytes": path.stat().st_size, "sha256": _sha256(path)}
        for relative, path in _run_files(store.root)
    ]
    return {"files": files, "registry": _registry_rows(store.registry)}


def _backup_run_inventory(root: Path) -> dict[str, Any]:
    files = [
        {"path": relative, "bytes": path.stat().st_size, "sha256": _sha256(path)}
        for relative, path in _run_files(root)
    ]
    return {
        "files": files,
        "registry": _registry_rows(root / "registry.sqlite", immutable=True),
    }


def _source_prediction_inventory(root: Path) -> list[dict[str, Any]]:
    return [
        {"path": path.name, "bytes": path.stat().st_size, "sha256": _sha256(path)}
        for path in _prediction_files(root)
    ]


def _source_knowledge_inventory(store: KnowledgeStore) -> dict[str, Any]:
    report = store.validate()
    if not report["valid"]:
        raise IntegrityError("Knowledge graph is invalid")
    return {
        "graph_sha256": _sha256(store.graph_path),
        "schema_sha256": _sha256(store.schema_path),
        "schema_version": report["schema_version"],
        "nodes": report["nodes"],
        "edges": report["edges"],
    }


def _registry_rows(
    path: Path,
    *,
    immutable: bool = False,
) -> dict[str, list[dict[str, Any]]]:
    if immutable:
        connection_target = f"file:{path}?mode=ro&immutable=1"
        connection = sqlite3.connect(connection_target, uri=True)
    else:
        connection = sqlite3.connect(path)
    with closing(connection) as connection:
        connection.row_factory = sqlite3.Row
        runs = []
        for row in connection.execute("SELECT * FROM runs ORDER BY run_id").fetchall():
            value = dict(row)
            value.pop("run_path", None)
            runs.append(value)
        return {
            "runs": runs,
            "jobs": [
                dict(row)
                for row in connection.execute(
                    "SELECT * FROM jobs ORDER BY queue_sequence"
                ).fetchall()
            ],
        }


def _validate_registry(root: Path) -> None:
    from emrf.runs.records import _run_from_payload

    registry = root / "registry.sqlite"
    if not registry.is_file() or registry.is_symlink():
        raise IntegrityError("Run registry snapshot is missing or unsafe")
    with closing(
        sqlite3.connect(f"file:{registry}?mode=ro&immutable=1", uri=True)
    ) as connection:
        if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise IntegrityError("Run registry failed SQLite integrity checking")
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise IntegrityError("Run registry contains invalid relationships")
        indexed = {
            row[0] for row in connection.execute("SELECT run_id FROM runs").fetchall()
        }
    durable = {path.name for path in root.iterdir() if path.is_dir()}
    if indexed != durable:
        raise IntegrityError("Run registry and durable run directories differ")
    for run_id in durable:
        try:
            payload = json.loads((root / run_id / "run.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise IntegrityError(f"Could not read recovered run: {run_id}") from exc
        if payload.get("run_id") != run_id:
            raise IntegrityError(f"Recovered run identifier differs: {run_id}")
        _run_from_payload(payload, root / run_id)


def _validate_predictions(root: Path) -> None:
    _prediction_files(root)


def _validate_knowledge(root: Path) -> None:
    report = KnowledgeStore(
        root / "GRAPH_MEMORY.json",
        root / "graph_memory.schema.json",
    ).validate()
    if not report["valid"]:
        raise IntegrityError("Recovered knowledge graph is invalid")


def _inventory(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise IntegrityError(f"State backup contains a symbolic link: {path}")
        if path.is_file() and path.name != _MANIFEST:
            rows.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": _sha256(path),
                }
            )
    return rows


def _read_manifest(source: str | Path) -> tuple[Path, dict[str, Any]]:
    root = Path(source).expanduser().resolve()
    try:
        text = (root / _MANIFEST).read_text(encoding="utf-8")
    except FileNotFoundError:
        raise
    except OSError as exc:
        raise IntegrityError(f"Could not read state backup manifest: {root}") from exc
    try:
        manifest = json.loads(text)
    except json.JSONDecodeError as exc:
        raise IntegrityError(f"Could not read state backup manifest: {root}") from exc
    if not isinstance(manifest, dict) or manifest.get("schema_version") != _SCHEMA_VERSION:
        raise IntegrityError("Unsupported state backup manifest schema")
    if set(manifest) != {
        "schema_version",
        "created_utc",
        "source_fingerprint",
        "files",
        "components",
    }:
        raise IntegrityError("State backup manifest contains unknown fields")
    if not isinstance(manifest.get("files"), list):
        raise IntegrityError("State backup manifest files must be a list")
    components = manifest.get("components")
    required_components = {
        "runs",
        "jobs",
        "run_files",
        "prediction_commitments",
        "knowledge_nodes",
        "knowledge_edges",
    }
    if (
        not isinstance(components, dict)
        or set(components) != required_components
        or any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in components.values()
        )
    ):
        raise IntegrityError("State backup component summary is invalid")
    created = manifest.get("created_utc")
    if not isinstance(created, str):
        raise IntegrityError("State backup creation time is invalid")
    try:
        parsed_created = datetime.fromisoformat(created)
    except ValueError as exc:
        raise IntegrityError("State backup creation time is invalid") from exc
    if parsed_created.tzinfo is None:
        raise IntegrityError("State backup creation time must include a timezone")
    fingerprint = manifest.get("source_fingerprint")
    if (
        not isinstance(fingerprint, str)
        or len(fingerprint) != 64
        or any(character not in "0123456789abcdef" for character in fingerprint)
    ):
        raise IntegrityError("State backup manifest fingerprint is invalid")
    return root, manifest


def _validate_file_entry(entry: object) -> str:
    if not isinstance(entry, dict):
        raise IntegrityError("State backup file entries must be JSON objects")
    relative = entry.get("path")
    size = entry.get("bytes")
    digest = entry.get("sha256")
    if (
        not isinstance(relative, str)
        or not relative
        or "\\" in relative
        or Path(relative).is_absolute()
        or ".." in Path(relative).parts
        or not isinstance(size, int)
        or isinstance(size, bool)
        or size < 0
        or not isinstance(digest, str)
        or len(digest) != 64
        or any(character not in "0123456789abcdef" for character in digest)
    ):
        raise IntegrityError("State backup contains invalid file metadata")
    return relative


def _copy_exclusive(source: Path, destination: Path) -> None:
    try:
        with source.open("rb") as input_file, destination.open("xb") as output:
            shutil.copyfileobj(input_file, output, length=1024 * 1024)
            output.flush()
            os.fsync(output.fileno())
    except OSError as exc:
        raise StorageError(f"Could not copy application state: {source}") from exc


def _validate_commitment(record: object, commitment_id: str) -> None:
    if not isinstance(record, dict):
        raise IntegrityError(f"Prediction commitment must be an object: {commitment_id}")
    required = {
        "commitment_id",
        "label",
        "created_utc",
        "sha256",
        "bytes",
        "source_name",
        "media_type",
        "evidence_class",
        "content_stored",
    }
    digest = record.get("sha256")
    if (
        set(record) != required
        or record.get("commitment_id") != commitment_id
        or not isinstance(record.get("label"), str)
        or not record["label"]
        or not isinstance(record.get("created_utc"), str)
        or not isinstance(digest, str)
        or len(digest) != 64
        or any(character not in "0123456789abcdef" for character in digest)
        or isinstance(record.get("bytes"), bool)
        or not isinstance(record.get("bytes"), int)
        or record["bytes"] < 0
        or (
            record.get("source_name") is not None
            and not isinstance(record["source_name"], str)
        )
        or not isinstance(record.get("media_type"), str)
        or not record["media_type"]
        or record.get("evidence_class") != "preregistered-prediction"
        or record.get("content_stored") is not False
    ):
        raise IntegrityError(f"Prediction commitment is invalid: {commitment_id}")
    try:
        created = datetime.fromisoformat(record["created_utc"])
    except ValueError as exc:
        raise IntegrityError(
            f"Prediction commitment time is invalid: {commitment_id}"
        ) from exc
    if created.tzinfo is None:
        raise IntegrityError(
            f"Prediction commitment time lacks timezone: {commitment_id}"
        )


@contextmanager
def _destination_lock(target: Path) -> Generator[None, None, None]:
    lock = target.with_name(f".{target.name}.recovery.lock")
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise FileExistsError(
            f"State destination is reserved by another operation: {target}"
        ) from exc
    try:
        os.write(descriptor, f"{os.getpid()}\n".encode("ascii"))
        os.fsync(descriptor)
        yield
    finally:
        os.close(descriptor)
        lock.unlink(missing_ok=True)


def _write_json_exclusive(path: Path, value: object) -> None:
    temporary: Path | None = None
    try:
        descriptor, name = tempfile.mkstemp(
            prefix=f".{path.name}-",
            suffix=".part",
            dir=path.parent,
        )
        temporary = Path(name)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as output:
            json.dump(value, output, indent=2, sort_keys=True, allow_nan=False)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.link(temporary, path)
        temporary.unlink()
        temporary = None
        _fsync_directory(path.parent)
    except OSError as exc:
        raise StorageError(f"Could not write application-state JSON: {path}") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _fsync_directory(path: Path) -> None:
    flags = getattr(os, "O_DIRECTORY", 0) | os.O_RDONLY
    try:
        descriptor = os.open(path, flags)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


__all__ = ["StateRecoveryManager"]
