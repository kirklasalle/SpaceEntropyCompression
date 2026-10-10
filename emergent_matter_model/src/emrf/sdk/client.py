"""Typed in-process application interface for EMRF."""

from __future__ import annotations

from typing import Any

import emrf_registry

from .errors import InvalidRequestError, ResourceNotFoundError
from .models import (
    CommandInfo,
    CommandListResponse,
    RunInfo,
    RunListResponse,
    RunRequest,
    RunResult,
    VerificationReport,
)


class EMRFClient:
    """Expose stable typed operations without transport-specific behavior."""

    def list_commands(self, category: str | None = None) -> CommandListResponse:
        if category is not None and category not in emrf_registry.CATEGORIES:
            raise InvalidRequestError(
                f"Unknown category: {category}",
                details={"categories": list(emrf_registry.CATEGORIES)},
            )
        commands = tuple(
            CommandInfo.from_mapping(command)
            for command in emrf_registry.list_commands(category)
        )
        return CommandListResponse(commands)

    def get_command(self, name: str) -> CommandInfo:
        try:
            emrf_registry.get_command(name)
        except KeyError as exc:
            raise ResourceNotFoundError(
                exc.args[0],
                details={"resource": "command", "name": name},
            ) from None
        row = next(
            command
            for command in emrf_registry.list_commands()
            if command["name"] == name
        )
        return CommandInfo.from_mapping(row)

    def run(self, request: RunRequest, *, capture: bool = False) -> RunResult:
        self.get_command(request.command)
        result: dict[str, Any] = emrf_registry.run_command(
            request.command,
            list(request.args),
            timeout=request.timeout,
            capture=capture,
            evidence_class=request.evidence_class,
            inputs=dict(request.inputs),
            seeds=dict(request.seeds),
        )
        return RunResult.from_mapping(result)

    def list_runs(self, *, limit: int = 50) -> RunListResponse:
        from emrf_run_access import public_record, run_store

        records = tuple(
            RunInfo.from_mapping(public_record(record))
            for record in run_store().list(limit=limit)
        )
        return RunListResponse(records)

    def get_run(self, run_id: str) -> RunInfo:
        from emrf_run_access import public_record, run_store

        try:
            record = run_store().get(run_id)
        except KeyError as exc:
            raise ResourceNotFoundError(
                exc.args[0],
                details={"resource": "run", "run_id": run_id},
            ) from None
        return RunInfo.from_mapping(public_record(record))

    def verify_physics(self) -> VerificationReport:
        from emrf_physics_access import known_limit_report

        return VerificationReport.from_mapping(known_limit_report())

    def verify_inference(self) -> VerificationReport:
        from emrf_validation_access import inference_validation_report

        return VerificationReport.from_mapping(inference_validation_report())

    def verify_engines(self) -> VerificationReport:
        from emrf_validation_access import engine_validation_report

        return VerificationReport.from_mapping(engine_validation_report())


__all__ = ["EMRFClient"]
