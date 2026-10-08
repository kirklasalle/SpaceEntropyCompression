# Show Your Work: An Independent Audit of the EMRF Mathematics, Theory, and Ten Empirical Regimes

**Prepared for:** Kirk LaSalle
**Prepared by:** An AI assistant (GitHub Copilot SDK in VS Code), working at Kirk's request
**Date:** 2026-10-07
**Scope:** [`paper/main.tex`](../paper/main.tex), the [`knowledgebase/`](../knowledgebase/) theory documents, all code in [`emergent_matter_model/`](../emergent_matter_model/), and all data in [`data/`](../data/)
**How to check this document:** run `python tools/show_your_work_audit.py`. Every number below is produced by that script ([`tools/show_your_work_audit.py`](../tools/show_your_work_audit.py)) or by the repository's own code, so you don't have to take my word for any of it.

> I'm an AI, and I can make mistakes. That's why every step is written out and every number can be reproduced. Before anything goes to a journal or arXiv, a human physicist should review this document **and** the project. Disagreement with any line here should be settled by running the script and checking the arithmetic.

---

## 0. The bottom line, in plain words

Kirk, you asked for the truth, so here it is plainly.

1. **The arithmetic in the code is mostly done correctly.** When I ran the scripts, they reproduced the published numbers exactly (ΔBIC = +70.743, −52,490.1, −100.08, and so on). The Kepler solver, sky projection, precession formula, and Baryonic Tully–Fisher algebra are all correct textbook physics.
2. **But most of the observational data in `data/` is not real measurement data**, even though it is labeled with real telescope names and real paper citations. I show below that the S2 and S301 star files describe motions no real orbit can have (S301 would have to move faster than light). The S301 discovery paper reports *no* radial velocities, but the repo has 15 of them. The SPARC galaxy files don't match the real SPARC database (and one galaxy, NGC 1560, isn't in SPARC at all). The JWST list has wrong redshifts and an object with no rotation measurement. The supernova file has far too little scatter to be real. Five of the 13 DESI rows don't match the published table.
3. **The central theoretical step isn't derived.** The weak-field law `g = √(g_N² + a₀ g_N)` is asserted, not derived from the stated action. It is a known MOND-style formula (Milgrom 1983). The constant `a₀ ≈ cH₀/2π` is a known numerical coincidence (Milgrom 1999); it doesn't follow from the Unruh/Gibbons–Hawking argument as written, which gives `cH₀` with no 2π.
4. **Different regimes use different, mutually incompatible formulas.** The exact formula used for SPARC, JWST, and the paper is the one the repo's own Solar System test labels **FALSIFIED** (it predicts an extra pull on Saturn 1,875× larger than the Cassini limit).
5. **Several "tests" are circular.** The answer is written into the code: GW speed `return C_LIGHT`, equivalence principle `η = 0`, quantum mass `m/(m/m₀) = m₀`, black-hole entropy that assumes the Bekenstein–Hawking ¼ per Planck area, CMB peak heights copied into both the model and the "data", and stability coefficients that are written down by hand rather than derived from an action.
6. **A real, honest result exists, and I computed it.** On the *real* SPARC database (175 galaxies, 3,391 points), the EMRF weak-field formula beats Newtonian gravity without dark matter by a huge margin, as every MOND-like law does. It is **worse** than McGaugh's standard Radial Acceleration Relation (ΔBIC ≈ +5,800) and **worse** than ordinary dark-matter halo fits (ΔBIC ≈ +35,600). That is a real, publishable-quality *negative-to-neutral* result. It isn't a discovery.

**Verdict:** The project shows real effort, clean code, and a good instinct (the pre-registered "Branch A / Branch B" falsification idea is sound scientific practice). But **as it stands, the paper should not be submitted.** Its empirical claims rest on data that isn't authentic, and its main theoretical claims aren't derived. Section 7 lists exactly what has to change to make it honest and submittable.

---

## 1. Ground rules for this audit

* **"Verified"** means I recomputed it independently and it is right.
* **"Correct but not EMRF"** means the math is right, but it's standard physics (GR, ΛCDM, MOND) that EMRF relabels. It doesn't test anything new.
* **"Asserted"** means the result is typed into the code or text, not computed from the theory.
* **"Not authentic data"** means the numbers can't be real observations. Each case comes with a proof.
* **"Wrong"** means an arithmetic or physics error, with the correct value shown.

Constants used: G = 6.67430×10⁻¹¹ m³ kg⁻¹ s⁻², c = 2.99792458×10⁸ m/s, ħ = 1.054571817×10⁻³⁴ J s, k_B = 1.380649×10⁻²³ J/K, M☉ = 1.98847×10³⁰ kg, AU = 1.495978707×10¹¹ m, pc = 3.085677581×10¹⁶ m.

---

## 2. The theory, line by line

### 2.1 The spatial ontology

*"Space is dimensional (x, y, z, d₀, d₁, …); entropy and time are not spatial axes."*

This is a legitimate philosophical starting position, and fixing the earlier mistake of treating S as an axis was correct. By itself, though, it makes **no testable prediction**. A prediction only appears once a specific equation is written down and solved. Everything below audits those equations.

### 2.2 The matter ansatz `M = k (C/C₀)^α`

This is a curve-fitting form with three free constants (k, C₀, α) and free weights wᵢ. It isn't derived from anything; the docs call it an ansatz, which is honest.

**Check of the α claim** in [`theoretical_framework.md`](../knowledgebase/theoretical_framework.md) §4.2:

* Take C ∝ √K, where K = 48G²M²/(c⁴r⁶). Then √K ∝ r⁻³, so ρ ∝ C^α ∝ r^(−3α).
* α = 1 gives ρ ∝ r⁻³ ✔. α = 2 gives ρ ∝ r⁻⁶ ✔. α = 1/3 gives ρ ∝ r⁻¹ ✔ (the arithmetic is fine).
* **Wrong:** the document says r⁻¹ is the "isothermal halo / flat rotation curve profile". It isn't. A flat rotation curve needs M(r) ∝ r, which means ρ ∝ r⁻². With ρ ∝ r⁻¹ you get M(r) ∝ r² and V ∝ √r, a rising curve. **The correct exponent for a flat curve is α = 2/3.**
* There is also an inconsistency: the docs use C ∝ √K, but [`compare_schwarzschild.py`](../emergent_matter_model/compare_schwarzschild.py) uses C ∝ K (1/r⁶). That script then fails its own check (measured slope −0.80 vs expected −6.00, printed as "Match: approximate"), because the constant entropy term dominates at large r.

