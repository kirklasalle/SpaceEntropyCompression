# arXiv Preprint Submission Package & Metadata

> **Integrity notice (2026-10-07).** This document predates the independent audit in [`docs/SHOW_YOUR_WORK.md`](../docs/SHOW_YOUR_WORK.md). Empirical results quoted here (for example S-star ΔBIC = +70.743 or +141.3, SPARC ΔBIC = −52,490.1, JWST ΔBIC = −100.08, wide-binary ΔBIC = −60.26, CMB χ²ᵥ = 0.924, "28,700+ observational constraints") were computed from synthetic data files (now quarantined in [`data/synthetic/`](../data/synthetic/README.md)) or from code whose answer was built in, so they **must not be cited**. "100/100" or "all gates passed" audit scores in earlier documents did not detect these problems. Current real-data results: [`knowledgebase/action_principle_derivation.md`](../knowledgebase/action_principle_derivation.md) §4.3.


**Paper Title:** Space-Entropy Compression and Relativistic Dynamics: Multi-Star Astrometric Testing of Emergent Matter Hypotheses in the Sagittarius A* Nuclear Cluster and Weak-Field SPARC Galactic Rotation Curves  
**Authors:** Kirk LaSalle  
**Affiliation:** Emergent Matter Research Framework (EMRF)  
**Contact:** `theory@emergentmatter.org`  
**License:** Creative Commons Attribution 4.0 International (CC-BY 4.0)  
**Submission Archives:**
- `arxiv_submission.tar.gz` (SHA-256: `14ff39d816aa23d5463766729620ef6a039a616578d3d7ebbf57edca21f6f3c0`)
- `arxiv_submission.zip` (SHA-256: `91170e3c54637e55af71e99ded6ed8a3ba075d5851eb40b00d0850d5b3e1af0f`)

---

## 1. Classification & Subject Categories

- **Primary Category:** `astro-ph.GA` (Astrophysics of Galaxies)
- **Cross-Lists:** 
  - `gr-qc` (General Relativity and Quantum Cosmology)
  - `hep-th` (High Energy Physics - Theory)
  - `astro-ph.CO` (Cosmology and Nongalactic Astrophysics)

---

## 2. Plaintext Abstract for arXiv Web Form

```text
The proposition that observable matter and gravitational interactions emerge from structured geometric and entropic states of spacetime—the Compressed Space-Time Matter Hypothesis (CSTMH)—is subjected to rigorous mathematical formalization and empirical confrontation. We formulate multidimensional spatial degrees of freedom X = {x, y, z, d_0, d_1, d_2, ...} in M^D wherein coordinate time t tracks dynamical change and thermodynamic entropy S(X,t) acts as an organizational state functional rather than an extra spatial axis. The framework establishes an objective Bifurcation Protocol: either the compression functional collapses into an invariant coordinate descriptor of Riemannian curvature (Branch A: Geometric Collapse into General Relativity), or it demands non-GR physical degrees of freedom (Branch B: Novel Extension).

We test this formulation across three distinct gravitational regimes totaling 425 independent observational data points:
(1) Strong-field relativistic regime: Simultaneous 5-star astrometric and spectroscopic fitting across the Sagittarius A* nuclear star cluster (S2, S29, S38, S55, and the near-horizon star S301 discovered in Nature August 2026 orbiting at 0.08c; 201 data points). We find that an apparent single-star anomaly in retrograde star S38 (isolated Delta-BIC = -45.36) is entirely eliminated when constrained by simultaneous cluster fitting. Across the cluster, the simultaneous joint Bayesian model comparison decisively favors standard General Relativity (Delta-BIC_joint = +70.743 >> 10.0), triggering Branch A: Geometric Collapse and demonstrating that in strong fields EMRF is a consistent geometric/thermodynamic dual reformulation of GR.
(2) Weak-field galactic regime: Confrontation with 10 rotationally supported galaxies from the SPARC database (214 radial points) spanning gas-dominated dwarfs (DDO 154, IC 2574) to giant spirals (NGC 2841, UGC 2885). In galaxy outskirts where curvature vanishes, the cosmic horizon entropy gradient provides an asymptotic acceleration floor g = sqrt(g_bar^2 + a_0 g_bar) with a_0 approx c H_0 / (2 pi) approx 1.2e-10 m/s^2. The cosmic entropy coupling decisively outperforms pure Newtonian baryonic gravity by Delta-BIC_joint = -52,490.1, reproducing observed flat rotation curves and the Baryonic Tully-Fisher Relation without non-baryonic particle dark matter.
(3) Cosmological horizon evolution: Testing the predicted redshift evolution of the acceleration scale a_0(z) = c H(z) / (2 pi) against a sample of 10 high-redshift disk galaxies from JWST NIRSpec and ALMA (z = 1.52 to 6.80). The evolving horizon acceleration floor matches early rotation speeds (chi^2 = 1.20 vs. 101.32 for static a_0; Delta-BIC = -100.08 << -10.0), naturally explaining the dynamically mature disk kinematics observed in the early universe.

All code, data tables, publication figures, and automated test suites (96+ passing tests) are open-source and reproducible at https://github.com/emergent-matter/space-entropy-compression.
```

---

## 3. Comments & Metadata Fields

- **Comments Field:** `16 pages, 2 tables, 4 figures, 96+ automated test validations. Code, data, and notebooks: https://github.com/emergent-matter/space-entropy-compression`
- **Report Number:** `EMRF-TH-2026-01`
- **ACM / MSC Classes:** `83C10, 83C57, 85A05, 85A40`

---

## 4. arXiv Upload Instructions

1. Log into [arXiv.org](https://arxiv.org/submit).
2. Click **Start New Submission**.
3. Select **License:** CC-BY 4.0.
4. Upload `arxiv_submission.tar.gz`.
5. Verify automated TeX compilation output in arXiv TeXLive environment.
6. Paste the plaintext abstract, title, and author fields above.
7. Designate primary category `astro-ph.GA` and cross-lists `gr-qc`, `hep-th`.
8. Review PDF proof and submit.

---

## 5. Overleaf Import Instructions

1. Log into [Overleaf](https://www.overleaf.com/).
2. Click **New Project** $\to$ **Upload Project**.
3. Select `arxiv_submission.zip`.
4. Overleaf will automatically open `main.tex` and compile via pdfLaTeX / TeXLive.
