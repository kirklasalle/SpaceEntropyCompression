#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\ids_bridge.py #api #python #source_code  
**Category:** Source Code  
**Status:** Active
"""





import subprocess
import sys
from pathlib import Path

# Resolve project root and src path robustly
PROJECT_ROOT = Path(__file__).resolve().parents[2]
IDS_API_PATH = PROJECT_ROOT / 'src' / 'core' / 'utils' / 'ids_server_api.py'

class IDSBridge:
    """Bridge for DPA to control IDS server operations."""
    def __init__(self, ids_api_path=IDS_API_PATH):
        self.ids_api_path = str(ids_api_path)

    def update(self):
        return self._run_cmd(['update'])

    def tag(self):
        return self._run_cmd(['tag'])

    def sync(self):
        return self._run_cmd(['sync'])

    def status(self):
        return self._run_cmd(['status'])

    def search(self, query):
        return self._run_cmd(['search', query])

    def generate_docs(self):
        return self._run_cmd(['generate-docs'])

    def _run_cmd(self, args):
        cmd = [sys.executable, self.ids_api_path] + args
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"[IDSBridge Error] {e.stderr}"
