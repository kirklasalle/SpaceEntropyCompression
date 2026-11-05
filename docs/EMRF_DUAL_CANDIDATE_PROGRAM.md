# EMRF dual-candidate program: Candidates A and B

**Updated:** November 5, 2026 (amended model-only validation; observational evidence unchanged).
**Principal investigator:** Kirk LaSalle.

EMRF now runs two research programs concurrently: Candidate A and Candidate B.
Both are active and neither is paused. This document states plainly what each
candidate claims, what has actually been done for each, where the work is
uneven, and the rules that keep the two programs honest.

**Neither candidate is confirmed. No observation in this repository currently
supports A or B over standard physics.**

## 1. How the decision developed

| Date | Author decision | Status |
|---|---|---|
| 2026-10-08 | "I'm for candidate A." A selected; B kept as an unselected proposal | Historical |
| 2026-10-16 | A and B both selected; "one at a time", with B worked first | Historical |
| 2026-10-16 (evening) | "We are now running dual experiment concurrently with candidate A and B" | **Current** |
| 2026-10-16 (later) | "Candidate A, all options 1, 2, and 3 can be tested. Run the gamut." Full-density route selected for option 3 | **Current A investigation scope**, not selection of one final law |

The earlier decisions are kept in the
[candidate ledger](../knowledgebase/thermodynamic_collision_candidates.json)
history rather than rewritten. Files frozen under the earlier decisions (the
two Candidate B preregistrations, the first-test protocol and their result
artifacts) still say "B active". That wording is correct for the time they were
frozen and is deliberately left unchanged; editing them would break their
SHA-256 freezes.

## 2. What each candidate says

| | Candidate A | Candidate B |
|---|---|---|
| Idea | C re-describes existing geometry and energy organization, inside GR | A separately budgeted energy-exchange sector, in a restricted test via physical extra dimensions |
| New force, reservoir or particle? | No | Yes (in the restricted test: a bulk scalar mixing with the Higgs) |
| Origin | Kirk's recovered project intention; "why can't we find this inside of GR?" | AI-proposed generic ansatz; extra dimensions are Kirk's 2026-10-13 specification; the Higgs-portal benchmark is assistant-proposed and Kirk-approved |
| Precise definition chosen? | All three C_m options authorized for investigation, not one final law. Option 2 has a frozen observational definition; option 3 has a frozen source reconstruction and protocol, with numerical gates still incomplete | Only for the restricted model: one circle, quadratic tree-level potential, exact Higgs-mass matching |

The two candidates make different commitments: A adds no new sector and B adds
one. They are developed separately. A bound on B is not evidence for A, and a
difficulty for A is not evidence for B, unless a comparison between them is
specified and frozen in advance. No such comparison exists yet.

## 3. What has actually been done

### Candidate A

