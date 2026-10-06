# Java ↔ Python API Contract

This document maps the JavaFX client request/response contract for the Python simulation endpoint.

## Endpoint

- Method: `POST`
- URL: `http://127.0.0.1:5000/api/v1/simulate`
- Content-Type: `application/json`

## Request payload

Fields used by `Scatter3DApp`:

- `n` (int): total dimensions, including entropy dimension as the last axis
- `weights` (float[]): length = `n`
- `X_grid` (float[][]): list of one-dimensional axis arrays, length = `n`
  - `X_grid[n-1]` is entropy values `S`
- `k` (float, optional)
- `alpha` (float, optional)
- `C0` (float, optional)

Current Java payload shape:

- `n = 4`
- `weights = [0.3, 0.3, 0.2, 0.2]`
- `X_grid = [x, y, z, s]`

## Response payload

- Success body: `{ "M": ... }`
- `M` is nested as `M[x][y][z][s]` for the 4D case

Client mapping in `Scatter3DApp`:

1. Reads `M` as `JSONArray` nesting.
2. Uses highest entropy slice (`sIndex = ns - 1`).
3. Converts each `(ix, iy, iz)` to a rendered 3D point.
4. Normalizes matter value for color/size.

## Errors

- HTTP 400: `{ "error": "..." }` for validation issues
- HTTP 500: `{ "error": "Internal server error" }`

Fallback behavior in Java client:

- If request fails or response is invalid, the app renders built-in sample points.

## Spec reference

Formal API schema: `../openapi.yaml`