### 2.3 The action and the step that's missing

[`action_principle_derivation.md`](../knowledgebase/action_principle_derivation.md) writes:

```
L_entropy = −½ κ_S g^{AB} ∇_A S ∇_B S − V(S)
```

and then says this produces `g_eff = √(g_bar² + a₀ g_bar)`. **No derivation is shown, and the Lagrangian as written cannot produce that law.** Here is the reasoning:

1. Vary the action with respect to S. With any source coupling to matter density ρ, the static field equation is κ_S ∇²S − V′(S) = (source ∝ ρ).
2. Far from sources, S sits near the minimum of V, so V′(S) ≈ m²(S − S_vac). The equation is then **linear**: ∇²δS − (m²/κ_S) δS ∝ ρ.
3. Solutions of a linear equation scale linearly with the source. Double the mass and you double the field and its force. So the extra acceleration is ∝ M (a Newton-like or Yukawa-like 1/r² term).
4. The deep-MOND law needs g = √(G M a₀)/r, which is **∝ √M**. A linear field equation can't produce √M scaling.
5. Getting √M needs a *non-canonical* kinetic term, for example Bekenstein & Milgrom's AQUAL (1984), L ∝ a₀²·F(|∇φ|²/a₀²) with F(x) → (2/3)x^{3/2}. That's well-known, published physics, not part of EMRF as written.

**Status: Asserted.** The weak-field formula is phenomenological. The honest wording is: "We adopt the MOND-type interpolating function g = √(g_N² + a₀g_N) (cf. Milgrom 1983; Famaey & McGaugh 2012)."

The claim |T^entropy|/|T^curvature| ~ a₀/a in §3.2 of the same document is also stated without derivation.

### 2.4 Where `a₀` comes from: show the work

The paper writes T_dS = ħH₀/(2πk_B), then claims a₀ = cH₀/2π ≈ 1.20×10⁻¹⁰ m/s². Let me do it step by step.

* Unruh temperature for acceleration a: T_U = ħa / (2π c k_B).
* Gibbons–Hawking de Sitter temperature: T_dS = ħH / (2π k_B).
* Set T_U = T_dS: ħa/(2πck_B) = ħH/(2πk_B), so **a = cH**. The 2π cancels.

| H₀ (km/s/Mpc) | cH₀ (m/s²) | cH₀/2π (m/s²) |
|---|---|---|
| 67.4 (Planck) | 6.55×10⁻¹⁰ | 1.04×10⁻¹⁰ |
| 70.0 | 6.80×10⁻¹⁰ | 1.08×10⁻¹⁰ |
| 73.0 (SH0ES) | 7.09×10⁻¹⁰ | 1.13×10⁻¹⁰ |

* The stated argument gives a = cH₀ ≈ 6.5×10⁻¹⁰ m/s², about **5.5× larger** than the empirical a₀.
* The extra 1/2π is inserted by hand. It reflects Milgrom's (1999) observation that a₀ ≈ cH₀/2π, a known coincidence, not a derivation.
* Even with the 2π, getting exactly 1.20×10⁻¹⁰ needs H₀ = 77.6 km/s/Mpc, which no measurement supports.
* [`action_principle_derivation.md`](../knowledgebase/action_principle_derivation.md) §4.2 writes "a₀ = cH₀ ≈ 1.2×10⁻¹⁰". That is **wrong** by a factor of about 5.5, and it contradicts the paper's cH₀/2π.

### 2.5 The weak-field law: what's right and what breaks

**Right (verified): the Baryonic Tully–Fisher algebra.**
For g_N ≪ a₀: g = √(g_N² + a₀g_N) → √(a₀ g_N) = √(G M a₀)/r. Set g = V²/r, so V⁴ = G M a₀. For M = 10¹⁰ M☉ that gives V_flat = 112.3 km/s. ✔

**Breaks: the strong-field limit.**
For g_N ≫ a₀, expand:

```
√(g_N² + a₀ g_N) = g_N √(1 + a₀/g_N) = g_N + a₀/2 − a₀²/(8 g_N) + …
```

So the law adds a **constant extra acceleration of a₀/2 = 6.0×10⁻¹¹ m/s² everywhere**, including inside the Solar System:

| Body | g_N (m/s²) | Extra from EMRF law | Bound used in the repo | Ratio |
|---|---|---|---|---|
| Mercury | 3.96×10⁻² | 6.0×10⁻¹¹ | 1.2×10⁻¹² | **50×** too big |
| Earth (LLR) | 5.93×10⁻³ | 6.0×10⁻¹¹ | 1.0×10⁻¹³ | **600×** too big |
| Saturn (Cassini) | 6.46×10⁻⁵ | 6.0×10⁻¹¹ | 3.2×10⁻¹⁴ | **1,875×** too big |

This is the **exact formula** used for SPARC (`fit_sparc.py` line 126), JWST, and the paper. The repo's own [`stress_test_solar_system.py`](../emergent_matter_model/stress_test_solar_system.py) calls it `unscreened_naive` and marks it **FALSIFIED**. The "EMRF" model that passes there is a *different*, hand-built function (McGaugh's ν multiplied by 1 − tanh(y/100)). The scale "100" isn't derived. That function was never used to fit galaxies.

### 2.6 Curvature numbers: show the work

K = 48 (GM/c²)² / r⁶. For M = 4.297×10⁶ M☉: GM/c² = 6.345×10⁹ m, so (GM/c²)² = 4.026×10¹⁹ m².

* S2 pericentre r = 118.3 AU = 1.770×10¹³ m, r⁶ = 3.07×10⁷⁹ m⁶. **K = 6.29×10⁻⁵⁹ m⁻⁴.** The repo says 1.25×10⁻²⁴, which is **wrong by 10³⁴**.
* S301 pericentre r = 12.2 AU: **K = 5.23×10⁻⁵³ m⁻⁴.** The repo says 1.4×10⁻¹⁸, also **wrong by 10³⁴**.
* Ratio K(S301)/K(S2) = (118.3/12.2)⁶ = 8.31×10⁵. ✔ (The paper is right here.)
* Galaxy outskirts (10¹⁰ M☉ at 10 kpc): K ≈ 1.2×10⁻⁹⁵ m⁻⁴. The repo says ~10⁻⁷⁸, wrong by about 10¹⁷.

