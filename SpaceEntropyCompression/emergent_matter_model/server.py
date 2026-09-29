"""REST API for emergent matter simulation.

Entropy (S) is the last dimension in X_grid, treated as a full
dimensional coordinate — not a separate time parameter.
"""

import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from model import EmergentMatterModel
import numpy as np
from typing import Any, Dict, List, Tuple

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _is_real_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and np.isfinite(value)


def _validate_and_parse_payload(data: Dict[str, Any]) -> Tuple[int, List[float], List[np.ndarray], float, float, float]:
    for field in ("n", "weights", "X_grid"):
        if field not in data:
            raise ValueError(f"Missing required field: '{field}'")

    n_raw = data["n"]
    if not isinstance(n_raw, int):
        raise ValueError("n must be an integer")
    n = int(n_raw)
    if n < 1:
        raise ValueError("n must be >= 1")

    weights_raw = data["weights"]
    if not isinstance(weights_raw, list) or len(weights_raw) != n:
        raise ValueError(f"weights must be a list of length n={n}")
    if not all(_is_real_number(w) for w in weights_raw):
        raise ValueError("weights must contain only finite numeric values")

    weight_sum = float(np.sum(weights_raw))
    if np.isclose(weight_sum, 0.0):
        raise ValueError("weights must not sum to zero")

    x_grid_raw = data["X_grid"]
    if not isinstance(x_grid_raw, list) or len(x_grid_raw) != n:
        raise ValueError(f"X_grid must be a list of {n} arrays")

    x_grid: List[np.ndarray] = []
    for idx, axis in enumerate(x_grid_raw):
        if not isinstance(axis, list):
            raise ValueError(f"X_grid[{idx}] must be a list of numeric values")
        if len(axis) == 0:
            raise ValueError(f"X_grid[{idx}] must not be empty")
        if not all(_is_real_number(v) for v in axis):
            raise ValueError(f"X_grid[{idx}] must contain only finite numeric values")
        x_grid.append(np.array(axis, dtype=float))

    for optional_field in ("k", "alpha", "C0"):
        if optional_field in data and not _is_real_number(data[optional_field]):
            raise ValueError(f"{optional_field} must be a finite numeric value")

    k = float(data.get("k", 1.0))
    alpha = float(data.get("alpha", 1.0))
    C0 = float(data.get("C0", 1.0))
    return n, [float(w) for w in weights_raw], x_grid, k, alpha, C0


@app.route('/api/v1/simulate', methods=['POST'])
def simulate():
    """Run a simulation.

    Expected JSON payload
    ---------------------
    n        : int   — total dimensions (spatial + entropy)
    weights  : list  — one weight per dimension (last = entropy)
    X_grid   : list of lists — one grid per dimension (last = entropy S values)
    k, alpha, C0 : float (optional, default 1.0)

    The server uses demo curvature functions.  Custom curvature
    functions can be supported in a future version.
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Request body must be valid JSON'}), 400

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'error': 'Request body must be valid JSON'}), 400

        n, weights, X_grid, k, alpha, C0 = _validate_and_parse_payload(data)

        # Demo curvature: one function per dimension (single-argument).
        # The last function applies to the entropy dimension.
        C_funcs = [lambda x, i=i: (x + i) ** 2 for i in range(n)]

        model = EmergentMatterModel(n, weights, k, alpha, C0)
        M = model.simulate_grid(X_grid, C_funcs)

        logger.info("Simulation complete — shape %s", M.shape)
        return jsonify({'M': M.tolist()})

    except (ValueError, TypeError, KeyError) as exc:
        logger.warning("Bad request: %s", exc)
        return jsonify({'error': str(exc)}), 400
    except Exception as exc:
        logger.exception("Internal error during simulation")
        return jsonify({'error': 'Internal server error'}), 500


# Backward-compatible route (no version prefix)
@app.route('/simulate', methods=['POST'])
def simulate_legacy():
    """Legacy endpoint — forwards to /api/v1/simulate."""
    return simulate()


if __name__ == '__main__':
    app.run(debug=False)
