"""Validate synchronized EMRF release metadata and extract release notes."""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "emergent_matter_model" / "src" / "emrf" / "_version.py"
PYPROJECT = ROOT / "emergent_matter_model" / "pyproject.toml"
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
REPOSITORY_URL = "https://github.com/kirklasalle/SpaceEntropyCompression"


def _canonical_version() -> str:
    tree = ast.parse(
        VERSION_FILE.read_text(encoding="utf-8"), filename=str(VERSION_FILE)
    )
    for statement in tree.body:
        if (
            isinstance(statement, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "__version__"
                for target in statement.targets
            )
            and isinstance(statement.value, ast.Constant)
            and isinstance(statement.value.value, str)
        ):
            return statement.value.value
    raise ValueError(f"Could not find a literal __version__ in {VERSION_FILE}")


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a YAML object")
    return value


def _release_notes(version: str) -> str:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    heading = re.compile(
        rf"^## \[{re.escape(version)}\][^\n]*\n(?P<body>.*?)(?=^## \[|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = heading.search(changelog)
    if match is None:
        raise ValueError(f"CHANGELOG.md has no [{version}] release section")
    return f"# EMRF {version}\n\n{match.group('body').strip()}\n"


def validate_release_metadata(*, tag: str | None = None) -> tuple[str, list[str]]:
    version = _canonical_version()
    errors: list[str] = []
    if SEMVER.fullmatch(version) is None:
        errors.append(f"Canonical version is not semantic: {version!r}")

    pyproject = PYPROJECT.read_text(encoding="utf-8")
    if 'dynamic = ["version"]' not in pyproject:
        errors.append("pyproject.toml must declare version as dynamic")
    if 'version = {attr = "emrf._version.__version__"}' not in pyproject:
        errors.append("pyproject.toml must read version from emrf._version.__version__")

    bridge = (ROOT / "emergent_matter_model" / "emrf_version.py").read_text(
        encoding="utf-8"
    )
    if "from emrf._version import API_VERSION, __version__" not in bridge:
        errors.append("emrf_version.py must re-export the canonical package version")

    citation = _load_yaml(ROOT / "CITATION.cff")
    codemeta = _load_json(ROOT / "codemeta.json")
    zenodo = _load_json(ROOT / ".zenodo.json")
    expected = {
        "CITATION.cff version": citation.get("version"),
        "codemeta.json softwareVersion": codemeta.get("softwareVersion"),
        ".zenodo.json version": zenodo.get("version"),
    }
    for name, value in expected.items():
        if str(value) != version:
            errors.append(f"{name} is {value!r}, expected {version!r}")

    versioned_urls = {
        "CITATION.cff repository-artifact": (
            citation.get("repository-artifact"),
            f"{REPOSITORY_URL}/releases/tag/v{version}",
        ),
        "codemeta.json releaseNotes": (
            codemeta.get("releaseNotes"),
            f"{REPOSITORY_URL}/blob/v{version}/CHANGELOG.md",
        ),
    }
    for name, (value, expected_url) in versioned_urls.items():
        if value != expected_url:
            errors.append(f"{name} is {value!r}, expected {expected_url!r}")

    release_dates = {
        "CITATION.cff date-released": citation.get("date-released"),
        "codemeta.json datePublished": codemeta.get("datePublished"),
        ".zenodo.json publication_date": zenodo.get("publication_date"),
    }
    normalized_dates = {str(value) for value in release_dates.values()}
    if len(normalized_dates) != 1 or "None" in normalized_dates:
        errors.append(f"Release dates are missing or inconsistent: {release_dates}")

    try:
        _release_notes(version)
    except ValueError as exc:
        errors.append(str(exc))

    if tag is not None and tag != f"v{version}":
        errors.append(
            f"Release tag {tag!r} does not match canonical version v{version}"
        )
    return version, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", help="require this release tag to equal vVERSION")
    parser.add_argument(
        "--write-release-notes",
        type=Path,
        help="write the canonical changelog section to this path",
    )
    args = parser.parse_args(argv)
    try:
        version, errors = validate_release_metadata(tag=args.tag)
    except (
        OSError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
        yaml.YAMLError,
    ) as exc:
        print(f"release metadata error: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"release metadata error: {error}", file=sys.stderr)
        return 1
    if args.write_release_notes is not None:
        args.write_release_notes.parent.mkdir(parents=True, exist_ok=True)
        args.write_release_notes.write_text(
            _release_notes(version),
            encoding="utf-8",
            newline="\n",
        )
    print(f"Release metadata is synchronized for EMRF {version}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
