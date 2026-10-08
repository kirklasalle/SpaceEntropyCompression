# Real-data rerun and reviewer guide

This package accompanies the [SPARC paper](SPARC_HORIZON_TEST_PAPER.md), [regime report](REAL_DATA_REGIME_AUDIT.md) and [compression audit](EMRF_COMPRESSION_AND_HORIZONS_AUDIT.md). It is a research draft, not a submitted or peer-reviewed paper.

## Environment

The repository's Git attributes preserve exact bytes for hashed Python/TeX
sources, result artifacts and historical evidence. Do not normalize archived
line endings or trailing whitespace: that would invalidate the provenance
hashes. Historical result snapshots describe their recorded source versions;
failed earlier runs are not expected to match a later corrected runner.

Run from the repository root on Windows. The existing project interpreter is `emergent_matter_model\.venv\Scripts\python.exe`; its dependency declarations are in [pyproject.toml](../emergent_matter_model/pyproject.toml). Runtime/dependency and input hashes must accompany the numerical result artifacts. Do not substitute a fresh package environment and assume bitwise-identical optimizers.

## Verification completed

The full project software suite passed **219 tests** after numerical correction and manuscript integration. Existing Ruff checks passed for the changed validation modules and report/package tooling. The manuscript compiled locally to a **six-page PDF** with Tectonic 0.17.0. PDF text extraction with pypdf confirmed the title, principal findings and references without replacement-glyph markers. A non-fatal Fontconfig configuration error was printed, but compilation completed successfully; the TeX log had no overfull boxes, missing characters or undefined references. Unit tests validate software behavior only; they do not turn blocked physical cases into confirmed regimes.

Focused mypy checking passed for the nine changed implementation files using `--explicit-package-bases --follow-imports=silent --disable-error-code=import-untyped`. Namespace-package resolution is required by the repository's import layout. SciPy lacks installed stubs in this environment, so its untyped-import diagnostic is explicitly excluded; this is not a claim of strict, complete third-party type coverage. The numerical environment was not upgraded merely to install optional type stubs.

## Evidence boundaries

- Only traceable observed data or explicitly identified published observational constraints support empirical conclusions.
- Algebra checks and unit tests are software evidence, not observations.
- A blocked prediction is a documented scientific outcome, not a physical pass.
- Historical files under `results` and archived release bundles are retained; use the versioned `results/real_data_v1` outputs for the new draft.
- Profiling is not marginalization; interval widths from a penalized objective are conditional. The new report does not certify the historical significance claims.

## Fresh observed-data run

```powershell
& .\emergent_matter_model\.venv\Scripts\python.exe tools\run_sparc_profile_validation.py --step 0.05
& .\emergent_matter_model\.venv\Scripts\python.exe tools\check_sparc_influence.py
& .\emergent_matter_model\.venv\Scripts\python.exe tools\run_real_data_gauntlet.py
& .\emergent_matter_model\.venv\Scripts\python.exe tools\build_real_data_report.py
& .\emergent_matter_model\.venv\Scripts\python.exe tools\build_sparc_paper.py --compiler tectonic
& .\emergent_matter_model\.venv\Scripts\python.exe tools\package_real_data_release.py
```

The report generator refuses an incomplete or numerically unverified SPARC artifact, or a gauntlet linked to different SPARC bytes. The first command runs four fixed-stellar reference laws and four nuisance-profile laws; RAR prior-centre, bulge-ratio, free-bulge and selection sensitivities; deep subsets; deterministic leave-one-galaxy-out grid profiles; and a reverse-scan check. Successful individual optimizations are not assumed to prove global convergence. The second retrieves public source pages and version-pinned observed cosmology tables, fits a covariance-aware flat-LCDM BAO baseline, and records precise theory/data blockers. Source pages are not counted as measurement tables. DESI baseline agreement is not EMRF agreement.