### 2.7 "EMRF analytically derives the exact Schwarzschild geometry"

This sentence appears in the abstract and conclusion. **No such derivation exists anywhere in the repository.** In the code, GR is simply the β = 0 setting of `omega_rate × (1 + β)`. "Agrees with GR when the extra parameter is zero" is true by construction. It isn't a derivation and shouldn't be described as one.

### 2.8 One theory, or a different formula for each regime?

| Regime | Acceleration / physics law actually used in code |
|---|---|
| SPARC, JWST, paper | √(g_N² + a₀ g_N) |
| Solar System ("EMRF" version) | McGaugh ν(y) × (1 − tanh(y/100)) |
| Wide binaries | McGaugh ν evaluated at √(g_int² + g_ext²) |
| RAR scatter test | McGaugh ν(y) = 1/(1 − e^{−√y}) |
| Lensing | Standard GR singular isothermal sphere |
| Bullet Cluster | Gas weighted by (1 + 0.45 S)^−2.2 (both numbers chosen by hand) |
| CMB | ΛCDM with Ω_c = 0.266 (cold dark matter renamed) |
| Cosmic expansion | Standard w₀w_a (CPL) dark energy |
| GW speed / WEP | `return c` / `η = 0` (asserted) |

A single physical theory has to use **one** law everywhere. There's also a known theorem problem. The GW170817 test argues that EMRF couples matter only *conformally* (g̃ = Ω²η). Under a conformal coupling, light rays aren't bent by the extra field (Bekenstein & Sanders 1994), so EMRF couldn't produce the extra gravitational lensing that galaxies and the Bullet Cluster show. Those two claims contradict each other.

---

## 3. The ten regimes, one by one

The regime list and claimed results are taken from [`README.md`](../README.md) ("Empirical Verification Program").

### Regime 1: Strong field, Sgr A* S-stars (claimed ΔBIC = +70.743; README says +141.3)

**What the code does** ([`fit_astrometry.py`](../emergent_matter_model/fit_astrometry.py)):

* Orbital elements are **hard-coded**, not fitted. β is **fixed at 0.005**, not fitted. The "EMRF model" is just GR precession × (1 + β).
* The parameter counts (6, 8, 9) in the BIC formula count parameters that are never varied.
* The reduced χ² for GR is **2×10⁵ to 1.6×10⁶** per star. A model that fit the data would give about 1. At these values, no model fits the data, and a ΔBIC of 70 on a χ² of 88,534,305 means nothing.
* The **"simultaneous joint fit" is a sum** of independent per-star χ² values: Σ Δχ²ᵢ + ln(201) = 65.440 + 5.303 = **70.743**. Nothing is shared. The S38 "anomaly" (Δχ² = −48.7) isn't eliminated; it's still in the sum, just outweighed by S301 (+88.2).
* If β were actually free, the χ²-minimizing value runs to the edge of the searched range (±50) for every star. β isn't constrained at all.

**Data provenance: not authentic** ([`data/astrometry/`](../data/astrometry/)):

* **S2:** the file's two pericentre passages, 2002.337 and 2018.379 (one period apart), sit at (42.5, −31.2) mas and (−14.25, −16.12) mas, **58.7 mas apart**. Relativistic precession of 12.2′ moves the pericentre by only ~0.05 mas. A real orbit can't do this.
* **S2:** from 2018.379 to 2018.420 the sky speed is 8,155 km/s. Combined with the listed v_r = 7,550 km/s, that gives |v| ≈ 11,100 km/s, but S2's maximum orbital speed is 7,758 km/s.
* **S301, worked example:** from 2024.115 to 2024.120 the position moves from (8.20, −52.10) to (−1.45, −1.48) mas, so Δθ = √(9.65² + 50.62²) = 51.5 mas. One mas at 8,275 pc is 8.275 AU, so that's 426 AU in 0.005 yr (1.58×10⁵ s), or **404,000 km/s, faster than light** (c = 299,792 km/s). S301's real pericentre speed is about 25,000 km/s.
* **S301:** the Nature 2026 discovery paper (arXiv:2607.12664) states that **no radial velocity had been measured**. Its 19 astrometric points come from 2017 and 2021–2025. The repo file has 15 radial velocities from 2020–2026, with errors of 8–40 km/s. These can't come from the cited source.
* **Paper table, S301 row:** a = 620 AU and e = 0.960 give a(1 − e) = 24.8 AU, not the stated 12.2 AU, and a Kepler period of 7.44 yr, not 8.7 yr. The published values are about 83 mas (~690 AU) and e ≈ 0.983. (The code uses 679 AU and 0.982, which are consistent.)

**Verified physics:** Schwarzschild precession of S2 = 12.2′ per orbit ✔ and of S301 = 1.89° per orbit ✔ (published: 1.9–2.0°). S301 v_peri = 0.083c ✔.

**Verdict: no valid result.** The method doesn't fit anything, and the data isn't authentic.

### Regime 2: Solar System (claimed "EMRF passes Cassini")

* The bounds table is plausible.
* "EMRF screened" passes only because an ad-hoc `1 − tanh(y/100)` factor switches the effect off at y > 100. The docstring describes an exp(−(y/y_crit)^p) function that the code computes and then never uses.
* The formula EMRF actually uses everywhere else fails here by 1,875× (§2.5).

**Verdict: the theory used in the paper fails this test.** The passing version is a different, unmotivated function.

### Regime 3: SPARC rotation curves (claimed ΔBIC = −52,490 vs Newton)

* **Data not authentic:** the repo files don't match the real SPARC database (Lelli, McGaugh & Schombert 2016):

