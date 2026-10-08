# Referee Action Roadmap and Task Register

> **Integrity notice (2026-10-07).** This document predates the independent audit in [`docs/SHOW_YOUR_WORK.md`](SHOW_YOUR_WORK.md). Empirical results quoted here (for example S-star ΔBIC = +70.743 or +141.3, SPARC ΔBIC = −52,490.1, JWST ΔBIC = −100.08, wide-binary ΔBIC = −60.26, CMB χ²ᵥ = 0.924, "28,700+ observational constraints") were computed from synthetic data files (now quarantined in [`data/synthetic/`](../data/synthetic/README.md)) or from code whose answer was built in, so they **must not be cited**. "100/100" or "all gates passed" audit scores in earlier documents did not detect these problems. Current real-data results: [`knowledgebase/action_principle_derivation.md`](../knowledgebase/action_principle_derivation.md) §4.3.


**Date:** 2026-10-07  
**Basis:** Independent due-diligence audit at commit `3241e0aff5286a861902abb79be164dc84eb8a5c`  
**Audit baseline:** CQSI 49/100; Level 2 - Numerically Implemented  
**Related guidance:** [Referee recommendations](./REFEREE_RECOMMENDATIONS_2026-10-07.md)

## Purpose and operating rule

This roadmap turns the audit recommendations into sequenced, verifiable work. It is an action plan, not a claim that the proposed theory is correct or that any empirical result has been independently replicated.

The project has a useful software base: 178 tests passed in the audited checkout, and the local CI harness completed successfully, including the JavaFX build. The next effort should address scientific claims and evidence, not inflate test counts or add more regimes for their own sake.

**Operating rule:** do not promote a claim beyond its evidence. If a covariant physical theory cannot be derived, retain and label the work as a phenomenological model rather than filling gaps with assertions.

## Sequencing and gates

| Gate | Work that must be complete | Decision |
|---|---|---|
| **G0 - Stable starting point** | T01-T03: claims corrected, reproducible software baseline, ontology decision recorded | Proceed only with a consistent description and a known-good reproducible checkout. |
| **G1 - Theory defined** | T04-T05: equations, units, GR limit, and perturbative stability assessed | If a defensible derivation is unavailable, limit claims to the phenomenological model. |
| **G2 - One test specified** | T06: a preregistered, falsifiable empirical study and complete data plan | Do not tune the model or change the target population after seeing held-out outcomes. |
| **G3 - Empirical result challenged** | T07-T09: reproducible fit, independent challenge/holdout, proportional safety assessment | Report failures, null results, sensitivity, and limitations alongside favorable outcomes. |
| **G4 - Release and expansion** | T10-T11: release provenance sealed and next regime selected using the same standard | Expand only after the first regime is reproducible and survives its stated falsification tests. |

No calendar durations are assigned: effort and staffing have not been estimated. Complete tasks in dependency order; independent tasks within a gate may proceed in parallel.

## Task register

### T01 - Correcting public scientific claims

**Priority:** P0  
**Prerequisites:** None  
**Work:** Review the README, status pages, model card, manuscript, figures, and release notes. Reconcile test counts. Label results as theoretical, simulated, exploratory, or observationally tested. Replace unsupported descriptions such as "exact derivation," "joint Bayesian model selection," or "full-catalog validation" unless the referenced evidence actually supports them. Maintain a claim-to-evidence ledger.

**Done when:** All public-facing claims in scope identify their evidence and limitations; counts and dataset descriptions agree; unsupported claims have been corrected or explicitly marked as future work.

### T02 - Locking the reproducible software baseline

**Priority:** P0  
**Prerequisites:** None  
**Work:** Add a dependency lock and verify a clean-environment install. Make pull-request CI run the full Python test suite, lint/style checks, and required build checks. Audit data/file paths from a clean checkout on supported platforms. Add a visualizer syntax/console check where practical. Record the supported Python/Java versions and handle the Java compiler warning.

**Done when:** A clean checkout can install and run the full required checks without relying on a developer's existing virtual environment; CI and the documented local command cover the same required checks.

### T03 - Resolving the entropy ontology

**Priority:** P0  
**Prerequisites:** None  
**Work:** Decide whether entropy is a thermodynamic field/state variable or an additional geometric coordinate. Document the meaning, units, transformation behavior, coupling, and consequences for the model API. Align the implementation and documentation; do not conflate a coordinate with thermodynamic entropy.

**Done when:** One consistent ontology is stated and implemented, and tests/documentation no longer assert conflicting interpretations.

### T04 - Deriving the physical model and GR limit

