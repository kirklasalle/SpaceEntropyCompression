# REST API v2 reference

Generated from the FastAPI OpenAPI document. Do not edit manually.

API version: `1.0.0`

Interactive documentation is served at `/api/v2/docs` and the machine
contract at `/api/v2/openapi.json`.

## Operations

| Method | Path | Authentication | Tags |
|---|---|---|---|
| `GET` | `/api/v2/commands` | No | commands |
| `GET` | `/api/v2/commands/{name}` | No | commands |
| `POST` | `/api/v2/commands/{name}/runs` | Required | commands, runs |
| `POST` | `/api/v2/data/backups` | Required | data |
| `POST` | `/api/v2/data/backups/offsite` | Required | data |
| `POST` | `/api/v2/data/backups/verify` | Required | data |
| `POST` | `/api/v2/data/gc` | Required | data |
| `POST` | `/api/v2/data/restore-drills` | Required | data |
| `POST` | `/api/v2/data/restores` | Required | data |
| `GET` | `/api/v2/datasets` | No | data |
| `POST` | `/api/v2/datasets/verify` | No | data |
| `GET` | `/api/v2/datasets/{dataset_id}` | No | data |
| `POST` | `/api/v2/datasets/{dataset_id}/fetch` | Required | data |
| `POST` | `/api/v2/datasets/{dataset_id}/import` | Required | data |
| `GET` | `/api/v2/doctor` | No | service |
| `GET` | `/api/v2/health` | No | service |
| `GET` | `/api/v2/jobs` | No | jobs |
| `POST` | `/api/v2/jobs` | Required | jobs |
| `POST` | `/api/v2/jobs/worker/run-next` | Required | jobs |
| `GET` | `/api/v2/jobs/{job_id}` | No | jobs |
| `POST` | `/api/v2/jobs/{job_id}/cancel` | Required | jobs |
| `GET` | `/api/v2/knowledge` | No | knowledge |
| `GET` | `/api/v2/knowledge/export` | No | knowledge |
| `POST` | `/api/v2/knowledge/runs/{run_id}/link` | Required | knowledge |
| `POST` | `/api/v2/knowledge/sources` | Required | knowledge |
| `GET` | `/api/v2/knowledge/validate` | No | knowledge |
| `GET` | `/api/v2/knowledge/{node_id}` | No | knowledge |
| `POST` | `/api/v2/predictions/commit` | Required | predictions |
| `GET` | `/api/v2/predictions/{commitment_id}` | No | predictions |
| `POST` | `/api/v2/predictions/{commitment_id}/verify` | No | predictions |
| `GET` | `/api/v2/runs` | No | runs |
| `GET` | `/api/v2/runs/{run_id}` | No | runs |
| `GET` | `/api/v2/runs/{run_id}/artifacts` | Required | artifacts |
| `GET` | `/api/v2/runs/{run_id}/artifacts/{relative_path}` | Required | artifacts |
| `POST` | `/api/v2/simulations` | Required | simulation |
| `GET` | `/api/v2/verification/engines` | No | verification |
| `GET` | `/api/v2/verification/inference` | No | verification |
| `GET` | `/api/v2/verification/physics` | No | verification |

## Error model

Transport errors use `ErrorResponse` with `code`, `message`, and
`details`. Validation failures return HTTP 422. Mutating operations
require `EMRF_API_V2_TOKEN` and a matching bearer token.

## Schema inventory

- `ArtifactInfo`
- `ArtifactListResponse`
- `BackupRequest`
- `CommandInfo`
- `CommandListResponse`
- `DatasetFetchRequest`
- `DatasetListResponse`
- `DatasetWriteRequest`
- `EnvironmentReport`
- `ErrorResponse`
- `GarbageCollectRequest`
- `HTTPValidationError`
- `HealthResponse`
- `JobInfo`
- `JobListResponse`
- `JobSubmitRequest`
- `KnowledgeQueryResponse`
- `KnowledgeRunLinkRequest`
- `KnowledgeSourceRequest`
- `KnowledgeValidationError`
- `KnowledgeValidationResponse`
- `OffsiteBackupRequest`
- `OperationResponse`
- `PathRequest`
- `PredictionCommitRequest`
- `PredictionCommitment`
- `PredictionVerification`
- `PredictionVerifyRequest`
- `RestoreDrillRequest`
- `RunInfo`
- `RunListResponse`
- `RunRequest`
- `RunResult`
- `SimulationRequest`
- `SimulationResult`
- `ValidationError`
- `VerificationReport`
- `WorkerRequest`
