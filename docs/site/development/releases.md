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

## Zenodo boundary

The DOI `10.5281/zenodo.23197308` belongs to a historical snapshot whose
scientific claims were later corrected. It must not identify version 1.0.0.
The repository carries accurate deposit metadata, but a new DOI may be added
only after Zenodo confirms a new archived release. Until then, cite the GitHub
release URL and exact commit.

## Failure and recovery

- Never move or recreate a published tag.
- Fix a failed workflow on `main`, increment the version if a release already
  exists, and create a new tag.
- Preserve withdrawn releases with prominent correction notices.
- Never publish when audit, package, provenance, metadata, or scientific
  golden checks are incomplete.
