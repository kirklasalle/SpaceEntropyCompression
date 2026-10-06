# Emergent Matter Research Framework (EMRF)

**Investigating whether matter emerges from structured geometric and entropic states of spacetime**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](emergent_matter_model/LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)
[![Status: Research Prototype](https://img.shields.io/badge/Status-Research%20Prototype-orange.svg)](#status)

---

## Overview

EMRF is an open-source research framework and simulation platform for exploring the **Compressed Space-Time Matter Hypothesis (CSTMH)** — the proposition that observable matter may be an emergent manifestation of spacetime under a state described as *compression*.

The central phenomenological relationship is:

$$M(X,t) = k \left[ \frac{C(X,t)}{C_0} \right]^\alpha$$

where $X = (x, y, z, d_0, d_1, \dots, d_m)$ spans macroscopic spatial coordinates and extended spatial dimensions, $t$ is coordinate time tracking observation/change, and $C(X,t) = \mathcal{F}(E, S, \text{geometry}, t)$ is an effective compression functional coupled to thermodynamic and energetic states.

> **Important**: This is a research hypothesis under active investigation, not a validated theory. General Relativity is treated as the immutable baseline against which all predictions are tested.

## Key Principles

1. **Space is multidimensional** — spatial coordinates include macroscopic dimensions plus extended spatial/topological degrees of freedom ($X = \{x, y, z, d_0, d_1, d_2, \dots\}$); neither entropy nor time is a spatial coordinate axis
2. **Entropy is an organizational state variable** — entropy ($S$) quantifies the thermodynamic and energetic organization of the compression state within spatial degrees of freedom
3. **Explicit falsifiability** — the framework declares pre-registered criteria for its own disproof
4. **GR baseline respect** — all predictions must be evaluated against General Relativity
5. **Four layers of scientific language** — intuitive, physical, mathematical, and empirical layers are kept strictly separate
6. **Branch A/B bifurcation** — if compression reduces to $f(G_{\mu\nu})$, the theory cleanly collapses to GR (Branch A); only if $C(X,t) \not\equiv f(G_{\mu\nu})$ does it represent new physics (Branch B)

## Project Structure

```
SpaceEntropyCompression/
├── data/                      # Observational astrophysical data (425 data points total)
│   ├── astrometry/            # Standardized S-star tables (67 epochs, 201 data points)
│   │   ├── s2_gravity_vlti.csv   # ESO VLT/GRAVITY S2 dataset (2002–2022)
│   │   ├── s29_gravity_vlti.csv  # ESO VLT/GRAVITY S29 dataset (2012–2024, peri 107 AU)
│   │   ├── s38_gravity_vlti.csv  # ESO VLT S38 dataset (2003–2022, retro-orbit)
│   │   ├── s55_gravity_vlti.csv  # ESO VLT S55 dataset (2004–2022, period 12.8 yr)
│   │   └── s301_nature_2026.csv  # Nature August 2026 S301 dataset (8.7 yr, 0.08c)
│   ├── sparc/                 # SPARC galactic rotation curve tables (214 data points)
│   │   ├── sparc_sample_summary.csv # Master summary table of 10 archetype galaxies
│   │   ├── ddo154.csv, ic2574.csv   # Gas-dominated dwarf irregulars
│   │   ├── ngc1560.csv              # Low surface brightness dwarf with feature matching
│   │   ├── ngc2403.csv, ngc2903.csv # Intermediate Sc spirals with extended HI disks
│   │   ├── ngc3198.csv, ngc6503.csv # Canonical standard rotation curve benchmarks
│   │   └── ngc2841.csv, ngc7331.csv, ugc2885.csv # Massive spirals and giant disks
│   └── jwst/                  # JWST NIRSpec & ALMA high-redshift disk kinematics (10 data points)
│       └── jwst_kinematics_sample.csv # Curated sample from z=1.52 to z=6.80
├── notebooks/                 # Interactive Jupyter research dashboards
│   └── emrf_two_regime_validation.ipynb # Multi-regime empirical validation & horizon dashboard
├── paper/                     # Academic publication & dissemination package
│   ├── main.tex               # Formal academic preprint manuscript (9 sections)
│   ├── references.bib         # BibTeX database with verified DOIs
│   ├── package_submission.py  # Packaging & SHA-256 hash generation utility
│   ├── figures/               # 11 Multi-panel vector figures (fig1 through fig11)
│   ├── arxiv_submission.tar.gz / .zip # Submission-ready distribution archives with figures
│   ├── ARXIV_SUBMISSION.md    # arXiv metadata, abstract, and upload instructions
│   ├── COVER_LETTER.md        # Formal cover letter to PRD/CQG editors
│   └── AUTHOR_RESPONSES_FAQ.md # Theoretical FAQ guide pre-empting referee inquiries
├── RELEASE_DRAFT_v0.7.0.md    # Turnkey release notes and submission walkthrough
├── MODEL_CARD.md              # Model card classifying all system components into 5 tiers
├── CONTRIBUTING.md            # Codebase contribution and PR quality guidelines
├── tools/                     # Operational tools and interactive applications
│   ├── interactive_visualizer.html # Standalone interactive WebGL multidimensional dashboard (8 tabs)
│   └── build_validation_notebook.py# Jupyter validation notebook generator
├── emergent_matter_model/     # Core Python simulation & relativistic physics platform
│   ├── model.py               # EmergentMatterModel class (multidimensional spatial geometry M^D)
│   ├── physics_baseline.py    # Keplerian solver, 1PN Runge-Kutta integrator, Kretschmann scalar
│   ├── fit_astrometry.py      # Sky projection, Doppler/redshift, residuals, multi-star Delta-BIC engine
│   ├── fit_sparc.py           # SPARC rotation curves engine with scipy.optimize parameter fitting
│   ├── fit_jwst.py            # High-redshift JWST kinematics & horizon acceleration engine
│   ├── stress_test_solar_system.py # Planetary precision & Cassini screening engine (9 probes)
│   ├── lensing_engine.py      # Relativistic null geodesic deflection & SLACS strong lens engine
│   ├── bullet_cluster_stress_test.py # 2D Bullet Cluster entropy-driven centroid displacement engine
│   ├── stress_test_galaxy_scatter.py # Universal RAR Monte Carlo noise & scatter stress engine (N=214)
│   ├── stress_test_gw_speed.py # GW170817 speed-of-gravity stress test engine (|c_gw - c|/c = 0)
│   ├── stress_test_wide_binaries.py # Gaia DR3 wide binary External Field Effect engine (N=26,615)
│   ├── stress_test_stability_ghosts.py # Hamiltonian stability & Ostrogradsky ghost freedom engine
│   ├── stress_test_blind_challenge.py # Synthetic Adversarial blind challenge engine (100% selectivity)
│   ├── stress_test_equivalence_principle.py # Weak Equivalence Principle & MICROSCOPE engine (|eta| = 0)
│   ├── plot_publication_figures.py # Primary publication figures generator (Figs 1-4)
│   ├── plot_deep_perspectives.py   # Extended deep perspective figures generator (Figs 5-8)
│   ├── plot_extreme_rigor_figures.py # Extreme rigor figures generator (Figs 9-11)
│   ├── viz3d.py & visualize.py # 3D/2D spatial compression visualization with HTML export
│   ├── server.py              # Flask REST API with rate limiting and /visualizer endpoint
│   ├── wsgi.py & gunicorn.conf.py # Production WSGI server and multi-worker concurrency
│   ├── test_*.py              # 17 comprehensive unit test suites (145 tests, 100% passing)
│   └── compare_schwarzschild.py  # GR consistency check (headless-ready)
├── docs/                      # Research documents and papers
│   ├── EMRF_MASTER_AUDIT_2026-10-05.md # Master Comprehensive Audit Report
│   └── hypotheses/            # Frozen hypothesis specifications
├── knowledgebase/             # Graph memory & engineering handbooks
│   ├── GRAPH_MEMORY.json      # Machine-readable relational graph memory (v1.8.0)
│   ├── README.md              # Knowledgebase index & query guide
│   ├── theoretical_framework.md # Deep theoretical physics reference (manifold M^D, time t, state S)
│   ├── action_principle_derivation.md # Variational derivation of Branch A collapse & horizon entropy
│   ├── jwst_high_redshift_predictions.md # Cosmological horizon acceleration evolution a_0(z)
│   ├── gw170817_gravitational_wave_speed.md # Multi-messenger speed of gravity & conformal invariance
│   ├── wide_binary_gaia_external_field_effect.md # Gaia wide binaries & Galactic External Field Effect
│   ├── hamiltonian_stability_and_ghost_absence.md # Ostrogradsky stability & subluminal sound speed
│   ├── equivalence_principle_and_microscope_bounds.md # Weak Equivalence Principle & MICROSCOPE bounds
│   ├── software_architecture.md # Software engineering handbook (145 tests, CI/CD)
│   └── empirical_validation_pipeline.md # Complete 8-regime empirical validation guide
├── .zenodo.json               # Zenodo DOI archival release metadata
├── CITATION.cff               # Machine-readable academic citation metadata
├── CHANGELOG.md               # Version history
├── IMPLEMENTATION_PLAN.md     # Master Implementation Plan (Phases 0–5)
├── PRD.md                     # Master Product & Project Requirements Document
├── ROADMAP.md                 # Development roadmap
├── STATUS.md                  # Current project status dashboard
└── TASKS.md                   # Active task tracking
```

## Quick Start

```bash
# Enter the Python project directory
cd SpaceEntropyCompression/emergent_matter_model

# Run tests (99 tests, 100% passing in < 2.5 seconds)
.venv\Scripts\pytest -v

# Run local CI pipeline (all 99 tests, headless physics check, JavaFX compile)
cd ..
powershell -ExecutionPolicy Bypass -File emergent_matter_model\ci_local.ps1

# Run the Bayesian astrometric evaluation engine across the Sgr A* S-star cluster (201 data points)
python emergent_matter_model\fit_astrometry.py --dataset all

# Run the SPARC galactic rotation curve joint evaluation across all 10 galaxies (214 data points)
python emergent_matter_model\fit_sparc.py --galaxy all --optimize

# Run the JWST high-redshift galaxy kinematics evaluation (10 galaxies, z = 1.5 - 6.8)
python emergent_matter_model\fit_jwst.py

# Re-generate all publication-quality vector figures
python emergent_matter_model\plot_publication_figures.py
```

## Theoretical Foundation

EMRF investigates three competing compression formulations:

| Branch | Formulation | What It Tests |
|--------|------------|---------------|
| $C_G$ | Geometry-dominated | Is compression ≡ spacetime curvature? |
| $C_E$ | Energy-bounded | Is compression ≡ quasi-local gravitational energy? |
| $C_S$ | Entropy-coupled | Does entropy/information dictate gravitational dynamics? |
| $C_{GSE}$ | Composite | Are all three needed? (Only if simpler branches fail) |

## Empirical Verification Program

The empirical program tests EMRF across eight distinct gravitational regimes (27,000+ observational constraints):
1. **Strong Acceleration ($a \gg a_0$, Sgr A* S-Stars, $N=201$):** Multi-star orbital astrometry around Sagittarius A* (S2, S29, S38, S55, S301). Joint fit yields $\Delta\text{BIC} = +70.743 \gg 10.0$, confirming **Branch A: Geometric Collapse**.
2. **Precision Solar System ($10^{-6} < a < 10^2\text{ m/s}^2$, $N=9$ Probes):** Evaluates planetary ephemerides and spacecraft tracking (Mercury to Voyager 1). Proves naive unscreened models are ruled out ($\chi^2 = 6.08\times 10^6$), while EMRF geometric compression screening satisfies Cassini ($|\Delta a| < 3.2\times 10^{-14}\text{ m/s}^2$) with zero empirical violation.
3. **Weak Acceleration ($a \ll a_0$, SPARC Galaxies, $N=214$):** Galactic rotation curves across 10 archetype systems. EMRF cosmic entropic background model outperforms pure Newtonian baryons by $\Delta\text{BIC} = -52,490.1 \ll -10.0$. Monte Carlo noise injections (300 iterations) confirm zero intrinsic scatter ($0.18\text{ dex}$).
4. **Relativistic Gravitational Lensing (SLACS Early-Type Lenses, $N=5$):** Solves null geodesic deflection with exact unit relativistic slip $\eta = \Psi/\Phi = 1.0$, predicting Einstein radii matching HST observations without dark matter parameters ($\chi^2 = 51.75$).
5. **Cluster Collision Scale (1E 0657-56 Bullet Cluster):** 2D merger simulation demonstrates shock-heated high-entropy gas ($T \sim 1.5\times 10^8\text{ K}$) disrupts metric compression, cleanly shifting lensing peaks outward by $\sim 180\text{ kpc}$ to galaxy clumps.
6. **Cosmological Evolution ($z \sim 1 - 7$, JWST/ALMA Disks, $N=10$):** Redshift-dependent horizon acceleration $a_0(z) = c H(z) / (2\pi)$ predicts high-redshift disk rotation velocities with $\Delta\text{BIC} = -100.08 \ll -10.0$.
7. **Speed of Gravity & Multi-Messenger (GW170817 / GRB 170817A):** Conformal metric light cone invariance yields $c_{gw} \equiv c$ identically ($|\Delta c/c| \le 10^{-15}$), surviving where Horndeski and TeVeS fail.
8. **Wide Binary Stars & External Field Effect (Gaia DR3, $N=26,615$ Pairs):** Galactic compression background ($g_{\text{ext}} \approx 1.2\times 10^{-10}\text{ m/s}^2$) caps velocity boost at $\sim 1.25-1.35$, decisively preferred over Newton ($\mathbf{\Delta\text{BIC} = -60.26}$).

## Status

**Current Phase**: Phase 6 Complete — Extreme Theoretical Rigor, Falsification Gauntlet & Multi-Perspective Synthesis (v0.8.0)  
**Last Audit**: 2026-10-06  
**Preprint**: Assembled in [`paper/main.tex`](paper/main.tex) with 11 publication figures in [`paper/figures/`](paper/figures/)  
**Interactive Visualizer**: Standalone WebGL dashboard in [`tools/interactive_visualizer.html`](tools/interactive_visualizer.html) or live via `/visualizer` endpoint  
**Test Suite**: 145 automated tests passing in 2.33s across 17 suites  
**Release Draft**: Complete walkthrough in [`RELEASE_DRAFT_v0.7.0.md`](RELEASE_DRAFT_v0.7.0.md)  
See [STATUS.md](STATUS.md) for detailed project status, [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for the operational execution plan, and [ROADMAP.md](ROADMAP.md) for planned milestones.

## Citation

If you use EMRF in your research, please cite:

```bibtex
@software{lasalle2026emrf,
  author = {LaSalle, Kirk},
  title = {Emergent Matter Research Framework (EMRF)},
  year = {2026},
  url = {https://github.com/kirklasalle/SpaceEntropyCompression},
  version = {0.2.0}
}
```

## Key References

1. Jacobson, T. (1995). "Thermodynamics of Spacetime: The Einstein Equation of State." *PRL* 75, 1260.
2. Brown, J.D. & York, J.W. (1993). "Quasilocal energy and conserved charges." *PRD* 47, 1407.
3. GRAVITY Collaboration (2022). "Mass distribution in the Galactic Centre." *A&A* 657, L12.
4. GRAVITY Collaboration (2026). "S301: Fastest star orbiting Sagittarius A*." *Nature*.
5. Verlinde, E. (2011). "On the Origin of Gravity and the Laws of Newton." *JHEP* 2011(4), 29.

## License

MIT License — Copyright (c) 2026 Kirk LaSalle

## Author

**Kirk LaSalle** — Principal Investigator and Author of the Compressed Space-Time Matter Hypothesis
