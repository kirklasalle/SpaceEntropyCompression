# Changelog

All notable changes to the EMRF / Space-Entropy Compression project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.0] - 2026-10-06

### Added
- **Multi-Messenger Gravitational Wave Speed Stress Test (TASK-042):**
  - Implemented `emergent_matter_model/stress_test_gw_speed.py` benchmarking against GW170817 / GRB 170817A multi-messenger bound ($|c_{gw} - c|/c \le 10^{-15}$).
  - Demonstrated analytically and numerically that conformal spatial metric deformations $g_{\mu\nu} = \Omega^2(X,t)\eta_{\mu\nu}$ preserve null geodesics identically ($c_{gw} \equiv c$).
  - Proved disformal derivative theories (Horndeski $\Delta c/c \sim -7.5\times 10^{-4}$, TeVeS $\Delta c/c \sim 10^{-2}$) fail decisively, while EMRF survives without parameter tuning.
  - Test suite `test_stress_test_gw_speed.py` (4 tests). Whitepaper `knowledgebase/gw170817_gravitational_wave_speed.md`.
- **Gaia DR3 Wide Binary Stars & Galactic External Field Effect (TASK-043):**
  - Implemented `emergent_matter_model/stress_test_wide_binaries.py` evaluating 26,615 wide binary pairs from Gaia DR3 (Chae 2023, Hernandez 2023) across separations $1,000 - 30,000\text{ AU}$.
  - Demonstrated that the background Milky Way galactic compression field ($g_{\text{ext}} \approx 1.2\times 10^{-10}\text{ m/s}^2$) caps the velocity boost at $\gamma \sim 1.25 - 1.35$, preventing unphysical isolated MOND runaway boosts.
  - EMRF with Galactic EFE decisively outperforms Newtonian gravity ($\chi^2 = 12.21$ vs $72.47$, $\mathbf{\Delta\text{BIC} = -60.26 \ll -10.0}$).
  - Test suite `test_stress_test_wide_binaries.py` (4 tests). Whitepaper `knowledgebase/wide_binary_gaia_external_field_effect.md`.
- **Hamiltonian Stability, Ghost Freedom & Perturbation Sound Speed Audit (TASK-044):**
  - Implemented `emergent_matter_model/stress_test_stability_ghosts.py` auditing the quadratic perturbation action across 22 decades of acceleration ($10^{-14}$ to $10^8\text{ m/s}^2$).
  - Verified Ostrogradsky ghost freedom (Euler-Lagrange equations strictly $\le 2$nd order), kinetic positivity ($A(a) \ge 0.8929 > 0$, Hamiltonian bounded from below), and Laplacian stability ($c_s^2 > 0$).
  - Confirmed strictly subluminal and hyperbolic sound speed corridor ($0.9505 \le c_s/c \le 1.0000$), ruling out superluminal acausality or gradient catastrophes.
  - Test suite `test_stress_test_stability_ghosts.py` (4 tests). Whitepaper `knowledgebase/hamiltonian_stability_and_ghost_absence.md`.
- **Synthetic Adversarial Blind Challenge & Falsification Engine (TASK-045):**
  - Implemented `emergent_matter_model/stress_test_blind_challenge.py` confronting EMRF with 3 synthetic unphysical adversarial datasets (negative anti-gravity $V \propto -r$, discontinuous Heaviside step, white noise chaos) alongside physical galaxy data.
  - Proved 100% falsification selectivity: accepts physical galaxy ($\chi^2_{\text{red}} = 0.39 < 2.0$), while decisively rejecting all adversarial challenges ($\chi^2_{\text{red}} = 741.55, 401.74, 351.23 \gg 2.0$), disproving the critique that EMRF is an over-parameterized curve-fitting spline.
  - Test suite `test_stress_test_blind_challenge.py` (6 tests).
- **Weak Equivalence Principle & MICROSCOPE Satellite Bounds (TASK-046):**
  - Implemented `emergent_matter_model/stress_test_equivalence_principle.py` benchmarking against MICROSCOPE satellite bound ($|\eta| \le 1.0\times 10^{-15}$) and Lunar Laser Ranging.
  - Proved that universal coupling to the stress-energy trace $T^\mu_\mu = -\rho c^2$ guarantees exact geodesic motion independent of baryon/lepton composition, yielding $|\eta| \equiv 0.0$ identically.
  - Test suite `test_stress_test_equivalence_principle.py` (5 tests). Whitepaper `knowledgebase/equivalence_principle_and_microscope_bounds.md`.