| Work | Evidence class | Result |
|---|---|---|
| [Functional comparison](EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md) | Exact-background mathematics | The Einstein-projection reference reproduces a scalar GR identity for alpha = 1 and fixed k. Radiation, vacuum and regional-energy counterexamples rule out treating Ricci or sqrt(K) as a universal local density |
| `tools/check_candidate_a_definitions.py` | Algebra checks, not observations | Identities and counterexamples reproduced |
| [SPARC test of option 2](EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md#11-preregistered-sparc-test-of-option-2) | Preregistered observational falsification test; **not blind** | **Rejected.** With C = C_m, alpha = 1 and M = observed baryons, A predicts that every rotation curve equals its baryonic Newtonian curve. In 153 SPARC galaxies, Delta_Q_cons = 98,216 (T1) and 100,067 (T2) against a threshold of 388.2 |
| [All-option gates](EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md#12-all-three-options-authorized-full-density-gates) | GR consistency, full-density numerical benchmarks, reproduction and public-data audit | Option 1: 81 checks pass. Option 2: 6,621 fields reproduce. Option 3: source and protocol are defined; numerical gates remain incomplete and **no observational fit** was run |

The November 4 [option-3 source audit](EMRF_CANDIDATE_A_OPTION3_SOURCE_AUDIT_2026-11-04.md)
reverified the pinned inputs and found zero complete profiles among the 11
Leroy/SPARC overlaps. Kirk approved a literature-constrained axisymmetric
parametric-profile family. Its source, censoring and test rules are now frozen
in the [option-3 protocol](../knowledgebase/candidate_a_option3_reconstruction_protocol.json)
(SHA-256 `CD9687DD…16270518`). Primary sources have now been reconstructed
without parsing observed velocities. Their conservative order-64/128 check
reaches 2.27%, above the 0.5% threshold, under frozen v1. A distinct
[segmented experiment](EMRF_CANDIDATE_A_OPTION3_SEGMENTED_EXPERIMENT_2026-11-04.md)
records a sub-threshold pre-approval candidate result. Kirk subsequently
approved amendment 1; its hash-verified model-only rerun passes V3/V3b. The fit
remains blocked: the full amendment-1 run reports V4, but V1 and V5 are
incomplete because the outer-tail and spherical-bulge sensitivities fail for
part of the source sample. An independent closed-form spherical projection
recheck passes all 20 galaxy/envelope cases with no integration warnings.
No new observational result has been produced.

Option 2 was originally assistant-proposed; Kirk has now authorized
investigation of all three options. The rejection still falsifies **one
operationalization of A, not Candidate A**. The outcome was
expected: the SPARC mass discrepancy was known, and the preregistration says
so. Option 1 (M = all gravitating energy) is an exact GR identity with no
independent observational discrimination from GR; option 3 (free alpha) has
mathematical and solver checks, not an observational verdict. Calling the missing mass
"emergent matter" would be relabelling unless A predicted its amount
independently.

The earlier SPARC, DESI and Pantheon+ analyses elsewhere in EMRF are real-data
work, but they are **not tests of Candidate A**. They test a phenomenological
acceleration law or standard-cosmology baselines.

### Candidate B

All three tests below use public data and preregistrations frozen by SHA-256
before the relevant data values were read. All apply to the restricted
Higgs-portal model only.

| Test | Data | Outcome |
|---|---|---|
| [First test](engineering/CANDIDATE_B_MODEL_CONTRACT_DRAFT_2026-10-13.md#16-selected-research-program-and-first-test) | ATLAS Run-2 (kappa_V, kappa_F) observed contour | Compatible with limit; kappa_lo = 0.97591 and conditional mu4 bounds |
| [Rate likelihood](engineering/CANDIDATE_B_MODEL_CONTRACT_DRAFT_2026-10-13.md#17-extended-tests-higgs-rate-likelihood-and-cms-direct-resonance-comparison) | ATLAS global signal-strength profile likelihood | Compatible with limit; mu_hat = 1.054, kappa_lo = 0.97059 |
| [Direct resonance](engineering/CANDIDATE_B_MODEL_CONTRACT_DRAFT_2026-10-13.md#17-extended-tests-higgs-rate-likelihood-and-cms-direct-resonance-comparison) | CMS-HIG-24-002 heavy scalar to ZZ limits | Stronger mu4 bound at 3 of 12 grid points; 3 points not covered by the theory tables |

"Compatible with limit" means the data allow the coupling to be zero and set
an upper bound on it. These are **bounds, not detections**: a model that
reduces to the Standard Model when its new coupling vanishes cannot be
supported by data that agree with the Standard Model. The tests do not exclude
Candidate B in general, only coupling values within the restricted model.

The November 4 [STXS feasibility review](engineering/CANDIDATE_B_STXS_FEASIBILITY_DRAFT_2026-11-04.md)
qualified the already-pinned 36-bin measurement vector and its 36 × 36
correlation matrix. ATLAS's Gaussian-approximation appendix supports its SMEFT
fits generally, but does not validate Candidate B's exact bounded universal
rescaling direction. Figure 7 central values were inadvertently exposed
before any new protocol was frozen; no statistic, fit, or bound was computed.
The STXS work is now non-blind and cannot be called prospectively preregistered.
The Gaussian approximation's direction-specific validity gate remains unmet.
That gate is moot for the restricted model: B predicts exactly the global-`mu`
hypothesis, and ATLAS's official global-`mu` profile likelihood from the same
dataset is already the basis of the rate-likelihood test above. An STXS fit
along that direction would add no independent constraint, so the
restricted-model STXS line is closed without any computation. STXS remains
relevant only to a future non-universal variant under a new contract and
protocol.

## 4. Where the work is uneven

Being transparent means saying where the two programs differ in maturity:

- **Both programs now have preregistered public-data tests, but of different
  kinds.** B has three, all on the restricted Higgs-portal model; each gives a
  bound, because that model contains the Standard Model limit. A has one: a
  falsification test of an assistant-proposed operationalization, which
  rejected it. Neither count is a finding about which idea is stronger.
- **A's remaining barrier is a complete prediction and source reconstruction,
  not permission to investigate.** Kirk authorized all three options.
  Option 1 passes conditional GR checks; option 2 is rejected. Option 3's
  nonunit exponent changes the baryonic source and needs declared physical
  scope, three-dimensional density modeling and a frozen observational protocol.
  All 11 overlaps of the newly downloaded Leroy profiles with the certified
  SPARC sample have missing components somewhere; no values were zero-filled.
- **A's test was not blind, and B's tests were not fully blind either.** A's
  outcome was strongly expected from the literature and from earlier work in
  this repository. B's likelihood test was preregistered knowing the ATLAS
  headline signal strength. Both preregistrations disclose this.
- **B's tests cover a narrow benchmark.** They say nothing yet about B's
  original collision-heating motivation, entropy closure or any geometry other
  than one circle.
- **Assistance from AI tools.** Much of the analysis, code and wording for both
  programs was produced by AI assistants under Kirk's direction. Every claim is
  recorded with its evidence class and attribution, but independent review by
  domain experts has not yet taken place.

## 5. Rules shared by both programs

1. Freeze the model, parameter domain, data and decision rule (by SHA-256)
   before reading the outcome-relevant data.
2. Pin every external data file by hash; never substitute synthetic data for
   observations.
3. Label each claim with its evidence class: recovered intent, standard
   physics, new assumption, algebra check, software test or observational
   result.
4. Report outcomes as they fall, including incompatibility, non-coverage and
   numerical problems. Do not rerun with new choices after seeing a result
   unless a new preregistration documents why.
5. Never present compatibility or a bound as confirmation.
6. **Account for multiple tests.** Two programs, many grid points and several
   datasets give more chances for a chance fluctuation to look like a signal.
   Any future claimed anomaly must specify its look-elsewhere treatment in
   advance.
7. Keep A and B separate: separate ledger entries, preregistrations, scripts
   and result artifacts. Do not choose between them by whichever happens to fit
   better without a frozen comparison.

## 6. What would change each status

| Candidate | Next step | What it could establish |
|---|---|---|
| A | Resolve the primary-source convergence failure through approved numerical change control, complete sensitivity validation V1–V3b and report V4–V5 before any fit. Keep options 1 and 2 as consistency and rejected observational baselines | A qualified full-density observational test of one operationalization, not another software benchmark |
| B | Interference and loop widths, or a published resonance statistical model, each under a new frozen preregistration. STXS is closed for the restricted model (redundant with the global-`mu` likelihood) | Tighter or more robust bounds on the restricted coupling |
| B (general) | Connect the restricted model back to the collision energy and entropy budget | Whether the broader candidate makes a distinct prediction |

## 7. Where the records live

- Ledger: [thermodynamic_collision_candidates.json](../knowledgebase/thermodynamic_collision_candidates.json)
- Graph: [GRAPH_MEMORY.json](../knowledgebase/GRAPH_MEMORY.json)
- Candidate A: [functional comparison](EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md)
- Candidate B: [model contract](engineering/CANDIDATE_B_MODEL_CONTRACT_DRAFT_2026-10-13.md)
  and [dimensionality exploration](engineering/CANDIDATE_B_DIMENSIONALITY_EXPLORATION_2026-10-13.md);
  [STXS feasibility draft](engineering/CANDIDATE_B_STXS_FEASIBILITY_DRAFT_2026-11-04.md)
- Both: [collision candidate specification](EMRF_COLLISION_CANDIDATE_SPECIFICATION.md),
  [status](../STATUS.md), [roadmap](../ROADMAP.md) and [tasks](../TASKS.md)

## 8. Engineering checkpoint (2026-11-03)

The non-golden software suite passes (633 passed, 1 skipped, 1 deselected) in
the local Python 3.12.10 environment. Hypothesis 6.169.0 is outside the
development constraint `<6.169`; use the project constraints for an exact CI
environment. These software results do not change either candidate's
scientific status. The workspace profile now declares nine project-local MCP
servers, using `python` from `PATH` and forward-slash workspace-relative paths.
IDS documentation search resolves the project root and returns documentation
hits. Its knowledge graph is not yet populated for Candidate A, so graph
queries do not provide Candidate A lineage; agents must not substitute a
non-local server.

See the [engineering and documentation audit](site/development/project-audit-2026-11-03.md)
for the complete validation record, documentation findings and next gates.

The November 4 preparation work adds an option-3 source audit and a Candidate B
STXS feasibility review. These are not new fits. The
[reconstruction specification](EMRF_CANDIDATE_A_OPTION3_RECONSTRUCTION_SPEC_2026-11-04.md)
sets literature-grounded source rules, and the approved option-3 test is
frozen before any computation with observed velocities. The test is
non-blind. B
remains limited to its existing preregistered bounds. Its restricted-model STXS
line is closed as redundant with the global-`mu` likelihood already used.

### GPU implementation checkpoint (2026-11-04)

The [GPU runbook](site/development/gpu-compute.md) records the verified GTX 1050 Ti
(4 GiB dedicated VRAM, compute capability 6.1), CUDA-12/CuPy environment,
optional dependency installation, host-memory distinction and validation rules.
The reported 32 GB RAM and up-to-16 GB shared GPU memory do not enlarge the
dedicated CUDA allocation budget. Full-fit runtime remains unmeasured; the
earlier 15--25-hour estimate was based only on a synthetic scratch benchmark.

The protocol and historical results are unchanged. Implementation proceeds
through density-only reconstruction and numerical gates, not a fit. GPU/CPU
agreement (V3b) and quadrature convergence (V3) are separate requirements.

The [corrected 180-case artifact](../results/candidate_a_option3_validation_2026-11-04_r2.json)
passes primary projection checks (< 2.75e-9), measured-gas conversion checks,
and CPU/GPU agreement (< 1.28e-15). The conservative V3 convergence check
for frozen v1 fails at 2.27% versus 0.5%; 120 cases exceed the threshold. The
separate segmented experiment's pre-approval model-only result is not
retroactive. The full amendment-1 sensitivity run passes V3 (`2.7904e-4`) and
V3b (`2.0769e-15`); V4 is reported for 20 model-only cases. V1 remains
incomplete because 11 of 20 outer-tail source cases have non-decaying profiles.
V5 reports 10 of 12 variants; the outer-tail variant lacks 11 source pairs,
and spherical-bulge density is negative for eight galaxies, causing 144 of 180
fixed-grid cases to fail. A separate exact line-of-sight integration check of
the piecewise-linear spherical-density interpolant passes all 20 cases at
`6.175843e-4` maximum relative error versus `< 1e-3`, with no integration
warnings. Its hash-verified artifact is
[`candidate_a_option3_projection_recheck_2026-11-05_r2.json`](../results/candidate_a_option3_projection_recheck_2026-11-05_r2.json).
The outer-tail blocker and negative densities remain. No fit or observational
verdict follows.
The exact velocity-dependent fit subset was not evaluated: numerical checks
used all positive-radius rows inside the density coverage.

The hybrid GPU validation path measured 115.04 s versus 36.18 s CPU. It is
currently slower, not the forecast speedup. No optimizer runtime is claimed.
The [initial normalization error](../results/candidate_a_option3_validation_2026-11-04.json)
is retained alongside the corrected run. **No fit was run**, no old evidence
or frozen protocol was changed, and neither candidate is confirmed.
