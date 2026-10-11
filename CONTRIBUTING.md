# Contributing to EMRF / Space-Entropy Compression

Thank you for your interest in contributing to the **Emergent Matter Research Framework (EMRF)**. We welcome contributions from theoretical physicists, astronomers, software engineers, and data scientists.

---

## 1. Core Scientific Ethos

All contributions must respect the foundational principles of the framework:

1. **Dimensional Spatial Ontology:** Space is represented by a Riemannian manifold $\mathcal{M}^D$ with coordinates $X = \{x, y, z, d_0, d_1, d_2, \dots\}$. Neither coordinate time $t$ nor thermodynamic entropy $S(X,t)$ is a spatial coordinate axis. Time parameterizes dynamical change, and entropy is an organizational thermodynamic state variable.
2. **Evidence and falsifiability:** Report null and negative results. A BIC non-preference does not prove equivalence to GR, and penalized nuisance objectives are not automatically valid BIC likelihoods. Candidate A is the selected research direction, not an equivalence theorem. See the [model card](MODEL_CARD.md) and [functional comparison](docs/EMRF_CANDIDATE_A_FUNCTIONAL_COMPARISON.md).
3. **Zero-Regression Testing:** Every new physics module, data parser, or mathematical formulation must be accompanied by automated unit tests passing under `pytest`.

---

## 2. Development Setup

The certified Python versions are 3.10 and 3.12. Use a standard virtual
environment or open the repository in the included VS Code dev container.

```powershell
# Clone the repository
git clone https://github.com/kirklasalle/SpaceEntropyCompression.git
Set-Location SpaceEntropyCompression

# Activate virtual environment
python -m venv emergent_matter_model\.venv

# Install the complete certified development environment
& .\emergent_matter_model\.venv\Scripts\python.exe -m pip install `
  -r requirements-dev.txt -c constraints-ci.txt
& .\emergent_matter_model\.venv\Scripts\python.exe -m pip install `
  -e .\emergent_matter_model -c constraints-ci.txt
```

---

## 3. Running Tests and Quality Checks

Before submitting changes, run the relevant tests and existing lint rules.
The legacy repository is not claimed to be globally lint/type-clean; do not
hide new failures behind pre-existing diagnostics.

```powershell
& .\emergent_matter_model\.venv\Scripts\python.exe -m pytest -m "not golden" -q
# Apply Ruff to the changed files; example:
& .\emergent_matter_model\.venv\Scripts\python.exe -m ruff check tools\check_candidate_a_definitions.py
# Validate knowledge and generated documentation:
& .\emergent_matter_model\.venv\Scripts\python.exe emergent_matter_model\emrf_cli.py kb validate
& .\emergent_matter_model\.venv\Scripts\python.exe tools\generate_docs_reference.py --check
& .\emergent_matter_model\.venv\Scripts\mkdocs.exe build --strict
& .\emergent_matter_model\.venv\Scripts\python.exe tools\validate_release_metadata.py
```

Keep observational data separate from fixtures; record sources, hashes, units,
selection and covariance. Tests of generated inputs are software checks only.
Do not add a new physical mechanism or silently choose C on the author's behalf.
Preserve historical source copies and qualify graph entries by evidence type.

---

## 4. Pull Request Workflow

1. **Fork and Branch:** Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Commit Standards:** Write an imperative subject no longer than 72
   characters. Explain scientific, compatibility, and data-safety reasons in
   the body when the change is non-trivial.
3. **Knowledgebase Teaching Directive:**
   Whenever modifying existing algorithms, adding datasets, or introducing new equations:
   - Update `knowledgebase/GRAPH_MEMORY.json` with new nodes and edges.
   - Update corresponding reference handbooks in `knowledgebase/`.
   - Validate with `emrf kb validate`.
4. **Open a Pull Request:** Submit your PR against the `main` branch with a description of the physical motivation, mathematical formulation, and test results.

Cross-cutting architecture changes require an ADR under `docs/adr/`.
External runtime plugins are not supported; follow the in-tree extension
tutorial in the documentation site.

---

## 5. Release Governance

Only a protected, fully green `main` commit may be tagged. Release metadata,
the changelog, package version, CFF, CodeMeta, and Zenodo deposit metadata must
pass `tools/validate_release_metadata.py`. A `vMAJOR.MINOR.PATCH` tag starts the
release workflow, which reruns the non-golden suite and all eight scientific
golden cases before publishing checksummed distributions, a CycloneDX SBOM,
the dependency-audit report, and signed GitHub build-provenance attestations.

Do not create or move a release tag to bypass a failed gate. Do not attach the
historical Zenodo DOI to a new release. Record a new DOI only after the archive
service confirms the deposit. See the
[release engineering guide](https://kirklasalle.github.io/SpaceEntropyCompression/development/releases/).

---

## 6. Contact & Discussion

- **Lead Investigator:** Kirk LaSalle
- **Repository Issues:** [GitHub Issues](https://github.com/kirklasalle/SpaceEntropyCompression/issues)
- **Discussions:** [GitHub Discussions](https://github.com/kirklasalle/SpaceEntropyCompression/discussions)
- **Security:** Follow [SECURITY.md](SECURITY.md), never a public exploit issue.