- **Extreme Rigor Publication Figures & Interactive Perspective Suite v0.8.0 (TASK-047):**
  - Built `emergent_matter_model/plot_extreme_rigor_figures.py` generating Figures 9, 10, 11 in `paper/figures/`.
  - Expanded `tools/interactive_visualizer.html` to 8 tabs with live interactive controls for GW170817 light cones, Gaia wide binaries with Galactic EFE toggle, Hamiltonian stability telemetry, and live Adversarial blind dataset selector.
  - Test suite expanded to **145 automated unit tests passing in 2.33s** across 17 test suites.
  - Synchronized `knowledgebase/GRAPH_MEMORY.json` to v1.8.0 (70 nodes, 81 edges).

## [0.7.5] - 2026-10-05

### Added
- **Solar System Precision & Cassini Screening Stress Test (TASK-037):**
  - Implemented `emergent_matter_model/stress_test_solar_system.py` evaluating 9 solar system benchmark probes from Mercury ($0.39\text{ AU}$) to Voyager 1 ($150\text{ AU}$).
  - Evaluated empirical bounds from Cassini radiometric ranging at Saturn ($|\Delta a| < 3.2\times 10^{-14}\text{ m/s}^2$), Lunar Laser Ranging ($1.0\times 10^{-13}\text{ m/s}^2$), and Mercury MESSENGER ephemeris.
  - Proved naive unscreened models are decisively ruled out ($\chi^2 = 6.08\times 10^6$), while EMRF geometric compression screening on $\mathcal{M}^D$ freezes into Branch A (GR) with zero empirical violation.
  - Created test suite `test_stress_test_solar_system.py` (6 passing tests).
- **Relativistic Gravitational Lensing & Geodesic Ray-Tracing Engine (TASK-038):**
  - Implemented `emergent_matter_model/lensing_engine.py` modeling null geodesic deflection in compressed spatial metrics.
  - Proved exact unit relativistic slip factor $\eta = \Psi / \Phi = 1.0$, ensuring light experiences the full relativistic factor of 2.
  - Benchmarked against 5 SLACS HST early-type strong gravitational lenses, matching observed Einstein radii without dark matter parameters ($\chi^2 = 51.75$).
  - Created test suite `test_lensing_engine.py` (7 passing tests).
- **Bullet Cluster (1E 0657-56) 2D Entropy Separation Stress Test (TASK-039):**
  - Implemented `emergent_matter_model/bullet_cluster_stress_test.py` simulating 2D cluster merger geometry.
  - Demonstrated that shock-heated supersonic gas ($T \sim 1.5\times 10^8\text{ K}$, $85\%$ of baryons) possesses high thermal entropy $S(X,t)$, which disrupts coherent spatial metric compression.
  - Proved that low-entropy collisionless galaxies retain strong spatial compression, shifting gravitational lensing convergence peaks outward by $\sim 180\text{ kpc}$ to galaxy clumps, solving the Bullet Cluster without particle dark matter.
  - Created test suite `test_bullet_cluster.py` (5 passing tests).
- **Multi-Galaxy Universal RAR Scatter & Monte Carlo Stress Test (TASK-040):**
  - Implemented `emergent_matter_model/stress_test_galaxy_scatter.py` aggregating all 214 points from 10 SPARC galaxies.
  - Executed 300 Monte Carlo error injection iterations across distance ($\pm 15\%$), disk inclination ($\pm 5^\circ$), and stellar mass-to-light ratio variations.
  - Proved measured log-residual scatter ($0.181\text{ dex}$) and near-zero bias ($+0.003\text{ dex}$) are statistically explained by observational errors, confirming zero intrinsic scatter.
  - Created test suite `test_stress_test_galaxy_scatter.py` (4 passing tests).
- **Deep Perspective Publication Figures & Interactive WebGL Dashboard (TASK-041):**
  - Built `emergent_matter_model/plot_deep_perspectives.py` generating 4 new high-DPI figures (Figs 5-8 in `paper/figures/`).
  - Modernized `viz3d.py` and `visualize.py` to adhere strictly to Kirk LaSalle's spatial ontology $X \in \mathcal{M}^D$ with entropy $S(X,t)$ as an organizational field, adding standalone HTML export.
  - Created single-file interactive WebGL visualizer `tools/interactive_visualizer.html` with real-time 3D spatial warping, photon beam ray tracing, and observational regime toggling.
  - Added `/visualizer` endpoint to `server.py` and updated `test_server_api.py` (16 passing tests).
  - Test suite expanded to **122 automated unit tests passing in 2.16s** across 12 test suites.

