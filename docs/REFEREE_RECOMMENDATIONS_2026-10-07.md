# Referee Recommendations Following the Due-Diligence Audit

**Date:** 2026-10-07  
**Audit basis:** Repository checkout at commit `3241e0aff5286a861902abb79be164dc84eb8a5c`  
**Audit outcome:** CQSI 49/100; Level 2 - Numerically Implemented  
**Purpose:** An actionable improvement plan, not a new scientific result or certification.

## Executive recommendation

Treat the Emergent Matter Research Framework (EMRF) as a **phenomenological research prototype** until its physical ontology, equations, stability, and empirical inference are established independently. The software test suite is a real strength: 178 tests passed, and the local CI harness completed its test and JavaFX build steps. Those results show that the tested software behaves as expected; they do not establish that its assumptions describe nature.

The best route forward is not to add more regimes, figures, or headline claims. First reconcile the model's stated ontology with its implementation, make one end-to-end result reproducible, derive the theory sufficiently to expose its physical assumptions, and then test a narrow, preregistered claim against complete and independently sourced data. Expand to other regimes only after that pipeline survives meaningful attempts to falsify it.

## Priority 0: Correct claims and stabilize the scientific record

Before publishing new claims:

1. **Describe the work accurately.** Use terms such as "phenomenological model," "exploratory fit," or "prototype" where those describe the actual evidence. Do not describe a toy comparison as a measured bound, a summed statistic as a joint Bayesian fit, or a selected sample as a full-catalog validation.
2. **Resolve the entropy ontology.** The documentation treats entropy as a state variable, while the implementation uses it as a modeled coordinate in [`emergent_matter_model/model.py`](../emergent_matter_model/model.py). Choose and explain one formulation:
   - If entropy is a thermodynamic scalar or functional, represent it as a field/state variable and specify its coupling.
   - If an extra geometric coordinate is intended, define the manifold, metric, signature, units, and physical interpretation, and distinguish that coordinate from thermodynamic entropy.
3. **Reconcile public counts and descriptions.** Make README, status dashboards, test badges, papers, and release notes agree on the current test count and on what those tests establish. State clearly which datasets are complete catalogs, selected subsets, simulations, or illustrative examples.
4. **Correct strong-language claims.** Reserve "exact derivation," "joint Bayesian model selection," "verified DOI," and "100% rejection" for cases where the corresponding derivation or verification is actually present and reproducible.
5. **Keep an evidence ledger.** For every public scientific claim, record the claim, supporting equation/code/data, uncertainty, validation status, and known limitation. Mark claims as theoretical, simulated, exploratory, or observationally tested.

These changes improve credibility immediately and do not require abandoning the research direction.

## Priority 1: Establish a coherent physical model

Do not treat a screening function or a passing stability test as a substitute for a field theory. For any proposed model intended as fundamental physics:

1. Define all degrees of freedom, coordinates, signatures, constants, and units. Perform dimensional analysis term by term, including fitted and fixed parameters.
2. Provide a complete action (or explain why a different formulation is used) and derive the Euler-Lagrange equations. Identify the assumptions and approximations at each step.
3. Derive the stress-energy tensor and show how the field equations satisfy the relevant conservation laws and Bianchi identities.
4. Derive the GR limit rather than imposing it through a chosen interpolation. State which observables approach GR, at what order, and under what parameter limits.
5. Evaluate energy conditions where applicable. Expand perturbations about relevant backgrounds and report the kinetic matrix, its eigenvalues, gradient stability, characteristic speeds, and regime of validity. Do not infer stability of the full model from coefficients selected to pass a toy scan.
6. Compare the derivation with an independent specialist review before claiming new relativistic physics.

If a defensible action and covariant field equations cannot be produced, keep the scope explicitly phenomenological. A useful data model does not need to be advertised as a fundamental theory to be worth studying.

## Priority 2: Rebuild the empirical program around reproducibility

Start with one tractable regime, not ten. Select it based on whether the full input data, uncertainty model, and relevant selection function can be recovered and documented. Then:

