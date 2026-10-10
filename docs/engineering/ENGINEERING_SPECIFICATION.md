# EMRF Engineering Specification: World-Class Formalization

| Field | Value |
|---|---|
| Document | Target engineering specification (normative) |
| Date | 2026-10-09 |
| Owner | Kirk LaSalle |
| Baseline | [Current Build Reference](CURRENT_BUILD_REFERENCE.md) |
| Execution | [Formalization Implementation Plan](FORMALIZATION_IMPLEMENTATION_PLAN.md) |
| Status | Proposed, for owner approval |

The words MUST, SHOULD and MAY are used as in RFC 2119.

---

## 1. Mission and quality goals

EMRF shall be research software of reference quality for testing
gravitational and emergent-matter hypotheses against real observations:
trustworthy in its numbers, honest in its claims, safe with data,
reproducible by strangers, and extensible by other scientists.

| Goal | Measurable target |
|---|---|
| Scientific correctness | Every physics engine recovers its known limits (Newtonian, Schwarzschild, flat-LCDM, Bekenstein-Hawking) within documented tolerances; verified by automated tests |
| Reproducibility | Any published number can be regenerated from a run record (code commit + environment lock + input hashes + config + seed) with one command |
| Data integrity | Zero silent data changes: every observational byte is content-addressed, hash-verified on read, never modified in place |
| Robustness | No data loss under crash, kill, power loss, disk full or network failure; all writes atomic; interrupted runs resumable |
| Interface completeness | Every capability available through CLI, REST API and Python SDK, with tested parity |
| Maintainability | Ruff and strict mypy clean on all library code; >= 90% line and >= 80% branch coverage on library code |
| Supply-chain safety | Hash-locked dependencies, SBOM per release, zero known high-severity vulnerabilities at release |
| Usability | New user from clone to first verified SPARC result in < 15 minutes using documented steps |
| Openness | FAIR4RS principles; citable releases (Zenodo DOI), CITATION.cff, codemeta.json kept in sync automatically |

Reference standards: ISO/IEC 25010 (software quality model), IEEE 1012
(verification and validation), FAIR Principles for Research Software
(FAIR4RS, 2022), Scientific Python SPEC 0 (dependency support windows),
pyOpenSci and JOSS review criteria, OpenAPI 3.1, Keep a Changelog and
Semantic Versioning, CycloneDX SBOM, OpenSSF Scorecard.

## 2. Non-negotiable invariants

1. **Preservation.** No existing capability is removed. Legacy entry points
   remain as thin shims until a documented deprecation window (two minor
   releases) expires.
2. **Evidence honesty.** Synthetic, illustrative and observational results
   are typed differently in code and cannot be confused in outputs. Software
   test passes are never reported as physical confirmation.
3. **Fail closed.** Missing provenance, hash mismatch, unit mismatch,
   non-finite inputs or unconverged numerics MUST stop the computation with
   a typed error, never produce a silently degraded number.
4. **Immutability of observations.** Raw data is write-once.
   Derived data records the hashes of everything it was derived from.
5. **Determinism.** Given the same run record, results are bit-identical on
   the same platform and within stated tolerances across platforms.

## 3. Target architecture

### 3.1 Layered package

A single importable namespace `emrf` replaces the flat module layout. Lower
layers never import higher ones (enforced by `import-linter`).

```text
emrf/
  core/          units, constants (CODATA 2022 via astropy), errors, typing, numerics guards, atomic I/O
  physics/       model plugins: emrf (Candidate A), gr, newtonian, mond, lcdm baselines
    engines/     cosmology, cmb, lensing, horizons, astrometry, rotation curves
  data/          library: catalog, content-addressed store, fetchers, readers, verifiers, schemas
  inference/     likelihood protocol, priors, samplers (adapters), model comparison, diagnostics
  validation/    regime harness, stress tests, known-limit checks, injection-recovery, SBC
  runs/          run records, provenance capture, checkpoints, job queue, result registry
  knowledge/     graph memory, literature/source registry, claim ledger, evidence status
  interfaces/
    cli/         `emrf` command (current emrf_cli.py migrates here)
    api/         REST service (v1 kept; v2 with generated OpenAPI)
    sdk/         stable public Python API (`emrf.sdk`)
  viz/           figures, Plotly, web dashboard assets
legacy/          shims preserving every current script path and CLI flag
```

