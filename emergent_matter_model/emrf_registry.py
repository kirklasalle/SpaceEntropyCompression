"""Registry of every runnable EMRF program, shared by the CLI and the REST API.

Each entry wraps an existing script without changing it, so legacy invocations
(``python emergent_matter_model/fit_sparc.py ...``) keep working unchanged.
``test_emrf_registry.py`` fails if a runnable script is added but not registered.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import importlib.util
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    from emrf_paths import app_root, data_root, project_root, resolve_data_path
    from emrf_version import API_VERSION, __version__
except ModuleNotFoundError:  # package-qualified legacy import
    from emergent_matter_model.emrf_paths import (
        app_root,
        data_root,
        project_root,
        resolve_data_path,
    )
    from emergent_matter_model.emrf_version import API_VERSION, __version__

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = app_root()
PROJECT_ROOT = project_root()
EXTERNAL_DIR = data_root() / "external"
MANIFEST = EXTERNAL_DIR / "download_manifest.json"

CATEGORIES = (
    "data", "analysis", "stress-test", "figures", "visualization", "service", "audit", "release",
)


@dataclass(frozen=True)
class Command:
    name: str
    script: str
    category: str
    summary: str
    network: bool = False
    gui: bool = False

    @property
    def path(self) -> Path:
        return REPO_ROOT / self.script

    @property
    def module(self) -> str | None:
        path = Path(self.script)
        if path.parts and path.parts[0] == "emergent_matter_model":
            return path.stem
        return None

    @property
    def source_only(self) -> bool:
        return self.module is None

    @property
    def available(self) -> bool:
        if self.path.is_file():
            return True
        return self.module is not None and importlib.util.find_spec(self.module) is not None


_M = "emergent_matter_model/"
_T = "tools/"

COMMANDS: tuple[Command, ...] = (
    # data acquisition
    Command("fetch-real-data", _M + "fetch_real_data.py", "data",
            "Download/verify official public datasets (SPARC) with SHA-256 provenance",
            network=True),
    Command("fetch-sparc", _M + "fetch_sparc.py", "data", "SPARC catalog ingestion and management"),
    # real-data and fitting analyses
    Command("sparc-real-analysis", _M + "sparc_real_analysis.py", "analysis",
            "Real-data test of a0 = cH0/2pi against SPARC"),
    Command("sparc-marginalized-a0", _M + "sparc_marginalized_a0.py", "analysis",
            "SPARC a0 test marginalizing distance and inclination"),
    Command("sparc-tension-diagnostics", _M + "sparc_tension_diagnostics.py", "analysis",
            "Gas- vs star-dominated a0 disagreement diagnostics"),
    Command("sparc-bulge-test", _M + "sparc_bulge_test.py", "analysis",
            "Bulge mass-to-light test of a0 universality"),
    Command("fit-sparc", _M + "fit_sparc.py", "analysis", "SPARC rotation-curve evaluation engine"),
    Command("fit-jwst", _M + "fit_jwst.py", "analysis", "JWST high-z kinematics evaluation engine"),
    Command("fit-astrometry", _M + "fit_astrometry.py", "analysis",
            "Astrometric orbit fitting and Bayesian model comparison"),
    Command("fit-pantheon-covariance", _T + "fit_pantheon_real_covariance.py", "analysis",
            "Full-covariance Pantheon+ flat-LCDM baseline"),
    Command("sparc-profile-validation", _T + "run_sparc_profile_validation.py", "analysis",
            "SPARC four-law profile validation"),
    Command("sparc-influence", _T + "check_sparc_influence.py", "analysis",
            "SPARC influence (leave-one-out) cross-check"),
    Command("real-data-gauntlet", _T + "run_real_data_gauntlet.py", "analysis",
            "Real-data regime gauntlet"),
    Command("compare-schwarzschild", _M + "compare_schwarzschild.py", "analysis",
            "Schwarzschild curvature consistency check"),
    Command("lensing", _M + "lensing_engine.py", "analysis",
            "Lensing and geodesic deflection engine"),
    # stress tests
    Command("stress-blind-challenge", _M + "stress_test_blind_challenge.py", "stress-test",
            "Synthetic adversarial blind challenge"),
    Command("stress-cmb-peaks", _M + "stress_test_cmb_peaks.py", "stress-test",
            "CMB third acoustic peak harness"),
    Command("stress-cosmology-expansion", _M + "stress_test_cosmology_expansion.py", "stress-test",
            "Late-time expansion harness"),
    Command("stress-equivalence-principle", _M + "stress_test_equivalence_principle.py",
            "stress-test", "Equivalence principle / MICROSCOPE bounds"),
    Command("stress-galaxy-scatter", _M + "stress_test_galaxy_scatter.py", "stress-test",
            "RAR scatter and noise injection"),
    Command("stress-gw-speed", _M + "stress_test_gw_speed.py", "stress-test",
            "GW170817 gravitational-wave speed bound"),
    Command("stress-solar-system", _M + "stress_test_solar_system.py", "stress-test",
            "Solar-system precision / Cassini screening"),
    Command("stress-stability-ghosts", _M + "stress_test_stability_ghosts.py", "stress-test",
            "Hamiltonian ghost / Ostrogradsky stability"),
    Command("stress-wide-binaries", _M + "stress_test_wide_binaries.py", "stress-test",
            "Gaia DR3 wide binaries / external field effect"),
    Command("bullet-cluster", _M + "bullet_cluster_stress_test.py", "stress-test",
            "Static Bullet Cluster illustration (not an observational test)"),
    # figures
    Command("figures-cosmology", _M + "plot_cosmology_figures.py", "figures",
            "Cosmology and CMB figures"),
    Command("figures-deep-perspectives", _M + "plot_deep_perspectives.py", "figures",
            "Deep-perspective stress-test figures"),
    Command("figures-extreme-rigor", _M + "plot_extreme_rigor_figures.py", "figures",
            "Extreme-rigor figures"),
    Command("figures-publication", _M + "plot_publication_figures.py", "figures",
            "Publication figures"),
    Command("figures-three-horizons", _M + "plot_three_horizons_figures.py", "figures",
            "Three Research Horizons figures"),
    # visualization
    Command("visualize", _M + "visualize.py", "visualization", "2D visualization client",
            gui=True),
    Command("viz3d", _M + "viz3d.py", "visualization", "3D Plotly visualization", gui=True),
    # services
    Command("server-dev", _M + "server.py", "service", "Flask development API server"),
    Command("server-wsgi", _M + "wsgi.py", "service", "WSGI entry point"),
    # audit / integrity
    Command("check-candidate-a", _T + "check_candidate_a_definitions.py", "audit",
            "Candidate A definition checks"),
    Command("check-compression-claims", _T + "check_compression_claims.py", "audit",
            "Compression-claims audit"),
    Command("golden-results", _T + "run_golden_results.py", "audit",
            "Re-run real-data analyses and compare golden JSON results"),
    Command("show-your-work", _T + "show_your_work_audit.py", "audit", "Show-your-work audit"),
    Command("verify-antigravity-recovery", _T + "verify_antigravity_recovery.py", "audit",
            "Verify recovered development-history evidence hashes"),
    Command("recover-antigravity-evidence", _T + "recover_antigravity_evidence.py", "audit",
            "Recover development-history evidence (requires local archive)"),
    Command("integrate-recovered-graph", _T + "integrate_recovered_graph.py", "audit",
            "Integrate recovered claims into graph memory"),
    # release / documents
    Command("build-real-data-report", _T + "build_real_data_report.py", "release",
            "Build real-data report"),
    Command("build-sparc-paper", _T + "build_sparc_paper.py", "release", "Build SPARC paper"),
    Command("build-validation-notebook", _T + "build_validation_notebook.py", "release",
            "Build validation notebook"),
    Command("package-real-data-release", _T + "package_real_data_release.py", "release",
            "Package real-data review bundle"),
)

_BY_NAME = {c.name: c for c in COMMANDS}

CORE_DEPENDENCIES = ("numpy", "scipy", "matplotlib", "Flask", "flask-cors", "requests", "plotly")
OPTIONAL_DEPENDENCIES = (
    "pytest",
    "coverage",
    "hypothesis",
    "pytest-xdist",
    "ruff",
    "mypy",
    "pre-commit",
    "gunicorn",
)


def get_command(name: str) -> Command:
    try:
        return _BY_NAME[name]
    except KeyError:
        raise KeyError(f"Unknown command: {name!r}") from None


def list_commands(category: str | None = None) -> list[dict]:
    return [
        {
            **asdict(c),
            "module": c.module,
            "source_only": c.source_only,
            "exists": c.available,
        }
        for c in COMMANDS
        if category is None or c.category == category
    ]


def run_command(
    name: str,
    args: list[str] | None = None,
    timeout: float | None = None,
    capture: bool = False,
    *,
    evidence_class: str = "software",
    inputs: dict[str, str] | None = None,
    seeds: dict[str, int] | None = None,
    resume_run_id: str | None = None,
    prepared_run_id: str | None = None,
) -> dict:
    """Run a registered script in a fresh interpreter (isolates sys.exit, globals, plots)."""
    from emrf_run_access import run_store

    cmd = get_command(name)
    args = list(args or [])
    if not all(isinstance(a, str) for a in args):
        raise TypeError("args must be a list of strings")
    if not cmd.available:
        if cmd.source_only:
            raise FileNotFoundError(
                f"{cmd.name} requires an EMRF source checkout containing {cmd.script}"
            )
        raise FileNotFoundError(f"Command target is unavailable: {cmd.script}")
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(PACKAGE_DIR), str(REPO_ROOT), env.get("PYTHONPATH", "")]
    ).rstrip(os.pathsep)
    env.setdefault("MPLBACKEND", "Agg")
    REPO_ROOT.mkdir(parents=True, exist_ok=True)
    store = run_store()
    if resume_run_id is not None and prepared_run_id is not None:
        raise ValueError("A run cannot be both prepared and resumed")
    if resume_run_id is None and prepared_run_id is None:
        record = store.create(
            name,
            args,
            evidence_class=evidence_class,
            inputs=inputs,
            seeds=seeds,
        )
        record = store.begin(record.run_id)
    elif resume_run_id is not None:
        record = store.get(resume_run_id)
        if record.command != name or record.args != tuple(args):
            raise ValueError("Resume command and arguments must match the original run")
        record = store.begin(resume_run_id, resume=True)
    else:
        record = store.get(str(prepared_run_id))
        if record.command != name or record.args != tuple(args):
            raise ValueError("Prepared command and arguments must match the run")
        record = store.begin(record.run_id)
    env["EMRF_RUN_ID"] = record.run_id
    env["EMRF_RUN_DIR"] = str(record.path)
    env["EMRF_RUN_ATTEMPT"] = str(record.attempt)
    env["EMRF_CHECKPOINT_DIR"] = str(record.path / "checkpoints")
    started = time.time()
    target = [str(cmd.path)] if cmd.path.is_file() else ["-m", str(cmd.module)]
    try:
        proc = subprocess.run(  # noqa: S603 - fixed interpreter + registered target, no shell
            [sys.executable, *target, *args],
            cwd=str(REPO_ROOT),
            env=env,
            timeout=timeout,
            capture_output=capture,
            text=True,
        )
    except subprocess.TimeoutExpired as exc:
        store.finish(
            record.run_id,
            status="timed_out",
            returncode=None,
            duration_seconds=time.time() - started,
        )
        exc.run_id = record.run_id
        raise
    except BaseException:
        store.finish(
            record.run_id,
            status="interrupted",
            returncode=None,
            duration_seconds=time.time() - started,
        )
        raise
    if capture:
        try:
            store.write_log(record.run_id, "stdout", record.attempt, proc.stdout)
            store.write_log(record.run_id, "stderr", record.attempt, proc.stderr)
        except Exception:
            store.finish(
                record.run_id,
                status="failed",
                returncode=proc.returncode,
                duration_seconds=time.time() - started,
            )
            raise
    final = store.finish(
        record.run_id,
        status="succeeded" if proc.returncode == 0 else "failed",
        returncode=proc.returncode,
        duration_seconds=time.time() - started,
    )
    result = {
        "command": name,
        "args": args,
        "returncode": proc.returncode,
        "seconds": round(final.duration_seconds or 0.0, 3),
        "run_id": final.run_id,
    }
    if capture:
        result["stdout"] = proc.stdout
        result["stderr"] = proc.stderr
    return result


def resume_run(
    run_id: str,
    *,
    timeout: float | None = None,
    capture: bool = False,
) -> dict:
    """Resume a failed, interrupted or timed-out registered command."""
    from emrf_run_access import run_store

    record = run_store().get(run_id)
    return run_command(
        record.command,
        list(record.args),
        timeout=timeout,
        capture=capture,
        evidence_class=record.evidence_class,
        inputs=record.inputs,
        seeds=record.seeds,
        resume_run_id=run_id,
    )


def run_next_job(worker_id: str, *, lease_seconds: float = 3600) -> object | None:
    """Claim and execute one queued job, returning its durable final state."""
    from emrf_run_access import run_store

    store = run_store()
    job = store.claim(worker_id, lease_seconds=lease_seconds)
    if job is None:
        return None
    try:
        command = get_command(job.command)
        if command.gui or command.category == "service":
            raise ValueError(
                f"{job.command} is interactive or a service and cannot run as a job"
            )
        run = store.create(
            job.command,
            list(job.args),
            evidence_class=job.evidence_class,
        )
        store.attach_run(job.job_id, run.run_id)
        result = run_command(
            job.command,
            list(job.args),
            timeout=job.timeout_seconds,
            capture=True,
            evidence_class=job.evidence_class,
            prepared_run_id=run.run_id,
        )
    except subprocess.TimeoutExpired:
        return store.complete_job(
            job.job_id,
            returncode=None,
            error=f"Command exceeded timeout of {job.timeout_seconds}s",
        )
    except Exception as exc:
        return store.complete_job(
            job.job_id,
            returncode=None,
            error=f"{type(exc).__name__}: {exc}",
        )
    except BaseException as exc:
        store.complete_job(
            job.job_id,
            returncode=None,
            error=f"{type(exc).__name__}: {exc}",
        )
        raise
    return store.complete_job(
        job.job_id,
        returncode=int(result["returncode"]),
        error=None if result["returncode"] == 0 else "Command returned a nonzero exit code",
    )


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _manifest_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    if path.parts and path.parts[0].lower() == "data":
        return resolve_data_path(path)
    return REPO_ROOT / path


def dataset_status(verify: bool = False) -> list[dict]:
    """List manifest-registered observational files; optionally re-hash them (read-only)."""
    if not MANIFEST.is_file():
        return []
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    out = []
    for key, entry in sorted(manifest.items()):
        path = _manifest_path(entry.get("file", ""))
        row = {
            "id": key,
            "file": entry.get("file"),
            "url": entry.get("url"),
            "citation": entry.get("citation"),
            "bytes": entry.get("bytes"),
            "sha256": entry.get("sha256"),
            "retrieved_utc": entry.get("retrieved_utc"),
            "present": path.is_file(),
        }
        if verify:
            if not path.is_file():
                row["status"] = "missing"
            elif path.stat().st_size != entry.get("bytes"):
                row["status"] = "size-mismatch"
            else:
                row["status"] = "ok" if _sha256(path) == entry.get("sha256") else "hash-mismatch"
        out.append(row)
    return out


def _dist_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def environment_report() -> dict:
    """Read-only diagnostics of interpreter, dependencies, registry, and data."""
    core = {d: _dist_version(d) for d in CORE_DEPENDENCIES}
    optional = {d: _dist_version(d) for d in OPTIONAL_DEPENDENCIES}
    missing_scripts = [c.name for c in COMMANDS if not c.available and not c.source_only]
    source_only_unavailable = [c.name for c in COMMANDS if not c.available and c.source_only]
    py_ok = sys.version_info >= (3, 10)
    return {
        "emrf_version": __version__,
        "api_version": API_VERSION,
        "python": sys.version.split()[0],
        "python_ok": py_ok,
        "executable": sys.executable,
        "platform": sys.platform,
        "core_dependencies": core,
        "optional_dependencies": optional,
        "missing_core": [d for d, v in core.items() if v is None],
        "registered_commands": len(COMMANDS),
        "missing_scripts": missing_scripts,
        "source_only_unavailable": source_only_unavailable,
        "app_root": str(REPO_ROOT),
        "data_root": str(data_root()),
        "manifest_present": MANIFEST.is_file(),
        "healthy": py_ok and not missing_scripts and all(core.values()),
    }