The first numerical run found a forward/reverse objective discrepancy of about 5.98. It is preserved as `sparc_initial_scan_order_failure.json` and is **not** a validated inference. A residual-based rerun reduced the discrepancy to about 0.379 but still failed; it is preserved separately as `sparc_residual_scan_order_failure.json`. A targeted diagnostic located the difference in UGC 07577, where signed gas components and the declared baryonic floor create multiple smooth regions. The corrected implementation partitions the fixed-bulge stellar-mass domain at those transitions, optimizes each region using scaled least-squares with an analytically checked Jacobian, and takes the lowest objective. This changes the numerical search, not the data or physical law. Free-bulge fits use additional floor-aware starts. Report generation requires the primary RAR rerun's maximum total-objective discrepancy to be below 0.1; that tolerance tests numerical repeatability, not statistical coverage.

The completed branch-aware rerun achieved a maximum primary scan discrepancy of **4.7403 × 10⁻⁹**. Separately, the exploratory UGC 06787 exclusion was recomputed by a full-grid refit, not just by subtracting a previously stored profile. It reproduces the deep-bulge grid shift from 1.60 to 0.90 × 10⁻¹⁰ m/s², demonstrating substantial single-galaxy influence rather than a robust population discovery.

## Algebra diagnostic

```powershell
& .\emergent_matter_model\.venv\Scripts\python.exe tools\check_compression_claims.py
& .\emergent_matter_model\.venv\Scripts\python.exe -m pytest emergent_matter_model\test_compression_claims_audit.py -q
```

The output is labelled non-empirical. It deliberately exposes the input-mass normalization and assumed entropy coefficient rather than claiming their agreement as physical confirmation.

## Manuscript build

```powershell
Set-Location paper
pdflatex -interaction=nonstopmode -halt-on-error sparc_horizon_test.tex
bibtex sparc_horizon_test
pdflatex -interaction=nonstopmode -halt-on-error sparc_horizon_test.tex
pdflatex -interaction=nonstopmode -halt-on-error sparc_horizon_test.tex
```

The manuscript depends on its generated results supplement and bibliography. No compiler was initially on PATH; the official portable Tectonic 0.17.0 Windows release was subsequently installed in session storage. With Tectonic available, the equivalent build is `tectonic --untrusted --keep-logs paper\\sparc_horizon_test.tex` from the repository root. The final `manuscript_build.json` artifact records the actual compiler execution and PDF/source hashes. Tectonic automatically runs the bibliography and required reruns; no external document-upload service is used.

## Scope not completed by this bounded implementation

The fresh runner does not replace every historical statistical script. It adds a separately labelled validation path while preserving legacy behavior. Conditional intervals and influence ranges remain grid-based; continuous interval/root refinement, an exhaustive quality-cut study, integrated external H₀ uncertainty and a physical covariance/discrepancy model remain open. Source acquisition for most non-SPARC regimes records primary pages and their blockers, not full instrument-level datasets. Pantheon+ ingestion does not include a full supernova covariance likelihood. DESI has a real flat-LCDM baseline fit, but no derived EMRF cosmological likelihood. These scientific limitations remain attached to the paper; the project does not certify a theorem or complete ten-regime empirical confirmation.

## Independent-review questions

1. Are the observed-coordinate likelihood, distance/inclination transformations and signed component conventions correct?
2. Are nuisance constraints defensible for this sample, particularly bulges and nearly edge-on galaxies?
3. How should radial covariance, noncircular motions and intrinsic model discrepancy alter the inference?
4. Do numerical convergence, grid range and multi-start tests establish reliable conditional profiles?
5. Are subgroup contrasts dominated by particular galaxies, shared errors or quality selections?
6. Is any claimed novelty already present in published SPARC/universality/bulge analyses?
7. Which comparisons admit a defensible likelihood-ratio or information criterion, and which should remain descriptive?
8. What extra dynamics are needed before the other regimes can constrain the same EMRF model?

## Release staging, not publication

Before an eventual Zenodo release, include the new manuscript/source, generated tables and figures, versioned results, manifests, scripts/tests, protocol, correction history and exact reproduction commands. Respect catalogue redistribution conditions; link to restricted or large original products rather than silently bundling them. Do not include credentials, private account information or mutable environment directories. Record the final source revision and file checksums.

No repository commit, Zenodo upload, arXiv submission, reviewer contact or IBM Quantum job is authorized by this preparation step. Release approval should follow independent review and a successful manuscript build.