### 3.2 Plugin model

Third parties extend EMRF without modifying it, via Python entry points:

| Entry-point group | Contract |
|---|---|
| `emrf.models` | `PhysicsModel` protocol: `parameters`, `predict(observable, inputs, theta) -> Quantity`, declared `regimes`, declared `known_limits` |
| `emrf.datasets` | `DatasetSpec`: id, version, sources, licence, citation, `fetch()`, `load() -> typed table/array`, `verify()` |
| `emrf.likelihoods` | `Likelihood`: binds a dataset and an observable; `loglike(theta)`, covariance handling, nuisance parameters |
| `emrf.checks` | Validation checks returning a typed `CheckResult` with evidence class |

Every model, including EMRF itself, is run beside GR/Newtonian, MOND-family
and LCDM baselines through the same likelihoods, so comparisons are always
like-for-like.

### 3.3 Evidence typing

```python
class EvidenceClass(Enum):
    OBSERVATIONAL = "observational"      # verified real data, real likelihood
    PUBLISHED_SUMMARY = "published"      # collaboration likelihood or compressed statistic
    SYNTHETIC = "synthetic"              # fixtures, injection tests
    ILLUSTRATIVE = "illustrative"        # prescribed maps, demonstrations
    SOFTWARE = "software"                # code correctness only
```

All results carry an `EvidenceClass`; reports and API responses display it.
The lowest class among inputs propagates to the output.

## 4. Data management, library and memory

### 4.1 Observational data library

| Component | Specification |
|---|---|
| Catalog | `knowledgebase/library/data_catalog.json` (human-curated sources) plus a SQLite registry `data/library.sqlite` (WAL mode) of holdings |
| Store | Content-addressed: `data/store/sha256/ab/cdef...` ; filenames are views (hard links or small pointer files) |
| Acquisition | Streaming download to `*.part`, resumable (HTTP Range), size and SHA-256 checked, then atomic rename; mirrors and pinned commits for Git-hosted releases |
| Verification | On every read (fast path: size + mtime cache; full re-hash on demand and in CI) |
| Metadata | Per dataset: id, version, provider, URLs, retrieval time, licence, citation (DOI/bibcode), size, hash, schema, units, known systematics, evidence class |
| Formats | Raw kept verbatim; derived tables as Parquet, arrays/covariances as HDF5 or `.npy` with sidecar JSON |
| Deduplication | Identical bytes stored once (the current three 33 MB covariance copies become one object) |
| Backup | 3-2-1 rule: working copy, local backup, off-site (Zenodo for redistributable derived data; institutional or cloud object store for the rest). `emrf data backup` and `emrf data restore --verify` |
| Large data | Datasets above 1 GB fetched lazily per subset (astroquery/TAP queries recorded as reproducible query specs) |
| Licences | The library never redistributes data whose licence forbids it; the catalog records licence and redistribution rights |

### 4.2 Knowledge base and memory

* `GRAPH_MEMORY.json` becomes a validated schema (JSON Schema 2020-12) with
  node types: concept, equation, dataset, source (paper), software, model,
  run, result, claim, decision. Edges carry provenance and evidence class.
* Every result produced by a run is linked automatically to its run record,
  datasets and model version.
* Literature registry: DOI/arXiv/ADS bibcode, retrieval snapshot hash,
  BibTeX, and which claims cite it.
* `emrf kb query`, `emrf kb add-source`, `emrf kb validate` and the
  matching API endpoints manage it.
* The schema also supports inheritance with overrides, conditional
  (regime-of-validity) claims, per-edge confidence and explicit conflicts.
  These are adopted from the UKS assessment in section 13.13. An external
  UKS integration remains an optional plugin.

