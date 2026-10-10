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
The nested SPARC golden tolerance is reduced from `5e-3` to `1e-3`.

Completed deliverables:

1. Known-limit test matrix for every engine (Newtonian, Schwarzschild,
   PPN, flat-LCDM vs astropy/CAMB, Bekenstein-Hawking).
2. Units at boundaries with `astropy.units`; constants from CODATA 2022.
3. Convergence-order tests for integrators and ray tracing.
4. Property-based tests for model invariants.
5. Stabilize legacy nested SPARC optimization across CPUs (deterministic
   parameterization, convergence diagnostics and repeated-start agreement);
   reduce its temporary `rtol=5e-3` golden allowance.
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

1. `emrf.sdk` typed public API; CLI and API reimplemented as thin layers.
2. REST v2 with FastAPI + pydantic (generated OpenAPI), jobs, artefact
   download, token auth for mutating endpoints; v1 kept and tested.
3. Schemathesis contract fuzzing of both API versions in CI.
4. JavaFX client: Maven wrapper with declared dependencies; remove vendored
   SDK/Maven from git (history kept); decide keep vs retire in favour of the
   web dashboard.

**Exit gate:** CLI/API/SDK parity tests cover every operation; v1 clients
(including JavaFX and `visualize.py`) still work.

## Phase 7 - Knowledge base, memory and library (2-3 weeks, then ongoing)

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

## Phase 8 - Documentation and support (2 weeks, then ongoing)

1. Documentation site (Diataxis): tutorials (first SPARC result in 15
   minutes), how-tos, generated reference, physics explanations.
2. Issue templates, discussion forum, `emrf doctor --report`.
3. Dev container, CONTRIBUTING update, plugin tutorial, ADRs.

## Phase 9 - Release engineering and governance (1-2 weeks)

1. Automated release: tests, golden results, SBOM (CycloneDX), pip-audit,
   CITATION/codemeta sync, changelog, signed artefacts, Zenodo DOI.
2. Branch protection and required checks; OpenSSF Scorecard.
3. Release EMRF 1.0.0 when Phases 1-7 gates are met.

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

1. Review the three engineering documents and the library catalog.
2. Approve or adjust the architect's recommendations (spec section 13).
3. Commit Phase 0 and tag the baseline.
4. Approve the Phase 3 priority datasets for download (licence and disk size
   are listed in the catalog).
5. Commit the Phase 0/1 foundation and run the GitHub Actions matrix.
6. Close the Phase 1 exit gate, then start Phase 2.