| Galaxy | Repo N / R_max / V_disk,max | Real SPARC N / R_max / V_disk,max |
|---|---|---|
| DDO 154 | 18 / 8.5 / 16.8 | 12 / 5.9 / 14.6 |
| NGC 1560 | 20 / 8.0 / 29.0 | **not in SPARC** |
| NGC 2403 | 25 / 20.0 / 107.0 | 73 / 20.9 / 106.7 |
| NGC 2903 | 22 / 30.6 / 154.0 | 34 / 25.0 / 300.5 |
| NGC 3198 | 25 / 39.4 / 106.1 | 43 / 44.1 / 142.3 |
| NGC 7331 | 20 / 35.0 / 198.0 | 36 / 36.3 / 371.2 |

  The repo's radii are evenly spaced, for example 0.68 × n kpc for NGC 3198. Real SPARC radii follow the actual HI rings.

* "Gas-dominated dwarfs yield Υ_disk ≈ 0.05" is the optimizer hitting its **lower bound**, and those fits still have reduced χ² ≈ 34–40. That isn't "physically expected".
* The paper's own table shows EMRF is **worse than the standard RAR** (χ² 9,339 vs 6,953). The paper doesn't say so.
* **Real-data re-analysis:** see Section 4.

**Verdict: the formula captures flat rotation curves vs Newton (true of all MOND-type laws), but underperforms both the RAR and dark-matter halos on real data.**

### Regime 4: Strong lensing, SLACS (claimed "matches HST without dark matter", χ² = 51.75)

* The SLACS input values look approximately real (Bolton et al. 2008).
* The "EMRF" prediction is the textbook **GR singular-isothermal-sphere formula** θ_E = 4π(σ/c)² D_LS/D_S. No EMRF quantity enters.
* In GR, an isothermal σ ≈ 230–330 km/s mass profile inside these galaxies **includes** dark matter. Agreement between σ and θ_E tests GR's consistency; it isn't evidence against dark matter.
* χ² = 51.75 for 5 lenses (reduced ≈ 10) is a poor fit, not a match.
* The script crashes on NumPy ≥ 2.0 (`np.trapz` was removed), causing 3 failing tests.

**Verdict: correct but not EMRF;** also a poor fit.

### Regime 5: Bullet Cluster (claimed lensing peaks shifted ~180 kpc)

* All mass and entropy distributions are hand-placed Gaussians. The stars are put at x = +240 kpc, and the "EMRF peak" is found at x = +240 kpc.
* The gas suppression factor (1 + 0.45 S)^−2.2 uses two hand-chosen numbers, and the "naive MOND" comparison κ ∝ √Σ is a strawman.
* κ is normalized to its maximum, so the test never checks the **amount** of lensing mass. That's the real Bullet Cluster problem: the lensing mass at the galaxy peaks is several times the visible stellar mass.
* Making a source's gravity depend on its temperature or entropy violates the universality of gravitational coupling that the WEP test claims EMRF obeys exactly.

**Verdict: asserted (tuned toy model).**

### Regime 6: JWST/ALMA high-redshift disks (claimed ΔBIC = −100.08)

* **Data problems** ([`jwst_kinematics_sample.csv`](../data/jwst/jwst_kinematics_sample.csv)):
  * GN-z11 is at z = 10.6. A "GN-z11-companion" at z = 3.15 isn't a real association.
  * REBELS-12 is at z = 7.35, not 5.18.
  * GS-9422 (Cameron et al. 2024) is a nebular-continuum spectrum; there's no published rotation velocity.
  * The remaining IDs (COSMOS-10028, ZFOURGE-22996, TEMPLATES-01, CRISTAL-06, ALMA-DLA-04, …) **have not been verified** against the cited papers in this audit. Each needs a traceable catalogue ID and the exact table it came from.
* **The fit is statistically too good:** χ² = 1.20 for 9 degrees of freedom has probability P = 0.0012 (about 1 in 850). That usually means the points were constructed from the model.
* Stellar-mass errors (0.12–0.28 dex) are listed but never used.
* The deep-MOND formula V = (GMa₀(z))^¼ requires g_N ≪ a₀(z). At the listed half-light radii, g_N/a₀(z) = 0.1–0.9, so the approximation isn't valid for the lower-z objects.
* The idea that a₀ ∝ H(z) is old (Milgrom) and has been tested against real z ≈ 1–2.5 rotation curves; those tests should be cited and compared against.

**Verdict: no valid result** (data not authentic).

### Regime 7: Gravitational-wave speed, GW170817 (claimed c_gw ≡ c)

* The code returns `C_LIGHT` for EMRF by definition. The "Horndeski" (−1.5×10⁻³) and "TeVeS" (+10⁻²) offsets are invented numbers.
* The observational bound itself is correctly quoted.

**Verdict: asserted.** It also conflicts with the lensing requirements (§2.8).

### Regime 8: Gaia wide binaries (claimed N = 26,615 pairs, ΔBIC = −60.26)

* The code contains **4 hand-entered bins** (1.00, 1.12, 1.28, 1.34), not 26,615 pairs.
* These ratios don't appear in Chae (2023), which reports an *acceleration* boost of about 1.4, roughly 1.2 in velocity.
* The topic is actively disputed: Banik et al. (2024, MNRAS 527, 4573) analyzed Gaia DR3 and found Newtonian gravity strongly preferred over MOND. A one-sided citation isn't acceptable.
* The EFE treatment (ν evaluated at √(g_int² + g_ext²)) is a rough approximation, and it's a third different law (§2.8).

**Verdict: data provenance unverified; the claim is overstated.**

### Regime 9: Late-time expansion, Pantheon+ and DESI (claimed "beats ΛCDM")

* The model is standard **w₀w_a (CPL) dark energy**, relabeled "void spatial compression". No EMRF equation determines w₀ or w_a.
* **Pantheon+ file:** 32 points, not 1,701 SNe. A flat ΛCDM fit gives χ² = 5.4 for 30 dof, P(χ² ≤ 5.4) = 2×10⁻⁷. The points sit on a smooth curve with almost no scatter, so they're generated, not binned real data.
* **DESI file vs DR1 Table 1** (arXiv:2404.03002):

