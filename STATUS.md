# EMRF current status

Research selection updated October 16, 2026. This replaces the old all-green dashboard; historical
versions remain in Git history and the [correction archive](docs/archive/antigravity_recovery/README.md).

| Area | Current state |
|---|---|
| Research direction | A and B selected by Kirk; one active at a time. B active, A retained but paused |
| Candidate B first test | Restricted quadratic bulk-scalar Higgs portal with exact mass matching and lower-bound widths; preregistered ATLAS joint-contour check gives conditional compatibility and mu4 bounds, no likelihood evaluated |
| Candidate B data gate | ATLAS Figure 4 contour and CMS-HIG-24-002 archive retrieved and SHA-256 pinned; correlated likelihood and width-matched resonance test not yet done |
| Exact C definition | Recommended observer Einstein-curvature projection, not yet author-selected |
| Matter/thermodynamics theorem | Not established; conditional GR identities are not origin-of-matter proofs |
| Real-data analyses | SPARC four-law profiling/influence checks; DESI and full-covariance Pantheon+ baselines executed |
| Ten regimes / three horizons | Evidence matrix completed; missing predictions/data likelihoods remain not yet testable |
| Collision module | Static synthetic illustration, reports NOT TESTED; no moving-well/entropy evolution |
| Recovered history | 47 copy/reference/extract records hash-verified; qualified graph and original meanings preserved |
| Software tests | **244 passed locally**, October 8, 2026; software correctness, not physical confirmation |
| Paper | [Six-page SPARC PDF](paper/sparc_horizon_test.pdf), compiled research draft; no submission |
| Publication | Current `main` documentation; no new tag or Zenodo deposit implied |

## Read current evidence

- [Candidate A comparison](docs/EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md)
- [Selected Candidate B test contract](docs/engineering/CANDIDATE_B_MODEL_CONTRACT_DRAFT_2026-10-13.md#16-selected-research-program-and-first-test)
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
