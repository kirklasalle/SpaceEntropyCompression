"""Atomic scientific run records and a crash-recoverable SQLite job queue."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import math
import os
import platform
import re
import sqlite3
import subprocess
import sys
import tempfile
import time
import uuid
from collections.abc import Generator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from emrf.core.errors import IntegrityError, StorageError
from emrf_paths import app_root, project_root

_RUN_ID = re.compile(r"^\d{8}T\d{12}Z-[0-9a-f]{8}$")
_CHECKPOINT_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_RUN_STATES = {"pending", "running", "succeeded", "failed", "timed_out", "interrupted"}
_JOB_STATES = {"queued", "running", "succeeded", "failed", "cancelled"}

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    command TEXT NOT NULL,
    args_json TEXT NOT NULL,
    evidence_class TEXT NOT NULL,
    status TEXT NOT NULL,
    attempt INTEGER NOT NULL,
    created_utc TEXT NOT NULL,
    started_utc TEXT,
    completed_utc TEXT,
    returncode INTEGER,
    duration_seconds REAL,
    run_path TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    command TEXT NOT NULL,
    args_json TEXT NOT NULL,
    timeout_seconds REAL,
    evidence_class TEXT NOT NULL,
    status TEXT NOT NULL,
    attempts INTEGER NOT NULL,
    max_attempts INTEGER NOT NULL,
    created_utc TEXT NOT NULL,
    updated_utc TEXT NOT NULL,
    lease_owner TEXT,
    lease_expires_utc TEXT,
    run_id TEXT REFERENCES runs(run_id),
    returncode INTEGER,
    last_error TEXT
);
CREATE INDEX IF NOT EXISTS jobs_status_created_idx ON jobs(status, created_utc);
"""


class EvidenceClass(str, Enum):
    OBSERVATIONAL = "observational"
    PUBLISHED_SUMMARY = "published"
    SYNTHETIC = "synthetic"
    ILLUSTRATIVE = "illustrative"
    SOFTWARE = "software"


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    command: str
    args: tuple[str, ...]
    evidence_class: str
    status: str
    attempt: int
    created_utc: str
    started_utc: str | None
    completed_utc: str | None
    returncode: int | None
    duration_seconds: float | None
    path: Path
    environment_sha256: str
    git_commit: str | None
    git_dirty: bool | None
    inputs: dict[str, str]
    seeds: dict[str, int]


@dataclass(frozen=True)
class JobRecord:
    job_id: str
    command: str
    args: tuple[str, ...]
    timeout_seconds: float | None
    evidence_class: str
    status: str
    attempts: int
    max_attempts: int
    created_utc: str
    updated_utc: str
    lease_owner: str | None
    lease_expires_utc: str | None
    run_id: str | None
    returncode: int | None
    last_error: str | None