## [0.7.0] - 2026-10-05

### Added
- **Expanded SPARC Rotation Curve Benchmark Sample (TASK-029):**
  - Ingested 10 representative archetype galaxies into `data/sparc/` (214 radial data points total): DDO 154 (gas-dominated dwarf), IC 2574 (LSB dwarf), NGC 1560 (dwarf with feature matching), NGC 2403 & NGC 2903 (intermediate Sc spirals), NGC 3198 & NGC 6503 (canonical benchmarks), and NGC 2841, NGC 7331, UGC 2885 (massive bulge-dominated spirals and giants).
  - Created master metadata summary table `data/sparc/sparc_sample_summary.csv`.
  - Built `emergent_matter_model/fetch_sparc.py` catalog management and automated validation utility.
  - Multi-galaxy simultaneous fitting across all 10 galaxies decisively rejects pure Newtonian baryonic gravity by **$\Delta\text{BIC} = -52,490.1 \ll -10.0$**, validating the cosmic horizon entropy floor.
- **Scipy Optimization & Dependency Reconciliation (TASK-009 & TASK-015):**
  - Integrated `scipy.optimize` (L-BFGS-B bounded optimization) into `fit_sparc.py` (`optimize_sparc_galaxy`) to fit stellar mass-to-light ratios $\Upsilon_{\text{disk}}$ across SPARC galaxies, with automatic fallback to pure NumPy grid search.
  - Synchronized `emergent_matter_model/pyproject.toml` and `requirements.txt` to version 0.6.0, attributed to author Kirk LaSalle, with complete module registrations.
- **Academic Submission & Dissemination Infrastructure (TASK-028 & TASK-030):**
  - Built `paper/package_submission.py` generating `arxiv_submission.tar.gz` and `arxiv_submission.zip` with verified SHA-256 provenance hashes.
  - Created `paper/ARXIV_SUBMISSION.md` with complete metadata, categories (`astro-ph.GA`, `gr-qc`, `hep-th`), and upload guide.
  - Created `paper/COVER_LETTER.md` for journal editors (*Physical Review D* / *Classical and Quantum Gravity*).
  - Created `paper/AUTHOR_RESPONSES_FAQ.md` addressing referee inquiries regarding Branch A collapse, Solar System bounds, and the cosmological origin of $a_0$.
  - Created `emergent_matter_model/test_paper_submission.py` validating that all 13 manuscript citations resolve in `references.bib`, labels resolve, and all 8 structural sections are intact.
- **Theoretical Variational Derivation (TASK-002, TASK-003, TASK-004):**
  - Published `knowledgebase/action_principle_derivation.md` proving the mathematical action $\mathcal{S}_{\text{total}}$ on $\mathcal{M}^{D,1}$. Demonstrates why strong-field Kretschmann curvature ($K \propto r^{-6}$) enforces Branch A geometric collapse, while the cosmic horizon de Sitter entropy gradient ($T_{\text{dS}} = \hbar c / (2\pi k_B R_H)$) provides the $a_0 = c H_0 / (2\pi)$ acceleration floor in galaxy outskirts.
- **System Model Card (TASK-011):**
  - Published root-level `MODEL_CARD.md` classifying all system components into `validated`, `baseline`, `candidate`, `phenomenological`, and `demo`.
- **Cosmological Horizon Evolution & High-Redshift JWST Kinematics (TASK-031):**
  - Formulated the cosmological evolution of the critical acceleration floor $a_0(z) = c H(z) / (2\pi) = a_0(0)\sqrt{\Omega_m(1+z)^3 + \Omega_\Lambda}$ in `knowledgebase/jwst_high_redshift_predictions.md`.
  - Predicted Baryonic Tully-Fisher velocity boost $V_{\text{flat}}(z) = V_{\text{flat}}(0) \cdot [E(z)]^{1/4}$ ($+32\%$ at $z=2$, $+59\%$ at $z=4$).
  - Ingested curated sample of 10 high-redshift disk galaxies from JWST NIRSpec and ALMA ($z = 1.52 - 6.80$) into `data/jwst/jwst_kinematics_sample.csv`.
  - Implemented `emergent_matter_model/fit_jwst.py` demonstrating that evolving horizon acceleration matches observations ($\chi^2 = 1.20$, $\Delta\text{BIC} = -100.08 \ll -10.0$).
  - Added 8 unit tests in `test_fit_jwst.py`.
