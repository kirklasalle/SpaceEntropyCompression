from __future__ import annotations

import hashlib
import os
import sqlite3
import stat
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from emrf.core.errors import IntegrityError, StorageError
from emrf.data.store import ContentAddressedStore


def _make_writable(path: Path) -> None:
    path.chmod(stat.S_IWRITE | stat.S_IREAD)


def test_put_bytes_is_content_addressed_and_deduplicated(tmp_path: Path) -> None:
    store = ContentAddressedStore(tmp_path)
    raw = b"immutable observation bytes\n"
    digest = hashlib.sha256(raw).hexdigest()

    first = store.put_bytes(raw, expected_sha256=digest, expected_bytes=len(raw))
    second = store.put_bytes(raw)

    assert first == second
    assert first.path == tmp_path / "store" / "sha256" / digest[:2] / digest[2:]
    assert first.path.read_bytes() == raw
    assert list((tmp_path / "store" / "tmp").glob("*.part")) == []


def test_integrity_mismatch_never_publishes_an_object(tmp_path: Path) -> None:
    store = ContentAddressedStore(tmp_path)
    raw = b"wrong bytes"

    with pytest.raises(IntegrityError, match="Expected SHA-256"):
        store.put_bytes(raw, expected_sha256="0" * 64)

    assert list((tmp_path / "store" / "sha256").glob("*/*")) == []
    assert list((tmp_path / "store" / "tmp").glob("*.part")) == []


def test_file_ingest_and_holding_metadata_persist(tmp_path: Path) -> None:
    source = tmp_path / "source.dat"
    source.write_bytes(b"published table\n")
    store = ContentAddressedStore(tmp_path / "library")

    stored = store.put_file(source)
    holding = store.register_holding(
        "example-observation",
        "v1",
        "table.dat",
        stored,
        source_url="https://example.org/table.dat",
        citation="Example Collaboration (2026)",
        licence="Example terms",
        metadata={"units": "dimensionless", "evidence_class": "observational"},
    )
    reopened = ContentAddressedStore(tmp_path / "library").get_holding(
        "example-observation", "v1", "table.dat"
    )

    assert reopened == holding
    assert reopened.path.read_bytes() == source.read_bytes()
    assert reopened.metadata["evidence_class"] == "observational"


def test_holding_cannot_be_rebound_to_different_bytes(tmp_path: Path) -> None:
    store = ContentAddressedStore(tmp_path)
    first = store.put_bytes(b"first")
    second = store.put_bytes(b"second")
    store.register_holding("dataset", "v1", "raw", first)

    with pytest.raises(IntegrityError, match="cannot be rebound"):
        store.register_holding("dataset", "v1", "raw", second)

    assert store.get_holding("dataset", "v1", "raw").sha256 == first.sha256


def test_corruption_is_detected_before_bytes_are_returned(tmp_path: Path) -> None:
    store = ContentAddressedStore(tmp_path)
    stored = store.put_bytes(b"authentic")
    _make_writable(stored.path)
    stored.path.write_bytes(b"tampered!")

    with pytest.raises(IntegrityError, match="failed integrity verification"):
        store.get(stored.sha256)


def test_registry_uses_wal_and_foreign_keys(tmp_path: Path) -> None:
    store = ContentAddressedStore(tmp_path)
    store.initialize()

    with sqlite3.connect(store.registry) as connection:
        assert connection.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
    assert {"objects", "holdings"} <= tables


def test_default_store_respects_configured_data_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("EMRF_DATA_DIR", str(tmp_path))
    store = ContentAddressedStore()
    assert store.root == tmp_path


def test_invalid_holding_metadata_is_rejected(tmp_path: Path) -> None:
    store = ContentAddressedStore(tmp_path)
    stored = store.put_bytes(b"data")

    with pytest.raises(ValueError, match="dataset_id"):
        store.register_holding("", "v1", "raw", stored)
    with pytest.raises(ValueError, match="HTTPS"):
        store.register_holding(
            "dataset", "v1", "raw", stored, source_url="http://example.org/raw"
        )


