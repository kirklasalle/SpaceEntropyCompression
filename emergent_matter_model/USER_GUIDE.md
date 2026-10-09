# User Guide

## Overview
This platform simulates and visualises emergent matter as a function of effective curvature across spatial dimensions and a thermodynamic entropy state parameter. 

Entropy S(X,t) is a thermodynamic state variable, not a spatial coordinate or time parameter. It characterizes the organizational state of the system and is "the arrow"—the direction in which physical processes naturally proceed (Second Law). The platform evaluates the matter field over a grid of spatial coordinates for a range of entropy states, producing output M[x, y, z, ..., S_j] = matter at spatial point (x,y,z,...) and entropy state S_j.

The platform provides a Python backend, JavaFX and web visualisation, and advanced math support via MCP server.

## Core Mathematical Theory
- **Spatial manifold:** \( X = (x_1, \ldots, x_n) \) with n spatial/topological coordinates.
- **Thermodynamic state field:** \( S(X,t) \) is entropy, a state variable (not a coordinate).
- **Weights:** \( w_i \) are normalised weights (\( \sum_{i=1}^{n} w_i = 1 \)), one per spatial dimension.
- **Curvature:** \( C_i(x_i) \) is the curvature contribution of the i-th spatial dimension.
- **Effective curvature:** \( C(X, S) = \sum_{i=1}^{n} w_i \, C_i(x_i) + w_S \, C_S(S) \) couples spatial and entropy contributions.
- **Matter field:** \( M(X, S) = k \left( \frac{C(X, S)}{C_0} \right)^\alpha \) is the emergent density.

When simulating, the model evaluates C and M at each point in the spatial grid for each entropy state in the sweep. The output array has shape (n_x, n_y, n_z, ..., n_S).

## Getting Started
1. Install Python requirements (`requirements.txt`).
2. For an installed CLI, run `python -m pip install .` from the
   `emergent_matter_model` directory. Check the installation:
   `python emergent_matter_model/emrf_cli.py doctor`.
3. List all supported operations:
   `python emergent_matter_model/emrf_cli.py list`.
4. Verify downloaded observations:
   `python emergent_matter_model/emrf_cli.py data list --verify`.
5. Start the API:
   `python emergent_matter_model/emrf_cli.py serve`.

Legacy commands such as `python emergent_matter_model/server.py` remain
supported. Use `python emergent_matter_model/emrf_cli.py run NAME -- ARGS`
for registered research, audit and release programs.

After installation, the equivalent supported command is `emrf doctor` or
`emrf list`; both use the same registry and preserve the legacy behavior.

## Features
- Simulate emergent matter models across spatial dimensions with entropy state sweep
- Entropy as a thermodynamic state field—the arrow of change
- Visualise results in 2D/3D at any entropy slice
- Parameter inference and quantum/discrete support
- Advanced math via MCP server

## API Quick Links
- OpenAPI spec: `openapi.yaml`
- Runnable requests: `API_EXAMPLES.md`
- Postman import: `postman/EmergentMatterAPI.postman_collection.json`
- Health/version: `GET /api/v1/health`, `GET /api/v1/version`
- Command discovery: `GET /api/v1/commands`
- Dataset status: `GET /api/v1/datasets?verify=true`

Remote command execution is disabled by default. It requires the explicit
`EMRF_API_ALLOW_RUN=1` environment flag and still refuses service and GUI
commands.

## Example Workflow
1. Configure model parameters in the client or API (spatial dimensions, weights, curvature functions).
2. Define a spatial grid and an entropy state sweep.
3. Run simulations and view results at chosen entropy states.
4. Export or analyse data as needed.

## Troubleshooting
- Run `emrf_cli.py doctor` and resolve every missing core dependency.
- Run `emrf_cli.py data list --verify`; do not analyze missing or mismatched
  observational bytes.
- Check server logs for errors.
- Consult the Developer Guide for golden-result and development workflows.

## AI Assistant Commitment
This user guide is created and maintained with the direct assistance of GitHub Copilot, ensuring clarity, accuracy, and user empowerment.