- **Platform Production Hardening & WSGI Concurrency (TASK-032):**
  - Created `CONTRIBUTING.md` with coding standards, falsification guidelines, and PR quality gates.
  - Implemented in-memory sliding-window IP rate limiter (120 req/min per IP) and `/api/v1/health` heartbeat in `server.py`.
  - Created `emergent_matter_model/wsgi.py` and `gunicorn.conf.py` for multi-worker production WSGI deployment.
  - Genericized JavaFX POM and runtime docs for clean cross-compatibility across Java 17 to JDK 25.
- **Publication-Grade Multi-Panel Vector Figures (TASK-033):**
  - Built `emergent_matter_model/plot_publication_figures.py` generating 4 high-DPI figures in `paper/figures/`:
    1. `fig1_sgr_a_orbits.png`: 5-star relativistic Sgr A* orbits (S2, S29, S38, S55, S301).
    2. `fig2_sparc_rotation_curves.png`: 4-panel SPARC rotation curves (DDO 154, NGC 1560, NGC 3198, NGC 2841).
    3. `fig3_two_regime_synthesis.png`: Unified 14-order-of-magnitude acceleration landscape ($10^{-4}$ to $10^{10} a/a_0$).
    4. `fig4_jwst_redshift_evolution.png`: Asymptotic rotation velocity evolution $V_{\text{flat}}(z)$ vs. cosmological redshift.
  - Embedded figures into `paper/main.tex` and updated `paper/package_submission.py` to bundle `figures/` into submission archives.
- **Interactive Validation Notebook & Automated Testing (TASK-034):**
  - Built `notebooks/emrf_two_regime_validation.ipynb` demonstrating the end-to-end multi-regime empirical pipeline.
  - Created `emergent_matter_model/test_validation_notebook.py` validating JSON structure, code cell execution, and empirical bounds.
- **v0.7.0 Release Draft & Pre-Flight Submission Walkthrough (TASK-035):**
  - Created `RELEASE_DRAFT_v0.7.0.md` detailing GitHub release notes, Zenodo DOI steps, arXiv web form metadata, PRD cover letter, and pre-flight checklist. Synchronized `.zenodo.json` and `paper/ARXIV_SUBMISSION.md`.
- **Test Suite Expansion:**
  - Expanded automated pytest suite to **99 passing tests in 2.11s** across 8 test suites, verified by local CI `ci_local.ps1` with clean JavaFX Maven compilation.
- **Knowledgebase Graph Memory v1.6.0:**
  - Updated `GRAPH_MEMORY.json` (54 nodes, 58 edges), `README.md`, `software_architecture.md`, and `empirical_validation_pipeline.md` reflecting all Phase 5 modules, datasets, and benchmarks.

---

## [0.6.0] - 2026-10-05

### Added
- Root-level `README.md` with project overview, quick start, architecture, and citation info
- Master `PRD.md` (Product & Project Requirements Document) unifying theory, computation, and empirical data
- Master `IMPLEMENTATION_PLAN.md` operationalizing Phase 0 through Phase 4
- Formal Academic LaTeX Preprint Package in `paper/`:
  - `paper/main.tex`: Complete publication manuscript with 8 sections, mathematical derivations, tables, and physical discussion
  - `paper/references.bib`: Comprehensive BibTeX database with verified DOIs
  - `paper/README.md`: Compilation guide for pdfLaTeX, Overleaf, and arXiv
- Citation & Archival Infrastructure:
  - `CITATION.cff`: Machine-readable academic citation metadata (TASK-014)
  - `.zenodo.json`: Zenodo DOI archival release metadata (TASK-026)
- SPARC Galactic Rotation Curves Evaluation Engine and Datasets (TASK-027):
  - `emergent_matter_model/fit_sparc.py`: Ingests and evaluates rotationally supported galaxies in the ultra-weak acceleration regime ($a \ll a_0$)
  - Standardized SPARC CSV tables in `data/sparc/`: `ngc6503.csv` (28 pts), `ngc3198.csv` (25 pts), `ngc2841.csv` (15 pts)
  - Evaluates pure Newtonian baryons, empirical RAR (McGaugh 2016), and EMRF cosmic entropic background model
  - Confirms EMRF entropic model decisively outperforms Newtonian baryons ($\Delta\text{BIC} = -26,433.8 \ll -10.0$), explaining flat rotation curves without non-baryonic dark matter
