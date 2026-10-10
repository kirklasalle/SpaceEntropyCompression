"""Content-addressed, crash-safe storage for immutable observation bytes."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import tempfile
import threading
import time
from collections.abc import Generator, Mapping
from contextlib import closing, contextmanager, suppress
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO

from emrf.core.errors import IntegrityError, StorageError
from emrf_paths import data_root

_BUFFER_SIZE = 1024 * 1024
_SCHEMA = """
CREATE TABLE IF NOT EXISTS objects (
    sha256 TEXT PRIMARY KEY CHECK(length(sha256) = 64),
    bytes INTEGER NOT NULL CHECK(bytes >= 0),
    created_utc TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS holdings (
    dataset_id TEXT NOT NULL,
    version TEXT NOT NULL,
    logical_name TEXT NOT NULL,
    sha256 TEXT NOT NULL REFERENCES objects(sha256),
    source_url TEXT,
    citation TEXT,
    licence TEXT,
    metadata_json TEXT NOT NULL,
    created_utc TEXT NOT NULL,
    PRIMARY KEY (dataset_id, version, logical_name)
);
CREATE INDEX IF NOT EXISTS holdings_sha256_idx ON holdings(sha256);
"""


@dataclass(frozen=True)
class StoredObject:
    """Identity and location of one immutable stored byte sequence."""

    sha256: str
    bytes: int
    path: Path


@dataclass(frozen=True)
class Holding:
    """A dataset/version/logical-name view of a stored object."""

    dataset_id: str
    version: str
    logical_name: str
    sha256: str
    bytes: int
    path: Path
    source_url: str | None
    citation: str | None
    licence: str | None
    metadata: dict[str, Any]


class ContentAddressedStore:
    """Immutable SHA-256 object store with transactional holding metadata.

    Object promotion uses an fsynced temporary file and atomic replacement.
    Parent-directory fsync is best effort because Windows does not expose a
    portable directory fsync operation.
    """

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else data_root()
        self.objects = self.root / "store" / "sha256"
        self.temporary = self.root / "store" / "tmp"
        self.registry = self.root / "library.sqlite"
        self._initialization_lock = threading.Lock()
        self._promotion_lock = threading.Lock()
        self._initialized = False

    def initialize(self) -> None:
        """Create store directories and the WAL-enabled registry schema."""
        if self._initialized:
            return
        with self._initialization_lock:
            if self._initialized:
                return
            try:
                self.objects.mkdir(parents=True, exist_ok=True)
                self.temporary.mkdir(parents=True, exist_ok=True)
                self.prune_temporary()
                with self._connect() as connection:
                    connection.executescript(_SCHEMA)
                self._initialized = True
            except (OSError, sqlite3.Error) as exc:
                raise StorageError(
                    f"Could not initialize data store at {self.root}"
                ) from exc

    def prune_temporary(self, max_age_seconds: float = 7 * 86400) -> int:
        """Remove abandoned partial objects older than the conservative cutoff."""
        if max_age_seconds < 0:
            raise ValueError("max_age_seconds must be nonnegative")
        if not self.temporary.is_dir():
            return 0
        cutoff = time.time() - max_age_seconds
        removed = 0
        for path in self.temporary.glob("object-*.part"):
            try:
                if path.stat().st_mtime < cutoff:
                    path.unlink()
                    removed += 1
            except FileNotFoundError:
                pass
            except OSError as exc:
                raise StorageError(f"Could not prune temporary object: {path}") from exc
        return removed

    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection, None, None]:
        self.root.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.registry, timeout=30.0)
        try:
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA busy_timeout = 30000")
            connection.execute("PRAGMA foreign_keys = ON")
            _enable_wal(connection)
            connection.execute("PRAGMA synchronous = FULL")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def object_path(self, sha256: str) -> Path:
        """Return the canonical path for a validated SHA-256 digest."""
        digest = sha256.lower()
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("sha256 must be 64 lowercase hexadecimal characters")
        return self.objects / digest[:2] / digest[2:]

    def put_bytes(
        self,
        data: bytes,
        *,
        expected_sha256: str | None = None,
        expected_bytes: int | None = None,
    ) -> StoredObject:
        """Atomically store bytes after optional size and digest verification."""
        return self._put_stream(
            source=_BytesReader(data),
            expected_sha256=expected_sha256,
            expected_bytes=expected_bytes,
        )

    def put_file(
        self,
        source: str | Path,
        *,
        expected_sha256: str | None = None,
        expected_bytes: int | None = None,
    ) -> StoredObject:
        """Stream a file into the store without modifying the source."""
        path = Path(source)
        try:
            with path.open("rb") as stream:
                return self._put_stream(
                    stream,
                    expected_sha256=expected_sha256,
                    expected_bytes=expected_bytes,
                )
        except IntegrityError:
            raise
        except OSError as exc:
            raise StorageError(f"Could not read source object: {path}") from exc

    def _put_stream(
        self,
        source: BinaryIO,
        *,
        expected_sha256: str | None,
        expected_bytes: int | None,
    ) -> StoredObject:
        self.initialize()
        digest = hashlib.sha256()
        size = 0
        temporary_path: Path | None = None
        try:
            descriptor, name = tempfile.mkstemp(
                prefix="object-", suffix=".part", dir=self.temporary
            )
            temporary_path = Path(name)
            with os.fdopen(descriptor, "wb") as output:
                while chunk := source.read(_BUFFER_SIZE):
                    output.write(chunk)
                    digest.update(chunk)
                    size += len(chunk)
                output.flush()
                os.fsync(output.fileno())
            actual_sha256 = digest.hexdigest()
            if expected_bytes is not None and size != expected_bytes:
                raise IntegrityError(f"Expected {expected_bytes} bytes, received {size}")
            if expected_sha256 is not None and actual_sha256 != expected_sha256.lower():
                raise IntegrityError(
                    f"Expected SHA-256 {expected_sha256.lower()}, received {actual_sha256}"
                )
            destination = self.object_path(actual_sha256)
            destination.parent.mkdir(parents=True, exist_ok=True)
            with self._promotion_lock:
                if destination.exists():
                    try:
                        self._verify_existing(destination, actual_sha256, size)
                    except IntegrityError:
                        with suppress(OSError):
                            destination.chmod(0o600)
                        os.replace(temporary_path, destination)
                        temporary_path = None
                        _fsync_directory(destination.parent)
                    else:
                        temporary_path.unlink()
                        temporary_path = None
                else:
                    try:
                        os.replace(temporary_path, destination)
                    except (FileExistsError, PermissionError):
                        self._verify_existing(destination, actual_sha256, size)
                        temporary_path.unlink()
                    temporary_path = None
                    _fsync_directory(destination.parent)
            created = datetime.now(timezone.utc).isoformat()
            with self._connect() as connection:
                connection.execute(
                    "INSERT OR IGNORE INTO objects (sha256, bytes, created_utc) VALUES (?, ?, ?)",
                    (actual_sha256, size, created),
                )
            return StoredObject(actual_sha256, size, destination)
        except StorageError:
            raise
        except (OSError, sqlite3.Error) as exc:
            raise StorageError(f"Could not store object under {self.root}") from exc
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    def register_holding(
        self,
        dataset_id: str,
        version: str,
        logical_name: str,
        stored: StoredObject,
        *,
        source_url: str | None = None,
        citation: str | None = None,
        licence: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> Holding:
        """Transactionally bind a logical dataset name to an immutable object."""
        for field, value in (
            ("dataset_id", dataset_id),
            ("version", version),
            ("logical_name", logical_name),
        ):
            if not value or not value.strip():
                raise ValueError(f"{field} must not be empty")
        dataset_id = dataset_id.strip()
        version = version.strip()
        logical_name = logical_name.strip()
        verified = self.get(stored.sha256, verify=True)
        if verified.bytes != stored.bytes:
            raise IntegrityError("Stored object size does not match registry request")
        if source_url is not None and not source_url.startswith("https://"):
            raise ValueError("source_url must use HTTPS")
        metadata_json = json.dumps(dict(metadata or {}), sort_keys=True, separators=(",", ":"))
        created = datetime.now(timezone.utc).isoformat()
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT OR IGNORE INTO holdings (
                        dataset_id, version, logical_name, sha256, source_url,
                        citation, licence, metadata_json, created_utc
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        dataset_id,
                        version,
                        logical_name,
                        stored.sha256,
                        source_url,
                        citation,
                        licence,
                        metadata_json,
                        created,
                    ),
                )
                existing = connection.execute(
                    """
                    SELECT sha256, source_url, citation, licence, metadata_json
                    FROM holdings
                    WHERE dataset_id = ? AND version = ? AND logical_name = ?
                    """,
                    (dataset_id, version, logical_name),
                ).fetchone()
                if existing is None or existing["sha256"] != stored.sha256:
                    raise IntegrityError(
                        "A holding cannot be rebound to different observation bytes"
                    )
                existing_provenance = (
                    existing["source_url"],
                    existing["citation"],
                    existing["licence"],
                    existing["metadata_json"],
                )
                requested_provenance = (source_url, citation, licence, metadata_json)
                if existing_provenance != requested_provenance:
                    raise IntegrityError(
                        "A holding's provenance metadata is immutable; register a new version"
                    )
        except sqlite3.Error as exc:
            raise StorageError("Could not register dataset holding") from exc
        return self.get_holding(dataset_id, version, logical_name, verify=False)

    def get(self, sha256: str, *, verify: bool = True) -> StoredObject:
        """Return an object and optionally re-hash it before use."""
        path = self.object_path(sha256)
        if path.is_symlink():
            raise IntegrityError(f"Stored object must not be a symbolic link: {path}")
        if not path.is_file():
            raise FileNotFoundError(path)
        size = path.stat().st_size
        if verify:
            self._verify_path(path, sha256.lower(), size)
        return StoredObject(sha256.lower(), size, path)

    def get_holding(
        self,
        dataset_id: str,
        version: str,
        logical_name: str,
        *,
        verify: bool = True,
    ) -> Holding:
        """Resolve a logical holding and fail if its object is missing or corrupt."""
        try:
            with self._connect() as connection:
                row = connection.execute(
                    """
                    SELECT h.*, o.bytes
                    FROM holdings h JOIN objects o ON o.sha256 = h.sha256
                    WHERE h.dataset_id = ? AND h.version = ? AND h.logical_name = ?
                    """,
                    (dataset_id, version, logical_name),
                ).fetchone()
        except sqlite3.Error as exc:
            raise StorageError("Could not query dataset holding") from exc
        if row is None:
            raise KeyError((dataset_id, version, logical_name))
        stored = self.get(row["sha256"], verify=verify)
        if stored.bytes != row["bytes"]:
            raise IntegrityError("Stored object size differs from registry metadata")
        return Holding(
            dataset_id=row["dataset_id"],
            version=row["version"],
            logical_name=row["logical_name"],
            sha256=row["sha256"],
            bytes=row["bytes"],
            path=stored.path,
            source_url=row["source_url"],
            citation=row["citation"],
            licence=row["licence"],
            metadata=json.loads(row["metadata_json"]),
        )

    def list_objects(self, *, verify: bool = False) -> list[StoredObject]:
        """List registry objects, optionally verifying every byte sequence."""
        self.initialize()
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    "SELECT sha256, bytes FROM objects ORDER BY sha256"
                ).fetchall()
        except sqlite3.Error as exc:
            raise StorageError("Could not list stored objects") from exc
        objects: list[StoredObject] = []
        for row in rows:
            stored = self.get(row["sha256"], verify=verify)
            if stored.bytes != row["bytes"]:
                raise IntegrityError("Stored object size differs from registry metadata")
            objects.append(stored)
        return objects

    def list_holdings(self, *, verify: bool = False) -> list[Holding]:
        """List logical holdings in stable key order."""
        self.initialize()
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT dataset_id, version, logical_name
                    FROM holdings
                    ORDER BY dataset_id, version, logical_name
                    """
                ).fetchall()
        except sqlite3.Error as exc:
            raise StorageError("Could not list dataset holdings") from exc
        return [
            self.get_holding(
                row["dataset_id"],
                row["version"],
                row["logical_name"],
                verify=verify,
            )
            for row in rows
        ]

    def garbage_collect(self, *, execute: bool = False) -> list[StoredObject]:
        """Find or remove objects that are not referenced by any holding."""
        self.initialize()
        try:
            with self._connect() as connection:
                if execute:
                    connection.execute("BEGIN IMMEDIATE")
                rows = connection.execute(
                    """
                    SELECT o.sha256, o.bytes
                    FROM objects o
                    LEFT JOIN holdings h ON h.sha256 = o.sha256
                    WHERE h.sha256 IS NULL
                    ORDER BY o.sha256
                    """
                ).fetchall()
                objects = [
                    self.get(row["sha256"], verify=True)
                    for row in rows
                ]
                if execute and rows:
                    connection.executemany(
                        "DELETE FROM objects WHERE sha256 = ?",
                        ((row["sha256"],) for row in rows),
                    )
            if execute:
                for stored in objects:
                    stored.path.unlink(missing_ok=True)
            return objects
        except sqlite3.Error as exc:
            raise StorageError("Could not garbage-collect stored objects") from exc

    def backup_registry(self, destination: str | Path) -> Path:
        """Write a transactionally consistent SQLite registry snapshot."""
        self.initialize()
        target = Path(destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            with (
                closing(sqlite3.connect(self.registry)) as source,
                closing(sqlite3.connect(target)) as backup,
            ):
                source.backup(backup)
        except (OSError, sqlite3.Error) as exc:
            raise StorageError(f"Could not back up registry to {target}") from exc
        return target

    @staticmethod
    def _verify_path(path: Path, expected_sha256: str, expected_bytes: int) -> None:
        if path.is_symlink():
            raise IntegrityError(f"Stored object must not be a symbolic link: {path}")
        digest = hashlib.sha256()
        size = 0
        try:
            with path.open("rb") as stream:
                while chunk := stream.read(_BUFFER_SIZE):
                    digest.update(chunk)
                    size += len(chunk)
        except OSError as exc:
            raise StorageError(f"Could not verify stored object: {path}") from exc
        if size != expected_bytes or digest.hexdigest() != expected_sha256:
            raise IntegrityError(f"Stored object failed integrity verification: {path}")

    @classmethod
    def _verify_existing(
        cls,
        path: Path,
        expected_sha256: str,
        expected_bytes: int,
    ) -> None:
        for attempt in range(10):
            try:
                cls._verify_path(path, expected_sha256, expected_bytes)
                return
            except StorageError as exc:
                if not isinstance(exc.__cause__, PermissionError) or attempt == 9:
                    raise
                time.sleep(0.01 * (attempt + 1))


class _BytesReader:
    def __init__(self, data: bytes) -> None:
        self._data = data
        self._position = 0

    def read(self, size: int = -1) -> bytes:
        if self._position >= len(self._data):
            return b""
        end = len(self._data) if size < 0 else self._position + size
        chunk = self._data[self._position : end]
        self._position += len(chunk)
        return chunk


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


def _enable_wal(connection: sqlite3.Connection) -> None:
    for attempt in range(100):
        try:
            journal_mode = connection.execute("PRAGMA journal_mode").fetchone()[0]
            if journal_mode.lower() != "wal":
                connection.execute("PRAGMA journal_mode = WAL")
            return
        except sqlite3.OperationalError as exc:
            if "locked" not in str(exc).lower() or attempt == 99:
                raise
            time.sleep(min(0.01 * (attempt + 1), 0.1))