| Row | Repo | Published DR1 |
|---|---|---|
| LRG1 D_M/r_d | 13.59 ± 0.25 | 13.62 ± 0.25 |
| LRG2 D_M/r_d | 17.47 ± 0.34 | 16.85 ± 0.32 |
| LRG3+ELG1 | z = 0.85; 19.51, 19.59 | z = 0.93; 21.71 ± 0.28, 17.88 ± 0.35 |
| QSO | D_M = 30.69, D_H = 13.06 | only D_V/r_d = 26.07 ± 0.67 published |
| Lyα D_M/r_d error | ± 1.05 | ± 0.94 |

**Verdict: correct (standard) cosmology math, relabeled; the data partly isn't authentic.**

### Regime 10: CMB acoustic peaks (claimed χ²_red = 0.924)

* Peak heights 5748.2, 2552.4, and 2521.8 μK² are **typed into the model** ([`cmb_acoustic_engine.py`](../emergent_matter_model/cmb_acoustic_engine.py)), and the **same numbers** are in the "data" file. Phase shifts are "calibrated to Planck".
* The distance to recombination is hard-coded as 13,872 Mpc × (67.4/H₀).
* The model needs Ω_c = 0.266, which is exactly Planck's **cold dark matter density**, renamed "clustered spatial compression density". So this regime **assumes** a dark-matter-like component, which contradicts the paper's "without dark matter" message.

**Verdict: circular.** It reproduces Planck by copying Planck.

### Supporting modules (not counted among the ten)

| Module | Finding |
|---|---|
| [`stress_test_equivalence_principle.py`](../emergent_matter_model/stress_test_equivalence_principle.py) | η = 0 is written in, not computed. |
| [`stress_test_stability_ghosts.py`](../emergent_matter_model/stress_test_stability_ghosts.py) | A, B, and M² are hand-chosen formulas, for example c_s = 1 − 0.05e^{−√y}, and "EOM order = 2" is a hard-coded constant. No action is perturbed. |
| [`stress_test_blind_challenge.py`](../emergent_matter_model/stress_test_blind_challenge.py) | The "real galaxy" is generated *from the model* plus noise. The adversarial sets (inverted curve, step, white noise) would be rejected by any smooth model, so this doesn't demonstrate falsifiability. |
| [`stress_test_galaxy_scatter.py`](../emergent_matter_model/stress_test_galaxy_scatter.py) | Uses McGaugh's RAR, not the EMRF law, on non-authentic data. |
| [`quantum_vibrational_compression.py`](../emergent_matter_model/quantum_vibrational_compression.py) | Computes m_em, then returns m_em / (m_em/m) = m. The "0 % error" is guaranteed algebraically. |
| [`black_hole_horizon_entropy.py`](../emergent_matter_model/black_hole_horizon_entropy.py) | Assumes ¼ k_B per Planck area (which is the Bekenstein–Hawking result) and integrates a sphere's area. Circular. |
| [`model.py`](../emergent_matter_model/model.py) | Correct implementation of the ansatz. It's a generic weighted power law and makes no physical prediction by itself. |

---

## 4. An honest re-analysis with the real SPARC data

To show what the EMRF weak-field law *really* does, I re-ran the comparison on the official SPARC rotation-curve files, downloaded by the audit script from `astroweb.case.edu/SPARC`. For every galaxy, the disk mass-to-light ratio Υ_disk was fitted in [0.1, 2.0], with Υ_bulge = 1.4 Υ_disk. a₀ = 1.2×10⁻¹⁰ m/s². No error floor was added.

**The 9 paper galaxies that exist in SPARC (332 points):**

| Model | χ² | Free params | BIC | ΔBIC vs EMRF |
|---|---|---|---|---|
| Newtonian baryons only | 160,254 | 9 | 160,306 | +155,620 |
| **EMRF √(g² + a₀g)** | **4,634** | 9 | **4,686** | 0 |
| McGaugh RAR (2016) | 3,560 | 9 | 3,612 | **−1,074** (better) |
| Baryons + isothermal DM halo | 1,228 | 27 | 1,385 | **−3,301** (better) |

**All 175 SPARC galaxies (3,391 points):**

| Model | χ² | Free params | BIC | ΔBIC vs EMRF |
|---|---|---|---|---|
| Newtonian baryons only | 605,258 | 175 | 606,681 | +559,033 |
| **EMRF √(g² + a₀g)** | **46,226** | 175 | **47,648** | 0 |
| McGaugh RAR (2016) | 40,459 | 175 | 41,882 | **−5,767** (better) |
| Baryons + isothermal DM halo | 7,804 | 525 | 12,072 | **−35,576** (better) |

**What this honestly shows:**

* "Beats Newton without dark matter" is true, but every MOND-type law does that. It isn't evidence for EMRF specifically.
* Against the two baselines a referee will demand (the RAR and dark-matter halos), the EMRF interpolating function **loses**.
* On top of that, this same function is ruled out in the Solar System (§2.5).

That is a legitimate, reportable result. It just isn't the result the paper currently claims.

---

## 5. What is genuinely sound

Credit where it's due:

* **The scientific stance is right.** Pre-registering a falsification rule (Branch A / Branch B), and accepting "reduces to GR" as a valid outcome, is good science.
* **Correct textbook physics in the code:** Kepler's equation solver, true anomaly, Thiele–Innes/Campbell sky projection, line-of-sight velocity, transverse Doppler + gravitational redshift (≈200 km/s for S2), Schwarzschild precession (S2: 12.2′ ✔, S301: 1.89° ✔), and the K(S301)/K(S2) ratio (8.3×10⁵ ✔).
* **The BTFR derivation from the adopted interpolation law is algebraically correct.**
* **The code is clean, modular, and tested** (175 of 178 tests pass; the 3 failures come from the NumPy 2 `np.trapz` removal). One caution: most tests check that the code returns its own hard-coded values, so "tests pass" doesn't mean "physics verified".
* **The ontology clarification** (entropy is a state variable, not an axis) fixed a real conceptual error from earlier drafts.

---

## 6. Status of each headline claim in `paper/main.tex`