def test_object_path_rejects_invalid_digest(tmp_path: Path) -> None:
    store = ContentAddressedStore(tmp_path)
    with pytest.raises(ValueError, match="sha256"):
        store.object_path("not-a-digest")


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="symbolic links unavailable")
def test_symbolic_link_object_is_rejected(tmp_path: Path) -> None:
    store = ContentAddressedStore(tmp_path)
    raw = b"external"
    digest = hashlib.sha256(raw).hexdigest()
    external = tmp_path / "external"
    external.write_bytes(raw)
    destination = store.object_path(digest)
    destination.parent.mkdir(parents=True)
    try:
        destination.symlink_to(external)
    except OSError:
        pytest.skip("symbolic links require additional privileges")

    with pytest.raises(IntegrityError, match="symbolic link"):
        store.get(digest, verify=False)


def test_prune_temporary_removes_only_stale_partial_objects(tmp_path: Path) -> None:
    store = ContentAddressedStore(tmp_path)
    store.initialize()
    stale = store.temporary / "object-stale.part"
    recent = store.temporary / "object-recent.part"
    unrelated = store.temporary / "unrelated.part"
    for path in (stale, recent, unrelated):
        path.write_bytes(b"partial")
    old = time.time() - 100
    os.utime(stale, (old, old))

    assert store.prune_temporary(max_age_seconds=50) == 1
    assert not stale.exists()
    assert recent.exists()
    assert unrelated.exists()


def test_registry_enforces_foreign_keys(tmp_path: Path) -> None:
    store = ContentAddressedStore(tmp_path)
    store.initialize()

    with pytest.raises(sqlite3.IntegrityError), store._connect() as connection:
        connection.execute(
            """
            INSERT INTO holdings (
                dataset_id, version, logical_name, sha256, metadata_json, created_utc
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("missing", "v1", "raw", "0" * 64, "{}", "2026-01-01T00:00:00Z"),
        )


def test_multi_chunk_file_ingest_and_expected_size_validation(tmp_path: Path) -> None:
    raw = b"a" * (1024 * 1024 + 17)
    source = tmp_path / "large.dat"
    source.write_bytes(raw)
    store = ContentAddressedStore(tmp_path / "library")

    stored = store.put_file(source, expected_bytes=len(raw))
    assert stored.sha256 == hashlib.sha256(raw).hexdigest()
    assert stored.path.read_bytes() == raw

    with pytest.raises(IntegrityError, match="Expected .* bytes"):
        store.put_file(source, expected_bytes=len(raw) - 1)
    assert list(store.temporary.glob("*.part")) == []


def test_replace_failure_cleans_up_partial_object(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = ContentAddressedStore(tmp_path)

    def fail_replace(source: Path, destination: Path) -> None:
        raise OSError("injected replacement failure")

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(StorageError, match="Could not store object"):
        store.put_bytes(b"data")

    assert list(store.temporary.glob("*.part")) == []
    assert list(store.objects.glob("*/*")) == []


def test_concurrent_identical_ingestion_deduplicates(tmp_path: Path) -> None:
    store = ContentAddressedStore(tmp_path)
    raw = b"concurrent observation" * 1000

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(lambda _: store.put_bytes(raw), range(16)))

    assert len({result.sha256 for result in results}) == 1
    assert len({result.path for result in results}) == 1
    assert results[0].path.read_bytes() == raw
    assert list(store.temporary.glob("*.part")) == []


def test_ingest_repairs_corrupt_existing_object(tmp_path: Path) -> None:
    store = ContentAddressedStore(tmp_path)
    raw = b"authentic bytes"
    stored = store.put_bytes(raw)
    stored.path.write_bytes(b"corrupt bytes!")

    repaired = store.put_bytes(raw)

    assert repaired == stored
    assert repaired.path.read_bytes() == raw
    assert store.get(repaired.sha256) == repaired


def test_holding_registration_is_immutable_and_normalizes_keys(tmp_path: Path) -> None:
    store = ContentAddressedStore(tmp_path)
    stored = store.put_bytes(b"observation")
    original = store.register_holding(
        " dataset ",
        " v1 ",
        " raw ",
        stored,
        citation="Original citation",
        metadata={"revision": 1},
    )
    replay = store.register_holding(
        "dataset",
        "v1",
        "raw",
        stored,
        citation="Original citation",
        metadata={"revision": 1},
    )

    with pytest.raises(IntegrityError, match="provenance metadata is immutable"):
        store.register_holding(
            "dataset",
            "v1",
            "raw",
            stored,
            citation="Changed citation",
            metadata={"revision": 2},
        )

    assert original.dataset_id == "dataset"
    assert original.version == "v1"
    assert original.logical_name == "raw"
    assert replay == original
    assert replay.citation == "Original citation"
    assert replay.metadata == {"revision": 1}
