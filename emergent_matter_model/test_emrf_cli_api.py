"""Tests for the unified CLI/API registry: completeness, CLI behaviour, API parity."""

from __future__ import annotations

import json
import re
import subprocess

import pytest

import emrf_cli
import emrf_registry as reg
import server
from emrf.runs import RunStore
from server import app

_MAIN_GUARD = re.compile(r"^if __name__ == ['\"]__main__['\"]", re.MULTILINE)
_NOT_COMMANDS = {"emrf_cli.py"}  # the CLI itself


def _runnable_scripts() -> set[str]:
    found = set()
    for folder in (reg.PACKAGE_DIR, reg.REPO_ROOT / "tools"):
        for p in folder.glob("*.py"):
            if p.name.startswith("test_") or p.name in _NOT_COMMANDS:
                continue
            if _MAIN_GUARD.search(p.read_text(encoding="utf-8", errors="ignore")):
                found.add(p.relative_to(reg.REPO_ROOT).as_posix())
    return found


def test_every_runnable_script_is_registered():
    registered = {c.script for c in reg.COMMANDS}
    assert _runnable_scripts() - registered == set()


def test_registry_entries_are_valid_and_unique():
    names = [c.name for c in reg.COMMANDS]
    assert len(names) == len(set(names))
    for c in reg.COMMANDS:
        assert c.category in reg.CATEGORIES
        assert c.path.is_file(), c.script
        assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", c.name)


def test_unknown_command_raises():
    with pytest.raises(KeyError):
        reg.get_command("does-not-exist")


def test_run_rejects_non_string_args():
    with pytest.raises(TypeError):
        reg.run_command("compare-schwarzschild", [1])  # type: ignore[list-item]


def test_registry_execution_writes_run_record(
    tmp_path, monkeypatch: pytest.MonkeyPatch
):
    store = RunStore(tmp_path)
    monkeypatch.setattr("emrf_run_access.run_store", lambda: store)

    result = reg.run_command("compare-schwarzschild", ["--help"], capture=True)
    record = store.get(result["run_id"])

    assert result["returncode"] == 0
    assert record.status == "succeeded"
    assert record.command == "compare-schwarzschild"
    assert record.args == ("--help",)
    assert (record.path / "stdout-1.txt").read_text(encoding="utf-8")


def test_registry_failed_run_can_be_resumed(
    tmp_path, monkeypatch: pytest.MonkeyPatch
):
    store = RunStore(tmp_path)
    monkeypatch.setattr("emrf_run_access.run_store", lambda: store)
    first = reg.run_command(
        "compare-schwarzschild",
        ["--not-a-real-option"],
        capture=True,
    )

    resumed = reg.resume_run(first["run_id"], capture=True)
    record = store.get(first["run_id"])

    assert first["returncode"] != 0
    assert resumed["returncode"] != 0
    assert record.status == "failed"
    assert record.attempt == 2
    assert (record.path / "stderr-1.txt").is_file()
    assert (record.path / "stderr-2.txt").is_file()


def test_registry_timeout_records_terminal_state(
    tmp_path, monkeypatch: pytest.MonkeyPatch
):
    store = RunStore(tmp_path)
    monkeypatch.setattr("emrf_run_access.run_store", lambda: store)

    with pytest.raises(subprocess.TimeoutExpired) as exc:
        reg.run_command(
            "compare-schwarzschild",
            ["--help"],
            timeout=1e-9,
            capture=True,
        )

    run_id = exc.value.run_id
    assert store.get(run_id).status == "timed_out"
    assert not list((tmp_path / run_id).glob("*.part"))


