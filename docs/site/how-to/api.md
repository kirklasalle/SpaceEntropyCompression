# Operate the APIs safely

## REST v1 compatibility

Flask REST v1 preserves existing clients. Its mutation flags are independent:

- `EMRF_API_ALLOW_RUN=1`
- `EMRF_API_ALLOW_DATA_WRITE=1`
- `EMRF_API_ALLOW_PREDICTION_WRITE=1`

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

See the generated [REST v2 reference](../reference/api-v2.md).
