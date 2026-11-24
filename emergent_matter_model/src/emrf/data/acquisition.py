"""Resumable, integrity-pinned acquisition for catalog holdings."""

from __future__ import annotations

import ipaddress
import math
import os
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, BinaryIO, Protocol

from emrf import __version__
from emrf.core.errors import AcquisitionError, IntegrityError

from .catalog import CatalogDataset, CatalogHolding, DataCatalog
from .store import ContentAddressedStore, Holding

_BUFFER_SIZE = 1024 * 1024
_MAX_REDIRECTS = 5


def _validate_public_https_url(url: str, *, resolve_dns: bool = True) -> str:
    """Validate HTTPS scheme and block local, private, or multicast destinations."""
    try:
        parsed = urllib.parse.urlsplit(url)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise AcquisitionError(f"Invalid acquisition URL: {url}") from exc

    if (
        parsed.scheme.lower() != "https"
        or not hostname
        or parsed.username is not None
        or parsed.password is not None
        or port not in (None, 443)
        or hostname.lower().endswith((".localhost", ".local"))
    ):
        raise AcquisitionError(
            f"Refusing non-HTTPS or disallowed acquisition URL: {url}"
        )

    addresses: list[ipaddress.IPv4Address | ipaddress.IPv6Address] = []
    try:
        addresses = [ipaddress.ip_address(hostname)]
    except ValueError:
        if resolve_dns:
            try:
                addresses = [
                    ipaddress.ip_address(info[4][0])
                    for info in socket.getaddrinfo(
                        hostname, port or 443, type=socket.SOCK_STREAM
                    )
                ]
            except OSError as exc:
                raise AcquisitionError(
                    f"Hostname resolution failed for acquisition URL: {hostname}"
                ) from exc
    if any(not address.is_global or address.is_multicast for address in addresses):
        raise AcquisitionError(
            f"Refusing non-public or multicast acquisition destination: {url}"
        )
    return url


class _SafeHTTPSRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Redirect handler enforcing HTTPS and public IP destinations on every hop."""

    max_redirections = _MAX_REDIRECTS

    def redirect_request(  # type: ignore[override]
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> urllib.request.Request | None:
        redirect_dict = getattr(req, "redirect_dict", {})
        if len(redirect_dict) >= _MAX_REDIRECTS:
            raise AcquisitionError(
                f"Acquisition exceeded maximum redirect limit ({_MAX_REDIRECTS})"
            )
        _validate_public_https_url(newurl, resolve_dns=True)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _default_urlopen(request: urllib.request.Request, timeout: float) -> Any:
    opener = urllib.request.build_opener(_SafeHTTPSRedirectHandler)
    return opener.open(request, timeout=timeout)


class _Response(Protocol):
    headers: Any

    def __enter__(self) -> _Response: ...

    def __exit__(self, *args: object) -> None: ...

    def getcode(self) -> int: ...

    def geturl(self) -> str: ...

    def read(self, size: int = -1, /) -> bytes: ...


class ResumableFetcher:
    """Fetch catalog-pinned HTTPS objects while preserving partial progress."""

    def __init__(
        self,
        store: ContentAddressedStore,
        catalog: DataCatalog,
        *,
        opener: Callable[..., _Response] | None = None,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.store = store
        self.catalog = catalog
        self._custom_opener = opener is not None
        self._opener: Callable[..., _Response] = opener or _default_urlopen
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
        if expected.bytes and offset > expected.bytes:
            partial.unlink(missing_ok=True)
            raise AcquisitionError(
                f"Partial download exceeds expected size for {expected.logical_name}"
            )
        headers = {"User-Agent": f"EMRF/{__version__} scientific-data-acquisition"}
        if offset:
            headers["Range"] = f"bytes={offset}-"
        expected_url = expected.url
        if not expected_url:
            raise AcquisitionError(
                f"No URL configured for {expected.logical_name}"
            )
        _validate_public_https_url(expected_url, resolve_dns=not self._custom_opener)
        request = urllib.request.Request(expected_url, headers=headers)
        with self._opener(request, timeout=timeout) as response:
            final_url = response.geturl()
            _validate_public_https_url(final_url, resolve_dns=not self._custom_opener)
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
            written = offset if append else 0
            mode = "ab" if append else "wb"
            with partial.open(mode) as output:
                while chunk := response.read(_BUFFER_SIZE):
                    written += len(chunk)
                    if expected.bytes and written > expected.bytes:
                        raise AcquisitionError(
                            f"Download exceeded expected size ({expected.bytes} bytes) "
                            f"for {expected.logical_name}"
                        )
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
    if sys.platform == "win32":
        import msvcrt

        msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
    else:
        import fcntl

        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)


def _unlock_file(lock_file: BinaryIO) -> None:
    lock_file.seek(0)
    if sys.platform == "win32":
        import msvcrt

        msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        import fcntl

        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
