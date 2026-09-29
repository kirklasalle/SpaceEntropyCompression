#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\main_server.py #documentation #python #source_code  
**Category:** Source Code  
**Status:** Active
"""





# Add project root and src to sys.path for reliable imports
import sys
import os
from pathlib import Path
import asyncio
import logging
from typing import Any, Dict, List

CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SRC_ROOT))

from nlu_bridge import DPANLUBridge
from ids_bridge import IDSBridge

# MCP imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent, ServerCapabilities, ToolsCapability

# Chronology loader (shared, read-only)
try:
    from assistant.chronology_loader import load_chronology, query_chronology, load_delta  # type: ignore
    HAS_CHRONOLOGY = True
except Exception:
    HAS_CHRONOLOGY = False

# Setup logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DPA_DEBUG") else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("dpa-mcp-server")

# DPA Core
class DPACore:
    """Core DPA logic and tool implementations"""
    def __init__(self):
        self.nlu = DPANLUBridge()
        self.ids = IDSBridge()
        # Add other subsystem initializations as needed

    def analyze(self, text: str) -> Any:
        """Analyze user input and return NLUResult."""
        return self.nlu.analyze(text)

    def get_intent(self, text: str) -> Any:
        """Extract only the intent from user input."""
        return self.nlu.get_intent(text)

    def get_entities(self, text: str) -> Any:
        """Extract only entities from user input."""
        return self.nlu.get_entities(text)

    def shutdown(self) -> str:
        """Shutdown the DPA server and all bridges."""
        self.nlu.shutdown()
        # Shutdown other modules as needed
        return "DPA server shutdown."

    def ids_update(self) -> Any:
        """Trigger IDS update operation."""
        return self.ids.update()

    def ids_tag(self) -> Any:
        """Trigger IDS tag operation."""
        return self.ids.tag()

    def ids_sync(self) -> Any:
        """Trigger IDS sync operation."""
        return self.ids.sync()

    def ids_status(self) -> Any:
        """Get IDS system status."""
        return self.ids.status()

    def ids_search(self, query: str) -> Any:
        """Search IDS documentation."""
        return self.ids.search(query)

    def ids_generate_docs(self) -> Any:
        """Trigger IDS documentation generation."""
        return self.ids.generate_docs()

# Instantiate core
dpa_core = DPACore()



# Accessibility Integration (absolute import for script execution)
from accessibility.accessibility_integration import AccessibilityIntegrationManager
from accessibility.accessibility_manager import AccessibilityManager
from accessibility.user_experience_manager import UserExperienceManager
from core.query_processor import QueryProcessor
from nlp.nlu_engine import NLUEngine

# Initialize accessibility subsystem components explicitly
_accessibility_manager = AccessibilityManager()
_ux_manager = UserExperienceManager(_accessibility_manager)
_query_processor = QueryProcessor()
_nlu_engine = NLUEngine()
accessibility = AccessibilityIntegrationManager(
    accessibility_manager=_accessibility_manager,
    ux_manager=_ux_manager,
    query_processor=_query_processor,
    nlu_engine=_nlu_engine,
    user_id=None
)

# MCP Server Setup
server = Server("impressioncore-dpa")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List all available DPA tools"""
    return [
        Tool(
            name="analyze",
            description="Analyze user input and return NLUResult",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "User input text to analyze"}
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="get_intent",
            description="Extract only the intent from user input",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "User input text to extract intent from"}
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="get_entities",
            description="Extract only entities from user input",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "User input text to extract entities from"}
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="ids_update",
            description="Trigger IDS update operation",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="ids_tag",
            description="Trigger IDS tag operation",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="ids_sync",
            description="Trigger IDS sync operation",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="ids_status",
            description="Get IDS system status",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="ids_search",
            description="Search IDS documentation",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Query string for IDS search"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="ids_generate_docs",
            description="Trigger IDS documentation generation",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="shutdown",
            description="Shutdown the DPA server and all bridges",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="process_accessibility_request",
            description="Process a natural language accessibility or UX query.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Accessibility-related query"},
                    "user_context": {"type": "object", "description": "Optional user context", "default": {}}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_user_interface_config",
            description="Get user interface configuration for adaptive UI rendering.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User identifier"}
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="apply_accessibility_to_response",
            description="Apply accessibility transformations to a response.",
            inputSchema={
                "type": "object",
                "properties": {
                    "response": {"type": "string", "description": "Response text"},
                    "user_id": {"type": "string", "description": "User identifier"}
                },
                "required": ["response", "user_id"]
            }
        ),
        Tool(
            name="get_accessibility_integration_status",
            description="Get the current status of accessibility integration.",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="dpa_chronology_snapshot",
            description="Chronology snapshot (docs/source/mcp/root/all) creation-ordered",
            inputSchema={
                "type": "object",
                "properties": {
                    "kind": {"type": "string", "enum": ["all","docs","source","mcp","root"], "default": "all"},
                    "limit": {"type": "integer", "default": 40},
                    "reverse": {"type": "boolean", "default": False}
                }
            }
        ),
        Tool(
            name="dpa_chronology_delta",
            description="Chronology delta (added/removed/changed) if diff present",
            inputSchema={
                "type": "object",
                "properties": {
                    "include": {"type": "array", "items": {"type": "string", "enum": ["added","removed","changed"]}},
                    "limit": {"type": "integer", "default": 200}
                }
            }
        ),
        Tool(
            name="dpa_chronology_stats",
            description="Chronology statistics (counts per category + delta counts)",
            inputSchema={"type": "object", "properties": {}}
        ),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls for DPA tools"""
    try:
        if name == "analyze":
            text = arguments.get("text", "")
            result = await dpa_core.nlu.analyze_async(text)
            return [TextContent(type="text", text=str(result))]
        elif name == "get_intent":
            text = arguments.get("text", "")
            result = await dpa_core.nlu.get_intent_async(text)
            return [TextContent(type="text", text=str(result))]
        elif name == "get_entities":
            text = arguments.get("text", "")
            result = await dpa_core.nlu.get_entities_async(text)
            return [TextContent(type="text", text=str(result))]
        elif name == "ids_update":
            result = dpa_core.ids_update()
            return [TextContent(type="text", text=str(result))]
        elif name == "ids_tag":
            result = dpa_core.ids_tag()
            return [TextContent(type="text", text=str(result))]
        elif name == "ids_sync":
            result = dpa_core.ids_sync()
            return [TextContent(type="text", text=str(result))]
        elif name == "ids_status":
            result = dpa_core.ids_status()
            return [TextContent(type="text", text=str(result))]
        elif name == "ids_search":
            query = arguments.get("query", "")
            result = dpa_core.ids_search(query)
            return [TextContent(type="text", text=str(result))]
        elif name == "ids_generate_docs":
            result = dpa_core.ids_generate_docs()
            return [TextContent(type="text", text=str(result))]
        elif name == "shutdown":
            result = dpa_core.shutdown()
            return [TextContent(type="text", text=str(result))]
        # Accessibility tools
        elif name == "process_accessibility_request":
            query = arguments.get("query", "")
            user_context = arguments.get("user_context", {})
            result = accessibility.process_accessibility_request(query, user_context)
            return [TextContent(type="text", text=str(result))]
        elif name == "get_user_interface_config":
            user_id = arguments.get("user_id", "")
            result = accessibility.get_user_interface_config(user_id)
            return [TextContent(type="text", text=str(result))]
        elif name == "apply_accessibility_to_response":
            response = arguments.get("response", "")
            user_id = arguments.get("user_id", "")
            result = accessibility.apply_accessibility_to_response(response, user_id)
            return [TextContent(type="text", text=str(result))]
        elif name == "get_accessibility_integration_status":
            result = accessibility.get_integration_status()
            return [TextContent(type="text", text=str(result))]
        elif name == "dpa_chronology_snapshot":
            if not HAS_CHRONOLOGY:
                return [TextContent(type="text", text=str({"error": "chronology_loader_not_available"}))]
            data = load_chronology()
            kind = arguments.get('kind', 'all')
            limit = arguments.get('limit', 40)
            reverse = arguments.get('reverse', False)
            items = query_chronology(data, kind=kind, limit=limit, reverse=reverse)
            payload = {
                'kind': kind,
                'limit': limit,
                'reverse': reverse,
                'count': len(items),
                'items': items,
                'generated': data.get('generated'),
                'ordering': data.get('ordering'),
                'schema_version': data.get('schema_version')
            }
            return [TextContent(type="text", text=str(payload))]
        elif name == "dpa_chronology_delta":
            if not HAS_CHRONOLOGY:
                return [TextContent(type="text", text=str({"error": "chronology_loader_not_available"}))]
            diff = load_delta()
            if not diff:
                return [TextContent(type="text", text=str({"error": "delta_not_available", "hint": "Generate chronology with --delta in IDS."}))]
            include = arguments.get('include') or ['added','removed','changed']
            limit = arguments.get('limit', 200)
            payload = {'generated': diff.get('generated'), 'counts': diff.get('counts', {})}
            for key in ['added','removed','changed']:
                if key in include and key in diff:
                    data_slice = diff[key]
                    payload[key] = data_slice[:limit] if limit else data_slice
            return [TextContent(type="text", text=str(payload))]
        elif name == "dpa_chronology_stats":
            if not HAS_CHRONOLOGY:
                return [TextContent(type="text", text=str({"error": "chronology_loader_not_available"}))]
            data = load_chronology()
            stats = {
                'documents': len(data.get('documents', [])),
                'source': len(data.get('source', [])),
                'mcp': len(data.get('mcp', [])),
                'root': len(data.get('root', [])),
                'generated': data.get('generated'),
                'ordering': data.get('ordering'),
                'schema_version': data.get('schema_version')
            }
            diff = load_delta()
            if diff and diff.get('counts'):
                stats['delta'] = diff['counts']
            return [TextContent(type="text", text=str(stats))]
        else:
            return [TextContent(type="text", text=f"\u274c Unknown tool: {name}")]
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [TextContent(type="text", text=f"\u274c Error executing {name}: {str(e)}")]

from mcp.server.stdio import stdio_server

async def main():
    """Main server entry point for MCP event loop (stdio)"""
    logger.info("\U0001F680 Starting ImpressionCore DPA MCP Server...")
    from mcp.server.models import InitializationOptions
    initialization_options = InitializationOptions(
        server_name="ImpressionCore DPA",
        server_version="1.0.0",
        capabilities=ServerCapabilities(tools=ToolsCapability()),
        instructions=None
    )
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, initialization_options)

if __name__ == "__main__":
    asyncio.run(main())
