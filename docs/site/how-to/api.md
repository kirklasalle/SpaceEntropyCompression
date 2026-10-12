# Operate the APIs safely

## REST v1 compatibility

Flask REST v1 preserves existing clients. Its mutation flags are independent:

- `EMRF_API_ALLOW_RUN=1`
- `EMRF_API_ALLOW_DATA_WRITE=1`
- `EMRF_API_ALLOW_PREDICTION_WRITE=1`

Application-state backup, verification, isolated restore, and drills use
`EMRF_API_ALLOW_DATA_WRITE=1` because they read protected scientific state and
write backup or receipt paths. REST v1 remains unauthenticated compatibility
infrastructure and must not be exposed directly to an untrusted network.

## REST v2

FastAPI v2 is served from the ASGI application:

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

All `/api/v2/recovery/*` operations require the bearer token, including
verification, because callers can select server-side filesystem paths.

See the generated [REST v2 reference](../reference/api-v2.md).
