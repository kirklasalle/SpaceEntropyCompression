# Action Principle on $\mathcal{M}^D$ with Cosmic-Horizon Entropy Coupling: What Is Assumed, What Is Derived

**Emergent Matter Research Framework (EMRF): theoretical note**
**Author:** Kirk LaSalle
**Original date:** 2026-10-05 · **Corrected:** 2026-10-07 (see [`docs/SHOW_YOUR_WORK.md`](../docs/SHOW_YOUR_WORK.md))

> **Correction notice (2026-10-07).** The earlier version of this note contained numerical errors (curvature values wrong by ~10³⁴; a₀ = cH₀ stated as 1.2×10⁻¹⁰ m/s²). It also described steps as "derived" that were in fact assumed. It quoted Δ-BIC results computed from data that were later shown to be synthetic. This version marks every step as **[DERIVED]**, **[ASSUMED]**, or **[OPEN]**. Empirical results now come only from real data ([`emergent_matter_model/sparc_real_analysis.py`](../emergent_matter_model/sparc_real_analysis.py)).

---

> **Subsequent inference clarification (2026-10-08):** the numerical summaries below are historical. Their nuisance treatment is penalized profiling, not Bayesian marginalization; quoted σ levels and BIC rankings are not independently calibrated discovery evidence. See the [fresh paper](../docs/SPARC_HORIZON_TEST_PAPER.md), [profile results](../docs/SPARC_FRESH_RESULTS.md), and [compression audit](../docs/EMRF_COMPRESSION_AND_HORIZONS_AUDIT.md). The linearized argument below is conditional on its background/coupling assumptions, not a no-go theorem for every nonlinear completion.

## 1. Spatial ontology (foundational postulates)

1. **[ASSUMED]** Space is dimensional: $X = \{x, y, z, d_0, d_1, \dots\} \in \mathcal{M}^D$, with $D = 3 + d_{\text{ext}}$.
2. **[ASSUMED]** Coordinate time $t$ parameterizes change. Thermodynamic entropy $S(X,t)$ is a scalar state field, not a coordinate.
3. **[ASSUMED]** A compression functional $C(X,t) = \mathcal{F}(E, S, \text{geom}, t)$ characterizes how energy–momentum is organized.

These postulates are a coherent philosophical starting point. By themselves they make no quantitative prediction.

## 2. The action

$$
\mathcal{S} = \int d^D X\, dt \sqrt{-g}\left[\frac{R}{16\pi G_D} + \mathcal{L}_{\text{matter}} + \mathcal{L}_{\text{entropy}}\right],
\qquad
\mathcal{L}_{\text{entropy}} = -\tfrac12 \kappa_S\, g^{AB}\nabla_A S \nabla_B S - V(S).
$$

**[DERIVED]** Varying with respect to $S$ gives $\kappa_S \Box S - V'(S) = J$, where $J$ is whatever source couples $S$ to matter.

**[DERIVED, important]** Far from sources, $S$ sits near the minimum of $V$, so $V'(S) \approx m^2 (S - S_{\text{vac}})$ and the field equation is **linear**. Its static solutions scale linearly with the source mass, so any extra force it produces is $\propto M$ (a Newton-like or Yukawa-like $1/r^2$ term). A deep-MOND acceleration $g = \sqrt{G M a_0}/r$ scales as $\sqrt{M}$, which this Lagrangian **cannot** produce. Getting $\sqrt{M}$ scaling requires a non-canonical kinetic term, for example the AQUAL form $\mathcal{L} \propto a_0^2\, F(|\nabla\phi|^2/a_0^2)$ with $F(x) \to \tfrac23 x^{3/2}$ (Bekenstein & Milgrom 1984). A full relativistic theory must also produce lensing and the CMB peaks. For a known working example, see AeST, which uses a scalar field plus a unit time-like vector (Skordis & Złośnik 2021).

**[OPEN]** Writing down an EMRF action that actually yields the weak-field law used below is the central unsolved theoretical task of this project.

## 3. Strong-field regime (black holes, Solar System)

**[DERIVED]** Kretschmann invariant of Schwarzschild: $K = 48 G^2M^2/(c^4 r^6)$. With $M = 4.297\times10^6\,M_\odot$, $GM/c^2 = 6.345\times10^9$ m:

