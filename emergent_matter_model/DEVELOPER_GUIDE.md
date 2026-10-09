# Developer Guide

## Current research and validation entry points

See the [root README](../README.md) for environment setup and supported
real-data commands, and [CONTRIBUTING.md](../CONTRIBUTING.md) for evidence rules.
New verification runners live in [tools](../tools/); old stress-test scripts
may use synthetic inputs or imposed answers. Passing software tests does not
establish physical confirmation. The workflow file under this package's
`.github` directory is historical; the active repository workflow is
[`../.github/workflows/ci.yml`](../.github/workflows/ci.yml).

## Project Structure
- `model.py`: Core mathematical model (spatial dimensions + entropy state evaluation)
- `server.py`: Python REST API
- `openapi.yaml`: OpenAPI 3.0 specification for REST endpoints
- `visualize.py`: 2D Python visualisation client
- `viz3d.py`: 3D Plotly visualisation
- `javafx_client/`: JavaFX Maven project
- `requirements.txt`: Python dependencies
- `pom.xml`: JavaFX Maven config
- `resources/`: JavaFX SDK and other assets

## Foundational Principle (T03 Decision, 2026-10-07)
**Entropy is a thermodynamic state field, not a spatial coordinate.**

Space is multidimensional: X = (x, y, z, d_0, d_1, d_2, …).
Time t is the progression parameter; entropy S(X,t) is a state variable.
The model couples entropy into the effective compression as C(X,S,t) = F(E, S, geometry, t).
Entropy is the arrow: physical processes proceed in the direction of increasing entropy (Second Law).

When evaluating the model, we sweep over entropy states: for each spatial point X, 
we compute M(X, S_1), M(X, S_2), ..., M(X, S_m). The output array M[x, y, z, ..., j] 
is the matter field at spatial coords (x,y,z,...) and entropy state S_j.

## Core Mathematical Theory
- **Spatial manifold:** \( X = (x_1, \ldots, x_n) \) with n spatial/topological coordinates.
- **State field:** \( S(X,t) \) is entropy, a thermodynamic state variable (not a coordinate).
- **Weights:** \( w_i \) are normalised weights (\( \sum_{i=1}^{n} w_i = 1 \)), one per spatial dimension.
- **Curvature:** \( C_i(x_i) \) depends only on coordinate i; \( C_S(S) \) couples entropy state.
- **Effective curvature:** \( C(X, S) = \sum_{i=1}^{n} w_i \, C_i(x_i) + w_S \, C_S(S) \)
- **Matter field:** \( M(X, S) = k \left( \frac{C(X, S)}{C_0} \right)^\alpha \)

Each curvature function `C_i` takes a **single argument** (its own coordinate value).
The entropy coupling `C_S(S)` should be monotonically non-decreasing to respect the Second Law.

Discrete/quantum versions, parameter inference, and falsifiable predictions are supported. See the PRD for full details.

## Setup
1. Install Python and Java dependencies
2. Configure JavaFX SDK path in `pom.xml`
3. Run Python server and JavaFX client

## Extending the Model
- Add new spatial curvature functions in `model.py` — each `c_func` takes one
  argument: `c_func(x_i) -> float`
- For entropy coupling, design `C_S(S)` to be monotonically non-decreasing to respect the Second Law
- Extend API endpoints in `server.py`
- Add new visualisations in Python or JavaFX
- Use `EmergentMatterModel.from_spatial_and_entropy(n_spatial, spatial_weights, entropy_weight)` for clarity

## MCP Server Integration
- Document API endpoints and math preservation features
- Use MCP server for advanced math and computation

## API Specification
- REST contract is formally defined in `openapi.yaml`
- Primary endpoint: `POST /api/v1/simulate`
- Legacy alias: `POST /simulate`
- Runnable examples: `API_EXAMPLES.md`
- Postman collection: `postman/EmergentMatterAPI.postman_collection.json`

## Testing

Install the development environment from the repository root:

```powershell
emergent_matter_model\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

CI additionally applies `constraints-ci.txt`, which freezes the exact
dependency versions used to certify the current golden results. Dependency
upgrades require a separate reviewed change and a golden-result comparison.

Then run:

```powershell
# Fast software suite
emergent_matter_model\.venv\Scripts\python.exe -m pytest -m "not golden" -q

# Real-data regression suite (requires verified external holdings)
emergent_matter_model\.venv\Scripts\python.exe tools\run_golden_results.py --all

# Inspect available golden cases
emergent_matter_model\.venv\Scripts\python.exe emergent_matter_model\emrf_cli.py run golden-results -- --list
```

The golden runner copies code, inputs and reference results to a temporary
workspace. It re-runs eight fixed real-data pipelines without overwriting the
reviewed `results/` tree. Integers, strings, hashes and collection shapes are
exact; computed floating-point values use `rtol=1e-10`. Only declared
timestamps, environment metadata and derived parent hashes are ignored.
The two pseudo-isothermal-halo totals use `rtol=1e-7` because L-BFGS-B
termination varies at approximately 2e-8 relative across Windows hardware;
legacy optimizer-heavy SPARC cases use `rtol=5e-3` because hosted-CPU trials
exposed up to approximately 1.8e-3 relative drift in nested nuisance profiles.
This is a documented numerical-stability limitation, not a scientific
uncertainty. Non-optimizer floating-point outputs retain `rtol=1e-10`, and
structure, integers, strings and hashes remain exact.
The current reviewed results were generated and certified on Windows x86-64
with Python 3.10. Linux and Python 3.12 run the complete functional suite;
separate reviewed golden baselines are required before claiming numerical
parity for those environments.

## CI/CD
- Root GitHub Actions workflow: `../.github/workflows/ci.yml`
- Unit/coverage matrix: Windows and Linux on Python 3.10 and 3.12
- Separate Windows/Python 3.10 job: verified SPARC/Pantheon+ acquisition and
  all real-data golden comparisons on the baseline environment
- Local equivalent: `ci_local.ps1`; set `EMRF_RUN_GOLDEN=1` to include the
  expensive golden suite
- Java 25 warning mitigation for Maven is configured via:
  - `javafx_client/.mvn/jvm.config`
  - `../install_maven.ps1` (`MAVEN_OPTS`)

## Contribution
- Follow code style and documentation guidelines
- Submit PRs for review

## AI Assistant Commitment
This developer guide is written and updated with the help of GitHub Copilot, ensuring technical accuracy and transparency for all contributors.
