# Developer Guide

## Project Structure
- `model.py`: Core mathematical model (space + entropy dimensions)
- `server.py`: Python REST API
- `openapi.yaml`: OpenAPI 3.0 specification for REST endpoints
- `visualize.py`: 2D Python visualisation client
- `viz3d.py`: 3D Plotly visualisation
- `javafx_client/`: JavaFX Maven project
- `requirements.txt`: Python dependencies
- `pom.xml`: JavaFX Maven config
- `resources/`: JavaFX SDK and other assets

## Foundational Principle
Entropy (S) is **dimensional**, not parametric. It is the quantifiable
expression of what is conventionally called "time". The model treats
entropy as the (n+1)-th dimension alongside n spatial dimensions.

## Core Mathematical Theory
- \( \tilde{X} = (x_1, \ldots, x_n, S) \) — n spatial coordinates plus one entropy coordinate.
- \( w_i \) are normalised weights (\( \sum_{i=1}^{n+1} w_i = 1 \)), one per dimension.
- \( C_i(\tilde{x}_i) \) is the curvature in the i-th dimension — a function of that dimension's coordinate only.
- \( C(\tilde{X}) = \sum_{i=1}^{n+1} w_i \, C_i(\tilde{x}_i) \) is the effective curvature.
- \( M(\tilde{X}) = k \left( \frac{C(\tilde{X})}{C_0} \right)^\alpha \) is the emergent matter mapping.

The last dimension is always entropy.  Each curvature function `C_i` takes
a **single argument** (its own coordinate value).

Discrete/quantum versions, parameter inference, and falsifiable predictions are supported. See the PRD for full details.

## Setup
1. Install Python and Java dependencies
2. Configure JavaFX SDK path in `pom.xml`
3. Run Python server and JavaFX client

## Extending the Model
- Add new curvature functions in `model.py` — each `c_func` takes one
  argument: `c_func(x_i) -> float`
- For the entropy dimension, design `C_S(S)` to be monotonically
  non-decreasing to respect the second law of thermodynamics
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
