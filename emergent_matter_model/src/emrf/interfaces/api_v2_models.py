"""Pydantic contracts for the generated EMRF REST API v2 schema."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, RootModel


class APIModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ErrorResponse(APIModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class HealthResponse(APIModel):
    status: str
    service: str
    version: str
    api_version: str


class EnvironmentReport(APIModel):
    emrf_version: str
    api_version: str
    python: str
    python_ok: bool
    platform: str
    core_dependencies: dict[str, str | None]
    optional_dependencies: dict[str, str | None]
    missing_core: list[str]
    registered_commands: int
    missing_scripts: list[str]
    source_only_unavailable: list[str]
    app_root: str
    data_root: str
    manifest_present: bool
    offsite_backup_destination_configured: bool
    healthy: bool


class PerformanceRequest(APIModel):
    profile: str = Field(default="standard", pattern="^(test|standard)$")
    repeats: int | None = Field(default=None, ge=1, le=10)
    workloads: list[str] | None = None


class CommandInfo(APIModel):
    name: str
    script: str
    category: str
    summary: str
    network: bool
    gui: bool
    module: str | None
    source_only: bool
    exists: bool


class CommandListResponse(APIModel):
    commands: list[CommandInfo]
    execution_enabled: bool


class RunRequest(APIModel):
    args: list[str] = Field(default_factory=list)
    timeout: float | None = Field(default=300.0, gt=0, le=600)
    evidence_class: str = Field(default="software", min_length=1)
    inputs: dict[str, str] = Field(default_factory=dict)
    seeds: dict[str, int] = Field(default_factory=dict)


class RunResult(APIModel):
    command: str
    args: list[str]
    returncode: int
    seconds: float
    run_id: str
    stdout: str | None = None
    stderr: str | None = None


class RunInfo(APIModel):
    run_id: str
    command: str
    args: list[str]
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
    inputs: dict[str, str]
    seeds: dict[str, int]


class RunListResponse(APIModel):
    runs: list[RunInfo]


class JobInfo(APIModel):
    job_id: str
    command: str
    args: list[str]
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


class JobListResponse(APIModel):
    jobs: list[JobInfo]


class JobSubmitRequest(RunRequest):
    command: str = Field(min_length=1)
    max_attempts: int = Field(default=1, ge=1, le=100)


class WorkerRequest(APIModel):
    worker_id: str = Field(min_length=1, max_length=200)
    lease_seconds: float = Field(default=3600, gt=0, le=86400)


class ArtifactInfo(APIModel):
    path: str
    bytes: int = Field(ge=0)
    media_type: str


class ArtifactListResponse(APIModel):
    artifacts: list[ArtifactInfo]


class DatasetListResponse(APIModel):
    datasets: list[dict[str, Any]]


class OperationResponse(RootModel[dict[str, Any]]):
    pass


class KnowledgeQueryResponse(APIModel):
    nodes: list[dict[str, Any]]
    count: int = Field(ge=0)


class KnowledgeValidationError(APIModel):
    path: str
    message: str


class KnowledgeValidationResponse(APIModel):
    valid: bool
    schema_version: str | None
    graph_path: str
    nodes: int = Field(ge=0)
    edges: int = Field(ge=0)
    errors: list[KnowledgeValidationError]


class KnowledgeSourceRequest(APIModel):
    id: str = Field(pattern=r"^source:[a-z0-9][a-z0-9_.-]*$")
    title: str = Field(min_length=1)
    authors: list[str] = Field(min_length=1)
    year: int = Field(ge=1000, le=9999)
    snapshot_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    bibtex: str = Field(min_length=1)
    doi: str | None = Field(default=None, min_length=1)
    arxiv: str | None = Field(default=None, min_length=1)
    ads_bibcode: str | None = Field(default=None, min_length=1)


class KnowledgeRunLinkRequest(APIModel):
    claim_ids: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    dataset_ids: list[str] = Field(default_factory=list)


class DatasetWriteRequest(APIModel):
    logical_name: str | None = None
    source: str | None = None


class DatasetFetchRequest(APIModel):
    logical_name: str | None = None
    retries: int = Field(default=3, ge=0, le=20)
    timeout: float = Field(default=180.0, gt=0, le=3600)


class PathRequest(APIModel):
    source: str = Field(min_length=1)


class BackupRequest(APIModel):
    destination: str = Field(min_length=1)


class OffsiteBackupRequest(APIModel):
    destination_root: str | None = Field(default=None, min_length=1)


class RestoreDrillRequest(APIModel):
    receipt: str | None = Field(default=None, min_length=1)
    workspace: str | None = Field(default=None, min_length=1)


class StateRestoreRequest(APIModel):
    source: str = Field(min_length=1)
    destination: str = Field(min_length=1)


class GarbageCollectRequest(APIModel):
    execute: bool = False


class PredictionCommitRequest(APIModel):
    label: str = Field(min_length=1, max_length=100)
    prediction: Any


class PredictionVerifyRequest(APIModel):
    prediction: Any


class PredictionCommitment(APIModel):
    commitment_id: str
    label: str
    created_utc: str
    sha256: str
    bytes: int
    source_name: str | None
    media_type: str
    evidence_class: str
    content_stored: bool


class PredictionVerification(APIModel):
    commitment_id: str
    matches: bool
    expected_sha256: str
    actual_sha256: str
    bytes: int


class SimulationRequest(APIModel):
    n: int = Field(ge=1)
    weights: list[float]
    X_grid: list[list[float]]
    k: float = 1.0
    alpha: float = 1.0
    C0: float = 1.0


class SimulationResult(APIModel):
    shape: list[int]
    M: Any


class VerificationReport(APIModel):
    evidence_class: str
    all_passed: bool
    checks: list[dict[str, Any]]
    metadata: dict[str, Any] = Field(default_factory=dict)


__all__ = [
    "CommandInfo",
    "CommandListResponse",
    "ArtifactInfo",
    "ArtifactListResponse",
    "ErrorResponse",
    "EnvironmentReport",
    "DatasetFetchRequest",
    "DatasetListResponse",
    "DatasetWriteRequest",
    "BackupRequest",
    "GarbageCollectRequest",
    "HealthResponse",
    "JobInfo",
    "JobListResponse",
    "JobSubmitRequest",
    "OffsiteBackupRequest",
    "OperationResponse",
    "PathRequest",
    "PerformanceRequest",
    "PredictionCommitment",
    "PredictionCommitRequest",
    "PredictionVerification",
    "PredictionVerifyRequest",
    "RestoreDrillRequest",
    "WorkerRequest",
    "RunInfo",
    "RunListResponse",
    "RunRequest",
    "RunResult",
    "SimulationRequest",
    "SimulationResult",
    "StateRestoreRequest",
    "VerificationReport",
]
