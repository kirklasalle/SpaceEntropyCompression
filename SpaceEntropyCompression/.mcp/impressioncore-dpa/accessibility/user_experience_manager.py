#!/usr/bin/env python3
r"""
User Experience Manager

Created: October-15-2024
Updated: August 4, 2025 10:26:57 AM
Author: ImpressionCore Team
Tags: #.mcp\impressioncore_dpa\accessibility\user_experience_manager.py #api #python #source_code
Category: Source Code
Status: Active

User Experience Enhancement Manager for ImpressionCore Personal Assistant.
This module implements comprehensive user experience enhancements including
adaptive interfaces, personalization, and intelligent user interaction patterns.
Builds upon the accessibility framework to provide optimal user experiences.

Version: 1.0
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import asyncio

from accessibility.accessibility_manager import AccessibilityManager, AccessibilityProfile
from src.core.utils.rich_logging import setup_rich_logging
from src.core.utils.rich_status_animation import StatusAnimation


class InteractionPattern(Enum):
    """User interaction patterns"""
    CONVERSATIONAL = "conversational"
    TASK_ORIENTED = "task_oriented"
    EXPLORATORY = "exploratory"
    TUTORIAL = "tutorial"
    QUICK_ACCESS = "quick_access"


class ExperienceLevel(Enum):
    """User experience levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class InterfaceTheme(Enum):
    """Interface theme options"""
    LIGHT = "light"
    DARK = "dark"
    HIGH_CONTRAST = "high_contrast"
    COLORFUL = "colorful"
    MINIMAL = "minimal"
    CUSTOM = "custom"


class NotificationStyle(Enum):
    """Notification style preferences"""
    SUBTLE = "subtle"
    STANDARD = "standard"
    PROMINENT = "prominent"
    URGENT_ONLY = "urgent_only"
    DISABLED = "disabled"


@dataclass
class UserPreferences:
    """Comprehensive user preferences for UX customization"""
    user_id: str
    
    # Interface preferences
    theme: InterfaceTheme = InterfaceTheme.LIGHT
    font_size: str = "medium"  # small, medium, large, extra_large
    animation_speed: str = "normal"  # slow, normal, fast, disabled
    layout_density: str = "comfortable"  # compact, comfortable, spacious
    
    # Interaction preferences
    interaction_pattern: InteractionPattern = InteractionPattern.CONVERSATIONAL
    experience_level: ExperienceLevel = ExperienceLevel.INTERMEDIATE
    keyboard_shortcuts: bool = True
    gesture_controls: bool = False
    voice_feedback: bool = False
    
    # Notification preferences
    notification_style: NotificationStyle = NotificationStyle.STANDARD
    notification_sound: bool = True
    notification_vibration: bool = False
    quiet_hours_start: Optional[str] = "22:00"
    quiet_hours_end: Optional[str] = "08:00"
    
    # Personalization
    preferred_name: Optional[str] = None
    language: str = "en-US"
    timezone: str = "UTC"
    
    # Advanced preferences
    detailed_explanations: bool = True
    show_confidence_scores: bool = False
    remember_context: bool = True
    auto_save_sessions: bool = True
    
    # Usage patterns (automatically learned)
    most_used_features: List[str] = field(default_factory=list)
    preferred_response_length: str = "medium"  # brief, medium, detailed
    typical_session_duration: int = 30  # minutes
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class UsageAnalytics:
    """User usage analytics for personalization"""
    user_id: str
    
    # Session statistics
    total_sessions: int = 0
    total_interaction_time: timedelta = field(default_factory=lambda: timedelta(0))
    average_session_duration: timedelta = field(default_factory=lambda: timedelta(minutes=30))
    
    # Feature usage
    feature_usage_count: Dict[str, int] = field(default_factory=dict)
    preferred_features: List[str] = field(default_factory=list)
    
    # Interaction patterns
    peak_usage_hours: List[int] = field(default_factory=list)
    common_query_types: Dict[str, int] = field(default_factory=dict)
    error_patterns: Dict[str, int] = field(default_factory=dict)
    
    # Success metrics
    task_completion_rate: float = 0.85
    user_satisfaction_score: float = 4.2  # out of 5
    response_relevance_score: float = 0.90
    
    last_updated: datetime = field(default_factory=datetime.now)


