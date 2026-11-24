#!/usr/bin/env python3
"""Read-only EMRF workspace MCP server (diagnostics, catalog, knowledge graph, files)."""

from __future__ import annotations

import asyncio
import importlib.util
import sys
from pathlib import Path
from typing import Any

MCP_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = MCP_ROOT.parent
PACKAGE_ROOT = REPO_ROOT / "emergent_matter_model"
SRC_ROOT = PACKAGE_ROOT / "src"

for _entry in (str(MCP_ROOT), str(SRC_ROOT), str(PACKAGE_ROOT)):
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

from shared.sdk_adapter import build_server, serve_stdio  # noqa: E402
from shared.workspace import resolve_workspace_path, resolve_workspace_root  # noqa: E402

MAX_FILE_READ_BYTES = 262_144
WORKSPACE_ROOT = resolve_workspace_root(REPO_ROOT)

TOOLS = [
    {
        "name": "emrf_doctor",
        "description": "Return read-only EMRF runtime and dependency diagnostics.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "emrf_list_commands",
        "description": "List registered EMRF CLI/research commands with optional category filter.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {"type": "string"},
            },
        },
    },
    {
        "name": "emrf_list_datasets",
        "description": "List EMRF observational datasets and local verification status.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "verify": {"type": "boolean", "default": False},
            },
        },
    },
    {
        "name": "emrf_query_knowledge",
        "description": "Query nodes in knowledgebase/GRAPH_MEMORY.json.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "kind": {"type": "string"},
                "lifecycle_status": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 200, "default": 50},
            },
        },
    },
    {
        "name": "emrf_validate_knowledge",
        "description": "Validate the EMRF knowledge graph schema and integrity invariants.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "emrf_read_workspace_file",
        "description": "Read a UTF-8 file strictly inside the workspace root (bounded to 256 KiB).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "minLength": 1},
                "max_bytes": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": MAX_FILE_READ_BYTES,
                    "default": 65536,
                },
            },
            "required": ["path"],
        },
    },
]


def _client():
    from emrf.sdk import EMRFClient

    return EMRFClient()


def read_workspace_file(relative_path: str, max_bytes: int = 65536) -> dict[str, Any]:
    if not isinstance(max_bytes, int) or isinstance(max_bytes, bool) or not 1 <= max_bytes <= MAX_FILE_READ_BYTES:
        raise ValueError(f"max_bytes must be between 1 and {MAX_FILE_READ_BYTES}")
    target = resolve_workspace_path(WORKSPACE_ROOT, relative_path)
    if not target.is_file():
        raise FileNotFoundError(f"Workspace file not found: {relative_path}")
    raw = target.read_bytes()
    truncated = len(raw) > max_bytes
    snippet = raw[:max_bytes].decode("utf-8", errors="replace")
    return {
        "path": str(target.relative_to(WORKSPACE_ROOT.resolve())).replace("\\", "/"),
        "bytes": len(raw),
        "truncated": truncated,
        "content": snippet,
    }


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    try:
        if name == "emrf_doctor":
            return _client().environment_report().to_dict()
        if name == "emrf_list_commands":
            return _client().list_commands(arguments.get("category")).to_dict()
        if name == "emrf_list_datasets":
            return _client().list_datasets(
                verify=bool(arguments.get("verify", False))
            ).to_dict()
        if name == "emrf_query_knowledge":
            return _client().query_knowledge(
                arguments.get("text"),
                kind=arguments.get("kind"),
                lifecycle_status=arguments.get("lifecycle_status"),
                limit=int(arguments.get("limit", 50)),
            ).to_dict()
        if name == "emrf_validate_knowledge":
            return _client().validate_knowledge().to_dict()
        if name == "emrf_read_workspace_file":
            return read_workspace_file(
                str(arguments.get("path", "")),
                int(arguments.get("max_bytes", 65536)),
            )
        return {"error": "unknown_tool", "tool": name}
    except Exception as exc:
        return {"error": str(exc), "tool": name}


def build_app():
    return build_server(
        "emrf-workspace",
        "1.0.0",
        lambda: TOOLS,
        call_tool,
        instructions=(
            f"Read-only EMRF workspace server rooted at {WORKSPACE_ROOT}. "
            "No write or command execution tools are exposed."
        ),
    )


app = build_app() if importlib.util.find_spec("mcp") is not None else None


async def main() -> None:
    await serve_stdio(app or build_app())


if __name__ == "__main__":
    asyncio.run(main())
