"""Shared application service for data-library CLI and REST interfaces."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .acquisition import ResumableFetcher
from .backup import BackupManager
from .catalog import CatalogDataset, DataCatalog
from .store import ContentAddressedStore, Holding, StoredObject


class DataLibrary:
    """Coordinate catalog, storage, acquisition and backup operations."""

    def __init__(
        self,
        *,
        root: str | Path | None = None,
        catalog_path: str | Path | None = None,
    ) -> None:
        self.store = ContentAddressedStore(root)
        self.catalog = DataCatalog(catalog_path)
        self.fetcher = ResumableFetcher(self.store, self.catalog)
        self.backups = BackupManager(self.store)

    def catalog_status(self, *, verify: bool = False) -> list[dict[str, Any]]:
        return self.catalog.status(self.store, verify=verify)

    def info(self, dataset_id: str, *, verify: bool = False) -> dict[str, Any]:
        dataset = self.catalog.get(dataset_id)
        status = next(
            row
            for row in self.catalog.status(self.store, verify=verify)
            if row["id"] == dataset_id
        )
        return {"catalog": dataset.raw, "managed": status}

    def import_dataset(
        self,
        dataset_id: str,
        *,
        logical_name: str | None = None,
        source: str | Path | None = None,
    ) -> list[dict[str, Any]]:
        dataset = self.catalog.get(dataset_id)
        selected = _select_holdings(dataset, logical_name)
        if source is not None and len(selected) != 1:
            raise ValueError("source may only be used when one holding is selected")
        return [
            _holding_record(
                self.catalog.import_holding(
                    self.store,
                    dataset_id,
                    holding.logical_name,
                    source=source,
                )
            )
            for holding in selected
        ]

    def fetch_dataset(
        self,
        dataset_id: str,
        *,
        logical_name: str | None = None,
        retries: int = 3,
        timeout: float = 180.0,
    ) -> list[dict[str, Any]]:
        dataset = self.catalog.get(dataset_id)
        return [
            _holding_record(
                self.fetcher.fetch(
                    dataset_id,
                    holding.logical_name,
                    retries=retries,
                    timeout=timeout,
                )
            )
            for holding in _select_holdings(dataset, logical_name)
        ]

    def verify(self) -> dict[str, Any]:
        datasets = self.catalog_status(verify=True)
        managed = self.store.list_holdings(verify=True)
        failed = [
            dataset["id"]
            for dataset in datasets
            if (
                dataset["catalog_status"] == "existing_holding"
                and dataset["status"] != "ok"
            )
        ]
        return {
            "healthy": not failed,
            "failed_datasets": failed,
            "managed_holdings": len(managed),
            "datasets": datasets,
        }

    def create_backup(self, destination: str | Path) -> dict[str, Any]:
        manifest = self.backups.create(destination)
        return {
            "destination": str(Path(destination).expanduser().resolve()),
            "objects": len(manifest["objects"]),
            "holdings": len(manifest["holdings"]),
            "created_utc": manifest["created_utc"],
        }

    def create_offsite_backup(
        self,
        destination_root: str | Path | None = None,
    ) -> dict[str, Any]:
        configured = destination_root or os.environ.get("EMRF_OFFSITE_BACKUP_DIR")
        if configured is None:
            raise ValueError(
                "Set EMRF_OFFSITE_BACKUP_DIR or provide an off-site destination root"
            )
        root = Path(configured).expanduser().resolve()
        data_root = self.store.root.expanduser().resolve()
        if root == data_root or data_root in root.parents or root in data_root.parents:
            raise ValueError("Off-site backup destination must be independent of the data root")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        target = root / f"emrf-backup-{timestamp}"
        return {"offsite": True, **self.create_backup(target)}

    def verify_backup(self, source: str | Path) -> dict[str, Any]:
        manifest = self.backups.verify(source)
        return {
            "source": str(Path(source).expanduser().resolve()),
            "objects": len(manifest["objects"]),
            "holdings": len(manifest["holdings"]),
            "created_utc": manifest["created_utc"],
        }

    def restore_backup(self, source: str | Path) -> dict[str, int]:
        return self.backups.restore(source)

    def run_restore_drill(
        self,
        *,
        receipt: str | Path | None = None,
        workspace: str | Path | None = None,
    ) -> dict[str, Any]:
        if receipt is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            receipt = self.store.root / "drills" / f"restore-{timestamp}.json"
        result = self.backups.drill(receipt, workspace=workspace)
        return {"receipt": str(Path(receipt).expanduser().resolve()), **result}

    def garbage_collect(self, *, execute: bool = False) -> dict[str, Any]:
        objects = self.store.garbage_collect(execute=execute)
        return {
            "executed": execute,
            "objects": [_object_record(stored) for stored in objects],
            "count": len(objects),
            "bytes": sum(stored.bytes for stored in objects),
        }


def _select_holdings(
    dataset: CatalogDataset,
    logical_name: str | None,
) -> tuple[Any, ...]:
    if logical_name is None:
        if not dataset.holdings:
            raise ValueError(f"Dataset has no approved holdings: {dataset.dataset_id}")
        return dataset.holdings
    selected = tuple(
        holding for holding in dataset.holdings if holding.logical_name == logical_name
    )
    if not selected:
        raise KeyError(f"Unknown holding for {dataset.dataset_id}: {logical_name}")
    return selected


def _holding_record(holding: Holding) -> dict[str, Any]:
    return {
        "dataset_id": holding.dataset_id,
        "version": holding.version,
        "logical_name": holding.logical_name,
        "sha256": holding.sha256,
        "bytes": holding.bytes,
        "path": str(holding.path),
        "source_url": holding.source_url,
        "citation": holding.citation,
        "licence": holding.licence,
        "metadata": holding.metadata,
    }


def _object_record(stored: StoredObject) -> dict[str, Any]:
    return {
        "sha256": stored.sha256,
        "bytes": stored.bytes,
        "path": str(stored.path),
    }
