"""Release metadata synchronization tests."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tools import validate_release_metadata as release_metadata

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate_release_metadata.py"
RELEASE_WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"


def test_release_workflow_requires_current_protected_main_commit() -> None:
    workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")

    assert 'test "$GITHUB_SHA" = "$(git rev-parse origin/main)"' in workflow
    assert "git merge-base --is-ancestor" not in workflow


def test_release_metadata_matches_v1_tag(tmp_path: Path) -> None:
    notes = tmp_path / "release-notes.md"
    result = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--tag",
            "v1.0.0",
            "--write-release-notes",
            str(notes),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert notes.read_text(encoding="utf-8").startswith("# EMRF 1.0.0\n")


def test_release_metadata_rejects_mismatched_tag() -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--tag", "v9.9.9"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "does not match canonical version v1.0.0" in result.stderr


def test_release_metadata_rejects_stale_versioned_urls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    load_yaml = release_metadata._load_yaml
    load_json = release_metadata._load_json

    def stale_yaml(path: Path) -> dict[str, object]:
        value = load_yaml(path)
        if path.name == "CITATION.cff":
            value["repository-artifact"] = (
                "https://github.com/kirklasalle/SpaceEntropyCompression/"
                "releases/tag/v0.9.1"
            )
            value["doi"] = "10.5281/zenodo.23197308"
        return value

    def stale_json(path: Path) -> dict[str, object]:
        value = load_json(path)
        if path.name == "codemeta.json":
            value["releaseNotes"] = (
                "https://github.com/kirklasalle/SpaceEntropyCompression/"
                "blob/v0.9.1/CHANGELOG.md"
            )
            value["identifier"] = "https://doi.org/10.5281/zenodo.23197308"
        if path.name == ".zenodo.json":
            value["description"] = (
                "A future deposit; historical DOI 10.5281/zenodo.23197308."
            )
        return value

    monkeypatch.setattr(release_metadata, "_load_yaml", stale_yaml)
    monkeypatch.setattr(release_metadata, "_load_json", stale_json)

    _, errors = release_metadata.validate_release_metadata()

    assert any("CITATION.cff repository-artifact" in error for error in errors)
    assert any("codemeta.json releaseNotes" in error for error in errors)
    assert any("CITATION.cff doi" in error for error in errors)
    assert any("codemeta.json identifier" in error for error in errors)
    assert any(".zenodo.json description must identify" in error for error in errors)
