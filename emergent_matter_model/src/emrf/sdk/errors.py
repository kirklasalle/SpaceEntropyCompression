"""Public SDK exception hierarchy."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .models import ErrorResponse


class SDKError(Exception):
    """Base class for errors raised by the stable Python SDK."""

    code = "sdk_error"

    def __init__(
        self,
        message: str,
        *,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = dict(details or {})

    def __str__(self) -> str:
        return self.message

    def as_response(self) -> ErrorResponse:
        return ErrorResponse(self.code, self.message, self.details)


class InvalidRequestError(SDKError, ValueError):
    code = "invalid_request"


class ResourceNotFoundError(SDKError, KeyError):
    code = "not_found"


class OperationUnavailableError(SDKError):
    code = "operation_unavailable"


__all__ = [
    "InvalidRequestError",
    "OperationUnavailableError",
    "ResourceNotFoundError",
    "SDKError",
]
