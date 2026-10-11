"""Regression tests for sustainable GitHub Actions governance."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
ACTION = re.compile(
    r"^\s*(?:-\s+)?uses:\s+"
    r"(?P<name>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)?)"
    r"@(?P<sha>[0-9a-f]{40})\s+#\s+v(?P<version>\d+(?:\.\d+){0,2})$",
    re.MULTILINE,
)
APPROVED_ACTIONS = {
    "actions/attest": (
        "1e69f48acb82d1966a394da916b4c1698aa569d6",
        "4.2.2",
    ),
    "actions/checkout": (
        "3d3c42e5aac5ba805825da76410c181273ba90b1",
        "7.0.1",
    ),
    "actions/configure-pages": (
        "45bfe0192ca1faeb007ade9deae92b16b8254a0d",
        "6.0.0",
    ),
    "actions/dependency-review-action": (
        "a1d282b36b6f3519aa1f3fc636f609c47dddb294",
        "5.0.0",
    ),
    "actions/deploy-pages": (
        "368f82528645a54fb793d4d04e342629a3f51346",
        "5.0.1",
    ),
    "actions/download-artifact": (
        "9000827ccba6bdab643e8b6fd33ac0654aef8333",
        "8.0.2",
    ),
    "actions/setup-java": (
        "de7274f081f381c8f8158605e0321c36c376e2e6",
        "6.0.1",
    ),
    "actions/setup-python": (
        "5fda3b95a4ea91299a34e894583c3862153e4b97",
        "7.0.0",
    ),
    "actions/upload-artifact": (
        "cf430e030ddbb5b0abf93d22962f4752f3646cd9",
        "7.0.2",
    ),
    "actions/upload-pages-artifact": (
        "fc324d3547104276b827a68afc52ff2a11cc49c9",
        "5.0.0",
    ),
    "github/codeql-action/upload-sarif": (
        "24c54180a607b1449ed407dd24f251e4e9147c8d",
        "4.38.3",
    ),
    "ossf/scorecard-action": (
        "2d1146689b8cda280b9bc96326124645441f03bc",
        "2.4.4",
    ),
}
APPROVED_RUNNERS = {"ubuntu-24.04", "windows-2022", "${{ matrix.os }}"}


def _workflows() -> dict[str, tuple[str, dict[str, Any]]]:
    workflows: dict[str, tuple[str, dict[str, Any]]] = {}
    paths = sorted((*WORKFLOWS.glob("*.yml"), *WORKFLOWS.glob("*.yaml")))
    for path in paths:
        text = path.read_text(encoding="utf-8")
        value = yaml.load(text, Loader=yaml.BaseLoader)
        assert isinstance(value, dict), path.name
        workflows[path.name] = (text, value)
    return workflows


def _values_for_key(value: object, key: str) -> list[object]:
    results: list[object] = []
    if isinstance(value, dict):
        for child_key, child in value.items():
            if child_key == key:
                results.append(child)
            results.extend(_values_for_key(child, key))
    elif isinstance(value, list):
        for child in value:
            results.extend(_values_for_key(child, key))
    return results


def test_actions_match_approved_immutable_releases() -> None:
    observed: set[str] = set()
    for filename, (workflow, _) in _workflows().items():
        uses_lines = [line for line in workflow.splitlines() if "uses:" in line]
        matches = list(ACTION.finditer(workflow))

        assert len(matches) == len(uses_lines), filename
        for match in matches:
            name = match["name"]
            observed.add(name)
            assert name in APPROVED_ACTIONS, name
            assert (match["sha"], match["version"]) == APPROVED_ACTIONS[name], name

    assert observed == set(APPROVED_ACTIONS)


def test_runner_images_are_explicitly_approved() -> None:
    for filename, (_, workflow) in _workflows().items():
        for job_name, job in workflow["jobs"].items():
            runner = job["runs-on"]
            assert runner in APPROVED_RUNNERS, (filename, job_name, runner)
            if runner == "${{ matrix.os }}":
                matrix = job["strategy"]["matrix"]
                assert matrix["os"] == ["ubuntu-24.04", "windows-2022"], (
                    filename,
                    job_name,
                    matrix["os"],
                )


def test_ci_triggers_do_not_duplicate_pull_request_branches() -> None:
    trigger = _workflows()["ci.yml"][1]["on"]

    assert trigger == {
        "push": {"branches": ["main"]},
        "pull_request": "",
    }


def test_validation_and_publication_concurrency_is_safe() -> None:
    workflows = _workflows()
    expected = {
        "ci.yml": "true",
        "docs.yml": "false",
        "release-health.yml": "false",
        "release.yml": "false",
        "security.yml": "true",
    }

    for filename, cancel_in_progress in expected.items():
        concurrency = workflows[filename][1]["concurrency"]
        assert concurrency["cancel-in-progress"] == cancel_in_progress

    assert workflows["release.yml"][1]["concurrency"]["group"] == (
        "release-${{ github.ref }}"
    )


def test_release_health_is_read_only_and_non_publishing() -> None:
    text, workflow = _workflows()["release-health.yml"]

    assert workflow["on"] == {
        "schedule": [{"cron": "17 5 1 * *"}],
        "workflow_dispatch": {
            "inputs": {
                "tag": {
                    "description": (
                        "Published stable release tag; blank selects the latest release"
                    ),
                    "required": "false",
                    "type": "string",
                }
            }
        },
    }
    assert workflow["permissions"] == {
        "attestations": "read",
        "contents": "read",
    }

    job = workflow["jobs"]["rehearse"]
    assert "env" not in job
    steps = {step.get("name"): step for step in job["steps"] if "name" in step}
    token_steps = {
        "Resolve immutable stable release",
        "Download published release bundle",
        "Verify release provenance",
    }
    for name, step in steps.items():
        if name in token_steps:
            assert step["env"]["GH_TOKEN"] == "${{ github.token }}"
        else:
            assert "GH_TOKEN" not in step.get("env", {})
    resolver = steps["Resolve immutable stable release"]
    assert resolver["env"]["REQUESTED_TAG"] == "${{ inputs.tag }}"
    assert "${{ inputs.tag }}" not in resolver["run"]

    for prohibited in (
        "actions/attest",
        "gh api --method",
        "gh release create",
        "gh release delete",
        "gh release edit",
        "gh release upload",
        "git push",
        "git tag",
        "secrets.",
        "twine upload",
    ):
        assert prohibited not in text
