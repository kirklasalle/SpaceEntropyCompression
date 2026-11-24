"""Shared HTTP security, path confinement, and rate-limiting helpers."""

from __future__ import annotations

import os
import threading
import time
from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path

import emrf_paths

ALLOWED_IO_ROOTS_ENV = "EMRF_ALLOWED_IO_ROOTS"
_MAX_HTTP_REQUEST_BYTES_DEFAULT = 1 * 1024 * 1024
_MAX_CLI_ARGS = 64
_MAX_CLI_ARG_LENGTH = 4096

_PATH_FLAGS = frozenset({
    "-o",
    "--output",
    "--input",
    "--file",
    "--path",
    "--dest",
    "--destination",
    "--destination-root",
    "--receipt",
    "--workspace",
    "--source",
})


def max_http_request_bytes() -> int:
    raw = os.environ.get("EMRF_MAX_REQUEST_BYTES", str(_MAX_HTTP_REQUEST_BYTES_DEFAULT))
    try:
        limit = int(raw)
    except ValueError:
        return _MAX_HTTP_REQUEST_BYTES_DEFAULT
    return limit if limit > 0 else _MAX_HTTP_REQUEST_BYTES_DEFAULT


def allowed_io_roots() -> tuple[Path, ...]:
    """Return resolved directory roots permitted for HTTP-supplied file paths."""
    configured = os.environ.get(ALLOWED_IO_ROOTS_ENV, "").strip()
    if configured:
        roots = [
            Path(part.strip()).expanduser().resolve()
            for part in configured.split(os.pathsep)
            if part.strip()
        ]
        if roots:
            return tuple(roots)
    defaults: list[Path] = [
        emrf_paths.app_root().resolve(),
        emrf_paths.data_root().resolve(),
    ]
    offsite = os.environ.get("EMRF_OFFSITE_BACKUP_DIR", "").strip()
    if offsite:
        defaults.append(Path(offsite).expanduser().resolve())
    return tuple(dict.fromkeys(defaults))


def validate_http_io_path(raw: str, *, field_name: str = "path") -> str:
    """Validate that an HTTP-supplied filesystem path resolves inside an allowed root."""
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError(f"{field_name} must be non-empty text")
    if "\x00" in raw or "\n" in raw or "\r" in raw:
        raise ValueError(f"{field_name} contains disallowed control characters")
    candidate = Path(raw).expanduser().resolve()
    roots = allowed_io_roots()
    if not any(candidate == root or root in candidate.parents for root in roots):
        raise ValueError(
            f"{field_name} resolves outside allowed IO roots ({ALLOWED_IO_ROOTS_ENV})"
        )
    return raw


def validate_http_cli_args(args: Sequence[str]) -> tuple[str, ...]:
    """Validate CLI arguments accepted over HTTP endpoints."""
    if len(args) > _MAX_CLI_ARGS:
        raise ValueError(f"args may contain at most {_MAX_CLI_ARGS} arguments")
    validated: list[str] = []
    expect_path_flag: str | None = None
    for idx, arg in enumerate(args):
        if not isinstance(arg, str):
            raise ValueError(f"args[{idx}] must be text")
        if len(arg) > _MAX_CLI_ARG_LENGTH:
            raise ValueError(
                f"args[{idx}] exceeds maximum length of {_MAX_CLI_ARG_LENGTH}"
            )
        if "\x00" in arg or "\n" in arg or "\r" in arg:
            raise ValueError(f"args[{idx}] contains disallowed control characters")
        if expect_path_flag is not None:
            validate_http_io_path(arg, field_name=f"args[{expect_path_flag}]")
            expect_path_flag = None
        elif arg in _PATH_FLAGS:
            expect_path_flag = arg
        else:
            flag, sep, value = arg.partition("=")
            if sep == "=" and flag in _PATH_FLAGS:
                validate_http_io_path(value, field_name=f"args[{flag}]")
        validated.append(arg)
    return tuple(validated)


class SlidingWindowRateLimiter:
    """Thread-safe bounded sliding-window rate limiter keyed by client IP."""

    def __init__(
        self,
        max_requests: int = 120,
        window_seconds: float = 60.0,
        max_tracked_ips: int = 10_000,
    ) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.max_tracked_ips = max_tracked_ips
        self._records: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def allow(self, client_ip: str) -> bool:
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            if (
                client_ip not in self._records
                and len(self._records) >= self.max_tracked_ips
            ):
                stale = [
                    ip
                    for ip, times in self._records.items()
                    if not times or times[-1] <= cutoff
                ]
                for ip in stale:
                    del self._records[ip]
                while len(self._records) >= self.max_tracked_ips:
                    self._records.pop(next(iter(self._records)))
            timestamps = [t for t in self._records[client_ip] if t > cutoff]
            if len(timestamps) >= self.max_requests:
                self._records[client_ip] = timestamps
                return False
            timestamps.append(now)
            self._records[client_ip] = timestamps
            return True
