"""Typed in-process application interface for EMRF."""

from __future__ import annotations

from typing import Any

import emrf_registry

from .errors import InvalidRequestError, ResourceNotFoundError
from .models import (
    CommandInfo,
    CommandListResponse,
    JobInfo,
    JobListResponse,
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

    def submit_job(
        self,
        request: RunRequest,
        *,
        max_attempts: int = 1,
    ) -> JobInfo:
        from emrf_run_access import public_record, run_store

        command = self.get_command(request.command)
        if command.gui or command.category == "service":
            raise InvalidRequestError(
                f"{request.command} is interactive or a service and cannot run as a job"
            )
        try:
            record = run_store().enqueue(
                request.command,
                list(request.args),
                timeout_seconds=request.timeout,
                evidence_class=request.evidence_class,
                max_attempts=max_attempts,
            )
        except (TypeError, ValueError) as exc:
            raise InvalidRequestError(str(exc)) from exc
        return JobInfo.from_mapping(public_record(record))

    def list_jobs(self, *, limit: int = 50) -> JobListResponse:
        from emrf_run_access import public_record, run_store

        jobs = tuple(
            JobInfo.from_mapping(public_record(record))
            for record in run_store().list_jobs(limit=limit)
        )
        return JobListResponse(jobs)

    def get_job(self, job_id: str) -> JobInfo:
        from emrf_run_access import public_record, run_store

        try:
            record = run_store().get_job(job_id)
        except KeyError as exc:
            raise ResourceNotFoundError(
                exc.args[0],
                details={"resource": "job", "job_id": job_id},
            ) from None
        return JobInfo.from_mapping(public_record(record))

    def cancel_job(self, job_id: str) -> JobInfo:
        from emrf_run_access import public_record, run_store

        try:
            record = run_store().cancel_job(job_id)
        except KeyError as exc:
            raise ResourceNotFoundError(
                exc.args[0],
                details={"resource": "job", "job_id": job_id},
            ) from None
        except ValueError as exc:
            raise InvalidRequestError(str(exc)) from exc
        return JobInfo.from_mapping(public_record(record))

    def run_next_job(
        self,
        worker_id: str,
        *,
        lease_seconds: float = 3600,
    ) -> JobInfo | None:
        from emrf_run_access import public_record

        if not isinstance(worker_id, str) or not worker_id.strip():
            raise InvalidRequestError("worker_id must be non-empty text")
        if (
            isinstance(lease_seconds, bool)
            or not isinstance(lease_seconds, (int, float))
            or lease_seconds <= 0
        ):
            raise InvalidRequestError("lease_seconds must be a positive number")
        try:
            record = emrf_registry.run_next_job(
                worker_id.strip(),
                lease_seconds=float(lease_seconds),
            )
        except (TypeError, ValueError) as exc:
            raise InvalidRequestError(str(exc)) from exc
        if record is None:
            return None
        return JobInfo.from_mapping(public_record(record))

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
