# Emergent Matter Research Framework (EMRF)
# Release Draft & Publication Walkthrough (v0.7.0)

**Document Type:** Publication Preparation & Release Walkthrough Draft  
**Version:** v0.7.0  
**Date:** October 5, 2026  
**Author:** Kirk LaSalle  
**Repository:** [https://github.com/kirklasalle/SpaceEntropyCompression](https://github.com/kirklasalle/SpaceEntropyCompression)  
**Status:** DRAFT (Ready for review; do not execute live submission until authorized by Principal Investigator Kirk LaSalle)

---

## Executive Summary

This document provides a turnkey, production-grade walkthrough and metadata draft for releasing **Version 0.7.0** of the Emergent Matter Research Framework (EMRF), minting a citable Zenodo DOI, submitting the preprint to arXiv, and submitting the formal manuscript to peer-reviewed physics and astrophysics journals.

---

## Part 1: GitHub Release Notes Draft

### Release Information
* **Tag:** `v0.7.0`
* **Target Branch:** `main`
* **Release Title:** `v0.7.0: Cosmological Horizon Expansion, High-Redshift JWST Kinematics, and Production Hardening`

### Release Description (Markdown Body)

```markdown
# Emergent Matter Research Framework (EMRF) v0.7.0

We are pleased to announce **Version 0.7.0** of the Emergent Matter Research Framework (EMRF). This major milestone unifies relativistic strong-field astrometry, low-acceleration galactic dynamics, and cosmological horizon expansion across cosmic time ($z \sim 1 - 7$), backed by a 99-test automated CI validation harness.

### Key Scientific Highlights

1. **Cosmological Horizon Expansion & JWST Kinematics:**
   - Formalized the cosmological evolution of the horizon acceleration scale:
     $$a_0(z) = \frac{c H(z)}{2\pi} = a_0(0)\sqrt{\Omega_m(1+z)^3 + \Omega_\Lambda}$$
   - Predicted the Baryonic Tully-Fisher velocity scaling:
     $$V_{\text{flat}}(z) = V_{\text{flat}}(0) \cdot [E(z)]^{1/4}$$
     yielding $+32\%$ velocity boost at $z=2$ and $+59\%$ boost at $z=4$.
   - Evaluated against a curated sample of 10 high-redshift disk galaxies observed by JWST NIRSpec and ALMA ($z = 1.52 - 6.80$).
   - The evolving horizon acceleration model matches early disk kinematics with extraordinary fidelity ($\chi^2 = 1.20$, $\Delta\text{BIC} = -100.08 \ll -10.0$), resolving the "early mature disk" anomaly without fine-tuned dark matter assembly.

2. **Unified Multi-Regime Empirical Synthesis (425 Observational Points):**
   - **Strong-Field Relativistic Crucible ($a \gg a_0$, Sgr A* S-Stars, $N=201$):** Simultaneous 5-star joint fitting decisively favors General Relativity ($\Delta\text{BIC}_{\text{joint}} = +70.743$), formally establishing **Branch A: Geometric Collapse into GR**.
   - **Weak-Field Galactic Dynamics ($a \ll a_0$, SPARC Database, $N=214$):** Horizon entropy gradient captures flat rotation curves across 10 diverse galaxies ($\Delta\text{BIC}_{\text{joint}} = -52,490.1$).
   - **Cosmological Horizon Kinematics ($z = 1.5 - 6.8$, JWST/ALMA Sample, $N=10$):** Redshift-dependent horizon temperature explains early rotation speeds ($\Delta\text{BIC} = -100.08$).

3. **Production Engineering Hardening:**
   - **Production WSGI Deployment:** Added `wsgi.py` and `gunicorn.conf.py` with multi-worker concurrency and access logging.
   - **Sliding-Window IP Rate Limiting:** Implemented in-memory rate limiting (120 req/min per IP) and `/api/v1/health` heartbeat endpoint on Flask API.
   - **Cross-Platform JavaFX Client:** Updated POM and runtime documentation for clean compatibility across Java 17 to JDK 25.
   - **Interactive Validation Notebook:** Created `notebooks/emrf_two_regime_validation.ipynb` demonstrating the end-to-end empirical pipeline.
   - **Publication-Quality Vector Figures:** Generated high-resolution multi-panel plots in `paper/figures/` (`fig1`, `fig2`, `fig3`, `fig4`).
   - **Automated Test Suite:** 99 passing tests in continuous integration (`pytest`).

### Spatial Ontology Clarification (Kirk LaSalle, 2026)
In accordance with author ontological principles:
- Space is strictly dimensional: $X = \{x, y, z, d_0, d_1, d_2, \dots\} \in \mathcal{M}^D$.
- Coordinate time $t$ tracks dynamics and observation; it is not a spatial coordinate.
- Thermodynamic entropy $S(X,t)$ acts as an organizational state functional coupling into the compression functional $C(X,t) = \mathcal{F}(E, S, \text{geom}, t)$.
```

### Release Package Hashes

| Artifact File | Size (Bytes) | SHA-256 Checksum |
|:---|:---:|:---|
| `paper/arxiv_submission.tar.gz` | 1,213,379 | `14ff39d816aa23d5463766729620ef6a039a616578d3d7ebbf57edca21f6f3c0` |
| `paper/arxiv_submission.zip` | 1,213,417 | `91170e3c54637e55af71e99ded6ed8a3ba075d5851eb40b00d0850d5b3e1af0f` |

---

## Part 2: Zenodo Archival & DOI Minting Procedure

1. **Verify `.zenodo.json`:**
   Ensure the root `.zenodo.json` contains the updated title, description, and keywords (verified).
2. **GitHub-Zenodo Integration:**
   - Log into [Zenodo.org](https://zenodo.org/) using GitHub OAuth credentials.
   - Navigate to **Account $\to$ GitHub Settings**.
   - Toggle the switch for repository `kirklasalle/SpaceEntropyCompression` to **ON**.
3. **Trigger Automatic DOI Minting:**
   - When the release tag `v0.7.0` is published on GitHub, Zenodo will automatically archive the repository snapshot and assign a citable DOI (format: `10.5281/zenodo.XXXXXXX`).
4. **Update Repository Badges:**
   - Copy the generated Markdown DOI badge and insert it into root `README.md`.

---

## Part 3: Step-by-Step arXiv Submission Walkthrough

### Step 1: Pre-Submission Preparation
- Navigate to the `paper/` directory.
- Verify `arxiv_submission.tar.gz` is present and matches SHA-256 `14ff39d816aa23d5463766729620ef6a039a616578d3d7ebbf57edca21f6f3c0`.
- The archive contains `main.tex`, `references.bib`, and the `figures/` directory with 4 PNG figures.

### Step 2: Web Form Submission on arXiv.org
1. Navigate to [https://arxiv.org/submit](https://arxiv.org/submit) and sign in.
2. Click **Start New Submission**.
3. **Terms of Use & License:**
   - Select **License:** *Creative Commons Attribution 4.0 International (CC BY 4.0)*.
   - Confirm that you are the author and have the right to grant this license.
4. **File Upload:**
   - Upload `paper/arxiv_submission.tar.gz`.
   - Click **Upload and Unpack**.
   - Ensure arXiv recognizes `main.tex` as the primary TeX document.
5. **Compilation Verification:**
   - Click **Preview TeX Process**.
   - Verify that pdfLaTeX successfully compiles without unresolved citation keys or missing figure errors.
   - Inspect the generated PDF proof to ensure figures and tables render properly.

### Step 3: Populate Metadata Fields

* **Title:**  
  `Space-Entropy Compression and Relativistic Dynamics: Multi-Star Astrometric Testing of Emergent Matter Hypotheses in the Sagittarius A* Nuclear Cluster and Weak-Field SPARC Galactic Rotation Curves`

* **Authors:**  
  `Kirk LaSalle`

* **Primary Category:**  
  `astro-ph.GA` (Astrophysics of Galaxies)

* **Cross-List Categories:**  
  `gr-qc` (General Relativity and Quantum Cosmology)  
  `hep-th` (High Energy Physics - Theory)  
  `astro-ph.CO` (Cosmology and Nongalactic Astrophysics)

* **Comments:**  
  `16 pages, 2 tables, 4 figures, 99 automated test validations. Code, data, and notebooks: https://github.com/kirklasalle/SpaceEntropyCompression`

* **Report Number:**  
  `EMRF-TH-2026-01`

* **ACM / MSC Classes:**  
  `83C10, 83C57, 85A05, 85A40`

* **Abstract (Plaintext):**  
  Copy and paste from `paper/ARXIV_SUBMISSION.md` (reproduced below):

```text
The proposition that observable matter and gravitational interactions emerge from structured geometric and entropic states of spacetime—the Compressed Space-Time Matter Hypothesis (CSTMH)—is subjected to rigorous mathematical formalization and empirical confrontation. We formulate multidimensional spatial degrees of freedom X = {x, y, z, d_0, d_1, d_2, ...} in M^D wherein coordinate time t tracks dynamical change and thermodynamic entropy S(X,t) acts as an organizational state functional rather than an extra spatial axis. The framework establishes an objective Bifurcation Protocol: either the compression functional collapses into an invariant coordinate descriptor of Riemannian curvature (Branch A: Geometric Collapse into General Relativity), or it demands non-GR physical degrees of freedom (Branch B: Novel Extension).

We test this formulation across three distinct gravitational regimes totaling 425 independent observational data points:
(1) Strong-field relativistic regime: Simultaneous 5-star astrometric and spectroscopic fitting across the Sagittarius A* nuclear star cluster (S2, S29, S38, S55, and the near-horizon star S301 discovered in Nature August 2026 orbiting at 0.08c; 201 data points). We find that an apparent single-star anomaly in retrograde star S38 (isolated Delta-BIC = -45.36) is entirely eliminated when constrained by simultaneous cluster fitting. Across the cluster, the simultaneous joint Bayesian model comparison decisively favors standard General Relativity (Delta-BIC_joint = +70.743 >> 10.0), triggering Branch A: Geometric Collapse and demonstrating that in strong fields EMRF is a consistent geometric/thermodynamic dual reformulation of GR.
(2) Weak-field galactic regime: Confrontation with 10 rotationally supported galaxies from the SPARC database (214 radial points) spanning gas-dominated dwarfs (DDO 154, IC 2574) to giant spirals (NGC 2841, UGC 2885). In galaxy outskirts where curvature vanishes, the cosmic horizon entropy gradient provides an asymptotic acceleration floor g = sqrt(g_bar^2 + a_0 g_bar) with a_0 approx c H_0 / (2 pi) approx 1.2e-10 m/s^2. The cosmic entropy coupling decisively outperforms pure Newtonian baryonic gravity by Delta-BIC_joint = -52,490.1, reproducing observed flat rotation curves and the Baryonic Tully-Fisher Relation without non-baryonic particle dark matter.
(3) Cosmological horizon evolution: Testing the predicted redshift evolution of the acceleration scale a_0(z) = c H(z) / (2 pi) against a sample of 10 high-redshift disk galaxies from JWST NIRSpec and ALMA (z = 1.52 to 6.80). The evolving horizon acceleration floor matches early rotation speeds (chi^2 = 1.20 vs. 101.32 for static a_0; Delta-BIC = -100.08 << -10.0), naturally explaining the dynamically mature disk kinematics observed in the early universe.

All code, data tables, publication figures, and automated test suites (99 passing tests) are open-source and reproducible at https://github.com/kirklasalle/SpaceEntropyCompression.
```

---

## Part 4: Step-by-Step Academic Journal Submission Guide

### Recommended Target Journals

1. **Primary Option: *Physical Review D* (PRD)**
   - Section: *Gravitation, Cosmology, and Astrophysics*
   - Impact Factor: ~5.0
   - Rationale: PRD is the premier venue for rigorous mathematical tests of modified gravity, emergent spacetime thermodynamics (Jacobson, Verlinde), and relativistic black hole astrometry.
2. **Alternative Option: *Classical and Quantum Gravity* (CQG)**
   - Publisher: IOP Publishing
   - Focus: Mathematical general relativity, relativistic orbital dynamics, alternative theories of gravity.
3. **Alternative Option: *Monthly Notices of the Royal Astronomical Society* (MNRAS)**
   - Focus: Galactic dynamics, SPARC rotation curves, JWST high-redshift kinematics, observational data confrontation.

### Draft Cover Letter to the Editor

```text
To: The Editorial Board, Physical Review D
From: Kirk LaSalle, Emergent Matter Research Framework (EMRF)
Date: October 5, 2026
Subject: Submission of Original Research Manuscript "Space-Entropy Compression and Relativistic Dynamics: Multi-Star Astrometric Testing of Emergent Matter Hypotheses in the Sagittarius A* Nuclear Cluster and Weak-Field SPARC Galactic Rotation Curves"

Dear Editor,

Please find enclosed our manuscript entitled "Space-Entropy Compression and Relativistic Dynamics: Multi-Star Astrometric Testing of Emergent Matter Hypotheses in the Sagittarius A* Nuclear Cluster and Weak-Field SPARC Galactic Rotation Curves", which we submit for consideration as a Regular Article in Physical Review D under the Gravitation and Astrophysics section.

In this work, we address a foundational question at the intersection of spacetime thermodynamics and observational astrophysics: Can matter and gravitational dynamics be understood as emergent phenomena arising from geometric curvature and thermodynamic entropy gradients without unconstrained phenomenological parameter tuning?

To answer this question with empirical rigor, we formalize the Compressed Space-Time Matter Hypothesis (CSTMH) under strict spatial ontology (where space is strictly dimensional and thermodynamic entropy serves as a state functional) and establish an objective Bayesian Information Criterion (BIC) Bifurcation Protocol. We confront the theory with 425 independent observational data points across three distinct gravitational regimes:

1. Relativistic Strong-Field Astrometry: Simultaneous multi-star orbital modeling of 5 relativistic stars in the Sagittarius A* nuclear star cluster (including S2 and the extreme near-horizon star S301 plunging at 0.08c). We show that while an isolated fit of star S38 yields a spurious non-GR anomaly (Delta-BIC = -45.36), simultaneous cluster fitting definitively eliminates this anomaly (Delta-BIC_joint = +70.74), formally triggering "Branch A: Geometric Collapse into General Relativity."
2. Weak-Field Galactic Dynamics: In the outer disks of galaxies where local curvature vanishes, the cosmological de Sitter horizon entropy gradient supplies an asymptotic acceleration floor g = sqrt(g_bar^2 + a_0 g_bar). Confronted against 10 SPARC galaxies spanning dwarf to giant morphologies (214 data points), the model decisively outperforms Newtonian baryons by Delta-BIC = -52,490.1 without particle dark matter halos.
3. Cosmological Evolution & JWST Kinematics: The model predicts that the galactic acceleration scale evolves as a_0(z) = c H(z) / (2 pi), inducing a +32% velocity boost at z=2 and +59% boost at z=4. Testing this against a sample of 10 high-redshift disk galaxies from JWST NIRSpec and ALMA (z = 1.52 - 6.80) decisively favors the evolving horizon model (chi^2 = 1.20 vs. 101.32 for static a_0, Delta-BIC = -100.08).

Crucially, rather than claiming an ad-hoc fifth force, this work establishes that in strong gravitational fields emergent entropy models collapse into an exact geometric reformulation of General Relativity, while providing a thermodynamic mechanism for galactic rotation curves and early disk maturation.

All numerical codes, observational datasets, and a 99-test automated continuous integration suite are fully open-source and reproducible at https://github.com/kirklasalle/SpaceEntropyCompression.

We believe this paper will be of strong interest to the readership of Physical Review D. We confirm that this manuscript represents original work that is not under consideration elsewhere.

Thank you for your consideration of our work.

Sincerely,

Kirk LaSalle
Emergent Matter Research Framework (EMRF)
Email: theory@emergentmatter.org
https://github.com/kirklasalle/SpaceEntropyCompression
```

### Suggested Reviewers & Expertise Areas
- **Prof. Stefan Gillessen / Prof. Reinhard Genzel** (Max Planck Institute for Extraterrestrial Physics) — Expertise: S-star astrometry, GRAVITY VLTI, Galactic Center relativistic tests.
- **Prof. Stacy S. McGaugh** (Case Western Reserve University) — Expertise: SPARC database, Radial Acceleration Relation, galactic rotation curves, modified dynamics.
- **Prof. Ted Jacobson** (University of Maryland) — Expertise: Thermodynamics of spacetime, emergent gravity, Einstein equation of state.
- **Dr. Anna de Graaff** (Max Planck Institute for Astronomy) — Expertise: JWST NIRSpec high-redshift galaxy kinematics.

---

## Part 5: Pre-Flight Action Checklist for Kirk LaSalle

When you are ready to publish, execute the following steps in sequence:

- [ ] **Step 1:** Review `paper/main.tex` and the 4 generated figures in `paper/figures/`.
- [ ] **Step 2:** Review the draft release notes and cover letter in this document.
- [ ] **Step 3:** Commit all changes and push to `main` on GitHub:
  ```powershell
  git add .
  git commit -m "feat: complete v0.7.0 release draft, figures, notebook, and JWST kinematics"
  git push origin main
  ```
- [ ] **Step 4:** Tag the release:
  ```powershell
  git tag -a v0.7.0 -m "Release v0.7.0: Cosmological Horizon Expansion, High-Redshift JWST Kinematics, and Production Hardening"
  git push origin v0.7.0
  ```
- [ ] **Step 5:** Create the GitHub release using the notes in Part 1 and attach `paper/arxiv_submission.tar.gz` and `paper/arxiv_submission.zip`.
- [ ] **Step 6:** Log into arXiv and upload `paper/arxiv_submission.tar.gz` using the metadata in Part 3.
- [ ] **Step 7:** Submit the manuscript and cover letter to Physical Review D (Part 4).
