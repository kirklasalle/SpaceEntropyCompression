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
from emrf_sdk_access import EMRFClient, RunRequest
from emrf_version import API_VERSION, __version__
from model import EmergentMatterModel

# Remote execution of registered programs is disabled unless explicitly enabled.
RUN_ENV_FLAG = "EMRF_API_ALLOW_RUN"
DATA_WRITE_ENV_FLAG = "EMRF_API_ALLOW_DATA_WRITE"
PREDICTION_WRITE_ENV_FLAG = "EMRF_API_ALLOW_PREDICTION_WRITE"
_MAX_RUN_TIMEOUT_SEC = 600.0

app = Flask(__name__)
CORS(app)
sdk = EMRFClient()

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


def _data_library():
    from emrf_data_access import data_library

    return data_library()


def _run_store():
    from emrf_run_access import run_store

    return run_store()


def _public_record(record):
    from emrf_run_access import public_record

    return public_record(record)


def _run_write_denied():
    if os.environ.get(RUN_ENV_FLAG) == "1":
        return None
    return jsonify({
        'error': f'Command execution is disabled. Set {RUN_ENV_FLAG}=1 '
                 'on a trusted host to enable it.'
    }), 403


def _run_error(exc: Exception):
    from emrf_run_access import run_errors

    errors = run_errors()
    IntegrityError = errors.IntegrityError
    StorageError = errors.StorageError
    if isinstance(exc, KeyError):
        return jsonify({'error': str(exc)}), 404
    if isinstance(exc, (ValueError, TypeError)):
        return jsonify({'error': str(exc)}), 400
    if isinstance(exc, IntegrityError):
        return jsonify({'error': str(exc)}), 409
    if isinstance(exc, StorageError):
        logger.exception("Run-store operation failed")
        return jsonify({'error': 'Run-store operation failed'}), 500
    logger.exception("Run operation failed")
    return jsonify({'error': 'Run operation failed'}), 500


def _data_write_denied():
    if os.environ.get(DATA_WRITE_ENV_FLAG) == "1":
        return None
    return jsonify({
        'error': f'Data mutation is disabled. Set {DATA_WRITE_ENV_FLAG}=1 '
                 'on a trusted host to enable it.'
    }), 403


def _json_object() -> dict[str, Any]:
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("Request body must be a JSON object")
    return data


