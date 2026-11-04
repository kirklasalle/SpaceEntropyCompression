# Candidate A option-3 three-dimensional source reconstruction specification

**Date:** 2026-11-04

**Status:** Specification for the **frozen** protocol
[`candidate_a_option3_reconstruction_protocol.json`](../knowledgebase/candidate_a_option3_reconstruction_protocol.json)
(SHA-256 `CD9687DDAC497025E709FCCC0C6BAF3D40AE5BCE92166B8C23FEFEEC16270518`).
The JSON is authoritative where the two differ. The approved decisions are
recorded in [§9](#9-approved-decisions-and-frozen-protocol). No reconstruction,
fit, or observational statistic has been computed. This is a model-assumption
document, not a measurement.

## 1. Scope

This specification applies option 3 of the frozen
[all-option protocol](../knowledgebase/candidate_a_all_options_protocol.json)
(SHA-256 `99bb1ab4…3847`) without changing it:

- `rho_eff = rho0 * (rho_bar / rho0)^(1/alpha)`, applied after summing stellar,
  HI and H2 volume densities;
- `nabla^2 Phi = 4 pi G rho_eff`, and `V_c^2 = R dPhi/dR` at `z = 0`, computed
  from the full source with `axisymmetric_v2`;
- no second helium factor, because the Leroy gas surface densities already
  include helium.

It specifies how `rho_bar(R, z)` is built from the pinned Leroy et al. (2008)
profiles. It does not establish a covariant completion. The GR gate still
requires an additional source or modified dynamics for nonunit `alpha`.

## 2. Prior knowledge disclosure

The analysis cannot be blind:

- The SPARC rotation curves for these galaxies were analysed in the option-2
  test, which rejected option 2.
- On 2026-11-04, an exploratory density-table extract also printed Leroy's
  published Table 4 `vflat` rotation-curve fit parameter for the 11 overlap
  galaxies. These are Leroy's values, not SPARC data, and no statistic was
  computed. They are nonetheless outcome-related prior knowledge.
- Bacchini et al. (2019) derived gas thicknesses for these galaxies using
  dark-matter halos fitted to rotation curves. Those per-galaxy thicknesses are
  **not** used, because they encode the fit target.

Any option-3 protocol must be labelled non-blind and post-data-exposure.

## 3. Inputs and geometry

| Input | Use |
|---|---|
| Leroy `table7.dat` | Ring-centre radius `r`, `SigmaHI`, `SigmaH2`, `Sigma*`, and their rms values (face-on, inclination-corrected, gas including helium) |
| Leroy `table4.dat` | Distance, inclination, stellar scale length `l*`, CO scale length `lCO`, global `logMH2` and its 5σ upper-limit flag |
| SPARC primary-sample metadata | Distance and inclination only, to align geometry with the rotation data |

**Distance and inclination alignment.** Radii scale as
`R = r * D_SPARC / D_Leroy`. Surface densities in `Msun pc^-2` are
distance-independent. Face-on surface densities are rescaled for inclination
as `Sigma * cos(i_SPARC) / cos(i_Leroy)`. In the fit, the option-2 distance and
inclination nuisances apply to the aligned source. Sensitivity: retain Leroy's
geometry.

## 4. Radial representation

- Between ring centres, interpolate `ln Sigma` linearly in `R` for each
  component with positive values.
- Inside the innermost ring centre, the primary model keeps `Sigma` constant to
  `R = 0`. Sensitivity: inward exponential continuation with scale length
  `l*` for stars.
- Beyond the outermost ring centre, the primary model truncates each component
  at `R_max + Delta R / 2`, where `Delta R` is the galaxy's outer ring spacing.
  Sensitivity: an exponential tail using that component's mean log-slope over
  its last three positive rings.
- Any observational statistic is evaluated only at SPARC radii inside the
  Leroy coverage `[R_min, R_max]`, after distance alignment.

## 5. Vertical structure

All components are even in `z`, normalized so that `integral rho dz = Sigma(R)`.

### 5.1 Stellar disc

`rho_*(R, z) = Sigma_*(R) / (2 z0) * sech^2(z / z0)`, with `z0 = 2 h_z`
(Bershady et al. 2010 convention) and `h_z = h_R / q`:

`log10 q = 0.367 log10(h_R / kpc) + 0.708`, with 0.095 dex 1σ scatter per
galaxy (Bershady et al. 2010, ApJ 716, 234, eq. 1, calibrated on Kregel et
al. 2002). Here `h_R = l*` from Leroy Table 4, after distance alignment. The
scale height is radially constant, following Kregel et al. (2002) and de Grijs
& Peletier (1997) for late-type discs.

Cross-checks and sensitivity bracket: Kregel et al. (2002, MNRAS 334, 646)
report a volume-corrected `<h_R/h_z> = 7.3 ± 2.2`. Bacchini et al. (2019) adopt
`z* = R*/5` for `sech^2(z/z*)`, which is `q = 10`. The sensitivity grid
evaluates `q` at the relation value ±0.19 dex (±2σ).

**Band caveat:** the relation is calibrated on I-band scale lengths, while
`l*` comes from 3.6 µm Σ*. That systematic is covered by the scatter and
sensitivity grid only to the extent the bands agree; it is recorded as a model
assumption.

### 5.2 Bulges

Leroy's `Sigma*` is a single profile without a bulge decomposition. The primary
model treats all stellar mass as the disc in §5.1. As a bounding geometry
sensitivity, the inner excess of `Sigma*` above an exponential disc with scale
length `l*` (normalized at `R = 2 l*`) is placed in a spherical component,
deprojected by Abel inversion. Thin disc and sphere are the two geometric
limits, so no axis-ratio prior is introduced.

### 5.3 Atomic and molecular gas

Gaussian vertical profiles with `sigma_z = HWHM / sqrt(2 ln 2)`. The primary
values are Milky Way measurements inside the solar circle (Marasco et al. 2017,
A&A 607, A106):

| Component | HWHM | Velocity dispersion |
|---|---:|---:|
| HI | 202 ± 28 pc | 8.9 ± 1.1 km/s |
| H2 | 64 ± 12 pc | 4.4 ± 1.2 km/s |

Required flaring sensitivity: replace the constant thickness by the harmonic
hydrostatic thickness in the reconstructed **Newtonian baryonic** midplane
density, `sigma_z,g(R) = sigma_g / sqrt(4 pi G rho_bar(R, 0))`, iterated to
self-consistency, using the dispersions above. It uses no rotation curve or
halo. Low-mass galaxies (DDO 154, IC 2574) are expected to be most sensitive to
this choice.

### 5.4 Thickness degeneracy with `rho0`

For any single component `rho = Sigma / h * g(z/h)`, the vertically integrated
effective source is
`Sigma_eff = (rho0 h)^(1 - 1/alpha) * Sigma^(1/alpha) * integral g(u)^(1/alpha) du`.
A common rescaling of all thicknesses is therefore nearly degenerate with
`rho0` whenever `alpha != 1`. Relative thicknesses between components and
galaxies, and radial flaring, are not absorbed. Consequently, the thickness
priors are inference-relevant and cannot be treated as negligible nuisances.

## 6. Conversion factors

- **CO-to-H2.** Leroy adopts `X_CO = 2 × 10^20 cm^-2 (K km s^-1)^-1`,
  `I_CO(2-1) = 0.8 I_CO(1-0)`, and the 1.36 helium factor. A global
  multiplicative factor `f_CO` on CO-derived `Sigma_H2` has range
  `[0.7, 1.3]`, from the ±30% uncertainty for Milky-Way-like discs in Bolatto,
  Wolfire & Leroy (2013, ARA&A 51, 207). Low-metallicity and central `X_CO`
  departures are recorded as unmodelled systematics, not silently absorbed.
- **Stellar mass-to-light.** Leroy uses `Upsilon_K = 0.5 Msun/Lsun,K` with a
  fixed `I_3.6 = 0.55 I_K`; their Bell et al. (2003) colour estimate gives a
  sample mean range of 0.48–0.60. A per-galaxy multiplicative factor
  `f_* = Upsilon / 0.5` is a nuisance; its bounds are a decision item in §9.
- **Helium.** No factor is applied. Tests must assert this.

## 7. Missing and censored data rules

### 7.1 Flag semantics (erratum to the source audit)

The Leroy ReadMe says `1.0 = upper limit` in the `e_SigmaHI` and `e_Sigma*`
columns. Inspection shows that rows with a **present** value and `1.0` are
measurements with an rms of 1.0. For example, IC 2574 has
`SigmaHI = 9.0 ± 1.0`, and NGC 2841 has stellar `170.8 ± 1.0`. The only
consistent censoring pattern is a **blank** value with `1.0`, which we
interpret as `SigmaHI < 1.0 Msun pc^-2`. Across the 11 overlaps:

- HI: 13 censored rows, exactly the 13 blank HI values (NGC 2841 at
  `r <= 3.1 kpc`; NGC 2976 at `r >= 3.2 kpc`). The earlier audit count of 28
  included 15 genuine rms values of 1.0.
- Stars: no censored values. All 10 audit flags are genuine rms values.

**Verification gate D1:** resolved below.

### 7.2 Classification and treatment

No missing value is replaced by zero without being labelled as one end of an
explicit interval. Every censored or unmeasured quantity enters as an interval
`[low, high]`. The source is built at both envelope ends.

| Class | Galaxies (rows) | Treatment |
|---|---|---|
| HI censored, `< 1.0` | NGC 2841 (5), NGC 2976 (8) | Interval `[0, 1.0]` Msun pc^-2 |
| H2 measured inside, missing beyond CO detection | NGC 3198 (13, `r >= 7.0`), NGC 3521 (11, `>= 10.1`), NGC 5055 (20, `>= 11.5`), NGC 6946 (14, `>= 7.9`), NGC 7331 (17, `>= 11.8`) | Interval `[0, f_CO U]`, with `U` the smallest detected `SigmaH2` in that galaxy's profile |
| H2 missing inside and outside the detected range | NGC 2841 (16: `r <= 3.1` and `>= 9.9`) | Same `[0, f_CO U]` rule. No `lCO` exists for continuation |
| H2 global value of unstated provenance, no CO map | NGC 2403 (57; `logMH2 = 7.3`, `lCO = 1.9`), NGC 2976 (26; `7.8`, `1.2`) | Leroy has no CO data for these galaxies and treats their molecular content as unknown (Table 2; Appendix A.3). Interval from zero to an exponential profile with scale `lCO` whose mass inside the truncation radius is `f_CO × 1.36 ×` the Table 4 mass. At the high envelope this covers the `X_CO` range and a possibly missing helium factor |
| H2 global 5σ upper limit, no profile | DDO 154 (7; `<= 6.8`), IC 2574 (46; `<= 7.9`) | Interval from zero to an exponential profile with scale `l*` whose mass inside the truncation radius is `f_CO × 1.36 ×` the 5σ limit mass |
| No H2 information | NGC 7793 (38) | Excluded from the primary sample; no bound is available |

The row counts total 265, matching the audit.

**Gate D1 resolved.** Leroy et al. (2008, Appendix A) adopt "a working
sensitivity of `SigmaHI = 1 Msun pc^-2`". This matches the 1.0 in the blank HI
rows, so those rows are below the working sensitivity, and the `[0, 1.0]`
interval applies.

**Gate D2 resolved conservatively.** Equation A2 (`SigmaH2 = 4.4 cos i I_CO`)
includes the 1.36 helium factor in the profiles. However, the paper does not
state the helium convention for the Table 4 global masses of the galaxies
without CO maps. The upper ends above therefore include the 1.36 factor. Under
the robustness rule, this conservatism can only make a result
`not_determinable_censoring`; it cannot favour either model.

The six galaxies with CO profiles (NGC 2841, 3198, 3521, 5055, 6946, 7331) are
all HERACLES targets (Leroy Table 2).

### 7.3 Robustness rule

Approved rule: any observational conclusion is reported only if it is
identical when the source is built at the low and high ends of every interval
(with `f_CO = 0.7` and `1.3` respectively). Otherwise the outcome is
`not_determinable_censoring`.

## 8. Validation gates before any fit

These gates use no observed rotation velocity.

| Gate | Check | Threshold |
|---|---|---|
| V1 projection | `integral rho_c dz` reproduces each component's tabulated `Sigma` at every ring centre, for every envelope end and sensitivity variant | Relative error < 1e-3 |
| V2 helium | No helium factor is applied after loading | Exact |
| V3 solver | Existing Miyamoto–Nagai benchmark and order-64/128 convergence pass; for every galaxy and envelope at `alpha` in {0.5, 1, 2} and `log10 rho0` in {−4, −1, 2}, `max |V64² − V128²| / max(|V128²|, 0.01 km² s⁻²)` over retained radii | < 0.005 |
| V3b backend | A GPU implementation reproduces the CPU `axisymmetric_v2` reference on every V3 case, in float64 | < 1e-10 |
| V4 Newtonian descriptive | At `alpha = 1`, compare reconstructed `V_bar` with SPARC tabulated `Vgas`/`Vdisk`/`Vbul` model components (not `V_obs`) | Descriptive only, not a gate |
| V5 sensitivity | Model-only change in `V_c(R)` across §4–§7 variants at fixed `(alpha, rho0)` grid points | Reported before any fit |

Failure of V1, V2, V3 or V3b blocks the fit.

## 9. Approved decisions and frozen protocol

Kirk LaSalle approved the following on 2026-11-04. The complete rules are in
the frozen protocol
[`candidate_a_option3_reconstruction_protocol.json`](../knowledgebase/candidate_a_option3_reconstruction_protocol.json),
SHA-256 `CD9687DDAC497025E709FCCC0C6BAF3D40AE5BCE92166B8C23FEFEEC16270518`.

1. **Parameter sharing and domains.** Global `alpha` in [0.5, 2.0] and global
   `log10(rho0 / Msun pc^-3)` in [−4, 2], profiled on the full 775-point grid
   (steps 0.05 and 0.25 dex) without continuous refinement.
2. **Sample.** 10-galaxy primary sample (NGC 7793 excluded) with censoring
   intervals; the six CO-profile galaxies form a pre-specified secondary sample
   with an independent refit that never changes the primary outcome.
3. **Comparators and statistic.** The option-2 pseudo-isothermal comparator is
   primary, with the option-2 statistic, error inflation (six parameters per
   galaxy) and the 0.999 chi-square threshold with `2N` degrees of freedom. The
   parameter-count difference is `2N − 2`, so this is slightly lenient toward
   A3. A nested `alpha = 1` comparator is secondary.
4. **Nuisances.** Per-galaxy `f_*` in [0.5, 2] log-uniform with a 0.1 dex
   prior in T1 only; `delta_q` with a 0.095 dex prior; distance and inclination
   as in option 2. Inclination enters only through `sin(i) / sin(i0)`; distance
   rebuilds the source at `f_D` times the catalogue distance with gas
   thicknesses fixed in pc. `f_CO` multiplies every CO-derived H2 quantity once.
5. **Robustness rule** in §7.3.
6. **Computation.** Eighteen nuisance starts at every grid point, computed on
   the GPU only after gate V3b passes.

An independent pre-freeze review identified ambiguities in inclination,
distance, starts, outcome logic, nested clamping, secondary refit,
synthetic-profile edges, `f_CO` application and solver scales. All were
resolved as listed above before hashing.

## 10. References

- Bershady M. A. et al. 2010, ApJ 716, 234 (arXiv:1004.5043): disc oblateness
  relation, eq. 1.
- Bolatto A. D., Wolfire M., Leroy A. K. 2013, ARA&A 51, 207: `X_CO`
  uncertainty.
- Kregel M., van der Kruit P. C., de Grijs R. 2002, MNRAS 334, 646
  (arXiv:astro-ph/0204154): disc flattening.
- Leroy A. K. et al. 2008, AJ 136, 2782 (arXiv:0810.2556): profiles,
  `X_CO`, helium and `Upsilon_K` conventions.
- Marasco A. et al. 2017, A&A 607, A106 (arXiv:1707.00743): Milky Way HI and
  H2 scale heights and dispersions.
- Bacchini C. et al. 2019, A&A 622, A64 (arXiv:1810.03616): context and the
  `q = 10` stellar convention only; per-galaxy thicknesses not used.