**Priority:** P1  
**Prerequisites:** T03  
**Work:** Define degrees of freedom, metric/signature, units, parameters, and assumptions. Derive the action and equations of motion, stress-energy, conservation properties, and the conditions under which the model recovers GR. Evaluate relevant energy conditions. If no covariant derivation is supportable, document the framework as phenomenological and narrow the theoretical claims.

**Done when:** A specialist can reproduce the derivation from the documented definitions, check dimensions, identify approximations, and verify the stated GR limit—or the project explicitly adopts the narrower phenomenological scope.

### T05 - Auditing stability and causal propagation

**Priority:** P1  
**Prerequisites:** T04  
**Work:** Expand the derived theory about stated backgrounds. Compute the kinetic matrix and perturbation equations; check for ghosts, gradient instabilities, hyperbolicity, and propagation speeds. State the regime of validity and avoid extrapolating a toy parameter scan to the full nonlinear theory.

**Done when:** Results follow from the derived model, include reproducible calculations and assumptions, and are independently reviewable. If the analysis is unavailable, stability claims are explicitly marked unestablished.

### T06 - Preregistering one empirical study

**Priority:** P1  
**Prerequisites:** T02, T03, T04  
**Work:** Select one regime with recoverable observations and uncertainties. Before fitting, record the target population, inclusion/exclusion rules, model and baseline, shared/free parameters, priors or estimator, likelihood, covariance/nuisance treatment, holdout, and quantitative rejection criteria.

**Done when:** The plan is timestamped or versioned before the confirmatory fit, includes a data-provenance manifest, and cannot silently change after holdout results are observed.

### T07 - Building one end-to-end empirical pipeline

**Priority:** P1  
**Prerequisites:** T02, T04, T06  
**Work:** Implement the preregistered data ingestion and analysis. Preserve source/version/checksum and transformations. Fit the proposed model and established comparator to the same observations with consistent uncertainty treatment. Estimate parameters and uncertainty rather than relying on a fixed candidate value where inference is required. Generate every reported metric and figure from a documented command.

**Done when:** A clean environment reproduces the result from documented inputs; shared parameters are genuinely fit jointly when described as joint; residuals, uncertainty, comparator results, and sensitivity analyses are reported.

### T08 - Running independent falsification and holdout tests

**Priority:** P1  
**Prerequisites:** T07  
**Work:** Test blinded or held-out observations and independently designed challenge cases. Include realistic correlated noise, systematics, missing data, plausible near-degenerate alternatives, valid positive controls, and tests for false rejection as well as false acceptance. Publish per-case outcomes and failures.

**Done when:** The preregistered acceptance/rejection criteria are applied without post-hoc changes, holdout outcomes are disclosed, and the challenge generator is not simply validating its own assumptions.

### T09 - Completing a proportional safety and stewardship review

**Priority:** P2  
**Prerequisites:** T04, T05  
**Work:** Document the current software's intended use, plausible dual-use concerns, physical effects actually implied by the derived theory, computational footprint if measured, and limits of the safety analysis. Distinguish "not applicable," "not identified," and "demonstrated safe." Do not propose physical experiments on the basis of unverified energetic or metric claims.

**Done when:** Safety statements are tied to explicit evidence and unresolved questions; ethical commitments are not represented as proof of physical safety.

### T10 - Sealing release provenance

**Priority:** P2  
**Prerequisites:** T01, T02, T07, T08, T09  
**Work:** Build the release from a clean checkout. Verify licenses, citation metadata, bibliography identifiers/DOIs, data provenance, package contents, and generated figures. Publish checksums for the exact release artifacts and link the archived source, data, and environment.

**Done when:** A third party can identify the audited source revision, retrieve permitted inputs, verify artifact checksums, and reproduce the released results.

### T11 - Expanding to additional regimes

**Priority:** P3  
**Prerequisites:** T08  
**Work:** Select the next regime only after reviewing the first regime's outcome. Reuse the provenance, preregistration, covariance, baseline, holdout, and reporting standards. Maintain a public record of successes, failures, exclusions, and deviations.

**Done when:** Every added regime has a documented, reproducible pipeline and an independently assessable result; broad cross-regime claims are limited to the regimes that meet that standard.

## Immediate starting set

Begin with **T01, T02, and T03**. They are independent and reduce avoidable uncertainty:

- T01 prevents further overstatement while the science is being developed.
- T02 preserves the current passing software baseline and makes future results reproducible.
- T03 resolves the core mismatch between the documented entropy interpretation and the implemented coordinate treatment.

Do not treat completion of these tasks as scientific validation. The decisive evidence gates are T04-T08: a coherent model, a prespecified empirical test, and a result that survives independent attempts to falsify it.
