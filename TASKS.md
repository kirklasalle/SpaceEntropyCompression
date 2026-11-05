# EMRF active research tasks

Research selection updated October 16, 2026; engineering audit updated November 3, 2026. A and B run concurrently. Earlier task lists marked several assumptions or
synthetic exercises as completed physical validation; those statuses are not
carried forward.

| Task | State | Acceptance condition |
|---|---|---|
| Select research candidates and work mode | Decided: A and B selected and run concurrently | Separate records and preregistrations for each; see the [dual-candidate program](docs/EMRF_DUAL_CANDIDATE_PROGRAM.md) |
| Test restricted Candidate B Higgs portal | First check done: compatible with limit | Exact physical Higgs mass, specified potential and widths; frozen preregistration; no hidden fit assumptions |
| Extend B data tests | Done: rate likelihood compatible with limit; CMS stronger at 3 of 12 points | Width-matched CMS-HIG-24-002 comparison and ATLAS global-mu likelihood under a frozen second preregistration |
| Deepen B constraints | Restricted-model STXS closed as redundant with the existing global-mu likelihood | Interference and loop widths, or a published resonance statistical model, each under a new frozen protocol; a future non-universal STXS model needs a new contract |
| Investigate all Candidate A options | Authorized by Kirk; full-density route selected for option 3 | Keep authorization to investigate distinct from selection or validation of a final theory |
| Check Candidate A option 1 | Done: 81 conditional GR checks plus vacuum checks | No claim of independent support over GR or full dynamical equivalence |
| Reproduce Candidate A option 2 | Done: SPARC rejection reproduced across 6,621 result fields (not blind) | Preserve the old frozen protocol and result, including historical attribution |
| Develop Candidate A option 3 | Amendment-1 model-only run passes V3/V3b and reports V4; independent spherical-projection recheck passes; V1 incomplete (11 non-decaying outer tails), V5 incomplete (outer-tail and spherical-bulge source failures) | Preserve frozen-v1 result; resolve invalid variants and revalidate under an explicitly approved source protocol, without velocities |
| Fit Candidate A option 3 | Protocol frozen at `8437889`; **blocked** by numerical validation | Do not fit until all required gates pass; preserve non-blind/post-data disclosure and never relax frozen gates to obtain a fit |
| Qualify optional GPU execution | GTX 1050 Ti float64 V3b agreement passes at < 2.08e-15; model-only V1/V4/V5 run completed with documented incompleteness | Follow the [GPU runbook](docs/site/development/gpu-compute.md); 1 GiB process pool cap, explicit failures and provenance; do not infer fit throughput |
| Assess equivalence and matter mapping | Conditional identities/counterexamples documented | No inference of complete equivalence from fits or one scalar identity |
| Recover original theory intentions | Completed with stated coverage limits | Source-hashed archive, qualified graph and attribution |
| Complete engineering/documentation audit | Completed November 3, 2026 | 633 non-golden tests pass in the CI-constrained environment; current evidence, link corrections, MCP pack status and remaining lint debt are recorded in the [audit](docs/site/development/project-audit-2026-11-03.md) |
| Repair project-local IDS catalog | Completed November 3, 2026 | The launched IDS entrypoint resolves this repository through `MCP_WORKSPACE_ROOT` and returns real `docs/` hits; its knowledge graph is not yet populated for Candidate A. Do not substitute a non-local MCP |
| Integrate the project-local MCP server pack | Integrated, not certified | Nine local servers; 9/9 smoke targets pass, 21 of 63 listed tools are individually exercised, and the `.mcp` CI matrix passes on Ubuntu/Windows with Python 3.11/3.12 (run 41829273692). See the [audit](docs/site/development/project-audit-2026-11-03.md#project-local-mcp-server-pack) |
| Run real SPARC comparison and influence checks | Completed within documented scope | Converged profiles, real inputs and visible systematic limits |
| Fit real Pantheon+/DESI baselines | Completed within documented scope | Covariance-aware likelihood; no attribution to new EMRF cosmology |
| Complete every empirical regime | Blocked, not passed | A defined prediction and usable data likelihood for each case |
| Derive entropy/matter origin | Open | Independent mathematical derivation and physical assumptions, not normalization identities |
| Correct all legacy scientific verdict surfaces | Partially complete | Per-module review; illustration/assumption must not imply observation |
| Submit manuscript or archive new release | Not performed | Independent review, correct version/metadata and explicit publication decision |

References: [functional comparison](docs/EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md),
[top-down audit](docs/EMRF_TOP_DOWN_AUDIT_2026-10-08.md),
[reproducibility guide](docs/REAL_DATA_REPRODUCIBILITY.md), and the
[engineering audit](docs/site/development/project-audit-2026-11-03.md).
