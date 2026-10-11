# Architecture

`EMRFClient` is the authoritative in-process application layer.

```text
CLI ───────────────┐
Flask REST v1 ─────┼──> EMRFClient ──> domain services and durable stores
FastAPI REST v2 ───┘
```

Key services:

- content-addressed observational-data library;
- crash-recoverable runs and jobs;
- scientific verification certificates;
- versioned scientific knowledge graph;
- immutable prediction commitments.

Adapters own transport formatting and authentication, not scientific or
storage rules. REST v1 is compatibility-only. New operations require typed SDK
contracts first, then CLI/v2 adapters and parity tests.
