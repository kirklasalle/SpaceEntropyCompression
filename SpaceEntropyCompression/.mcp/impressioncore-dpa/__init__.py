#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\__init__.py #memory_management #python #source_code  
**Category:** Source Code  
**Status:** Active
"""









# Init

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\__init__.py #memory_management #python #source_code  
**Category:** Source Code  
**Status:** Active

"""
ImpressionCore Personal Assistant - Phase 8B MVP Implementation
============================================================

Core personal assistant capabilities leveraging ImpressionCore's brain-inspired
architecture for intelligent information processing and contextual assistance.

Phase 8B Components:
- Query Processing and Intent Classification
- Natural Language Understanding 
- Information Retrieval and Knowledge Access
- Context Management and Conversation State
- Response Generation and Multi-modal Output
- Task Management and Reminders Integration
- Accessibility and User Experience Enhancements (Week 3)

Author: ImpressionCore Development Team
Created: 2025-06-06 (Phase 8B Week 1)
Updated: 2025-01-06 (Phase 8B Week 3 - Accessibility & UX)
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
Memory Budget: 125MB total allocation
"""

from .core.query_processor import QueryProcessor
from .core.retrieval_engine import InformationRetrievalEngine
from .core.context_manager import ContextManager
from .core.response_generator import ResponseGenerator, create_response_generator

# Integration Components
from .integration.comprehensive_integration import AssistantIntegrationManager
from .integration import (
    TaskIntegrationManager, 
    TaskIntegration,
    AccessibilityIntegrationManager, 
    AccessibilityIntegration
)

# Accessibility and UX Components
from .accessibility import (
    AccessibilityManager,
    UserExperienceManager,
    AccessibilityProfile,
    UserPreferences
)

__version__ = "8B.3.0"
__phase__ = "8B Week 3 - Complete Integration with Accessibility & UX"

__all__ = [
    # Core Components
    'QueryProcessor',
    'InformationRetrievalEngine', 
    'ContextManager',
    'ResponseGenerator',
    'create_response_generator',
    
    # Comprehensive Integration
    'AssistantIntegrationManager',
    
    # Specialized Integrations
    'TaskIntegrationManager',
    'TaskIntegration',
    'AccessibilityIntegrationManager',
    'AccessibilityIntegration',
    
    # Accessibility and UX Management
    'AccessibilityManager',
    'UserExperienceManager',
    'UserAccessibilityProfile',
    'UserPersonalizationProfile'
]
