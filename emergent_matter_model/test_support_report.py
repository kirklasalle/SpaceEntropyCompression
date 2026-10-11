"""Privacy, durability, SDK, and CLI tests for support reports."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

import emrf.support as support
import emrf_cli
from emrf.sdk import EMRFClient, InvalidRequestError
from emrf.support import (
    SUPPORT_REPORT_SCHEMA,
    _write_private_json,
    build_support_report,
)


def test_support_report_redacts_sensitive_surfaces(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("EMRF_API_V2_TOKEN", "must-not-appear")
    report = build_support_report(
        generated=datetime(2026, 10, 11, 12, 0, tzinfo=timezone.utc)
    )
    encoded = json.dumps(report)

    assert report["schema"] == SUPPORT_REPORT_SCHEMA
    assert report["generated_utc"] == "2026-10-11T12:00:00Z"
    assert report["privacy"] == {
        "environment_variables_included": False,
        "credentials_included": False,
        "user_paths_redacted": True,
        "run_arguments_included": False,
        "dataset_urls_included": False,
    }
    assert report["environment"]["app_root"] == "<app-root>"
    assert report["environment"]["data_root"] == "<data-root>"
    assert report["knowledge"]["graph_path"] == "<knowledge-graph>"
    assert report["knowledge"]["error_count"] == 0
    assert report["knowledge"]["error_paths"] == []
    assert "executable" not in report["environment"]
    assert "must-not-appear" not in encoded
    assert str(Path.home()) not in encoded


def test_support_report_excludes_raw_knowledge_validation_messages(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    private_value = str(tmp_path / "private-observation.fits")

    class InvalidKnowledgeStore:
        def validate(self) -> dict[str, object]:
            return {
                "valid": False,
                "schema_version": "1.0.0",
                "graph_path": private_value,
                "nodes": 1,
                "edges": 0,
                "errors": [
                    {
                        "path": "$.nodes[0].evidence[0]",
                        "message": f"{private_value!r} is not valid evidence",
                    }
                ],
            }

    monkeypatch.setattr("emrf.knowledge.KnowledgeStore", InvalidKnowledgeStore)
    report = build_support_report()
    encoded = json.dumps(report)

    assert report["knowledge"]["error_count"] == 1
    assert report["knowledge"]["error_paths"] == ["$.nodes[0].evidence[0]"]
    assert private_value not in encoded
    assert "is not valid evidence" not in encoded


def test_sdk_writes_private_atomic_report(tmp_path: Path):
    destination = tmp_path / "support.json"

    result = EMRFClient().create_support_report(str(destination))
    payload = json.loads(destination.read_text(encoding="utf-8"))

    assert result.path == str(destination)
    assert result.bytes == destination.stat().st_size
    assert result.sha256 == hashlib.sha256(destination.read_bytes()).hexdigest()
    assert payload["schema"] == SUPPORT_REPORT_SCHEMA
    assert not list(tmp_path.glob("*.part"))
    with pytest.raises(InvalidRequestError, match="already exists"):
        EMRFClient().create_support_report(str(destination))


def test_default_report_uses_user_application_root(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    monkeypatch.setattr(support, "default_app_root", lambda: tmp_path)

    result = support.create_support_report()
    path = Path(result["path"])

    assert path.parent == tmp_path / "support"
    assert path.name.startswith("emrf-doctor-")
    assert path.suffix == ".json"


def test_atomic_writer_cannot_replace_destination(tmp_path: Path):
    destination = tmp_path / "support.json"
    destination.write_text("preserve", encoding="utf-8")

    with pytest.raises(FileExistsError):
        _write_private_json(destination, {"new": "content"})

    assert destination.read_text(encoding="utf-8") == "preserve"
    assert not list(tmp_path.glob("*.part"))


def test_doctor_report_cli(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    destination = tmp_path / "doctor.json"

    class HealthyEnvironment:
        def to_dict(self) -> dict[str, bool]:
            return {"healthy": True}

    monkeypatch.setattr(
        emrf_cli.sdk,
        "environment_report",
        lambda **_kwargs: HealthyEnvironment(),
    )
    result = emrf_cli.main(["doctor", "--json", "--report", str(destination)])
    output = json.loads(capsys.readouterr().out)

    assert result == 0
    assert destination.is_file()
    assert output["healthy"] is True
    assert output["support_report"]["path"] == str(destination)
    assert output["support_report"]["sha256"] == hashlib.sha256(
        destination.read_bytes()
    ).hexdigest()


def test_writer_falls_back_when_hard_links_are_unavailable(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    destination = tmp_path / "support.json"
    monkeypatch.setattr(
        support.os,
        "link",
        lambda *_args: (_ for _ in ()).throw(OSError("hard links unsupported")),
    )

    _write_private_json(destination, {"fallback": True})

    assert json.loads(destination.read_text(encoding="utf-8")) == {"fallback": True}
    assert not list(tmp_path.glob("*.part"))
