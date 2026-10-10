"""Verified backup and non-destructive restore for the managed data store."""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import tempfile
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from emrf.core.errors import IntegrityError, StorageError

from .store import ContentAddressedStore

_BACKUP_SCHEMA = "1.0.0"
_MANIFEST = "backup_manifest.json"


class BackupManager:
    """Create and restore self-verifying portable store backups."""

    def __init__(self, store: ContentAddressedStore) -> None:
        self.store = store

    def create(self, destination: str | Path) -> dict[str, Any]:
        target = Path(destination).expanduser().resolve()
        if target.exists():
            raise FileExistsError(f"Backup destination already exists: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=f".{target.name}-", dir=target.parent))
        try:
            objects = self.store.list_objects(verify=True)
            holdings = self.store.list_holdings(verify=True)
            object_rows: list[dict[str, Any]] = []
            for stored in objects:
                relative = Path("objects") / stored.sha256[:2] / stored.sha256[2:]
                copied = staging / relative
                copied.parent.mkdir(parents=True, exist_ok=True)
                _copy_fsynced(stored.path, copied)
                object_rows.append(
                    {
                        "sha256": stored.sha256,
                        "bytes": stored.bytes,
                        "path": relative.as_posix(),
                    }
                )
            holding_rows = [
                {
                    "dataset_id": holding.dataset_id,
                    "version": holding.version,
                    "logical_name": holding.logical_name,
                    "sha256": holding.sha256,
                    "source_url": holding.source_url,
                    "citation": holding.citation,
                    "licence": holding.licence,
                    "metadata": holding.metadata,
                }
                for holding in holdings
            ]
            manifest = {
                "schema_version": _BACKUP_SCHEMA,
                "created_utc": datetime.now(timezone.utc).isoformat(),
                "objects": object_rows,
                "holdings": holding_rows,
            }
            _write_json_fsynced(staging / _MANIFEST, manifest)
            self.store.backup_registry(staging / "library.sqlite")
            self.verify(staging)
            os.replace(staging, target)
            return manifest
        except Exception:
            shutil.rmtree(staging, ignore_errors=True)
            raise

    def verify(self, source: str | Path) -> dict[str, Any]:
        root, manifest = _read_manifest(source)
        object_keys: set[tuple[str, int]] = set()
        for entry in manifest["objects"]:
            path = _safe_object_path(root, entry)
            key = (entry["sha256"], entry["bytes"])
            if key in object_keys:
                raise IntegrityError(f"Backup repeats object: {entry['sha256']}")
            object_keys.add(key)
            ContentAddressedStore._verify_path(
                path,
                entry["sha256"],
                entry["bytes"],
            )
        holding_keys: set[tuple[str, str, str]] = set()
        for entry in manifest["holdings"]:
            key = _validate_holding(entry, {digest for digest, _ in object_keys})
            if key in holding_keys:
                raise IntegrityError(f"Backup repeats holding: {key}")
            holding_keys.add(key)
        _verify_registry_snapshot(root, manifest)
        return manifest

    def restore(self, source: str | Path) -> dict[str, int]:
        root, manifest = _read_manifest(source)
        self.verify(root)
        objects_by_hash: dict[str, Any] = {}
        for entry in manifest["objects"]:
            stored = self.store.put_file(
                _safe_object_path(root, entry),
                expected_sha256=entry["sha256"],
                expected_bytes=entry["bytes"],
            )
            objects_by_hash[stored.sha256] = stored
        for entry in manifest["holdings"]:
            try:
                stored = objects_by_hash[entry["sha256"]]
            except KeyError:
                raise IntegrityError(
                    f"Backup holding references missing object: {entry['sha256']}"
                ) from None
            self.store.register_holding(
                entry["dataset_id"],
                entry["version"],
                entry["logical_name"],
                stored,
                source_url=entry.get("source_url"),
                citation=entry.get("citation"),
                licence=entry.get("licence"),
                metadata=entry.get("metadata"),
            )
        return {
            "objects": len(manifest["objects"]),
            "holdings": len(manifest["holdings"]),
        }


def _read_manifest(source: str | Path) -> tuple[Path, dict[str, Any]]:
    root = Path(source).expanduser().resolve()
    try:
        manifest = json.loads((root / _MANIFEST).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IntegrityError(f"Could not read backup manifest: {root}") from exc
    if manifest.get("schema_version") != _BACKUP_SCHEMA:
        raise IntegrityError("Unsupported backup manifest schema")
    for field in ("objects", "holdings"):
        if not isinstance(manifest.get(field), list):
            raise IntegrityError(f"Backup manifest '{field}' must be a list")
    return root, manifest


def _safe_object_path(root: Path, entry: object) -> Path:
    if not isinstance(entry, dict):
        raise IntegrityError("Backup object entries must be JSON objects")
    digest = entry.get("sha256")
    size = entry.get("bytes")
    relative = entry.get("path")
    if (
        not isinstance(digest, str)
        or len(digest) != 64
        or any(char not in "0123456789abcdef" for char in digest)
        or not isinstance(size, int)
        or size < 0
        or not isinstance(relative, str)
    ):
        raise IntegrityError("Backup contains invalid object metadata")
    expected = Path("objects") / digest[:2] / digest[2:]
    if Path(relative) != expected:
        raise IntegrityError(f"Backup object path is not canonical: {relative}")
    unresolved = root / expected
    if unresolved.is_symlink():
        raise IntegrityError(f"Backup object must not be a symbolic link: {relative}")
    path = unresolved.resolve()
    if root not in path.parents:
        raise IntegrityError("Backup object path escapes the backup root")
    return unresolved


def _validate_holding(
    entry: object,
    object_hashes: set[str],
) -> tuple[str, str, str]:
    if not isinstance(entry, dict):
        raise IntegrityError("Backup holding entries must be JSON objects")
    dataset_id = entry.get("dataset_id")
    version = entry.get("version")
    logical_name = entry.get("logical_name")
    if not all(
        isinstance(value, str) and value.strip()
        for value in (dataset_id, version, logical_name)
    ):
        raise IntegrityError("Backup contains an invalid holding key")
    digest = entry.get("sha256")
    if not isinstance(digest, str) or digest not in object_hashes:
        raise IntegrityError(f"Backup holding references missing object: {digest}")
    source_url = entry.get("source_url")
    if source_url is not None and (
        not isinstance(source_url, str) or not source_url.startswith("https://")
    ):
        raise IntegrityError("Backup holding contains an invalid source URL")
    for field in ("citation", "licence"):
        value = entry.get(field)
        if value is not None and not isinstance(value, str):
            raise IntegrityError(f"Backup holding contains invalid {field}")
    if not isinstance(entry.get("metadata"), dict):
        raise IntegrityError("Backup holding metadata must be a JSON object")
    assert isinstance(dataset_id, str)
    assert isinstance(version, str)
    assert isinstance(logical_name, str)
    return dataset_id, version, logical_name


def _verify_registry_snapshot(root: Path, manifest: dict[str, Any]) -> None:
    registry = root / "library.sqlite"
    if registry.is_symlink() or not registry.is_file():
        raise IntegrityError("Backup registry snapshot is missing or symbolic")
    try:
        uri = f"{registry.as_uri()}?mode=ro"
        with closing(sqlite3.connect(uri, uri=True)) as connection:
            if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise IntegrityError("Backup registry failed SQLite integrity check")
            objects = set(connection.execute("SELECT sha256, bytes FROM objects"))
            holdings = {
                (
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    row[6],
                    json.dumps(
                        json.loads(row[7]),
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                )
                for row in connection.execute(
                    """
                    SELECT dataset_id, version, logical_name, sha256, source_url,
                           citation, licence, metadata_json
                    FROM holdings
                    """
                )
            }
    except (OSError, sqlite3.Error, json.JSONDecodeError) as exc:
        raise IntegrityError("Could not verify backup registry snapshot") from exc
    expected_objects = {
        (entry["sha256"], entry["bytes"]) for entry in manifest["objects"]
    }
    expected_holdings = {
        (
            entry["dataset_id"],
            entry["version"],
            entry["logical_name"],
            entry["sha256"],
            entry.get("source_url"),
            entry.get("citation"),
            entry.get("licence"),
            json.dumps(entry["metadata"], sort_keys=True, separators=(",", ":")),
        )
        for entry in manifest["holdings"]
    }
    if objects != expected_objects or holdings != expected_holdings:
        raise IntegrityError("Backup manifest and registry snapshot differ")


def _copy_fsynced(source: Path, destination: Path) -> None:
    try:
        with source.open("rb") as input_file, destination.open("xb") as output:
            shutil.copyfileobj(input_file, output, length=1024 * 1024)
            output.flush()
            os.fsync(output.fileno())
    except OSError as exc:
        raise StorageError(f"Could not copy backup object: {source}") from exc


def _write_json_fsynced(path: Path, value: object) -> None:
    try:
        with path.open("x", encoding="utf-8", newline="\n") as output:
            json.dump(value, output, indent=2, sort_keys=True)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
    except OSError as exc:
        raise StorageError(f"Could not write backup manifest: {path}") from exc
