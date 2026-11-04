# Candidate A option-3 source reconstruction audit

**Date:** 2026-11-04

**Status:** Preparation-only audit. Kirk approved a literature-constrained,
axisymmetric parametric-profile family. Its exact profiles, priors, uncertainty
model, and observational protocol are not frozen. No source reconstruction,
imputation, fit, or new observational claim was performed.

## Scope and reproducibility

This audit applies the existing
[all-option protocol](../knowledgebase/candidate_a_all_options_protocol.json)
without changing it. The protocol SHA-256 and the pinned Leroy `ReadMe`,
`table4.dat`, and `table7.dat` hashes verified. The certified SPARC loader
returned the expected primary sample of 153 galaxies and 3,168 points. The
existing `audit_density_profiles` routine was run in memory; no result artifact
was written or overwritten.

## Findings

| Quantity | Audit result |
|---|---:|
| Galaxies in Leroy table 4 | 23 |
| Leroy/SPARC primary-sample overlap | 11 |
| Profile rows across those overlaps | 369 |
| Overlap galaxies complete in all tabulated components | 0 of 11 |
| HI component values missing | 13 |
| H2 component values missing | 265 |
| Stellar component values missing | 0 |
| Rows with at least one missing component | 265 |
| Nonpositive or missing profile radii | 0 |
| Negative component values | 0 |
| Upper-limit flags: HI / stars (raw `== 1.0` count) | 28 / 10 |
| Censored values after flag correction: HI / stars | 13 / 0 |
| Vertical volume-density profiles supplied | No |

**Erratum (flag semantics).** The raw count treats every `1.0` in the
uncertainty columns as an upper limit. Inspection shows that a present value
with `1.0` is a measurement with rms 1.0. Only a blank value with `1.0` is
consistently censored. That gives 13 censored HI values, exactly the 13 blank
HI entries, and no censored stellar values. The committed all-option artifact
keeps the raw count unchanged. The
[reconstruction specification](EMRF_CANDIDATE_A_OPTION3_RECONSTRUCTION_SPEC_2026-11-04.md#71-flag-semantics-erratum-to-the-source-audit)
uses the corrected semantics, pending verification against the published
table.

Every overlap has at least one missing H2 value. Missing values were not
replaced with zero. The table notes that the gas surface densities already
include helium; a reconstruction must not apply another helium correction.
The source tables are projected surface densities, so their completeness at
the tabulated radii does not supply the missing three-dimensional geometry.

## Reconstruction gates still open

The approved route is a literature-constrained axisymmetric parametric model
with scale-height and conversion uncertainties, plus explicit treatment of
censored and missing measurements. This selects a model family, not a complete
reconstruction specification. Before any option-3 fit, the source model and
observational protocol must resolve:

- how stellar discs and bulges are deprojected, including vertical scale
  heights, inner structure, and the mapping to the SPARC distances and
  inclinations;
- how HI and H2 maps/profiles, missing measurements, and upper limits are
  represented, including the CO-to-H2 conversion and its uncertainty;
- how radial truncation, outer extrapolation, resolution, and measurement
  covariance are handled;
- whether the claim is restricted to the specified weak-field effective
  source law or has a covariant, conserved completion;
- whether `alpha` and `rho0` are global or galaxy-specific, and how their
  domains and nuisance parameters are set independently of the fit;
- which sample, comparator, statistic, uncertainty treatment, and calibrated
  decision threshold are frozen in a new observational protocol.

The preparatory routes are:

1. Retrieve and qualify the underlying HI, CO, and photometric observations,
   then reconstruct each three-dimensional source with explicit measurement
   and geometry uncertainties.
2. **Selected at the model-family level:** specify a parametric axisymmetric
   volume-density model with independent literature-based priors on
   deprojection and scale heights, propagate conversion and measurement
   uncertainties, treat censored/missing values explicitly, and report
   sensitivity to those assumptions. This is a model assumption, not a direct
   measurement. Numerical priors and implementation details remain open.
3. Search for a separately justified complete-source sample. The current 11
   overlaps do not provide one; sample restriction would itself need to be
   fixed before fitting.

Rotation curves or component speed tables alone do not uniquely determine a
nonspherical, finite-thickness volume density. They are not a substitute for
the missing source reconstruction.

## Conclusion

Option 3 remains **blocked pending a fully specified three-dimensional source
reconstruction and a new frozen observational protocol**. The broad
reconstruction family is approved, but its numerical priors and treatment of
the incomplete profiles are not. This audit confirms the data gate; it neither
rejects nor supports option 3 and does not change the option-2 SPARC result or
option-1 conditional GR checks.
