"""Generated-contract FastAPI application for EMRF REST API v2."""

from __future__ import annotations

import logging
import os
import secrets
import subprocess
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
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
    CommandInfo,
    CommandListResponse,
    ErrorResponse,
    HealthResponse,
    RunInfo,
    RunListResponse,
    RunRequest,
    RunResult,
    VerificationReport,
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
