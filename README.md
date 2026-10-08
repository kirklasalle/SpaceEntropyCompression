# Emergent Matter Research Framework (EMRF)

**Investigating whether matter and the galactic acceleration scale emerge from the organization of space, with entropy as a state field**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23197308.svg)](https://doi.org/10.5281/zenodo.23197308)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](emergent_matter_model/LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)
[![Status: Corrected research release](https://img.shields.io/badge/Status-corrected%20after%20audit-orange.svg)](docs/SHOW_YOUR_WORK.md)

![EMRF Space-Entropy Compression Hero Banner](docs/assets/emrf_hero_banner.jpg)

> *"Let every line of mathematics be weighed in truth. Let every line of code execute without deceit. Let every discovery serve the protection and elevation of life upon our shared Earth—for humanity, for the creatures of land, sea, and sky, and for the generations yet unborn. These works shall indeed be good works."*  
> — **Kirk LaSalle, Principal Investigator**

---

## Integrity notice (2026-10-07)

An independent "show your work" audit ([`docs/SHOW_YOUR_WORK.md`](docs/SHOW_YOUR_WORK.md), reproducible with `python tools/show_your_work_audit.py`) found that **earlier versions of this repository, and the Zenodo release above, reported results computed from synthetic data files labelled as real observations.** Several "stress tests" also returned answers written into the code. Specifically:

* The S-star, SPARC, JWST, supernova and CMB tables were not authentic. They are now quarantined, clearly labelled, in [`data/synthetic/`](data/synthetic/README.md). Pipelines that read them print a `SYNTHETIC INPUT DATA` banner.
* **All earlier headline results are withdrawn:** ΔBIC = +70.743 / +141.3 (S-stars), −52,490.1 (SPARC), −100.08 (JWST), −60.26 (wide binaries), CMB χ²ᵥ = 0.924, "28,700+ constraints", and the "Certified Level 5" and "100/100" audit scores.
* The DESI BAO table has been corrected to the official DR1 values.
* The real-data replacement is described below and in the revised paper [`paper/main.tex`](paper/main.tex).

## Current real-data result

On the **real SPARC database** (Lelli, McGaugh & Schombert 2016; 153 galaxies, 3,168 points after standard cuts), a single global acceleration scale was fitted for four candidate laws ([`emergent_matter_model/sparc_real_analysis.py`](emergent_matter_model/sparc_real_analysis.py)):

| Law | Best global a₀ (10⁻¹⁰ m/s²), range over M/L treatments | ΔBIC vs RAR | Solar System |
|---|---|---|---|
| McGaugh RAR, 1/(1 − exp(−√y)) | 1.03 – 1.22 | 0 | passes |
| MOND "simple" | 1.06 – 1.18 | +1,088 | fails |
| **Earlier EMRF law √(g_N² + a₀g_N)** | 1.30 – 1.59 | **+6,440** | **fails (+a₀/2)** |
| MOND "standard" | 1.34 – 1.77 | +10,548 | passes |

* **EMRF's horizon hypothesis a₀ = cH₀/2π** (1.04 for H₀ = 67.4; 1.13 for H₀ = 73.0) is consistent with this first pass within the stellar mass-to-light systematic, when an RAR-like law is used.
* The specific law in earlier EMRF drafts is **disfavoured** by both galaxies and the Solar System.
* The pipeline reproduces the published a₀ = 1.20×10⁻¹⁰ m/s² (McGaugh+2016) under the published conventions (it gives 1.22).
* With distances and inclinations fixed, baryons plus a dark halo are preferred by BIC. This comparison isn't yet like-for-like (see the paper).

### Sharpened test: distance and inclination marginalized ([`sparc_marginalized_a0.py`](emergent_matter_model/sparc_marginalized_a0.py))

This follows the method of Li et al. (2018). It's validated as unbiased on known-answer tests and reproduces their a₀ ≈ 1.2.

| Sample | RAR law a₀ (10⁻¹⁰ m/s²) | vs cH₀/2π (H₀ = 67.4 / 73.0) | vs Λ-tied version (0.863) |
|---|---|---|---|
| All 153 galaxies | 1.234 ± 0.048 | **+4.0σ / +2.2σ** (tension) | +7.8σ |
| 66 gas-dominated galaxies | 1.019 ± 0.082 | −0.3σ / −1.3σ (consistent) | +1.9σ |

**Honest bottom line:** the hypothesis is **neither confirmed nor excluded**. Gas-dominated galaxies, the cleanest probe, agree with it. The full sample sits 2–4σ above it.

### Step 3: where the disagreement comes from ([`sparc_tension_diagnostics.py`](emergent_matter_model/sparc_tension_diagnostics.py))

| Subset (RAR law) | a₀ (10⁻¹⁰ m/s²) | vs cH₀/2π (67.4 / 73.0) |
|---|---|---|
| Star-dominated, **with bulges** (31 galaxies; post hoc) | 1.91 ± 0.18 | +4.8σ / +4.3σ |
| Star-dominated, **bulgeless** (56) | 0.894 ± 0.050 | −3.0σ / −4.7σ |
| Gas-dominated (66) | 1.019 ± 0.082 | −0.3σ / −1.4σ |
| All galaxies, deep points only (141) | 1.098 ± 0.062 | +0.9σ / −0.5σ |
| Bulgeless gas + star combined (post hoc) | 0.930 ± 0.042 | −2.7σ / −4.7σ |

* The gas-vs-star disagreement is really a **bulge-vs-bulgeless disagreement** (5.4σ, and 4.8σ even in the deep regime). Either bulge mass models are wrong, or a₀ isn't universal.
* Without bulges, gas- and star-dominated galaxies agree, at a₀ ≈ 0.93, which is *below* cH₀/2π.
* Defensible galaxy selections give a₀ ≈ 0.84–1.28. The measurement is **limited by stellar-mass systematics at ±15–20%**, so current SPARC mass models can't settle the hypothesis. The next lever is independent bulge and stellar mass estimates.

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
├── data/                      # Observational astrophysical data (28,700+ constraints total)
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
│   ├── jwst/                  # JWST NIRSpec & ALMA high-redshift disk kinematics (10 data points)
│   │   └── jwst_kinematics_sample.csv # Curated sample from z=1.52 to z=6.80
│   └── cosmology/             # Cosmological expansion & CMB acoustic peak benchmarks
│       ├── pantheon_plus_sample.csv  # Pantheon+ Type Ia SNe sample (32 binned points, z <= 2.26)
│       ├── desi_2024_bao.csv         # DESI 2024 BAO distance measurements (13 points, 7 tracers)
│       └── planck_2018_cmb_peaks.csv # Planck 2018 PR3 TT acoustic peak multipoles (l1, l2, l3)
├── notebooks/                 # Interactive Jupyter research dashboards
│   └── emrf_two_regime_validation.ipynb # Multi-regime empirical validation & horizon dashboard
├── paper/                     # Academic publication & dissemination package
│   ├── main.tex               # Formal academic preprint manuscript (9 sections)
│   ├── references.bib         # BibTeX database with verified DOIs
│   ├── package_submission.py  # Packaging & SHA-256 hash generation utility
│   ├── figures/               # 13 Multi-panel vector figures (fig1 through fig13)
│   ├── arxiv_submission.tar.gz / .zip # Submission-ready distribution archives with figures
│   ├── ARXIV_SUBMISSION.md    # arXiv metadata, abstract, and upload instructions
│   ├── COVER_LETTER.md        # Formal cover letter to PRD/CQG editors
│   └── AUTHOR_RESPONSES_FAQ.md # Theoretical FAQ guide pre-empting referee inquiries
├── RELEASE_DRAFT_v0.7.0.md    # Turnkey release notes and submission walkthrough
├── MODEL_CARD.md              # Model card classifying all system components into 5 tiers
├── CONTRIBUTING.md            # Codebase contribution and PR quality guidelines
├── tools/                     # Operational tools and interactive applications
│   ├── interactive_visualizer.html # Standalone interactive WebGL dashboard (10 tabs)
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
│   ├── cosmology_expansion.py # Late-time cosmic expansion engine (Pantheon+ & DESI BAO)
│   ├── stress_test_cosmology_expansion.py # Cosmology expansion stress test engine
│   ├── cmb_acoustic_engine.py # Early-universe relativistic CMB acoustic oscillation engine (z ~ 1100)
│   ├── stress_test_cmb_peaks.py # Planck 2018 PR3 CMB TT acoustic peaks stress test engine
│   ├── plot_publication_figures.py # Primary publication figures generator (Figs 1-4)
│   ├── plot_deep_perspectives.py   # Extended deep perspective figures generator (Figs 5-8)
│   ├── plot_extreme_rigor_figures.py # Extreme rigor figures generator (Figs 9-11)
│   ├── plot_cosmology_figures.py   # Cosmological frontiers figures generator (Figs 12-13)
│   ├── viz3d.py & visualize.py # 3D/2D spatial compression visualization with HTML export
│   ├── server.py              # Flask REST API with rate limiting and /visualizer endpoint
│   ├── wsgi.py & gunicorn.conf.py # Production WSGI server and multi-worker concurrency
│   ├── test_*.py              # 19 comprehensive unit test suites (159 tests, 100% passing)
│   └── compare_schwarzschild.py  # GR consistency check (headless-ready)
├── docs/                      # Research documents, audits, and visual assets
│   ├── assets/                # Visual assets and scientific illustrations
│   │   ├── emrf_hero_banner.jpg          # High-resolution hero banner
│   │   └── emrf_multiscale_regimes.jpg   # Multiscale empirical regimes illustration
│   ├── GRAND_DUE_DILIGENCE_AUDIT_CASE_001_EMRF.md # Sealed & Ratified Case 001 Audit Report (Level 5)
│   ├── GRAND_DUE_DILIGENCE_AUDIT_TEMPLATE.md      # Grand Due Diligence Audit Framework (v1.0.0)
│   ├── COSMOLOGICAL_FRONTIERS_PLAN.md             # Cosmological Frontiers Implementation Plan
│   ├── EMRF_MASTER_AUDIT_2026-10-05.md            # Master Comprehensive Audit Report
│   └── hypotheses/            # Frozen hypothesis specifications
├── knowledgebase/             # Graph memory & engineering handbooks
│   ├── GRAPH_MEMORY.json      # Machine-readable relational graph memory (v1.9.0)
│   ├── README.md              # Knowledgebase index & query guide
│   ├── theoretical_framework.md # Deep theoretical physics reference (manifold M^D, time t, state S)
│   ├── action_principle_derivation.md # Variational derivation of Branch A collapse & horizon entropy
│   ├── jwst_high_redshift_predictions.md # Cosmological horizon acceleration evolution a_0(z)
│   ├── gw170817_gravitational_wave_speed.md # Multi-messenger speed of gravity & conformal invariance
│   ├── wide_binary_gaia_external_field_effect.md # Gaia wide binaries & Galactic External Field Effect
│   ├── hamiltonian_stability_and_ghost_absence.md # Ostrogradsky stability & subluminal sound speed
│   ├── equivalence_principle_and_microscope_bounds.md # Weak Equivalence Principle & MICROSCOPE bounds
│   ├── cosmological_expansion_pantheon_desi.md # Void spatial metric compression, Pantheon+ & DESI BAO
│   ├── cmb_acoustic_oscillations_early_universe.md # Early-universe CMB acoustic oscillations & 3rd peak
│   ├── software_architecture.md # Software engineering handbook (159 tests, CI/CD)
│   └── empirical_validation_pipeline.md # Complete 10-regime empirical validation guide
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
cd SpaceEntropyCompression

# Run the test suite (203 tests)
python -m pytest emergent_matter_model -q

# REAL DATA: download SPARC (checksummed) and test a0 = c H0 / 2 pi with four candidate laws
python emergent_matter_model/sparc_real_analysis.py      # ~1 minute; writes results/ and paper/figures/

# Sharpened test: marginalize distance + inclination (Li et al. 2018 method)
python emergent_matter_model/sparc_marginalized_a0.py    # ~12 minutes

# Diagnose the gas- vs star-dominated disagreement (bulges, deep points)
python emergent_matter_model/sparc_tension_diagnostics.py  # ~20 minutes

# Reproduce every number in the audit (docs/SHOW_YOUR_WORK.md)
python tools/show_your_work_audit.py

# Code demonstrations on SYNTHETIC fixtures (print a warning banner; not scientific results)
python emergent_matter_model/fit_astrometry.py --dataset all
python emergent_matter_model/fit_sparc.py --galaxy all
python emergent_matter_model/fit_jwst.py
```

## Theoretical Foundation

EMRF investigates three competing compression formulations:

| Branch | Formulation | What It Tests |
|--------|------------|---------------|
| $C_G$ | Geometry-dominated | Is compression ≡ spacetime curvature? |
| $C_E$ | Energy-bounded | Is compression ≡ quasi-local gravitational energy? |
| $C_S$ | Entropy-coupled | Does entropy/information dictate gravitational dynamics? |
| $C_{GSE}$ | Composite | Are all three needed? (Only if simpler branches fail) |

## Empirical status by regime

| # | Regime | Status after the audit |
|---|---|---|
| 1 | Sgr A* S-stars | No valid result (synthetic data; no fitting). EMRF is *required* to equal GR here, so these orbits can't discriminate it. |
| 2 | Solar System | Constraint: the earlier EMRF law fails. RAR-like laws pass (EFE quadrupole not yet evaluated). |
| 3 | **SPARC rotation curves** | **Real-data tests done.** a₀ = cH₀/2π is neither confirmed nor excluded. The gas/star disagreement traces to bulge galaxies (5σ), and a₀ is systematics-limited at ±15–20%. The earlier EMRF law is disfavoured. |
| 4 | Strong lensing | The code used the standard GR formula; no EMRF prediction exists yet. |
| 5 | Bullet Cluster | Hand-tuned toy model; withdrawn. MOND-type laws leave residual missing mass (Angus+2007). |
| 6 | High-z disks (a₀ ∝ H(z)) | No valid result (synthetic data). Existing studies disfavour strong evolution (Genzel+2017; Nestor Shachar+2023). |
| 7 | GW170817 | The result was asserted in code, not computed. |
| 8 | Gaia wide binaries | No valid result (hand-entered bins). The literature is contested and leans Newtonian (Banik+2024). |
| 9 | Cosmic expansion | Standard w₀w_a dark energy relabelled; not an EMRF prediction. DESI table corrected. |
| 10 | CMB peaks | Circular (peak heights hard-coded; assumes a CDM-like density). Needs a relativistic completion (cf. AeST). |

Open theoretical task: derive an RAR-like interpolating function from an action. The canonical entropy-field Lagrangian can't do it ([`knowledgebase/action_principle_derivation.md`](knowledgebase/action_principle_derivation.md)).

## Status

* **Paper:** [`paper/main.tex`](paper/main.tex) (revised 2026-10-07; real-data SPARC test; correction statement). [`paper/use_case_lasalle_ontology.tex`](paper/use_case_lasalle_ontology.tex) is conceptual; its empirical claims are withdrawn.
* **Audit:** [`docs/SHOW_YOUR_WORK.md`](docs/SHOW_YOUR_WORK.md).
* **Tests:** 203 passing. Note that many older tests only check internal consistency, not physics.
* **Community Ethics Charter:** [`docs/COMMUNITY_ETHICS.md`](docs/COMMUNITY_ETHICS.md).
* Older planning and status documents (STATUS, ROADMAP, earlier audits) carry an integrity notice at the top.

## Citation

If you use EMRF in your research, please cite:

```bibtex
@software{lasalle2026emrf,
  author = {LaSalle, Kirk},
  title = {Emergent Matter Research Framework (EMRF)},
  year = {2026},
  url = {https://github.com/kirklasalle/SpaceEntropyCompression},
  version = {0.10.0}
}
```

## Key References

1. Jacobson, T. (1995). "Thermodynamics of Spacetime: The Einstein Equation of State." *PRL* 75, 1260.
2. Brown, J.D. & York, J.W. (1993). "Quasilocal energy and conserved charges." *PRD* 47, 1407.
3. GRAVITY Collaboration (2022). "Mass distribution in the Galactic Centre." *A&A* 657, L12.
4. GRAVITY Collaboration (2026). "Discovery of a star sensitive to the spin of Sgr A*." *Nature*; arXiv:2607.12664.
6. McGaugh, S., Lelli, F. & Schombert, J. (2016). "Radial Acceleration Relation in Rotationally Supported Galaxies." *PRL* 117, 201101.
7. Lelli, F., McGaugh, S. & Schombert, J. (2016). "SPARC: Mass Models for 175 Disk Galaxies." *AJ* 152, 157.
8. Milgrom, M. (1999). "The modified dynamics as a vacuum effect." *Phys. Lett. A* 253, 273.
5. Verlinde, E. (2011). "On the Origin of Gravity and the Laws of Newton." *JHEP* 2011(4), 29.

## License

MIT License — Copyright (c) 2026 Kirk LaSalle

## Author

**Kirk LaSalle** — Principal Investigator and Author of the Compressed Space-Time Matter Hypothesis
