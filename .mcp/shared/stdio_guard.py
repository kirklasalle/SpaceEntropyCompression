#!/usr/bin/env python3
"""Protocol-safe stdio wrapper keeping JSON-RPC messages separate from stderr logs."""

from __future__ import annotations

import io
import os
import sys
from contextlib import asynccontextmanager
from typing import AsyncIterator, BinaryIO, Optional, Tuple

_protocol_out: Optional[BinaryIO] = None


def protect_stdout() -> BinaryIO:
    """Reserve real stdout for MCP protocol traffic; redirect sys.stdout to stderr."""
    global _protocol_out
    if _protocol_out is not None:
        return _protocol_out

    try:
        sys.stdout.flush()
    except Exception:
        pass

    try:
        saved_fd = os.dup(1)
        _protocol_out = os.fdopen(saved_fd, "wb", buffering=0)
        os.dup2(2, 1)
    except OSError:
        _protocol_out = sys.stdout.buffer  # type: ignore[assignment]

    sys.stdout = sys.stderr
    return _protocol_out  # type: ignore[return-value]


@asynccontextmanager
async def stdio_server() -> AsyncIterator[Tuple[object, object]]:
    """Run MCP stdio server writing protocol frames to protected stdout."""
    import anyio
    from mcp.server.stdio import stdio_server as _sdk_stdio_server

    out = protect_stdout()
    stdin = anyio.wrap_file(
        io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")
    )
    stdout = anyio.wrap_file(
        io.TextIOWrapper(out, encoding="utf-8", newline="", write_through=True)
    )
    async with _sdk_stdio_server(stdin=stdin, stdout=stdout) as streams:
        yield streams
