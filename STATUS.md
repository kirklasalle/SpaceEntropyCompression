# EMRF current status

Research selection updated October 16, 2026; engineering audit updated November 3, 2026; Candidate A option-3 model-only sensitivity validation updated November 5, 2026. A and B run concurrently. This replaces the old all-green dashboard; historical
versions remain in Git history and the [correction archive](docs/archive/antigravity_recovery/README.md).

| Area | Current state |
|---|---|
| Research direction | A and B selected by Kirk and run concurrently as a [dual-candidate program](docs/EMRF_DUAL_CANDIDATE_PROGRAM.md); neither is paused or confirmed |
| Candidate A | Kirk authorized testing all three C_m options, choosing the full-density route for option 3; not selection of one final theory |
| Candidate A option 1 | 81 fluid/observer/normalization checks plus vacuum checks pass; conditional GR consistency, not independent empirical confirmation |
| Candidate A SPARC test | Frozen option-2 test remains **rejected**: Delta_Q_cons = 98,216 (T1) and 100,067 (T2) against 388.2 in 153 galaxies. All 6,621 result fields reproduced within frozen tolerances. Original assistant-proposed provenance preserved; testing is now author-authorized. Not blind; option 2 only |
| Candidate A option 3 | The [reconstruction specification](docs/EMRF_CANDIDATE_A_OPTION3_RECONSTRUCTION_SPEC_2026-11-04.md) and [protocol](knowledgebase/candidate_a_option3_reconstruction_protocol.json) remain frozen (SHA-256 `CD9687DD…16270518`; non-blind/post-data). Frozen-v1 V3 still fails at **2.27% versus 0.5%**. Under Kirk-approved [amendment 1](knowledgebase/candidate_a_option3_reconstruction_protocol_v1_amendment_1_segmented_quadrature.json), the full model-only run passes V3 (`2.79e-4`) and V3b (`2.08e-15`); V4 is reported for 20 cases. The [independent spherical-projection recheck](results/candidate_a_option3_projection_recheck_2026-11-05_r2.json) passes all 20 cases at max relative error `6.18e-4`, with no integration warnings. V1 nevertheless remains incomplete: 11 of 20 outer-tail sources have non-decaying tails and no finite source mass. V5 is incomplete: 10/12 variants reported; outer-tail and spherical-bulge source failures remain. **Fit blocked; no observational verdict**; see the [sensitivity artifact](results/candidate_a_option3_sensitivity_validation_2026-11-04.json) |
| GPU resource | GTX 1050 Ti, 4 GiB dedicated VRAM, float64 CuPy/CUDA-12 path verified; optional `gpu` extra and [runbook](docs/site/development/gpu-compute.md). Latest amended V3 CPU path took 1066.14 s; GPU V3b took 881.96 s including first use/transfers. Validation timings, not fit-time estimates; peak memory was not measured. User-reported shared memory is not dedicated VRAM |
| Candidate B first test | Restricted quadratic bulk-scalar Higgs portal with exact mass matching and lower-bound widths; preregistered ATLAS joint-contour check gives conditional compatibility and mu4 bounds |
| Candidate B extended tests | Second frozen preregistration. The ATLAS global-mu likelihood gives kappa_lo = 0.97059, compatible with limit. The width-matched CMS-HIG-24-002 comparison is the stronger mu4 bound at 3 of 12 grid points. Both are bounds, not support for B |
| Candidate B data gate | ATLAS, CMS-HIG-24-002 and HXSWG inputs SHA-256 pinned; the 36-bin STXS vector and 36 × 36 correlation matrix are identified in the pinned HEPData archive. Gaussian validity for B's universal-rescaling direction is not established, but the official global-`mu` profile likelihood along that direction (same dataset) is already used by the extended test, so the restricted-model STXS line is closed as non-independent without computation. Figure 7 central values were inadvertently exposed before a new protocol; no fit was computed, and any later STXS analysis is non-blind, not prospectively preregistered. Interference, loop widths and a direct-resonance likelihood remain open |
| Exact C definition | Observer Einstein-curvature projection authorized for investigation under all three options; no unique final law selected |
| Matter/thermodynamics theorem | Not established; conditional GR identities are not origin-of-matter proofs |
| Real-data analyses | SPARC four-law profiling/influence checks; DESI and full-covariance Pantheon+ baselines executed |
| Ten regimes / three horizons | Evidence matrix completed; missing predictions/data likelihoods remain not yet testable |
| Collision module | Static synthetic illustration, reports NOT TESTED; no moving-well/entropy evolution |
| Recovered history | 47 copy/reference/extract records hash-verified; qualified graph and original meanings preserved |
| Software tests | **633 passed, 1 skipped, 1 deselected** in the non-golden suite, November 3, 2026; Python 3.12.10 with Hypothesis 6.169.0 (outside the `<6.169` development constraint). Software checks, not physical confirmation |
| Engineering checks | Focused correctness lint, CI-selected Ruff rules, strict MkDocs build, generated-reference check, JavaFX tests, release metadata, knowledge graph, CLI doctor, dependency consistency and performance checks passed. The full default Ruff profile still reports pre-existing repository-wide style/import debt; see the [audit](docs/site/development/project-audit-2026-11-03.md) |
| Paper | [Six-page SPARC PDF](paper/sparc_horizon_test.pdf), compiled research draft; no submission |
| Publication | Current `main` documentation; no new tag or Zenodo deposit implied |

