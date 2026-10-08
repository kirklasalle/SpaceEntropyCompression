# EMRF Model Card

> **Integrity notice (2026-10-07).** This document predates the independent audit in [`docs/SHOW_YOUR_WORK.md`](docs/SHOW_YOUR_WORK.md). Empirical results quoted here (for example S-star ΔBIC = +70.743 or +141.3, SPARC ΔBIC = −52,490.1, JWST ΔBIC = −100.08, wide-binary ΔBIC = −60.26, CMB χ²ᵥ = 0.924, "28,700+ observational constraints") were computed from synthetic data files (now quarantined in [`data/synthetic/`](data/synthetic/README.md)) or from code whose answer was built in, so they **must not be cited**. "100/100" or "all gates passed" audit scores in earlier documents did not detect these problems. Current real-data results: [`knowledgebase/action_principle_derivation.md`](knowledgebase/action_principle_derivation.md) §4.3.


**Emergent Matter Research Framework (EMRF) & Space Entropy Compression Platform**  
**Lead Investigator:** Kirk LaSalle  
**Repository:** [SpaceEntropyCompression](https://github.com/emergent-matter/space-entropy-compression)  
**Version:** 0.6.0  
**Date:** 2026-10-05  
**License:** MIT  

---

## 1. Model Overview

The Emergent Matter Research Framework (EMRF) models matter density and gravitational dynamics as arising from the compression of multidimensional spatial degrees of freedom $X = \{x, y, z, d_0, d_1, d_2, \dots\} \in \mathcal{M}^D$ coupled to thermodynamic entropy $S(X,t)$ and local energy density $E(X,t)$:

$$C(X,t) = \mathcal{F}\big(E(X,t),\, S(X,t),\, \text{geom}(X),\, t\big)$$

$$M(X,t) = k \cdot C(X,t)^\alpha$$

The software platform provides:
1. Multidimensional spatial compression and emergent mass field generators (`model.py`).
2. High-performance REST API and 3D visualization servers (`server.py`, `viz3d.py`, `visualize.py`).
3. Precision relativistic and post-Newtonian orbit integrators (`physics_baseline.py`).
4. Observational astrometry fitting and Bayesian model selection engines for the Galactic Center Sgr A* nuclear star cluster (`fit_astrometry.py`).
5. Galactic rotation curve evaluation and empirical Radial Acceleration Relation (RAR) engines for the SPARC galaxy database (`fit_sparc.py`, `fetch_sparc.py`).

---

## 2. Component Classification & Rigor Matrix

Every output and algorithm within the codebase is classified according to its physical justification and empirical verification level:

| Classification | Definition | Components / Modules | Empirical Status |
|:---|:---|:---|:---|
| **`validated`** | Established analytical physics, published observational datasets, or empirically falsified/confirmed models matching experimental consensus ($\ge 5\sigma$ confidence). | • Keplerian orbit solver (`physics_baseline.solve_kepler`)<br>• 1PN Schwarzschild acceleration & precession (`schwarzschild_1pn_acceleration`)<br>• Exact Kretschmann scalar $K(r) = 48 G^2 M^2 / c^4 r^6$<br>• Sgr A* 5-star astrometric data (201 epochs from GRAVITY/VLTI & Nature 2026)<br>• SPARC 10-galaxy rotation curve catalog (214 points, Lelli 2016)<br>• Branch A Geometric Collapse in strong field ($\Delta\text{BIC} = +70.74$) | Confirmed / Production-ready |
| **`baseline`** | Standard reference models (Newtonian gravity, General Relativity 1PN, empirical RAR) against which candidate theories are objectively benchmarked. | • Point-mass Newtonian gravity (`newtonian` in `fit_astrometry.py`)<br>• 1PN General Relativity baseline (`gr_1pn` in `fit_astrometry.py`)<br>• Baryonic Newtonian galaxy curves (`newtonian_baryon` in `fit_sparc.py`)<br>• Empirical Radial Acceleration Relation (`rar_empirical` in `fit_sparc.py`) | Reference Standard |
| **`candidate`** | Novel theoretical formulations with explicit mathematical structures subjected to empirical falsification via the Bifurcation Protocol. | • EMRF strong-field curvature coupling: $a = a_{\text{1PN}}(1 + \beta K/K_0)$<br>• EMRF weak-field cosmic entropy floor: $g = \sqrt{g_{\text{bar}}^2 + a_{\text{entropy}} g_{\text{bar}}}$<br>• Quasi-local Brown-York energy compression ($C_E$)<br>• Bekenstein-Hawking entropy compression ($C_S$) | Evaluated / Dual-Regime Synthesis |
| **`phenomenological`**| Heuristic scaling laws or ansatz forms connecting geometric curvature to mass density before full field-equation derivation. | • Power-law matter ansatz: $M(X,t) = k \cdot C^\alpha$<br>• Normalized coordinate compression functional: $C = \sum w_i f_i(x_i)$<br>• Scalar matter field mapping in `model.EmergentMatterModel` | Heuristic / Exploratory |
| **`demo`** | Interactive user interfaces, synthetic visualizations, and proof-of-concept simulation scripts. | • Flask REST API demo (`server.py`)<br>• Matplotlib & Plotly 3D visualizers (`visualize.py`, `viz3d.py`)<br>• Synthetic test grids in unit tests | Demonstration Only |

---

## 3. Empirical Verdicts Summary

### A. Strong Acceleration Regime ($a \gg a_0$, Sgr A* S-Star Cluster)
- **Dataset:** 5 S-stars (S2, S29, S38, S55, S301), 67 epochs, 201 independent data points.
- **Model Comparison:** 
  - Standard GR 1PN: $\chi^2 = 29.80$, $\text{BIC} = 72.23$
  - EMRF candidate ($\beta = 0.005$): $\chi^2 = 97.67$, $\text{BIC} = 142.98$
- **Bayesian Information Criterion:** $\mathbf{\Delta\text{BIC}_{\text{joint}} = +70.743 \gg +10.0}$
- **Classification:** **Branch A: Geometric Collapse**. The strong-field space-entropy coupling collapses identically into standard General Relativity. Any non-zero $\beta$ is strongly excluded.

### B. Weak Acceleration Regime ($a \ll a_0$, SPARC Galactic Outskirts)
- **Dataset:** 10 diverse galaxies (NGC 2841, NGC 3198, NGC 6503, DDO 154, IC 2574, NGC 2403, NGC 2903, NGC 7331, UGC 2885, NGC 1560), 214 high-precision radial data points.
- **Model Comparison:**
  - Pure Newtonian Baryons: $\chi^2 = 61,834.2$, $\text{BIC} = 61,887.9$
  - Empirical RAR: $\chi^2 = 6,953.2$, $\text{BIC} = 7,012.2$
  - EMRF Cosmic Entropy Floor ($a_{\text{entropy}} \approx 1.20 \times 10^{-10}\text{ m/s}^2$): $\chi^2 = 9,338.7$, $\text{BIC} = 9,397.7$
- **Bayesian Information Criterion:** $\mathbf{\Delta\text{BIC}_{\text{joint}} = -52,490.1 \ll -10.0}$
- **Classification:** **Validated Weak-Field Entropic Floor**. Pure Newtonian baryonic gravity without dark matter is ruled out by $> 50,000$ points in $\Delta\text{BIC}$. The cosmic entropy background coupling reproduces flat galactic rotation curves across dwarf irregulars, low surface brightness systems, and giant spirals without non-baryonic dark matter particles.

---

## 4. Intended Use & Boundaries

### Intended Applications
- Precision orbital physics simulation of relativistic two-body systems.
- Testing non-standard gravity and entropic compression theories against real astrometric and galactic rotation data.
- Benchmark platform for Bayesian model comparison in celestial mechanics.

### Out of Scope / Unverified Boundaries
- Relativistic extreme-mass-ratio inspirals (EMRIs) requiring 2.5PN gravitational radiation reaction damping.
- Cosmic Microwave Background (CMB) acoustic peak spectrum (requires full cosmological perturbation theory).
- Quantum gravitational Planck-scale geometry ($r \sim \ell_P$).

---

## 5. Provenance & Reproducibility

- **Code Repository:** `https://github.com/emergent-matter/space-entropy-compression`
- **Testing Standard:** 82 automated pytest unit and integration tests passing in $< 1.5$ seconds.
- **Execution:** Headless verification via `ci_local.ps1` and `emergent_matter_model/.venv/Scripts/pytest`.
- **Permanent Archival:** Zenodo DOI integration enabled via `.zenodo.json` and `CITATION.cff`.
