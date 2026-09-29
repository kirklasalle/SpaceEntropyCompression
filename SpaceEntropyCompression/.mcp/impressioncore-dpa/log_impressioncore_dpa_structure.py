#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\log_impressioncore_dpa_structure.py #python #source_code  
**Category:** Source Code  
**Status:** Active
"""









# Log Impressioncore Dpa Structure

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\log_impressioncore_dpa_structure.py #python #source_code  
**Category:** Source Code  
**Status:** Active

"""
Script: log_impressioncore_dpa_structure.py
Logs the complete directory structure and full file contents of .mcp/impressioncore-dpa/ to a single log file for analysis.

Author: ImpressionCore Copilot
Created: 2025-07-01
"""

import os
from pathlib import Path

LOG_PATH = Path(__file__).parent / 'impressioncore_dpa_full_log.txt'
DPA_ROOT = Path(__file__).parent


def log_structure_and_contents(root: Path, log_path: Path):
    with open(log_path, 'w', encoding='utf-8') as log:
        for dirpath, dirnames, filenames in os.walk(root):
            rel_dir = os.path.relpath(dirpath, root)
            log.write(f"\n# Directory: {rel_dir}\n")
            for fname in filenames:
                fpath = Path(dirpath) / fname
                log.write(f"\n## File: {os.path.relpath(fpath, root)}\n")
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    log.write(content)
                except Exception as e:
                    log.write(f"\n[Error reading file: {e}]\n")

if __name__ == "__main__":
    log_structure_and_contents(DPA_ROOT, LOG_PATH)
    print(f"Log written to {LOG_PATH}")