## Read current evidence

- [Dual-candidate program (A and B)](docs/EMRF_DUAL_CANDIDATE_PROGRAM.md)
- [Candidate A comparison](docs/EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md)
- [Candidate A option-2 SPARC test](docs/EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md#11-preregistered-sparc-test-of-option-2)
- [Candidate A all-option gates](docs/EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md#12-all-three-options-authorized-full-density-gates)
- [Selected Candidate B test contract](docs/engineering/CANDIDATE_B_MODEL_CONTRACT_DRAFT_2026-10-13.md#16-selected-research-program-and-first-test)
- [Candidate B extended tests](docs/engineering/CANDIDATE_B_MODEL_CONTRACT_DRAFT_2026-10-13.md#17-extended-tests-higgs-rate-likelihood-and-cms-direct-resonance-comparison)
- [Candidate A option-3 source audit](docs/EMRF_CANDIDATE_A_OPTION3_SOURCE_AUDIT_2026-11-04.md)
- [Candidate B STXS feasibility draft](docs/engineering/CANDIDATE_B_STXS_FEASIBILITY_DRAFT_2026-11-04.md)
- [Candidate A option-3 reconstruction specification](docs/EMRF_CANDIDATE_A_OPTION3_RECONSTRUCTION_SPEC_2026-11-04.md) and [frozen protocol](knowledgebase/candidate_a_option3_reconstruction_protocol.json)
- [Top-down audit](docs/EMRF_TOP_DOWN_AUDIT_2026-10-08.md)
- [Fresh SPARC results](docs/SPARC_FRESH_RESULTS.md)
- [Pantheon+ output](results/real_data_followup/pantheon_baseline.json)
- [Regime assessment](docs/REAL_DATA_REGIME_AUDIT.md)
- [Reproducibility](docs/REAL_DATA_REPRODUCIBILITY.md)
- [Engineering and documentation audit](docs/site/development/project-audit-2026-11-03.md)
- [GPU resource, reproducibility and validation limits](docs/site/development/gpu-compute.md)

## Known limits

The SPARC inference is penalized profiling, not Bayesian marginalization.
Profile widths are not calibrated discovery significances. Removing UGC 06787
strongly changes the deep-bulge subset result. Legacy classification APIs,
templates and figures may still overstate their scientific interpretation;
use the current reports and [model card](MODEL_CARD.md), not old verdict strings.

The current test run does not claim strict whole-repository lint/type coverage,
independent peer review, or completion of every scientific test. No private IDE
archive or raw observational cache is required to read the public reports.

## November 5 publication verification

The focused reconstruction, GPU, knowledge and report tests passed **53 tests**.
Strict MkDocs, focused Ruff and projection-validator mypy checks passed.
The [projection recheck](results/candidate_a_option3_projection_recheck_2026-11-05_r2.json)
has SHA-256 `951448be4cb1dd819f0c4f072f87f997433e30cbb577fe4364ad59c3ee6f2d41`;
the frozen source protocol and amendment hashes remain unchanged. These are
software and model-only checks, not physical confirmation or fit authorization.
