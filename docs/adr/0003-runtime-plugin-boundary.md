# ADR 0003: No arbitrary runtime plugins

- Status: accepted
- Date: 2026-10-11

## Decision

Core EMRF does not auto-load third-party Python entry points. Extensions remain
reviewed, in-tree operation families until a separate ADR defines trust,
isolation, versioning, provenance, signing, and failure-containment policy.

## Consequences

The extension tutorial documents the supported in-tree path. UKS and other
external reasoning tools remain optional, one-way, ADR-gated integrations.
