"""Cross-platform advisory file locks and process-liveness checks."""

from __future__ import annotations

import os
import threading
import time
import uuid
from contextlib import suppress
from pathlib import Path

from emrf.core.errors import StorageError

_PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
_STILL_ACTIVE = 259
_ERROR_ACCESS_DENIED = 5
_EMPTY_LOCK_GRACE_SECONDS = 1.0
_REGISTRY_GUARD = threading.Lock()
_IN_PROCESS_LOCKS: dict[Path, threading.RLock] = {}


def _thread_lock_for(path: Path) -> threading.RLock:
    resolved = path.resolve(strict=False)
    with _REGISTRY_GUARD:
        lock = _IN_PROCESS_LOCKS.get(resolved)
        if lock is None:
            lock = threading.RLock()
            _IN_PROCESS_LOCKS[resolved] = lock
        return lock


def process_alive(process_id: int) -> bool:
    """Return True if *process_id* is alive (safe on both Windows and POSIX)."""
    if process_id <= 0:
        return False
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        open_process = kernel32.OpenProcess
        open_process.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        open_process.restype = wintypes.HANDLE
        get_exit_code = kernel32.GetExitCodeProcess
        get_exit_code.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        get_exit_code.restype = wintypes.BOOL
        close_handle = kernel32.CloseHandle
        close_handle.argtypes = [wintypes.HANDLE]
        close_handle.restype = wintypes.BOOL

        handle = open_process(_PROCESS_QUERY_LIMITED_INFORMATION, False, process_id)
        if not handle:
            error = ctypes.get_last_error()
            return error == _ERROR_ACCESS_DENIED
        try:
            exit_code = wintypes.DWORD(0)
            if not get_exit_code(handle, ctypes.byref(exit_code)):
                return True
            return int(exit_code.value) == _STILL_ACTIVE
        finally:
            close_handle(handle)

    try:
        os.kill(process_id, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return True
    return True


def lock_owner_alive(path: Path) -> bool:
    """Return True unless the lock file unambiguously belongs to a dead process."""
    try:
        raw = path.read_text(encoding="ascii").strip()
    except FileNotFoundError:
        return False
    except OSError:
        return True
    if not raw:
        try:
            age = time.time() - path.stat().st_mtime
        except FileNotFoundError:
            return False
        except OSError:
            return True
        return age < _EMPTY_LOCK_GRACE_SECONDS
    try:
        process_id = int(raw.splitlines()[0].strip())
    except ValueError:
        return False
    return process_alive(process_id)


def _unlink_with_retry(path: Path) -> None:
    for attempt in range(5):
        try:
            path.unlink()
            return
        except FileNotFoundError:
            return
        except PermissionError:
            if attempt == 4:
                return
            time.sleep(0.01 * (attempt + 1))


class ProcessFileLock:
    """Crash-recoverable exclusive lock file serialized across threads and processes."""

    def __init__(self, path: Path, *, timeout: float = 30.0) -> None:
        self.path = path
        self.timeout = timeout
        self._thread_lock = _thread_lock_for(path)
        self._held_thread = False
        self._held_file = False

    def _try_acquire(self) -> bool:
        payload = f"{os.getpid()}\n".encode("ascii")
        candidate = self.path.with_name(
            f".{self.path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp"
        )
        descriptor = os.open(
            candidate,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            0o600,
        )
        try:
            os.write(descriptor, payload)
            with suppress(OSError):
                os.fsync(descriptor)
        finally:
            os.close(descriptor)
        try:
            os.link(candidate, self.path)
            return True
        except FileExistsError:
            return False
        except OSError:
            # Filesystems without hard-link support (e.g., FAT32/exFAT)
            with suppress(FileNotFoundError):
                candidate.unlink()
            try:
                exclusive_fd = os.open(
                    self.path,
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                    0o600,
                )
            except FileExistsError:
                return False
            try:
                os.write(exclusive_fd, payload)
                with suppress(OSError):
                    os.fsync(exclusive_fd)
            finally:
                os.close(exclusive_fd)
            return True
        finally:
            with suppress(FileNotFoundError):
                candidate.unlink()

    def __enter__(self) -> ProcessFileLock:
        if not self._thread_lock.acquire(timeout=self.timeout):
            raise StorageError(f"Timed out waiting for lock: {self.path}")
        self._held_thread = True
        try:
            deadline = time.monotonic() + self.timeout
            self.path.parent.mkdir(parents=True, exist_ok=True)
            while True:
                if self._try_acquire():
                    self._held_file = True
                    return self
                if not lock_owner_alive(self.path):
                    _unlink_with_retry(self.path)
                    continue
                if time.monotonic() >= deadline:
                    raise StorageError(f"Timed out waiting for lock: {self.path}")
                time.sleep(0.05)
        except Exception:
            self._held_thread = False
            self._thread_lock.release()
            raise

    def __exit__(self, *_: object) -> None:
        try:
            if self._held_file:
                self._held_file = False
                _unlink_with_retry(self.path)
        finally:
            if self._held_thread:
                self._held_thread = False
                self._thread_lock.release()
