"""Generated-contract FastAPI application for EMRF REST API v2."""

from __future__ import annotations

import logging
import mimetypes
import os
import secrets
import subprocess
from pathlib import Path, PurePosixPath
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.exceptions import HTTPException as StarletteHTTPException

from emrf import __version__
from emrf.sdk import (
    EMRFClient,
    InvalidRequestError,
    ResourceNotFoundError,
)
from emrf.sdk import RunRequest as SDKRunRequest

from .api_v2_models import (
    ArtifactInfo,
    ArtifactListResponse,
    CommandInfo,
    CommandListResponse,
    ErrorResponse,
    HealthResponse,
    JobInfo,
    JobListResponse,
    JobSubmitRequest,
    RunInfo,
    RunListResponse,
    RunRequest,
    RunResult,
    VerificationReport,
    WorkerRequest,
)

API_V2_TOKEN_ENV = "EMRF_API_V2_TOKEN"
API_V2_VERSION = "v2"

logger = logging.getLogger(__name__)
bearer = HTTPBearer(auto_error=False)


class APIError(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        *,
        details: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = ErrorResponse(
            code=code,
            message=message,
            details=details or {},
        )
        self.headers = headers


def _error_response(
    status_code: int,
    code: str,
    message: str,
    *,
    details: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            code=code,
            message=message,
            details=details or {},
        ).model_dump(mode="json"),
        headers=headers,
    )


