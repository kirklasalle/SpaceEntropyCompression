# User Guide

## Overview
This platform simulates and visualises emergent matter as a function of effective curvature across n spatial dimensions plus one entropy dimension. Entropy (S) is treated as a full dimension — it is the quantifiable expression of what is conventionally called "time". There is no separate time parameter; entropy IS the clock.

The platform provides a Python backend, JavaFX and web visualisation, and advanced math support via MCP server.

## Core Mathematical Theory
- \( \tilde{X} = (x_1, \ldots, x_n, S) \) — n spatial coordinates plus one entropy coordinate (S), giving (n+1) total dimensions.
- \( w_i \) are normalised weights (\( \sum_{i=1}^{n+1} w_i = 1 \)), one per dimension.
- \( C_i(\tilde{x}_i) \) is the curvature contribution of the i-th dimension, depending only on its own coordinate.
- \( C(\tilde{X}) = \sum_{i=1}^{n+1} w_i \, C_i(\tilde{x}_i) \) is the effective curvature.
- \( M(\tilde{X}) = k \left( \frac{C(\tilde{X})}{C_0} \right)^\alpha \) is the emergent matter mapping.

The **last dimension** in any coordinate vector is always the entropy dimension S.

Discrete/quantum versions, parameter inference, and falsifiable predictions are supported. See the PRD for full details.

## Getting Started
1. Install Python requirements (`requirements.txt`).
2. Run the Python server (`server.py`).
3. Use the Python or JavaFX client to visualise results.
4. (Optional) Use the web client for browser-based visualisation.

## Features
- Simulate emergent matter models across space + entropy
- Entropy as a full dimension — not a time parameter
- Visualise results in 2D/3D at any entropy slice
- Parameter inference and quantum/discrete support
- Advanced math via MCP server

## API Quick Links
- OpenAPI spec: `openapi.yaml`
- Runnable requests: `API_EXAMPLES.md`
- Postman import: `postman/EmergentMatterAPI.postman_collection.json`

## Example Workflow
1. Configure model parameters in the client or API (dimensions, weights, curvature functions).
2. Include an entropy grid as the last element of `X_grid`.
3. Run simulations and view results at chosen entropy slices.
4. Export or analyse data as needed.

## Troubleshooting
- Ensure all dependencies are installed
- Check server logs for errors
- Consult the Developer Guide for advanced usage

## AI Assistant Commitment
This user guide is created and maintained with the direct assistance of GitHub Copilot, ensuring clarity, accuracy, and user empowerment.