def test_registry_interrupt_records_terminal_state(
    tmp_path, monkeypatch: pytest.MonkeyPatch
):
    store = RunStore(tmp_path)
    monkeypatch.setattr("emrf_run_access.run_store", lambda: store)
    record = store.create("compare-schwarzschild", ["--help"])

    def interrupt(*args, **kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr(reg.subprocess, "run", interrupt)
    with pytest.raises(KeyboardInterrupt):
        reg.run_command(
            "compare-schwarzschild",
            ["--help"],
            prepared_run_id=record.run_id,
        )

    assert store.get(record.run_id).status == "interrupted"


def test_cli_version(capsys):
    with pytest.raises(SystemExit) as exc:
        emrf_cli.main(["--version"])
    assert exc.value.code == 0
    assert reg.__version__ in capsys.readouterr().out


def test_cli_list_json(capsys):
    assert emrf_cli.main(["list", "--json"]) == 0
    rows = json.loads(capsys.readouterr().out)
    assert {r["name"] for r in rows} == {c.name for c in reg.COMMANDS}


def test_cli_list_category(capsys):
    assert emrf_cli.main(["list", "--category", "stress-test"]) == 0
    assert "stress-gw-speed" in capsys.readouterr().out


def test_cli_run_unknown_is_usage_error(capsys):
    assert emrf_cli.main(["run", "nope"]) == 2


def test_cli_run_passes_args_and_exit_code():
    assert emrf_cli.main(["run", "compare-schwarzschild", "--", "--help"]) == 0


def test_cli_simulate_matches_api(capsys):
    argv = ["simulate", "--n", "2", "--weights", "0.5", "0.5",
            "--grid=-1,0,1", "--grid=0,0.5,1"]
    assert emrf_cli.main(argv) == 0
    cli_m = json.loads(capsys.readouterr().out)["M"]
    app.config["TESTING"] = True
    resp = app.test_client().post("/api/v1/simulate", json={
        "n": 2, "weights": [0.5, 0.5], "X_grid": [[-1, 0, 1], [0, 0.5, 1]]})
    assert resp.status_code == 200
    assert resp.get_json()["M"] == cli_m


def test_cli_simulate_invalid_input_is_usage_error(capsys):
    assert emrf_cli.main(["simulate", "--n", "2", "--weights", "1", "--grid", "0,1"]) == 2


def test_cli_doctor_json(capsys):
    emrf_cli.main(["doctor", "--json"])
    rep = json.loads(capsys.readouterr().out)
    assert rep["emrf_version"] == reg.__version__
    assert rep["missing_scripts"] == []


def test_cli_physics_verification_json(capsys):
    assert emrf_cli.main(["verify", "physics", "--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["all_passed"]
    assert report["evidence_class"] == "mixed"
    assert len(report["checks"]) == 10


def test_cli_data_list_runs(capsys):
    assert emrf_cli.main(["data", "list", "--json"]) == 0
    assert isinstance(json.loads(capsys.readouterr().out), list)


def test_cli_data_catalog_and_info(capsys):
    assert emrf_cli.main(["data", "catalog", "--json"]) == 0
    rows = json.loads(capsys.readouterr().out)
    assert "sparc-rotation-curves" in {row["id"] for row in rows}

    assert emrf_cli.main(["data", "info", "sparc-rotation-curves"]) == 0
    info = json.loads(capsys.readouterr().out)
    assert info["catalog"]["id"] == "sparc-rotation-curves"


def test_cli_data_unknown_dataset_is_usage_error(capsys):
    assert emrf_cli.main(["data", "info", "does-not-exist"]) == 2
    assert "Unknown dataset" in capsys.readouterr().err


def test_cli_run_and_job_management(tmp_path, monkeypatch, capsys):
    store = RunStore(tmp_path)
    monkeypatch.setattr("emrf_run_access.run_store", lambda: store)
    run = store.create("compare-schwarzschild", ["--not-a-real-option"])
    store.begin(run.run_id)
    store.finish(run.run_id, status="failed", returncode=2, duration_seconds=0.1)

    assert emrf_cli.main(["runs", "info", run.run_id]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "failed"
    assert emrf_cli.main(["runs", "list", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)[0]["run_id"] == run.run_id

    assert emrf_cli.main([
        "jobs", "submit", "compare-schwarzschild", "--", "--help"
    ]) == 0
    job = json.loads(capsys.readouterr().out)
    assert job["status"] == "queued"
    assert emrf_cli.main(["jobs", "run-next", "--worker-id", "test-worker"]) == 0
    completed = json.loads(capsys.readouterr().out)
    assert completed["status"] == "succeeded"
    assert completed["run_id"]


def test_dataset_verify_detects_tampering(tmp_path, monkeypatch):
    f = tmp_path / "obs.dat"
    f.write_bytes(b"real bytes")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"x/obs": {
        "file": "obs.dat", "url": "https://example.org/obs", "citation": "c",
        "bytes": 10, "sha256": reg._sha256(f)}}), encoding="utf-8")
    monkeypatch.setattr(reg, "MANIFEST", manifest)
    monkeypatch.setattr(reg, "REPO_ROOT", tmp_path)
    assert reg.dataset_status(verify=True)[0]["status"] == "ok"
    f.write_bytes(b"REAL bytes")
    assert reg.dataset_status(verify=True)[0]["status"] == "hash-mismatch"
    f.unlink()
    assert reg.dataset_status(verify=True)[0]["status"] == "missing"


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_api_version(client):
    data = client.get("/api/v1/version").get_json()
    assert data == {"version": reg.__version__, "api_version": "v1"}


def test_api_commands_parity_with_cli(client):
    data = client.get("/api/v1/commands").get_json()
    assert {c["name"] for c in data["commands"]} == {c.name for c in reg.COMMANDS}
    assert client.get("/api/v1/commands?category=bogus").status_code == 400
    assert client.get("/api/v1/commands/fit-sparc").get_json()["category"] == "analysis"
    assert client.get("/api/v1/commands/nope").status_code == 404


def test_api_run_disabled_by_default(client, monkeypatch):
    monkeypatch.delenv("EMRF_API_ALLOW_RUN", raising=False)
    assert client.post("/api/v1/commands/stress-gw-speed/run", json={}).status_code == 403


def test_api_run_validates_and_executes(client, monkeypatch):
    monkeypatch.setenv("EMRF_API_ALLOW_RUN", "1")
    assert client.post("/api/v1/commands/viz3d/run", json={}).status_code == 400
    assert client.post("/api/v1/commands/server-dev/run", json={}).status_code == 400
    assert client.post("/api/v1/commands/fit-sparc/run",
                       json={"args": [1]}).status_code == 400
    assert client.post("/api/v1/commands/fit-sparc/run",
                       json={"timeout": 10_000}).status_code == 400
    resp = client.post("/api/v1/commands/compare-schwarzschild/run",
                       json={"args": ["--help"], "timeout": 120})
    body = resp.get_json()
    assert resp.status_code == 200 and body["returncode"] == 0
    assert "Schwarzschild" in body["stdout"]


def test_api_run_records_and_jobs(client, tmp_path, monkeypatch):
    store = RunStore(tmp_path)
    monkeypatch.setattr("emrf_run_access.run_store", lambda: store)
    monkeypatch.setenv("EMRF_API_ALLOW_RUN", "1")

    submitted = client.post("/api/v1/jobs", json={
        "command": "compare-schwarzschild",
        "args": ["--help"],
        "max_attempts": 2,
    })
    assert submitted.status_code == 202
    job_id = submitted.get_json()["job_id"]
    assert client.get(f"/api/v1/jobs/{job_id}").get_json()["status"] == "queued"
    assert len(client.get("/api/v1/jobs").get_json()["jobs"]) == 1
    cancelled = client.post(f"/api/v1/jobs/{job_id}/cancel")
    assert cancelled.status_code == 200
    assert cancelled.get_json()["status"] == "cancelled"

    result = client.post(
        "/api/v1/commands/compare-schwarzschild/run",
        json={"args": ["--not-a-real-option"]},
    ).get_json()
    run_id = result["run_id"]
    assert client.get(f"/api/v1/runs/{run_id}").get_json()["status"] == "failed"
    assert client.get("/api/v1/runs").get_json()["runs"][0]["run_id"] == run_id
    resumed = client.post(f"/api/v1/runs/{run_id}/resume", json={"timeout": 120})
    assert resumed.status_code == 200
    assert resumed.get_json()["returncode"] != 0
    assert store.get(run_id).attempt == 2


def test_api_job_mutation_disabled_by_default(client, monkeypatch):
    monkeypatch.delenv("EMRF_API_ALLOW_RUN", raising=False)
    assert client.post("/api/v1/jobs", json={
        "command": "compare-schwarzschild",
    }).status_code == 403


def test_api_datasets_and_doctor(client):
    datasets = client.get("/api/v1/datasets").get_json()["datasets"]
    assert "sparc-rotation-curves" in {row["id"] for row in datasets}
    detail = client.get("/api/v1/datasets/sparc-rotation-curves").get_json()
    assert detail["catalog"]["id"] == "sparc-rotation-curves"
    rep = client.get("/api/v1/doctor").get_json()
    assert "executable" not in rep and rep["registered_commands"] == len(reg.COMMANDS)


def test_api_physics_verification(client):
    response = client.get("/api/v1/verification/physics")
    report = response.get_json()
    assert response.status_code == 200
    assert report["all_passed"]
    assert report["evidence_class"] == "mixed"
    assert len(report["checks"]) == 10


def test_api_data_mutation_requires_explicit_opt_in(client, monkeypatch):
    monkeypatch.delenv(server.DATA_WRITE_ENV_FLAG, raising=False)
    assert client.post(
        "/api/v1/datasets/sparc-rotation-curves/import",
        json={"logical_name": "Rotmod_LTG.zip"},
    ).status_code == 403
    assert client.post(
        "/api/v1/data/backups",
        json={"destination": "backup"},
    ).status_code == 403
    assert client.post(
        "/api/v1/data/restore-drills",
        json={},
    ).status_code == 403
    assert client.post(
        "/api/v1/data/backups/offsite",
        json={},
    ).status_code == 403


def test_api_data_gc_dry_run_remains_read_only(client, monkeypatch):
    class Library:
        def garbage_collect(self, *, execute=False):
            return {"executed": execute, "count": 0, "objects": [], "bytes": 0}

    monkeypatch.setattr(server, "_data_library", Library)
    monkeypatch.delenv(server.DATA_WRITE_ENV_FLAG, raising=False)
    response = client.post("/api/v1/data/gc", json={"execute": False})
    assert response.status_code == 200
    assert response.get_json()["executed"] is False


def test_api_unknown_route_returns_json(client):
    resp = client.get("/api/v1/does-not-exist")
    assert resp.status_code == 404 and "error" in resp.get_json()


def test_openapi_documents_every_route():
    spec = (reg.PACKAGE_DIR / "openapi.yaml").read_text(encoding="utf-8")
    documented = set(re.findall(r"^  (/[^:\s]*):\s*$", spec, re.MULTILINE))
    routes = {
        re.sub(r"<(?:\w+:)?(\w+)>", r"{\1}", r.rule)
        for r in app.url_map.iter_rules() if r.endpoint != "static"
    }
    assert routes == documented
