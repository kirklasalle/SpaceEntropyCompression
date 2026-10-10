"""Validated access to the curated EMRF observational-data catalog."""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Any

from emrf.core.errors import IntegrityError
from emrf_paths import project_root, resolve_data_path

from .store import ContentAddressedStore, Holding

_PACKAGED_CATALOG = "data_catalog.json"


@dataclass(frozen=True)
class CatalogHolding:
    """One expected file within a catalog dataset."""

    path: str
    sha256: str
    bytes: int | None
    url: str | None

    @property
    def logical_name(self) -> str:
        return Path(self.path).name


@dataclass(frozen=True)
class CatalogDataset:
    """Validated catalog metadata for one scientific dataset."""

    dataset_id: str
    title: str
    status: str
    priority: str
    version: str | None
    url: str
    citation: str
    licence: str
    holdings: tuple[CatalogHolding, ...]
    raw: dict[str, Any]


class DataCatalog:
    """Read and validate the human-curated observational catalog."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else _default_catalog_path()
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise IntegrityError(f"Could not read data catalog: {self.path}") from exc
        self.schema_version = _required_text(payload, "schema_version")
        entries = payload.get("datasets")
        if not isinstance(entries, list):
            raise IntegrityError("Data catalog 'datasets' must be a list")
        datasets = tuple(_parse_dataset(entry) for entry in entries)
        ids = [dataset.dataset_id for dataset in datasets]
        if len(ids) != len(set(ids)):
            raise IntegrityError("Data catalog contains duplicate dataset IDs")
        self._datasets = {dataset.dataset_id: dataset for dataset in datasets}

    def list(self) -> tuple[CatalogDataset, ...]:
        return tuple(self._datasets.values())

    def get(self, dataset_id: str) -> CatalogDataset:
        try:
            return self._datasets[dataset_id]
        except KeyError:
            raise KeyError(f"Unknown dataset: {dataset_id}") from None

    def status(
        self,
        store: ContentAddressedStore,
        *,
        verify: bool = False,
    ) -> list[dict[str, Any]]:
        """Return catalog metadata combined with managed-store availability."""
        store.initialize()
        rows: list[dict[str, Any]] = []
        for dataset in self.list():
            holdings: list[dict[str, Any]] = []
            for expected in dataset.holdings:
                state = "missing"
                try:
                    if dataset.version is None:
                        raise KeyError(dataset.dataset_id)
                    managed = store.get_holding(
                        dataset.dataset_id,
                        dataset.version,
                        expected.logical_name,
                        verify=verify,
                    )
                except KeyError:
                    try:
                        store.get(expected.sha256, verify=verify)
                    except FileNotFoundError:
                        pass
                    except IntegrityError:
                        state = "corrupt"
                    else:
                        state = "unregistered"
                except FileNotFoundError:
                    pass
                except IntegrityError:
                    state = "corrupt"
                else:
                    if (
                        managed.sha256 != expected.sha256
                        or (
                            expected.bytes is not None
                            and managed.bytes != expected.bytes
                        )
                    ):
                        state = "corrupt"
                    else:
                        state = "ok" if verify else "present"
                holdings.append(
                    {
                        "logical_name": expected.logical_name,
                        "path": expected.path,
                        "sha256": expected.sha256,
                        "expected_bytes": expected.bytes,
                        "url": expected.url,
                        "status": state,
                    }
                )
            rows.append(
                {
                    "id": dataset.dataset_id,
                    "title": dataset.title,
                    "catalog_status": dataset.status,
                    "priority": dataset.priority,
                    "version": dataset.version,
                    "url": dataset.url,
                    "holdings": holdings,
                    "status": _dataset_state(holdings),
                }
            )
        return rows

    def import_holding(
        self,
        store: ContentAddressedStore,
        dataset_id: str,
        logical_name: str,
        *,
        source: str | Path | None = None,
    ) -> Holding:
        dataset = self.get(dataset_id)
        expected = _get_holding(dataset, logical_name)
        if dataset.version is None:
            raise IntegrityError(f"Dataset has no pinned version: {dataset_id}")
        source_path = Path(source) if source is not None else resolve_data_path(expected.path)
        stored = store.put_file(
            source_path,
            expected_sha256=expected.sha256,
            expected_bytes=expected.bytes,
        )
        return store.register_holding(
            dataset.dataset_id,
            dataset.version,
            expected.logical_name,
            stored,
            source_url=expected.url,
            citation=dataset.citation,
            licence=dataset.licence,
            metadata={"catalog_path": expected.path, "catalog_schema": self.schema_version},
        )


def _default_catalog_path() -> Path:
    root = project_root()
    if root is not None:
        return root / "knowledgebase" / "library" / _PACKAGED_CATALOG
    return Path(str(files("emrf.data").joinpath(_PACKAGED_CATALOG)))


def _required_text(value: object, field: str) -> str:
    if not isinstance(value, dict):
        raise IntegrityError("Data catalog entries must be JSON objects")
    result = value.get(field)
    if not isinstance(result, str) or not result.strip():
        raise IntegrityError(f"Data catalog field '{field}' must be non-empty text")
    return result.strip()


def _optional_text(value: dict[str, Any], field: str) -> str | None:
    result = value.get(field)
    if result is None:
        return None
    if not isinstance(result, str) or not result.strip():
        raise IntegrityError(f"Data catalog field '{field}' must be non-empty text")
    return result.strip()


def _parse_dataset(value: object) -> CatalogDataset:
    dataset_id = _required_text(value, "id")
    assert isinstance(value, dict)
    status = _required_text(value, "status")
    priority = _required_text(value, "priority")
    if status not in {"existing_holding", "planned"}:
        raise IntegrityError(f"Invalid status for dataset {dataset_id}: {status}")
    if priority not in {"high", "medium", "low"}:
        raise IntegrityError(f"Invalid priority for dataset {dataset_id}: {priority}")
    url = _required_text(value, "url")
    licence = _required_text(value, "redistribution")
    if not url.startswith("https://"):
        raise IntegrityError(f"Dataset URL must use HTTPS: {dataset_id}")
    raw_holdings = value.get("holdings", [])
    if not isinstance(raw_holdings, list):
        raise IntegrityError(f"Dataset holdings must be a list: {dataset_id}")
    holdings = tuple(_parse_holding(dataset_id, entry) for entry in raw_holdings)
    names = [holding.logical_name for holding in holdings]
    if len(names) != len(set(names)):
        raise IntegrityError(f"Dataset has duplicate holding names: {dataset_id}")
    version = _optional_text(value, "version")
    if status == "existing_holding" and not holdings:
        raise IntegrityError(f"Existing dataset has no holdings: {dataset_id}")
    if holdings and version is None:
        raise IntegrityError(f"Dataset holdings require a pinned version: {dataset_id}")
    if status == "existing_holding" and any(
        holding.url is None for holding in holdings
    ):
        raise IntegrityError(f"Existing dataset holdings require HTTPS URLs: {dataset_id}")
    return CatalogDataset(
        dataset_id=dataset_id,
        title=_required_text(value, "title"),
        status=status,
        priority=priority,
        version=version,
        url=url,
        citation=_required_text(value, "citation"),
        licence=licence,
        holdings=holdings,
        raw=dict(value),
    )


def _parse_holding(dataset_id: str, value: object) -> CatalogHolding:
    path = _required_text(value, "path")
    assert isinstance(value, dict)
    digest = _required_text(value, "sha256").lower()
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise IntegrityError(f"Invalid holding SHA-256 in dataset {dataset_id}")
    expected_bytes = value.get("bytes")
    if expected_bytes is not None and (
        isinstance(expected_bytes, bool)
        or not isinstance(expected_bytes, int)
        or expected_bytes < 0
    ):
        raise IntegrityError(f"Invalid holding byte count in dataset {dataset_id}")
    url = _optional_text(value, "url")
    if url is not None and not url.startswith("https://"):
        raise IntegrityError(f"Holding URL must use HTTPS in dataset {dataset_id}")
    return CatalogHolding(path, digest, expected_bytes, url)


def _get_holding(dataset: CatalogDataset, logical_name: str) -> CatalogHolding:
    matches = [holding for holding in dataset.holdings if holding.logical_name == logical_name]
    if not matches:
        raise KeyError(f"Unknown holding for {dataset.dataset_id}: {logical_name}")
    return matches[0]


def _dataset_state(holdings: list[dict[str, Any]]) -> str:
    states = {holding["status"] for holding in holdings}
    if not holdings:
        return "planned"
    if "corrupt" in states:
        return "corrupt"
    if "unregistered" in states:
        return "partial" if len(states) > 1 else "unregistered"
    if "missing" in states:
        return "partial" if len(states) > 1 else "missing"
    return "ok" if states == {"ok"} else "present"