| Claim | Status |
|---|---|
| "EMRF analytically derives the exact Schwarzschild geometry" | **Not shown anywhere.** Remove, or supply a derivation. |
| ΔBIC_joint = +70.743, Branch A | **Invalid.** No fitting; non-authentic data; reduced χ² ~10⁵–10⁶. |
| "S38 anomaly eliminated by joint fit with shared parameters" | **False.** Nothing is shared; S38's Δχ² is still in the sum. |
| S301 table row (620 AU, e = 0.960, r_p = 12.2 AU, P = 8.7 yr) | **Internally inconsistent.** Use the published ~690 AU, e ≈ 0.983. |
| a₀ = cH₀/2π ≈ 1.20×10⁻¹⁰ from horizon thermodynamics | **Not derived.** The argument gives cH₀; cH₀/2π = 1.04×10⁻¹⁰ for Planck H₀. |
| g_eff = √(g² + a₀g) from L_entropy | **Not derived.** It's a MOND interpolating function. |
| SPARC ΔBIC = −52,490 "resolves missing mass" | **Non-authentic data.** On real data EMRF loses to the RAR and to DM halos. |
| JWST ΔBIC = −100.08 | **Invalid.** Non-authentic data; χ² implausibly small. |
| K values (1.25×10⁻²⁴, 1.4×10⁻¹⁸, 10⁻⁷⁸ m⁻⁴) | **Wrong** by ~10³⁴ (and ~10¹⁷ for galaxies). |
| "159+ / 178 passing tests" | Currently 175 pass, 3 fail. The tests don't validate the physics. |
| README: "28,700+ observational constraints", "N = 26,615 pairs", "1,701 SNe" | **Not true of the repository.** About 500 numbers total, mostly non-authentic. |

---

## 7. What must change before anything is submitted (in priority order)

1. **Remove every non-authentic data file**, or clearly label it `SYNTHETIC – for code testing only`, and stop citing real papers for it. This is the most urgent item; submitting fabricated-looking data under real citations would end the project's credibility, regardless of intent. (My best guess is that these tables were produced as placeholders during AI-assisted development and later treated as real. The fix is the same either way.)
2. **Use real data with traceable provenance:**
   * S2: public tables in Gillessen et al. 2017 (ApJ 837, 30) and GRAVITY releases.
   * S301: astrometry only, from the Nature 2026 paper or its supplementary data.
   * SPARC: the official files (the audit script already downloads them).
   * Pantheon+: the official GitHub data release, with its covariance matrix.
   * DESI: DR1 or DR2 tables, with correlations.
   * Planck: the Planck Legacy Archive binned TT spectrum.
