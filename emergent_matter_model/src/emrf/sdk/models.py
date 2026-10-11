"""Stable typed values shared by the EMRF SDK, CLI and HTTP interfaces."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ErrorResponse:
    code: str
    message: str
    details: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CommandInfo:
    name: str
    script: str
    category: str
    summary: str
    network: bool
    gui: bool
    module: str | None
    source_only: bool
    exists: bool

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> CommandInfo:
        return cls(
            name=str(value["name"]),
            script=str(value["script"]),
            category=str(value["category"]),
            summary=str(value["summary"]),
            network=bool(value["network"]),
            gui=bool(value["gui"]),
            module=None if value["module"] is None else str(value["module"]),
            source_only=bool(value["source_only"]),
            exists=bool(value["exists"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CommandListResponse:
    commands: tuple[CommandInfo, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"commands": [command.to_dict() for command in self.commands]}


@dataclass(frozen=True)
class RunRequest:
    command: str
    args: tuple[str, ...] = ()
    timeout: float | None = None
    evidence_class: str = "software"
    inputs: Mapping[str, str] = field(default_factory=dict)
    seeds: Mapping[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.command, str) or not self.command:
            raise ValueError("command must be non-empty text")
        if not isinstance(self.args, tuple) or not all(
            isinstance(argument, str) for argument in self.args
        ):
            raise TypeError("args must be a tuple of strings")
        if self.timeout is not None and (
            isinstance(self.timeout, bool)
            or not isinstance(self.timeout, (int, float))
            or not math.isfinite(self.timeout)
            or self.timeout <= 0
        ):
            raise ValueError("timeout must be a finite positive number")
        if not isinstance(self.evidence_class, str) or not self.evidence_class:
            raise ValueError("evidence_class must be non-empty text")


@dataclass(frozen=True)
class RunResult:
    command: str
    args: tuple[str, ...]
    returncode: int
    seconds: float
    run_id: str
    stdout: str | None = None
    stderr: str | None = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> RunResult:
        return cls(
            command=str(value["command"]),
            args=tuple(str(argument) for argument in value["args"]),
            returncode=int(value["returncode"]),
            seconds=float(value["seconds"]),
            run_id=str(value["run_id"]),
            stdout=None if "stdout" not in value else str(value["stdout"]),
            stderr=None if "stderr" not in value else str(value["stderr"]),
        )

    def to_dict(self) -> dict[str, Any]:
        value: dict[str, Any] = {
            "command": self.command,
            "args": list(self.args),
            "returncode": self.returncode,
            "seconds": self.seconds,
            "run_id": self.run_id,
        }
        if self.stdout is not None:
            value["stdout"] = self.stdout
        if self.stderr is not None:
            value["stderr"] = self.stderr
        return value


@dataclass(frozen=True)
class RunInfo:
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
    environment_sha256: str
    git_commit: str | None
    git_dirty: bool | None
    inputs: Mapping[str, str]
    seeds: Mapping[str, int]

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> RunInfo:
        return cls(
            run_id=str(value["run_id"]),
            command=str(value["command"]),
            args=tuple(str(argument) for argument in value["args"]),
            evidence_class=str(value["evidence_class"]),
            status=str(value["status"]),
            attempt=int(value["attempt"]),
            created_utc=str(value["created_utc"]),
            started_utc=(
                None if value["started_utc"] is None else str(value["started_utc"])
            ),
            completed_utc=(
                None
                if value["completed_utc"] is None
                else str(value["completed_utc"])
            ),
            returncode=(
                None if value["returncode"] is None else int(value["returncode"])
            ),
            duration_seconds=(
                None
                if value["duration_seconds"] is None
                else float(value["duration_seconds"])
            ),
            environment_sha256=str(value["environment_sha256"]),
            git_commit=(
                None if value["git_commit"] is None else str(value["git_commit"])
            ),
            git_dirty=(
                None if value["git_dirty"] is None else bool(value["git_dirty"])
            ),
            inputs=dict(value["inputs"]),
            seeds={str(key): int(seed) for key, seed in value["seeds"].items()},
        )

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["args"] = list(self.args)
        return value


@dataclass(frozen=True)
class RunListResponse:
    runs: tuple[RunInfo, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"runs": [run.to_dict() for run in self.runs]}


@dataclass(frozen=True)
class JobInfo:
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

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> JobInfo:
        return cls(
            job_id=str(value["job_id"]),
            command=str(value["command"]),
            args=tuple(str(argument) for argument in value["args"]),
            timeout_seconds=(
                None
                if value["timeout_seconds"] is None
                else float(value["timeout_seconds"])
            ),
            evidence_class=str(value["evidence_class"]),
            status=str(value["status"]),
            attempts=int(value["attempts"]),
            max_attempts=int(value["max_attempts"]),
            created_utc=str(value["created_utc"]),
            updated_utc=str(value["updated_utc"]),
            lease_owner=(
                None if value["lease_owner"] is None else str(value["lease_owner"])
            ),
            lease_expires_utc=(
                None
                if value["lease_expires_utc"] is None
                else str(value["lease_expires_utc"])
            ),
            run_id=None if value["run_id"] is None else str(value["run_id"]),
            returncode=(
                None if value["returncode"] is None else int(value["returncode"])
            ),
            last_error=(
                None if value["last_error"] is None else str(value["last_error"])
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["args"] = list(self.args)
        return value


@dataclass(frozen=True)
class JobListResponse:
    jobs: tuple[JobInfo, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"jobs": [job.to_dict() for job in self.jobs]}


@dataclass(frozen=True)
class DatasetInfo:
    dataset_id: str
    title: str
    status: str
    priority: str
    citation: str | None = None
    licence: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DatasetRecord:
    payload: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return dict(self.payload)


@dataclass(frozen=True)
class DatasetListResponse:
    datasets: tuple[DatasetRecord, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"datasets": [dataset.to_dict() for dataset in self.datasets]}


@dataclass(frozen=True)
class OperationResult:
    payload: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return dict(self.payload)


@dataclass(frozen=True)
class KnowledgeNode:
    payload: Mapping[str, Any]

    @property
    def node_id(self) -> str:
        return str(self.payload["id"])

    def to_dict(self) -> dict[str, Any]:
        return dict(self.payload)


@dataclass(frozen=True)
class KnowledgeQueryResponse:
    nodes: tuple[KnowledgeNode, ...]

    @property
    def count(self) -> int:
        return len(self.nodes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "count": self.count,
        }


@dataclass(frozen=True)
class KnowledgeSourceRequest:
    source_id: str
    title: str
    authors: tuple[str, ...]
    year: int
    snapshot_sha256: str
    bibtex: str
    doi: str | None = None
    arxiv: str | None = None
    ads_bibcode: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.source_id,
            "title": self.title,
            "authors": list(self.authors),
            "year": self.year,
            "snapshot_sha256": self.snapshot_sha256,
            "bibtex": self.bibtex,
            "doi": self.doi,
            "arxiv": self.arxiv,
            "ads_bibcode": self.ads_bibcode,
        }


@dataclass(frozen=True)
class KnowledgeValidationReport:
    valid: bool
    schema_version: str | None
    graph_path: str
    nodes: int
    edges: int
    errors: tuple[Mapping[str, str], ...]

    @classmethod
    def from_mapping(
        cls,
        value: Mapping[str, Any],
    ) -> KnowledgeValidationReport:
        return cls(
            valid=bool(value["valid"]),
            schema_version=(
                None
                if value["schema_version"] is None
                else str(value["schema_version"])
            ),
            graph_path=str(value["graph_path"]),
            nodes=int(value["nodes"]),
            edges=int(value["edges"]),
            errors=tuple(dict(error) for error in value["errors"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "schema_version": self.schema_version,
            "graph_path": self.graph_path,
            "nodes": self.nodes,
            "edges": self.edges,
            "errors": [dict(error) for error in self.errors],
        }


@dataclass(frozen=True)
class EnvironmentReport:
    payload: Mapping[str, Any]

    @property
    def healthy(self) -> bool:
        return bool(self.payload["healthy"])

    def to_dict(self) -> dict[str, Any]:
        return dict(self.payload)


@dataclass(frozen=True)
class SupportReport:
    path: str
    sha256: str
    bytes: int
    healthy: bool
    schema: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> SupportReport:
        return cls(
            path=str(value["path"]),
            sha256=str(value["sha256"]),
            bytes=int(value["bytes"]),
            healthy=bool(value["healthy"]),
            schema=str(value["schema"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SimulationRequest:
    n: int
    weights: tuple[float, ...]
    grid: tuple[tuple[float, ...], ...]
    k: float = 1.0
    alpha: float = 1.0
    C0: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "n": self.n,
            "weights": list(self.weights),
            "X_grid": [list(axis) for axis in self.grid],
            "k": self.k,
            "alpha": self.alpha,
            "C0": self.C0,
        }


@dataclass(frozen=True)
class SimulationResult:
    shape: tuple[int, ...]
    values: Any

    def to_dict(self) -> dict[str, Any]:
        return {"shape": list(self.shape), "M": self.values}


@dataclass(frozen=True)
class ArtifactInfo:
    path: str
    bytes: int
    media_type: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ArtifactListResponse:
    artifacts: tuple[ArtifactInfo, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"artifacts": [artifact.to_dict() for artifact in self.artifacts]}


@dataclass(frozen=True)
class ArtifactContent:
    info: ArtifactInfo
    file_path: Path


@dataclass(frozen=True)
class VerificationReport:
    evidence_class: str
    all_passed: bool
    checks: tuple[Mapping[str, Any], ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> VerificationReport:
        return cls(
            evidence_class=str(value["evidence_class"]),
            all_passed=bool(value["all_passed"]),
            checks=tuple(dict(check) for check in value["checks"]),
            metadata={
                key: item
                for key, item in value.items()
                if key not in {"evidence_class", "all_passed", "checks"}
            },
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_class": self.evidence_class,
            "all_passed": self.all_passed,
            **dict(self.metadata),
            "checks": [dict(check) for check in self.checks],
        }


@dataclass(frozen=True)
class PredictionCommitment:
    commitment_id: str
    label: str
    created_utc: str
    sha256: str
    bytes: int
    source_name: str | None
    media_type: str
    evidence_class: str
    content_stored: bool

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> PredictionCommitment:
        return cls(
            commitment_id=str(value["commitment_id"]),
            label=str(value["label"]),
            created_utc=str(value["created_utc"]),
            sha256=str(value["sha256"]),
            bytes=int(value["bytes"]),
            source_name=(
                None if value["source_name"] is None else str(value["source_name"])
            ),
            media_type=str(value["media_type"]),
            evidence_class=str(value["evidence_class"]),
            content_stored=bool(value["content_stored"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PredictionVerification:
    commitment_id: str
    matches: bool
    expected_sha256: str
    actual_sha256: str
    bytes: int

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> PredictionVerification:
        return cls(
            commitment_id=str(value["commitment_id"]),
            matches=bool(value["matches"]),
            expected_sha256=str(value["expected_sha256"]),
            actual_sha256=str(value["actual_sha256"]),
            bytes=int(value["bytes"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


__all__ = [
    "ArtifactContent",
    "ArtifactInfo",
    "ArtifactListResponse",
    "CommandInfo",
    "CommandListResponse",
    "DatasetInfo",
    "DatasetListResponse",
    "DatasetRecord",
    "EnvironmentReport",
    "ErrorResponse",
    "OperationResult",
    "PredictionCommitment",
    "PredictionVerification",
    "RunInfo",
    "RunListResponse",
    "RunRequest",
    "RunResult",
    "SimulationRequest",
    "SimulationResult",
    "SupportReport",
    "JobInfo",
    "JobListResponse",
    "KnowledgeNode",
    "KnowledgeQueryResponse",
    "KnowledgeSourceRequest",
    "KnowledgeValidationReport",
    "VerificationReport",
]
