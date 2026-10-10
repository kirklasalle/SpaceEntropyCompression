"""Re-run real-data analyses in an isolated workspace and compare golden JSON results."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import Any
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RTOL = 1e-10
OPTIMIZER_RTOL = 1e-3
BULGE_OPTIMIZER_RTOL = 1e-2
REFERENCE_SOURCE_KIND = "reference_or_archive_page_not_measurement_table"


@dataclass(frozen=True)
class GoldenCase:
    command: str
    script: str
    output: str
    args: tuple[str, ...] = ()
    ignored_paths: tuple[str, ...] = ()
    requires: tuple[str, ...] = ()
    rtol: float = DEFAULT_RTOL
    rtol_overrides: tuple[tuple[str, float], ...] = ()
    atol_overrides: tuple[tuple[str, float], ...] = ()


CASES = (
    GoldenCase(
        "sparc-real-analysis",
        "emergent_matter_model/sparc_real_analysis.py",
        "results/sparc_real_analysis.json",
        ("--no-figures",),
        requires=("data/external/sparc/Rotmod_LTG.zip",),
        rtol_overrides=(
            ("isothermal_halo.bic", 1e-7),
            ("isothermal_halo.chi2", 1e-7),
        ),
    ),
    GoldenCase(
        "sparc-marginalized-a0",
        "emergent_matter_model/sparc_marginalized_a0.py",
        "results/sparc_marginalized_a0.json",
        ("--no-figures",),
        requires=("data/external/sparc/Rotmod_LTG.zip",),
        rtol=OPTIMIZER_RTOL,
    ),
    GoldenCase(
        "sparc-tension-diagnostics",
        "emergent_matter_model/sparc_tension_diagnostics.py",
        "results/sparc_tension_diagnostics.json",
        ("--no-figures",),
        requires=("data/external/sparc/Rotmod_LTG.zip",),
        rtol=OPTIMIZER_RTOL,
    ),
    GoldenCase(
        "sparc-bulge-test",
        "emergent_matter_model/sparc_bulge_test.py",
        "results/sparc_bulge_test.json",
        ("--no-figures",),
        requires=("data/external/sparc/Rotmod_LTG.zip",),
        rtol=BULGE_OPTIMIZER_RTOL,
    ),
    GoldenCase(
        "fit-pantheon-covariance",
        "tools/fit_pantheon_real_covariance.py",
        "results/real_data_followup/pantheon_baseline.json",
        ignored_paths=("generated_utc", "python", "numpy"),
        requires=(
            "data/external/Pantheon+SH0ES.dat.txt",
            "data/external/Pantheon+SH0ES_STAT+SYS.cov.txt",
        ),
        rtol=1e-7,
        atol_overrides=(("integration_check_absolute_delta_chi2", 1e-11),),
    ),
    GoldenCase(
        "sparc-profile-validation",
        "tools/run_sparc_profile_validation.py",
        "results/real_data_v1/sparc_profile_validation.json",
        ignored_paths=(
            "generated_utc",
            "python",
            "numpy",
            "scipy",
            "command",
            "revision",
            "dirty",
            "source_sha256",
            "inputs.sparc/Rotmod_LTG.zip.retrieved_utc",
            "inputs.sparc/SPARC_Lelli2016c.mrt.retrieved_utc",
        ),
        requires=("data/external/sparc/Rotmod_LTG.zip",),
        rtol=OPTIMIZER_RTOL,
    ),
    GoldenCase(
        "sparc-influence",
        "tools/check_sparc_influence.py",
        "results/real_data_v1/sparc_influence_crosscheck.json",
        ignored_paths=("parent_sha256", "checker_sha256"),
        requires=("data/external/sparc/Rotmod_LTG.zip",),
        rtol=OPTIMIZER_RTOL,
    ),
    GoldenCase(
        "real-data-gauntlet",
        "tools/run_real_data_gauntlet.py",
        "results/real_data_v1/gauntlet.json",
        ignored_paths=(
            "generated_utc",
            "python",
            "profile_link_updated_utc",
            "source_sha256",
            "sparc_profile.sha256",
        ),
        requires=(
            "data/external/sparc/Rotmod_LTG.zip",
            "results/real_data_v1/sparc_profile_validation.json",
        ),
        args=("--refresh-profile-only",),
        rtol=1e-7,
    ),
)

_BY_NAME = {case.command: case for case in CASES}


class GoldenMismatch(AssertionError):
    pass


def _remove_readonly(function: Any, path: str, _error: Any) -> None:
    os.chmod(path, stat.S_IWRITE)
    function(path)


def _ignored(path: str, ignored_paths: set[str]) -> bool:
    return path in ignored_paths


def compare_values(
    expected: Any,
    actual: Any,
    *,
    path: str = "",
    ignored_paths: set[str] | None = None,
    rtol: float = DEFAULT_RTOL,
    rtol_overrides: dict[str, float] | None = None,
    atol_overrides: dict[str, float] | None = None,
) -> list[str]:
    """Return deterministic mismatch descriptions for two JSON-compatible values."""
    ignored_paths = ignored_paths or set()
    rtol_overrides = rtol_overrides or {}
    atol_overrides = atol_overrides or {}
    if _ignored(path, ignored_paths):
        return []
    if isinstance(expected, bool) or isinstance(actual, bool):
        return (
            []
            if expected is actual
            else [f"{path}: expected {expected!r}, got {actual!r}"]
        )
    if isinstance(expected, int) and isinstance(actual, int):
        return (
            [] if expected == actual else [f"{path}: expected {expected}, got {actual}"]
        )
    if (
        isinstance(expected, (int, float))
        and isinstance(actual, (int, float))
        and not isinstance(expected, bool)
        and not isinstance(actual, bool)
    ):
        if not math.isfinite(float(expected)) or not math.isfinite(float(actual)):
            return [f"{path}: non-finite numeric value"]
        path_rtol = rtol_overrides.get(path, rtol)
        path_atol = atol_overrides.get(path, 0.0)
        if math.isclose(
            float(expected),
            float(actual),
            rel_tol=path_rtol,
            abs_tol=path_atol,
        ):
            return []
        return [
            (
                f"{path}: expected {expected!r}, got {actual!r} "
                f"(rtol={path_rtol:g}, atol={path_atol:g})"
            )
        ]
    if isinstance(expected, dict) and isinstance(actual, dict):
        errors: list[str] = []
        expected_keys = {
            key
            for key in expected
            if not _ignored(f"{path}.{key}".lstrip("."), ignored_paths)
        }
        actual_keys = {
            key
            for key in actual
            if not _ignored(f"{path}.{key}".lstrip("."), ignored_paths)
        }
        if expected_keys != actual_keys:
            missing = sorted(expected_keys - actual_keys)
            extra = sorted(actual_keys - expected_keys)
            errors.append(
                f"{path or '<root>'}: missing keys={missing}, extra keys={extra}"
            )
        for key in sorted(expected_keys & actual_keys):
            child = f"{path}.{key}".lstrip(".")
            errors.extend(
                compare_values(
                    expected[key],
                    actual[key],
                    path=child,
                    ignored_paths=ignored_paths,
                    rtol=rtol,
                    rtol_overrides=rtol_overrides,
                    atol_overrides=atol_overrides,
                )
            )
        return errors
    if isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            return [f"{path}: expected {len(expected)} items, got {len(actual)}"]
        errors = []
        for index, (expected_item, actual_item) in enumerate(zip(expected, actual)):
            errors.extend(
                compare_values(
                    expected_item,
                    actual_item,
                    path=f"{path}[{index}]",
                    ignored_paths=ignored_paths,
                    rtol=rtol,
                    rtol_overrides=rtol_overrides,
                    atol_overrides=atol_overrides,
                )
            )
        return errors
    if type(expected) is not type(actual):
        return [
            f"{path}: expected type {type(expected).__name__}, got {type(actual).__name__}"
        ]
    return (
        [] if expected == actual else [f"{path}: expected {expected!r}, got {actual!r}"]
    )


def compare_json(expected_path: Path, actual_path: Path, case: GoldenCase) -> None:
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    actual = json.loads(actual_path.read_text(encoding="utf-8"))
    errors = compare_values(
        expected,
        actual,
        ignored_paths=set(case.ignored_paths),
        rtol=case.rtol,
        rtol_overrides=dict(case.rtol_overrides),
        atol_overrides=dict(case.atol_overrides),
    )
    if errors:
        shown = "\n".join(f"  - {error}" for error in errors[:50])
        suffix = f"\n  ... {len(errors) - 50} more" if len(errors) > 50 else ""
        raise GoldenMismatch(f"{case.command} changed:\n{shown}{suffix}")


def _copy_workspace(destination: Path) -> None:
    for relative in ("emergent_matter_model", "tools", "data", "results"):
        source = ROOT / relative
        if not source.exists():
            continue
        shutil.copytree(
            source,
            destination / relative,
            ignore=shutil.ignore_patterns(
                ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"
            ),
        )
    subprocess.run(
        ("git", "init", "--quiet"),
        cwd=destination,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ("git", "config", "user.email", "golden-runner@invalid.local"),
        cwd=destination,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ("git", "config", "user.name", "EMRF Golden Runner"),
        cwd=destination,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        (
            "git",
            "commit",
            "--allow-empty",
            "--quiet",
            "-m",
            "isolated golden workspace",
        ),
        cwd=destination,
        check=True,
        capture_output=True,
        text=True,
    )


def _serialized_path(root: Path, value: str) -> Path:
    return root.joinpath(*PureWindowsPath(value).parts)


def _hydrate_gauntlet_sources(workspace: Path) -> None:
    manifest_path = ROOT / "results" / "real_data_v1" / "gauntlet.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for record in manifest["source_records"]:
        if record["kind"] == REFERENCE_SOURCE_KIND:
            continue
        destination = _serialized_path(workspace, record["file"])
        downloaded = False
        if destination.is_file():
            raw = destination.read_bytes()
        else:
            request = Request(
                record["url"], headers={"User-Agent": "EMRF-real-data-audit/1.0"}
            )
            with urlopen(request, timeout=300) as response:
                raw = response.read()
            downloaded = True
        if len(raw) != record["bytes"]:
            raise RuntimeError(
                f"Pinned gauntlet source has wrong size: {record['file']} "
                f"(expected {record['bytes']}, got {len(raw)})"
            )
        digest = hashlib.sha256(raw).hexdigest()
        if digest != record["sha256"]:
            raise RuntimeError(
                f"Pinned gauntlet source changed: {record['url']} "
                f"(expected {record['sha256']}, got {digest})"
            )
        if downloaded:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(raw)


def _verify_gauntlet_case(case: GoldenCase, workspace: Path) -> None:
    original_sys_path = sys.path.copy()
    sys.path.insert(0, str(ROOT))
    try:
        from tools import run_real_data_gauntlet as gauntlet
    finally:
        sys.path[:] = original_sys_path

    expected = json.loads((ROOT / case.output).read_text(encoding="utf-8"))
    profile = json.loads(
        (workspace / "results" / "real_data_v1" / "sparc_profile_validation.json").read_text(
            encoding="utf-8"
        )
    )
    if not profile.get("complete") or not profile.get("numerically_verified"):
        raise GoldenMismatch("Fresh SPARC profile is incomplete or unverified")
    actual_desi = gauntlet.desi_baseline(
        workspace / "data" / "external" / "real_data_v1"
    )
    errors = compare_values(
        expected["desi_baseline"], actual_desi, rtol=case.rtol
    )
    if errors:
        shown = "\n".join(f"  - {error}" for error in errors)
        raise GoldenMismatch(f"{case.command} DESI baseline changed:\n{shown}")


def _run_case(case: GoldenCase, workspace: Path) -> None:
    if case.command == "real-data-gauntlet":
        _hydrate_gauntlet_sources(workspace)
    missing = [
        relative for relative in case.requires if not (workspace / relative).is_file()
    ]
    if missing:
        joined = ", ".join(missing)
        raise FileNotFoundError(
            f"{case.command} is missing required input(s): {joined}. "
            "Fetch and verify the real datasets before running the golden suite."
        )
    if case.command == "real-data-gauntlet":
        _verify_gauntlet_case(case, workspace)
        return
    env = os.environ.copy()
    env["MPLBACKEND"] = "Agg"
    env["PYTHONPATH"] = os.pathsep.join(
        (str(workspace / "emergent_matter_model"), str(workspace))
    )
    command = [sys.executable, case.script, *case.args]
    completed = subprocess.run(
        command,
        cwd=workspace,
        env=env,
        text=True,
        capture_output=True,
        timeout=3600,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(
            f"{case.command} failed with exit code {completed.returncode}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    compare_json(ROOT / case.output, workspace / case.output, case)


def run(selected: list[str], keep_workspace: bool = False) -> Path | None:
    unknown = sorted(set(selected) - _BY_NAME.keys())
    if unknown:
        raise KeyError(f"Unknown golden case(s): {', '.join(unknown)}")
    workspace_root = ROOT / ".golden-workspaces"
    workspace_root.mkdir(exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix="emrf-golden-", dir=workspace_root))
    try:
        _copy_workspace(temporary)
        for name in selected:
            print(f"[golden] {name}", flush=True)
            _run_case(_BY_NAME[name], temporary)
        print(f"Golden results match ({len(selected)} pipelines).")
        if keep_workspace:
            print(f"Kept isolated workspace: {temporary}")
            return temporary
        return None
    finally:
        if not keep_workspace:
            try:
                shutil.rmtree(temporary, onerror=_remove_readonly)
            except OSError as exc:
                raise RuntimeError(
                    f"Failed to remove isolated golden workspace: {temporary}"
                ) from exc
            try:
                workspace_root.rmdir()
            except OSError:
                pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cases", nargs="*", metavar="CASE")
    parser.add_argument(
        "--all", action="store_true", help="run all real-data golden cases"
    )
    parser.add_argument(
        "--list", action="store_true", help="list cases without running them"
    )
    parser.add_argument("--keep-workspace", action="store_true")
    args = parser.parse_args()
    if args.list:
        for case in CASES:
            print(f"{case.command:28s} {case.output}")
        return 0
    selected = list(_BY_NAME) if args.all else args.cases
    if not selected:
        parser.error("select one or more cases, or use --all")
    try:
        run(selected, keep_workspace=args.keep_workspace)
    except (FileNotFoundError, GoldenMismatch, KeyError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
