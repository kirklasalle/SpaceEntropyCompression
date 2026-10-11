# Release engineering

EMRF releases certify software engineering and reproducibility gates. They do
not promote a scientific claim or convert a hypothesis into physical fact.

## Release prerequisites

A release candidate must be on protected `main` with these checks green:

- Windows and Linux on Python 3.10 and 3.12;
- JavaFX on Java 17;
- deterministic documentation on Python 3.10 and 3.12;
- all eight scientific golden suites;
- dependency audit, package metadata, and CycloneDX SBOM generation;
- OpenSSF Scorecard analysis.

The package version has one source in `emrf._version`. Before tagging, update
the changelog, CFF, CodeMeta, and `.zenodo.json`, then run:

```text
python tools/validate_release_metadata.py --tag vMAJOR.MINOR.PATCH
```

## Automated tag release

Pushing `vMAJOR.MINOR.PATCH` starts the release workflow. It independently
reruns the non-golden and golden gates, builds the wheel and source
distribution, validates package metadata, creates SHA-256 checksums, retains
the dependency-audit report and CycloneDX SBOM, and signs build provenance
through GitHub's Sigstore-backed artifact attestation service. Publication
occurs only after every prerequisite job succeeds.

Verify a downloaded distribution with the GitHub CLI:

```text
gh attestation verify emergent_matter_model-1.0.0-py3-none-any.whl \
  --repo kirklasalle/SpaceEntropyCompression
```

Also compare the file against `SHA256SUMS` from the same release.

## Monthly release-health rehearsal

The read-only `Release health` workflow runs on the first day of each month and
can also be dispatched for a specific stable tag. It resolves an existing
annotated release tag without moving it, checks out its immutable commit, and:

- validates synchronized release metadata and rebuilds the wheel and source
  distribution without publishing them;
- downloads the published bundle and requires complete SHA-256 coverage;
- verifies every published asset against GitHub's signed release-workflow
  provenance, exact source tag, and commit;
- installs the published wheel in an isolated environment and exercises the
  CLI doctor, typed SDK, REST v2 OpenAPI contract, and packaged knowledge graph;
- confirms the version-specific Zenodo DOI remains resolvable; and
- retains a machine-readable health receipt for 90 days.

The workflow has read-only repository and attestation permissions. It contains
no tag movement, repository push, release creation, package upload, or archival
publication step. A failed rehearsal is a maintenance incident; correct the
cause through protected `main` without altering the published tag or its assets.

## Zenodo boundary

Zenodo confirmed the version-specific EMRF 1.0.0 archive as
[`10.5281/zenodo.23304395`](https://doi.org/10.5281/zenodo.23304395). Cite that
DOI for version 1.0.0 together with the exact Git commit when reproducibility
requires it.

The DOI `10.5281/zenodo.23197308` belongs to a historical snapshot whose
scientific claims were later corrected. It must not identify version 1.0.0.
Neither DOI is evidence that the EMRF physics hypotheses are physically true.

## Failure and recovery

- Never move or recreate a published tag.
- Fix a failed workflow on `main`, increment the version if a release already
  exists, and create a new tag.
- Preserve withdrawn releases with prominent correction notices.
- Never publish when audit, package, provenance, metadata, or scientific
  golden checks are incomplete.

## Action and runner lifecycle

Workflow dependencies are executable supply-chain inputs. EMRF therefore:

- pins every external action to a full commit SHA and records its release
  version in a comment;
- requires action lines that use supported Node.js runtimes;
- pins hosted runner images instead of following migrating `latest` aliases;
- runs branch validation once through `pull_request`, with `push` validation
  reserved for protected `main`;
- cancels superseded CI and security runs while never cancelling release
  publication; and
- uses Dependabot plus workflow-governance regression tests to keep these
  guarantees current.

When an action or runner line reaches deprecation, update the immutable pins,
run Actionlint and the workflow-governance tests, and open a pull request. If
job display names change, wait for the replacement checks to pass on that pull
request, atomically replace the old required contexts with the successful new
names, and only then merge. The exact merged `main` commit must subsequently
pass CI, documentation, security and Scorecard publication.
