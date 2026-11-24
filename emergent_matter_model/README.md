# emergent-matter-model (EMRF)

Simulation and reproducible scientific verification framework for emergent matter from multidimensional space-entropy compression ($X \in \mathcal{M}^D$, with thermodynamic entropy $S(X,t)$ as a state functional).

## Installation

```bash
pip install emergent-matter-model
```

Recommended runtime: Python 3.10.1+ or 3.12.

## Interfaces

- **CLI:** `emrf doctor`, `emrf list`, `emrf kb validate`, `emrf simulate ...`
- **Python SDK:** `from emrf.sdk import EMRFClient`
- **REST API v2 (canonical):** `uvicorn asgi:app` serving `/api/v2/docs` (legacy Flask v1 compatibility routes remain deprecated under 1.x).

## What's New

- **November 24, 2026 hardening:** Bound Gunicorn to loopback by default, enforced HTTP payload (`1 MiB`), rate-limit, security/deprecation header, bearer-auth, path-confinement, and CLI-validation controls across Flask REST v1 (deprecated) and FastAPI REST v2; scrubbed secrets from subprocess execution and hardened observational HTTPS acquisition.
- **Concurrency & numerical fixes:** Added Win32-safe PID checks and cross-process file locking across storage, SQLite runs, backups, and recovery; added bracketed Halley/Newton–bisection Kepler solver (`e <= 0.99999`), explicit `synthetic_benchmark_not_real_epochs` / `illustrative_tautology` evidence tags, opt-in PAVA bulge regularization, and `mypy -p emrf` static type checking.
- **Runtime baseline:** Requires Python `>=3.10.1` (`3.12` recommended; `emrf doctor` warns on CPython `3.10.0` `bpo-45662`).

## Scientific Caveat

Model outputs on synthetic fixtures or conceptual toy stress tests are software verification checks, not observational confirmation. See the repository `MODEL_CARD.md` and `docs/` for empirical evidence classifications.
