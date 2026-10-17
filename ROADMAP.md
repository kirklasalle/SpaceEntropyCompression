# EMRF research roadmap

Current selection (October 16, 2026): A and B, as selected by Kirk LaSalle.
**Both run concurrently** as a [dual-candidate program](docs/EMRF_DUAL_CANDIDATE_PROGRAM.md);
each keeps its own ledger entries, preregistrations and artifacts.
This replaces the
historical timeline that treated incomplete physics as completed milestones.
No schedule or guaranteed discovery is implied.

## 1. Test Candidate B

Follow the [restricted Higgs-portal test contract](docs/engineering/CANDIDATE_B_MODEL_CONTRACT_DRAFT_2026-10-13.md#16-selected-research-program-and-first-test).
The tree-level potential, Higgs-mass matching, lower-bound widths, frozen
preregistration and ATLAS joint-contour comparison are done; the outcome is
conditional compatibility with mu4 bounds. The
[extended tests](docs/engineering/CANDIDATE_B_MODEL_CONTRACT_DRAFT_2026-10-13.md#17-extended-tests-higgs-rate-likelihood-and-cms-direct-resonance-comparison)
add the ATLAS global-mu profile likelihood and a width-matched
CMS-HIG-24-002 direct-resonance comparison. CMS is the stronger bound at
3 of 12 grid points. Next, if pursued: a correlated STXS likelihood,
interference and loop widths, or a published resonance statistical model,
each under a new frozen preregistration.
Do not manufacture a likelihood from summary uncertainties or limit curves.
An excluded restricted model is not exclusion of every possible Candidate B.

## 2. Test all three Candidate A options without conflating evidence

Review the [Candidate A functional comparison](docs/EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md).
Kirk authorized investigation of options 1, 2 and 3 and chose the full-density
route for option 3. The [all-option gates](docs/EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md#12-all-three-options-authorized-full-density-gates)
have run: option 1 passes GR consistency checks, option 2's SPARC rejection
reproduces, and option 3's density mapping and Poisson solver pass numerical
benchmarks. These are not three independent observational tests.

Next for option 3: reconstruct three-dimensional stellar, HI, H2 and bulge
densities using the acquired Leroy profiles and their underlying observations;
treat missing and censored values, vertical structure, inner/outer boundaries,
distance/inclination and conversion uncertainties explicitly. Do not set
missing gas to zero or substitute a spherical mass profile. Specify whether
the model is only a weak-field effective-source ansatz or has a covariant
completion. Then freeze global/local parameter choices, ranges, nuisance
treatments, comparator and decision rule before fitting. No observational
parameter range or likelihood is yet authorized by the diagnostic protocol.

## 3. Establish what the mapping actually says

Check units, independent scales, domain and circularity. An exact scalar GR
identity can be useful without deriving matter. Full equivalence requires
mapping equations, constraints, boundaries and observables. A BIC non-preference
does not establish equivalence.

## 4. Select one observational question

Preserve the original multi-star common-field design as a viable route.
For collisions, use genuine density/temperature/kinematic constraints and
standard plasma alternatives, not a prescribed entropy map. No bulk data
acquisition should precede a specified observable and uncertainty treatment.

## 5. Improve scientific software boundaries

Keep real-data and illustration outputs separate. Continue replacing misleading
legacy labels and validating likelihoods, numerical stability, provenance and
missing-data behavior. Maintain regression tests without equating them with
empirical confirmations.

## 6. Independent review and publication

Seek domain/statistical review of a bounded, reproducible claim. Preserve
negative results and historical corrections. Any release/tag/DOI must identify
the exact revision and avoid inheriting the unsupported claims of old releases.

Current results and blockers: [STATUS.md](STATUS.md), [TASKS.md](TASKS.md),
[regime report](docs/REAL_DATA_REGIME_AUDIT.md).