## 5. Reliability and graceful recovery

| Hazard | Required behaviour |
|---|---|
| Crash or kill during write | All writes go to temp file + `fsync` + atomic `os.replace`; manifests and registries use SQLite transactions or append-only journals |
| Crash during long run | Periodic checkpoints (sampler state, completed galaxies); `emrf run --resume <run-id>` continues; no partial results are published |
| Network failure | Bounded retries with exponential backoff and jitter; resume partial downloads; clear offline mode using local library |
| Disk full / permission denied | Pre-flight space check from catalog sizes; typed `StorageError`; nothing corrupted |
| Corrupted or tampered data | Hash mismatch quarantines the object, refetches from the pinned source, never uses it |
| Numerical failure | Guards for NaN/Inf, overflow, ill-conditioned covariances (condition number, Cholesky with jitter policy logged), non-convergence (sampler R-hat, ESS, evidence error) produce typed errors |
| Concurrent runs | File locks on store writes; SQLite WAL; run directories namespaced by run ID |
| Dependency drift | Locked environment; `emrf doctor` reports mismatch against the lock |

### 5.1 Durable run and queue implementation

`emrf.runs.RunStore` stores each run in a namespaced directory under the
managed application root. `run.json` is the durable source of truth;
`config.toml` is immutable; checkpoints and captured logs use temporary files,
`fsync` and atomic replacement. The SQLite WAL registry is a rebuildable index
and reconciles from run JSON on initialization. Run directories are staged
under non-public temporary names and atomically promoted only after both
metadata files are complete.

Queued commands use transactional claims and bounded worker leases. An expired
lease is requeued only while attempts remain; expiry after the final allowed
attempt is a terminal failure. REST submission, cancellation and resumption
are off by default with command execution and require
`EMRF_API_ALLOW_RUN=1`. Interactive and service commands cannot be queued or
resumed remotely.

Checkpoint-aware pipelines read `EMRF_RUN_ID`, `EMRF_RUN_DIR`,
`EMRF_RUN_ATTEMPT` and `EMRF_CHECKPOINT_DIR`. Checkpoints are optimization
state, not evidence by themselves; only an atomically published terminal
result from a successful run may be treated as a result artifact.

Error taxonomy (`emrf.core.errors`): `ProvenanceError`, `IntegrityError`,
`UnitError`, `NumericalError`, `ConvergenceError`, `StorageError`,
`NetworkError`, `ConfigError`. CLI exit codes and API status codes map
one-to-one onto these classes.

## 6. Verification and validation

### 6.1 Software verification

| Layer | Practice | Tooling |
|---|---|---|
| Static | Lint, format, strict typing, layer rules | ruff, mypy `--strict`, import-linter |
| Unit | Fast, isolated, offline | pytest, pytest-xdist |
| Property | Invariants over generated inputs (symmetry, monotonicity, scaling, unit invariance) | hypothesis |
| Contract | CLI/API/SDK parity; OpenAPI schema conformance | schemathesis, parity tests |
| Integration | End-to-end pipelines on cached real data | pytest markers `real_data` |
| Golden results | Current `results/` numbers reproduced within tolerance | snapshot comparison |
| Mutation | Tests actually detect injected faults | mutmut (scheduled, not per commit) |
| Fuzz | Parsers (MRT, Pantheon, covariance) and API payloads | hypothesis, atheris (optional) |
| Fault injection | Kill mid-write, disk full, network drop, corrupted bytes | dedicated `resilience` suite |
| Coverage | >= 90% lines, >= 80% branches on `emrf/` | coverage.py |
| Platforms | Windows, Linux, macOS; Python 3.11-3.13 | CI matrix |

### 6.2 Mathematical and computational verification

* **Known-limit recovery** for every engine (weak-field Newtonian,
  Schwarzschild perihelion and light bending, flat-LCDM distances against
  CAMB/CLASS/astropy.cosmology, Bekenstein-Hawking entropy).
