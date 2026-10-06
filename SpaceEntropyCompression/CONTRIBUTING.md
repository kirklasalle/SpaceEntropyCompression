# Contributing to EMRF / Space-Entropy Compression

Thank you for your interest in contributing to the **Emergent Matter Research Framework (EMRF)**. We welcome contributions from theoretical physicists, astronomers, software engineers, and data scientists.

---

## 1. Core Scientific Ethos

All contributions must respect the foundational principles of the framework:

1. **Dimensional Spatial Ontology:** Space is represented by a Riemannian manifold $\mathcal{M}^D$ with coordinates $X = \{x, y, z, d_0, d_1, d_2, \dots\}$. Neither coordinate time $t$ nor thermodynamic entropy $S(X,t)$ is a spatial coordinate axis. Time parameterizes dynamical change, and entropy is an organizational thermodynamic state variable.
2. **Strict Falsifiability & Bifurcation Protocol:** We do not protect speculative models with post-hoc fine-tuning. If a model collapses to General Relativity in high-curvature regimes ($\Delta\text{BIC} \ge +10.0$), it is celebrated as **Branch A: Geometric Collapse**. Null and negative results must be published with equal prominence.
3. **Zero-Regression Testing:** Every new physics module, data parser, or mathematical formulation must be accompanied by automated unit tests passing under `pytest`.

---

## 2. Development Setup

The project uses Python 3.10+ and a standard virtual environment.

```bash
# Clone the repository
git clone https://github.com/emergent-matter/space-entropy-compression.git
cd space-entropy-compression/emergent_matter_model

# Activate virtual environment
.venv\Scripts\activate      # Windows PowerShell/CMD
# source .venv/bin/activate  # Linux / macOS

# Install package in editable mode with development dependencies
pip install -e ".[dev]"
```

---

## 3. Running Tests and Quality Checks

Before submitting any Pull Request, ensure that all tests and lint checks pass cleanly:

```bash
# 1. Run all unit and integration tests
pytest -v

# 2. Run Ruff linter and code formatter
ruff check .
ruff format --check .

# 3. Run Mypy static type checker
mypy model.py physics_baseline.py fit_astrometry.py fit_sparc.py

# 4. Run full local CI runner (includes headless check and JavaFX compile)
cd ..
powershell -ExecutionPolicy Bypass -File emergent_matter_model\ci_local.ps1
```

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

- **Lead Investigator:** Kirk LaSalle (`theory@emergentmatter.org`)
- **Repository Issues:** [GitHub Issues](https://github.com/emergent-matter/space-entropy-compression/issues)
