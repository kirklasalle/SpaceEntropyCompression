# EMRF Current Build Reference (as-built baseline)

| Field | Value |
|---|---|
| Document | Current build reference, frozen baseline before formalization |
| Date | 2026-10-09 |
| Git baseline | `7f5e4a4` on `main` (plus the CLI/API layer described in section 6) |
| Software version | 0.9.1 (`emergent_matter_model/emrf_version.py`) |
| Public API version | v1 (OpenAPI contract 1.1.0) |
| Python | 3.10.0 in `emergent_matter_model/.venv` |
| Companion documents | [Engineering Specification](ENGINEERING_SPECIFICATION.md), [Implementation Plan](FORMALIZATION_IMPLEMENTATION_PLAN.md), [Library catalog](../../knowledgebase/library/README.md) |

This document records what exists and how it is built **today**. It is the
reference that the formalization program must preserve: every capability
listed here must still work, with the same results, after each migration step.

---

## 1. Purpose and scientific scope

The Emergent Matter Research Framework (EMRF) is research software that
tests a space-entropy-compression hypothesis about emergent matter and
gravity against public observations. Its current scientific position is
documented in [STATUS.md](../../STATUS.md) and the [model card](../../MODEL_CARD.md):

* Candidate A (description within GR) is the selected research direction.
* Real-data analyses exist for SPARC rotation curves, Pantheon+ (full
  STAT+SYS covariance) and DESI DR1 BAO baselines.
* Many "stress tests" are software checks of prescribed or synthetic inputs,
  not observational confirmations. This distinction must be preserved.

## 2. Repository layout

| Path | Size | Role |
|---|---|---|
| `emergent_matter_model/` | 83 files, 0.5 MB | Python source (flat module layout), tests, server, JavaFX client |
| `tools/` | 15 scripts | Pipelines, audits, report/paper/notebook builders, HTML visualizer |
| `data/synthetic/` | 20 files | Code-test fixtures, each with a `# SYNTHETIC DATA` banner |
| `data/cosmology/` | 1 file | `desi_2024_bao.csv` summary table |
| `data/external/` | 203 files, 69 MB | Downloaded observations (git-ignored, local only) |
| `results/` | 21 files | Machine-readable outputs of real-data runs |
| `knowledgebase/` | 19 files + `library/` | Theory notes, `GRAPH_MEMORY.json`, claim ledgers, data/software library |
| `docs/` | 93 files, 59 MB | Audits, protocols, papers, archive, media |
| `paper/` | 39 files | LaTeX sources, figures, compiled PDF |
| `notebooks/` | 1 notebook | `emrf_two_regime_validation.ipynb` |
| `resources/javafx-sdk-24.0.2/` | 102 tracked files | Vendored JavaFX SDK |
| `tools/apache-maven/` | 40 tracked files | Vendored Maven 3.9.6 |

Language mix: 87 Python files (~13.6k lines), 4 Java files, 4 PowerShell
scripts, 80 Markdown files (~12.5k lines), 4 LaTeX sources.

## 3. Software components

### 3.1 Core model and physics engines

| Module | Function |
|---|---|
| `model.py` | `EmergentMatterModel`: matter density from multidimensional curvature/entropy compression on a grid |
| `physics_baseline.py` | Relativistic and celestial-mechanics baselines (Schwarzschild, Kepler, etc.) |
| `cosmology_expansion.py` | Late-time expansion engine |
| `cmb_acoustic_engine.py` | Photon-baryon acoustic oscillation engine |
| `lensing_engine.py` | Deflection and geodesic ray tracing |
| `black_hole_horizon_entropy.py` | Bekenstein-Hawking demonstration engine |
| `quantum_vibrational_compression.py` | Microscopic "vibrational compression" demonstration engine |
| `jwst_highz_early_galaxies.py` | High-redshift early-galaxy engine |
| `bullet_cluster_stress_test.py` | Static, synthetic Bullet Cluster illustration (not an observational test) |

### 3.2 Real-data analysis

| Module | Function |
|---|---|
| `fetch_real_data.py` | Downloads SPARC, records URL/size/SHA-256 in `data/external/download_manifest.json`, fails closed on modified cache |
| `data_provenance.py` | Synthetic-banner detection and fail-closed observation verification |
| `fetch_sparc.py` | SPARC catalog ingestion |
| `sparc_real_analysis.py` | Test of `a0 = c H0 / 2 pi` against SPARC |
| `sparc_marginalized_a0.py` | Distance/inclination marginalization |
| `sparc_tension_diagnostics.py` | Gas- vs star-dominated disagreement |
| `sparc_bulge_test.py` | Bulge mass-to-light test |
| `fit_sparc.py`, `fit_jwst.py`, `fit_astrometry.py` | Fitting engines (synthetic fixtures by default) |
| `tools/fit_pantheon_real_covariance.py` | Full-covariance Pantheon+ flat-LCDM baseline |
| `tools/run_sparc_profile_validation.py`, `tools/check_sparc_influence.py`, `tools/run_real_data_gauntlet.py` | Profile validation, influence, regime gauntlet |