* **Dimensional analysis** enforced at module boundaries with
  `astropy.units`; hot loops may use plain floats in SI after a checked
  conversion.
* **Convergence tests**: grid/step refinement shows the expected order of
  accuracy (Richardson extrapolation) for ODE/quadrature/ray tracing.
* **Conservation and symmetry checks** where they apply (energy, angular
  momentum, Bianchi-identity-derived constraints).
* **Cross-code comparison** with independent implementations (CAMB, CLASS,
  astropy.cosmology, published SPARC fits).
* **Floating-point hygiene**: compensated summation where needed, log-space
  likelihoods, Cholesky solves rather than inverses, condition numbers logged.

The executable Phase 5 foundation certificate is exposed identically through
`emrf verify physics --json` and `GET /api/v1/verification/physics`. Each check
returns its measured value, independent reference, unit, tolerance, relative
error, evidence class and any scientific limitation. A report may therefore
contain mixed `software` and `illustrative` evidence; passing a calibrated
template consistency check never upgrades it to an independent prediction.
The detailed engine inventory and remaining verification gaps are tracked in
`SCIENTIFIC_VERIFICATION_MATRIX.md`; a missing check is reported as pending,
never inferred to pass from unrelated regression coverage.

The executable inference certificate is exposed through `emrf verify
inference --json` and `GET /api/v1/verification/inference`. It uses 64
deterministic realizations to measure standardized ensemble bias, nominal
68.27% interval coverage, posterior-predictive residual scale, boundary
avoidance and repeated-start agreement for representative SPARC and
Pantheon-like designs. The certificate calls the same scaled SPARC fitter and
full-covariance Pantheon profile used by the analysis software. All checks are
typed `synthetic`, and the report explicitly states that passing does not
constitute observational evidence for EMRF.

### 6.3 Scientific validation (statistics)

* **Injection-recovery**: inject a known signal into real-noise realizations
  and show the pipeline recovers it with calibrated uncertainty.
* **Simulation-based calibration (SBC)** for every Bayesian inference.
* **Blind analysis and pre-registration**: predictions are hash-committed
  into the run registry before the confronting data is loaded.
* **Model comparison** with Bayesian evidence (nested sampling), information
  criteria and cross-validation; look-elsewhere corrections when scanning.
* **Posterior predictive checks** and residual diagnostics per dataset.
* **Systematics**: nuisance parameters for distance, inclination,
  mass-to-light, calibration; robustness to influential objects (the existing
  UGC 06787 sensitivity is the model for this).

## 7. Dependency management

### 7.1 Policy

* Runtime environment fully locked with hashes (`uv lock` or `pip-tools
  --generate-hashes`); `conda-lock` file for users needing compiled stacks.
* Support window follows SPEC 0. Recommended interpreter: Python 3.12
  (3.11 minimum); move off 3.10.0.
* Weekly automated update PRs (Dependabot/Renovate); each must pass the full
  suite and golden results.
* `pip-audit` and OSV scanning in CI; CycloneDX SBOM attached to releases.
* Every dependency has an owner-approved entry in
  `knowledgebase/library/software_catalog.json` with purpose and licence.

### 7.2 Dependency tiers

| Tier | Packages | Rationale |
|---|---|---|
| Core numeric | numpy, scipy | Foundation |
| Astronomy | astropy (units, constants, cosmology, tables, FITS), astroquery | Community standard; replaces hand-written constants |
| Data | pyarrow (Parquet), h5py, pooch (optional) | Columnar and array storage, cached fetch |
| Inference | emcee, nautilus or dynesty, getdist, cobaya (optional extra) | Proven samplers and evidence |
| Cosmology (optional extra) | camb, classy | Cross-code verification and CMB |
| Interfaces | Flask (v1), FastAPI + pydantic (v2), uvicorn | Schema-generated API |
| Visualization | matplotlib, plotly | Existing |
| Dev | pytest, hypothesis, coverage, ruff, mypy, import-linter, schemathesis, mutmut, pip-audit | Quality gates |

