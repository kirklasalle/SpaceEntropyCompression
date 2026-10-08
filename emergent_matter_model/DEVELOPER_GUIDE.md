# Developer Guide

## Current research and validation entry points

See the [root README](../README.md) for environment setup and supported
real-data commands, and [CONTRIBUTING.md](../CONTRIBUTING.md) for evidence rules.
New verification runners live in [tools](../tools/); old stress-test scripts
may use synthetic inputs or imposed answers. Passing software tests does not
establish physical confirmation. The workflow file under this package's
`.github` directory is historical and is not a root GitHub Actions workflow.

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
- Use `pytest` for Python (`test_model.py`, `test_server_api.py`)
- Use Maven test for Java

## CI/CD
- GitHub Actions workflow: `.github/workflows/ci.yml`
- Runs Python unit tests (`pytest test_model.py -v`)
- Runs JavaFX client compile (`mvn -DskipTests compile`)
- Local equivalent when GitHub Actions is unavailable: `ci_local.ps1`
- Java 25 warning mitigation for Maven is configured via:
  - `javafx_client/.mvn/jvm.config`
  - `../install_maven.ps1` (`MAVEN_OPTS`)

## Contribution
- Follow code style and documentation guidelines
- Submit PRs for review

## AI Assistant Commitment
This developer guide is written and updated with the help of GitHub Copilot, ensuring technical accuracy and transparency for all contributors.
