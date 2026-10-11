# ADR 0001: Authoritative typed application layer

- Status: accepted
- Date: 2026-10-10

## Decision

`EMRFClient` is the authoritative application layer. CLI, REST v1, and REST v2
are thin adapters. Stable immutable SDK types and errors define the supported
programmatic contract.

## Consequences

Scientific/storage logic is implemented once. Adapter parity is testable.
REST v1 remains a compatibility surface; new functionality targets SDK and v2.
