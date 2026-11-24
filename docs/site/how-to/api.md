# Operate the APIs safely

## REST v1 compatibility

Flask REST v1 preserves existing clients and is deprecated for removal no
earlier than EMRF `2.0`. Its mutation flags are independent:

- `EMRF_API_ALLOW_RUN=1`
- `EMRF_API_ALLOW_DATA_WRITE=1`
- `EMRF_API_ALLOW_PREDICTION_WRITE=1`

`gunicorn.conf.py` defaults to loopback binding (`127.0.0.1:5000`) with a
`150`s worker timeout above the `120`s route execution cap. REST v1 enforces
opt-in CORS (`EMRF_CORS_ORIGINS`), a `1 MiB` request body limit, bounded
sliding-window rate limiting, deprecation/security headers, IO path confinement,
and CLI argument validation. Mutation routes require a bearer token when
`EMRF_API_V1_TOKEN` or `EMRF_API_V2_TOKEN` is configured, and reject
non-loopback callers when no token is configured outside tests; do not expose
REST v1 directly to an untrusted network.

Application-state backup, verification, isolated restore, and drills use
`EMRF_API_ALLOW_DATA_WRITE=1` because they read protected scientific state and
write backup or receipt paths. Performance baseline execution uses
`EMRF_API_ALLOW_RUN=1`; expose it only to trusted operators.

## REST v2

FastAPI v2 is the canonical REST surface and is served from the ASGI application:

```text
uvicorn asgi:app --host 127.0.0.1 --port 8000
```

Configure `EMRF_API_V2_TOKEN` before enabling mutation endpoints. Send:

```text
Authorization: Bearer TOKEN
```

Use `/api/v2/docs` for interactive documentation and
`/api/v2/openapi.json` for generated clients. Bind to loopback unless a
trusted reverse proxy supplies TLS, request limits, authentication policy,
and audit logging.

REST v2 enforces a `1 MiB` request body limit, sliding-window rate limiting,
security response headers, HTTP IO path confinement, and CLI argument
validation. Bearer authentication is required for `/api/v2/runs*`,
`/api/v2/jobs*`, `/api/v2/datasets/verify`, `/api/v2/verification/*`, all
`/api/v2/recovery/*` operations, and `POST /api/v2/performance/baselines`;
`/api/v2/doctor` redacts `app_root` and `data_root` when unauthenticated, and
`/api/v2/datasets*` `?verify=true` requires bearer authentication.

See the generated [REST v2 reference](../reference/api-v2.md).
