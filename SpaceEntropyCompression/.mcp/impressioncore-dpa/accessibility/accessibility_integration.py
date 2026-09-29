#!/usr/bin/env python3
r"""
ImpressionCore DPA Accessibility Integration

Created: October-15-2024
Updated: August-04-2025
Author: ImpressionCore Team

Accessibility Integration Manager for ImpressionCore Personal Assistant.
This module integrates accessibility and UX features with the assistant,
providing adaptive interfaces via natural language.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import asyncio

from accessibility.accessibility_manager import AccessibilityManager, AccessibilityProfile, AccessibilityLevel
from accessibility.user_experience_manager import UserExperienceManager, UserPreferences, InteractionPattern
from core.query_processor import QueryProcessor
from nlp.nlu_engine import NLUEngine
from src.core.utils.rich_logging import setup_rich_logging
from src.core.utils.rich_status_animation import StatusAnimation


class AccessibilityIntegrationManager:
    """
    Integration layer that connects accessibility and UX management with
    the Personal Assistant Core components for seamless user adaptation.
    """
    
    def __init__(self, 
                 accessibility_manager: AccessibilityManager,
                 ux_manager: UserExperienceManager,
                 query_processor: Optional[QueryProcessor] = None,
                 nlu_engine: Optional[NLUEngine] = None,
                 user_id: Optional[str] = None):
        """Initialize accessibility integration manager"""
        self.logger = setup_rich_logging(__name__)
        self.user_id = user_id
        
        # Component references
        self.accessibility_manager = accessibility_manager
        self.ux_manager = ux_manager
        self.query_processor = query_processor
        self.nlu_engine = nlu_engine
        
        # Accessibility-specific intent mappings
        self.accessibility_intents = {
            'enable_accessibility': self._handle_enable_accessibility,
            'disable_accessibility': self._handle_disable_accessibility,
            'set_accessibility_preference': self._handle_set_accessibility_preference,
            'get_accessibility_status': self._handle_get_accessibility_status,
            'transform_content': self._handle_transform_content,
            'change_interface_mode': self._handle_change_interface_mode,
            'set_personalization': self._handle_set_personalization,
            'get_user_profile': self._handle_get_user_profile,
            'update_user_preferences': self._handle_update_user_preferences,
            'accessibility_help': self._handle_accessibility_help
        }
        
        # Initialize accessibility profiles for current user
        self._initialize_user_profiles()
        
        self.logger.info(
            f"AccessibilityIntegrationManager initialized | user_id={self.user_id} "
            f"registered_intents={len(self.accessibility_intents)}"
        )
    
    def _initialize_user_profiles(self) -> None:
        """Initialize user accessibility and UX profiles if they don't exist"""
        if self.user_id:
            try:
                # Check if profiles exist, create if not
                accessibility_profile = self.accessibility_manager.get_user_profile(self.user_id)
                if not accessibility_profile:
                    self.accessibility_manager.create_user_profile(self.user_id)
                
                ux_profile = self.ux_manager.get_user_profile(self.user_id)
                if not ux_profile:
                    self.ux_manager.create_user_profile(self.user_id)
                    
            except Exception as e:
                self.logger.warning(f"Failed to initialize user profiles: {e}")
    
    def process_accessibility_query(self, query: str, context: Optional[Any] = None) -> Dict[str, Any]:
        """
        Process a natural language query related to accessibility or UX
        
        Args:
            query: Natural language query
            context: Conversation context
        
        Returns:
            Processing result with accessibility actions and response
        """
        animation = StatusAnimation(
            total_steps=5,
            description="Processing accessibility query"
        )
        
        try:
            animation.start()
            
            # Step 1: Analyze query with NLU (if available)
            animation.update(1, "Analyzing query intent")
            if self.nlu_engine:
                nlu_result = self.nlu_engine.analyze_query(query, context)
            else:
                nlu_result = self._basic_intent_analysis(query)
            
            # Step 2: Extract accessibility-specific entities
            animation.update(2, "Extracting accessibility entities")
            entities = self._extract_accessibility_entities(query)
            
            # Step 3: Determine primary intent
            animation.update(3, "Determining accessibility intent")
            primary_intent = self._get_primary_accessibility_intent(nlu_result, entities, query)
            
            # Step 4: Execute accessibility action
            animation.update(4, "Executing accessibility action")
            if primary_intent in self.accessibility_intents:
                result = self.accessibility_intents[primary_intent](query, entities, context)
            else:
                result = self._handle_generic_accessibility_query(query, entities, context)
            
            # Step 5: Generate accessible response
            animation.update(5, "Generating accessible response")
            response = self._generate_accessible_response(result, primary_intent)
            
            animation.complete("Accessibility query processed successfully")
            
            return {
                'intent': primary_intent,
                'entities': entities,
                'result': result,
                'response': response,
                'success': True
            }
            
        except Exception as e:
            animation.fail(f"Failed to process accessibility query: {str(e)}")
            self.logger.error(
                f"Accessibility query processing failed | query={query} error={str(e)}"
            )
            
            return {
                'intent': None,
                'entities': {},
                'result': None,
                'response': f"I encountered an error processing your accessibility request: {str(e)}",
                'success': False
            }
    
    def _basic_intent_analysis(self, query: str) -> Dict[str, Any]:
        """Basic intent analysis when NLU engine is not available"""
        query_lower = query.lower()
        
        # Basic keyword matching for accessibility intents
        if any(word in query_lower for word in ['enable', 'turn on', 'activate']):
            if any(word in query_lower for word in ['accessibility', 'screen reader', 'high contrast']):
                return {'intent': 'enable_accessibility', 'confidence': 0.8}
        
        if any(word in query_lower for word in ['disable', 'turn off', 'deactivate']):
            if any(word in query_lower for word in ['accessibility', 'screen reader', 'high contrast']):
                return {'intent': 'disable_accessibility', 'confidence': 0.8}
        
        if any(word in query_lower for word in ['change', 'set', 'update']):
            if any(word in query_lower for word in ['interface', 'theme', 'mode']):
                return {'intent': 'change_interface_mode', 'confidence': 0.7}
        
        if any(word in query_lower for word in ['help', 'support', 'assistance']):
            if 'accessibility' in query_lower:
                return {'intent': 'accessibility_help', 'confidence': 0.9}
        
        return {'intent': 'generic_accessibility', 'confidence': 0.3}

    # --- Placeholder handler implementations (to be expanded) ---
    def _handle_enable_accessibility(self, query: str, entities: Dict[str, Any], context: Optional[Any]):
        return {'success': True, 'action': 'enable_accessibility', 'message': 'Accessibility enable stub'}

    def _handle_disable_accessibility(self, query: str, entities: Dict[str, Any], context: Optional[Any]):
        return {'success': True, 'action': 'disable_accessibility', 'message': 'Accessibility disable stub'}

    def _handle_set_accessibility_preference(self, query: str, entities: Dict[str, Any], context: Optional[Any]):
        return {'success': True, 'action': 'set_preference', 'message': 'Set preference stub'}

    def _handle_get_accessibility_status(self, query: str, entities: Dict[str, Any], context: Optional[Any]):
        return {'success': True, 'action': 'status', 'message': 'Status stub'}

    def _handle_transform_content(self, query: str, entities: Dict[str, Any], context: Optional[Any]):
        return {'success': True, 'action': 'transform', 'message': 'Transform stub'}

    def _handle_change_interface_mode(self, query: str, entities: Dict[str, Any], context: Optional[Any]):
        return {'success': True, 'action': 'change_interface_mode', 'message': 'Change mode stub'}

    def _handle_set_personalization(self, query: str, entities: Dict[str, Any], context: Optional[Any]):
        return {'success': True, 'action': 'set_personalization', 'message': 'Set personalization stub'}

    def _handle_get_user_profile(self, query: str, entities: Dict[str, Any], context: Optional[Any]):
        return {'success': True, 'action': 'get_user_profile', 'message': 'Get profile stub'}

    def _handle_update_user_preferences(self, query: str, entities: Dict[str, Any], context: Optional[Any]):
        return {'success': True, 'action': 'update_user_preferences', 'message': 'Update preferences stub'}

    def _handle_accessibility_help(self, query: str, entities: Dict[str, Any], context: Optional[Any]):
        return {'success': True, 'action': 'help', 'message': 'Accessibility help stub'}


