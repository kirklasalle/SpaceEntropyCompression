"""Security, SSRF, path confinement, and server tests for .mcp."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
import urllib.request
from pathlib import Path
from unittest import mock

MCP_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = MCP_ROOT.parent
if str(MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(MCP_ROOT))

import emrf_workspace.server as ws_server  # noqa: E402
import science_data.adapters as adapters  # noqa: E402
import science_data.server as sd_server  # noqa: E402
from shared.mutation_gate import mutation_denial  # noqa: E402
from shared.network_safety import (  # noqa: E402
    _SafeHTTPSRedirectHandler,
    validate_public_https_url,
)
from shared.workspace import resolve_workspace_path  # noqa: E402


class _FakeHTTPResponse:
    def __init__(self, payload: bytes, final_url: str) -> None:
        self._payload = payload
        self._final_url = final_url

    def __enter__(self) -> "_FakeHTTPResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def geturl(self) -> str:
        return self._final_url

    def read(self, size: int = -1) -> bytes:
        return self._payload if size < 0 else self._payload[:size]


class TestEMRFMCP(unittest.TestCase):
    def test_network_safety_blocks_private_multicast_and_redirects(self) -> None:
        for bad in (
            "http://example.org/api",
            "https://localhost/api",
            "https://user:pass@example.org/api",
            "https://example.org:8443/api",
            "https://127.0.0.1/api",
            "https://10.0.0.1/api",
            "https://169.254.169.254/latest/meta-data/",
            "https://224.0.0.1/multicast",
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    validate_public_https_url(bad, resolve_dns=False)

        handler = _SafeHTTPSRedirectHandler()
        req = urllib.request.Request("https://example.org/api")
        with self.assertRaises(ValueError):
            handler.redirect_request(
                req, None, 302, "Found", {}, "https://127.0.0.1/internal"
            )

    def test_science_data_adapters_reject_bad_redirect_and_preserve_provenance(self) -> None:
        downgrade = lambda *args, **kwargs: _FakeHTTPResponse(  # noqa: E731
            b"[]", "http://insecure.example.org/data"
        )
        with self.assertRaises(adapters.ScienceDataError):
            adapters.query_exoplanets(limit=1, opener=downgrade)

        ok = lambda *args, **kwargs: _FakeHTTPResponse(  # noqa: E731
            json.dumps([{"pl_name": "K2-18 b"}]).encode("utf-8"),
            adapters.EXOPLANET_ENDPOINT,
        )
        result = adapters.query_exoplanets(columns=["pl_name"], limit=1, opener=ok)
        self.assertEqual(result["source"], "nasa-exoplanet-archive")
        self.assertEqual(result["record_count"], 1)
        self.assertIn("sha256", result)

        listed = sd_server.call_tool("science_data_list_sources", {"domain": "astronomy"})
        self.assertIn("domains", listed)

    def test_workspace_confinement_blocks_traversal_and_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "ws"
            outside = Path(tmp) / "outside.txt"
            root.mkdir()
            outside.write_text("secret", encoding="utf-8")
            (root / "ok.txt").write_text("hello", encoding="utf-8")

            self.assertEqual(
                resolve_workspace_path(root, "ok.txt").name, "ok.txt"
            )
            with self.assertRaises(ValueError):
                resolve_workspace_path(root, "../outside.txt")
            with self.assertRaises(ValueError):
                resolve_workspace_path(root, str(outside))

            link = root / "escape.txt"
            try:
                link.symlink_to(outside)
            except (OSError, NotImplementedError):
                pass
            else:
                with self.assertRaises(ValueError):
                    resolve_workspace_path(root, "escape.txt")

    def test_mutation_gate_requires_env_and_explicit_approval(self) -> None:
        with mock.patch.dict(os.environ, {"MCP_ALLOW_MUTATIONS": "0"}, clear=False):
            denied = mutation_denial("demo_tool", {"approved": True})
            self.assertEqual(denied["error"], "explicit_approval_required")

        with mock.patch.dict(os.environ, {"MCP_ALLOW_MUTATIONS": "1"}, clear=False):
            self.assertIsNotNone(mutation_denial("demo_tool", {}))
            self.assertIsNone(mutation_denial("demo_tool", {"approved": True}))

    def test_emrf_workspace_tools_are_read_only_and_functional(self) -> None:
        doc = ws_server.call_tool("emrf_doctor", {})
        self.assertIn("emrf_version", doc)
        commands = ws_server.call_tool("emrf_list_commands", {"category": "analysis"})
        self.assertIn("commands", commands)
        readme = ws_server.call_tool("emrf_read_workspace_file", {"path": ".mcp/README.md"})
        self.assertIn("emrf-workspace", readme["content"])
        escaped = ws_server.call_tool("emrf_read_workspace_file", {"path": "../outside"})
        self.assertIn("error", escaped)

    def test_zero_impressioncore_references_in_mcp(self) -> None:
        forbidden = (
            "ImpressionCore",
            "Sacred Covenant",
            "GOLIATH",
            "VRGC",
            "AGENTIC_PRIME_DIRECTIVE",
            "nexus_briefing",
        )
        for py_or_md in MCP_ROOT.rglob("*"):
            if (
                not py_or_md.is_file()
                or py_or_md.name == "test_emrf_mcp.py"
                or "__pycache__" in py_or_md.parts
            ):
                continue
            text = py_or_md.read_text(encoding="utf-8", errors="ignore")
            for marker in forbidden:
                self.assertNotIn(
                    marker.lower(),
                    text.lower(),
                    f"Forbidden reference {marker!r} found in {py_or_md}",
                )


if __name__ == "__main__":
    unittest.main()
