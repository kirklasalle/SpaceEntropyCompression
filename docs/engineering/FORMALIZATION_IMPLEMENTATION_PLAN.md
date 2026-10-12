# EMRF Formalization Implementation Plan

| Field | Value |
|---|---|
| Date | 2026-10-09 |
| Inputs | [Current Build Reference](CURRENT_BUILD_REFERENCE.md), [Engineering Specification](ENGINEERING_SPECIFICATION.md) |
| Approach | Incremental strangler migration: new structure grows around the working system; legacy paths stay working until replaced and verified |

## How to read this plan

Each phase lists **why**, **steps**, **deliverables** and an **exit gate**.
A phase is complete only when its gate passes. Every gate includes the
**preservation gate**:

> Full test suite passes; `emrf data list --verify` is all `ok`;
> golden-result comparison of the real-data pipelines (SPARC analyses,
> Pantheon+ baseline, DESI baseline, gauntlet) matches `results/` within
> the stated tolerance; every legacy script path still runs.

Phases 1-4 are foundations and should go in order. Phases 5-9 can overlap
once Phase 4 is complete.

---

## Phase 0 - Baseline freeze (complete, 2026-10-09)

* As-built document: [CURRENT_BUILD_REFERENCE.md](CURRENT_BUILD_REFERENCE.md).
* Unified CLI (`emrf_cli.py`), shared registry, REST API parity endpoints,
  OpenAPI 1.1.0, 21 new tests; suite at 265 passing.
* Library catalog seeded in `knowledgebase/library/`.
* Measured baseline: 1,051 ruff findings, 156 mypy errors, no coverage, no CI.

**Next action for Kirk:** review and commit Phase 0, then tag
`baseline-2026-10-09` so every later step can be compared against it.

## Phase 1 - Safety net (1-2 weeks)

**Why:** before moving code, capture behaviour so any change that alters a
number is caught automatically.

1. Golden-result harness: `tests/golden/` re-runs each real-data pipeline
   into a temp directory and compares with `results/` (exact for integers
   and hashes, `rtol=1e-10` for floats unless documented).
2. Add `coverage`, `hypothesis`, `pytest-xdist`; record coverage baseline.
3. GitHub Actions CI: Windows + Linux, Python 3.10 (current) and 3.12,
   running ruff (report-only at first), pytest, golden results, `emrf doctor`.
4. Fix the correctness-relevant lint classes first: `W605` invalid escapes
   (future syntax errors), `B023` loop-variable closures, `F841`, `E741`.
   Leave pinned files untouched, or update them together with a regenerated
   review manifest and a changelog entry.
5. Pre-commit hooks (ruff format/check, end-of-file, large-file guard).

**Exit gate:** CI green on both OSes; golden harness covers all `analysis`
registry commands that use real data; preservation gate.

### Phase 1 implementation status (2026-10-09)

Implemented locally:

* isolated golden-result runner for all eight fixed real-data analysis
  commands, with exact integer/string comparisons and `rtol=1e-10` for
  non-optimizer floats on the Windows x86-64/Python 3.10 baseline
  environment; legacy nested SPARC optimizer cases use a measured `rtol=5e-3`
  (the bulge scan uses `rtol=1e-2` after measured 5.3e-3 drift) pending
  deterministic reformulation, while
  two standalone L-BFGS-B halo totals use a path-specific `rtol=1e-7`;
  Pantheon+ and DESI baseline optimizer outputs also use `rtol=1e-7`, with a
  path-specific `atol=1e-11` only for a Pantheon+ quadrature diagnostic whose
  expected value is at machine-zero scale;
* immutable published data products listed by the reviewed gauntlet are
  acquired into the isolated workspace and rejected unless both byte count
  and SHA-256 match; mutable reference/archive webpages remain citations and
  are excluded from the byte-stability gate (link availability belongs in a
  separate scheduled check);
* `coverage.py`, Hypothesis and pytest-xdist development dependencies;
* Windows/Linux CI on Python 3.10 and 3.12, plus a separate Windows/Python
  3.10 real-data golden matrix (one job per pipeline) constrained to the
  measured baseline dependency versions;
* pre-commit whitespace, JSON/TOML, large-file and Ruff hooks;
* correctness lint cleanup outside hash-pinned evidence files; the remaining
  exceptions are declared narrowly for two pinned files;
* measured source-only non-golden baseline: 272 tests passed, 52.5% line
  coverage and 42.4% branch coverage (50.7% combined).

