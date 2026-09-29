#!/usr/bin/env python3
import sys
sys.path[:0] = [r'd:/Projects/impressioncore', r'd:/Projects/impressioncore/src']
from src.services.assistant.nlp.nlu_engine import quick_analyze_sync
print(quick_analyze_sync('Hello there'))
