# EMRF Knowledgebase & Graph Memory System

## Current engineering and library entry points

- [Scientific data/software library](library/README.md), including the
  [data catalog](library/data_catalog.json) and
  [software catalog](library/software_catalog.json).
- [Current build reference](../docs/engineering/CURRENT_BUILD_REFERENCE.md).
- [Engineering specification](../docs/engineering/ENGINEERING_SPECIFICATION.md).
- [Formalization implementation plan](../docs/engineering/FORMALIZATION_IMPLEMENTATION_PLAN.md).

## Current recovered-evidence entry points

- [Candidate A functional comparison](../docs/EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md):
  precise definitions, normalization, vacuum/radiation counterexamples and a
  recommended local energy reference awaiting author selection. These are
  mathematical diagnostics, not new observational results. Section 11 records
  the one observational test of A: option 2 (M = observed baryons), proposed by
  the assistant while Kirk was unavailable, was rejected on SPARC under the
  frozen `candidate_a_sparc_baryonic_test_preregistration.json`. That test was
  not blind and falsifies option 2 only.

- [Collision candidate specification](../docs/EMRF_COLLISION_CANDIDATE_SPECIFICATION.md)
  and [candidate ledger](thermodynamic_collision_candidates.json): Kirk selected
  A and B as research candidates (October 16, 2026), and they now run
  concurrently as a [dual-candidate program](../docs/EMRF_DUAL_CANDIDATE_PROGRAM.md).
  A's exact functional remains unspecified.
  B's restricted Higgs-portal tests give bounds, not empirical validation; see the
  [dimensionality exploration](../docs/engineering/CANDIDATE_B_DIMENSIONALITY_EXPLORATION_2026-10-13.md)
  and [draft model contract](../docs/engineering/CANDIDATE_B_MODEL_CONTRACT_DRAFT_2026-10-13.md).
  The B tests are pinned by two frozen preregistrations and a theory-input
  table in this folder (`candidate_b_*.json`). Do not edit them; `.gitattributes`
  keeps their bytes, and so their SHA-256 freezes, identical on every platform.
  Neither selection nor a proposal is observational confirmation.

- [Antigravity recovery audit](../docs/ANTIGRAVITY_RECOVERY_AUDIT.md): search
  coverage, preserved sources, original conceptual distinctions and limits.
- [Recovered theory intentions](antigravity_recovered_theory.md): downstream
  thermodynamics, separate geometric entropy, C families, U and multi-star design.
- [Curated claim ledger](antigravity_recovery_claims.json) and
  [qualified graph](GRAPH_MEMORY.json): source hashes and attribution, not
  historical AI certification.

The graph content is now v2.1.0 under the versioned
[`GRAPH_MEMORY.schema.json`](GRAPH_MEMORY.schema.json) format. Legacy nodes are
preserved but explicitly marked as historical or source-review-dependent.
Every node has one canonical kind, every edge carries confidence, evidence
class and provenance, and claim nodes use the lifecycle `proposed`, `tested`,
`supported`, `refuted` or `retracted`. Conditions, inheritance overrides and
explicit conflicts are schema-supported. In particular, old "validated"
dataset labels and `validated_by` relationships must not be used as current
empirical evidence. The old graph has been preserved in the recovery archive.

The supported interfaces are:

```text
emrf kb validate [--json]
emrf kb query [TEXT] [--kind KIND] [--status STATUS] [--json]
emrf kb add-source source:ID --title TITLE --author AUTHOR --year YEAR \
  (--doi DOI | --arxiv ID | --ads-bibcode CODE) \
  --snapshot-sha256 SHA256 --bibtex-file FILE
emrf kb export --output FILE
emrf kb link-run RUN_ID [--claim ID] [--source ID] [--dataset ID]
```

`link-run` accepts only terminal durable runs, discovers and hashes regular,
non-symlink artifacts, and creates the run -> result -> claim, claim -> source
and run -> dataset links atomically. Re-linking rejects any artifact whose
published bytes changed. New literature sources require a stable
identifier, pinned retrieval-snapshot hash and BibTeX. REST v2 provides the
same query, validation, export, source-registration and run-linking operations;
mutations retain the v2 bearer-token requirement.
The directory tree and version descriptions below are historical.

> **Integrity notice (2026-10-07).** This document predates the independent audit in [`docs/SHOW_YOUR_WORK.md`](../docs/SHOW_YOUR_WORK.md). Empirical results quoted here (for example S-star ΔBIC = +70.743 or +141.3, SPARC ΔBIC = −52,490.1, JWST ΔBIC = −100.08, wide-binary ΔBIC = −60.26, CMB χ²ᵥ = 0.924, "28,700+ observational constraints") were computed from synthetic data files (now quarantined in [`data/synthetic/`](../data/synthetic/README.md)) or from code whose answer was built in, so they **must not be cited**. "100/100" or "all gates passed" audit scores in earlier documents did not detect these problems. Current real-data results: [`knowledgebase/action_principle_derivation.md`](action_principle_derivation.md) §4.3.