### 7.3 Build versus buy

Write from scratch (domain specific, small, critical to trust):
content-addressed data store; dataset catalog and verifier; run-record and
provenance capture; evidence typing; likelihood and model protocols;
regime/validation harness; knowledge-graph schema and tools.

Do not write from scratch (mature, heavily verified upstream): units and
constants, cosmological Boltzmann solvers, samplers, FITS/HDF5/Parquet I/O,
HTTP servers, cryptographic hashing.

## 8. Interfaces

* **CLI** `emrf`: noun-verb groups (`data`, `run`, `model`, `check`, `kb`,
  `report`, `serve`, `doctor`); `--json` on every command; stable exit codes.
* **REST API**: `/api/v1` frozen and maintained; `/api/v2` generated from
  pydantic models (OpenAPI cannot drift), long jobs as `POST /jobs` returning
  a job ID with `GET /jobs/{id}` status, logs and artefacts; token
  authentication for mutating endpoints; CORS restricted by configuration.
* **Python SDK** `emrf.sdk`: the same operations as typed functions; the CLI
  and API are thin layers over it, guaranteeing parity.
* **Configuration**: one validated TOML file per run, recorded in the run record.

## 9. Observability

Structured JSON logs with run ID and correlation ID; run timeline
(start, checkpoints, end, resources); optional OpenTelemetry export for
service deployments; `emrf runs list/show/diff`.

## 10. Security

Mutating API endpoints require authentication and are off by default; no
shell execution; path-traversal-safe file access restricted to the library;
dependency and secret scanning in CI; signed release artefacts (Sigstore).

## 11. Documentation and support

* Documentation site (MkDocs Material or Sphinx) following the Diataxis
  model: tutorials, how-to guides, reference (auto-generated from
  docstrings and OpenAPI), explanation (physics and statistics).
* Physics documentation: every equation implemented links to its derivation
  note and source paper; every engine page lists known limits and tests.
* User support: issue templates (bug, data request, physics question),
  discussion forum, `emrf doctor --report` bundle for bug reports.
* Developer support: CONTRIBUTING, architecture decision records
  (`docs/adr/`), plugin tutorial, dev container, pre-commit hooks.

## 12. Release and governance

Semantic versioning; deprecation policy (two minor releases); release
checklist automated in CI (tests, golden results, SBOM, CITATION/codemeta
sync, changelog, Zenodo DOI); protected `main` with required reviews and
checks; ADR for every architectural decision.

---

## 13. Architect's recommendations: how I would build EMRF

These are my own recommendations as the software and physics architect for
this formalization, offered for your decision. They go beyond the minimum
specification above.

### 13.1 Make the run record the atom of science

Every number the project ever reports should be the output of a run record:
code commit, locked environment hash, input dataset hashes, configuration,
random seeds, platform, wall time, and evidence class, stored in
`runs/<run-id>/` and indexed in SQLite. Papers, figures and the knowledge
graph should cite run IDs, not files. This one decision makes the project
reproducible, auditable and resistant to the "old verdict string" problem
the project has already had to correct.

### 13.2 Separate physics, data and inference completely

A physics model should only answer "what does this theory predict for this
observable given these inputs and parameters". A dataset only answers "what
was measured, with what covariance". A likelihood joins them. A sampler
explores parameters. Keeping these four apart is what lets EMRF, GR,
MOND-family and LCDM be confronted with identical data through identical
code, which is the strongest possible scientific comparison.

### 13.3 Always run the baselines

Every confrontation with data should automatically include the standard
models as controls. A hypothesis looks meaningful only relative to how GR+dark
matter, LCDM and MOND-family fits perform on exactly the same inputs and
nuisance parameters.

### 13.4 Use the community's verified engines where they exist

