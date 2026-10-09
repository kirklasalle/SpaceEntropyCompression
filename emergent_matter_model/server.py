"""REST API for emergent matter simulation.

X_grid spans multidimensional spatial coordinates X = {x, y, z, d_0, d_1, d_2, ...} in M^D.
Time t parameterizes dynamical evolution; entropy S(X,t) is a thermodynamic state field that
characterizes organizational compression and couples into the matter density via C(X,S,t).

Entropy is not a spatial coordinate. When evaluating the model over entropy states,
pass the entropy values as the last grid entry; output M[..., j] represents matter
at the j-th entropy state S_j.
"""

import logging
import os
import subprocess
import time
from collections import defaultdict
from typing import Any

import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

import emrf_registry as registry
from emrf_version import API_VERSION, __version__
from model import EmergentMatterModel

# Remote execution of registered programs is disabled unless explicitly enabled.
RUN_ENV_FLAG = "EMRF_API_ALLOW_RUN"
_MAX_RUN_TIMEOUT_SEC = 600.0

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory sliding window rate limiter: client_ip -> list of timestamps
_RATE_LIMIT_WINDOW_SEC = 60.0
_RATE_LIMIT_MAX_REQUESTS = 120
_request_records: dict[str, list[float]] = defaultdict(list)


def _check_rate_limit(client_ip: str) -> bool:
    """Return True if request is allowed, False if rate limit is exceeded."""
    now = time.time()
    cutoff = now - _RATE_LIMIT_WINDOW_SEC
    timestamps = [t for t in _request_records[client_ip] if t > cutoff]
    if len(timestamps) >= _RATE_LIMIT_MAX_REQUESTS:
        _request_records[client_ip] = timestamps
        return False
    timestamps.append(now)
    _request_records[client_ip] = timestamps
    return True


def _is_real_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and np.isfinite(value)


def _validate_and_parse_payload(
    data: dict[str, Any],
) -> tuple[int, list[float], list[np.ndarray], float, float, float]:
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

    x_grid: list[np.ndarray] = []
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


def run_simulation(
    n: int, weights: list[float], x_grid: list[np.ndarray], k: float, alpha: float, C0: float
) -> np.ndarray:
    """Shared simulation core used by both the REST API and the CLI."""
    # Demo curvature: one function per dimension (single-argument).
    C_funcs = [lambda x, i=i: (x + i) ** 2 for i in range(n)]
    model = EmergentMatterModel(n, weights, k, alpha, C0)
    return model.simulate_grid(x_grid, C_funcs)


@app.errorhandler(HTTPException)
def _json_http_error(exc: HTTPException):
    return jsonify({'error': exc.description, 'status': exc.code}), exc.code


@app.route('/api/v1/health', methods=['GET'])
def health():
    """Health check endpoint for service monitoring and load balancers."""
    return jsonify({
        'status': 'healthy',
        'service': 'emergent-matter-model',
        'version': __version__
    }), 200


@app.route('/api/v1/version', methods=['GET'])
def version():
    return jsonify({'version': __version__, 'api_version': API_VERSION})


@app.route('/api/v1/doctor', methods=['GET'])
def doctor():
    """Read-only environment and dependency diagnostics (same as `emrf doctor`)."""
    report = registry.environment_report()
    report.pop('executable', None)
    return jsonify(report)


@app.route('/api/v1/commands', methods=['GET'])
def list_commands():
    category = request.args.get('category')
    if category is not None and category not in registry.CATEGORIES:
        return jsonify({'error': f'Unknown category: {category}',
                        'categories': list(registry.CATEGORIES)}), 400
    return jsonify({'commands': registry.list_commands(category),
                    'run_enabled': os.environ.get(RUN_ENV_FLAG) == '1'})


@app.route('/api/v1/commands/<name>', methods=['GET'])
def get_command(name: str):
    try:
        registry.get_command(name)
    except KeyError as exc:
        return jsonify({'error': exc.args[0]}), 404
    return jsonify(next(c for c in registry.list_commands() if c['name'] == name))