### 3.3 Stress tests (software and bound checks)

`stress_test_{blind_challenge, cmb_peaks, cosmology_expansion,
equivalence_principle, galaxy_scatter, gw_speed, solar_system,
stability_ghosts, wide_binaries}.py`.

### 3.4 Figures and visualization

`plot_{cosmology, deep_perspectives, extreme_rigor, publication,
three_horizons}_figures.py`, `visualize.py` (2D client of the REST API),
`viz3d.py` (Plotly), `tools/interactive_visualizer.html` (served at `/visualizer`),
JavaFX client `emergent_matter_model/javafx_client` (Maven, JavaFX 17.0.10,
calls `POST /api/v1/simulate`).

### 3.5 Audit, integrity and release tools

`tools/check_candidate_a_definitions.py`, `check_compression_claims.py`,
`show_your_work_audit.py`, `verify_antigravity_recovery.py`,
`recover_antigravity_evidence.py`, `integrate_recovered_graph.py`,
`build_real_data_report.py`, `build_sparc_paper.py`,
`build_validation_notebook.py`, `package_real_data_release.py`.
`results/real_data_v1/review_manifest.json` pins SHA-256 hashes of the
reviewed sources, results and paper.

## 4. Interfaces

### 4.1 Command line

All 44 runnable programs remain directly runnable as before, e.g.
`python emergent_matter_model/sparc_real_analysis.py`. They are also
reachable through the unified CLI (section 6).