class UserExperienceManager:
    """
    Comprehensive user experience management system.
    
    Handles personalization, adaptive interfaces, and intelligent
    user interaction optimization based on usage patterns and preferences.
    """
    
    def __init__(self, accessibility_manager: AccessibilityManager):
        """Initialize user experience manager"""
        self.logger = setup_rich_logging(__name__)
        self.accessibility_manager = accessibility_manager
        
        # User data storage
        self.user_preferences: Dict[str, UserPreferences] = {}
        self.usage_analytics: Dict[str, UsageAnalytics] = {}
        
        # Adaptive learning
        self.learning_enabled = True
        self.adaptation_threshold = 0.7  # Confidence threshold for automatic adaptations
        
        # Interface customization
        self.available_themes = list(InterfaceTheme)
        self.supported_languages = ["en-US", "es-ES", "fr-FR", "de-DE", "zh-CN", "ja-JP"]
        
        self.logger.info(
            f"UserExperienceManager initialized | available_themes={len(self.available_themes)} "
            f"supported_languages={len(self.supported_languages)} learning_enabled={self.learning_enabled}"
        )
    
    async def create_user_profile(self, user_id: str, **initial_preferences) -> UserPreferences:
        """
        Create a new user experience profile
        
        Args:
            user_id: User identifier
            **initial_preferences: Initial preference settings
        
        Returns:
            Created user preferences profile
        """
        animation = StatusAnimation(
            total_steps=4,
            description=f"Creating UX profile for {user_id}"
        )
        
        try:
            animation.start()
            
            # Step 1: Create preferences
            animation.update(1, "Creating preferences profile")
            preferences = UserPreferences(user_id=user_id, **initial_preferences)
            
            # Step 2: Initialize analytics
            animation.update(2, "Initializing usage analytics")
            analytics = UsageAnalytics(user_id=user_id)
            
            # Step 3: Apply intelligent defaults
            animation.update(3, "Applying intelligent defaults")
            await self._apply_intelligent_defaults(preferences)
            
            # Step 4: Store profiles
            animation.update(4, "Storing profiles")
            self.user_preferences[user_id] = preferences
            self.usage_analytics[user_id] = analytics
            
            animation.complete(f"UX profile created for {user_id}")
            
            self.logger.info(
                "User experience profile created | "
                f"user_id={user_id} theme={preferences.theme.value} "
                f"experience_level={preferences.experience_level.value} pattern={preferences.interaction_pattern.value}"
            )
            
            return preferences
            
        except Exception as e:
            animation.fail(f"Failed to create UX profile: {str(e)}")
            self.logger.error(
                f"Failed to create UX profile | user_id={user_id} error={str(e)}"
            )
            raise
    
    async def _apply_intelligent_defaults(self, preferences: UserPreferences):
        """Apply intelligent defaults based on accessibility profile"""
        
        # Get accessibility profile if available
        accessibility_profile = await self.accessibility_manager.get_profile(preferences.user_id)
        
        if accessibility_profile:
            # Adjust theme based on visual needs
            if accessibility_profile.high_contrast:
                preferences.theme = InterfaceTheme.HIGH_CONTRAST
            
            # Adjust font size
            if accessibility_profile.large_text:
                preferences.font_size = "extra_large"
            
            # Adjust animations
            if accessibility_profile.reduced_motion:
                preferences.animation_speed = "disabled"
            
            # Adjust interaction patterns
            if accessibility_profile.voice_control:
                preferences.voice_feedback = True
                preferences.interaction_pattern = InteractionPattern.CONVERSATIONAL
            
            # Adjust notifications
            if accessibility_profile.auditory_ability.value in ["hard_of_hearing", "deaf"]:
                preferences.notification_sound = False
                preferences.notification_vibration = True
            
            # Adjust complexity based on cognitive needs
            if accessibility_profile.simplified_ui:
                preferences.experience_level = ExperienceLevel.BEGINNER
                preferences.layout_density = "spacious"
                preferences.detailed_explanations = True
    
    async def update_preferences(self, user_id: str, **updates) -> UserPreferences:
        """
        Update user preferences
        
        Args:
            user_id: User identifier
            **updates: Preference updates
        
        Returns:
            Updated preferences
        """
        if user_id not in self.user_preferences:
            raise ValueError(f"No UX profile found for user {user_id}")
        
        preferences = self.user_preferences[user_id]
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(preferences, key):
                setattr(preferences, key, value)
        
        preferences.updated_at = datetime.now()
        
        self.logger.info(
            f"User preferences updated | user_id={user_id} updates={list(updates.keys())}"
        )
        
        return preferences
    
    async def record_interaction(self, user_id: str, 
                               feature: str, 
                               interaction_type: str,
                               success: bool = True,
                               duration: Optional[timedelta] = None):
        """
        Record user interaction for analytics and learning
        
        Args:
            user_id: User identifier
            feature: Feature used
            interaction_type: Type of interaction
            success: Whether interaction was successful
            duration: Time spent on interaction
        """
        if user_id not in self.usage_analytics:
            # Create analytics profile if it doesn't exist
            self.usage_analytics[user_id] = UsageAnalytics(user_id=user_id)
        
        analytics = self.usage_analytics[user_id]
        
        # Update feature usage
        analytics.feature_usage_count[feature] = analytics.feature_usage_count.get(feature, 0) + 1
        
        # Update interaction time
        if duration:
            analytics.total_interaction_time += duration
        
        # Update common query types
        analytics.common_query_types[interaction_type] = analytics.common_query_types.get(interaction_type, 0) + 1
        
        # Update error patterns if not successful
        if not success:
            analytics.error_patterns[feature] = analytics.error_patterns.get(feature, 0) + 1
        
        analytics.last_updated = datetime.now()
        
        # Trigger adaptive learning if enabled
        if self.learning_enabled:
            await self._trigger_adaptive_learning(user_id)
    
    async def _trigger_adaptive_learning(self, user_id: str):
        """Trigger adaptive learning based on usage patterns"""
        
        if user_id not in self.usage_analytics or user_id not in self.user_preferences:
            return
        
        analytics = self.usage_analytics[user_id]
        preferences = self.user_preferences[user_id]
        
        # Update preferred features
        sorted_features = sorted(analytics.feature_usage_count.items(), 
                               key=lambda x: x[1], reverse=True)
        analytics.preferred_features = [feature for feature, count in sorted_features[:5]]
        
        # Adapt experience level based on feature usage complexity
        advanced_features = ['api_integration', 'custom_scripts', 'advanced_search']
        advanced_usage = sum(analytics.feature_usage_count.get(feature, 0) for feature in advanced_features)
        
        if advanced_usage > 10 and preferences.experience_level == ExperienceLevel.BEGINNER:
            preferences.experience_level = ExperienceLevel.INTERMEDIATE
            self.logger.info(
                f"Auto-upgraded user experience level | user_id={user_id} new_level={ExperienceLevel.INTERMEDIATE.value}"
            )
        
        # Adapt interface based on usage patterns
        peak_hour = max(analytics.peak_usage_hours) if analytics.peak_usage_hours else 12
        if 22 <= peak_hour or peak_hour <= 6:  # Night usage
            if preferences.theme == InterfaceTheme.LIGHT:
                preferences.theme = InterfaceTheme.DARK
                self.logger.info(
                    f"Auto-switched to dark theme for night usage | user_id={user_id}"
                )
    
    async def get_personalized_interface(self, user_id: str) -> Dict[str, Any]:
        """
        Get personalized interface configuration
        
        Args:
            user_id: User identifier
        
        Returns:
            Personalized interface configuration
        """
        if user_id not in self.user_preferences:
            # Return default configuration
            return await self._get_default_interface()
        
        preferences = self.user_preferences[user_id]
        analytics = self.usage_analytics.get(user_id)
        accessibility_profile = await self.accessibility_manager.get_profile(user_id)
        
        interface_config = {
            "theme": {
                "name": preferences.theme.value,
                "font_size": preferences.font_size,
                "animation_speed": preferences.animation_speed,
                "layout_density": preferences.layout_density
            },
            "interaction": {
                "pattern": preferences.interaction_pattern.value,
                "experience_level": preferences.experience_level.value,
                "keyboard_shortcuts": preferences.keyboard_shortcuts,
                "gesture_controls": preferences.gesture_controls,
                "voice_feedback": preferences.voice_feedback
            },
            "notifications": {
                "style": preferences.notification_style.value,
                "sound": preferences.notification_sound,
                "vibration": preferences.notification_vibration,
                "quiet_hours": {
                    "start": preferences.quiet_hours_start,
                    "end": preferences.quiet_hours_end
                }
            },
            "personalization": {
                "preferred_name": preferences.preferred_name,
                "language": preferences.language,
                "timezone": preferences.timezone,
                "response_length": preferences.preferred_response_length,
                "show_confidence": preferences.show_confidence_scores
            }
        }
        
        # Add frequently used features for quick access
        if analytics:
            interface_config["quick_access"] = {
                "features": analytics.preferred_features[:3],
                "recent_queries": list(analytics.common_query_types.keys())[:5]
            }
        
        # Apply accessibility overrides
        if accessibility_profile:
            interface_config["accessibility"] = {
                "screen_reader": accessibility_profile.screen_reader,
                "high_contrast": accessibility_profile.high_contrast,
                "large_text": accessibility_profile.large_text,
                "reduced_motion": accessibility_profile.reduced_motion,
                "voice_control": accessibility_profile.voice_control,
                "keyboard_navigation": True
            }
        
        return interface_config
    
    async def _get_default_interface(self) -> Dict[str, Any]:
        """Get default interface configuration"""
        return {
            "theme": {
                "name": InterfaceTheme.LIGHT.value,
                "font_size": "medium",
                "animation_speed": "normal",
                "layout_density": "comfortable"
            },
            "interaction": {
                "pattern": InteractionPattern.CONVERSATIONAL.value,
                "experience_level": ExperienceLevel.INTERMEDIATE.value,
                "keyboard_shortcuts": True,
                "gesture_controls": False,
                "voice_feedback": False
            },
            "notifications": {
                "style": NotificationStyle.STANDARD.value,
                "sound": True,
                "vibration": False,
                "quiet_hours": {
                    "start": "22:00",
                    "end": "08:00"
                }
            },
            "personalization": {
                "preferred_name": None,
                "language": "en-US",
                "timezone": "UTC",
                "response_length": "medium",
                "show_confidence": False
            },
            "accessibility": {
                "screen_reader": False,
                "high_contrast": False,
                "large_text": False,
                "reduced_motion": False,
                "voice_control": False,
                "keyboard_navigation": True
            }
        }
    
    async def get_adaptive_suggestions(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get adaptive suggestions based on user patterns
        
        Args:
            user_id: User identifier
        
        Returns:
            List of adaptive suggestions
        """
        if user_id not in self.usage_analytics:
            return []
        
        analytics = self.usage_analytics[user_id]
        suggestions = []
        
        # Suggest features based on usage patterns
        if analytics.total_sessions > 10:
            # Suggest keyboard shortcuts if frequently used
            frequently_used = [f for f, count in analytics.feature_usage_count.items() if count > 5]
            if frequently_used and user_id in self.user_preferences:
                preferences = self.user_preferences[user_id]
                if not preferences.keyboard_shortcuts:
                    suggestions.append({
                        "type": "feature_enhancement",
                        "title": "Enable Keyboard Shortcuts",
                        "description": "You frequently use certain features. Keyboard shortcuts could speed up your workflow.",
                        "action": "enable_keyboard_shortcuts",
                        "confidence": 0.8
                    })
        
        # Suggest theme changes based on usage time
        night_usage = sum(1 for hour in analytics.peak_usage_hours if 20 <= hour or hour <= 6)
        if night_usage > len(analytics.peak_usage_hours) * 0.6:  # More than 60% night usage
            if user_id in self.user_preferences:
                preferences = self.user_preferences[user_id]
                if preferences.theme == InterfaceTheme.LIGHT:
                    suggestions.append({
                        "type": "theme_optimization",
                        "title": "Switch to Dark Theme",
                        "description": "You often use ImpressionCore in the evening. Dark theme might be easier on your eyes.",
                        "action": "switch_to_dark_theme",
                        "confidence": 0.9
                    })
        
        # Suggest accessibility features if error patterns indicate struggle
        error_rate = sum(analytics.error_patterns.values()) / max(sum(analytics.feature_usage_count.values()), 1)
        if error_rate > 0.2:  # More than 20% error rate
            suggestions.append({
                "type": "accessibility_help",
                "title": "Consider Accessibility Features",
                "description": "Some accessibility features might help improve your experience.",
                "action": "review_accessibility_options",
                "confidence": 0.7
            })
        
        return suggestions
    
    async def apply_automatic_optimizations(self, user_id: str) -> List[str]:
        """
        Apply automatic optimizations based on user patterns
        
        Args:
            user_id: User identifier
        
        Returns:
            List of applied optimizations
        """
        if user_id not in self.user_preferences or user_id not in self.usage_analytics:
            return []
        
        optimizations = []
        preferences = self.user_preferences[user_id]
        analytics = self.usage_analytics[user_id]
        
        # Auto-optimize response length based on reading patterns
        avg_interaction_time = analytics.total_interaction_time.total_seconds() / max(analytics.total_sessions, 1)
        
        if avg_interaction_time < 30 and preferences.preferred_response_length == "detailed":
            preferences.preferred_response_length = "brief"
            optimizations.append("Switched to brief responses for quick interactions")
        elif avg_interaction_time > 120 and preferences.preferred_response_length == "brief":
            preferences.preferred_response_length = "detailed"
            optimizations.append("Switched to detailed responses for thorough interactions")
        
        # Auto-enable features based on usage
        if analytics.feature_usage_count.get("voice_commands", 0) > 10 and not preferences.voice_feedback:
            preferences.voice_feedback = True
            optimizations.append("Enabled voice feedback for voice command users")
        
        # Update preferences timestamp
        if optimizations:
            preferences.updated_at = datetime.now()
            
            self.logger.info(
                f"Applied automatic optimizations | user_id={user_id} optimizations={optimizations}"
            )
        
        return optimizations
    
    async def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive user insights and analytics
        
        Args:
            user_id: User identifier
        
        Returns:
            User insights and analytics
        """
        if user_id not in self.usage_analytics:
            return {"error": "No analytics data available"}
        
        analytics = self.usage_analytics[user_id]
        preferences = self.user_preferences.get(user_id)
        
        insights = {
            "usage_summary": {
                "total_sessions": analytics.total_sessions,
                "total_time": str(analytics.total_interaction_time),
                "average_session": str(analytics.average_session_duration),
                "task_completion_rate": analytics.task_completion_rate,
                "satisfaction_score": analytics.user_satisfaction_score
            },
            "behavioral_patterns": {
                "preferred_features": analytics.preferred_features,
                "peak_usage_hours": analytics.peak_usage_hours,
                "common_queries": analytics.common_query_types,
                "interaction_pattern": preferences.interaction_pattern.value if preferences else "unknown"
            },
            "optimization_opportunities": await self.get_adaptive_suggestions(user_id),
            "accessibility_usage": {},
            "experience_trajectory": {
                "current_level": preferences.experience_level.value if preferences else "unknown",
                "feature_adoption_rate": len(analytics.feature_usage_count) / max(analytics.total_sessions, 1),
                "error_rate": sum(analytics.error_patterns.values()) / max(sum(analytics.feature_usage_count.values()), 1)
            }
        }
        
        # Add accessibility insights if profile exists
        accessibility_profile = await self.accessibility_manager.get_profile(user_id)
        if accessibility_profile:
            insights["accessibility_usage"] = {
                "screen_reader": accessibility_profile.screen_reader,
                "voice_control": accessibility_profile.voice_control,
                "high_contrast": accessibility_profile.high_contrast,
                "simplified_ui": accessibility_profile.simplified_ui
            }
        
        return insights
    
    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Export all user data for privacy compliance
        
        Args:
            user_id: User identifier
        
        Returns:
            Complete user data export
        """
        export_data = {
            "user_id": user_id,
            "export_timestamp": datetime.now().isoformat(),
            "preferences": None,
            "analytics": None,
            "accessibility_profile": None
        }
        
        # Export preferences
        if user_id in self.user_preferences:
            preferences = self.user_preferences[user_id]
            export_data["preferences"] = {
                "theme": preferences.theme.value,
                "font_size": preferences.font_size,
                "animation_speed": preferences.animation_speed,
                "layout_density": preferences.layout_density,
                "interaction_pattern": preferences.interaction_pattern.value,
                "experience_level": preferences.experience_level.value,
                "language": preferences.language,
                "timezone": preferences.timezone,
                "created_at": preferences.created_at.isoformat(),
                "updated_at": preferences.updated_at.isoformat()
            }
        
        # Export analytics (anonymized)
        if user_id in self.usage_analytics:
            analytics = self.usage_analytics[user_id]
            export_data["analytics"] = {
                "total_sessions": analytics.total_sessions,
                "total_interaction_time": str(analytics.total_interaction_time),
                "feature_usage_count": analytics.feature_usage_count,
                "common_query_types": analytics.common_query_types,
                "task_completion_rate": analytics.task_completion_rate,
                "user_satisfaction_score": analytics.user_satisfaction_score,
                "last_updated": analytics.last_updated.isoformat()
            }
        
        # Export accessibility profile
        accessibility_profile = await self.accessibility_manager.get_profile(user_id)
        if accessibility_profile:
            export_data["accessibility_profile"] = {
                "visual_ability": accessibility_profile.visual_ability.value,
                "auditory_ability": accessibility_profile.auditory_ability.value,
                "motor_ability": accessibility_profile.motor_ability.value,
                "cognitive_ability": accessibility_profile.cognitive_ability.value,
                "preferences": {
                    "high_contrast": accessibility_profile.high_contrast,
                    "large_text": accessibility_profile.large_text,
                    "screen_reader": accessibility_profile.screen_reader,
                    "voice_control": accessibility_profile.voice_control
                }
            }
        
        self.logger.info(
            f"User data exported | user_id={user_id} data_types={[key for key, value in export_data.items() if value is not None]}"
        )
        
        return export_data
    
    async def delete_user_data(self, user_id: str) -> bool:
        """
        Delete all user data for privacy compliance
        
        Args:
            user_id: User identifier
        
        Returns:
            Success status
        """
        deleted_items = []
        
        # Delete preferences
        if user_id in self.user_preferences:
            del self.user_preferences[user_id]
            deleted_items.append("preferences")
        
        # Delete analytics
        if user_id in self.usage_analytics:
            del self.usage_analytics[user_id]
            deleted_items.append("analytics")
        
        self.logger.info(
            f"User data deleted | user_id={user_id} deleted_items={deleted_items}"
        )
        
        return len(deleted_items) > 0