def _require_execution_token(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer),
    ],
) -> None:
    configured = os.environ.get(API_V2_TOKEN_ENV)
    if not configured:
        raise APIError(
            403,
            "execution_disabled",
            f"Command execution is disabled. Set {API_V2_TOKEN_ENV} on a trusted host.",
        )
    if (
        credentials is None
        or credentials.scheme.lower() != "bearer"
        or not secrets.compare_digest(credentials.credentials, configured)
    ):
        raise APIError(
            401,
            "invalid_token",
            "A valid bearer token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def _sdk(request: Request) -> EMRFClient:
    return request.app.state.sdk


def _verification(report: Any) -> VerificationReport:
    return VerificationReport(
        evidence_class=report.evidence_class,
        all_passed=report.all_passed,
        checks=[dict(check) for check in report.checks],
        metadata=dict(report.metadata),
    )


def _artifact_path(run_id: str, relative_path: str) -> tuple[Path, str]:
    from emrf_run_access import run_store

    try:
        record = run_store().get(run_id)
    except KeyError as exc:
        raise APIError(404, "run_not_found", "Run was not found.") from exc
    normalized = relative_path.replace("\\", "/")
    path = PurePosixPath(normalized)
    if (
        not normalized
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise APIError(400, "invalid_artifact_path", "Artifact path is invalid.")
    raw_candidate = record.path / Path(*path.parts)
    if raw_candidate.is_symlink():
        raise APIError(404, "artifact_not_found", "Artifact was not found.")
    candidate = raw_candidate.resolve()
    root = record.path.resolve()
    if root not in candidate.parents or not candidate.is_file():
        raise APIError(404, "artifact_not_found", "Artifact was not found.")
    return candidate, "/".join(path.parts)


def _artifact_rows(run_id: str) -> list[dict[str, Any]]:
    from emrf_run_access import run_store

    try:
        record = run_store().get(run_id)
    except KeyError as exc:
        raise APIError(404, "run_not_found", "Run was not found.") from exc
    root = record.path.resolve()
    rows: list[dict[str, Any]] = []
    for path in sorted(record.path.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        resolved = path.resolve()
        if root not in resolved.parents:
            continue
        relative = path.relative_to(record.path).as_posix()
        rows.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "media_type": mimetypes.guess_type(path.name)[0]
                or "application/octet-stream",
            }
        )
    return rows


def create_app(client: EMRFClient | None = None) -> FastAPI:
    application = FastAPI(
        title="Emergent Matter Research Framework API",
        summary="Typed scientific software, data, run, and verification interfaces.",
        version=__version__,
        openapi_url="/api/v2/openapi.json",
        docs_url="/api/v2/docs",
        redoc_url="/api/v2/redoc",
    )
    application.state.sdk = client or EMRFClient()

    @application.exception_handler(APIError)
    def api_error_handler(_: Request, exc: APIError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.response.model_dump(mode="json"),
            headers=exc.headers,
        )

    @application.exception_handler(ResourceNotFoundError)
    def not_found_handler(_: Request, exc: ResourceNotFoundError) -> JSONResponse:
        response = exc.as_response()
        return _error_response(
            404,
            response.code,
            response.message,
            details=dict(response.details),
        )

    @application.exception_handler(InvalidRequestError)
    def invalid_request_handler(
        _: Request,
        exc: InvalidRequestError,
    ) -> JSONResponse:
        response = exc.as_response()
        return _error_response(
            400,
            response.code,
            response.message,
            details=dict(response.details),
        )

    @application.exception_handler(RequestValidationError)
    def validation_handler(
        _: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return _error_response(
            422,
            "validation_error",
            "Request validation failed.",
            details={"errors": exc.errors()},
        )

    @application.exception_handler(subprocess.TimeoutExpired)
    def timeout_handler(
        _: Request,
        exc: subprocess.TimeoutExpired,
    ) -> JSONResponse:
        return _error_response(
            504,
            "command_timeout",
            "Command execution exceeded its timeout.",
            details={"run_id": getattr(exc, "run_id", None)},
        )

    @application.exception_handler(StarletteHTTPException)
    def http_error_handler(
        _: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        return _error_response(
            exc.status_code,
            "http_error",
            str(exc.detail),
        )

    @application.exception_handler(Exception)
    def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "Unhandled API v2 error for %s %s",
            request.method,
            request.url.path,
            exc_info=exc,
        )
        return _error_response(500, "internal_error", "Internal server error.")

    @application.get(
        "/api/v2/health",
        response_model=HealthResponse,
        tags=["service"],
    )
    def health() -> HealthResponse:
        return HealthResponse(
            status="healthy",
            service="emergent-matter-model",
            version=__version__,
            api_version=API_V2_VERSION,
        )

    @application.get(
        "/api/v2/commands",
        response_model=CommandListResponse,
        responses={400: {"model": ErrorResponse}},
        tags=["commands"],
    )
    def list_commands(
        request: Request,
        category: Annotated[str | None, Query()] = None,
    ) -> CommandListResponse:
        result = _sdk(request).list_commands(category)
        return CommandListResponse(
            commands=[
                CommandInfo.model_validate(command.to_dict())
                for command in result.commands
            ],
            execution_enabled=bool(os.environ.get(API_V2_TOKEN_ENV)),
        )

    @application.get(
        "/api/v2/commands/{name}",
        response_model=CommandInfo,
        responses={404: {"model": ErrorResponse}},
        tags=["commands"],
    )
    def get_command(name: str, request: Request) -> CommandInfo:
        return CommandInfo(**_sdk(request).get_command(name).to_dict())

    @application.post(
        "/api/v2/commands/{name}/runs",
        response_model=RunResult,
        responses={
            400: {"model": ErrorResponse},
            401: {"model": ErrorResponse},
            403: {"model": ErrorResponse},
            404: {"model": ErrorResponse},
            422: {"model": ErrorResponse},
            504: {"model": ErrorResponse},
        },
        tags=["commands", "runs"],
        dependencies=[Depends(_require_execution_token)],
    )
    def run_command(name: str, payload: RunRequest, request: Request) -> RunResult:
        client = _sdk(request)
        command = client.get_command(name)
        if command.gui or command.category == "service":
            raise APIError(
                400,
                "invalid_request",
                f"{name} is interactive or a service and cannot run via API.",
            )
        result = client.run(
            SDKRunRequest(
                command=name,
                args=tuple(payload.args),
                timeout=payload.timeout,
                evidence_class=payload.evidence_class,
                inputs=payload.inputs,
                seeds=payload.seeds,
            ),
            capture=True,
        )
        return RunResult(**result.to_dict())

    @application.get(
        "/api/v2/runs",
        response_model=RunListResponse,
        responses={422: {"model": ErrorResponse}},
        tags=["runs"],
    )
    def list_runs(
        request: Request,
        limit: Annotated[int, Query(ge=1, le=1000)] = 50,
    ) -> RunListResponse:
        result = _sdk(request).list_runs(limit=limit)
        return RunListResponse(
            runs=[RunInfo.model_validate(run.to_dict()) for run in result.runs]
        )

    @application.get(
        "/api/v2/runs/{run_id}",
        response_model=RunInfo,
        responses={404: {"model": ErrorResponse}},
        tags=["runs"],
    )
    def get_run(run_id: str, request: Request) -> RunInfo:
        return RunInfo(**_sdk(request).get_run(run_id).to_dict())

    @application.post(
        "/api/v2/jobs",
        response_model=JobInfo,
        status_code=202,
        responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}},
        tags=["jobs"],
        dependencies=[Depends(_require_execution_token)],
    )
    def submit_job(payload: JobSubmitRequest, request: Request) -> JobInfo:
        return JobInfo(
            **_sdk(request)
            .submit_job(
                SDKRunRequest(
                    command=payload.command,
                    args=tuple(payload.args),
                    timeout=payload.timeout,
                    evidence_class=payload.evidence_class,
                    inputs=payload.inputs,
                    seeds=payload.seeds,
                ),
                max_attempts=payload.max_attempts,
            )
            .to_dict()
        )

    @application.get(
        "/api/v2/jobs",
        response_model=JobListResponse,
        responses={422: {"model": ErrorResponse}},
        tags=["jobs"],
    )
    def list_jobs(
        request: Request,
        limit: Annotated[int, Query(ge=1, le=1000)] = 50,
    ) -> JobListResponse:
        result = _sdk(request).list_jobs(limit=limit)
        return JobListResponse(jobs=[JobInfo(**job.to_dict()) for job in result.jobs])

    @application.get(
        "/api/v2/jobs/{job_id}",
        response_model=JobInfo,
        responses={404: {"model": ErrorResponse}},
        tags=["jobs"],
    )
    def get_job(job_id: str, request: Request) -> JobInfo:
        return JobInfo(**_sdk(request).get_job(job_id).to_dict())

    @application.post(
        "/api/v2/jobs/{job_id}/cancel",
        response_model=JobInfo,
        responses={
            400: {"model": ErrorResponse},
            401: {"model": ErrorResponse},
            404: {"model": ErrorResponse},
        },
        tags=["jobs"],
        dependencies=[Depends(_require_execution_token)],
    )
    def cancel_job(job_id: str, request: Request) -> JobInfo:
        return JobInfo(**_sdk(request).cancel_job(job_id).to_dict())

    @application.post(
        "/api/v2/jobs/worker/run-next",
        response_model=JobInfo | None,
        responses={
            400: {"model": ErrorResponse},
            401: {"model": ErrorResponse},
        },
        tags=["jobs"],
        dependencies=[Depends(_require_execution_token)],
    )
    def run_next_job(payload: WorkerRequest, request: Request) -> JobInfo | None:
        result = _sdk(request).run_next_job(
            payload.worker_id,
            lease_seconds=payload.lease_seconds,
        )
        return None if result is None else JobInfo(**result.to_dict())

    @application.get(
        "/api/v2/runs/{run_id}/artifacts",
        response_model=ArtifactListResponse,
        responses={404: {"model": ErrorResponse}},
        tags=["artifacts"],
        dependencies=[Depends(_require_execution_token)],
    )
    def list_artifacts(run_id: str) -> ArtifactListResponse:
        return ArtifactListResponse(
            artifacts=[ArtifactInfo(**row) for row in _artifact_rows(run_id)]
        )

    @application.get(
        "/api/v2/runs/{run_id}/artifacts/{relative_path:path}",
        response_class=FileResponse,
        responses={
            400: {"model": ErrorResponse},
            401: {"model": ErrorResponse},
            404: {"model": ErrorResponse},
        },
        tags=["artifacts"],
        dependencies=[Depends(_require_execution_token)],
    )
    def download_artifact(run_id: str, relative_path: str) -> FileResponse:
        path, normalized = _artifact_path(run_id, relative_path)
        media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        return FileResponse(
            path,
            media_type=media_type,
            filename=Path(normalized).name,
        )

    @application.get(
        "/api/v2/verification/physics",
        response_model=VerificationReport,
        tags=["verification"],
    )
    def verify_physics(request: Request) -> VerificationReport:
        return _verification(_sdk(request).verify_physics())

    @application.get(
        "/api/v2/verification/inference",
        response_model=VerificationReport,
        tags=["verification"],
    )
    def verify_inference(request: Request) -> VerificationReport:
        return _verification(_sdk(request).verify_inference())

    @application.get(
        "/api/v2/verification/engines",
        response_model=VerificationReport,
        tags=["verification"],
    )
    def verify_engines(request: Request) -> VerificationReport:
        return _verification(_sdk(request).verify_engines())

    return application


app = create_app()

__all__ = ["API_V2_TOKEN_ENV", "API_V2_VERSION", "app", "create_app"]
