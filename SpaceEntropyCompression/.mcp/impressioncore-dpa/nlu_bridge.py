#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\nlu_bridge.py #memory_management #python #source_code #testing  
**Category:** Source Code  
**Status:** Active
"""





# Ensure project root is in sys.path for src imports
import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.services.assistant.nlp.nlu_engine import (
    NLUEngine,
    quick_analyze,            # async
    extract_intent_only,      # async
    extract_entities_only,    # async
    quick_analyze_sync,       # sync
    extract_intent_only_sync, # sync
    extract_entities_only_sync, # sync
)

class DPANLUBridge:
    """Bridge for DPA to use the NLU engine for user input analysis."""
    def __init__(self, max_memory_mb: int = 20):
        # NLUEngine expects a config dict; pass max_memory via config
        self.engine = NLUEngine({
            'max_memory_mb': max_memory_mb
        })

    def analyze(self, text: str):
        """Analyze user input and return a simple dict result (intent/entities/sentiment)."""
        # Use the provided synchronous wrapper which manages its own engine lifecycle
        return quick_analyze_sync(text)

    async def analyze_async(self, text: str):
        """Async analyze to be used when already inside an event loop (e.g., MCP server)."""
        return await quick_analyze(text)

    def get_intent(self, text: str):
        """Extract only the intent from user input."""
        return extract_intent_only_sync(text)

    async def get_intent_async(self, text: str):
        """Async intent extraction for event-loop contexts."""
        return await extract_intent_only(text)

    def get_entities(self, text: str):
        """Extract only entities from user input."""
        return extract_entities_only_sync(text)

    async def get_entities_async(self, text: str):
        """Async entities extraction for event-loop contexts."""
        return await extract_entities_only(text)

    def shutdown(self):
        """Safe no-op shutdown; underlying wrappers manage their own engine lifecycle."""
        return True

# Example usage for DPA integration
if __name__ == "__main__":
    bridge = DPANLUBridge()
    test_text = "Schedule a meeting for tomorrow at 2:00 PM"
    result = bridge.analyze(test_text)
    print(f"Intent: {result.intent.intent_type.value} (confidence: {result.intent.confidence:.2f})")
    print(f"Entities: {[ (e.text, e.entity_type.value) for e in result.entities ]}")
    if result.sentiment:
        print(f"Sentiment: polarity={result.sentiment.polarity:.2f}, confidence={result.sentiment.confidence:.2f}")
    bridge.shutdown()