| Location | r | K (m⁻⁴) |
|---|---|---|
| S2 pericentre | 118.3 AU | 6.3×10⁻⁵⁹ |
| S301 pericentre | 12.2 AU | 5.2×10⁻⁵³ |
| Galaxy outskirts, 10¹⁰ M☉ at 10 kpc | 10 kpc | 1.2×10⁻⁹⁵ |

(The earlier values of 1.25×10⁻²⁴, 1.4×10⁻¹⁸, and 10⁻⁷⁸ were wrong.)

**[ASSUMED]** EMRF reduces to General Relativity when $a \gg a_0$. This is a requirement placed on the theory, not a result derived from it. Earlier text saying that EMRF "analytically derives the Schwarzschild geometry" has been withdrawn.

**[CONSTRAINT]** Whatever weak-field law EMRF adopts must give an anomalous acceleration well below about 10⁻¹³–10⁻¹² m/s² inside the Solar System (planetary ephemerides and Cassini; Hees et al. 2014). See §4.3.

## 4. Weak-field regime and the cosmic-horizon scale

### 4.1 The horizon hypothesis for a₀

- Unruh temperature for acceleration $a$: $T_U = \hbar a/(2\pi c k_B)$.
- Gibbons–Hawking temperature of the de Sitter horizon: $T_{dS} = \hbar H/(2\pi k_B)$.
- **[DERIVED]** Setting $T_U = T_{dS}$ gives $a = cH_0 \approx 6.5\times10^{-10}$ m/s² for $H_0 = 67.4$. The $2\pi$ factors cancel.
- **[ASSUMED / hypothesis]** EMRF adopts $a_0 = cH_0/2\pi$ (Milgrom 1999 noted this numerical coincidence; Verlinde 2017 gave an entropic argument for the same scale). Numerically: **1.04×10⁻¹⁰ m/s² (H₀ = 67.4)** and **1.13×10⁻¹⁰ m/s² (H₀ = 73.0)**. The extra $1/2\pi$ isn't derived; it's a hypothesis to be tested against data.

### 4.2 The weak-field law

**[ASSUMED]** $g = g_N\,\nu(g_N/a_0)$ with $\nu(y) \to y^{-1/2}$ for $y \ll 1$ and $\nu \to 1$ for $y \gg 1$.

**[DERIVED]** In the deep regime $g \to \sqrt{a_0 g_N}$. With $g = V^2/r$ this gives $V^4 = G M a_0$, the baryonic Tully–Fisher relation. For $M = 10^{10} M_\odot$: $V_{\text{flat}} = 112$ km/s.

### 4.3 Which law? Real-data and Solar-System results

The earlier text used $\nu(y) = \sqrt{1 + 1/y}$, i.e. $g = \sqrt{g_N^2 + a_0 g_N}$.

**[DERIVED]** For $g_N \gg a_0$: $\sqrt{g_N^2 + a_0 g_N} = g_N + a_0/2 - a_0^2/(8g_N) + \dots$. That is a constant extra acceleration $a_0/2 \approx 6\times10^{-11}$ m/s² throughout the Solar System, hundreds of times too large.

Results on the **real SPARC database** (153 galaxies, 3,168 points, quality Q ≤ 2, inclination ≥ 30°; per-galaxy $\Upsilon_\star$ with prior 0.5 ± 0.1 dex). Run `python emergent_matter_model/sparc_real_analysis.py` to reproduce.

| Law | Best global a₀ (10⁻¹⁰ m/s²), range over Υ treatments | χ² | Contains cH₀/2π? | Solar System |
|---|---|---|---|---|
| EMRF $\sqrt{g_N^2 + a_0 g_N}$ | 1.30 – 1.59 | 38,546 | No | **Fails** (+a₀/2) |
| McGaugh RAR $1/(1 - e^{-\sqrt{y}})$ | 1.03 – 1.22 | **32,106** | **Yes** (both H₀) | Passes* |
| MOND "simple" | 1.06 – 1.18 | 33,194 | SH0ES only | **Fails** (+a₀) |
| MOND "standard" | 1.34 – 1.77 | 42,655 | No | Passes* |

\*Ignoring the External Field Effect quadrupole, which Cassini also constrains (Hees et al. 2014, 2016). This hasn't been evaluated here.

**Cross-check:** with $\Upsilon$ fixed at 0.5/0.7, the RAR fit gives a₀ = 1.22×10⁻¹⁰, reproducing the published 1.20 ± 0.02 (stat) ± 0.24 (sys) (McGaugh, Lelli & Schombert 2016).

