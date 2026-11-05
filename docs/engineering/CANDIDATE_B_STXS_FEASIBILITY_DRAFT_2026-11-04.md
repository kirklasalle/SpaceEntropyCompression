# Candidate B STXS likelihood feasibility and protocol gates

**Date:** 2026-11-04

**Status:** Closed for the restricted model without computation. Source
qualification completed for the pinned measurement vector and correlation
table. A metadata-print command inadvertently exposed the Figure 7 `Data` and
`SM prediction` central values before any new protocol was frozen. No
statistic or fit was computed. The Gaussian STXS approximation's
model-direction validity gate remains unmet. For the restricted universal-
rescaling model, the official full profile likelihood along that direction is
the global-`mu` scan already used by the frozen extended test, so an STXS
analysis would add no independent constraint (see
[Gate resolution](#gate-resolution-for-the-restricted-model)). No new
empirical result is claimed.

## Scope

This draft concerns only Candidate B's selected restricted one-circle,
tree-level Higgs-portal model and its existing parameter grid. It does not
extend the model, add widths, or combine Candidate A and B. The frozen parent
and extended preregistrations remain unchanged.

The candidate source is the ATLAS HIGG-2022-17 interpretation paper,
[arXiv:2402.05742](https://arxiv.org/abs/2402.05742),
published as [JHEP 11 (2024) 097](https://doi.org/10.1007/JHEP11(2024)097).
It reports Run-2 Higgs production/decay and STXS measurements using up to
139 fb^-1 at 13 TeV, includes STXS-based interpretations, and discusses the
validity of a Gaussian approximation in its SMEFT interpretation. These facts
make it a plausible source to qualify, not a validated likelihood for this
Candidate B model.

The project already pins the HEPData record
[ins2104706 v1](https://www.hepdata.net/record/ins2104706?version=1), the ATLAS
2022 measurement submission also used for the earlier Candidate B contour
comparison. Its original archive is
[`hepdata_ins2104706_v1_original.zip`](../../data/external/candidate_b/raw/hepdata_ins2104706_v1_original.zip),
SHA-256 `7237c3e7195df686d03f4abfd1b1969ec38f41059a9b38e2d8aed44a6b858d6e`.
The archive contains:

| Input | Contents | SHA-256 |
|---|---|---|
| `figure_7.yaml` | 36 measured STXS bins, SM predictions, and reported uncertainties | `e4f8a619976a48a93126677ede424278934e45c6924b0cefcd8b918a20ba3f9e` |
| `AuxFig13.yaml` | 36 × 36 STXS correlation matrix (HEPData metadata maps this to “Aux Figure 23”) | `de31458a9e8590182aff3b3a846d1579bdd9fe335209d2fa2006e1a1901a8094` |

These are source-qualified inputs, not an official full likelihood. The
Figure 7 metadata reports a 94% SM-compatibility p-value. In addition, the
metadata-print command exposed its `Data` and `SM prediction` central-value
entries before a new analysis protocol was frozen. No uncertainty or
correlation entries were used, and no statistic, fit, or bound was computed.
Any later STXS analysis is non-blind and cannot be represented as preregistered
before the numerical outcomes were read.

ATLAS HIGG-2022-17 ([arXiv:2402.05742](https://arxiv.org/abs/2402.05742),
JHEP 11 (2024) 097) states that its STXS measurements are identical to those
used in its reference [9]. This establishes overlap with an already used ATLAS
measurement product. The STXS result must not be multiplied with the prior
contour/global-`mu` results or presented as independent evidence without a
justified joint likelihood.

## Model mapping to test

Under the existing restricted hypothesis, the observed 125 GeV state has
universal modifier `kappa <= 1`, with `mu = kappa^2`. With SM kinematics and
no new or invisible 125 GeV decays, each included STXS production/decay
observable would therefore scale by the same `mu`. This is a one-parameter
direction through the published measurement space, not a new Candidate B
prediction. The `mu4 = 0` Standard Model limit remains allowed, so an STXS
result can set a conditional bound but cannot confirm the candidate.

The paper's appendix compares the collaboration's complex full STXS likelihood
with a covariance-based Gaussian approximation for its SMEFT fit, including
linear and quadratic SMEFT terms. It calls the approximation reasonably good
and reports generally good agreement in expected/observed parameter estimates
and 68%/95% intervals. The paper also says the full likelihood, with 78
cross-section parameters and over a thousand nuisance parameters, is not
readily available.

That is useful validation evidence for the paper's SMEFT fits, but it does not
demonstrate the Gaussian approximation's validity or coverage specifically
along Candidate B's one-dimensional universal-rescaling direction with
`0 <= mu <= 1` and a one-sided bound. The public covariance summary is not the
full likelihood. The required model-direction validity gate is therefore
**unmet**. Under the approved rule, do not fit the Gaussian fallback unless
that direction-specific validation is established; otherwise stop without a
fit.

## Remaining gates before a new analysis protocol can be frozen

1. Establish access to an official profile likelihood or a direction-specific
   validation of the covariance approximation for the Candidate B
   `mu`-rescaling model, including its boundary and one-sided confidence rule.
   The published SMEFT appendix alone does not pass this gate.
2. Verify the STXS bin mapping and exact uncertainty/correlation semantics
   against the table metadata before selecting the covariance construction.
3. Keep the known overlap with the ATLAS Nature 2022 analysis explicit; do not
   combine the results without a justified joint likelihood.
4. Only after gates 1–3 pass, freeze a separate protocol before any numerical
   computation, specifying the input members and hashes, covariance
   treatment, statistic, confidence construction, allowed `mu` domain,
   parameter-grid translation, validity checks, and incomplete-data outcome.
   Because central values have already been exposed, label it non-blind and
   post-data rather than prospective preregistration.

The published ATLAS interpretation, the HEPData metadata p-value, and the
Figure 7 central values have been inspected during this feasibility review.
Any future test must disclose this prior knowledge and must not be described
as blind or pre-data preregistered.

## Candidate statistical form (not authorized)

If ATLAS supplies an applicable profile likelihood, use it directly. A
covariance approximation would require a separately established
model-direction validity gate. Only then could a candidate form be

`q(mu) = (x - mu*s)^T V^-1 (x - mu*s)`,

where `s` is the documented SM prediction in the same STXS convention. The
equation is a design sketch only; the inputs, error symmetrization, covariance
construction, statistic, and confidence rule have not been preregistered.

Possible report outcomes are conditional compatibility/bound, incompatibility
of the restricted family under the frozen rule, or not determinable because
the required data product or coverage qualification is unavailable. No
outcome may be called support for Candidate B.

## Gate resolution for the restricted model

Gate 1 asks for an official likelihood along Candidate B's direction or
direction-specific validation of the covariance approximation. For the
restricted model, an official likelihood along exactly that direction already
exists and has already been used:

- The frozen extended preregistration,
  [`candidate_b_extended_test_preregistration.json`](../../knowledgebase/candidate_b_extended_test_preregistration.json)
  (`test_a_higgs_rate_likelihood`), uses `AuxFig1.yaml` “Aux Figure 8
  (Total)” from the same pinned ins2104706 v1 archive: ATLAS's observed
  `-2 ln Lambda(mu)` for the global signal strength, including all systematic
  uncertainties.
- Its frozen validity statement is that the restricted model predicts exactly
  the global-`mu` hypothesis (universal rate scaling, SM kinematics), with
  `mu = kappa^2`. In that hypothesis every STXS production × decay rate scales
  by the same `mu`. That is the one-dimensional direction an STXS fit would
  probe.
- The STXS bins and the global-`mu` scan come from the same ATLAS 2022 events
  and analysis. Along the universal direction, the collaboration's profile
  likelihood is the reference that a covariance approximation of the STXS
  summary would try to reproduce. It cannot add independent information.

Therefore:

1. An STXS Gaussian fit for the restricted model would be at most an
   approximation to a likelihood the project already uses. It is **not an
   independent test** and is not pursued. No STXS statistic, bound, or
   artifact will be produced for this model.
2. This closes the restricted-model STXS line on redundancy grounds. It does
   not pass the Gaussian validity gate, and it does not change or strengthen
   the existing extended-test result, which remains a conditional bound and
   not evidence that Candidate B is confirmed.
3. STXS data would become relevant only for a different hypothesis that
   predicts non-universal (production-, decay-, or kinematics-dependent)
   deviations. That would require a new model contract and a new frozen
   protocol. The central-value exposure recorded above would make any such
   STXS analysis non-blind and post-data.

## Decision

The source is qualified and byte-pinned. The Gaussian STXS approximation's
direction-specific validity gate is not met. For the restricted model, the
question is resolved without computation: the official global-`mu` profile
likelihood along the model's direction is already the basis of the frozen
extended test, so STXS adds no independent constraint. Do not calculate an
STXS bound, update existing test artifacts, or combine this product with the
prior ATLAS analyses. The accidental central-value exposure remains disclosed
and would apply to any future non-universal variant.
