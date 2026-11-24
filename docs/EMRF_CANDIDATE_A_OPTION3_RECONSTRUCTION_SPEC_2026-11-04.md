# Candidate A option-3 three-dimensional source reconstruction specification

**Date:** 2026-11-04

**Status:** Specification for the **frozen** protocol
[`candidate_a_option3_reconstruction_protocol.json`](../knowledgebase/candidate_a_option3_reconstruction_protocol.json)
(SHA-256 `CD9687DDAC497025E709FCCC0C6BAF3D40AE5BCE92166B8C23FEFEEC16270518`).
The JSON is authoritative where the two differ. The approved decisions are
recorded in [§9](#9-approved-decisions-and-frozen-protocol). The primary
reconstruction has now been implemented and checked without observed
velocities; the conservative V3 convergence check fails, so no fit or
observational statistic has been computed. See the [validation addendum](#11-implementation-and-validation-addendum).
This is a model-assumption document, not a measurement.

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
as `Sigma * cos(i_SPARC) / cos(i_Leroy)` once. The fitted inclination affects
only the velocity projection, not the source density. The distance nuisance
scales all source and field radii and stellar height, leaving gas thicknesses
fixed in pc; do not apply another square-root distance factor. Sensitivity:
retain Leroy's geometry.

## 4. Radial representation

- Between ring centres, interpolate `ln Sigma` linearly in `R` for each
  component with positive values; interpolate linearly in `Sigma` across a
  zero endpoint.
- Inside the innermost ring centre, the primary model keeps `Sigma` constant to
  `R = 0`. Sensitivity: inward exponential continuation with scale length
  `l*` for stars.
- Beyond the outermost ring centre, the primary model truncates each component
  at `R_max + Delta R / 2`, where `Delta R` is the galaxy's outer ring spacing;
  hold the last ring value constant up to that cutoff.
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
  `f_* = Upsilon / 0.5` is a nuisance with approved bounds [0.5, 2] in §9.
- **Helium.** No second factor is applied to measured gas profiles. The
  explicitly stated global-mass upper envelopes in §7 include 1.36; tests
  distinguish these from already-corrected measured profiles.

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
without CO maps. The upper ends above therefore include the 1.36 factor.
This is an assumed envelope, not proof of conservative statistical coverage.
Agreement at both ends does not establish monotonicity of the statistic inside
the interval or guarantee that widening it cannot favour either model.

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
| V2 helium | No second helium factor on measured gas profiles; the global-mass envelope exceptions are explicit | Exact |
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

The full-grid and full-multistart prescriptions remain frozen. No runtime
commitment follows from them: the scratch GPU timing was not a complete fit
benchmark. See the resource record below.

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

## 11. Implementation and validation addendum

The [model-only runner](../tools/validate_candidate_a_option3.py) and optional
[GPU backend](../tools/candidate_a_option3_gpu.py) implement primary sources.
The [resource runbook](site/development/gpu-compute.md) gives hardware,
dependencies, memory limits, commands, timing caveats and failure handling.

The [corrected validation artifact](../results/candidate_a_option3_validation_2026-11-04_r2.json)
records 180 galaxy/envelope/parameter cases. Primary projection checks are
below `2.75e-9`; V2 passes within primary scope. CPU/GPU agreement is below
`1.28e-15` at both quadrature orders. However, the conservative V3 check reaches
`0.0226783304`, above the frozen `0.005` threshold, with 120 cases exceeding it.
The check uses every positive-radius row inside the density coverage, not
the unevaluated velocity-dependent fit subset.

**Outcome at this checkpoint: incomplete; fit blocked.** At that time, full V1
required sensitivity variants that had not yet been validated, and V4/V5 had
not been run. The later amendment-1 sensitivity run is reported in §12 below.
This is not a rejection of option 3 or evidence for either candidate.
The [initial implementation failure](../results/candidate_a_option3_validation_2026-11-04.json)
is retained separately; the corrected run does not overwrite it.

Any revised numerical prescription must be approved and versioned separately.
The frozen JSON and its hash above remain unchanged. The earlier implication
that a synthetic order-64 benchmark established sufficient accuracy, or a
15--25-hour fit duration, is withdrawn; neither was measured on this workload.

## 12. Amendment-1 sensitivity validation update (2026-11-05)

The full model-only run is recorded in
[`candidate_a_option3_sensitivity_validation_2026-11-04.json`](../results/candidate_a_option3_sensitivity_validation_2026-11-04.json),
SHA-256 `b3d502f5b9be54260979e990b82a6dc398a4bc2b1800370eb4a99b4cf3be4654`.
It verifies amendment 1 SHA-256
`d71702204520526730b78f2df0298db272cd1b210572f83e5a6d02aac2898c3c`, the
unchanged parent-protocol hash, all recorded source hashes, and the absence of
observed-velocity parsing or an observational fit. The run covered the 12
frozen source variants, 10 primary galaxies, and low/high envelopes.

- **V1: incomplete.** The primary and ten other successfully constructed
  variants met the reported projection threshold. The outer-exponential-tail
  variant could not be built for 11 of 20 galaxy/envelope sources because at
  least one component's mean terminal log-slope was nonnegative; its infinite
  tail would have non-finite mass. The largest reported projection error was
  `6.1755e-4` versus `< 1e-3`. SciPy warnings from the spherical-profile
  improper integral were independently checked with a closed-form
  line-of-sight integral of the piecewise-linear spherical-density interpolant:
  all 20 galaxy/envelope cases pass at maximum relative error
  `6.175843e-4`, with zero integration warnings. The
  [projection recheck artifact](../results/candidate_a_option3_projection_recheck_2026-11-05_r2.json)
  records the method and hashes. V1 nevertheless remains incomplete because
  the outer-tail variant cannot be constructed for 11 cases.
- **V2: passed** for the measured-gas conversion and synthetic-envelope checks.
- **V3: passed** at `2.790382718485572e-4` versus `< 0.005` over 180 cases.
- **V3b: passed** at `2.076880311640573e-15` versus `< 1e-10` at both orders
  over the same primary-source cases.
- **V4: reported model-only** for 20 galaxy/envelope cases. It compares
  reconstructed baryonic component speeds with the tabulated Newtonian
  component sum; it does not parse observed velocities or form a fit statistic.
  The largest absolute `delta Vbar^2` was `100977.8781 km^2/s^2`; the largest
  relative discrepancy was `0.941354`.
- **V5: incomplete.** Ten of 12 variants produced all 180 fixed-grid
  summaries. The outer-tail variant lacked 11 source pairs. The
  spherical-inner-bulge variant produced 36/180 cases; its Abel-deprojected
  stellar profile makes total baryonic density negative for IC 2574, NGC 2403,
  NGC 2841, NGC 2976, NGC 3198, NGC 3521, NGC 5055 and NGC 6946. These
  densities were rejected, not clipped.

The V5 values below are maximum absolute and relative changes in model-only
`Vc` over the nine-point grid and each variant's available galaxy/envelope
cases. Partial-variant maxima are descriptive only and do not establish a
complete sensitivity result.

| Variant | Cases | Max `|delta Vc|` (km/s) | Max relative `delta Vc` | Status |
|---|---:|---:|---:|---|
| Primary | 180/180 | 0 | 0 | Reported |
| `delta_q_minus_0.19` | 180/180 | 4935.54 | 0.286784 | Reported |
| `delta_q_plus_0.19` | 180/180 | 6319.19 | 0.373387 | Reported |
| `gas_hwhm_minus_1sigma` | 180/180 | 816.18 | 0.068598 | Reported |
| `gas_hwhm_plus_1sigma` | 180/180 | 597.12 | 0.054708 | Reported |
| `hydrostatic_gas_flaring` | 180/180 | 44930.03 | 2.491136 | Reported |
| `inward_stellar_exponential` | 180/180 | 153.78 | 0.053185 | Reported |
| `outer_exponential_tails` | 81/180 | 211.70 | 0.161918 | Incomplete |
| `spherical_inner_bulge` | 36/180 | 1725.31 | 0.098374 | Incomplete |
| `leroy_geometry` | 180/180 | 4101.67 | 1.389690 | Reported |
| `t1_upsilon_k_0.4` | 180/180 | 3632.80 | 0.200690 | Reported |
| `t1_upsilon_k_0.6` | 180/180 | 3632.69 | 0.200663 | Reported |

The total validation run took `5893.1996` seconds; this is not a fit-runtime
estimate. The artifact records `fit_permitted: false`,
`observed_velocities_parsed: false` and
`observational_fit_performed: false`. **The fit remains blocked.** Do not alter
the frozen protocol, truncate non-decaying tails, or clip negative
deprojections. Any replacement source assumptions require a separately
approved, versioned protocol and a new model-only validation.