**Conclusion of this section (first pass):** the horizon hypothesis $a_0 = cH_0/2\pi$ is **consistent** with real galaxy data **if** the interpolating function is RAR-like. The specific law in the earlier EMRF text is disfavored by both the galaxy data and the Solar System.

**Sharpened test (distance and inclination marginalized; [`sparc_marginalized_a0.py`](../emergent_matter_model/sparc_marginalized_a0.py)):** with the RAR law, the full sample gives a₀ = 1.234 ± 0.048. That reproduces the literature value but sits 4.0σ (Planck H₀) and 2.2σ (SH0ES H₀) above cH₀/2π. The 66 gas-dominated galaxies give a₀ = 1.019 ± 0.082, consistent with cH₀/2π (−0.3σ / −1.3σ). The samples disagree at ~2.3σ, so **the hypothesis is neither confirmed nor excluded**. The Λ-tied variant c√(Λ/3)/2π ≈ 0.86 is disfavored at ≈2–3σ even in the gas-dominated sample.

**Diagnostics ([`sparc_tension_diagnostics.py`](../emergent_matter_model/sparc_tension_diagnostics.py)):** the disagreement traces to galaxies with bulges. Star-dominated bulge galaxies give a₀ = 1.91 ± 0.18 versus 0.894 ± 0.050 for bulgeless ones (5.4σ), and the gap persists in deep points (4.8σ). Bulgeless gas- and star-dominated galaxies agree, at a₀ ≈ 0.93 ± 0.04, below cH₀/2π. Defensible selections span a₀ ≈ 0.84–1.28, so a₀ is systematics-limited at ±15–20% and SPARC mass models alone can't decide the hypothesis. A bulge mass-to-light test ([`sparc_bulge_test.py`](../emergent_matter_model/sparc_bulge_test.py)) shows the bulge-galaxy excess isn't removed by any plausible stellar M/L: their deep-regime a₀ ≈ 1.6 for every assumed bulge or disk M/L. So either other systematics are at work, or a₀ isn't universal.

### 4.4 Redshift evolution

**[ASSUMED]** If $a_0 = cH(z)/2\pi$, then $a_0$ grows with redshift, by a factor $E(z) \approx 3$ at $z = 2$. Existing rotation-curve studies at $z \approx 1$–2.5 (Genzel et al. 2017; Nestor Shachar et al. 2023) report baryon-dominated inner disks with *lower* dark-matter fractions at higher $z$. That runs opposite to what a growing $a_0$ predicts, so strong $a_0 \propto H(z)$ evolution is **disfavored**, though not formally excluded. Any EMRF claim here must be tested against those real data sets.

## 5. Status summary

| Item | Status |
|---|---|
| Ontology (space dimensional, S a state field) | Postulate |
| Weak-field law from the action | **Open.** The stated canonical Lagrangian cannot produce it. |
| $a_0 = cH_0/2\pi$ | Hypothesis; consistent with real SPARC data within the Υ systematic, using an RAR-like law |
| $\sqrt{g_N^2 + a_0 g_N}$ law | Disfavored (worse χ² than RAR; fails Solar System) |
| $a_0 \propto H(z)$ | Disfavored by existing high-z kinematics; needs a real-data test |
| GR limit in strong field | Requirement, not a derivation |
| Bullet Cluster, CMB, lensing | Not addressed by any EMRF calculation; need a relativistic completion |

## References

- Bekenstein, J. & Milgrom, M. (1984), ApJ 286, 7.
- Genzel, R. et al. (2017), Nature 543, 397.
- Hees, A., Folkner, W. M., Jacobson, R. A. & Park, R. S. (2014), PRD 89, 102002.
- Hees, A., Famaey, B., Angus, G. W. & Gentile, G. (2016), MNRAS 455, 449.
- Lelli, F., McGaugh, S. S. & Schombert, J. M. (2016), AJ 152, 157.
- Li, P., Lelli, F., McGaugh, S. & Schombert, J. (2018), A&A 615, A3.
- McGaugh, S. S., Lelli, F. & Schombert, J. M. (2016), PRL 117, 201101.
- Milgrom, M. (1999), Phys. Lett. A 253, 273.
- Nestor Shachar, A. et al. (2023), ApJ 944, 78.
- Skordis, C. & Złośnik, T. (2021), PRL 127, 161302.
- Verlinde, E. (2017), SciPost Phys. 2, 016.