The complete local golden run matches all eight reviewed results. The Phase 1
remote exit gate passed all 12 functional and golden jobs on Windows and Linux
in [GitHub Actions run 37980145635](https://github.com/kirklasalle/SpaceEntropyCompression/actions/runs/37980145635).
Phase 2 may begin after the final Phase 1 status commit is tagged and submitted
for review; the original baseline tag remains immutable.

**Numerical-stability debt:** hosted runs exposed up to approximately 0.18%
relative drift in legacy nested SPARC nuisance profiles and 0.53% in two
bulge-derived interval widths despite fixed Python, NumPy and SciPy versions.
Phase 5 must replace or stabilize those optimizers, add convergence
diagnostics, and tighten their golden tolerance. This drift must not be
interpreted as observational uncertainty.

## Phase 2 - Packaging and namespace (2-3 weeks)

**Why:** `pip install` currently ships 8 of ~40 modules and the flat
namespace is fragile.

1. Create `src/emrf/` with the layered layout of spec section 3.1. The
   initial increment establishes the public namespace, package version, and
   `emrf` console entry point without relocating legacy implementations.
2. Move modules one layer at a time (core -> physics -> data -> inference ->
   validation -> interfaces), leaving a one-line shim at each old path
   (`from emrf.physics.engines.lensing import *`) so every legacy import and
   script keeps working.
3. Single `pyproject.toml` with extras `[api]`, `[viz]`, `[cosmo]`, `[dev]`;
   `[project.scripts] emrf = "emrf.interfaces.cli:main"`; dynamic version
   from `emrf/_version.py` (replaces `emrf_version.py`).
4. Lock with `uv lock` (hashes); generate `requirements.lock` for pip users;
   remove stale `pyyaml`; move off Python 3.10.0 to 3.12.
5. Regenerate the review manifest for intentionally changed files, recorded
   as a new evidence version; the old manifest is archived, not overwritten.
6. `import-linter` contracts enforce layer direction.

**Phase 2 increment status (2026-10-09):** the compatibility-preserving
`src/emrf` namespace and installed `emrf` console entry point are implemented.
The existing flat modules remain explicitly packaged, so legacy imports and
scripts are not removed while the layered migration proceeds. The first
`emrf.physics` bridge exposes `EmergentMatterModel` while retaining `model.py`
as the canonical implementation until direct-script and installed-package
execution can share the new module without path-dependent behavior. The same
compatibility pattern now exposes the standard orbital and Schwarzschild
benchmarks as `emrf.physics.baselines`, with function identity tests preventing
numerical divergence from `physics_baseline.py`. The first data-layer bridge,
`emrf.data.provenance`, exposes the existing fail-closed synthetic-data and
observation-integrity checks without changing their legacy consumers. The
installed REST surface is available as `emrf.interfaces.api`, re-exporting the
same Flask application and simulation function used by `server.py`.
Installed storage now resolves through `EMRF_HOME`/`EMRF_DATA_DIR` with
platform-user defaults, while checkouts retain their existing repository data
paths. Registry entries use packaged module targets when no checkout exists and
identify repository audit/release operations as `source_only`; the shared
catalog is exposed as `emrf.interfaces.registry`.

**Phase 2 local exit status (2026-10-09):** passed. A clean wheel resolves all
30 installable command modules, explicitly reports 15 checkout-required
operations, uses user-writable installed storage, and preserves legacy imports.
The complete non-golden suite and all eight reviewed golden pipelines pass.
Remote CI certification is required before Phase 3 changes are merged.

**Exit gate:** `pip install .` in a clean venv runs every installable registry
command and reports checkout-required commands explicitly; `emrf` console
script works; all legacy paths work; preservation gate.

## Phase 3 - Observational data library (3-4 weeks)

**Why:** the data is the project's scientific capital; it must be complete,
verified, deduplicated, backed up and queryable.

1. `emrf.data.store`: content-addressed store with atomic, fsync'd writes,
   file locks and quarantine for mismatches.
2. `emrf.data.catalog`: loads `knowledgebase/library/data_catalog.json`;
   SQLite holdings registry (`data/library.sqlite`, WAL).
3. Streaming, resumable fetchers with retries and pinned commits; register
   existing holdings (SPARC, Pantheon+, DESI DR1) by importing their pinned
   hashes from `download_manifest.json`, `pantheon_baseline.json` and
   `gauntlet.json`; deduplicate the three covariance copies.
4. CLI/API: `emrf data catalog|fetch|verify|info|import|backup|restore|gc`
   and matching `/api/v1/datasets/...` endpoints.
5. Acquire the priority tier (see catalog `priority` field), owner approval
   per dataset for licence and size: DESI DR2 BAO, DES-SN5YR, Union3,
   Planck 2018 likelihood summaries, GWTC catalogs, El-Badry wide binaries
   (Gaia subset), CODATA 2022 constants.
6. Backup: local plus off-site; quarterly restore drill with full verify.

**Foundation status (2026-10-09):** complete and remotely certified.
`emrf.data.store` provides
streamed SHA-256 ingestion, atomic promotion after file `fsync`, verified reads,
deduplication, corrupt-object repair, conservative stale-part cleanup and an
SQLite WAL holdings registry. Holding keys are normalized and immutable: an
idempotent replay may resolve the original record, but neither its bytes nor
its provenance metadata are silently rewritten. Parent-directory `fsync` is
best effort on platforms such as Windows.

**Catalog/interface/backup status (2026-10-09):** implemented locally.
`emrf.data.catalog` strictly validates the curated catalog and its packaged
wheel copy. Existing SPARC, Pantheon+ and DESI DR1 holdings now have pinned
versions and directly testable HTTPS object URLs. Resumable acquisition
validates HTTP range responses and final HTTPS URLs, retries transient
failures, retains safe partial progress, quarantines completed hash failures
and promotes only catalog-pinned bytes. Shared service logic now powers
`emrf data catalog|info|import|fetch|verify|backup|backup-verify|restore|gc`
and matching REST operations. REST mutations require the explicit
`EMRF_API_ALLOW_DATA_WRITE=1` trusted-host opt-in. Backups contain every
verified object, immutable provenance, a manifest and a consistent SQLite
snapshot; restore verifies all bytes before non-destructive import. Garbage
collection is dry-run unless explicitly executed. Automated restore and
tamper tests do not replace the still-required off-site quarterly restore
drill. Priority-tier acquisition remains owner-approved work.

**Local integration status (2026-10-09):** passed. The six pinned files for
SPARC, Pantheon+ and DESI DR1 were imported into the managed store and fully
re-hashed through `emrf data verify`. A temporary portable backup was created,
verified, restored into a separate empty data root and fully verified before
the drill files were removed. This local drill proves the workflow but does
not satisfy the independent off-site-copy requirement.

**Priority acquisition status (2026-10-09):** bounded summary products are
now pinned, acquired and managed for CODATA 2022, the DES-SN5YR Hubble diagram
with statistical and full-systematic covariance, and the official DESI DR2
base-LCDM BAO-only minimization summary. The managed store contains 13 fully
verified holdings. The 1.46 GB DES-SN5YR archive and full DESI chains were
intentionally excluded because the smaller products cover the approved
summary use cases. The Planck PR3 baseline likelihood remains deferred: its
verified official download is approximately 705 MB, has no published content
length at the endpoint, and a stable smaller official `plik_lite` artifact was
not verified. This is a documented safety decision, not an absent check.

**Operational backup status (2026-10-09):** provider-neutral off-site backup
configuration is available through `EMRF_OFFSITE_BACKUP_DIR` or an explicit
independent root; repository credentials are never stored and destinations
inside the managed data root are rejected. A full 13-object/13-holding restore
drill passed and its environment, counts and backup-manifest hash are retained
in `knowledgebase/library/drills/restore-2026-10-09.json`. A physical off-site
copy still requires the owner or operator to supply a mounted, synchronized or
provider-backed destination.

**Exit gate:** every dataset used by any result is in the catalog with
licence, citation and verified hash; kill-during-fetch and corrupted-byte
tests pass; restore drill succeeds; preservation gate.

## Phase 4 - Run records and resilience (2-3 weeks)

**Foundation implemented (2026-10-09):** every unified-registry execution now
creates a durable, time-sortable run record beneath the managed application
root. Atomic `run.json`, immutable `config.toml`, environment and source-control
provenance, input hashes, seeds, attempt state, captured logs and terminal
status are indexed in SQLite WAL. Durable JSON is the source of truth and
reconciles the disposable SQLite index after interruption. `emrf runs
list|info|resume` and matching `/api/v1/runs` endpoints expose inspection and
controlled resumption.

The durable job queue is available through `emrf jobs
submit|list|info|cancel|run-next` and matching `/api/v1/jobs` endpoints.
Transactional claims, leases, retry limits, cancellation and expired-worker
recovery are covered by concurrent and fault-injection tests. Queue and resume
mutations remain disabled in the REST service unless `EMRF_API_ALLOW_RUN=1`.
The SPARC real-data analysis is the first checkpoint-aware long pipeline: it
atomically records each completed acceleration law, resumes from the last
completed boundary and atomically publishes its final JSON result. Fresh-run
scientific results and golden behavior are unchanged.

1. `emrf.runs`: run ID, config TOML, environment lock hash, git commit and
   dirty flag, input hashes, seeds, platform, timings, evidence class.
2. Checkpoint/resume for long pipelines; job queue (SQLite) used by CLI and
   API `POST /api/v1/jobs`.
3. Error taxonomy and exit-code/HTTP mapping (spec section 5).
4. Resilience suite: process kill mid-write, disk full (simulated), network
   drop, permission errors, corrupted inputs, NaN injection.

**Exit gate:** every registry analysis writes a run record; resilience suite
green; no partial outputs after any injected failure; preservation gate.

## Phase 5 - Scientific verification and validation (completed 2026-10-10)

**Foundation slice implemented (2026-10-10):** CODATA 2022 constants now
carry explicit provenance, uncertainty and exactness metadata; public reference
calculations enforce Astropy units and reject missing, incompatible or
non-finite quantities. The first known-limit certificate covers the solar
Schwarzschild radius, PPN solar-limb light bending, Bekenstein-Hawking entropy
and flat-LCDM distance against Astropy. It is available through `emrf verify
physics` and `GET /api/v1/verification/physics`. The 1PN orbit integrator now
uses the exact final partial step, fails closed on non-finite state and
demonstrates fourth-order convergence. The complete current and pending engine
inventory is maintained in `SCIENTIFIC_VERIFICATION_MATRIX.md`.

**Deterministic engine slice implemented (2026-10-10):** the lensing engine
now recovers the first-order GR point-mass deflection and exposes an independent
finite-path ray integral with measured second-order convergence. The CMB
acoustic template is cross-checked against CAMB 1.6.0 for the angular scale and
first three unlensed TT peaks. These CMB checks are explicitly `illustrative`:
the current engine is Planck-calibrated and is not an independent Boltzmann
solver. `emrf verify physics` reports per-check evidence classes and
limitations instead of presenting numerical agreement as physical validation.

**Inference calibration slice implemented (2026-10-10):** the SPARC fitter
now optimizes the entropy acceleration in dimensionless `a/a0` units, checks
optimizer convergence, reports active bounds, and derives local covariance
diagnostics from the residual Jacobian. A deterministic 64-realization
certificate exercises this production fitter and the production Pantheon
full-covariance profile with known injections. It measures ensemble bias,
68.27% interval coverage, residual scale, boundary avoidance, and SPARC
repeated-start agreement through `emrf verify inference` and
`GET /api/v1/verification/inference`. Every result is classified `synthetic`;
the certificate is a software-calibration result, not observational evidence.

**Completion slice implemented (2026-10-10):** the inference certificate now
also profiles a representative SPARC hierarchy with mass-to-light, distance and
inclination nuisance draws, recovering nominal interval coverage. Pantheon
reports full-covariance whitened-residual diagnostics and a proper-prior
two-parameter marginal likelihood computed by deterministic quadrature. Direct
quadrature is used instead of stochastic nested sampling because the current
baseline has only two parameters and can therefore be marginalized more
accurately and reproducibly. The cross-engine certificate, exposed through
`emrf verify engines` and `GET /api/v1/verification/engines`, covers distributed
lens convergence, astrometry and high-redshift synthetic recovery, quantum
Compton limits and core-model invariance. `emrf predict --commit` and the gated
prediction REST API provide immutable metadata-only preregistration hashes.
The general nested SPARC golden tolerance is reduced from `5e-3` to `4e-3`.
Two explicitly named first-grid-point nuisance objectives retain `5e-3` after
hosted SciPy builds measured 0.43% drift; derived parameter summaries use the
tighter tolerance. Pantheon's platform-dependent quadrature error estimate is
reported but excluded from golden comparison, while the evidence value remains
gated.

Completed deliverables:

1. Known-limit test matrix for every engine (Newtonian, Schwarzschild,
   PPN, flat-LCDM vs astropy/CAMB, Bekenstein-Hawking).
2. Units at boundaries with `astropy.units`; constants from CODATA 2022.
3. Convergence-order tests for integrators and ray tracing.
4. Property-based tests for model invariants.
5. Stabilized legacy nested SPARC optimization with bounded Powell recovery,
   convergence failure handling, repeated-start agreement and a tighter
   `rtol=4e-3` general golden allowance.
6. Inference upgrades: deterministic proper-prior evidence quadrature for the
   current low-dimensional Pantheon baseline; SBC/injection-recovery for SPARC
   `a0` and its nuisance hierarchy; posterior-predictive residual checks.
7. Baseline zoo: GR+NFW halo, MOND-family RAR, LCDM run beside EMRF through
   the same likelihoods.
8. Evidence typing (`EvidenceClass`) on all outputs; retire legacy verdict
   strings behind a deprecation.
9. Pre-registration workflow (`emrf predict --commit`).

**Exit gate achieved:** every active engine family has an executable passing
known-limit, convergence, invariant or calibrated synthetic check with explicit
limitations; SPARC analyses report calibrated intervals; prediction
preregistration is operational; and the preservation gate retains all reviewed
golden scientific numbers. Derived CMB perturbation theory, higher-dimensional
Bayesian model expansion and additional real surveys are subsequent research
programs, not evidence silently inferred from Phase 5 software verification.

## Phase 6 - Interfaces v2 (2-3 weeks)

**Typed SDK foundation implemented (2026-10-10):** `emrf.sdk` now defines
immutable public request, response, error, run, dataset, verification and
prediction contracts. Command discovery and registered command execution are
the first shared application operations: direct Python, the compatibility CLI
and REST v1 call the same typed SDK client, while command execution continues
to produce the existing durable run records. Cross-interface parity tests lock
the v1 JSON shapes and legacy CLI behavior before further migration. Typed run
inspection and all three verification certificate families now use the same
SDK path as well.

**API v2 foundation implemented (2026-10-10):** a separate FastAPI ASGI
application exposes generated Pydantic/OpenAPI contracts for health, command
discovery and authenticated durable execution, run inspection, and all three
verification families. Mutating execution is disabled until
`EMRF_API_V2_TOKEN` is configured and then requires a constant-time-checked
bearer token. Flask REST v1 remains a separate, unchanged WSGI application.
Dependency ceilings are bounded to the FastAPI/Pydantic/HTTPX/Uvicorn
generations exercised by the cross-platform CI matrix; newer incompatible
generations require an explicit recertification rather than being accepted
silently.

**Durable jobs and artifact access implemented (2026-10-10):** the typed SDK
now supports submit, list, inspect, and cancel operations for the durable
queue. FastAPI v2 exposes the corresponding authenticated mutation endpoints
and read endpoints, including authenticated single-job worker execution, while
artifact listing and download require the same bearer token and enforce
run-root containment, regular-file checks, and symlink/path-traversal
rejection. Existing Flask v1 job behavior is unchanged.
The CI development constraints now include Schemathesis 3.39.16 and its
certified Hypothesis generation; read-only generated-contract tests exercise
the v2 generated OpenAPI document and the documented v1 contract without
fuzzing authenticated mutations.

1. `emrf.sdk` typed public API; CLI and API reimplemented as thin layers.
2. REST v2 with FastAPI + pydantic (generated OpenAPI), jobs, artifact
   download, token auth for mutating endpoints; v1 kept and tested. **Done.**
3. Schemathesis contract generation and response validation for safe read-only
   v1 and v2 OpenAPI operations in CI. **Done.** Authenticated mutation fuzzing
   remains intentionally excluded from ordinary CI.
4. JavaFX client: Maven wrapper with declared dependencies; remove vendored
   SDK/Maven from git (history kept); decide keep vs retire in favour of the
   web dashboard. **Done:** JavaFX remains a supported compatibility client,
   while the web dashboard is the recommended cross-platform UI. Java request
   construction and response mapping are tested on Java 17 in root CI.

**Client compatibility slice implemented (2026-10-11):** the Python 2D client
now has functional, mutually exclusive `--online` and `--offline` modes,
contract tests for REST v1 payloads, and tested local fallback. The JavaFX
client accepts a configurable API URL, has JUnit contract tests for payload and
response mapping, and builds through a pinned Maven Wrapper. The previously
committed 91 MiB Maven/JavaFX binary toolchains were removed from the current
tree because the wrapper and `pom.xml` now manage those dependencies.

**Remaining-family migration implemented (2026-10-11):** environment
diagnostics, dataset catalog/acquisition/integrity, local and off-site
backup/verification/restore drills, garbage collection, prediction
commitment/reveal verification, simulation, and run artifacts now have typed
SDK operations. The compatibility CLI and Flask REST v1 adapters call those
operations without changing their established response shapes or enablement
flags. FastAPI REST v2 exposes strict Pydantic contracts for every applicable
family, protects mutations with its bearer-token policy, and returns stable
SDK errors. Artifact containment, traversal, symlink and regular-file checks
now live in the authoritative SDK rather than an HTTP adapter.

**Phase 6 certification (2026-10-11):** direct SDK, CLI, Flask REST v1,
and FastAPI REST v2 parity/compatibility suites pass; the complete non-golden
suite passes 322 tests; Ruff, bytecode compilation and Pylance diagnostics are
clean. A clean wheel installed outside the source tree exposes all 20 migrated
SDK operations, executes doctor and simulation successfully, and generates
the expected 31-path OpenAPI document. Remote CI run `38126755336` passed all
13 jobs: Java 17, Windows/Linux Python 3.10/3.12, and all eight scientific
golden suites. REST v1 remains intentionally frozen: new artifact download and
worker execution are v2-only rather than additions to the compatibility API.

| Operation family | CLI | Typed SDK | REST v1 | REST v2 | Exit status |
|---|---:|---:|---:|---:|---|
| Command discovery/execution | Yes | Yes | Yes | Yes | Certified |
| Durable run list/detail | Yes | Yes | Yes | Yes | Certified |
| Durable job submit/list/detail/cancel/worker | Yes | Yes | Yes, except worker HTTP | Yes | Certified adapters |
| Physics/inference/engine verification | Yes | Yes | Yes | Yes | Certified |
| Run artifact list/download | Yes | Yes | Compatibility exclusion | Yes | Certified |
| Environment doctor | Yes | Yes | Yes | Yes | Certified |
| Dataset catalog/acquisition/integrity | Yes | Yes | Yes | Yes | Certified |
| Backup/restore/offsite drills | Yes | Yes | Yes | Yes | Certified |
| Prediction commitment/verification | Yes | Yes | Yes | Yes | Certified |
| Simulation model | Yes | Yes | Yes | Yes | Certified |
| Python/JavaFX/web visualization | Yes | Not applicable | REST v1 client | Not applicable | Certified |

**Exit gate:** CLI/API/SDK parity tests cover every operation; v1 clients
(including JavaFX and `visualize.py`) still work. **Passed 2026-10-11 and
cross-platform certified by remote CI run `38126755336`.**

## Phase 7 - Knowledge base, memory and library (2-3 weeks, then ongoing)

**Typed graph foundation implemented (2026-10-11):** `GRAPH_MEMORY.json` now
validates against a packaged JSON Schema 2020-12 contract and a semantic
validator that enforces unique/referentially valid nodes, acyclic inheritance,
legal overrides, and evidence-linked non-proposed claims. The migrated graph
classifies all 96 nodes into canonical kinds and qualifies all 113 edges with
confidence, evidence class and provenance. Pure-Python knowledge services
provide conditional claims, inheritance resolution, conflicts, pinned
DOI/arXiv/ADS source registration with snapshot hashes and BibTeX, atomic
query/export, and durable run/artifact evidence linking. Typed SDK, CLI and
authenticated FastAPI v2 mutation adapters share this service. CI invokes
`emrf kb validate`; UKS remains an unimplemented optional ADR-gated pilot.

**Phase 7 certification (2026-10-11):** all 333 local non-golden tests pass;
Ruff, focused mypy, bytecode compilation, Pylance diagnostics and dependency
consistency checks pass. A clean wheel installed outside the checkout
validated its portable 96-node seed, registered and queried a pinned
literature source, and generated all 37 REST v2 paths. Canonical and packaged
graph/schema hashes match. Independent review regressions cover concurrent
first-use initialization, installed portability, typed evidence endpoints,
terminal-run enforcement, post-publication artifact mutation and malformed
graph validation. Remote CI run `38145062641` passed all 13 jobs after rerunning
one isolated pre-existing Windows acquisition-lock test that also passed when
reproduced locally: Java 17, Windows/Linux Python 3.10/3.12, and all eight
scientific golden suites are green.

1. JSON Schema for `GRAPH_MEMORY.json`; validator in CI.
2. Automatic links: run -> results -> claims -> sources -> datasets.
3. Literature registry with DOI/arXiv/ADS, snapshots and BibTeX.
4. `emrf kb query|add-source|validate|export` and API endpoints.
5. Claim lifecycle: proposed, tested, supported, refuted, retracted.
6. Schema features adopted from the UKS assessment (spec section 13.13):
   `inherits_from` with overrides, regime-of-validity `conditions`,
   per-edge `confidence`, and `conflicts_with`.
7. Optional, ADR-gated: an `emrf kb export --format uks` exporter and a
   two-week Brain Simulator III pilot. Continue to suggestion import only
   if the pilot meets its success criterion.

**Exit gate:** every current claim links to evidence or is marked untested.
**Passed 2026-10-11 and cross-platform certified by remote CI run
`38145062641`.**

## Phase 8 - Documentation and support (2 weeks, then ongoing)

**Phase 8 implementation complete (2026-10-11):** the supported MkDocs site
now follows Diataxis and includes first-SPARC and knowledge tutorials,
installation/API/support how-tos, generated CLI and REST v2 reference,
SDK reference, evidence and physics explanations, architecture guidance,
extension boundaries and ADRs. CI rejects stale generated reference and
strict-build warnings; a dedicated GitHub Pages workflow publishes the site.
Structured software, scientific, feature and documentation issue forms route
work alongside enabled Discussions and private security reporting. The
reproducible Python 3.12/Java 17 dev container and expanded contribution,
support and security policies define the supported user and developer path.

`emrf doctor --report [FILE]` and the typed SDK now create a versioned,
privacy-sanitized diagnostic report without environment variables,
credentials, executable paths, run arguments or dataset URLs. Reports use
exclusive no-overwrite publication, durable synchronization, a hard-link-free
filesystem fallback and per-user application storage by default. Validation
error counts and structural locations are retained without copying raw
user-supplied values into the report.

**Local Phase 8 certification (2026-10-11):** all 433 non-golden tests pass
with one platform-conditional skip; dependency consistency, CI lint rules,
focused Ruff and mypy, deterministic generated-reference checks, strict
MkDocs build, JSON/YAML configuration validation and independent review pass.
A clean `0.9.1` wheel installed outside the checkout exposes the SDK support
contract and creates CLI/SDK reports with verified SHA-256 digests and
portable knowledge seeding. Review regressions cover invalid-graph privacy,
JSON-only CLI output, exclusive publication, existing destinations,
hard-link-free filesystems and default per-user placement. This established
the local gate before cross-platform remote certification.

**Phase 8 remote certification (2026-10-11):** CI run `38155737472`
passed all 15 jobs: Java 17, Windows/Linux Python 3.10/3.12, deterministic
documentation generation on Python 3.10 and 3.12, and all eight scientific
golden suites. Documentation run `38155737473` passed generated-reference and
strict-build checks and published the live site at
`https://kirklasalle.github.io/SpaceEntropyCompression/`. The first remote
attempt exposed an interpreter-dependent `argparse` positional-required flag;
the generator now derives requiredness from stable `nargs` semantics and has
cross-version regression coverage in CI.

1. Documentation site (Diataxis): tutorials (first SPARC result in 15
   minutes), how-tos, generated reference, physics explanations.
2. Issue templates, discussion forum, `emrf doctor --report`.
3. Dev container, CONTRIBUTING update, plugin tutorial, ADRs.

**Exit gate:** supported documentation is generated reproducibly and published;
diagnostic reports are privacy-safe, durable and installed-wheel compatible;
and user/developer contribution, support and architecture paths are explicit.
**Passed 2026-10-11 and cross-platform certified by CI run `38155737472`;
the live documentation was published by run `38155737473`.**

## Phase 9 - Release engineering and governance (1-2 weeks)

**Phase 9 implementation complete locally (2026-10-11):** the canonical package
version is `1.0.0` and Setuptools, runtime, CFF, CodeMeta, Zenodo-deposit
metadata, generated API reference and changelog metadata are synchronized by a
tested release validator. Release tooling now builds wheel and source
distributions, validates package metadata, produces a reproducible CycloneDX
1.6 SBOM, enforces a clean installed-environment `pip-audit`, generates
checksums, and creates GitHub Sigstore-backed attestations. All GitHub Actions
are immutable-SHA pinned. Dependabot, pull-request dependency review, OpenSSF
Scorecard/SARIF publication and scheduled supply-chain certification are
configured.

The tag workflow accepts only a semantic tag matching the canonical version,
requires the tagged commit to equal the current protected `main` head, reruns
the non-golden suite and all eight scientific golden jobs, and verifies
downloaded SPARC and Pantheon+ inputs against catalog-pinned byte counts and
SHA-256 hashes before publication. The existing Flask REST v1 and FastAPI REST
v2 JSON error handlers also retain transport-required headers under the
upgraded, vulnerability-free dependency set. The historical DOI
`10.5281/zenodo.23197308` remains explicitly historical and does not identify
1.0.0.

**Local Phase 9 certification (2026-10-11):** all 438 non-golden tests pass
with one platform-conditional skip and one golden deselection. Metadata and
tag validation, cross-version generated-reference checks on Python 3.10 and
3.12, strict MkDocs, correctness lint, focused Ruff and mypy, current
Actionlint, dependency consistency, a zero-vulnerability audit, and a
141-component validated CycloneDX SBOM pass. The final `1.0.0` wheel and sdist
pass Twine validation. An isolated wheel installation reports version 1.0.0,
passes doctor, exposes 47 typed SDK commands and 37 REST v2 OpenAPI paths, and
validates its portable packaged knowledge graph. Independent review found and
closed release-source, catalog-integrity and versioned-metadata-URL gaps.

**Remote Phase 9 pre-release certification (2026-10-11):** CI run
`38163055353` passed all 15 jobs across Java 17, Windows/Linux Python
3.10/3.12, both documentation interpreters and all eight scientific golden
suites. Documentation run `38163055269`, security/package run `38163055278`
and OpenSSF Scorecard run `38163055348` also passed; the dependency audit and
Dependabot report zero open vulnerabilities. The first remote attempt exposed
a Python 3.10-incompatible Hypothesis pin and a missing release-only PyYAML
dependency; corrected Python 3.10/3.12 resolution and standalone release
metadata validation passed before the successful replacement runs.

`main` now enforces strict up-to-date status from all 18 pull-request CI,
documentation, security/package and dependency-review contexts, requires pull
requests without an impossible solo-maintainer approval count, resolves
conversations, enforces linear history and administrator compliance, and blocks
force pushes and deletion. Main-only Pages deployment and Scorecard/SARIF
publication remain independently required by the release record rather than
being configured as impossible pull-request checks.

**Phase 9 release certification complete (2026-10-11):** protected `main`
commit `cdad211fa8a65ed61535f31a4681d82604b1c473` passed CI run
`38168041873`, documentation run `38168041844`, security/package run
`38168041934` and Scorecard run `38168041884`. The immutable annotated
`v1.0.0` tag points to that exact commit. Release run `38169063029` passed
source verification, non-golden validation, all eight catalog-verified golden
jobs, package/audit/SBOM generation, attestation and publication. The public
release contains eight assets; all seven entries in `SHA256SUMS`, all eight
GitHub attestations, both distributions, the zero-vulnerability 144-dependency
audit and the 144-component CycloneDX 1.6 SBOM were independently verified.
Zenodo archived 1.0.0 with the new version DOI
`10.5281/zenodo.23304395`; the historical version DOI remains distinct.
These gates certify engineering and reproducibility, not the physical truth of
EMRF hypotheses.

**Exit gate passed 2026-10-11.** EMRF 1.0.0 is released with protected-main
governance, reproducible supply-chain evidence, verified provenance and a
version-specific archival DOI.

1. Automated release: tests, golden results, SBOM (CycloneDX), pip-audit,
   CITATION/codemeta sync, changelog, signed artefacts, Zenodo DOI.
2. Branch protection and required checks; OpenSSF Scorecard.
3. Release EMRF 1.0.0 when Phases 1-7 gates are met.

## Phase 10 - Sustained operations and lifecycle maintenance (ongoing)

World-class research software must remain reproducible after its first formal
release. Phase 10 governs supported-runtime migrations, dependency renewal,
archival health, recovery rehearsals, and evidence-preserving maintenance.

**First lifecycle slice completed (2026-10-11):** all GitHub Actions have been
moved to current Node.js 24-compatible release lines with immutable commit pins.
CodeQL SARIF publication is on v4. Hosted runners are explicitly pinned to
Ubuntu 24.04 and Windows Server 2022 rather than migrating `latest` aliases.
Feature branches now run the expensive 15-job matrix only through
`pull_request`; protected `main` retains push certification. CI and security
workflows cancel superseded runs, while release publication remains
non-cancellable. Regression tests enforce immutable action pins and approved
versions, explicit runner images and matrices, non-duplicated branch validation,
and concurrency policy across both supported workflow-file extensions.

**First lifecycle slice remote certification (2026-10-11):** protected PR #14
passed the replacement CI and security checks after both review findings were
resolved, then merged by rebase as commit
`95bf735bcb2a51345821e33cd60856bfcef4a347`. Exact-main CI run `38179469801`,
documentation run `38179469808`, security run `38179469783`, and OpenSSF
Scorecard run `38179469833` all passed without deprecated Node.js 20, CodeQL v3,
or runner-migration warnings. Branch protection remains strict with 18 required
contexts; only the four runner-derived names changed, and administrator
enforcement, linear history, conversation resolution, and force-push/deletion
blocking remain enabled.

**Second lifecycle slice completed (2026-10-12):** a monthly and manually
dispatchable, read-only release-health rehearsal resolves an existing stable
annotated tag, requires its source commit, release URL and confirmed
post-publication DOI to match a protected archive registry, rebuilds its
distributions without publication, verifies complete release checksums and
exact tag/commit/workflow attestations, exercises the published wheel's doctor,
SDK, REST v2 OpenAPI and packaged knowledge in an isolated environment, checks
the version-specific DOI, and retains a 90-day machine-readable receipt.
Workflow-governance tests enforce its schedule, protected-main source, scoped
credentials, injection-safe input handling, read-only permissions,
non-cancellation, and non-publishing contract.

**Second lifecycle slice remote certification (2026-10-12):** protected PRs
#16, #17 and #18 established and hardened the rehearsal without moving or
republishing `v1.0.0`. The final implementation commit is
`f2cf336ea1d66d2a303248797320153de58a2c17`; exact-main CI run `38189552997`,
documentation run `38189553064`, security run `38189553039`, and OpenSSF
Scorecard run `38189553041` all passed. Manual release-health run `38189560943`
then passed every source-rebuild, checksum, provenance, isolated-wheel,
doctor, SDK, REST v2, knowledge and DOI check against certified release commit
`cdad211fa8a65ed61535f31a4681d82604b1c473`, and its downloaded 90-day receipt
was independently verified. Failed runs `38185094841` and `38187930382` remain
preserved as evidence of the post-tag DOI lifecycle boundary and the corrected
shell-parser defect rather than being hidden or deleted.

**Third lifecycle slice remotely certified (2026-10-12):** protected PR #21
merged as `bdbe16cdeaaae577f92ec29ffacb7aff80da368a`. The durable job queue
now assigns a persistent monotonic sequence and claims by that sequence,
including a serialized in-place migration for existing registries. This
preserves FIFO submission order when timestamps collide and removes random
identifier suffixes from scheduling semantics. The existing isolated data
restore drill now verifies the curated catalog, records phase timings and
catalog hashes, measures recovery-point age, rejects concurrent source changes,
enforces explicit five-minute drill objectives, and atomically retains success
or failure receipts. Operational RPO/RTO targets are defined for observations,
catalogs, runs, predictions, knowledge and release state. Review regressions
cover concurrent migration, source changes during recovery and interrupted
receipt writes. Issue #20 closed automatically when PR #21 merged. Exact-main
CI run `38256202517`, Documentation run `38256202171`, Security run
`38256202424` and OpenSSF Scorecard run `38256202902` then all passed.

**Fourth lifecycle slice remotely certified (2026-10-12):** protected PR #23
merged as `5fd8418f509cf89efa03d6a64b677ac5d4b9203a`. A versioned
application-state backup now takes a consistent SQLite snapshot of durable runs
and jobs, hashes every run artifact and prediction commitment, and preserves
the validated knowledge graph with its schema. Verification rejects tampering,
unsafe paths, false component summaries, malformed records and semantic
corruption. Exclusive destination reservations and final existence checks keep
backup and restore publication non-destructive under concurrent callers.
Restore requires a new isolated destination; the automated drill measures
one-hour RPO/four-hour RTO objectives, fails when the source changes, and
atomically retains success or failure receipts. The authoritative SDK now
powers matching CLI, Flask REST v1 and authenticated FastAPI REST v2 operations.
A supported-version and deprecation contract now covers Python, Java, SDK, CLI,
REST, stored schemas, datasets and scientific certificates. Exact-main CI run
`38278148172`, Documentation run `38278148218`, Security run `38278148336` and
OpenSSF Scorecard run `38278148473` all passed.

**Fifth lifecycle slice remotely certified (2026-10-12):** protected PR #25
merged as `4b6dad50ef63a8fa1838cfc45bd94f69eff943ce`. Versioned,
deterministic performance and resource baselines now cover a 512 x 512
covariance solve, 2,500 catalog records, 2,000 run artifacts and a 1,200-node
knowledge graph. Each workload records elapsed-time distributions, Python peak
allocation, fixture or native-array bytes, platform provenance and exact
scientific/software invariants. Complete runs are process-serialized, preserve
external tracing state, reject empty selections, and independently verify the
full artifact order. Deployment failures retain operational error semantics.
The authoritative SDK powers matching CLI, gated Flask REST v1 and
authenticated FastAPI REST v2 operations. A dedicated Ubuntu 24.04 / Python
3.12 CI job enforces evidence-based thresholds without changing physics,
tolerances or evidence classifications. The baseline update policy requires
before-and-after evidence, a new version and the complete golden matrix.
Exact-main CI run `38291473965`, Documentation run `38291474116`, Security run
`38291474025` and OpenSSF Scorecard run `38291474113` all passed.

**Sixth lifecycle slice remotely certified (2026-10-12):** protected PR #27
merged as `5fe33ffbf5220cc89246e68153ef23b6a5e015b5`. A read-only monthly and
manually dispatchable workflow now certifies controlled non-empty
observational and application state: one content-addressed holding, one durable
run with an artifact, one queued job, one prediction commitment and the
validated scientific knowledge graph. It executes both isolated recovery
drills and the standard performance baseline, continues independent checks
after an operational failure, and atomically retains individual and combined
JSON evidence for 90 days before failing closed. The workflow refuses any
commit other than current protected `main`, uses pinned actions and has no
publication permissions. First operational-certification run `38301619284`
passed on the merged commit; its downloaded receipt independently confirmed
both recovery domains, all non-empty component counts, the performance gate
and preserved scientific outputs. Exact-main CI run `38301598548`,
Documentation run `38301598347`, Security run `38301598342` and OpenSSF
Scorecard run `38301598266` all passed.

Planned sustained-operations increments:

1. Maintenance releases only through the protected release contract; new
   physics claims require preregistration and the existing evidence lifecycle.
2. Retain scheduled recovery, archive-health, security and performance
   evidence; investigate and preserve failed receipts before corrective reruns.

**First-slice exit gate:** the replacement checks must pass on the migration
pull request before the four runner-derived required contexts are atomically
changed from the old aliases to the pinned-runner names. The protected pull
request must then merge normally, and the exact merged `main` commit must pass
CI, documentation, security and Scorecard publication without Node.js 20,
CodeQL v3 or runner-migration warnings.

## Phase 11 - Evidence-qualified scientific challenges (in progress)

**SPARC quality-3 holdout completed (2026-10-12):** the protocol and exact
input/training hashes were frozen before outcome computation through protected
PR #29 and commitment `20261012T211327324282Z-d6ab49c9b4b7`. Protected PR #30
then added the manually dispatched, read-only analyzer with independent
population derivation, forward/reverse scans, complete optimizer diagnostics,
and separate scientific and operational gates. Its 19 CI and security checks
passed before the implementation merged as
`f09633b6bded2b239372dd76630b1e38d92e0992`.

Run `38315325901` executed that exact clean `main` revision. The retained
artifact is preserved unchanged as
`results/real_data_v1/sparc_q3_holdout_v1.json` (SHA-256
`87dea72269652bea6e24d03876dfe4c65075d7254031b2852e31a09add55231a`).
Independent checks confirmed a complete population of 10 Q=3 galaxies and 109
points, no missing or silently excluded targets, no protocol deviations, and
passing convergence and scan-order gates for both laws. The preregistered EMRF
screen was **rejected**: its `1.50e-10 m/s²` holdout minimum lies outside the
frozen `[1.55781092394229e-10, 1.60831784955957e-10] m/s²` interval. The RAR
comparator screen was also **rejected**: its `1.15e-10 m/s²` minimum lies
outside `[1.22152425035699e-10, 1.2557224809968e-10] m/s²`. These are
conditional same-catalogue lower-quality holdout outcomes, not calibrated
significance, blind discovery, or independent replication.

---

## Risk register

| Risk | Mitigation |
|---|---|
| Migration changes a published number | Golden harness in Phase 1 precedes all moves |
| Breaking hash-pinned evidence | Never edit pinned files silently; new manifest version per change |
| Licence violation in data library | Catalog records licence; redistribution flag enforced by `emrf data export` |
| Scope creep | Each phase has a gate; physics extensions wait for Phase 4 |
| Single-maintainer bus factor | Docs, ADRs, CI and dev container make the project transferable |
| Remote execution abuse | Disabled by default; token auth in v2; no shell |

## Immediate next steps

1. Continue scientific work only through preregistered predictions,
   independently traceable observations and evidence-qualified claims.
2. Execute maintenance releases only through the protected release contract
   and retain periodic recovery, archive-health and performance evidence.
3. Treat every failed scheduled certification as durable incident evidence;
   correct its root cause through protected `main` before rerunning it.
