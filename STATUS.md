# EMRF current status

Research selection updated October 16, 2026; engineering audit updated November 3, 2026. A and B run concurrently. This replaces the old all-green dashboard; historical
versions remain in Git history and the [correction archive](docs/archive/antigravity_recovery/README.md).

| Area | Current state |
|---|---|
| Research direction | A and B selected by Kirk and run concurrently as a [dual-candidate program](docs/EMRF_DUAL_CANDIDATE_PROGRAM.md); neither is paused or confirmed |
| Candidate A | Kirk authorized testing all three C_m options, choosing the full-density route for option 3; not selection of one final theory |
| Candidate A option 1 | 81 fluid/observer/normalization checks plus vacuum checks pass; conditional GR consistency, not independent empirical confirmation |
| Candidate A SPARC test | Frozen option-2 test remains **rejected**: Delta_Q_cons = 98,216 (T1) and 100,067 (T2) against 388.2 in 153 galaxies. All 6,621 result fields reproduced within frozen tolerances. Original assistant-proposed provenance preserved; testing is now author-authorized. Not blind; option 2 only |
| Candidate A option 3 | Full-density mapping and finite-thickness axisymmetric solver benchmarked (relative error 1.66e-6). Public Leroy profiles acquired and pinned; 11 SPARC overlaps, none complete across all tabulated components. Literature-constrained axisymmetric parametric-profile family approved; the [reconstruction specification](docs/EMRF_CANDIDATE_A_OPTION3_RECONSTRUCTION_SPEC_2026-11-04.md) fixes literature-grounded vertical, radial, conversion-factor and censored/missing-data rules (corrected flags: 13 censored HI values, 0 stellar). The approved test is frozen as [`candidate_a_option3_reconstruction_protocol.json`](knowledgebase/candidate_a_option3_reconstruction_protocol.json) (SHA-256 `CD9687DD…16270518`; non-blind, post-data-exposure). Reconstruction module and validation gates V1–V5 (no observed velocities) are next. **No observational fit computed**; not rejected or supported |
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

## Known limits

The SPARC inference is penalized profiling, not Bayesian marginalization.
Profile widths are not calibrated discovery significances. Removing UGC 06787
strongly changes the deep-bulge subset result. Legacy classification APIs,
templates and figures may still overstate their scientific interpretation;
use the current reports and [model card](MODEL_CARD.md), not old verdict strings.

The current test run does not claim strict whole-repository lint/type coverage,
independent peer review, or completion of every scientific test. No private IDE
archive or raw observational cache is required to read the public reports.
