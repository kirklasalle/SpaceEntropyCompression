# Supported versions and deprecation

EMRF support is an evidence-backed contract. “Supported” means the combination
is exercised by protected CI or an explicitly identified release rehearsal;
successful installation on another version is not equivalent to certification.

## Current 1.x support matrix

| Surface | Supported contract |
|---|---|
| Python | CPython 3.10 and 3.12 on Windows Server 2022 and Ubuntu 24.04 are certified; Python 3.12 is recommended |
| Java client | Java 17 and JavaFX 17 are certified |
| Python SDK | Public `emrf.sdk` types and `EMRFClient` methods follow package semantic versioning |
| CLI | Commands and JSON output documented in the generated CLI reference are stable within 1.x |
| REST v1 | Compatibility API; existing routes and payloads remain supported throughout 1.x |
| REST v2 | Preferred generated OpenAPI contract for new integrations |
| Data catalog | Schema `1.0.0`; every dataset version and object digest is immutable |
| Knowledge graph | Schema `1.0.0`; semantic validation is required in addition to JSON Schema |
| Data backup | Manifest schema `1.0.0` |
| Application-state backup | Manifest and receipt schema `1.0.0` |
| Scientific certificates | Versioned by the EMRF release and immutable once published |

Python 3.11 may work within the declared package range but is not currently a
certified matrix target. Python 3.13 and later are unsupported until numerical,
binary-wheel and golden-result CI is added. Operating systems, interpreters or
Java versions outside the matrix receive best-effort diagnostics, not release
certification.

## Compatibility rules

- Patch releases must be backward compatible and may contain correctness,
  security, documentation and dependency-lifecycle fixes.
- Minor releases may add fields, endpoints and commands. Existing typed fields
  and behavior remain compatible unless they complete the deprecation process.
- A major release is required to remove supported API behavior or introduce an
  incompatible schema.
- REST v1 is compatibility-only. Additive parity needed for safe operation may
  be supplied, but new integrations should use the SDK or REST v2.
- Readers fail closed on unknown backup or scientific-state schemas. Migration
  must be explicit, tested and non-destructive.
- Published dataset bytes are never replaced under an existing version. A
  changed object requires a new dataset version, digest, provenance record and
  regenerated dependent certificate.
- Published scientific certificates are evidence records. Corrections create a
  new certificate and retain the superseded record with its reason.

## Deprecation process

A normal deprecation requires all of the following:

1. a release-note and documentation notice identifying the replacement;
2. a runtime warning where a safe warning channel exists;
3. compatibility tests for both the old and replacement path;
4. at least two minor releases and six months of notice; and
5. removal only in a major release when public API or stored data is affected.

REST v1 as a whole receives at least twelve months of notice and cannot be
removed before EMRF 2.0. Dataset, knowledge, backup and certificate schema
readers remain available for every schema emitted by a supported 1.x release,
or a standalone migration tool must be provided before support ends.

Immediate removal is reserved for actively exploitable security behavior,
legally prohibited data distribution, or behavior that can silently corrupt
scientific evidence. Such a change requires an advisory, an explicit migration
or containment procedure, and retained evidence of the retired behavior.

## Runtime lifecycle

Python 3.10 is deprecated because its upstream security support ends in
October 2026. EMRF continues certifying it for the 1.0 line while downstream
users migrate, but no new runtime-specific capability will target 3.10.
Removal requires the notice window above and a protected release that first
certifies the replacement matrix. Java 17 remains the long-term-support client
baseline until a later LTS is certified in parallel.

Dependency lower and upper bounds remain authoritative in `pyproject.toml`.
Changes to those bounds require dependency resolution, audit, SBOM generation,
the complete platform matrix and scientific golden tests.
