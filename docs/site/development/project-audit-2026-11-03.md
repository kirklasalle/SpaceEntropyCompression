# Project engineering and documentation audit

**Audit date:** 2026-11-03
**Project:** Emergent Matter Research Framework (EMRF)
**Scope:** Tracked application code, tests, tools, project configuration and live documentation. Generated outputs, downloaded datasets and caches were not in the change scope. The first pass left `.mcp` implementation files out of scope; a second pass audited and changed the project-local MCP server pack (see [Project-local MCP server pack](#project-local-mcp-server-pack)).

## Executive summary

The project has substantial reproducibility, regression, data-provenance and
workflow controls, but it does not establish a new physical theory. Candidate
A and Candidate B remain separate, incomplete research programs. Their
software, mathematical and observational checks are evidence of different
kinds and must not be conflated.

The audit updated agent instructions, MCP configuration, current status
summaries and several stale or machine-specific documentation references. It
also hardened equal-length parallel-array handling in non-frozen code. Frozen
source files and historical evidence records remain byte-identical.

The first pass found that the sole configured MCP server (local IDS) resolved
its root to `.mcp` and returned an empty catalog. A second pass registered
`.mcp` as a submodule, repaired the root resolution and configured nine
project-local servers. The IDS server now returns real `docs/` hits, although
its knowledge graph is not yet populated for Candidate A. Smoke testing
individually exercised 21 of the 63 listed tools, so the pack is integrated
but not certified. No external or other-project MCP server was used. See
[Project-local MCP server pack](#project-local-mcp-server-pack).

**Theory-of-everything readiness: no.** No matter-origin theorem, entropy
theorem, unified theory or physical confirmation has been established.

## Scope and method

The review covered the current Python package and tools, tests, release and CI
configuration, agent guidance, user/developer documentation, candidate
contracts and research-status documents. Generated products and downloaded or
cached research data were excluded from source edits. Historical and frozen
protocol material was preserved except for corrections needed to keep current
documentation factual and navigable.

In the first pass the project-local IDS server was invoked read-only for
status, statistics and search. It reported no indexed documents or tags and
returned no Candidate A catalog result; that behavior was later traced to its
root resolution and repaired (see below). The second pass drove each launched
server over the MCP stdio protocol with a bounded probe and unit tests. No
non-local MCP was invoked in either pass.

## Engineering findings

### Agent instructions and MCP boundary

- The workspace `.vscode/mcp.json` declares nine project-local servers, all
  launched with `python` from `PATH` and forward-slash workspace-relative
  paths; `MCP_WORKSPACE_ROOT` is set to the repository. `.gitignore` allows
  only this profile from `.vscode/` to be tracked. The Linux profile paths are
  portable, but its full nine-server launch has not been exercised in the
  devcontainer.
- `.github/copilot-instructions.md` requires workspace agents to consult
  `AGENTIC_PRIME_DIRECTIVE.md`, `AGENTIC_SACRED_COVENANT.md`, and
  `Permanent_Active_Directives.txt`. It also limits MCP use to workspace
  configuration and preserves higher-level safety and platform requirements.
- **Resolved:** the legacy local IDS entry point (`.mcp/ids/server.py`)
  searches for the nearest `AGENTIC_SACRED_COVENANT.md`, and the copy under
  `.mcp` made it select `.mcp` as the root, so it indexed `.mcp/docs` and had
  no usable project catalog. The profile now launches
  `.mcp/ids/server_ai_enhanced.py`, which honors `MCP_WORKSPACE_ROOT`, and its
  search returns hits from the repository's `docs/`. The legacy entry point
  keeps the ancestor scan but is not launched. If a local server is
  unavailable or has no usable catalog, agents must still report that rather
  than switch MCPs.

### Code and provenance

- Added explicit strict-length checks to parallel-array operations in
  non-frozen code; marked the intentionally offset adjacent-window scan
  non-strict.
- The archived horizon-entropy source and the Candidate A marginalized-a0
  source are hash-pinned by recovery or result-provenance tests. Initial
  cleanup edits changed those hashes, so those two files were restored and
  verified byte-identical to `HEAD`. Their historical behavior and evidence
  were not changed to satisfy lint.
- CI's selected correctness lint passes. The full default Ruff profile still
  reports **747 findings**, chiefly E501 (323), W293 (98), F401 (73), UP006
  (71), I001 (57) and UP035 (48). This is existing broad style/import debt;
  the audit does not claim whole-repository lint or type-check cleanliness.

### Dependency reproducibility

The first-pass Python 3.12.10 run used Hypothesis 6.169.0, while
`requirements-dev.txt` constrains Hypothesis below 6.169, so that environment
was not an exact reproduction of the constrained CI environment. The second
pass rebuilt an isolated environment from `requirements-dev.txt` with
`constraints-ci.txt` (Python 3.12.10, Hypothesis 6.168.5, NumPy 2.2.6, SciPy
1.15.3, pytest 9.0.3) and obtained the same non-golden result, so the
mismatch did not change the outcome. Global packages were not altered.

## Documentation changes

- Updated `README.md`, `STATUS.md`, `ROADMAP.md`, `MODEL_CARD.md` and
  `CHANGELOG.md` with current software results and the distinction between
  software validation and physical evidence.
- Added this audit to the MkDocs development navigation and linked it from the
  current project entry points.
- Added workspace agent instructions and documented them in
  `CONTRIBUTING.md`.
- Replaced machine-specific `file:///` knowledgebase links with repository
  relative links, normalized absolute file URLs in seven maintained/top-level
  historical documents, and marked the knowledgebase's old directory tree and
  claims as historical. The six source snapshots in the recovery archive remain
  byte-identical.
- Removed the implication that the absent
  `data/jwst/jwst_kinematics_sample.csv` can be reproduced from this checkout.
  The legacy pipeline now states that the file is absent and that historic
  row-level claims require re-acquisition and hash-pinning.
- Documented the project-local MCP server pack: the `.mcp` integration guide
  (`docs/SPACE_ENTROPY_COMPRESSION.md`) and `[Unreleased]` changelog entries in
  the submodule, plus updates to `CONTRIBUTING.md`, `TASKS.md` and the project
  `CHANGELOG.md`. Historical capability and verification claims in the `.mcp`
  README, IDS and VRGC guides are marked unverified rather than deleted.
- Left `AGENTIC_SACRED_COVENANT.md` unedited. It differs from `HEAD` only by
  the owner's own title and subtitle edit, and an earlier audit edit to it was
  reverted. The covenant still links a `GOVERNANCE.md` that does not exist and
  states that CI checks it; no test, script, workflow or package module checks
  the covenant or that file. Suggested replacement wording for the owner to
  adopt or reject: "This covenant is a project policy document, not a runtime
  enforcement mechanism; the repository has no complete policy-to-code map or
  CI check proving these claims. The narrower workflow governance tests cover
  GitHub workflow controls, not covenant enforcement."

## Project-local MCP server pack

The second pass registered `.mcp` (repository `kirklasalle/.mcp`) as a git
submodule in `.gitmodules`, audited the nine servers that the workspace profile
launches, and used no ImpressionCore or other non-local MCP server.

| Server | Function | Tools listed | Individually exercised |
|--------|----------|-------------:|-----------------------:|
| Goliath | Read-only swarm and hardware status | 1 | 1 |
| IDS | Documentation and code search, knowledge graph, lineage | 5 | 5 |
| EDS | Public-source scrapers, license and quality checks, dataset curation | 9 | 2 |
| IPA | Multi-engine research search and history | 6 | 2 |
| VRGC | Hardware and covenant checks, web access, approval-gated downloads | 10 | 4 |
| DPA | Intent, entity and accessibility analysis, chronology, gated IDS bridge | 17 | 4 |
| web-search | Public web search and page fetch | 8 | 1 |
| LoC | Library of Congress catalog search | 4 | 1 |
| science-data | NASA Exoplanet Archive and INSPIRE-HEP queries | 3 | 1 |
| **Total** | | **63** | **21** |

"Individually exercised" means the bounded probe made a positive call that
returned a non-error result. Calls that must be denied are recorded separately
and are not counted. The other 42 tools are listed but were not exercised one by
one, so the pack is integrated, not certified. For `science_data`, the probe
exercised only the source registry; the two query tools were checked in an
earlier manual run (three records with provenance and SHA-256).

**Changes made**

- Added the `science_data` server, a shared workspace-root resolver
  (`MCP_WORKSPACE_ROOT`, fail-closed on an invalid root) and shared bounded
  outbound-request checks.
- Reduced Goliath to one read-only tool and removed simulated GPU telemetry.
- Removed IDS `neural_forge_integration` (hard-coded mock figures), stopped
  listing 18 unimplemented VRGC tools, and made `vrgc_verify_covenant` read-only.
- Fixed startup without PyTorch (DPA) or GPUtil (VRGC), LoC upstream failures
  now surfacing as tool errors, the DPA accessibility route, and IDS
  `single_file` scope and `ids_trace_lineage` for unknown entities.
- Added a protocol-only probe, per-tool coverage reporting, 43 unit tests and
  a CI workflow in the submodule that runs the unit tests and the
  protocol-only probe.

**Safety posture**

- One shared mutation gate (`MCP_ALLOW_MUTATIONS=1` plus a per-call
  `approved: true`) guards the listed VRGC tools `vrgc_download_file` and
  `vrgc_ftp_access`, non-read `vrgc_api_request` calls, and the four DPA
  IDS-control tools (`ids_update`, `ids_tag`, `ids_sync`, `ids_generate_docs`).
  Two further VRGC tools that the gate covers are unimplemented and not listed.
  The profile sets the flag to `0` for Goliath, VRGC and DPA. The probe checks
  that the four DPA calls and the VRGC download and FTP calls are denied.
- DPA's IDS bridge is disabled unless `DPA_IDS_API_PATH` is an absolute path to
  an existing script. It previously executed
  `src/core/utils/ids_server_api.py` from the host repository whenever that
  file existed, with no timeout. The child now runs with a 60-second timeout
  and without access to the MCP stdin stream.
- IDS graph caches are versioned JSON, replacing pickles that run code when a
  tampered cache is loaded.
- web-search validates outbound URLs as public HTTPS and does not follow
  redirects; VRGC validates before fetch, download and API requests; LoC checks
  a host allowlist; IPA keeps TLS verification on. EDS validates its generic
  fetch and `robots.txt` paths only, and its site-specific scrapers (MIT OCW,
  Khan Academy, Wikipedia, arXiv) call fixed endpoints directly and were not
  reviewed.

**Defects found by fresh-checkout verification**

- IDS crashed at startup on a clean checkout without `numpy`, because
  `networkx` was imported inside the optional AI-library guard. A leftover
  local cache hid this on the development machine. It is fixed and covered by a
  fresh-start regression test.
- The probe always exited 0, so the CI step could not fail. It now exits
  non-zero unless every server is OK, and it no longer depends on the host
  project's `STATUS.md`.

**Known limitations**

- 42 of 63 tools are not individually exercised. Legacy modules that the
  profile does not launch (for example `ids/server.py` and the DPA `tasks/`
  modules, some of which still import `pickle`) were not reviewed in depth and
  should be removed or reviewed before anything starts launching them.
- The IDS knowledge graph is not populated for Candidate A, so graph queries
  return "not found" rather than lineage.
- Only two science sources are implemented. There is no bounded image or
  spectral workflow and no immutable manifest store, and no rate-limit,
  schema-drift or checksum-failure tests exist for the adapters.
- The submodule's GitHub Actions workflow passed all four Ubuntu/Windows and
  Python 3.11/3.12 jobs on 2026-11-04 (run `41829273692`). The first run exposed
  a Windows UTF-8 decoding failure in the fresh-start test harness; explicit
  UTF-8 decoding fixed it. The two workspace-profile tests skip in a standalone
  checkout, and the project's own CI does not collect `.mcp/tests`. They run
  only on a workstation with the workspace profile.
- API responses, literature records and software checks are not physical
  confirmation of either candidate.

## Validation record

The non-golden suite completed with **633 passed, 1 skipped and 1 deselected**
in both passes: first with Python 3.12.10 and Hypothesis 6.169.0, then in an
environment built from `requirements-dev.txt` and `constraints-ci.txt`
(Hypothesis 6.168.5, NumPy 2.2.6, SciPy 1.15.3, pytest 9.0.3). The skipped and
deselected cases are reported by pytest; neither count is presented as a
physical test.

The following checks passed in the first pass:

- CI-selected Ruff correctness rules and focused changed-code checks.
- Markdown/text link scan: 148 documents and 654 local links. No missing or
  outside-repository relative targets remain; 69 non-portable file URLs are
  confined to six byte-preserved recovery snapshots.
- JavaFX test suite (4 tests).
- Strict MkDocs build and generated-reference check.
- Release metadata validation, `pip check`, CLI doctor and knowledge-graph
  validation (111 nodes, 132 edges).
- Performance baselines.
- Frozen-provenance tests after restoring the two hash-pinned source files.

The second pass re-ran, in the constrained environment, the strict MkDocs
build, the generated-reference check, release metadata validation, `pip check`,
CLI doctor (59 commands, healthy; advisory: no off-site backup destination is
configured) and knowledge-graph validation (111 nodes, 132 edges). For the
`.mcp` submodule, 43 unit tests pass, and the full smoke probe passed 9/9
targets with 21 of 63 tools individually exercised. The submodule's unit suite
and protocol-only probe also pass from a clean checkout in an environment built
only from its `requirements.txt` (two workspace-profile checks skip there).

Not re-run locally in the second pass: the Golden regression jobs, the Python
3.10 matrix, the JavaFX suite and the performance baselines. The merged PR #38
passed those remote checks for its own commit; they have not yet run on the
follow-up audit changes (including the `zip(strict=...)` edits). The `.mcp`
workflow passed all four jobs remotely, but its Ubuntu leg has not been
exercised locally. Parent-repository CI has not yet run on this follow-up
branch.

These are engineering checks, not independent scientific review, full
whole-repository type coverage or experimental confirmation.

## Research status and next tests

### Candidate A

- **Option 1:** conditional GR-consistency checks pass; this is not independent
  empirical confirmation or a matter-origin proof.
- **Option 2:** the preregistered baryons-only SPARC operationalization remains
  rejected. This falsifies that option only.
- **Option 3:** density mapping and the axisymmetric solver pass numerical
  benchmarks, but there is no observational fit or verdict.

The next gate is a justified three-dimensional reconstruction of stellar,
HI, H2 and bulge densities from the available profiles and underlying
observations. Explicitly model missing and censored components, vertical
structure, boundaries, geometry and conversion uncertainties; do not set
missing gas to zero or substitute a spherical profile. State whether the claim
is a weak-field effective-source model or has a covariant completion. Only
then freeze the global/local parameters, nuisance treatment, comparator and
decision rule before fitting.

### Candidate B

The restricted Higgs-portal checks produce upper bounds and conditional
compatibility, not evidence for Candidate B. Prioritize an official correlated
STXS likelihood if available; address interference and loop-induced widths.
Build a direct-resonance likelihood only from an actual published likelihood,
not summary uncertainties or limit curves. Freeze each new analysis before
outcome-relevant data are examined.

### Overall

Neither candidate is confirmed. Software tests, solver benchmarks and
consistency checks cannot establish the theory of everything. A bounded,
pre-registered observational claim and independent domain/statistical review
remain necessary.
