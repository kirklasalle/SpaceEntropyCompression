# EMRF current status

Research selection updated October 16, 2026: A and B now run concurrently. This replaces the old all-green dashboard; historical
versions remain in Git history and the [correction archive](docs/archive/antigravity_recovery/README.md).

| Area | Current state |
|---|---|
| Research direction | A and B selected by Kirk and run concurrently as a [dual-candidate program](docs/EMRF_DUAL_CANDIDATE_PROGRAM.md); neither is paused or confirmed |
| Candidate A | Exact-background definition checks only; C and M not yet author-selected; no observational test possible yet |
| Candidate B first test | Restricted quadratic bulk-scalar Higgs portal with exact mass matching and lower-bound widths; preregistered ATLAS joint-contour check gives conditional compatibility and mu4 bounds |
| Candidate B extended tests | Second frozen preregistration. The ATLAS global-mu likelihood gives kappa_lo = 0.97059, compatible with limit. The width-matched CMS-HIG-24-002 comparison is the stronger mu4 bound at 3 of 12 grid points. Both are bounds, not support for B |
| Candidate B data gate | ATLAS, CMS-HIG-24-002 and HXSWG inputs SHA-256 pinned; STXS likelihood, interference, loop widths and a direct-resonance likelihood not done |
| Exact C definition | Recommended observer Einstein-curvature projection, not yet author-selected |
| Matter/thermodynamics theorem | Not established; conditional GR identities are not origin-of-matter proofs |
| Real-data analyses | SPARC four-law profiling/influence checks; DESI and full-covariance Pantheon+ baselines executed |
| Ten regimes / three horizons | Evidence matrix completed; missing predictions/data likelihoods remain not yet testable |
| Collision module | Static synthetic illustration, reports NOT TESTED; no moving-well/entropy evolution |
| Recovered history | 47 copy/reference/extract records hash-verified; qualified graph and original meanings preserved |
| Software tests | **580 non-golden tests passed locally**, October 16, 2026; 3 property-based tests failed from a `hypothesis` library internal error. Software correctness, not physical confirmation |
| Paper | [Six-page SPARC PDF](paper/sparc_horizon_test.pdf), compiled research draft; no submission |
| Publication | Current `main` documentation; no new tag or Zenodo deposit implied |

## Read current evidence

- [Dual-candidate program (A and B)](docs/EMRF_DUAL_CANDIDATE_PROGRAM.md)
- [Candidate A comparison](docs/EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md)
- [Selected Candidate B test contract](docs/engineering/CANDIDATE_B_MODEL_CONTRACT_DRAFT_2026-10-13.md#16-selected-research-program-and-first-test)
- [Candidate B extended tests](docs/engineering/CANDIDATE_B_MODEL_CONTRACT_DRAFT_2026-10-13.md#17-extended-tests-higgs-rate-likelihood-and-cms-direct-resonance-comparison)
- [Top-down audit](docs/EMRF_TOP_DOWN_AUDIT_2026-10-08.md)
- [Fresh SPARC results](docs/SPARC_FRESH_RESULTS.md)
- [Pantheon+ output](results/real_data_followup/pantheon_baseline.json)
- [Regime assessment](docs/REAL_DATA_REGIME_AUDIT.md)
- [Reproducibility](docs/REAL_DATA_REPRODUCIBILITY.md)

## Known limits

The SPARC inference is penalized profiling, not Bayesian marginalization.
Profile widths are not calibrated discovery significances. Removing UGC 06787
strongly changes the deep-bulge subset result. Legacy classification APIs,
templates and figures may still overstate their scientific interpretation;
use the current reports and [model card](MODEL_CARD.md), not old verdict strings.

The current test run does not claim strict whole-repository lint/type coverage,
independent peer review, or completion of every scientific test. No private IDE
archive or raw observational cache is required to read the public reports.