1. **Predefine the test.** Before fitting, publish the target population, inclusion/exclusion rules, observables, model parameters, priors or estimators, comparator, acceptance/rejection criteria, and holdout procedure.
2. **Preserve provenance.** For each input, record the originating archive or publication, version/date, citation or DOI, license, checksum, transformations, and any manual decisions. Keep raw or minimally processed data distinguishable from derived tables.
3. **Use full statistical inputs.** Include measurement uncertainties, covariance matrices, selection effects, calibration/nuisance parameters, and contamination models where relevant. Document any approximations and test their impact.
4. **Fit shared parameters jointly when claiming a joint fit.** Optimize or sample the parameters under one stated likelihood. Report uncertainty and parameter correlations. Do not label a sum of separately evaluated chi-squares as a joint Bayesian inference.
5. **Compare like with like.** Fit the proposed model and established baselines to the same observations with consistent nuisance treatment. Explain the definition and assumptions behind any BIC, Bayes factor, or other model-selection quantity.
6. **Reserve independent data.** Use a holdout or genuinely external replication. Report failed targets and null results, not only aggregate scores or favorable examples.
7. **Make reproduction one command.** A clean checkout should fetch or validate the documented inputs and regenerate each reported table and figure, with fixed seeds and recorded software versions.

After a single regime is reproducible and survives out-of-sample tests, extend the method to other regimes one at a time. For especially demanding claims, such as the CMB, use the relevant published likelihood and covariance rather than a few selected summary values.

## Priority 3: Make adversarial tests independent and informative

Keep the existing synthetic challenges, but treat them as unit tests for obvious failure modes, not as proof of general selectivity. Strengthen them by:

- separating the code that generates challenges from the fitting code;
- defining challenge families and acceptance thresholds before running the fitter;
- adding realistic noise, correlated errors, missingness, systematics, and near-degenerate alternatives;
- including blinded and held-out cases prepared independently of the model implementation;
- testing false rejection of valid baseline data as well as false acceptance of unphysical data;
- reporting per-case outcomes and uncertainty, not only a success percentage.

A falsification test should have a realistic opportunity to fail the favored model. A deliberately extreme curve is a useful smoke test, but it is not a substitute for hard cases.

## Priority 4: Strengthen software reproducibility and release hygiene

Preserve the current test suite and CI success, then close the remaining engineering gaps:

1. Run the full Python suite on every pull request and release workflow, not only a subset of tests.
2. Add a dependency lock and a clean-environment install/test job. Verify that reproduction does not depend on a developer's pre-existing virtual environment.
3. Add configured linting and, where appropriate, type checks. Audit file and data paths from a fresh checkout on supported platforms.
4. Add automated checks for generated figures/tables and package contents. Test interactive visualizers for syntax errors and browser-console failures.
5. Resolve documentation drift by generating test counts and release metadata from the build or test workflow rather than maintaining conflicting hand-entered numbers.
6. Verify that the license covers the intended repository contents, that DOI metadata resolves to the released version, that bibliography DOIs resolve, and that SHA-256 hashes match the exact downloadable artifacts.
7. Document the JavaFX source-17 compiler warning and either resolve it or explain why it is benign for the supported build.

The passing tests are a good foundation; broaden automation so that a successful local run and a successful release run mean the same thing.

## Priority 5: Make safety and stewardship claims proportional to evidence

Keep the ethical commitments, but distinguish commitments from demonstrated safety properties. State what is known, what is not applicable to the current software, and what has not been assessed. Do not claim that vacuum decay, horizon formation, or biosphere risk has been ruled out without a defined physical model and analysis. Avoid proposing physical experiments based on unverified energy-density or metric claims. Record computational-resource measurements only if they are actually measured.

## Suggested stop/go milestones

| Milestone | Minimum evidence to proceed |
|---|---|
| **A. Accurate description** | Public claims match the implementation; counts and dataset scope are consistent. |
| **B. Reproducible baseline** | A clean checkout reruns the full test suite and regenerates one documented result from versioned inputs. |
| **C. Defined model** | Ontology, units, equations, parameter meaning, and stated GR limit are explicit and independently reviewable. |
| **D. One robust empirical test** | Preregistered selection, complete provenance, uncertainty/covariance treatment, baseline comparison, holdout, and failures are reported. |
| **E. Cross-regime expansion** | Each additional regime independently meets the same provenance and statistical standards. |
| **F. Strong theory claims** | Stability, conservation, and causal-propagation claims follow from the derived theory, not from test labels or tuned toy coefficients. |

Do not use the CQSI score as an optimization target. Improve the underlying evidence first and rescore only after the supporting artifacts exist. The practical next step is Milestone A, followed by a clean, fully reproducible result in one carefully selected regime.
