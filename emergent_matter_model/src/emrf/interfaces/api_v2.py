"""Generated-contract FastAPI application for EMRF REST API v2."""

from __future__ import annotations

import logging
import os
import secrets
import subprocess
from pathlib import Path
from typing import Annotated, Any, cast

from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.exceptions import HTTPException as StarletteHTTPException

from emrf import __version__
from emrf.sdk import (
    EMRFClient,
    InvalidRequestError,
    OperationUnavailableError,
    ResourceNotFoundError,
)
from emrf.sdk import RunRequest as SDKRunRequest
from emrf.sdk import SimulationRequest as SDKSimulationRequest

from .api_v2_models import (
    ArtifactInfo,
    ArtifactListResponse,
    BackupRequest,
    CommandInfo,
    CommandListResponse,
    DatasetFetchRequest,
    DatasetListResponse,
    DatasetWriteRequest,
    EnvironmentReport,
    ErrorResponse,
    GarbageCollectRequest,
    HealthResponse,
    JobInfo,
    JobListResponse,
    JobSubmitRequest,
    OffsiteBackupRequest,
    OperationResponse,
    PathRequest,
    PredictionCommitment,
    PredictionCommitRequest,
    PredictionVerification,
    PredictionVerifyRequest,
    RestoreDrillRequest,
    RunInfo,
    RunListResponse,
    RunRequest,
    RunResult,
    SimulationRequest,
    SimulationResult,
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


def _error_responses(*status_codes: int) -> dict[int, dict[str, object]]:
    return {status_code: {"model": ErrorResponse} for status_code in status_codes}


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
    return cast(EMRFClient, request.app.state.sdk)


def _verification(report: Any) -> VerificationReport:
    return VerificationReport(
        evidence_class=report.evidence_class,
        all_passed=report.all_passed,
        checks=[dict(check) for check in report.checks],
        metadata=dict(report.metadata),
    )


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

    @application.exception_handler(OperationUnavailableError)
    def unavailable_handler(
        _: Request,
        exc: OperationUnavailableError,
    ) -> JSONResponse:
        response = exc.as_response()
        return _error_response(
            503,
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
        "/api/v2/doctor",
        response_model=EnvironmentReport,
        tags=["service"],
    )
    def doctor(request: Request) -> EnvironmentReport:
        return EnvironmentReport(**_sdk(request).environment_report().to_dict())

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
    def list_artifacts(run_id: str, request: Request) -> ArtifactListResponse:
        result = _sdk(request).list_artifacts(run_id)
        return ArtifactListResponse(
            artifacts=[ArtifactInfo(**artifact.to_dict()) for artifact in result.artifacts]
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
    def download_artifact(
        run_id: str,
        relative_path: str,
        request: Request,
    ) -> FileResponse:
        artifact = _sdk(request).get_artifact(run_id, relative_path)
        return FileResponse(
            artifact.file_path,
            media_type=artifact.info.media_type,
            filename=Path(artifact.info.path).name,
        )

    @application.get(
        "/api/v2/datasets",
        response_model=DatasetListResponse,
        responses=_error_responses(400, 422, 503),
        tags=["data"],
    )
    def list_datasets(
        request: Request,
        verify: Annotated[bool, Query()] = False,
    ) -> DatasetListResponse:
        result = _sdk(request).list_datasets(verify=verify)
        return DatasetListResponse(
            datasets=[dataset.to_dict() for dataset in result.datasets]
        )

    @application.get(
        "/api/v2/datasets/{dataset_id}",
        response_model=OperationResponse,
        responses=_error_responses(400, 404, 422, 503),
        tags=["data"],
    )
    def get_dataset(
        dataset_id: str,
        request: Request,
        verify: Annotated[bool, Query()] = False,
    ) -> OperationResponse:
        return OperationResponse(
            root=_sdk(request).get_dataset(dataset_id, verify=verify).to_dict()
        )

    @application.post(
        "/api/v2/datasets/{dataset_id}/import",
        response_model=OperationResponse,
        status_code=201,
        responses=_error_responses(400, 401, 403, 404, 422, 503),
        tags=["data"],
        dependencies=[Depends(_require_execution_token)],
    )
    def import_dataset(
        dataset_id: str,
        payload: DatasetWriteRequest,
        request: Request,
    ) -> OperationResponse:
        result = _sdk(request).import_dataset(
            dataset_id,
            logical_name=payload.logical_name,
            source=payload.source,
        )
        return OperationResponse(root=result.to_dict())

    @application.post(
        "/api/v2/datasets/{dataset_id}/fetch",
        response_model=OperationResponse,
        status_code=201,
        responses=_error_responses(400, 401, 403, 404, 422, 503),
        tags=["data"],
        dependencies=[Depends(_require_execution_token)],
    )
    def fetch_dataset(
        dataset_id: str,
        payload: DatasetFetchRequest,
        request: Request,
    ) -> OperationResponse:
        result = _sdk(request).fetch_dataset(
            dataset_id,
            logical_name=payload.logical_name,
            retries=payload.retries,
            timeout=payload.timeout,
        )
        return OperationResponse(root=result.to_dict())

    @application.post(
        "/api/v2/datasets/verify",
        response_model=OperationResponse,
        responses=_error_responses(400, 503),
        tags=["data"],
    )
    def verify_datasets(request: Request) -> OperationResponse:
        return OperationResponse(root=_sdk(request).verify_datasets().to_dict())

    @application.post(
        "/api/v2/data/backups",
        response_model=OperationResponse,
        status_code=201,
        responses=_error_responses(400, 401, 403, 422, 503),
        tags=["data"],
        dependencies=[Depends(_require_execution_token)],
    )
    def create_backup(
        payload: BackupRequest,
        request: Request,
    ) -> OperationResponse:
        return OperationResponse(
            root=_sdk(request).create_data_backup(payload.destination).to_dict()
        )

    @application.post(
        "/api/v2/data/backups/offsite",
        response_model=OperationResponse,
        status_code=201,
        responses=_error_responses(400, 401, 403, 422, 503),
        tags=["data"],
        dependencies=[Depends(_require_execution_token)],
    )
    def create_offsite_backup(
        payload: OffsiteBackupRequest,
        request: Request,
    ) -> OperationResponse:
        return OperationResponse(
            root=_sdk(request)
            .create_offsite_data_backup(payload.destination_root)
            .to_dict()
        )

    @application.post(
        "/api/v2/data/backups/verify",
        response_model=OperationResponse,
        responses=_error_responses(400, 401, 403, 404, 422, 503),
        tags=["data"],
        dependencies=[Depends(_require_execution_token)],
    )
    def verify_backup(
        payload: PathRequest,
        request: Request,
    ) -> OperationResponse:
        return OperationResponse(
            root=_sdk(request).verify_data_backup(payload.source).to_dict()
        )

    @application.post(
        "/api/v2/data/restores",
        response_model=OperationResponse,
        responses=_error_responses(400, 401, 403, 404, 422, 503),
        tags=["data"],
        dependencies=[Depends(_require_execution_token)],
    )
    def restore_backup(
        payload: PathRequest,
        request: Request,
    ) -> OperationResponse:
        return OperationResponse(
            root=_sdk(request).restore_data_backup(payload.source).to_dict()
        )

    @application.post(
        "/api/v2/data/restore-drills",
        response_model=OperationResponse,
        responses=_error_responses(400, 401, 403, 404, 422, 503),
        tags=["data"],
        dependencies=[Depends(_require_execution_token)],
    )
    def restore_drill(
        payload: RestoreDrillRequest,
        request: Request,
    ) -> OperationResponse:
        return OperationResponse(
            root=_sdk(request)
            .run_data_restore_drill(
                receipt=payload.receipt,
                workspace=payload.workspace,
            )
            .to_dict()
        )

    @application.post(
        "/api/v2/data/gc",
        response_model=OperationResponse,
        responses=_error_responses(400, 401, 403, 422, 503),
        tags=["data"],
        dependencies=[Depends(_require_execution_token)],
    )
    def garbage_collect(
        payload: GarbageCollectRequest,
        request: Request,
    ) -> OperationResponse:
        return OperationResponse(
            root=_sdk(request).garbage_collect_data(execute=payload.execute).to_dict()
        )

    @application.post(
        "/api/v2/predictions/commit",
        response_model=PredictionCommitment,
        status_code=201,
        responses=_error_responses(400, 401, 403, 422),
        tags=["predictions"],
        dependencies=[Depends(_require_execution_token)],
    )
    def commit_prediction(
        payload: PredictionCommitRequest,
        request: Request,
    ) -> PredictionCommitment:
        result = _sdk(request).commit_json_prediction(
            payload.prediction,
            label=payload.label,
        )
        return PredictionCommitment(**result.to_dict())

    @application.get(
        "/api/v2/predictions/{commitment_id}",
        response_model=PredictionCommitment,
        responses=_error_responses(400, 404, 422),
        tags=["predictions"],
    )
    def get_prediction(
        commitment_id: str,
        request: Request,
    ) -> PredictionCommitment:
        return PredictionCommitment(
            **_sdk(request).get_prediction(commitment_id).to_dict()
        )

    @application.post(
        "/api/v2/predictions/{commitment_id}/verify",
        response_model=PredictionVerification,
        responses={
            **_error_responses(400, 404, 422),
            409: {"model": PredictionVerification},
        },
        tags=["predictions"],
    )
    def verify_prediction(
        commitment_id: str,
        payload: PredictionVerifyRequest,
        request: Request,
    ) -> PredictionVerification | JSONResponse:
        result = _sdk(request).verify_json_prediction(
            commitment_id,
            payload.prediction,
        )
        if not result.matches:
            return JSONResponse(status_code=409, content=result.to_dict())
        return PredictionVerification(**result.to_dict())

    @application.post(
        "/api/v2/simulations",
        response_model=SimulationResult,
        responses=_error_responses(400, 401, 403, 422),
        tags=["simulation"],
        dependencies=[Depends(_require_execution_token)],
    )
    def simulate(
        payload: SimulationRequest,
        request: Request,
    ) -> SimulationResult:
        result = _sdk(request).simulate(
            SDKSimulationRequest(
                n=payload.n,
                weights=tuple(payload.weights),
                grid=tuple(tuple(axis) for axis in payload.X_grid),
                k=payload.k,
                alpha=payload.alpha,
                C0=payload.C0,
            )
        )
        return SimulationResult(**result.to_dict())

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
