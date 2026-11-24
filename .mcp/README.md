# EMRF Local MCP Servers

Repository-owned, strictly read-only Model Context Protocol (MCP) servers for the
**Emergent Matter Research Framework (EMRF)**.

## Servers

1. **`emrf-workspace`** (`.mcp/emrf_workspace/server.py`)
   - Exposes read-only EMRF diagnostics (`emrf_doctor`), command registry lookup
     (`emrf_list_commands`), dataset status (`emrf_list_datasets`), knowledge graph
     queries and validation (`emrf_query_knowledge`, `emrf_validate_knowledge`), and
     workspace-confined file inspection (`emrf_read_workspace_file`).
2. **`science-data`** (`.mcp/science_data/server.py`)
   - Exposes bounded, read-only public archive queries against NASA Exoplanet Archive
     TAP (`science_data_query_exoplanets`) and INSPIRE-HEP literature metadata
     (`science_data_search_inspire`).
   - Enforces public HTTPS URL validation on both initial URLs and HTTP redirects
     (blocking localhost, private RFC1918/ULA, link-local, and multicast ranges).

## Running Tests

```powershell
python -m unittest discover -s .mcp/tests -v
```