class RunStore:
    """Manage immutable run configuration, mutable state and queued jobs."""

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else app_root() / "runs"
        self.registry = self.root / "registry.sqlite"
        self._initialized = False

    def initialize(self) -> None:
        if self._initialized:
            return
        try:
            self.root.mkdir(parents=True, exist_ok=True)
            with self._connect() as connection:
                connection.executescript(_SCHEMA)
            self._reconcile_run_index()
            self._initialized = True
        except (OSError, sqlite3.Error) as exc:
            raise StorageError(f"Could not initialize run store at {self.root}") from exc

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

    def create(
        self,
        command: str,
        args: list[str] | tuple[str, ...],
        *,
        evidence_class: str = EvidenceClass.SOFTWARE.value,
        inputs: Mapping[str, str] | None = None,
        seeds: Mapping[str, int] | None = None,
    ) -> RunRecord:
        self.initialize()
        clean_command = _validate_command(command)
        evidence = _validate_evidence(evidence_class)
        clean_args = _validate_args(args)
        clean_inputs = _validate_inputs(inputs or {})
        clean_seeds = _validate_seeds(seeds or {})
        run_id = _new_id()
        path = self.root / run_id
        staging = self.root / f".{run_id}-{uuid.uuid4().hex}.part"
        staging.mkdir(exist_ok=False)
        created = _utc_now()
        git_commit, git_dirty = _git_state()
        environment_sha256 = _environment_sha256()
        payload: dict[str, Any] = {
            "run_id": run_id,
            "command": clean_command,
            "args": list(clean_args),
            "evidence_class": evidence,
            "status": "pending",
            "attempt": 0,
            "created_utc": created,
            "started_utc": None,
            "completed_utc": None,
            "returncode": None,
            "duration_seconds": None,
            "environment_sha256": environment_sha256,
            "git_commit": git_commit,
            "git_dirty": git_dirty,
            "inputs": clean_inputs,
            "seeds": clean_seeds,
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "executable": sys.executable,
        }
        try:
            _write_json_atomic(staging / "run.json", payload)
            _write_config_toml(staging / "config.toml", payload)
            os.replace(staging, path)
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT OR IGNORE INTO runs (
                        run_id, command, args_json, evidence_class, status, attempt,
                        created_utc, run_path
                    ) VALUES (?, ?, ?, ?, 'pending', 0, ?, ?)
                    """,
                    (
                        run_id,
                        clean_command,
                        json.dumps(list(clean_args), separators=(",", ":")),
                        evidence,
                        created,
                        str(path),
                    ),
                )
        except Exception:
            _remove_run_files(staging)
            raise
        return self.get(run_id)

    def begin(self, run_id: str, *, resume: bool = False) -> RunRecord:
        self.initialize()
        record = self.get(run_id)
        if resume:
            if record.status not in {"failed", "timed_out", "interrupted"}:
                raise ValueError(f"Run cannot be resumed from status: {record.status}")
        elif record.status != "pending":
            raise ValueError(f"Run cannot begin from status: {record.status}")
        attempt = record.attempt + 1
        started = _utc_now()
        self._update(
            run_id,
            status="running",
            attempt=attempt,
            started_utc=started,
            completed_utc=None,
            returncode=None,
            duration_seconds=None,
        )
        return self.get(run_id)

    def finish(
        self,
        run_id: str,
        *,
        status: str,
        returncode: int | None,
        duration_seconds: float,
    ) -> RunRecord:
        self.initialize()
        if status not in {"succeeded", "failed", "timed_out", "interrupted"}:
            raise ValueError(f"Invalid terminal run status: {status}")
        self._update(
            run_id,
            status=status,
            completed_utc=_utc_now(),
            returncode=returncode,
            duration_seconds=round(duration_seconds, 6),
        )
        return self.get(run_id)

    def get(self, run_id: str) -> RunRecord:
        self.initialize()
        return self._read_run(run_id)

    def _read_run(self, run_id: str) -> RunRecord:
        path = self._run_path(run_id)
        try:
            payload = json.loads((path / "run.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise IntegrityError(f"Could not read run record: {run_id}") from exc
        return _run_from_payload(payload, path)

    def list(self, limit: int = 50) -> list[RunRecord]:
        if limit < 1 or limit > 1000:
            raise ValueError("limit must be in [1, 1000]")
        self.initialize()
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT run_id FROM runs ORDER BY created_utc DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [self.get(row["run_id"]) for row in rows]

    def save_checkpoint(
        self,
        run_id: str,
        name: str,
        value: Mapping[str, Any],
    ) -> Path:
        record = self.get(run_id)
        if not _CHECKPOINT_NAME.fullmatch(name):
            raise ValueError("checkpoint name must be lowercase kebab-case")
        destination = record.path / "checkpoints" / f"{name}.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        _write_json_atomic(destination, dict(value))
        return destination

    def write_log(self, run_id: str, stream: str, attempt: int, value: str) -> Path:
        record = self.get(run_id)
        if stream not in {"stdout", "stderr"}:
            raise ValueError("stream must be stdout or stderr")
        if attempt < 1:
            raise ValueError("attempt must be positive")
        destination = record.path / f"{stream}-{attempt}.txt"
        _write_text_atomic(destination, value)
        return destination

    def load_checkpoint(self, run_id: str, name: str) -> dict[str, Any]:
        if not _CHECKPOINT_NAME.fullmatch(name):
            raise ValueError("checkpoint name must be lowercase kebab-case")
        path = self._run_path(run_id) / "checkpoints" / f"{name}.json"
        if path.is_symlink():
            raise IntegrityError(f"Checkpoint must not be a symbolic link: {path}")
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise IntegrityError(f"Could not read checkpoint: {run_id}/{name}") from exc
        if not isinstance(value, dict):
            raise IntegrityError("Checkpoint payload must be a JSON object")
        return value

    def checkpoint_exists(self, run_id: str, name: str) -> bool:
        if not _CHECKPOINT_NAME.fullmatch(name):
            raise ValueError("checkpoint name must be lowercase kebab-case")
        path = self._run_path(run_id) / "checkpoints" / f"{name}.json"
        if path.is_symlink():
            raise IntegrityError(f"Checkpoint must not be a symbolic link: {path}")
        return path.is_file()

    def enqueue(
        self,
        command: str,
        args: list[str] | tuple[str, ...],
        *,
        timeout_seconds: float | None = None,
        evidence_class: str = EvidenceClass.SOFTWARE.value,
        max_attempts: int = 1,
    ) -> JobRecord:
        self.initialize()
        clean_command = _validate_command(command)
        clean_args = _validate_args(args)
        evidence = _validate_evidence(evidence_class)
        if timeout_seconds is not None and (
            isinstance(timeout_seconds, bool)
            or not isinstance(timeout_seconds, (int, float))
            or not math.isfinite(timeout_seconds)
            or timeout_seconds <= 0
        ):
            raise ValueError("timeout_seconds must be positive")
        if (
            isinstance(max_attempts, bool)
            or not isinstance(max_attempts, int)
            or not 1 <= max_attempts <= 100
        ):
            raise ValueError("max_attempts must be in [1, 100]")
        job_id = _new_id()
        now = _utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO jobs (
                    job_id, command, args_json, timeout_seconds, evidence_class,
                    status, attempts, max_attempts, created_utc, updated_utc
                ) VALUES (?, ?, ?, ?, ?, 'queued', 0, ?, ?, ?)
                """,
                (
                    job_id,
                    clean_command,
                    json.dumps(list(clean_args), separators=(",", ":")),
                    timeout_seconds,
                    evidence,
                    max_attempts,
                    now,
                    now,
                ),
            )
        return self.get_job(job_id)

    def claim(
        self,
        worker_id: str,
        *,
        lease_seconds: float = 3600,
    ) -> JobRecord | None:
        if not isinstance(worker_id, str) or not worker_id.strip():
            raise ValueError("worker_id must not be empty")
        if (
            isinstance(lease_seconds, bool)
            or not isinstance(lease_seconds, (int, float))
            or not math.isfinite(lease_seconds)
            or lease_seconds <= 0
        ):
            raise ValueError("lease_seconds must be positive")
        self.initialize()
        now = datetime.now(timezone.utc)
        expires = (now + timedelta(seconds=lease_seconds)).isoformat()
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                """
                UPDATE jobs
                SET status='failed', lease_owner=NULL, lease_expires_utc=NULL,
                    updated_utc=?, last_error='Worker lease expired after final attempt'
                WHERE status='running' AND lease_expires_utc IS NOT NULL
                  AND lease_expires_utc < ? AND attempts >= max_attempts
                """,
                (now.isoformat(), now.isoformat()),
            )
            connection.execute(
                """
                UPDATE jobs
                SET status='queued', lease_owner=NULL, lease_expires_utc=NULL,
                    updated_utc=?, last_error='Previous worker lease expired'
                WHERE status='running' AND lease_expires_utc IS NOT NULL
                  AND lease_expires_utc < ?
                  AND attempts < max_attempts
                """,
                (now.isoformat(), now.isoformat()),
            )
            row = connection.execute(
                """
                SELECT job_id FROM jobs
                WHERE status='queued' AND attempts < max_attempts
                ORDER BY created_utc, job_id
                LIMIT 1
                """
            ).fetchone()
            if row is None:
                return None
            connection.execute(
                """
                UPDATE jobs
                SET status='running', attempts=attempts+1, updated_utc=?,
                    lease_owner=?, lease_expires_utc=?, last_error=NULL
                WHERE job_id=? AND status='queued'
                """,
                (now.isoformat(), worker_id, expires, row["job_id"]),
            )
        return self.get_job(row["job_id"])

    def attach_run(self, job_id: str, run_id: str) -> JobRecord:
        self.get(run_id)
        self._update_job(job_id, run_id=run_id)
        return self.get_job(job_id)

    def complete_job(
        self,
        job_id: str,
        *,
        returncode: int | None,
        error: str | None = None,
    ) -> JobRecord:
        job = self.get_job(job_id)
        if job.status != "running":
            raise ValueError(f"Job cannot complete from status: {job.status}")
        succeeded = returncode == 0 and error is None
        if succeeded:
            status = "succeeded"
        elif job.attempts < job.max_attempts:
            status = "queued"
        else:
            status = "failed"
        self._update_job(
            job_id,
            status=status,
            returncode=returncode,
            last_error=error,
            lease_owner=None,
            lease_expires_utc=None,
        )
        return self.get_job(job_id)

    def cancel_job(self, job_id: str) -> JobRecord:
        job = self.get_job(job_id)
        if job.status != "queued":
            raise ValueError(f"Job cannot be cancelled from status: {job.status}")
        self._update_job(job_id, status="cancelled")
        return self.get_job(job_id)

    def get_job(self, job_id: str) -> JobRecord:
        _validate_id(job_id, "job")
        self.initialize()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM jobs WHERE job_id = ?",
                (job_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"Unknown job: {job_id}")
        return _job_from_row(row)

    def list_jobs(self, limit: int = 50) -> list[JobRecord]:
        if limit < 1 or limit > 1000:
            raise ValueError("limit must be in [1, 1000]")
        self.initialize()
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM jobs ORDER BY created_utc DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [_job_from_row(row) for row in rows]

    def _update(self, run_id: str, **changes: Any) -> None:
        record = self.get(run_id)
        payload = json.loads((record.path / "run.json").read_text(encoding="utf-8"))
        payload.update(changes)
        status = payload.get("status")
        if status not in _RUN_STATES:
            raise ValueError(f"Invalid run status: {status}")
        _write_json_atomic(record.path / "run.json", payload)
        columns = {
            "status",
            "attempt",
            "started_utc",
            "completed_utc",
            "returncode",
            "duration_seconds",
        }
        database_changes = {key: value for key, value in changes.items() if key in columns}
        if database_changes:
            assignments = ", ".join(f"{key} = ?" for key in database_changes)
            values = [*database_changes.values(), run_id]
            with self._connect() as connection:
                connection.execute(
                    f"UPDATE runs SET {assignments} WHERE run_id = ?",  # noqa: S608
                    values,
                )

    def _reconcile_run_index(self) -> None:
        records: list[RunRecord] = []
        for path in sorted(self.root.iterdir()):
            if not path.is_dir() or path.is_symlink() or not _RUN_ID.fullmatch(path.name):
                continue
            try:
                payload = json.loads((path / "run.json").read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise IntegrityError(f"Could not reconcile run record: {path.name}") from exc
            records.append(_run_from_payload(payload, path))
        with self._connect() as connection:
            indexed = {
                row["run_id"]
                for row in connection.execute("SELECT run_id FROM runs").fetchall()
            }
            present = {record.run_id for record in records}
            for record in records:
                connection.execute(
                    """
                    INSERT INTO runs (
                        run_id, command, args_json, evidence_class, status, attempt,
                        created_utc, started_utc, completed_utc, returncode,
                        duration_seconds, run_path
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(run_id) DO UPDATE SET
                        command=excluded.command,
                        args_json=excluded.args_json,
                        evidence_class=excluded.evidence_class,
                        status=excluded.status,
                        attempt=excluded.attempt,
                        created_utc=excluded.created_utc,
                        started_utc=excluded.started_utc,
                        completed_utc=excluded.completed_utc,
                        returncode=excluded.returncode,
                        duration_seconds=excluded.duration_seconds,
                        run_path=excluded.run_path
                    """,
                    (
                        record.run_id,
                        record.command,
                        json.dumps(list(record.args), separators=(",", ":")),
                        record.evidence_class,
                        record.status,
                        record.attempt,
                        record.created_utc,
                        record.started_utc,
                        record.completed_utc,
                        record.returncode,
                        record.duration_seconds,
                        str(record.path),
                    ),
                )
            for run_id in indexed - present:
                connection.execute("DELETE FROM runs WHERE run_id = ?", (run_id,))

    def _update_job(self, job_id: str, **changes: Any) -> None:
        self.get_job(job_id)
        allowed = {
            "status",
            "run_id",
            "returncode",
            "last_error",
            "lease_owner",
            "lease_expires_utc",
        }
        if not changes or set(changes) - allowed:
            raise ValueError("Invalid job update")
        if "status" in changes and changes["status"] not in _JOB_STATES:
            raise ValueError(f"Invalid job status: {changes['status']}")
        changes["updated_utc"] = _utc_now()
        assignments = ", ".join(f"{key} = ?" for key in changes)
        values = [*changes.values(), job_id]
        with self._connect() as connection:
            connection.execute(
                f"UPDATE jobs SET {assignments} WHERE job_id = ?",  # noqa: S608
                values,
            )

    def _run_path(self, run_id: str) -> Path:
        _validate_id(run_id, "run")
        path = self.root / run_id
        if not path.is_dir() or path.is_symlink():
            raise KeyError(f"Unknown run: {run_id}")
        return path


def _run_from_payload(payload: object, path: Path) -> RunRecord:
    if not isinstance(payload, dict):
        raise IntegrityError("Run record must be a JSON object")
    try:
        record = RunRecord(
            run_id=payload["run_id"],
            command=payload["command"],
            args=tuple(payload["args"]),
            evidence_class=payload["evidence_class"],
            status=payload["status"],
            attempt=payload["attempt"],
            created_utc=payload["created_utc"],
            started_utc=payload["started_utc"],
            completed_utc=payload["completed_utc"],
            returncode=payload["returncode"],
            duration_seconds=payload["duration_seconds"],
            path=path,
            environment_sha256=payload["environment_sha256"],
            git_commit=payload["git_commit"],
            git_dirty=payload["git_dirty"],
            inputs=dict(payload["inputs"]),
            seeds=dict(payload["seeds"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise IntegrityError(f"Invalid run record: {path}") from exc
    if record.status not in _RUN_STATES:
        raise IntegrityError(f"Invalid run status: {record.status}")
    if record.run_id != path.name or not _RUN_ID.fullmatch(record.run_id):
        raise IntegrityError(f"Run ID does not match its directory: {path}")
    if not isinstance(record.command, str) or not record.command.strip():
        raise IntegrityError(f"Invalid run command: {path}")
    if not all(isinstance(arg, str) for arg in record.args):
        raise IntegrityError(f"Invalid run arguments: {path}")
    return record


def _job_from_row(row: sqlite3.Row) -> JobRecord:
    return JobRecord(
        job_id=row["job_id"],
        command=row["command"],
        args=tuple(json.loads(row["args_json"])),
        timeout_seconds=row["timeout_seconds"],
        evidence_class=row["evidence_class"],
        status=row["status"],
        attempts=row["attempts"],
        max_attempts=row["max_attempts"],
        created_utc=row["created_utc"],
        updated_utc=row["updated_utc"],
        lease_owner=row["lease_owner"],
        lease_expires_utc=row["lease_expires_utc"],
        run_id=row["run_id"],
        returncode=row["returncode"],
        last_error=row["last_error"],
    )


def _validate_id(value: str, label: str) -> None:
    if not isinstance(value, str) or not _RUN_ID.fullmatch(value):
        raise ValueError(f"Invalid {label} ID")


def _validate_args(args: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    if not all(isinstance(arg, str) for arg in args):
        raise TypeError("args must contain only strings")
    return tuple(args)


def _validate_command(command: str) -> str:
    if not isinstance(command, str) or not command.strip():
        raise ValueError("command must be non-empty text")
    return command


def _validate_evidence(value: str) -> str:
    try:
        return EvidenceClass(value).value
    except ValueError:
        choices = ", ".join(item.value for item in EvidenceClass)
        raise ValueError(f"evidence_class must be one of: {choices}") from None


def _validate_inputs(values: Mapping[str, str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for name, digest in values.items():
        if not name.strip():
            raise ValueError("input names must not be empty")
        normalized = digest.lower()
        if len(normalized) != 64 or any(c not in "0123456789abcdef" for c in normalized):
            raise ValueError(f"input hash must be SHA-256: {name}")
        result[name] = normalized
    return dict(sorted(result.items()))


def _validate_seeds(values: Mapping[str, int]) -> dict[str, int]:
    result: dict[str, int] = {}
    for name, seed in values.items():
        if not name.strip() or isinstance(seed, bool) or not isinstance(seed, int):
            raise ValueError("seeds must map non-empty names to integers")
        result[name] = seed
    return dict(sorted(result.items()))


def _new_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return f"{timestamp}-{uuid.uuid4().hex[:8]}"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _environment_sha256() -> str:
    distributions = sorted(
        (
            distribution.metadata.get("Name", distribution.name).lower(),
            distribution.version,
        )
        for distribution in importlib.metadata.distributions()
    )
    payload = {
        "implementation": sys.implementation.name,
        "python": platform.python_version(),
        "distributions": distributions,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _git_state() -> tuple[str | None, bool | None]:
    root = project_root()
    if root is None:
        return None, None
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
                timeout=10,
            ).stdout
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise StorageError("Could not capture source-control provenance") from exc
    return commit, dirty


def _write_json_atomic(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        descriptor, name = tempfile.mkstemp(
            prefix=f".{path.name}-",
            suffix=".part",
            dir=path.parent,
        )
        temporary = Path(name)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as output:
            json.dump(value, output, indent=2, sort_keys=True)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
        temporary = None
        _fsync_directory(path.parent)
    except (OSError, TypeError, ValueError) as exc:
        raise StorageError(f"Could not write run metadata: {path}") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _write_config_toml(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        f'run_id = {json.dumps(payload["run_id"])}',
        f'command = {json.dumps(payload["command"])}',
        f'evidence_class = {json.dumps(payload["evidence_class"])}',
        f'created_utc = {json.dumps(payload["created_utc"])}',
        f'environment_sha256 = {json.dumps(payload["environment_sha256"])}',
        f"args = {json.dumps(payload['args'])}",
        "",
        "[inputs]",
    ]
    lines.extend(
        f"{json.dumps(key)} = {json.dumps(value)}"
        for key, value in payload["inputs"].items()
    )
    lines.extend(["", "[seeds]"])
    lines.extend(f"{json.dumps(key)} = {value}" for key, value in payload["seeds"].items())
    _write_text_atomic(path, "\n".join(lines) + "\n")


def _write_text_atomic(path: Path, value: str) -> None:
    temporary: Path | None = None
    try:
        descriptor, name = tempfile.mkstemp(
            prefix=f".{path.name}-",
            suffix=".part",
            dir=path.parent,
        )
        temporary = Path(name)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as output:
            output.write(value)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
        temporary = None
        _fsync_directory(path.parent)
    except OSError as exc:
        raise StorageError(f"Could not write run configuration: {path}") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _remove_run_files(path: Path) -> None:
    if not path.exists():
        return
    for child in path.iterdir():
        child.unlink(missing_ok=True)
    path.rmdir()


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
            mode = connection.execute("PRAGMA journal_mode").fetchone()[0]
            if mode.lower() != "wal":
                connection.execute("PRAGMA journal_mode = WAL")
            return
        except sqlite3.OperationalError as exc:
            if "locked" not in str(exc).lower() or attempt == 99:
                raise
            time.sleep(min(0.01 * (attempt + 1), 0.1))