For cosmology I would implement Candidate A as a Cobaya `Theory` component
and use CAMB/CLASS for the standard background and perturbations. This gives
access to the official Planck, ACT, DESI and Pantheon+/DES-SN likelihoods
already maintained by the collaborations, rather than re-implementing them.
For galaxy dynamics (SPARC, wide binaries), a native EMRF likelihood is
appropriate because no community framework covers it as well.

### 13.5 Pre-register predictions

Before confronting a new dataset, the model's prediction (with parameters
fixed from other data) should be computed and its hash committed. This is
the cleanest defence against unconscious tuning, and it is how a novel
theory earns credibility with referees.

### 13.6 Calibrate the statistics, not just the code

The current SPARC analysis is penalised profiling; STATUS correctly notes
that profile widths are not calibrated significances. I would add nested
sampling for evidence, simulation-based calibration and injection-recovery
before any claim of detection or exclusion is made.

### 13.7 Choose boring, durable storage

SQLite (WAL mode) for catalogs, run registry and job queue; Parquet for
tables; HDF5 or `.npy` for arrays; a content-addressed directory for raw
bytes. All are single-file or directory formats that survive decades,
need no server, and can be backed up with ordinary tools.

### 13.8 Modernise the toolchain

Python 3.12, `uv` for environments and locks, a single `pyproject.toml`
with extras (`[api]`, `[cosmo]`, `[viz]`, `[dev]`), GitHub Actions CI on
Windows/Linux/macOS, and a dev container so contributors get an identical
environment. Remove vendored Maven/JavaFX from git and use the Maven wrapper
with declared dependencies; consider retiring the JavaFX client in favour of
the web dashboard, which reaches more users with one code base.

### 13.9 Generate the API from types

Move to FastAPI + pydantic for API v2 so that the OpenAPI document, request
validation and SDK client are generated from one set of types. Keep v1
running unchanged for existing clients.

### 13.10 Treat the knowledge base as a typed graph

Validate `GRAPH_MEMORY.json` against a schema, link every claim to the run
records and sources that support it, and give each claim an evidence class
and status (proposed, tested, supported, refuted, retracted). Over time this
becomes the project's living, citable scientific memory.

### 13.11 Physics priorities I would pursue

1. Write the Candidate A action or field equations in covariant form and
   derive, symbolically (SymPy) and numerically, its weak-field limit, PPN
   parameters (gamma, beta) and gravitational-wave speed. These are the
   strongest, cheapest falsification tests (Cassini, LLR, GW170817).
2. Confront the radial acceleration relation with SPARC under full
   marginalisation, then test with independent samples (e.g., THINGS,
   LITTLE THINGS, Gaia wide binaries) without retuning.
3. Only then move to cosmology through Cobaya with Pantheon+, DES-SN5YR,
   DESI DR2 BAO and Planck/ACT CMB likelihoods.
4. Treat lensing (KiDS/DES/HSC, cluster mass maps) as an independent check
   on any modification of the gravitational potential.

### 13.12 Things I would deliberately not do

* Re-implement samplers, Boltzmann codes or unit systems.
* Report software test counts as scientific evidence.
* Download every large survey wholesale; record reproducible queries and
  fetch subsets.
* Merge unreviewed changes into hash-pinned evidence files.

### 13.13 Assessment: UKS (Universal Knowledge Store) as memory/knowledge base

Status: **assessed 2026-10-09; recommended as an optional, non-authoritative
reasoning plugin only.** Requires an ADR before any implementation.

