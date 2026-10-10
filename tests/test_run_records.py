from __future__ import annotations

import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from emrf.core.errors import IntegrityError, StorageError
from emrf.runs import RunStore


def test_run_record_captures_provenance_and_atomic_state(tmp_path: Path) -> None:
    store = RunStore(tmp_path)
    record = store.create(
        "example-analysis",
        ["--value", "1"],
        evidence_class="observational",
        inputs={"table": "a" * 64},
        seeds={"sampler": 42},
    )

    assert record.status == "pending"
    assert len(record.environment_sha256) == 64
    assert record.inputs == {"table": "a" * 64}
    assert record.seeds == {"sampler": 42}
    assert (record.path / "config.toml").is_file()
    assert list(record.path.glob("*.part")) == []

    running = store.begin(record.run_id)
    completed = store.finish(
        record.run_id,
        status="succeeded",
        returncode=0,
        duration_seconds=1.25,
    )

    assert running.attempt == 1
    assert completed.status == "succeeded"
    assert completed.returncode == 0
    assert completed.duration_seconds == 1.25


def test_failed_run_can_resume_without_rewriting_configuration(tmp_path: Path) -> None:
    store = RunStore(tmp_path)
    record = store.create("analysis", ["--x"])
    config = (record.path / "config.toml").read_bytes()
    store.begin(record.run_id)
    store.finish(record.run_id, status="failed", returncode=2, duration_seconds=0.1)

    resumed = store.begin(record.run_id, resume=True)

    assert resumed.status == "running"
    assert resumed.attempt == 2
    assert (record.path / "config.toml").read_bytes() == config
    with pytest.raises(ValueError, match="cannot be resumed"):
        store.begin(record.run_id, resume=True)


def test_checkpoints_are_atomic_and_fail_closed(tmp_path: Path) -> None:
    store = RunStore(tmp_path)
    record = store.create("analysis", [])

    path = store.save_checkpoint(record.run_id, "completed-items", {"items": [1, 2]})
    assert store.load_checkpoint(record.run_id, "completed-items") == {"items": [1, 2]}
    assert list(path.parent.glob("*.part")) == []

    path.write_text("{", encoding="utf-8")
    with pytest.raises(IntegrityError, match="Could not read checkpoint"):
        store.load_checkpoint(record.run_id, "completed-items")


def test_checkpoint_replace_failure_preserves_previous_value(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = RunStore(tmp_path)
    record = store.create("analysis", [])
    path = store.save_checkpoint(record.run_id, "progress", {"value": 1})

    def fail_replace(source: Path, destination: Path) -> None:
        raise OSError("injected")

    monkeypatch.setattr("emrf.runs.records.os.replace", fail_replace)
    with pytest.raises(StorageError, match="Could not write run metadata"):
        store.save_checkpoint(record.run_id, "progress", {"value": 2})

    assert json.loads(path.read_text(encoding="utf-8")) == {"value": 1}
    assert list(path.parent.glob("*.part")) == []


def test_job_queue_claims_once_and_retries_failures(tmp_path: Path) -> None:
    store = RunStore(tmp_path)
    first = store.enqueue("analysis", ["--one"], max_attempts=2)
    second = store.enqueue("analysis", ["--two"])

    claimed = store.claim("worker-1")
    assert claimed is not None
    assert claimed.job_id == first.job_id
    assert claimed.attempts == 1
    assert store.complete_job(first.job_id, returncode=1, error="failed").status == "queued"

    retried = store.claim("worker-2")
    assert retried is not None
    assert retried.job_id == first.job_id
    assert retried.attempts == 2
    assert store.complete_job(first.job_id, returncode=1, error="failed").status == "failed"

    claimed_second = store.claim("worker-3")
    assert claimed_second is not None
    assert claimed_second.job_id == second.job_id
    assert store.complete_job(second.job_id, returncode=0).status == "succeeded"
    assert store.claim("worker-4") is None


def test_concurrent_workers_cannot_claim_same_job(tmp_path: Path) -> None:
    store = RunStore(tmp_path)
    jobs = [store.enqueue("analysis", [str(index)]) for index in range(12)]

    def claim(index: int):
        return RunStore(tmp_path).claim(f"worker-{index}")

    with ThreadPoolExecutor(max_workers=12) as executor:
        claimed = [job for job in executor.map(claim, range(12)) if job is not None]

    assert len(claimed) == 12
    assert {job.job_id for job in claimed} == {job.job_id for job in jobs}


def test_concurrent_run_creation_publishes_complete_records(tmp_path: Path) -> None:
    def create(index: int):
        return RunStore(tmp_path).create("analysis", [str(index)])

    with ThreadPoolExecutor(max_workers=8) as executor:
        records = list(executor.map(create, range(8)))

    assert len({record.run_id for record in records}) == 8
    assert len(RunStore(tmp_path).list()) == 8
    assert not list(tmp_path.glob("*.part"))
    for record in records:
        assert (record.path / "run.json").is_file()
        assert (record.path / "config.toml").is_file()


def test_registry_enforces_foreign_keys_and_wal(tmp_path: Path) -> None:
    store = RunStore(tmp_path)
    store.initialize()
    with sqlite3.connect(store.registry) as connection:
        assert connection.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    with pytest.raises(sqlite3.IntegrityError), store._connect() as connection:
        connection.execute(
            """
            INSERT INTO jobs (
                job_id, command, args_json, evidence_class, status, attempts,
                max_attempts, created_utc, updated_utc, run_id
            ) VALUES (?, ?, '[]', 'software', 'queued', 0, 1, ?, ?, ?)
            """,
            (
                "20260101T000000000000Z-00000000",
                "analysis",
                "2026-01-01T00:00:00Z",
                "2026-01-01T00:00:00Z",
                "20260101T000000000000Z-11111111",
            ),
        )


def test_run_index_is_reconciled_from_durable_json(tmp_path: Path) -> None:
    store = RunStore(tmp_path)
    record = store.create("analysis", ["--one"])
    payload_path = record.path / "run.json"
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    payload.update({"status": "failed", "attempt": 3, "returncode": 9})
    payload_path.write_text(json.dumps(payload), encoding="utf-8")

    reopened = RunStore(tmp_path)
    listed = reopened.list()

    assert listed[0].status == "failed"
    assert listed[0].attempt == 3
    with sqlite3.connect(reopened.registry) as connection:
        row = connection.execute(
            "SELECT status, attempt, returncode FROM runs WHERE run_id = ?",
            (record.run_id,),
        ).fetchone()
    assert row == ("failed", 3, 9)


def test_expired_final_job_lease_transitions_to_failed(tmp_path: Path) -> None:
    store = RunStore(tmp_path)
    job = store.enqueue("analysis", [], max_attempts=1)
    claimed = store.claim("worker", lease_seconds=1)
    assert claimed is not None
    with store._connect() as connection:
        connection.execute(
            "UPDATE jobs SET lease_expires_utc = ? WHERE job_id = ?",
            ("2000-01-01T00:00:00+00:00", job.job_id),
        )

    assert store.claim("replacement") is None
    failed = store.get_job(job.job_id)
    assert failed.status == "failed"
    assert failed.last_error == "Worker lease expired after final attempt"


@pytest.mark.parametrize("value", [True, float("inf"), float("nan"), 0])
def test_queue_rejects_invalid_timeouts(tmp_path: Path, value: object) -> None:
    with pytest.raises(ValueError, match="timeout_seconds must be positive"):
        RunStore(tmp_path).enqueue("analysis", [], timeout_seconds=value)  # type: ignore[arg-type]