### 4.2 REST API (`server.py`, Flask)

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/v1/health` | Health, service name and version |
| GET | `/api/v1/version` | Software and API version |
| GET | `/api/v1/doctor` | Environment/dependency diagnostics |
| GET | `/api/v1/commands` | Registered programs (`?category=`) |
| GET | `/api/v1/commands/{name}` | One program |
| POST | `/api/v1/commands/{name}/run` | Run a program (disabled unless `EMRF_API_ALLOW_RUN=1`) |
| GET | `/api/v1/datasets` | Data library (`?verify=true` re-hashes) |
| POST | `/api/v1/simulate` | Grid simulation |
| POST | `/simulate` | Legacy alias |
| GET | `/visualizer` | HTML/WebGL dashboard |

Contract: [openapi.yaml](../../emergent_matter_model/openapi.yaml). In-memory
per-IP rate limit 120 requests/min. Production entry `wsgi.py` with
`gunicorn.conf.py`.

## 5. Build, environment and dependencies

### 5.1 Declared dependencies

`pyproject.toml` (setuptools, `requires-python >= 3.10`):

| Package | Declared range | Installed |
|---|---|---|
| numpy | `>=1.26,<3` | 2.2.6 |
| scipy | `>=1.12,<2` | 1.15.3 |
| matplotlib | `>=3.8,<4` | 3.10.9 |
| Flask | `>=3.0,<4` | 3.1.3 |
| flask-cors | `>=4.0,<5` | 4.0.2 |
| requests | `>=2.31,<3` | 2.34.2 |
| plotly | `>=5.18,<6` | 5.24.1 |
| dev: pytest / ruff / mypy | `>=8,<9` / `>=0.2` / `>=1.8` | 8.4.2 / 0.16.9 / 2.3.1 |
| server: gunicorn | `>=21.2,<23` | 22.0.0 |

`pip check`: no broken requirements. Java 25.0.2 is installed; Maven is
vendored but not on `PATH`.

### 5.2 Build and run procedures

```powershell
cd emergent_matter_model
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest              # full suite
.\.venv\Scripts\python.exe emrf_cli.py doctor     # environment check
.\ci_local.ps1                                    # tests + Schwarzschild check + JavaFX compile
.\run_all.ps1                                     # venv, tests, server, 2D client, JavaFX
```

`automate_project.ps1` is deprecated and delegates to `run_all.ps1`.

### 5.3 Measured quality baseline (2026-10-09)

| Check | Result |
|---|---|
| `pytest` (whole package) | **265 passed** (244 pre-existing + 21 CLI/API tests), 36 s |
| `ruff check` (package + tools) | 1,051 findings; 420 auto-fixable; includes 8 `W605` invalid escape sequences and 6 `B023` loop-variable closures |
| `mypy --ignore-missing-imports` | 156 errors in 24 of 75 files |
| Coverage measurement | Not installed |

Phase 1 subsequently established a measured source-only non-golden baseline
of 52.5% line coverage and 42.4% branch coverage (272 tests passed on
2026-10-09). The values above remain the frozen pre-formalization baseline.
| Property-based / fuzz testing | Not installed |
| Hosted CI | None (`.github/` absent); local `ci_local.ps1` only |
| `pip check` | Clean |
| Data verification | SPARC (2 files), Pantheon+ (data, STAT+SYS covariance, README, likelihood) and DESI DR1 (mean, covariance) all match pinned SHA-256 |

### 5.4 Known engineering defects (to be fixed during formalization)

1. **Packaging is incomplete.** `[tool.setuptools] py-modules` lists 8 of
   ~40 library modules; `pip install .` produces a package that cannot run
   most analyses. `readme` points to `README_3D.md`.
2. **Version drift.** The health endpoint reported `0.6.0` (fixed: it now
   reads `emrf_version.py`). `requirements.txt` still lists `pyyaml`,
   although STATUS records it as pruned, and mixes runtime and dev needs.
3. **Flat module namespace** (`model`, `server`, `fit_sparc` ...) collides
   easily with other packages and requires `sys.path` manipulation.
4. **Provenance coverage is partial.** Only SPARC is in
   `download_manifest.json`; Pantheon+ and DESI are pinned inside result
   JSONs instead of the data manifest. Three identical 33 MB covariance
   copies exist in `data/external`.
5. **Non-atomic manifest writes.** `fetch_real_data._record` rewrites the
   manifest in place; an interruption can corrupt it. Downloads read whole
   responses into memory.
6. **No single run record.** Results do not uniformly record code commit,
   environment lock, input hashes, seeds and wall time.
7. **Vendored toolchains in git** (JavaFX SDK, Maven) inflate the repository
   and bypass dependency management; a 47 MB release ZIP sits at repo root.
8. **Legacy verdict strings** in older modules can overstate scientific
   interpretation (documented in STATUS.md).
9. **Python 3.10.0** is an early patch release; the 3.10 line reaches end of
   life in October 2026.

## 6. Unified CLI and API layer (added 2026-10-09)

New, additive modules; no hash-pinned or legacy analysis script was modified.

| File | Role |
|---|---|
| `emrf_version.py` | Single source of the software and API version |
| `emrf_registry.py` | Registry of all 44 runnable programs; shared run, dataset-status and doctor logic |
| `emrf_cli.py` | `emrf` command-line front end |
| `test_emrf_cli_api.py` | 21 tests: registry completeness, CLI behaviour, CLI/API parity, OpenAPI/route parity, tamper detection |

```text
python emrf_cli.py --version
python emrf_cli.py list [--category analysis|stress-test|...] [--json]
python emrf_cli.py run <program> [--timeout S] -- <program args>
python emrf_cli.py simulate --n 2 --weights 0.5 0.5 --grid=-1,0,1 --grid=0,0.5,1 [--output M.npy]
python emrf_cli.py data list [--verify] [--json]
python emrf_cli.py doctor [--json]
python emrf_cli.py serve [--host H] [--port P]
python emrf_cli.py test [-- pytest args]
```

Guarantees enforced by tests:

* Every script with a `__main__` guard in `emergent_matter_model/` or `tools/`
  must be registered; adding an unregistered program fails the suite.
* Every Flask route must appear in `openapi.yaml`, and vice versa.
* `emrf simulate` and `POST /api/v1/simulate` return identical arrays.
* `data list --verify` reports `ok`, `missing`, `size-mismatch` or `hash-mismatch`.
* Remote execution is off by default (HTTP 403), refuses GUI/service
  programs, never uses a shell, validates args and caps timeouts at 600 s.

`pyproject.toml` is hash-pinned in the review manifest, so the `emrf`
console-script entry point is deferred to the packaging phase of the
implementation plan; until then use `python emrf_cli.py`.

## 7. Data holdings

| Dataset | Files | Source pin | Status |
|---|---|---|---|
| SPARC (Lelli+ 2016) | `Rotmod_LTG.zip` (175 curves), `SPARC_Lelli2016c.mrt` | `download_manifest.json` | verified |
| Pantheon+SH0ES | `.dat`, `STAT+SYS.cov`, README, cosmosis likelihood | Git commit `c447f0f` in `pantheon_baseline.json` | verified |
| DESI DR1 BAO (Gaussian) | mean and covariance | CobayaSampler/bao_data `bb0c1c9` in `gauntlet.json` | verified |
| Literature snapshots | `R01`-`R10`, `H01`, `H03` HTML | `gauntlet.json` | stored |
| Synthetic fixtures | 20 CSV | `# SYNTHETIC DATA` banner | fixtures only |

The full catalog of recommended sources is in the
[library catalog](../../knowledgebase/library/README.md).

## 8. Preservation rule

Formalization must not change any numeric result in `results/` for the same
inputs. Every migration step is accepted only when the full suite passes and
a golden-result comparison of the real-data pipelines is byte- or
tolerance-identical, as defined in the implementation plan.
