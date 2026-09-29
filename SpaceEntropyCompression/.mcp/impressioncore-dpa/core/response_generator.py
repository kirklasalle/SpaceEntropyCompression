#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\core\response_generator.py #memory_management #python #source_code  
**Category:** Source Code  
**Status:** Active
"""









# Response Generator

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\core\response_generator.py #memory_management #python #source_code  
**Category:** Source Code  
**Status:** Active

"""
Response Generator for ImpressionCore Personal Assistant

This module provides contextual response generation with multi-modal response planning,
personalization, and fact-based validation. Optimized for GTX 1050 Ti hardware 
constraints with 30MB memory budget.

Key Features:
- Contextual response generation
- Multi-modal response planning
- Response personalization
- Fact-based response validation
- Natural language generation optimization
- Memory-efficient response caching

Performance Targets:
- Response Generation: <1 second for standard queries
- Memory Usage: <30MB for active response generation
- Accuracy Rate: >85% factual accuracy
- Personalization: Context-aware adaptation

Author: ImpressionCore Development Team
Date: 2025-01-06
Phase: 8B Week 1 - Personal Assistant Core Foundation
"""

import time
import logging
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set, Union, Generator
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import threading
from collections import defaultdict, deque
import re

# Core imports
from src.core.utils.rich_logging import setup_rich_logging
from src.assistant.core.context_manager import ConversationSession
from src.assistant.nlp.nlu_engine import Intent, Entity

try:
    from src.core.utils.rich_enhancements import RichEnhancer
    from src.core.utils.rich_status_animation import StatusAnimation
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    
    class StatusAnimation:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def update(self, *args, **kwargs):
            pass

# Configuration and types
@dataclass
class ResponseConfig:
    """Configuration for response generation"""
    max_response_length: int = 500
    temperature: float = 0.7
    top_p: float = 0.9
    memory_limit_mb: int = 30
    cache_size: int = 100
    enable_personalization: bool = True
    enable_fact_checking: bool = True
    response_timeout: float = 1.0

class ResponseFormat(Enum):
    """Supported response formats"""
    TEXT = "text"
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"

@dataclass
class GeneratedResponse:
    """Container for generated response"""
    content: str
    format: ResponseFormat
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    processing_time: float = 0.0
    memory_usage: float = 0.0

@dataclass
class ResponseTemplate:
    """Template for response generation"""
    pattern: str
    variables: List[str]
    format: ResponseFormat
    category: str

@dataclass
class KnowledgeResult:
    """Knowledge retrieval result"""
    content: str
    confidence: float
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class ResponseGenerator:
    """
    Advanced response generator with contextual understanding and multi-modal capabilities.
    
    Features:
    - Template-based response generation
    - Context-aware personalization
    - Fact-based validation
    - Memory optimization
    - Response caching
    """
    
    def __init__(self, config: ResponseConfig = None):
        """Initialize the response generator"""
        self.config = config or ResponseConfig()
        self.logger = setup_rich_logging(__name__)
        
        # Response generation components
        self.templates: Dict[str, List[ResponseTemplate]] = {}
        self.response_cache: Dict[str, GeneratedResponse] = {}
        self.personalization_data: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Performance tracking
        self.performance_metrics = {
            'total_responses': 0,
            'avg_processing_time': 0.0,
            'cache_hits': 0,
            'memory_usage': 0.0
        }
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Initialize templates
        self._initialize_templates()
        
        self.logger.info("Response Generator initialized successfully")
    
    def _initialize_templates(self):
        """Initialize response templates"""
        self.templates = {
            'greeting': [
                ResponseTemplate(
                    pattern="Hello! How can I help you today?",
                    variables=[],
                    format=ResponseFormat.TEXT,
                    category="greeting"
                )
            ],
            'information': [
                ResponseTemplate(
                    pattern="Based on the information I found: {content}",
                    variables=['content'],
                    format=ResponseFormat.TEXT,
                    category="information"
                )
            ],
            'error': [
                ResponseTemplate(
                    pattern="I apologize, but I encountered an issue: {error}",
                    variables=['error'],
                    format=ResponseFormat.TEXT,
                    category="error"
                )
            ],
            'fallback': [
                ResponseTemplate(
                    pattern="I understand you're asking about {topic}, but I need more information to provide a helpful response.",
                    variables=['topic'],
                    format=ResponseFormat.TEXT,
                    category="fallback"
                )
            ]
        }
    
    def generate_response(self,
                         query: str,
                         intent: Intent,
                         entities: List[Entity],
                         context: ConversationSession,
                         facts: List[KnowledgeResult] = None,
                         response_format: ResponseFormat = ResponseFormat.TEXT) -> GeneratedResponse:
        """
        Generate a contextual response based on query, intent, and context.
        
        Args:
            query: User query string
            intent: Detected intent
            entities: Extracted entities
            context: Conversation context
            facts: Retrieved knowledge facts
            response_format: Desired response format
            
        Returns:
            GeneratedResponse object with generated content
        """
        start_time = time.time()
        
        try:
            with StatusAnimation(
                total_steps=5,
                description="Generating response"
            ) if RICH_AVAILABLE else self._null_context():
                
                # Check cache first
                cache_key = self._generate_cache_key(query, intent, entities)
                if cache_key in self.response_cache:
                    self.performance_metrics['cache_hits'] += 1
                    return self.response_cache[cache_key]
                
                # Generate contextual response
                response = self._generate_contextual_response(
                    query, intent, entities, context, facts, response_format
                )
                
                # Cache the response
                if len(self.response_cache) < self.config.cache_size:
                    self.response_cache[cache_key] = response
                
                # Update metrics
                processing_time = time.time() - start_time
                response.processing_time = processing_time
                self._update_metrics(processing_time)
                
                return response
                
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return self._generate_error_response(str(e), response_format)
    
    def _generate_contextual_response(self,
                                    query: str,
                                    intent: Intent,
                                    entities: List[Entity],
                                    context: ConversationSession,
                                    facts: List[KnowledgeResult] = None,
                                    response_format: ResponseFormat = ResponseFormat.TEXT) -> GeneratedResponse:
        """Generate contextual response with personalization"""
        
        # Determine response template category
        template_category = self._determine_template_category(intent)
        
        # Select appropriate template
        template = self._select_template(template_category, context)
        
        # Generate response content
        content = self._generate_content(template, query, intent, entities, facts, context)
        
        # Apply personalization
        if self.config.enable_personalization:
            content = self._apply_personalization(content, context)
        
        # Validate facts if enabled
        confidence = 0.8  # Default confidence
        if self.config.enable_fact_checking and facts:
            confidence = self._validate_facts(content, facts)
        
        return GeneratedResponse(
            content=content,
            format=response_format,
            confidence=confidence,
            metadata={
                'template_category': template_category,
                'entity_count': len(entities),
                'fact_count': len(facts) if facts else 0,
                'context_turns': len(context.messages) if hasattr(context, 'messages') else 0
            }
        )
    
    def _determine_template_category(self, intent: Intent) -> str:
        """Determine template category based on intent"""
        intent_name = intent.name.lower() if hasattr(intent, 'name') else str(intent).lower()
        
        if 'greet' in intent_name or 'hello' in intent_name:
            return 'greeting'
        elif 'information' in intent_name or 'search' in intent_name or 'find' in intent_name:
            return 'information'
        else:
            return 'fallback'
    
    def _select_template(self, category: str, context: ConversationSession) -> ResponseTemplate:
        """Select appropriate template based on category and context"""
        templates = self.templates.get(category, self.templates['fallback'])
        
        # For now, return the first template
        # In future versions, implement more sophisticated selection
        return templates[0]
    
    def _generate_content(self,
                         template: ResponseTemplate,
                         query: str,
                         intent: Intent,
                         entities: List[Entity],
                         facts: List[KnowledgeResult],
                         context: ConversationSession) -> str:
        """Generate content using template and context"""
        
        content = template.pattern
        
        # Replace template variables
        if 'content' in template.variables and facts:
            fact_content = "; ".join([fact.content for fact in facts[:3]])  # Limit to 3 facts
            content = content.replace('{content}', fact_content)
        
        if 'topic' in template.variables:
            # Extract topic from entities or query
            topic = "your request"
            if entities:
                entity_texts = [entity.text for entity in entities if hasattr(entity, 'text')]
                if entity_texts:
                    topic = entity_texts[0]
            content = content.replace('{topic}', topic)
        
        if 'error' in template.variables:
            content = content.replace('{error}', "processing your request")
        
        return content
    
    def _apply_personalization(self, content: str, context: ConversationSession) -> str:
        """Apply personalization based on context"""
        # Simple personalization - in production, this would be more sophisticated
        return content
    
    def _validate_facts(self, content: str, facts: List[KnowledgeResult]) -> float:
        """Validate response against facts and return confidence score"""
        if not facts:
            return 0.5
        
        # Simple validation - check if fact content appears in response
        fact_matches = 0
        for fact in facts:
            if any(word in content.lower() for word in fact.content.lower().split()[:5]):
                fact_matches += 1
        
        # Calculate confidence based on fact matches
        return min(0.9, 0.5 + (fact_matches / len(facts)) * 0.4)
    
    def _generate_cache_key(self, query: str, intent: Intent, entities: List[Entity]) -> str:
        """Generate cache key for response"""
        key_components = [
            query.lower(),
            str(intent),
            str(len(entities))
        ]
        key_string = "|".join(key_components)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _generate_error_response(self, error: str, response_format: ResponseFormat) -> GeneratedResponse:
        """Generate error response"""
        template = self.templates['error'][0]
        content = template.pattern.replace('{error}', error)
        
        return GeneratedResponse(
            content=content,
            format=response_format,
            confidence=0.0,
            metadata={'error': True}
        )
    
    def _update_metrics(self, processing_time: float):
        """Update performance metrics"""
        with self._lock:
            self.performance_metrics['total_responses'] += 1
            current_avg = self.performance_metrics['avg_processing_time']
            total_responses = self.performance_metrics['total_responses']
            
            # Update rolling average
            self.performance_metrics['avg_processing_time'] = (
                (current_avg * (total_responses - 1) + processing_time) / total_responses
            )
    
    def _null_context(self):
        """Null context manager for when rich is not available"""
        class NullContext:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
        return NullContext()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return self.performance_metrics.copy()
    
    def clear_cache(self):
        """Clear response cache"""
        with self._lock:
            self.response_cache.clear()
            self.logger.info("Response cache cleared")
    
    def get_cache_size(self) -> int:
        """Get current cache size"""
        return len(self.response_cache)

# Factory function for creating response generator
def create_response_generator(config: ResponseConfig = None) -> ResponseGenerator:
    """Create and configure a response generator instance"""
    return ResponseGenerator(config)

# Export classes for external use
__all__ = [
    'ResponseGenerator',
    'ResponseConfig', 
    'ResponseFormat',
    'GeneratedResponse',
    'ResponseTemplate',
    'KnowledgeResult',
    'create_response_generator'
]
