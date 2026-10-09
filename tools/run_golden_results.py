"""Re-run real-data analyses in an isolated workspace and compare golden JSON results."""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RTOL = 1e-10


@dataclass(frozen=True)
class GoldenCase:
    command: str
    script: str
    output: str
    args: tuple[str, ...] = ()
    ignored_paths: tuple[str, ...] = ()
    requires: tuple[str, ...] = ()
    rtol: float = DEFAULT_RTOL


CASES = (
    GoldenCase(
        "sparc-real-analysis",
        "emergent_matter_model/sparc_real_analysis.py",
        "results/sparc_real_analysis.json",
        ("--no-figures",),
        requires=("data/external/sparc/Rotmod_LTG.zip",),
    ),
    GoldenCase(
        "sparc-marginalized-a0",
        "emergent_matter_model/sparc_marginalized_a0.py",
        "results/sparc_marginalized_a0.json",
        ("--no-figures",),
        requires=("data/external/sparc/Rotmod_LTG.zip",),
    ),
    GoldenCase(
        "sparc-tension-diagnostics",
        "emergent_matter_model/sparc_tension_diagnostics.py",
        "results/sparc_tension_diagnostics.json",
        ("--no-figures",),
        requires=("data/external/sparc/Rotmod_LTG.zip",),
    ),
    GoldenCase(
        "sparc-bulge-test",
        "emergent_matter_model/sparc_bulge_test.py",
        "results/sparc_bulge_test.json",
        ("--no-figures",),
        requires=("data/external/sparc/Rotmod_LTG.zip",),
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
        ),
        requires=("data/external/sparc/Rotmod_LTG.zip",),
    ),
    GoldenCase(
        "sparc-influence",
        "tools/check_sparc_influence.py",
        "results/real_data_v1/sparc_influence_crosscheck.json",
        ignored_paths=("parent_sha256", "checker_sha256"),
        requires=("data/external/sparc/Rotmod_LTG.zip",),
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
) -> list[str]:
    """Return deterministic mismatch descriptions for two JSON-compatible values."""
    ignored_paths = ignored_paths or set()
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
        if math.isclose(float(expected), float(actual), rel_tol=rtol, abs_tol=0.0):
            return []
        return [f"{path}: expected {expected!r}, got {actual!r} (rtol={rtol:g})"]
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


def _run_case(case: GoldenCase, workspace: Path) -> None:
    missing = [
        relative for relative in case.requires if not (workspace / relative).is_file()
    ]
    if missing:
        joined = ", ".join(missing)
        raise FileNotFoundError(
            f"{case.command} is missing required input(s): {joined}. "
            "Fetch and verify the real datasets before running the golden suite."
        )
    env = os.environ.copy()
    env["MPLBACKEND"] = "Agg"
    env["PYTHONPATH"] = os.pathsep.join(
        (str(workspace / "emergent_matter_model"), str(workspace))
    )
    command = [sys.executable, str(workspace / case.script), *case.args]
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
    temporary = Path(tempfile.mkdtemp(prefix="emrf-golden-"))
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
