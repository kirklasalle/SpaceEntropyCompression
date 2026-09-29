#!/usr/bin/env python3
"""Accessibility and User Experience package for ImpressionCore DPA."""

from accessibility.accessibility_manager import (
    AccessibilityManager,
    AccessibilityProfile,
    AccessibilityLevel,
    MotorAbility,
    VisualAbility,
    AuditoryAbility,
    CognitiveAbility
)
from accessibility.user_experience_manager import (
    UserExperienceManager,
    UserPreferences,
    InteractionPattern,
    ExperienceLevel,
    InterfaceTheme,
    NotificationStyle,
    UsageAnalytics
)
from accessibility.accessibility_integration import (
    AccessibilityIntegrationManager,
    AccessibilityIntegration
)

__version__ = "8B.3.0"
__phase__ = "8B Week 3 - Accessibility & UX Enhancements"

__all__ = [
    # Accessibility Management
    'AccessibilityManager',
    'AccessibilityProfile',
    'AccessibilityLevel',
    'MotorAbility',
    'VisualAbility',
    'AuditoryAbility',
    'CognitiveAbility',

    # User Experience Management
    'UserExperienceManager',
    'UserPreferences',
    'InteractionPattern',
    'ExperienceLevel',
    'InterfaceTheme',
    'NotificationStyle',
    'UsageAnalytics',

    # Integration Components
    'AccessibilityIntegrationManager',
    'AccessibilityIntegration'
]

# Default accessibility and UX configuration
DEFAULT_ACCESSIBILITY_CONFIG = {
    'screen_reader_support': True,
    'high_contrast_mode': False,
    'large_text_mode': False,
    'keyboard_navigation': True,
    'audio_descriptions': False,
    'reduced_motion': False,
    'simplified_ui': False
}

DEFAULT_UX_CONFIG = {
    'interface_mode': 'adaptive',
    'theme_preference': 'system',
    'response_style': 'balanced',
    'interaction_style': 'conversational',
    'personalization_level': 'medium',
    'analytics_enabled': True,
    'feedback_collection': True
}
