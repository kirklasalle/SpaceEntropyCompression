# EMRF dual-candidate program: Candidates A and B

**Updated:** October 16, 2026.
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
| Precise definition chosen? | All three C_m options authorized for investigation, not one final law. Option 2 has a frozen observational definition; option 3 still needs a complete source reconstruction and observational protocol | Only for the restricted model: one circle, quadratic tree-level potential, exact Higgs-mass matching |

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
| [All-option gates](EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md#12-all-three-options-authorized-full-density-gates) | GR consistency, full-density numerical benchmarks, reproduction and public-data audit | Option 1: 81 checks pass. Option 2: 6,621 fields reproduce. Option 3: solver benchmark passes, but **no observational fit**; density reconstruction and an observational protocol remain open |

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
| A | Reconstruct option-3 volume densities, treat missing/censored data and geometry, declare physical scope and freeze an observational protocol. Keep options 1 and 2 as consistency and rejected observational baselines | A qualified full-density observational test, not another software benchmark |
| B | Correlated STXS likelihood, interference and loop widths, or a published resonance statistical model, each under a new frozen preregistration | Tighter or more robust bounds on the restricted coupling |
| B (general) | Connect the restricted model back to the collision energy and entropy budget | Whether the broader candidate makes a distinct prediction |

## 7. Where the records live

- Ledger: [thermodynamic_collision_candidates.json](../knowledgebase/thermodynamic_collision_candidates.json)
- Graph: [GRAPH_MEMORY.json](../knowledgebase/GRAPH_MEMORY.json)
- Candidate A: [functional comparison](EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md)
- Candidate B: [model contract](engineering/CANDIDATE_B_MODEL_CONTRACT_DRAFT_2026-10-13.md)
  and [dimensionality exploration](engineering/CANDIDATE_B_DIMENSIONALITY_EXPLORATION_2026-10-13.md)
- Both: [collision candidate specification](EMRF_COLLISION_CANDIDATE_SPECIFICATION.md),
  [status](../STATUS.md), [roadmap](../ROADMAP.md) and [tasks](../TASKS.md)
