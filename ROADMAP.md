# EMRF research roadmap

Current selection (October 16, 2026); engineering audit (November 3, 2026);
amended model-only validation artifact generated November 5 UTC:
A and B, as selected by Kirk LaSalle.
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
3 of 12 grid points. The restricted-model STXS line is now closed without
computation: it duplicates the already-used global-mu likelihood direction.
Next, if pursued: interference and loop widths, or a published resonance statistical model,
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

The November 4 [reconstruction specification](docs/EMRF_CANDIDATE_A_OPTION3_RECONSTRUCTION_SPEC_2026-11-04.md)
and [frozen protocol](knowledgebase/candidate_a_option3_reconstruction_protocol.json)
define the operational source and test. The amendment-1 model-only run now
reports V1, V3/V3b, V4 and V5: V3/V3b pass, V4 is reported, but V1 and V5 are
incomplete because some tail and spherical-bulge sources are invalid. The
independent spherical-projection recheck passes all 20 cases; resolve the
invalid source assumptions under an explicitly approved protocol change before
any fit. Preserve missing-data intervals and the physical-completion caveat. The
[GPU runbook](docs/site/development/gpu-compute.md) documents the GTX 1050 Ti,
optional dependencies and resource/accuracy limits.
A failed numerical gate blocks the fit; acceleration does not relax the gate.
Frozen-v1's first primary-source check exceeds its convergence threshold
(2.27% versus 0.5%). Kirk approved a separately versioned segmented amendment;
its full model-only run passes V3/V3b and reports V4, while V1/V5 are
incomplete. No fit is authorized. See the
[experiment report](docs/EMRF_CANDIDATE_A_OPTION3_SEGMENTED_EXPERIMENT_2026-11-04.md).

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

Future development (noted 2026-11-04, not started): design and build an
"EMRF farm" volunteer-compute client, in the spirit of SETI@home, so that
frozen-protocol computations can be distributed across contributed CPUs and
GPUs. This needs its own application design, including work-unit definition,
result validation and redundancy, provenance and protocol-hash pinning,
numerical reproducibility across hardware, and contributor security. Distributed
results must be traceable to the exact frozen protocol and code revision and
are computational outputs, not empirical confirmations.

## 6. Independent review and publication

Seek domain/statistical review of a bounded, reproducible claim. Preserve
negative results and historical corrections. Any release/tag/DOI must identify
the exact revision and avoid inheriting the unsupported claims of old releases.

Current results and blockers: [STATUS.md](STATUS.md), [TASKS.md](TASKS.md),
[regime report](docs/REAL_DATA_REGIME_AUDIT.md), and the
[engineering and documentation audit](docs/site/development/project-audit-2026-11-03.md).
