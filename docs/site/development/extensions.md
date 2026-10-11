# Add an EMRF extension

EMRF does not load arbitrary third-party code at runtime. Extensions are
reviewed, in-tree operation families so scientific provenance and API safety
remain enforceable.

## Add an operation

1. Implement or reuse a domain service under `emrf`.
2. Define immutable request/response values in `emrf.sdk.models`.
3. Add an `EMRFClient` method that translates domain failures into stable SDK
   errors.
4. Add the CLI adapter.
5. Add strict Pydantic REST v2 models and endpoint. Protect mutations.
6. Preserve REST v1 unless a compatibility requirement explicitly applies.
7. Add direct SDK/CLI/API parity tests.
8. If it is a runnable research program, register a module target in
   `emrf_registry`; never pass user input to a shell.
9. Update the knowledge graph when scientific claims, datasets, or sources
   change.
10. Regenerate reference documentation and run CI.

## Plugin boundary

A future external plugin API requires an ADR, signed/discoverable package
metadata, compatibility ranges, isolation policy, and evidence/provenance
contract. Entry-point auto-loading is intentionally unsupported today.