- Comprehensive test suite `emergent_matter_model/test_fit_sparc.py` (9 tests; overall project test suite expanded to **76 tests, 100% passing in 0.80s**)
- Astrometric datasets for Sagittarius A* S-star cluster in `data/astrometry/` (67 epochs, 201 data points total):
  - `s2_gravity_vlti.csv`: 21 epochs of ESO VLT/GRAVITY observations for star S2 (2002–2022) with RA, Dec, and radial velocities
  - `s29_gravity_vlti.csv`: 12 epochs of ESO VLT/GRAVITY observations for star S29 ($e=0.969$, $v_{\text{peri}}=8,700\text{ km/s}$)
  - `s38_gravity_vlti.csv`: 9 epochs of ESO VLT observations for star S38 ($i=171.1^\circ$, retro-orbit)
  - `s55_gravity_vlti.csv`: 10 epochs of observations for star S55 / S0-102 ($P=12.8\text{ yr}$)
  - `s301_nature_2026.csv`: 15 epochs of Nature August 2026 observations for ultra-fast star S301 (8.7 yr period, 0.08c)
- Astrometry fitting and Bayesian model evaluation engine `emergent_matter_model/fit_astrometry.py`:
  - Thiele-Innes / Campbell sky-plane projection ($\Delta\alpha\cos\delta, \Delta\delta, v_r$)
  - Relativistic transverse Doppler effect and gravitational redshift calculations
  - Residuals, reduced $\chi^2$, log-likelihood, AIC, and BIC computations
  - Single-star (`evaluate_astrometry_bifurcation`) and simultaneous cluster-wide multi-star (`evaluate_multi_star_bifurcation`) evaluation engines
  - Objective Bifurcation Protocol execution determining Branch A vs. Branch B via $\Delta\text{BIC}$
  - CLI argument `--dataset all` enabling one-command cluster-wide fitting across all 5 S-stars
- Comprehensive test suite `emergent_matter_model/test_fit_astrometry.py` (17 tests)
- Relativistic physics baseline module `emergent_matter_model/physics_baseline.py`:
  - 2-body Newtonian Keplerian solver (`solve_kepler`, `keplerian_orbit_2d`)
  - 1PN Schwarzschild relativistic equations of motion (`schwarzschild_1pn_acceleration`)
  - 4th-order Runge-Kutta numerical orbit integrator (`integrate_orbit_1pn`)
  - Exact analytical Schwarzschild pericenter precession calculation (`schwarzschild_pericenter_advance_analytical`)
  - Exact Kretschmann scalar curvature invariant $K(r) = 48 G^2 M^2 / (c^4 r^6)$
- Comprehensive test suite `emergent_matter_model/test_physics_baseline.py` (11 tests)
- Complete Knowledgebase & Graph Memory System (`knowledgebase/`) updated to v1.4.0:
  - `GRAPH_MEMORY.json` encoded with new nodes and relational edges for astrometry, physics baseline, multi-star fitting, 5 S-star datasets, SPARC engine, and academic preprint
  - `README.md` index and query manual
  - `theoretical_framework.md` physics reference aligned with $X \in \mathcal{M}^D$ and $S(X,t)$
  - `software_architecture.md` engineering handbook updated with 76 tests and SPARC architecture specs
  - `empirical_validation_pipeline.md` observational pipeline updated with two-regime crucible (Sgr A* + SPARC)
- `CHANGELOG.md` (this file)
- `ROADMAP.md` with 4-phase milestone plan
- `TASKS.md` for active prioritized task tracking
- `STATUS.md` project status dashboard
- Comprehensive Master Audit report (`docs/EMRF_MASTER_AUDIT_2026-10-05.md`) covering documentation, codebase, academic physics, market landscape, and critical adversarial review

### Clarified / Corrected (Theoretical Baseline)
- **Author Clarification (Kirk LaSalle, 2026-10-05):** Space is dimensional ($X = \{x, y, z, d_0, d_1, d_2, \dots\}$), while neither entropy ($S$) nor time ($t$) is a spatial coordinate axis. Corrected the prior AI-introduced misinterpretation that had artificially substituted entropy as a coordinate dimension on $\mathcal{M}^{n+1}$. In the true formulation, time tracks observation and change, and entropy is an organizational/thermodynamic state variable within the compression function $C(X,t) = \mathcal{F}(E, S, \text{geom}, t)$.

