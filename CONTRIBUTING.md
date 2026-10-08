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

The project uses Python 3.10+ and a standard virtual environment.

```powershell
# Clone the repository
git clone https://github.com/kirklasalle/SpaceEntropyCompression.git
Set-Location SpaceEntropyCompression

# Activate virtual environment
python -m venv emergent_matter_model\.venv

# Install package in editable mode with development dependencies
& .\emergent_matter_model\.venv\Scripts\python.exe -m pip install -e ".\emergent_matter_model[dev]"
```

---

## 3. Running Tests and Quality Checks

Before submitting changes, run the relevant tests and existing lint rules.
The legacy repository is not claimed to be globally lint/type-clean; do not
hide new failures behind pre-existing diagnostics.

```powershell
& .\emergent_matter_model\.venv\Scripts\python.exe -m pytest emergent_matter_model -q
# Apply Ruff to the changed files; example:
& .\emergent_matter_model\.venv\Scripts\python.exe -m ruff check tools\check_candidate_a_definitions.py
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
2. **Commit Standards:** Write clear, concise commit messages following standard conventions:
   - `feat:` New features or theoretical formulations
   - `fix:` Bug fixes or corrections to physical parameters
   - `test:` New or updated automated tests
   - `docs:` Documentation, knowledgebase, or research paper edits
3. **Knowledgebase Teaching Directive:**
   Whenever modifying existing algorithms, adding datasets, or introducing new equations:
   - Update `knowledgebase/GRAPH_MEMORY.json` with new nodes and edges.
   - Update corresponding reference handbooks in `knowledgebase/`.
   - Update `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/).
4. **Open a Pull Request:** Submit your PR against the `main` branch with a description of the physical motivation, mathematical formulation, and test results.

---

## 5. Contact & Discussion

- **Lead Investigator:** Kirk LaSalle
- **Repository Issues:** [GitHub Issues](https://github.com/kirklasalle/SpaceEntropyCompression/issues)
