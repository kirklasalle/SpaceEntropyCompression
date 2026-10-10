"""Resumable, integrity-pinned acquisition for catalog holdings."""

from __future__ import annotations

import math
import os
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Generator
from contextlib import contextmanager
from pathlib import Path
from typing import BinaryIO, Protocol

from emrf.core.errors import AcquisitionError, IntegrityError

from .catalog import CatalogDataset, CatalogHolding, DataCatalog
from .store import ContentAddressedStore, Holding

_BUFFER_SIZE = 1024 * 1024


class _Response(Protocol):
    headers: object

    def __enter__(self) -> BinaryIO: ...

    def __exit__(self, *args: object) -> None: ...

    def getcode(self) -> int: ...

    def geturl(self) -> str: ...


class ResumableFetcher:
    """Fetch catalog-pinned HTTPS objects while preserving partial progress."""

    def __init__(
        self,
        store: ContentAddressedStore,
        catalog: DataCatalog,
        *,
        opener: Callable[..., _Response] = urllib.request.urlopen,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.store = store
        self.catalog = catalog
        self._opener = opener
        self._sleeper = sleeper
        self.downloads = store.root / "acquisition"
        self.quarantine = store.root / "quarantine"

    def fetch(
        self,
        dataset_id: str,
        logical_name: str,
        *,
        retries: int = 3,
        timeout: float = 180.0,
    ) -> Holding:
        if isinstance(retries, bool) or not isinstance(retries, int) or retries < 0:
            raise ValueError("retries must be nonnegative")
        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError("timeout must be positive")
        dataset = self.catalog.get(dataset_id)
        expected = _catalog_holding(dataset, logical_name)
        if dataset.version is None:
            raise AcquisitionError(f"Dataset has no pinned version: {dataset_id}")
        if expected.url is None:
            raise AcquisitionError(
                f"Holding has no approved acquisition URL: {dataset_id}/{logical_name}"
            )
        if not expected.url.startswith("https://"):
            raise AcquisitionError("Acquisition URLs must use HTTPS")

        self.downloads.mkdir(parents=True, exist_ok=True)
        partial = self.downloads / f"{expected.sha256}.part"
        with _exclusive_lock(partial.with_suffix(".lock"), timeout):
            return self._fetch_locked(
                dataset,
                expected,
                partial,
                retries=retries,
                timeout=timeout,
            )

    def _fetch_locked(
        self,
        dataset: CatalogDataset,
        expected: CatalogHolding,
        partial: Path,
        *,
        retries: int,
        timeout: float,
    ) -> Holding:
        self.store.initialize()
        try:
            existing = self.store.get_holding(
                dataset.dataset_id,
                dataset.version or "",
                expected.logical_name,
                verify=True,
            )
        except (FileNotFoundError, KeyError, IntegrityError):
            pass
        else:
            if existing.sha256 != expected.sha256:
                raise IntegrityError(
                    "Managed holding differs from the catalog-pinned SHA-256"
                )
            if expected.bytes is not None and existing.bytes != expected.bytes:
                raise IntegrityError(
                    "Managed holding differs from the catalog-pinned byte count"
                )
            return existing
        if expected.bytes is not None and partial.is_file():
            if partial.stat().st_size > expected.bytes:
                partial.unlink()
            elif partial.stat().st_size == expected.bytes:
                try:
                    return self._promote(dataset, expected, partial)
                except IntegrityError:
                    self._quarantine(partial, expected.sha256)
                    raise

        last_error: Exception | None = None
        for attempt in range(retries + 1):
            try:
                self._download_once(expected, partial, timeout)
                return self._promote(dataset, expected, partial)
            except IntegrityError:
                self._quarantine(partial, expected.sha256)
                raise
            except AcquisitionError:
                raise
            except (OSError, urllib.error.URLError) as exc:
                last_error = exc
                if attempt == retries:
                    break
                self._sleeper(min(2**attempt, 30))
        raise AcquisitionError(
            f"Could not acquire {dataset.dataset_id}/{expected.logical_name} "
            f"after {retries + 1} attempts"
        ) from last_error

    def _download_once(
        self,
        expected: CatalogHolding,
        partial: Path,
        timeout: float,
    ) -> None:
        offset = partial.stat().st_size if partial.is_file() else 0
        headers = {"User-Agent": "EMRF/0.9 scientific-data-acquisition"}
        if offset:
            headers["Range"] = f"bytes={offset}-"
        request = urllib.request.Request(expected.url, headers=headers)
        with self._opener(request, timeout=timeout) as response:
            final_url = response.geturl()
            if not final_url.startswith("https://"):
                raise AcquisitionError("Acquisition redirected to a non-HTTPS URL")
            status = response.getcode()
            if status not in {200, 206}:
                raise AcquisitionError(f"Unexpected HTTP status {status}")
            append = offset > 0 and status == 206
            if append:
                content_range = response.headers.get("Content-Range")
                if not isinstance(content_range, str) or not content_range.startswith(
                    f"bytes {offset}-"
                ):
                    raise AcquisitionError("Server returned an invalid resume range")
            mode = "ab" if append else "wb"
            with partial.open(mode) as output:
                while chunk := response.read(_BUFFER_SIZE):
                    output.write(chunk)
                output.flush()
                os.fsync(output.fileno())

    def _promote(
        self,
        dataset: CatalogDataset,
        expected: CatalogHolding,
        partial: Path,
    ) -> Holding:
        stored = self.store.put_file(
            partial,
            expected_sha256=expected.sha256,
            expected_bytes=expected.bytes,
        )
        holding = self.store.register_holding(
            dataset.dataset_id,
            dataset.version or "",
            expected.logical_name,
            stored,
            source_url=expected.url,
            citation=dataset.citation,
            licence=dataset.licence,
            metadata={
                "catalog_path": expected.path,
                "catalog_schema": self.catalog.schema_version,
            },
        )
        partial.unlink()
        return holding

    def _quarantine(self, partial: Path, expected_sha256: str) -> None:
        if not partial.exists():
            return
        self.quarantine.mkdir(parents=True, exist_ok=True)
        timestamp = time.time_ns()
        destination = self.quarantine / f"{expected_sha256}.{timestamp}.invalid"
        os.replace(partial, destination)


def _catalog_holding(
    dataset: CatalogDataset,
    logical_name: str,
) -> CatalogHolding:
    for holding in dataset.holdings:
        if holding.logical_name == logical_name:
            return holding
    raise KeyError(f"Unknown holding for {dataset.dataset_id}: {logical_name}")


@contextmanager
def _exclusive_lock(path: Path, timeout: float) -> Generator[None, None, None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as lock_file:
        if lock_file.tell() == 0:
            lock_file.write(b"\0")
            lock_file.flush()
        deadline = time.monotonic() + timeout
        while True:
            try:
                _lock_file(lock_file)
                break
            except OSError as exc:
                if time.monotonic() >= deadline:
                    raise AcquisitionError(
                        f"Timed out waiting for acquisition lock: {path}"
                    ) from exc
                time.sleep(0.05)
        try:
            yield
        finally:
            _unlock_file(lock_file)


def _lock_file(lock_file: BinaryIO) -> None:
    lock_file.seek(0)
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
    else:
        import fcntl

        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)


def _unlock_file(lock_file: BinaryIO) -> None:
    lock_file.seek(0)
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        import fcntl

        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