**What it is.** The UKS is the core of Brain Simulator III (FutureAI /
Future AI Society, Charles Simon; MIT licence;
<https://github.com/FutureAIGuru/BrainSimIII>). It is a graph of "Things"
joined by typed "Relationships" (the type is itself a Thing), with
inheritance plus exceptions, "Clauses" that make one relationship
conditional on another, and tolerance of conflicting information. Agents
("modules") are written in C# or Python and run inside the Brain Simulator
host on Windows or macOS. Knowledge can be saved to and loaded from text
files.

#### First assessment

UKS is an AI common-sense store, not a scientific record. It has no built-in
content hashing, run records, W3C PROV lineage, units, uncertainties,
covariances or versioned schema. It runs on .NET and has a small community.
It cannot be EMRF's system of record.

#### Second assessment: value

On a second look, three UKS features map onto real problems in theory
development better than a plain graph does:

| UKS feature | Physics use in EMRF | Value |
|---|---|---|
| Inheritance with exceptions | Theory taxonomy: "MOND-family models predict asymptotically flat rotation curves"; Candidate A inherits that but overrides the screening behaviour. Store only what makes a model unique. | High |
| Clauses (conditional facts) | Regimes of validity: "prediction P holds IF g << a0", "tension with Cassini IF no screening". Most physics claims are conditional, and the current graph cannot express this. | High |
| Conflicting information | Competing measurements and claims (e.g. H0 tension, wide-binary results that disagree) can coexist, each with its own source, instead of being overwritten. | Medium |
| Agent modules | Automated "what follows from what" exploration, e.g. flagging claims that inherit from a refuted parent. | Medium, exploratory |

What it adds is the ability to reason over *concepts and assumptions*. It
adds nothing to data storage, statistics or reproducibility, where the
planned stack (section 4) is already stronger.

#### Second assessment: usability

* It does not work as a library. Python agents run inside the Brain Simulator
  host, so EMRF cannot `import` UKS from the CLI, the API or headless Linux
  CI. Integration must go through files or a bridge.
* Its text format is not a published standard and may change between
  releases. Any adapter must pin a UKS commit and test against a fixture.
* It adds a second runtime (.NET plus the GUI host) and goes against the
  managed-dependency policy (section 7) if it becomes a required dependency.
* There is no query language or schema validation, so integrity checks stay
  in EMRF.

#### Verdict

Take the ideas now. Treat the tool as an optional plugin to adopt later, and
only if a pilot shows it adds something.

#### Implementation, if adopted

1. **Adopt the concepts natively (no UKS dependency, Phase 7).** Extend the
   `GRAPH_MEMORY.json` schema (section 4.2) with:
   - an `inherits_from` edge, resolved with explicit `overrides`;
   - a `conditions` list on claims and predictions, holding regime-of-validity
     clauses with typed parameters and units;
   - `confidence` and `evidence_class` on every edge;
   - a `conflicts_with` edge that keeps both sides and their sources.

   Implement resolution in `emrf.knowledge` in pure Python, with unit tests.
   This gives most of UKS's value at zero runtime cost.
2. **One-way exporter (optional extra `emrf[uks]`).** Run with
   `emrf kb export --format uks --out kb.uks.txt`. The mapping is:

   | EMRF graph | UKS |
   |---|---|
   | Nodes (concept, model, claim, dataset, source) | Things |
   | Edges | Relationships, with the edge type as a Thing |
   | `conditions` | Clauses |
   | Hashes, DOIs, run IDs | Attribute Things, so traceability survives the round trip |

   Exports are read-only snapshots and carry the source graph hash.
3. **Pilot (time-boxed, about 2 weeks).** Load the export into a pinned Brain
   Simulator III build. Write one Python agent that propagates refutations
   and finds conditional conflicts. Success criterion: it surfaces at least
   one useful inference that `emrf kb query` cannot already produce. If it
   does not, stop at step 1.
4. **Controlled import of suggestions (only if the pilot succeeds).**
   UKS-derived inferences come back through `emrf kb import-suggestions`.
   They are stored as `proposed` claims with
   `evidence_class: "machine-inference (UKS)"`. They are never promoted
   automatically and need human review, consistent with the evidence-honesty
   invariant (section 2).
5. **Governance.**
   - Record the decision in an ADR.
   - Add UKS to `knowledgebase/library/software_catalog.json` with its pinned
     commit and licence.
   - Keep the adapter in a plugin package so the core never imports it.
   - CI tests only the exporter, against a golden-file fixture; the GUI host
     is not needed.