def _required_json_text(data: dict[str, Any], field: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text")
    return value


def _data_error(exc: Exception):
    from emrf_data_access import data_errors

    errors = data_errors()
    AcquisitionError = errors.AcquisitionError
    IntegrityError = errors.IntegrityError

    if isinstance(exc, KeyError):
        return jsonify({'error': str(exc)}), 404
    if isinstance(exc, (ValueError, TypeError)):
        return jsonify({'error': str(exc)}), 400
    if isinstance(exc, FileNotFoundError):
        return jsonify({'error': str(exc)}), 404
    if isinstance(exc, IntegrityError):
        return jsonify({'error': str(exc)}), 409
    if isinstance(exc, AcquisitionError):
        return jsonify({'error': str(exc)}), 502
    logger.exception("Data-library operation failed")
    return jsonify({'error': 'Data-library operation failed'}), 500


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


@app.route('/api/v1/verification/physics', methods=['GET'])
def verify_physics():
    """Run read-only foundational physics known-limit checks."""
    from emrf_physics_access import known_limit_report

    report = known_limit_report()
    return jsonify(report), 200 if report["all_passed"] else 500


@app.route('/api/v1/verification/engines', methods=['GET'])
def verify_engines():
    """Run remaining deterministic and synthetic engine checks."""
    from emrf_validation_access import engine_validation_report

    report = engine_validation_report()
    return jsonify(report), 200 if report["all_passed"] else 500


@app.route('/api/v1/verification/inference', methods=['GET'])
def verify_inference():
    """Run deterministic synthetic inference calibration checks."""
    from emrf_validation_access import inference_validation_report

    report = inference_validation_report()
    return jsonify(report), 200 if report["all_passed"] else 500


@app.route('/api/v1/predictions/commit', methods=['POST'])
def commit_prediction():
    """Commit a prediction digest without retaining prediction content."""
    if os.environ.get(PREDICTION_WRITE_ENV_FLAG) != "1":
        return jsonify({
            'error': f'Prediction writes are disabled. Set {PREDICTION_WRITE_ENV_FLAG}=1 '
                     'on a trusted host to enable them.'
        }), 403
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "prediction" not in data or "label" not in data:
        return jsonify({'error': 'JSON body requires label and prediction'}), 400
    try:
        from emrf_prediction_access import commit_json_prediction

        return jsonify(commit_json_prediction(data["prediction"], label=data["label"])), 201
    except (TypeError, ValueError, OSError) as exc:
        return jsonify({'error': str(exc)}), 400


@app.route('/api/v1/predictions/<commitment_id>', methods=['GET'])
def prediction_commitment(commitment_id: str):
    """Return public metadata for a prediction commitment."""
    try:
        from emrf_prediction_access import get_commitment

        return jsonify(get_commitment(commitment_id))
    except KeyError as exc:
        return jsonify({'error': exc.args[0]}), 404
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400


@app.route('/api/v1/predictions/<commitment_id>/verify', methods=['POST'])
def verify_prediction(commitment_id: str):
    """Verify a revealed JSON prediction against an immutable commitment."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "prediction" not in data:
        return jsonify({'error': 'JSON body requires prediction'}), 400
    try:
        from emrf_prediction_access import verify_json_prediction

        report = verify_json_prediction(commitment_id, data["prediction"])
        return jsonify(report), 200 if report["matches"] else 409
    except KeyError as exc:
        return jsonify({'error': exc.args[0]}), 404
    except (TypeError, ValueError) as exc:
        return jsonify({'error': str(exc)}), 400


@app.route('/api/v1/commands', methods=['GET'])
def list_commands():
    category = request.args.get('category')
    try:
        commands = sdk.list_commands(category)
    except ValueError as exc:
        return jsonify({'error': str(exc),
                        'categories': list(registry.CATEGORIES)}), 400
    return jsonify({'commands': commands.to_dict()["commands"],
                    'run_enabled': os.environ.get(RUN_ENV_FLAG) == '1'})


@app.route('/api/v1/commands/<name>', methods=['GET'])
def get_command(name: str):
    try:
        command = sdk.get_command(name)
    except KeyError as exc:
        return jsonify({'error': exc.args[0]}), 404
    return jsonify(command.to_dict())


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
        cmd = sdk.get_command(name)
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
        result = sdk.run(
            RunRequest(
                command=name,
                args=tuple(args),
                timeout=float(timeout),
            ),
            capture=True,
        )
    except subprocess.TimeoutExpired:
        return jsonify({'error': f'{name} exceeded timeout of {timeout}s'}), 504
    logger.info("API ran %s -> %s", name, result.returncode)
    return jsonify(result.to_dict()), 200


@app.route('/api/v1/runs', methods=['GET'])
def list_runs():
    try:
        limit = request.args.get('limit', 50, type=int)
        return jsonify({
            'runs': [_public_record(record) for record in _run_store().list(limit=limit)]
        })
    except Exception as exc:
        return _run_error(exc)


@app.route('/api/v1/runs/<run_id>', methods=['GET'])
def get_run(run_id: str):
    try:
        return jsonify(_public_record(_run_store().get(run_id)))
    except Exception as exc:
        return _run_error(exc)


@app.route('/api/v1/runs/<run_id>/resume', methods=['POST'])
def resume_run(run_id: str):
    if denied := _run_write_denied():
        return denied
    try:
        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            raise ValueError("Request body must be a JSON object")
        timeout = data.get('timeout')
        if timeout is not None and (
            not _is_real_number(timeout) or not 0 < timeout <= _MAX_RUN_TIMEOUT_SEC
        ):
            raise ValueError(f"timeout must be in (0, {_MAX_RUN_TIMEOUT_SEC}]")
        record = _run_store().get(run_id)
        command = registry.get_command(record.command)
        if command.gui or command.category == 'service':
            raise ValueError(
                f"{record.command} is interactive or a service and cannot run via API"
            )
        result = registry.resume_run(
            run_id,
            timeout=None if timeout is None else float(timeout),
            capture=True,
        )
        return jsonify(result)
    except subprocess.TimeoutExpired as exc:
        return jsonify({
            'error': 'Resumed command exceeded its timeout',
            'run_id': getattr(exc, 'run_id', run_id),
        }), 504
    except Exception as exc:
        return _run_error(exc)


@app.route('/api/v1/jobs', methods=['POST'])
def submit_job():
    if denied := _run_write_denied():
        return denied
    try:
        data = _json_object()
        name = _required_json_text(data, 'command')
        command = registry.get_command(name)
        if command.gui or command.category == 'service':
            raise ValueError(f"{name} is interactive or a service and cannot run as a job")
        args = data.get('args', [])
        if not isinstance(args, list) or not all(isinstance(arg, str) for arg in args):
            raise ValueError("args must be a list of strings")
        record = _run_store().enqueue(
            name,
            args,
            timeout_seconds=data.get('timeout'),
            evidence_class=data.get('evidence_class', 'software'),
            max_attempts=data.get('max_attempts', 1),
        )
        return jsonify(_public_record(record)), 202
    except Exception as exc:
        return _run_error(exc)


@app.route('/api/v1/jobs', methods=['GET'])
def list_jobs():
    try:
        limit = request.args.get('limit', 50, type=int)
        return jsonify({
            'jobs': [
                _public_record(record) for record in _run_store().list_jobs(limit=limit)
            ]
        })
    except Exception as exc:
        return _run_error(exc)


@app.route('/api/v1/jobs/<job_id>', methods=['GET'])
def get_job(job_id: str):
    try:
        return jsonify(_public_record(_run_store().get_job(job_id)))
    except Exception as exc:
        return _run_error(exc)


@app.route('/api/v1/jobs/<job_id>/cancel', methods=['POST'])
def cancel_job(job_id: str):
    if denied := _run_write_denied():
        return denied
    try:
        return jsonify(_public_record(_run_store().cancel_job(job_id)))
    except Exception as exc:
        return _run_error(exc)


@app.route('/api/v1/datasets', methods=['GET'])
def list_datasets():
    """Observational data library; ?verify=true re-hashes files (read-only)."""
    verify = request.args.get('verify', 'false').lower() in ('1', 'true', 'yes')
    try:
        return jsonify({'datasets': _data_library().catalog_status(verify=verify)})
    except Exception as exc:
        return _data_error(exc)


@app.route('/api/v1/datasets/<dataset_id>', methods=['GET'])
def get_dataset(dataset_id: str):
    verify = request.args.get('verify', 'false').lower() in ('1', 'true', 'yes')
    try:
        return jsonify(_data_library().info(dataset_id, verify=verify))
    except Exception as exc:
        return _data_error(exc)


@app.route('/api/v1/datasets/<dataset_id>/import', methods=['POST'])
def import_dataset(dataset_id: str):
    if denied := _data_write_denied():
        return denied
    try:
        data = _json_object()
        result = _data_library().import_dataset(
            dataset_id,
            logical_name=data.get('logical_name'),
            source=data.get('source'),
        )
        return jsonify({'holdings': result}), 201
    except Exception as exc:
        return _data_error(exc)


@app.route('/api/v1/datasets/<dataset_id>/fetch', methods=['POST'])
def fetch_dataset(dataset_id: str):
    if denied := _data_write_denied():
        return denied
    try:
        data = _json_object()
        result = _data_library().fetch_dataset(
            dataset_id,
            logical_name=data.get('logical_name'),
            retries=data.get('retries', 3),
            timeout=data.get('timeout', 180.0),
        )
        return jsonify({'holdings': result}), 201
    except Exception as exc:
        return _data_error(exc)


@app.route('/api/v1/datasets/verify', methods=['POST'])
def verify_datasets():
    try:
        result = _data_library().verify()
        return jsonify(result), 200 if result['healthy'] else 409
    except Exception as exc:
        return _data_error(exc)


@app.route('/api/v1/data/backups', methods=['POST'])
def create_data_backup():
    if denied := _data_write_denied():
        return denied
    try:
        data = _json_object()
        destination = _required_json_text(data, 'destination')
        return jsonify(_data_library().create_backup(destination)), 201
    except Exception as exc:
        return _data_error(exc)


@app.route('/api/v1/data/backups/offsite', methods=['POST'])
def create_offsite_data_backup():
    if denied := _data_write_denied():
        return denied
    try:
        data = _json_object()
        destination_root = data.get('destination_root')
        if destination_root is not None and (
            not isinstance(destination_root, str) or not destination_root.strip()
        ):
            raise ValueError("destination_root must be non-empty text")
        return jsonify(
            _data_library().create_offsite_backup(destination_root)
        ), 201
    except Exception as exc:
        return _data_error(exc)


@app.route('/api/v1/data/backups/verify', methods=['POST'])
def verify_data_backup():
    if denied := _data_write_denied():
        return denied
    try:
        data = _json_object()
        source = _required_json_text(data, 'source')
        return jsonify(_data_library().verify_backup(source))
    except Exception as exc:
        return _data_error(exc)


@app.route('/api/v1/data/restores', methods=['POST'])
def restore_data_backup():
    if denied := _data_write_denied():
        return denied
    try:
        data = _json_object()
        source = _required_json_text(data, 'source')
        return jsonify(_data_library().restore_backup(source))
    except Exception as exc:
        return _data_error(exc)


@app.route('/api/v1/data/restore-drills', methods=['POST'])
def run_data_restore_drill():
    if denied := _data_write_denied():
        return denied
    try:
        data = _json_object()
        receipt = data.get('receipt')
        workspace = data.get('workspace')
        for field, value in (("receipt", receipt), ("workspace", workspace)):
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{field} must be non-empty text")
        return jsonify(
            _data_library().run_restore_drill(
                receipt=receipt,
                workspace=workspace,
            )
        )
    except Exception as exc:
        return _data_error(exc)


@app.route('/api/v1/data/gc', methods=['POST'])
def garbage_collect_data():
    try:
        data = _json_object()
        execute = data.get('execute', False)
        if not isinstance(execute, bool):
            raise ValueError("execute must be a boolean")
        if execute:
            denied = _data_write_denied()
            if denied:
                return denied
        return jsonify(_data_library().garbage_collect(execute=execute))
    except Exception as exc:
        return _data_error(exc)


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
        return jsonify({
            'error': 'Rate limit exceeded (max 120 req/min). Please throttle requests.'
        }), 429

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
        return (
            vis_file.read_text(encoding="utf-8"),
            200,
            {"Content-Type": "text/html; charset=utf-8"},
        )
    return jsonify({"error": "Visualizer file not found"}), 404


if __name__ == '__main__':
    app.run(debug=False)
