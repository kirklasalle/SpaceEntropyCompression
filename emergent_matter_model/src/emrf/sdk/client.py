"""Typed in-process application interface for EMRF."""

from __future__ import annotations

import mimetypes
from pathlib import Path, PurePosixPath
from typing import Any, cast

import emrf_registry

from .errors import (
    InvalidRequestError,
    OperationUnavailableError,
    ResourceNotFoundError,
)
from .models import (
    ArtifactContent,
    ArtifactInfo,
    ArtifactListResponse,
    CommandInfo,
    CommandListResponse,
    DatasetListResponse,
    DatasetRecord,
    EnvironmentReport,
    JobInfo,
    JobListResponse,
    KnowledgeNode,
    KnowledgeQueryResponse,
    KnowledgeSourceRequest,
    KnowledgeValidationReport,
    OperationResult,
    PredictionCommitment,
    PredictionVerification,
    RunInfo,
    RunListResponse,
    RunRequest,
    RunResult,
    SimulationRequest,
    SimulationResult,
    SupportReport,
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

    def validate_knowledge(self) -> KnowledgeValidationReport:
        try:
            report = self._knowledge_store().validate()
        except OSError as exc:
            raise OperationUnavailableError(str(exc)) from exc
        return KnowledgeValidationReport.from_mapping(report)

    def query_knowledge(
        self,
        text: str | None = None,
        *,
        kind: str | None = None,
        lifecycle_status: str | None = None,
        limit: int = 100,
    ) -> KnowledgeQueryResponse:
        try:
            result = self._knowledge_store().query(
                text,
                kind=kind,
                lifecycle_status=lifecycle_status,
                limit=limit,
            )
        except (TypeError, ValueError) as exc:
            raise InvalidRequestError(str(exc)) from exc
        except OSError as exc:
            raise OperationUnavailableError(str(exc)) from exc
        return KnowledgeQueryResponse(
            tuple(KnowledgeNode(node) for node in result["nodes"])
        )

    def get_knowledge_node(
        self,
        node_id: str,
        *,
        resolve_inheritance: bool = False,
    ) -> KnowledgeNode:
        try:
            node = self._knowledge_store().get_node(
                node_id,
                resolve_inheritance=resolve_inheritance,
            )
        except KeyError as exc:
            raise ResourceNotFoundError(
                exc.args[0],
                details={"resource": "knowledge_node", "node_id": node_id},
            ) from None
        except OSError as exc:
            raise OperationUnavailableError(str(exc)) from exc
        return KnowledgeNode(node)

    def add_knowledge_source(
        self,
        request: KnowledgeSourceRequest,
    ) -> KnowledgeNode:
        try:
            node = self._knowledge_store().add_source(request.to_dict())
        except (TypeError, ValueError) as exc:
            raise InvalidRequestError(str(exc)) from exc
        except OSError as exc:
            raise OperationUnavailableError(str(exc)) from exc
        return KnowledgeNode(node)

    def knowledge_snapshot(self) -> OperationResult:
        try:
            graph = self._knowledge_store().load()
            report = self._knowledge_store().validate()
        except OSError as exc:
            raise OperationUnavailableError(str(exc)) from exc
        if not report["valid"]:
            raise OperationUnavailableError(
                "Knowledge graph failed validation",
                details={"errors": report["errors"]},
            )
        return OperationResult(graph)

    def export_knowledge(self, destination: str) -> OperationResult:
        try:
            result = self._knowledge_store().export(destination)
        except (TypeError, ValueError) as exc:
            raise InvalidRequestError(str(exc)) from exc
        except OSError as exc:
            raise OperationUnavailableError(str(exc)) from exc
        return OperationResult(result)

    def link_run_knowledge(
        self,
        run_id: str,
        *,
        claim_ids: tuple[str, ...] = (),
        source_ids: tuple[str, ...] = (),
        dataset_ids: tuple[str, ...] = (),
    ) -> OperationResult:
        try:
            result = self._knowledge_store().link_run(
                run_id,
                claim_ids=claim_ids,
                source_ids=source_ids,
                dataset_ids=dataset_ids,
            )
        except KeyError as exc:
            raise ResourceNotFoundError(
                exc.args[0],
                details={"resource": "knowledge_link", "run_id": run_id},
            ) from None
        except (TypeError, ValueError) as exc:
            raise InvalidRequestError(str(exc)) from exc
        except OSError as exc:
            raise OperationUnavailableError(str(exc)) from exc
        return OperationResult(result)

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

    def environment_report(self, *, include_executable: bool = False) -> EnvironmentReport:
        report = dict(emrf_registry.environment_report())
        if not include_executable:
            report.pop("executable", None)
        return EnvironmentReport(report)

    def create_support_report(
        self,
        destination: str | None = None,
    ) -> SupportReport:
        from emrf.support import create_support_report

        try:
            result = create_support_report(destination)
        except (FileExistsError, TypeError, ValueError) as exc:
            raise InvalidRequestError(str(exc)) from exc
        except OSError as exc:
            raise OperationUnavailableError(str(exc)) from exc
        return SupportReport.from_mapping(result)

    def list_datasets(self, *, verify: bool = False) -> DatasetListResponse:
        library = self._data_library()
        rows = self._data_call(lambda: library.catalog_status(verify=verify))
        return DatasetListResponse(tuple(DatasetRecord(row) for row in rows))

    def get_dataset(self, dataset_id: str, *, verify: bool = False) -> DatasetRecord:
        library = self._data_library()
        row = self._data_call(lambda: library.info(dataset_id, verify=verify))
        return DatasetRecord(row)

    def import_dataset(
        self,
        dataset_id: str,
        *,
        logical_name: str | None = None,
        source: str | None = None,
    ) -> OperationResult:
        library = self._data_library()
        holdings = self._data_call(
            lambda: library.import_dataset(
                dataset_id,
                logical_name=logical_name,
                source=source,
            )
        )
        return OperationResult({"holdings": holdings})

    def fetch_dataset(
        self,
        dataset_id: str,
        *,
        logical_name: str | None = None,
        retries: int = 3,
        timeout: float = 180.0,
    ) -> OperationResult:
        library = self._data_library()
        holdings = self._data_call(
            lambda: library.fetch_dataset(
                dataset_id,
                logical_name=logical_name,
                retries=retries,
                timeout=timeout,
            )
        )
        return OperationResult({"holdings": holdings})

    def verify_datasets(self) -> OperationResult:
        library = self._data_library()
        return OperationResult(self._data_call(library.verify))

    def create_data_backup(self, destination: str) -> OperationResult:
        library = self._data_library()
        return OperationResult(
            self._data_call(lambda: library.create_backup(destination))
        )

    def create_offsite_data_backup(
        self,
        destination_root: str | None = None,
    ) -> OperationResult:
        library = self._data_library()
        return OperationResult(
            self._data_call(
                lambda: library.create_offsite_backup(destination_root)
            )
        )

    def verify_data_backup(self, source: str) -> OperationResult:
        library = self._data_library()
        return OperationResult(
            self._data_call(lambda: library.verify_backup(source))
        )

    def restore_data_backup(self, source: str) -> OperationResult:
        library = self._data_library()
        return OperationResult(
            self._data_call(lambda: library.restore_backup(source))
        )

    def run_data_restore_drill(
        self,
        *,
        receipt: str | None = None,
        workspace: str | None = None,
    ) -> OperationResult:
        library = self._data_library()
        return OperationResult(
            self._data_call(
                lambda: library.run_restore_drill(
                    receipt=receipt,
                    workspace=workspace,
                )
            )
        )

    def garbage_collect_data(self, *, execute: bool = False) -> OperationResult:
        library = self._data_library()
        return OperationResult(
            self._data_call(lambda: library.garbage_collect(execute=execute))
        )

    def create_state_backup(self, destination: str) -> OperationResult:
        manager = self._recovery_manager()
        result = self._recovery_call(lambda: manager.create(destination))
        return OperationResult(
            {
                **result,
                "destination": str(Path(destination).expanduser().resolve()),
            }
        )

    def verify_state_backup(self, source: str) -> OperationResult:
        manager = self._recovery_manager()
        result = self._recovery_call(lambda: manager.verify(source))
        return OperationResult(
            {
                **result,
                "source": str(Path(source).expanduser().resolve()),
            }
        )

    def restore_state_backup(
        self,
        source: str,
        destination: str,
    ) -> OperationResult:
        manager = self._recovery_manager()
        return OperationResult(
            self._recovery_call(lambda: manager.restore(source, destination))
        )

    def run_state_restore_drill(
        self,
        *,
        receipt: str | None = None,
        workspace: str | None = None,
    ) -> OperationResult:
        manager = self._recovery_manager()
        if receipt is None:
            receipt = str(manager.default_receipt_path())
        result = self._recovery_call(
            lambda: manager.drill(receipt, workspace=workspace)
        )
        return OperationResult(
            {
                **result,
                "receipt": str(Path(receipt).expanduser().resolve()),
            }
        )

    def run_performance_baseline(
        self,
        *,
        profile: str = "standard",
        repeats: int | None = None,
        workloads: tuple[str, ...] | None = None,
    ) -> OperationResult:
        from emrf.performance import PerformanceBaselineRunner

        try:
            result = PerformanceBaselineRunner().run(
                profile=profile,
                repeats=repeats,
                workloads=workloads,
            )
        except (TypeError, ValueError) as exc:
            raise InvalidRequestError(str(exc)) from exc
        except OSError as exc:
            raise OperationUnavailableError(str(exc)) from exc
        return OperationResult(result)

    def commit_json_prediction(
        self,
        prediction: Any,
        *,
        label: str,
    ) -> PredictionCommitment:
        from emrf_prediction_access import commit_json_prediction

        try:
            record = commit_json_prediction(prediction, label=label)
        except (TypeError, ValueError, OSError) as exc:
            raise InvalidRequestError(str(exc)) from exc
        return PredictionCommitment.from_mapping(record)

    def commit_prediction_file(
        self,
        path: str,
        *,
        label: str,
    ) -> PredictionCommitment:
        from emrf_prediction_access import commit_prediction_file

        try:
            record = commit_prediction_file(path, label=label)
        except (TypeError, ValueError, OSError) as exc:
            raise InvalidRequestError(str(exc)) from exc
        return PredictionCommitment.from_mapping(record)

    def get_prediction(self, commitment_id: str) -> PredictionCommitment:
        from emrf_prediction_access import get_commitment

        try:
            record = get_commitment(commitment_id)
        except KeyError as exc:
            raise ResourceNotFoundError(
                exc.args[0],
                details={"resource": "prediction", "commitment_id": commitment_id},
            ) from None
        except ValueError as exc:
            raise InvalidRequestError(str(exc)) from exc
        return PredictionCommitment.from_mapping(record)

    def verify_json_prediction(
        self,
        commitment_id: str,
        prediction: Any,
    ) -> PredictionVerification:
        from emrf_prediction_access import verify_json_prediction

        try:
            report = verify_json_prediction(commitment_id, prediction)
        except KeyError as exc:
            raise ResourceNotFoundError(
                exc.args[0],
                details={"resource": "prediction", "commitment_id": commitment_id},
            ) from None
        except (TypeError, ValueError) as exc:
            raise InvalidRequestError(str(exc)) from exc
        return PredictionVerification.from_mapping(report)

    def verify_prediction_file(
        self,
        commitment_id: str,
        path: str,
    ) -> PredictionVerification:
        from emrf_prediction_access import verify_prediction_file

        try:
            report = verify_prediction_file(commitment_id, path)
        except KeyError as exc:
            raise ResourceNotFoundError(
                exc.args[0],
                details={"resource": "prediction", "commitment_id": commitment_id},
            ) from None
        except (TypeError, ValueError, OSError) as exc:
            raise InvalidRequestError(str(exc)) from exc
        return PredictionVerification.from_mapping(report)

    def simulate(self, request: SimulationRequest) -> SimulationResult:
        from server import _validate_and_parse_payload, run_simulation

        try:
            n, weights, grid, k, alpha, c0 = _validate_and_parse_payload(
                request.to_dict()
            )
        except (TypeError, ValueError) as exc:
            raise InvalidRequestError(str(exc)) from exc
        values = run_simulation(n, weights, grid, k, alpha, c0)
        return SimulationResult(tuple(int(size) for size in values.shape), values.tolist())

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

    def list_artifacts(self, run_id: str) -> ArtifactListResponse:
        from emrf.runs.artifacts import scan_artifacts

        root = self._run_path(run_id)
        return ArtifactListResponse(
            tuple(
                ArtifactInfo(
                    path=record.path,
                    bytes=record.bytes,
                    media_type=record.media_type,
                )
                for record in scan_artifacts(root)
            )
        )

    def get_artifact(self, run_id: str, relative_path: str) -> ArtifactContent:
        root = self._run_path(run_id)
        normalized = relative_path.replace("\\", "/")
        path = PurePosixPath(normalized)
        if (
            not normalized
            or path.is_absolute()
            or any(part in {"", ".", ".."} for part in path.parts)
        ):
            raise InvalidRequestError("Artifact path is invalid.")
        raw_candidate = root / Path(*path.parts)
        if raw_candidate.is_symlink():
            raise ResourceNotFoundError(
                "Artifact was not found.",
                details={"resource": "artifact", "path": normalized},
            )
        candidate = raw_candidate.resolve()
        if root not in candidate.parents or not candidate.is_file():
            raise ResourceNotFoundError(
                "Artifact was not found.",
                details={"resource": "artifact", "path": normalized},
            )
        info = ArtifactInfo(
            path="/".join(path.parts),
            bytes=candidate.stat().st_size,
            media_type=mimetypes.guess_type(candidate.name)[0]
            or "application/octet-stream",
        )
        return ArtifactContent(info, candidate)

    def verify_physics(self) -> VerificationReport:
        from emrf_physics_access import known_limit_report

        return VerificationReport.from_mapping(known_limit_report())

    def verify_inference(self) -> VerificationReport:
        from emrf_validation_access import inference_validation_report

        return VerificationReport.from_mapping(inference_validation_report())

    def verify_engines(self) -> VerificationReport:
        from emrf_validation_access import engine_validation_report

        return VerificationReport.from_mapping(engine_validation_report())

    @staticmethod
    def _data_library() -> Any:
        from emrf_data_access import data_library

        return data_library()

    @staticmethod
    def _knowledge_store() -> Any:
        from emrf.knowledge import KnowledgeStore

        return KnowledgeStore()

    @staticmethod
    def _recovery_manager() -> Any:
        from emrf_recovery_access import recovery_manager

        return recovery_manager()

    @staticmethod
    def _recovery_call(operation: Any) -> Any:
        from emrf.core.errors import IntegrityError

        try:
            return operation()
        except FileExistsError as exc:
            raise InvalidRequestError(str(exc)) from exc
        except FileNotFoundError as exc:
            raise ResourceNotFoundError(
                str(exc),
                details={"resource": "state_backup"},
            ) from exc
        except (TypeError, ValueError) as exc:
            raise InvalidRequestError(str(exc)) from exc
        except IntegrityError as exc:
            raise OperationUnavailableError(
                str(exc),
                details={"kind": "integrity"},
            ) from exc
        except OSError as exc:
            raise OperationUnavailableError(
                str(exc),
                details={"kind": "storage"},
            ) from exc

    @staticmethod
    def _data_call(operation: Any) -> Any:
        from emrf_data_access import data_errors

        errors = data_errors()
        try:
            return operation()
        except KeyError as exc:
            raise ResourceNotFoundError(
                exc.args[0],
                details={"resource": "dataset"},
            ) from None
        except FileNotFoundError as exc:
            raise ResourceNotFoundError(
                str(exc),
                details={"resource": "data_path"},
            ) from exc
        except (TypeError, ValueError) as exc:
            raise InvalidRequestError(str(exc)) from exc
        except errors.IntegrityError as exc:
            raise OperationUnavailableError(
                str(exc),
                details={"kind": "integrity"},
            ) from exc
        except errors.AcquisitionError as exc:
            raise OperationUnavailableError(
                str(exc),
                details={"kind": "acquisition"},
            ) from exc
        except OSError as exc:
            raise OperationUnavailableError(
                str(exc),
                details={"kind": "storage"},
            ) from exc

    @staticmethod
    def _run_path(run_id: str) -> Path:
        from emrf_run_access import run_store

        try:
            return cast(Path, run_store().get(run_id).path.resolve())
        except KeyError as exc:
            raise ResourceNotFoundError(
                exc.args[0],
                details={"resource": "run", "run_id": run_id},
            ) from None


__all__ = ["EMRFClient"]