> **Current status (2026-11-03).** Use the current entry points at the top of this file, [STATUS.md](../STATUS.md), [MODEL_CARD.md](../MODEL_CARD.md), the [dual-candidate program](../docs/EMRF_DUAL_CANDIDATE_PROGRAM.md), and the [project audit](../docs/site/development/project-audit-2026-11-03.md). Everything below this notice is legacy context and is not a current catalog of files or scientific conclusions. The historical JWST sample path is absent from this checkout.

**Project:** Emergent Matter Research Framework (EMRF) / Space-Entropy Compression  
**Repository:** [kirklasalle/SpaceEntropyCompression](https://github.com/kirklasalle/SpaceEntropyCompression)<br>
**Authors:** Kirk LaSalle & Antigravity  
**Version:** 1.6.0 (October 2026)  

---

## 1. Purpose & Architecture

The EMRF Knowledgebase is an integrated theoretical, computational, and empirical intelligence repository designed to maintain continuity across development sessions, preserve institutional research memory, and empower autonomous agents and human researchers alike.

It couples **machine-readable graph memory** (`GRAPH_MEMORY.json`) with **deep-dive reference manuals**:

The following legacy tree is illustrative only; it is not an inventory of
files present in this checkout.

```
<repository-root>/
├── data/
│   ├── astrometry/                      # Sgr A* S-star cluster observations (201 data points)
│   │   ├── s2_gravity_vlti.csv          # ESO VLT/GRAVITY observations for star S2 (2002–2022)
│   │   ├── s29_gravity_vlti.csv         # ESO VLT/GRAVITY observations for star S29 (2012–2024)
│   │   ├── s38_gravity_vlti.csv         # ESO VLT observations for retro-orbit star S38 (2003–2022)
│   │   ├── s55_gravity_vlti.csv         # ESO VLT observations for star S55 / S0-102 (2004–2022)
│   │   └── s301_nature_2026.csv         # Nature August 2026 observations for star S301 (8.7 yr, 0.08c)
│   ├── sparc/                           # SPARC galactic rotation curve observations (214 data points)
│   │   ├── sparc_sample_summary.csv     # Master summary table of 10 archetype galaxies
│   │   ├── ddo154.csv, ic2574.csv       # Gas-dominated dwarf irregulars
│   │   ├── ngc1560.csv                  # Low surface brightness dwarf with feature matching
│   │   ├── ngc2403.csv, ngc2903.csv     # Intermediate spirals with extended HI
│   │   ├── ngc3198.csv, ngc6503.csv     # Canonical rotation curve benchmarks
│   │   └── ngc2841.csv, ngc7331.csv, ugc2885.csv # Massive spirals and giants
│   └── jwst/                            # Historical directory; cited sample is absent from this checkout
├── notebooks/
│   └── emrf_two_regime_validation.ipynb # Interactive Jupyter validation & horizon dashboard
├── paper/                               # Academic publication & dissemination package
│   ├── main.tex                         # Complete formal academic preprint manuscript
│   ├── references.bib                   # BibTeX database with DOIs
│   ├── package_submission.py            # Automated packaging & hash generation utility
│   ├── figures/                         # Multi-panel vector figures (fig1, fig2, fig3, fig4)
│   ├── arxiv_submission.tar.gz / .zip   # Submission-ready distribution archives with figures
│   ├── ARXIV_SUBMISSION.md              # arXiv metadata, abstract, and upload instructions
│   ├── COVER_LETTER.md                  # PRD / CQG journal cover letter
│   └── AUTHOR_RESPONSES_FAQ.md          # Reviewer response and theoretical FAQ guide
├── RELEASE_DRAFT_v0.7.0.md              # Turnkey release notes and submission walkthrough
├── MODEL_CARD.md                        # Model card classifying all components and outputs
├── CONTRIBUTING.md                      # Codebase contribution and PR quality guidelines
├── knowledgebase/
│   ├── GRAPH_MEMORY.json                # Machine-readable relational graph (v1.6.0)
│   ├── README.md                        # Directory index & operational guide (this file)
│   ├── theoretical_framework.md         # Theoretical physics foundation (M^D, t, S, Lagrangian)
│   ├── action_principle_derivation.md   # Variational derivation of Branch A collapse & horizon entropy
│   ├── jwst_high_redshift_predictions.md# Cosmological horizon acceleration evolution a_0(z)
│   ├── software_architecture.md         # Software engineering handbook (99 unit tests)
│   └── empirical_validation_pipeline.md # Observational astrophysics benchmarks (425 data points total)
```

---

## 2. Using the Graph Memory (`GRAPH_MEMORY.json`)

`GRAPH_MEMORY.json` contains a structured schema of:
- **`Concept` Nodes:** Foundational theoretical concepts (Multidimensional Space, Entropy State Variable, Emergent Matter, Bifurcation, Multi-Star Joint Fitting, Cosmological Horizon Evolution).
- **`Equation` Nodes:** Exact mathematical formulations with parameters and LaTeX definitions.
- **`SoftwareComponent` Nodes:** Code modules (`model.py`, `physics_baseline.py`, `fit_astrometry.py`, `fit_sparc.py`, `fit_jwst.py`, `plot_publication_figures.py`, `wsgi.py`, `package_submission.py`), APIs, GUI clients, and validation harnesses (99 tests).
- **`EmpiricalDataset` Nodes:** Observational targets (Sgr A* 5-star cluster with 201 points; SPARC 10-galaxy catalog with 214 points; JWST 10-galaxy sample with 10 points).
- **`Publication` & `ArchivalRelease` Nodes:** Formal preprint manuscript (`paper/main.tex`), arXiv package (`ARXIV_SUBMISSION.md`), cover letter (`COVER_LETTER.md`), Zenodo metadata (`.zenodo.json`, `CITATION.cff`), and release draft (`RELEASE_DRAFT_v0.7.0.md`).
- **`LiteratureReference` Nodes:** Published academic papers (Jacobson 1995, Verlinde 2011, Sakharov 1967, Bianconi 2026, Nature S301 2026, SPARC 2016, RAR 2016, Planck 2018, de Graaff 2024).
- **`Edges`:** Typed semantic relationships (`formulated_by`, `implemented_in`, `validated_by`, `evaluates_delta_bic`, `theoretical_precedent`).

---

## 3. Knowledgebase Map & Deep References

| Document | Primary Domain | Key Topics Covered |
|:---|:---|:---|
| [theoretical_framework.md](theoretical_framework.md) | Physics & Math | Historical ontology and proposed formulations; consult current candidate contracts for status. |
| [action_principle_derivation.md](action_principle_derivation.md) | Variational Theory | Historical theoretical development; not a current derivation or empirical confirmation. |
| [jwst_high_redshift_predictions.md](jwst_high_redshift_predictions.md) | Cosmology | Historical predictions; no current JWST sample is cataloged in this checkout. |
| [solar_system_screening_and_cassini_bounds.md](solar_system_screening_and_cassini_bounds.md) | Precision Astrophysics | Historical proposed constraints; not a current completed test. |
| [gravitational_lensing_and_geodesic_deflection.md](gravitational_lensing_and_geodesic_deflection.md) | Relativistic Optics | Historical proposed model; use current evidence documents for executed results. |
| [bullet_cluster_entropy_separation.md](bullet_cluster_entropy_separation.md) | Cluster Astrophysics | Historical proposal and illustration; the collision module remains not tested. |
| [gw170817_gravitational_wave_speed.md](gw170817_gravitational_wave_speed.md) | Relativistic Gravitation | Historical proposal; assigning a parameter to the observed value is not an independent test. |
| [wide_binary_gaia_external_field_effect.md](wide_binary_gaia_external_field_effect.md) | Stellar Dynamics | Historical analysis; consult current real-data reports for qualified results. |
| [hamiltonian_stability_and_ghost_absence.md](hamiltonian_stability_and_ghost_absence.md) | Field Theory | Historical analysis; no general covariant completion is established. |
| [equivalence_principle_and_microscope_bounds.md](equivalence_principle_and_microscope_bounds.md) | Experimental Relativity | Historical analysis; not a current independent test of the candidates. |
| [software_architecture.md](software_architecture.md) | Software Engineering | Historical architecture notes; current interfaces and test commands are documented in the root guides. |
| [empirical_validation_pipeline.md](empirical_validation_pipeline.md) | Astrophysics | Historical plan; synthetic benchmark results are withdrawn and the cited JWST sample is absent. |
| [MODEL_CARD.md](../MODEL_CARD.md) | Model Governance | Current evidence classes and limitations. |
| [RELEASE_DRAFT_v0.7.0.md](../RELEASE_DRAFT_v0.7.0.md) | Dissemination | Historical release draft; not current release instructions. |
| [interactive_visualizer.html](../tools/interactive_visualizer.html) | Interactive WebGL | Historical illustration; not an observational result. |

---

## 4. Governance & Update Protocol

1. **Synchronized Updates:** When adding a new mathematical model or software module, register the node and its relationships in `GRAPH_MEMORY.json`.
2. **Citation Preservation:** Any theoretical claim must reference either established literature or note its status as speculative/ansatz.
3. **Preserve Scientific Honesty:** Never remove negative experimental outcomes. If Bayesian model comparison rejects a parameter set, archive the negative result in the empirical pipeline.