3. **Actually fit the models.** Free the parameters you count in BIC, report uncertainties, and check that the best fit has reduced χ² ≈ 1 before comparing models.
4. **Use one law in every regime.** If it's √(g² + a₀g), accept that it fails the Solar System test. If it's screened, use the screened law for galaxies too, and derive the screening.
5. **Either derive the weak-field law from an action** (for example with an AQUAL-type kinetic term, and then check lensing, which conformal coupling can't provide), **or present it honestly as phenomenological** and cite Milgrom 1983, Bekenstein & Milgrom 1984, Famaey & McGaugh 2012, and McGaugh, Lelli & Schombert 2016.
6. **Compare against the right baselines:** RAR/MOND and ΛCDM/dark-matter halos, not only "Newton without dark matter".
7. **Fix the numerical errors:** K values, a₀ (cH₀ vs cH₀/2π), α = 2/3 for flat curves, and the S301 table.
8. **Remove or relabel circular modules** (GW speed, WEP, stability, quantum mass, BH entropy, CMB) as "consistency demonstrations of assumed properties", not tests.
9. **Retract the overstatements** in README, paper, and status files: "derives Schwarzschild", "resolves dark matter", "beats ΛCDM", constraint counts, and "100/100" audit scores. The earlier internal "Grand Due Diligence" audits did not detect these problems, so they shouldn't be presented as independent verification.
10. **A paper that *would* be honest today** could be titled roughly: *"A phenomenological entropic-acceleration law confronted with SPARC: comparison with the RAR and dark-matter halos."* It would report the Section 4 result: the law captures the phenomenon, loses to the RAR and halos, and conflicts with Solar System bounds unless screened. Report it plainly, with the reasons and next steps. Honest negative results are publishable, and they build trust.

---

## 8. Remediation status (updated 2026-10-07, same day)

Following this audit, the fixes below were made. The sections above describe the repository **as it was audited**; file paths there refer to the original locations.

| Item (§7) | Status |
|---|---|
| 1. Quarantine non-authentic data | **Done.** All such files moved to [`data/synthetic/`](../data/synthetic/README.md) with `# SYNTHETIC DATA` headers; real instrument and object names removed; pipelines print a warning banner. |
| 2. Real data with provenance | **SPARC done** ([`fetch_real_data.py`](../emergent_matter_model/fetch_real_data.py), SHA-256 manifest). **DESI corrected** to DR1 Table 1. S-stars, Pantheon+, Planck and high-z kinematics: not yet ingested. |
| 3. Actually fit the models | **Done for SPARC:** global a₀ profile plus per-galaxy Υ⋆, validated on known-answer tests and against the published a₀. |
| 4. One law everywhere | **Done for the SPARC + Solar System comparison:** the same four laws are tested in both. |
| 5. Derive or present as phenomenological | **Presented as phenomenological;** derivation listed as the open problem ([`action_principle_derivation.md`](../knowledgebase/action_principle_derivation.md)). |
| 6. Right baselines | **Done:** RAR, MOND simple/standard, Newton and dark-halo comparators. |
| 7. Numerical errors | **Fixed** in the theory notes and the paper. |
| 8. Circular modules | Relabelled in docstrings, README and paper (no longer presented as tests). |
| 9. Retract overstatements | **Done** in README, paper, metadata and CHANGELOG; integrity notices on 35 older documents. |
| 10. Honest paper | **Done:** [`paper/main.tex`](../paper/main.tex) rewritten around the real-data result. |

### What the real data say (from `emergent_matter_model/sparc_real_analysis.py`)

Real SPARC, 153 galaxies, 3,168 points (Q ≤ 2, i ≥ 30°). a₀ is in units of 10⁻¹⁰ m/s²; the range spans three Υ⋆ treatments (prior / fixed 0.5–0.7 / free).

| Law | a₀ range | χ² (baseline) | ΔBIC vs RAR | Contains cH₀/2π? | Solar System |
|---|---|---|---|---|---|
| RAR | 1.03–1.22 | 32,106 | 0 | Yes, for both H₀ = 67.4 and 73.0 | pass |
| simple | 1.06–1.18 | 33,194 | +1,088 | H₀ = 73.0 only | fail |
| EMRF √(g² + a₀g) | 1.30–1.59 | 38,546 | +6,440 | No | fail |
| standard | 1.34–1.77 | 42,655 | +10,548 | No | pass |

**Reading this honestly:**
* The project's one sharp hypothesis, a₀ = cH₀/2π, **survives** a real-data test with the best-fitting law. It isn't uniquely confirmed, because the Υ⋆ systematic (~20%) is much larger than the statistical error (~1%).
* The law used in the earlier paper does **not** survive.
* With D and i fixed, dark-halo fits are preferred by BIC. A fair test needs D and i marginalized (as in Li et al. 2018).

### Step 2: sharpened test with distance and inclination marginalized (`emergent_matter_model/sparc_marginalized_a0.py`)

Each galaxy gets Υ⋆ (±0.1 dex), distance (±e_D) and inclination (±e_i) nuisance parameters, following Li et al. 2018.

How the physics enters: under D → f_D·D, g_bar is unchanged and g_obs ∝ 1/f_D; under i → i′, the observed velocities scale by sin i / sin i′.

Before fitting, I decided to report gas-dominated galaxies separately (gas fraction > 0.5: 66 galaxies, 966 points), because a₀ and Υ⋆ are degenerate in the deep regime.

**Validation:**
* The estimator is unbiased on known-answer galaxies with deliberately wrong catalogue D and i: mean of 10 realizations within 4% (12-realization study: 1.103 ± 0.020 vs a true 1.100).
* The full-sample RAR value, 1.234, matches Li et al. (2018), 1.20 ± 0.02.

| Law | All 153: a₀ | pull vs cH₀/2π (67.4 / 73.0) | Gas-dominated 66: a₀ | pull (67.4 / 73.0) | gas-dominated pull vs Λ-tied (0.863) |
|---|---|---|---|---|---|
| RAR | 1.234 ± 0.048 | +4.0σ / +2.2σ | 1.019 ± 0.082 | −0.3σ / −1.3σ | +1.9σ |
| simple | 1.301 ± 0.051 | +5.1σ / +3.4σ | 1.023 ± 0.081 | −0.2σ / −1.3σ | +2.0σ |
| EMRF √ | 1.583 ± 0.061 | +8.8σ / +7.4σ | 1.145 ± 0.083 | +1.2σ / +0.2σ | +3.4σ |
| standard | 1.602 ± 0.061 | +9.2σ / +7.8σ | 1.144 ± 0.087 | +1.2σ / +0.2σ | +3.2σ |

**What changed, honestly:**
* The first-pass "consistent" verdict **doesn't fully hold up**. The full sample is in 2–4σ tension with cH₀/2π for the best law.
* The gas-dominated galaxies, which are least sensitive to stellar masses and to the choice of law (spread ±0.06 vs ±0.18), remain consistent.
* The two samples disagree at ~2.3σ (RAR). That's the most important open empirical question.
* The Λ-tied reading of the hypothesis (constant a₀ = c√(Λ/3)/2π ≈ 0.86) is disfavoured at 1.9–3.4σ even in the gas-dominated sample. The H(z)-tracking reading is disfavoured by high-z kinematics. Each natural reading of the hypothesis therefore faces tension.
* The implied H₀ (66–74 ± 5–6) is too uncertain to inform the Hubble tension.
* Fit quality is still imperfect (χ²ᵥ ≈ 2.6 for gas-dominated galaxies, ~5 for the full sample).

### Step 3: diagnosing the disagreement (`emergent_matter_model/sparc_tension_diagnostics.py`)

Subsets were defined before fitting:
* bulgeless star-dominated galaxies;
* deep points only, g_bar < 0.3 × 1.2×10⁻¹⁰ at Υ = 0.5, where all laws coincide;
* locally gas-dominated points.

After removing bulges moved a₀ strongly, the complementary bulge galaxies were also fitted. That step is labelled **post hoc**. A full re-run reproduced subsets A–G exactly (zero difference).

| Subset (RAR) | galaxies / points | a₀ | pull vs cH₀/2π (67.4 / 73.0) |
|---|---|---|---|
| A gas-dominated | 66 / 966 | 1.019 ± 0.080 | −0.3 / −1.4 |
| B star-dominated, all | 87 / 2202 | 1.276 ± 0.062 | +3.8 / +2.4 |
| C star-dominated, bulgeless | 56 / 1070 | 0.894 ± 0.050 | −3.0 / −4.7 |
| D star-dominated, deep points | 75 / 919 | 1.162 ± 0.075 | +1.6 / +0.4 |
| E star-dominated, local-gas points | 6 / 50 | 0.915 ± 0.122 | −1.0 / −1.8 |
| F star-dominated, bulgeless, deep | 50 / 614 | 0.840 ± 0.065 | −3.1 / −4.4 |
| G all galaxies, deep points | 141 / 1859 | 1.098 ± 0.062 | +0.9 / −0.5 |
| H star-dominated, with bulge (post hoc) | 31 / 1132 | 1.910 ± 0.181 | +4.8 / +4.3 |
| I with bulge, deep (post hoc) | 25 / 305 | 1.616 ± 0.149 | +3.9 / +3.3 |

**What this shows, honestly:**
* The "gas vs star" disagreement is really **bulge vs bulgeless**: H vs C is +5.4σ, and I vs F (deep points only) is +4.8σ, so it isn't just an inner-region effect.
* Either bulge masses are mis-modelled (in the deep regime a₀ and baryonic mass are degenerate, so underestimated bulge mass mimics a larger a₀), or a₀ isn't universal. The second would hurt MOND-type laws and the horizon hypothesis alike.
* Without bulges, gas- and star-dominated galaxies agree (1.3σ). Combined (post hoc) they give a₀ = 0.930 ± 0.042, **below** cH₀/2π (−2.7σ Planck, −4.7σ SH0ES) and +1.6σ above the Λ-tied value.
* In the deep regime the law dependence collapses (spread ±0.07 vs ±0.18).
* **Overall:** reasonable selections give a₀ ≈ 0.84–1.28. The measurement is systematics-limited at ±15–20%, matching the published ±0.24. SPARC mass models alone can't decide whether a₀ = cH₀/2π, so the first-pass "consistent" result shouldn't be read as support.

### Step 4: bulge mass-to-light test (`emergent_matter_model/sparc_bulge_test.py`)

Question: is the bulge discrepancy a stellar-mass modelling problem, or is a₀ not universal? Sample: the 31 star-dominated bulge galaxies.

**Design fixed before running:**
* Test 1 scales the bulge M/L as Υ_b = r·Υ_d (standard r = 1.4).
* Test 2 frees each galaxy's Υ_b at fixed a₀ = 0.930 and 1.042.
* Plausibility, relative to the expected Υ_b ≈ 0.7: ≤ 1.0 plausible, 1.0–1.4 stretched, > 1.4 implausible.

**What went wrong with the plan:** I assumed heavier bulges would lower a₀. The first run showed the opposite. The bulge is pinned by the inner rotation curve; a heavier bulge forces a lighter disk, so the outer curve needs a larger a₀.

**Post hoc additions:** lighter ratios (r = 0.25–0.75); symmetric lower bounds (0.5 plausible, 0.35 stretched); and Test 3 (a₀ profiled with every Υ_b free).

| Check | Result |
|---|---|
| All points: Υ_b needed to reach a₀ = 0.930 / 1.042 | 0.34 (implausible) / 0.39 (stretched), with fits worsening (χ²ᵥ 6.4 → 7–9) |
| Deep points: a₀ across Υ_b = 0.12–2.0 | 1.60–1.63, insensitive to bulge mass |
| Deep points: a₀ across disk prior Υ₀ = 0.4–0.6 | 1.61–1.64, insensitive to disk mass |
| Test 3: every Υ_b free | a₀ = 1.28 ± 0.13; Δχ² ≈ 10.7 at 0.930 (~3.3σ), ≈ 4.2 at 1.042 (~2σ) |
| Test 2: per-galaxy Υ_b at a₀ = 0.930 | median 0.56, 16–84% range 0.26–0.97; 13 plausible, 7 stretched, 11 implausible |

**Conclusion:** stellar mass-to-light mis-modelling isn't sufficient. The bulge galaxies prefer a larger a₀ even in their outer, deep regime, whatever their stellar M/L. The remaining explanations are other galaxy-specific systematics (distances beyond the catalogued errors, non-circular motions, warps) or a non-universal a₀. The universality question is debated in the literature (Rodrigues et al. 2018, Nature Astronomy 2, 668; replies by McGaugh et al. and Kroupa et al. 2018). Either way, a single universal a₀ = cH₀/2π doesn't fit these 31 galaxies with standard mass models. For the hypothesis, that's a mark against, unless a non-stellar systematic is found.

### What remains open (the honest path forward)

1. **Theory:** construct an action whose weak-field limit is RAR-like. A canonical scalar can't do this; look at AQUAL-type or AeST-type structures (Bekenstein & Milgrom 1984; Skordis & Złośnik 2021).
2. ~~**Sharpen the a₀ test:** marginalize distance and inclination.~~ **Done** (Step 2). ~~Understand why gas- and star-dominated galaxies disagree.~~ **Done** (Step 3): it's bulges. ~~Test whether bulge masses explain it.~~ **Done** (Step 4): stellar M/L alone doesn't. **Next:** independent distances (TRGB, Cepheids) and resolved 2-D kinematics for the 31 bulge galaxies, to tell galaxy-specific systematics apart from a non-universal a₀.
3. **Redshift evolution:** test a₀ ∝ H(z) against published z ≈ 1–2.5 rotation curves (Genzel+2017; Nestor Shachar+2023), which currently disfavor strong evolution.
4. **Solar System:** add the External Field Effect quadrupole and compare with Cassini (Hees+2014, 2016).
5. **Release hygiene:** publish a new Zenodo *version* with the correction statement, so the earlier DOI points readers to the fix.
6. **Human review:** have an independent physicist review the revised paper before submission.

---

## Appendix A: How to reproduce everything

```powershell
# Re-run the original pipelines (now reading the quarantined SYNTHETIC fixtures; they print a warning banner)
cd emergent_matter_model
python fit_astrometry.py --dataset all
python fit_sparc.py --galaxy all --optimize
python fit_jwst.py
python stress_test_solar_system.py

# Run the independent audit (sections 1-7 of the evidence above)
cd ..
python tools/show_your_work_audit.py            # includes real-SPARC download and re-fit (~2-5 min)
python tools/show_your_work_audit.py --no-sparc # offline

# Run the real-data analysis that replaces the SPARC regime (section 8)
python emergent_matter_model/sparc_real_analysis.py
```

## Appendix B: References used for verification

* GRAVITY Collaboration (2026), *Discovery of a star sensitive to the spin of Sgr A\**, Nature; arXiv:2607.12664. S301: a ≈ 83 mas, e ≈ 0.983, P ≈ 8.7 yr; radial velocity not yet measured.
* GRAVITY Collaboration (2020), A&A 636, L5. S2 Schwarzschild precession.
* Gillessen, S. et al. (2017), ApJ 837, 30. Public S-star astrometry tables.
* Lelli, F., McGaugh, S. & Schombert, J. (2016), AJ 152, 157. SPARC database.
* McGaugh, S., Lelli, F. & Schombert, J. (2016), PRL 117, 201101. Radial Acceleration Relation.
* Milgrom, M. (1983), ApJ 270, 365; Milgrom, M. (1999), Phys. Lett. A 253, 273 (a₀ ≈ cH₀/2π).
* Bekenstein, J. & Milgrom, M. (1984), ApJ 286, 7. AQUAL.
* Bekenstein, J. & Sanders, R. (1994), ApJ 429, 480. Lensing in conformally coupled theories.
* Famaey, B. & McGaugh, S. (2012), Living Rev. Relativ. 15, 10.
* DESI Collaboration (2024), arXiv:2404.03002. DR1 BAO, Table 1.
* Chae, K.-H. (2023), ApJ 952, 128; Banik, I. et al. (2024), MNRAS 527, 4573. Wide binaries (disputed).
* Bouwens, R. et al. (2022), ApJ 931, 160. REBELS (REBELS-12 at z = 7.35).
