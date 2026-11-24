#!/usr/bin/env python3
"""Read-only, source-specific science-data MCP server for EMRF."""

from __future__ import annotations

import asyncio
import importlib.util
import sys
from pathlib import Path
from typing import Any

MCP_ROOT = Path(__file__).resolve().parents[1]
if str(MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(MCP_ROOT))

from science_data.adapters import (  # noqa: E402
    ScienceDataError,
    list_sources,
    query_exoplanets,
    search_inspire,
)
from shared.sdk_adapter import build_server, serve_stdio  # noqa: E402
from shared.workspace import resolve_workspace_root  # noqa: E402

WORKSPACE_ROOT = resolve_workspace_root(MCP_ROOT.parent)

TOOLS = [
    {
        "name": "science_data_list_sources",
        "description": "List supported public science-data sources and implemented coverage.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "enum": ["all", "astronomy", "hep_quantum"],
                    "default": "all",
                }
            },
        },
    },
    {
        "name": "science_data_query_exoplanets",
        "description": "Run a bounded read-only query against NASA Exoplanet Archive public TAP data.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "columns": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": sorted({
                            "pl_name", "hostname", "discoverymethod", "disc_year",
                            "sy_snum", "sy_pnum", "pl_orbper", "pl_rade", "pl_bmasse",
                        }),
                    },
                },
                "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
            },
        },
    },
    {
        "name": "science_data_search_inspire",
        "description": "Search bounded public HEP literature metadata through the official INSPIRE-HEP API.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "minLength": 1, "maxLength": 500},
                "limit": {"type": "integer", "minimum": 1, "maximum": 20, "default": 10},
            },
            "required": ["query"],
        },
    },
]


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    try:
        if name == "science_data_list_sources":
            return list_sources(arguments.get("domain", "all"))
        if name == "science_data_query_exoplanets":
            return query_exoplanets(
                columns=arguments.get("columns"),
                limit=arguments.get("limit", 20),
            )
        if name == "science_data_search_inspire":
            return search_inspire(
                query=arguments.get("query", ""),
                limit=arguments.get("limit", 10),
            )
        return {"error": "unknown_tool", "tool": name}
    except ScienceDataError as exc:
        return {"error": str(exc)}
    except Exception as exc:
        print(f"Science-data tool {name} failed: {exc}", file=sys.stderr)
        return {"error": "upstream_request_failed", "tool": name}


def build_app():
    return build_server(
        "spaceentropy-science-data",
        "1.0.0",
        lambda: TOOLS,
        call_tool,
        instructions=(
            f"Workspace root: {WORKSPACE_ROOT}. Read-only public archive APIs only. "
            "Every result includes source provenance; literature metadata or archive "
            "retrieval does not constitute physical model confirmation."
        ),
    )


app = build_app() if importlib.util.find_spec("mcp") is not None else None


async def main() -> None:
    await serve_stdio(app or build_app())


if __name__ == "__main__":
    asyncio.run(main())