class AccessibilityIntegration:
    """Backward-compatible wrapper expected by server.py.

    Historically the integration class was named `AccessibilityIntegration`.
    The refactor introduced `AccessibilityIntegrationManager` only; this shim
    preserves the original import path/identifier without changing server code.
    """

    def __init__(self, *args, **kwargs):
        # Build core components with proper dependency wiring
        accessibility_manager = AccessibilityManager()
        ux_manager = UserExperienceManager(accessibility_manager)
        query_processor = QueryProcessor()
        nlu_engine = NLUEngine()
        self._manager = AccessibilityIntegrationManager(
            accessibility_manager=accessibility_manager,
            ux_manager=ux_manager,
            query_processor=query_processor,
            nlu_engine=nlu_engine,
            user_id=kwargs.get("user_id")
        )

    def initialize(self):  # no-op for compatibility
        return True

    def process_accessibility_query(self, *args, **kwargs):
        return self._manager.process_accessibility_query(*args, **kwargs)

    # Expose other manager capabilities as needed
    def __getattr__(self, item):
        return getattr(self._manager, item)
    
    def _extract_accessibility_entities(self, query: str) -> Dict[str, Any]:
        """Extract accessibility-specific entities from query"""
        entities = {}
        query_lower = query.lower()
        
        # Accessibility features
        if 'screen reader' in query_lower:
            entities['accessibility_feature'] = 'screen_reader'
        elif 'high contrast' in query_lower:
            entities['accessibility_feature'] = 'high_contrast'
        elif 'large text' in query_lower or 'big font' in query_lower:
            entities['accessibility_feature'] = 'large_text'
        elif 'keyboard' in query_lower:
            entities['accessibility_feature'] = 'keyboard_navigation'
        elif 'audio' in query_lower:
            entities['accessibility_feature'] = 'audio_descriptions'
        elif 'motion' in query_lower:
            entities['accessibility_feature'] = 'reduced_motion'
        elif 'simple' in query_lower or 'simplified' in query_lower:
            entities['accessibility_feature'] = 'simplified_ui'
        
        # Interface modes
        if 'dark mode' in query_lower or 'dark theme' in query_lower:
            entities['interface_mode'] = 'dark'
        elif 'light mode' in query_lower or 'light theme' in query_lower:
            entities['interface_mode'] = 'light'
        elif 'adaptive' in query_lower:
            entities['interface_mode'] = 'adaptive'
        elif 'minimal' in query_lower:
            entities['interface_mode'] = 'minimal'
        elif 'full' in query_lower or 'complete' in query_lower:
            entities['interface_mode'] = 'full'
        
        # Accessibility levels
        if any(word in query_lower for word in ['basic', 'low', 'minimal']):
            entities['accessibility_level'] = AccessibilityLevel.BASIC
        elif any(word in query_lower for word in ['medium', 'moderate', 'standard']):
            entities['accessibility_level'] = AccessibilityLevel.ENHANCED
        elif any(word in query_lower for word in ['high', 'full', 'maximum', 'complete']):
            entities['accessibility_level'] = AccessibilityLevel.FULL
        
        return entities
    
    def _get_primary_accessibility_intent(self, nlu_result: Dict[str, Any], entities: Dict[str, Any], query: str) -> str:
        """Determine the primary accessibility intent"""
        if 'intent' in nlu_result:
            return nlu_result['intent']
        
        # Fallback to basic pattern matching
        query_lower = query.lower()
        
        if 'help' in query_lower and 'accessibility' in query_lower:
            return 'accessibility_help'
        elif any(word in query_lower for word in ['enable', 'activate', 'turn on']):
            return 'enable_accessibility'
        elif any(word in query_lower for word in ['disable', 'deactivate', 'turn off']):
            return 'disable_accessibility'
        elif 'status' in query_lower or 'current' in query_lower:
            return 'get_accessibility_status'
        elif any(word in query_lower for word in ['change', 'switch', 'set']) and 'mode' in query_lower:
            return 'change_interface_mode'
        elif 'profile' in query_lower:
            return 'get_user_profile'
        elif any(word in query_lower for word in ['preference', 'setting']):
            return 'update_user_preferences'
        
        return 'generic_accessibility'
    
    def _handle_enable_accessibility(self, query: str, entities: Dict[str, Any], context: Optional[Any]) -> Dict[str, Any]:
        """Handle accessibility enabling requests"""
        try:
            feature = entities.get('accessibility_feature')
            level = entities.get('accessibility_level', AccessibilityLevel.ENHANCED)
            
            if not self.user_id:
                return {'success': False, 'error': 'User ID required for accessibility settings'}
            
            if feature:
                # Enable specific feature
                success = self.accessibility_manager.enable_feature(self.user_id, feature)
                if success:
                    return {
                        'success': True,
                        'action': 'enabled_feature',
                        'feature': feature,
                        'message': f"Enabled {feature.replace('_', ' ')} accessibility feature"
                    }
                else:
                    return {'success': False, 'error': f'Failed to enable {feature}'}
            else:
                # Enable general accessibility with specified level
                profile = self.accessibility_manager.set_accessibility_level(self.user_id, level)
                return {
                    'success': True,
                    'action': 'enabled_accessibility',
                    'level': level.value,
                    'profile': profile,
                    'message': f"Enabled {level.value} accessibility level"
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_disable_accessibility(self, query: str, entities: Dict[str, Any], context: Optional[Any]) -> Dict[str, Any]:
        """Handle accessibility disabling requests"""
        try:
            feature = entities.get('accessibility_feature')
            
            if not self.user_id:
                return {'success': False, 'error': 'User ID required for accessibility settings'}
            
            if feature:
                # Disable specific feature
                success = self.accessibility_manager.disable_feature(self.user_id, feature)
                if success:
                    return {
                        'success': True,
                        'action': 'disabled_feature',
                        'feature': feature,
                        'message': f"Disabled {feature.replace('_', ' ')} accessibility feature"
                    }
                else:
                    return {'success': False, 'error': f'Failed to disable {feature}'}
            else:
                # Disable general accessibility
                profile = self.accessibility_manager.set_accessibility_level(self.user_id, AccessibilityLevel.BASIC)
                return {
                    'success': True,
                    'action': 'disabled_accessibility',
                    'profile': profile,
                    'message': "Disabled enhanced accessibility features"
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_change_interface_mode(self, query: str, entities: Dict[str, Any], context: Optional[Any]) -> Dict[str, Any]:
        """Handle interface mode change requests"""
        try:
            mode = entities.get('interface_mode')
            
            if not self.user_id:
                return {'success': False, 'error': 'User ID required for interface settings'}
            
            if not mode:
                return {'success': False, 'error': 'Interface mode not specified'}
            
            # Convert string to enum
            try:
                interface_mode = InteractionPattern(mode)
            except ValueError:
                return {'success': False, 'error': f'Invalid interface mode: {mode}'}
            
            # Update interface mode
            success = self.ux_manager.set_interface_mode(self.user_id, interface_mode)
            if success:
                return {
                    'success': True,
                    'action': 'changed_interface_mode',
                    'mode': mode,
                    'message': f"Changed interface to {mode} mode"
                }
            else:
                return {'success': False, 'error': f'Failed to change interface mode to {mode}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_get_accessibility_status(self, query: str, entities: Dict[str, Any], context: Optional[Any]) -> Dict[str, Any]:
        """Handle accessibility status requests"""
        try:
            if not self.user_id:
                return {'success': False, 'error': 'User ID required for accessibility status'}
            
            # Get accessibility profile
            accessibility_profile = self.accessibility_manager.get_user_profile(self.user_id)
            ux_profile = self.ux_manager.get_user_profile(self.user_id)
            
            return {
                'success': True,
                'action': 'status_retrieved',
                'accessibility_profile': accessibility_profile,
                'ux_profile': ux_profile,
                'message': "Retrieved current accessibility and user experience settings"
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_accessibility_help(self, query: str, entities: Dict[str, Any], context: Optional[Any]) -> Dict[str, Any]:
        """Handle accessibility help requests"""
        help_content = {
            'success': True,
            'action': 'accessibility_help',
            'help_content': {
                'available_features': [
                    'Screen reader support',
                    'High contrast mode',
                    'Large text mode',
                    'Keyboard navigation',
                    'Audio descriptions',
                    'Reduced motion',
                    'Simplified user interface'
                ],
                'interface_modes': [
                    'Adaptive (automatically adjusts)',
                    'Dark mode',
                    'Light mode',
                    'Minimal (simplified interface)',
                    'Full (all features visible)'
                ],
                'voice_commands': [
                    '"Enable screen reader"',
                    '"Turn on high contrast"',
                    '"Switch to dark mode"',
                    '"Set large text"',
                    '"Show accessibility status"'
                ]
            },
            'message': "Here are the available accessibility features and commands"
        }
        
        return help_content
    
    def _handle_generic_accessibility_query(self, query: str, entities: Dict[str, Any], context: Optional[Any]) -> Dict[str, Any]:
        """Handle generic accessibility queries"""
        return {
            'success': True,
            'action': 'generic_response',
            'message': "I can help you with accessibility settings. Try saying 'accessibility help' for available options."
        }
    
    def _generate_accessible_response(self, result: Dict[str, Any], intent: str) -> str:
        """Generate an accessible response based on the result and user's accessibility profile"""
        if not result.get('success', False):
            return result.get('message', 'An error occurred processing your accessibility request.')
        
        message = result.get('message', '')
        
        # Apply accessibility transformations if user has accessibility needs
        if self.user_id:
            try:
                accessibility_profile = self.accessibility_manager.get_user_profile(self.user_id)
                if accessibility_profile:
                    # Transform content for accessibility
                    transformed_content = self.accessibility_manager.transform_content(
                        self.user_id, message, 'text'
                    )
                    if transformed_content.get('success'):
                        message = transformed_content.get('transformed_content', message)
            except Exception as e:
                self.logger.warning(f"Failed to apply accessibility transformations: {e}")
        
        return message
    
    def apply_accessibility_to_response(self, response: str, user_id: Optional[str] = None) -> str:
        """Apply accessibility transformations to any response"""
        if not user_id:
            user_id = self.user_id
        
        if not user_id:
            return response
        
        try:
            transformed = self.accessibility_manager.transform_content(
                user_id, response, 'text'
            )
            if transformed.get('success'):
                return transformed.get('transformed_content', response)
        except Exception as e:
            self.logger.warning(f"Failed to apply accessibility to response: {e}")
        
        return response
    
    def get_user_interface_config(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get user interface configuration for adaptive UI rendering"""
        if not user_id:
            user_id = self.user_id
        
        if not user_id:
            return {}
        
        try:
            accessibility_profile = self.accessibility_manager.get_user_profile(user_id)
            ux_profile = self.ux_manager.get_user_profile(user_id)
            
            return {
                'accessibility': accessibility_profile.features if accessibility_profile else {},
                'interface_mode': ux_profile.interface_mode.value if ux_profile else 'adaptive',
                'theme_preference': ux_profile.preferences.get('theme_preference', 'system') if ux_profile else 'system',
                'personalization_level': ux_profile.personalization_level.value if ux_profile else 'medium'
            }
        except Exception as e:
            self.logger.warning(f"Failed to get user interface config: {e}")
            return {}

    def initialize(self, user_id: Optional[str] = None, **kwargs) -> bool:
        """Initialize the accessibility integration system.

        Args:
            user_id: Optional user identifier
            **kwargs: Additional configuration options

        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Initialize accessibility and UX managers
            accessibility_manager = AccessibilityManager()
            ux_manager = UserExperienceManager()
            
            # Create integration manager
            self.integration_manager = AccessibilityIntegrationManager(
                accessibility_manager=accessibility_manager,
                ux_manager=ux_manager,
                user_id=user_id,
                **kwargs
            )
            
            self._initialized = True
            self.logger.info("Accessibility integration initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize accessibility integration: {e}")
            return False
    
    def process_accessibility_request(self, query: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process an accessibility-related request.
        
        Args:
            query: Natural language query about accessibility
            user_context: Optional user context information
            
        Returns:
            Dictionary containing the response and any configuration changes
        """
        if not self.integration_manager:
            return {
                'success': False,
                'message': 'Accessibility integration manager not initialized',
                'config_changes': {}
            }
        
        try:
            # Create a mock conversation session for the query
            session = None  # ConversationSession placeholder removed
            
            # Process the query
            response = self.integration_manager.process_accessibility_query(query, session)
            
            return {
                'success': True,
                'message': response.get('response', ''),
                'config_changes': response.get('result', {}),
                'intent': response.get('intent')
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process accessibility request: {e}")
            return {
                'success': False,
                'message': f'Error processing accessibility request: {str(e)}',
                'config_changes': {}
            }
    
    def get_user_interface_config(self, user_id: str) -> Dict[str, Any]:
        """Get user interface configuration for adaptive rendering"""
        if not self.integration_manager:
            return {}
        
        return self.integration_manager.get_user_interface_config(user_id)
    
    def apply_accessibility_to_response(self, response: str, user_id: str) -> str:
        """Apply accessibility transformations to a response"""
        if not self.integration_manager:
            return response
        
        return self.integration_manager.apply_accessibility_to_response(response, user_id)
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get the current status of accessibility integration"""
        if not self.integration_manager:
            return {
                'initialized': False,
                'components': {}
            }
        
        return {
            'initialized': True,
            'components': {
                'accessibility_manager': self.integration_manager.accessibility_manager is not None,
                'ux_manager': self.integration_manager.ux_manager is not None,
                'query_processor': self.integration_manager.query_processor is not None,
                'nlu_engine': self.integration_manager.nlu_engine is not None
            }
        }