@app.route('/api/v1/commands/<name>/run', methods=['POST'])
def run_command(name: str):
    """Run a registered program (same as `emrf run`). Disabled unless EMRF_API_ALLOW_RUN=1."""
    if os.environ.get(RUN_ENV_FLAG) != '1':
        return jsonify({'error': f'Command execution is disabled. Set {RUN_ENV_FLAG}=1 '
                                 'on a trusted host to enable it.'}), 403
    client_ip = request.remote_addr or '127.0.0.1'
    if not _check_rate_limit(client_ip):
        return jsonify({'error': 'Rate limit exceeded'}), 429
    try:
        cmd = registry.get_command(name)
    except KeyError as exc:
        return jsonify({'error': exc.args[0]}), 404
    if cmd.gui or cmd.category == 'service':
        return jsonify({'error': f'{name} is interactive or a service and cannot run via API'}), 400
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({'error': 'Request body must be a JSON object'}), 400
    args = data.get('args', [])
    if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
        return jsonify({'error': 'args must be a list of strings'}), 400
    timeout = data.get('timeout', 300)
    if not _is_real_number(timeout) or not 0 < timeout <= _MAX_RUN_TIMEOUT_SEC:
        return jsonify({'error': f'timeout must be in (0, {_MAX_RUN_TIMEOUT_SEC}]'}), 400
    try:
        result = registry.run_command(name, args, timeout=float(timeout), capture=True)
    except subprocess.TimeoutExpired:
        return jsonify({'error': f'{name} exceeded timeout of {timeout}s'}), 504
    logger.info("API ran %s -> %s", name, result['returncode'])
    return jsonify(result), 200


@app.route('/api/v1/datasets', methods=['GET'])
def list_datasets():
    """Observational data library; ?verify=true re-hashes files (read-only)."""
    verify = request.args.get('verify', 'false').lower() in ('1', 'true', 'yes')
    return jsonify({'datasets': registry.dataset_status(verify=verify)})


@app.route('/api/v1/simulate', methods=['POST'])
def simulate():
    """Run a simulation.

    Expected JSON payload
    ---------------------
    n        : int   — total dimensions (spatial coordinates on M^D)
    weights  : list  — one weight per dimension
    X_grid   : list of lists — one grid per dimension
    k, alpha, C0 : float (optional, default 1.0)
    """
    client_ip = request.remote_addr or '127.0.0.1'
    if not _check_rate_limit(client_ip):
        logger.warning("Rate limit exceeded for IP: %s", client_ip)
        return jsonify({'error': 'Rate limit exceeded (max 120 req/min). Please throttle requests.'}), 429

    try:
        if not request.is_json:
            return jsonify({'error': 'Request body must be valid JSON'}), 400

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'error': 'Request body must be valid JSON'}), 400

        n, weights, X_grid, k, alpha, C0 = _validate_and_parse_payload(data)
        M = run_simulation(n, weights, X_grid, k, alpha, C0)

        logger.info("Simulation complete — shape %s", M.shape)
        return jsonify({'M': M.tolist()})

    except (ValueError, TypeError, KeyError) as exc:
        logger.warning("Bad request: %s", exc)
        return jsonify({'error': str(exc)}), 400
    except Exception:
        logger.exception("Internal error during simulation")
        return jsonify({'error': 'Internal server error'}), 500


# Backward-compatible route (no version prefix)
@app.route('/simulate', methods=['POST'])
def simulate_legacy():
    """Legacy endpoint — forwards to /api/v1/simulate."""
    return simulate()


@app.route('/visualizer', methods=['GET'])
def serve_visualizer():
    """Serve the interactive HTML5/WebGL multidimensional dashboard."""
    from pathlib import Path
    vis_file = Path(__file__).resolve().parent.parent / "tools" / "interactive_visualizer.html"
    if vis_file.is_file():
        return vis_file.read_text(encoding="utf-8"), 200, {"Content-Type": "text/html; charset=utf-8"}
    return jsonify({"error": "Visualizer file not found"}), 404


if __name__ == '__main__':
    app.run(debug=False)
