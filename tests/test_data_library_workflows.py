from __future__ import annotations

import hashlib
import io
import json
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from emrf.core.errors import AcquisitionError, IntegrityError
from emrf.data import (
    BackupManager,
    ContentAddressedStore,
    DataCatalog,
    DataLibrary,
    ResumableFetcher,
)

ROOT = Path(__file__).resolve().parents[1]


def _write_catalog(
    path: Path,
    raw: bytes,
    *,
    expected_sha256: str | None = None,
) -> DataCatalog:
    digest = expected_sha256 or hashlib.sha256(raw).hexdigest()
    payload = {
        "schema_version": "1.0.0",
        "datasets": [
            {
                "id": "example",
                "title": "Example observations",
                "status": "existing_holding",
                "priority": "high",
                "version": "v1",
                "url": "https://example.org/",
                "citation": "Example Collaboration",
                "redistribution": "Example terms",
                "holdings": [
                    {
                        "path": "data/external/example.dat",
                        "url": "https://example.org/example.dat",
                        "bytes": len(raw),
                        "sha256": digest,
                    }
                ],
            }
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return DataCatalog(path)


class _FakeResponse(io.BytesIO):
    def __init__(
        self,
        raw: bytes,
        status: int,
        content_range: str | None = None,
        final_url: str = "https://example.org/example.dat",
    ) -> None:
        super().__init__(raw)
        self._status = status
        self._final_url = final_url
        self.headers = {}
        if content_range is not None:
            self.headers["Content-Range"] = content_range

    def getcode(self) -> int:
        return self._status

    def geturl(self) -> str:
        return self._final_url

    def __enter__(self):
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


def test_packaged_catalog_copy_matches_curated_catalog() -> None:
    curated = ROOT / "knowledgebase" / "library" / "data_catalog.json"
    packaged = (
        ROOT
        / "emergent_matter_model"
        / "src"
        / "emrf"
        / "data"
        / "data_catalog.json"
    )
    assert packaged.read_bytes() == curated.read_bytes()


def test_catalog_import_registers_verified_immutable_holding(tmp_path: Path) -> None:
    raw = b"catalog observation"
    catalog = _write_catalog(tmp_path / "catalog.json", raw)
    source = tmp_path / "source.dat"
    source.write_bytes(raw)
    store = ContentAddressedStore(tmp_path / "store")

    holding = catalog.import_holding(
        store,
        "example",
        "example.dat",
        source=source,
    )

    assert holding.sha256 == hashlib.sha256(raw).hexdigest()
    assert holding.citation == "Example Collaboration"
    assert catalog.status(store, verify=True)[0]["status"] == "ok"


def test_catalog_does_not_treat_unregistered_bytes_as_a_holding(tmp_path: Path) -> None:
    raw = b"catalog observation"
    catalog = _write_catalog(tmp_path / "catalog.json", raw)
    store = ContentAddressedStore(tmp_path / "store")
    store.put_bytes(raw)

    status = catalog.status(store, verify=True)[0]

    assert status["status"] == "unregistered"
    assert status["holdings"][0]["status"] == "unregistered"


def test_resumable_fetch_uses_validated_range_and_promotes(tmp_path: Path) -> None:
    raw = b"resumable observation bytes"
    catalog = _write_catalog(tmp_path / "catalog.json", raw)
    store = ContentAddressedStore(tmp_path / "store")
    fetcher = ResumableFetcher(store, catalog)
    fetcher.downloads.mkdir(parents=True)
    partial = fetcher.downloads / f"{hashlib.sha256(raw).hexdigest()}.part"
    partial.write_bytes(raw[:7])

    def open_range(request, *, timeout: float):
        assert request.get_header("Range") == "bytes=7-"
        assert timeout == 12
        return _FakeResponse(raw[7:], 206, f"bytes 7-{len(raw) - 1}/{len(raw)}")

    fetcher._opener = open_range
    holding = fetcher.fetch("example", "example.dat", timeout=12)

    assert holding.path.read_bytes() == raw
    assert not partial.exists()


def test_fetch_keeps_partial_progress_after_network_failure(tmp_path: Path) -> None:
    raw = b"observation"
    catalog = _write_catalog(tmp_path / "catalog.json", raw)
    store = ContentAddressedStore(tmp_path / "store")

    def fail(*args, **kwargs):
        raise urllib.error.URLError("offline")

    fetcher = ResumableFetcher(store, catalog, opener=fail, sleeper=lambda _: None)
    fetcher.downloads.mkdir(parents=True)
    partial = fetcher.downloads / f"{hashlib.sha256(raw).hexdigest()}.part"
    partial.write_bytes(raw[:3])

    with pytest.raises(AcquisitionError, match="after 2 attempts"):
        fetcher.fetch("example", "example.dat", retries=1)
    assert partial.read_bytes() == raw[:3]


def test_fetch_quarantines_completed_hash_mismatch(tmp_path: Path) -> None:
    raw = b"expected"
    wrong = b"wrong!!!"
    catalog = _write_catalog(tmp_path / "catalog.json", raw)
    store = ContentAddressedStore(tmp_path / "store")
    fetcher = ResumableFetcher(
        store,
        catalog,
        opener=lambda *args, **kwargs: _FakeResponse(wrong, 200),
    )

    with pytest.raises(IntegrityError, match="Expected SHA-256"):
        fetcher.fetch("example", "example.dat")

    assert list(fetcher.downloads.glob("*.part")) == []
    assert len(list(fetcher.quarantine.glob("*.invalid"))) == 1


def test_fetch_quarantines_invalid_already_complete_partial(tmp_path: Path) -> None:
    raw = b"expected"
    catalog = _write_catalog(tmp_path / "catalog.json", raw)
    store = ContentAddressedStore(tmp_path / "store")
    fetcher = ResumableFetcher(store, catalog)
    fetcher.downloads.mkdir(parents=True)
    partial = fetcher.downloads / f"{hashlib.sha256(raw).hexdigest()}.part"
    partial.write_bytes(b"wrong!!!")

    with pytest.raises(IntegrityError, match="Expected SHA-256"):
        fetcher.fetch("example", "example.dat")

    assert not partial.exists()
    assert len(list(fetcher.quarantine.glob("*.invalid"))) == 1


def test_fetch_rejects_https_downgrade_redirect(tmp_path: Path) -> None:
    raw = b"expected"
    catalog = _write_catalog(tmp_path / "catalog.json", raw)
    store = ContentAddressedStore(tmp_path / "store")
    response = _FakeResponse(raw, 200, final_url="http://example.org/example.dat")
    fetcher = ResumableFetcher(
        store,
        catalog,
        opener=lambda *args, **kwargs: response,
        sleeper=lambda _: None,
    )

    with pytest.raises(AcquisitionError, match="non-HTTPS"):
        fetcher.fetch("example", "example.dat", retries=0)


def test_concurrent_fetches_share_one_locked_acquisition(tmp_path: Path) -> None:
    raw = b"shared acquisition"
    catalog = _write_catalog(tmp_path / "catalog.json", raw)
    store = ContentAddressedStore(tmp_path / "store")
    calls = 0

    def open_once(*args, **kwargs):
        nonlocal calls
        calls += 1
        return _FakeResponse(raw, 200)

    fetcher = ResumableFetcher(store, catalog, opener=open_once)
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(
            executor.map(
                lambda _: fetcher.fetch("example", "example.dat"),
                range(2),
            )
        )

    assert calls == 1
    assert results[0] == results[1]


def test_backup_restore_and_tamper_detection(tmp_path: Path) -> None:
    source = ContentAddressedStore(tmp_path / "source")
    held = source.put_bytes(b"held")
    orphan = source.put_bytes(b"orphan")
    source.register_holding("dataset", "v1", "raw", held, citation="Citation")
    backup = tmp_path / "backup"

    created = BackupManager(source).create(backup)
    assert len(created["objects"]) == 2
    assert len(created["holdings"]) == 1

    restored = ContentAddressedStore(tmp_path / "restored")
    result = BackupManager(restored).restore(backup)
    assert result == {"objects": 2, "holdings": 1}
    assert restored.get(held.sha256).path.read_bytes() == b"held"
    assert restored.get(orphan.sha256).path.read_bytes() == b"orphan"

    object_path = backup / "objects" / held.sha256[:2] / held.sha256[2:]
    object_path.write_bytes(b"bad!")
    with pytest.raises(IntegrityError, match="failed integrity verification"):
        BackupManager(restored).verify(backup)


def test_restore_drill_writes_passed_receipt_and_cleans_workspace(tmp_path: Path) -> None:
    store = ContentAddressedStore(tmp_path / "source")
    stored = store.put_bytes(b"drill observation")
    store.register_holding("dataset", "v1", "raw", stored)
    receipt = tmp_path / "receipts" / "drill.json"
    workspace = tmp_path / "workspace"

    result = BackupManager(store).drill(receipt, workspace=workspace)

    recorded = json.loads(receipt.read_text(encoding="utf-8"))
    assert result == recorded
    assert recorded["status"] == "passed"
    assert recorded["objects_verified"] == 1
    assert recorded["holdings_verified"] == 1
    assert list(workspace.iterdir()) == []

    with pytest.raises(FileExistsError, match="receipt already exists"):
        BackupManager(store).drill(receipt, workspace=workspace)


def test_offsite_backup_requires_independent_configured_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_catalog(tmp_path / "catalog.json", b"unused")
    library = DataLibrary(root=tmp_path / "data", catalog_path=tmp_path / "catalog.json")
    stored = library.store.put_bytes(b"offsite observation")
    library.store.register_holding("dataset", "v1", "raw", stored)
    monkeypatch.delenv("EMRF_OFFSITE_BACKUP_DIR", raising=False)

    with pytest.raises(ValueError, match="EMRF_OFFSITE_BACKUP_DIR"):
        library.create_offsite_backup()
    with pytest.raises(ValueError, match="independent of the data root"):
        library.create_offsite_backup(tmp_path / "data" / "backups")

    destination = tmp_path / "independent"
    monkeypatch.setenv("EMRF_OFFSITE_BACKUP_DIR", str(destination))
    result = library.create_offsite_backup()

    assert result["offsite"] is True
    assert Path(result["destination"]).parent == destination
    BackupManager(library.store).verify(result["destination"])


def test_garbage_collection_is_dry_run_by_default(tmp_path: Path) -> None:
    store = ContentAddressedStore(tmp_path)
    held = store.put_bytes(b"held")
    orphan = store.put_bytes(b"orphan")
    store.register_holding("dataset", "v1", "raw", held)

    assert store.garbage_collect() == [orphan]
    assert orphan.path.exists()
    assert store.garbage_collect(execute=True) == [orphan]
    assert not orphan.path.exists()
    assert store.get(held.sha256).path.exists()
