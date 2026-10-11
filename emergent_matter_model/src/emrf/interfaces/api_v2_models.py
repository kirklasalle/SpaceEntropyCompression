"""Pydantic contracts for the generated EMRF REST API v2 schema."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


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
    "HealthResponse",
    "JobInfo",
    "JobListResponse",
    "JobSubmitRequest",
    "WorkerRequest",
    "RunInfo",
    "RunListResponse",
    "RunRequest",
    "RunResult",
    "VerificationReport",
]
