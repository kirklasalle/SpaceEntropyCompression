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


class VerificationReport(APIModel):
    evidence_class: str
    all_passed: bool
    checks: list[dict[str, Any]]
    metadata: dict[str, Any] = Field(default_factory=dict)


__all__ = [
    "CommandInfo",
    "CommandListResponse",
    "ErrorResponse",
    "HealthResponse",
    "RunInfo",
    "RunListResponse",
    "RunRequest",
    "RunResult",
    "VerificationReport",
]