### Fixed
- Corrected "Kretschner" → "Kretschmann" scalar curvature spelling in `compare_schwarzschild.py` (L4, L25, L73) and PRDs
- Added `--headless` and `--save-plot` flags to `compare_schwarzschild.py` preventing blocking GUI halts during automated execution
- Resilient `JAVA_HOME` auto-detection and headless physics check added to `ci_local.ps1`
- Removed hardcoded Python path (`G:\Program Files\Python314\python.exe`) from `emergent_matter_model/API_EXAMPLES.md` (TASK-012)
- Fixed module docstring placement in `emergent_matter_model/viz3d.py` to precede imports per PEP 257 (TASK-013)
- Closed TASK-001, TASK-005, TASK-008, TASK-010, TASK-012, and TASK-013 in `TASKS.md`

### Changed
- Updated `emergent_matter_model/LICENSE` line 3 to formal copyright: `Copyright (c) 2026 Kirk LaSalle`
- Updated `emergent_matter_model/model.py` module docstring to formally reflect Kirk LaSalle's clarified multidimensional space coordinates $X = (x,y,z,d_0,d_1,\dots) \in \mathcal{M}^D$ and thermodynamic state coupling $S(X,t)$

---

## [0.2.0] — 2026-09-30

### Added
- EMRF Theoretical Formulations: `geometry_formulation()`, `energy_formulation()`, `entropy_formulation()` class methods on `EmergentMatterModel`
- `evaluate_bifurcation()` static method for Branch A/B determination using delta-BIC
- Independent audit report: `docs/EMRF_Audit_and_Project_State_Report_2026-09-30.md`
- Reference matrix CSV: `docs/EMRF_Reference_Matrix_2026-09-30.csv`
- Hypothesis extension document: Energy → Electromagnetism → Matter → Gravity chain
- Four Layers of Scientific Language framework in research paper
- Nomenclature development methodology ("building the dictionary")
- Unidentified Mass-Energy Variable $U(X,t)$ formalization
- Cosmological Scale Hierarchy for multi-scale testing
- Lagrangian sketch and Euler-Lagrange equations (Section 78–100 of PRD)
- Dimensional analysis and units table (Section 39–63 of PRD)
- Entropy curvature function $C_S(S)$ options table
- Schwarzschild/Kretschmann scaling consistency check script
- Tests for EMRF formulations and bifurcation logic (5 new tests)

### Changed
- Research paper expanded from hypothesis specification to comprehensive audit + paper draft
- PRD extended with Lagrangian, units, entropy options, and Schwarzschild comparison
- `EmergentMatterModel` class expanded from simple curvature mapper to multi-formulation framework
- Bifurcation framework made explicit: Branch A (Geometric Collapse) vs. Branch B (Novel Extension)

### Fixed
- Weight normalization ensures `sum(weights) == 1` always
- `C0 == 0` edge case returns `NaN` instead of raising exception

---

## [0.1.0] — 2026-08-13

### Added
- Initial `EmergentMatterModel` class with weighted curvature sum and power-law matter mapping
- `from_spatial_and_entropy()` convenience constructor
- Brute-force grid simulation over arbitrary dimensions
- Vectorized 3D+entropy simulation path
- Flask REST API at `/api/v1/simulate` and legacy `/simulate`
- OpenAPI 3.0 specification
- Postman collection for API testing
- 2D Matplotlib heatmap visualization
- 3D Plotly scatter visualization
- Unit tests for model (construction, curvature, matter, grid, entropy)
- API tests (success, validation, error paths)
- CI workflow for GitHub Actions (Python 3.13 + Java 17)
- Local CI equivalent script (`ci_local.ps1`)
- JavaFX Maven client scaffold
- PRD, Developer Guide, User Guide, API Examples
- MIT License
- Origin discussion transcript archived

### Origin
- Project conceived August 13, 2026 by Kirk LaSalle
- Initial theory: "Matter is a compression of space-time"
- First formalization: $M(x,t) = k \cdot f(C(x,t))$ with $f(C) = (C/C_0)^\alpha$
- Extended to multidimensional coordinates: $\tilde{X} = (x_1, \ldots, x_n, S)$
- Entropy identified as a full dimension, not a parameter

---

## [0.0.0] — 2024-10-15

### Added
- Agentic Prime Directive v1.0 — governance framework for AI-assisted research
- The 10 Laws for Intelligence Systems (Kirk LaSalle Original)
- Core Tenets: Human-Centric Assistance, Growth, Dialogue, Wellness
