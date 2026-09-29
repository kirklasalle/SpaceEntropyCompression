#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\nlp\nlu_engine.py #documentation #memory_management #python #source_code #testing  
**Category:** Source Code  
**Status:** Active
"""





import re
import time
import logging
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

# Core utilities and rich enhancements
from src.core.utils.rich_enhancements import create_panel, create_table
from src.core.utils.rich_logging import get_rich_logger
from src.core.utils.rich_status_animation import StatusAnimation

# Memory management
import psutil
import gc


class IntentType(Enum):
    """Enumeration of supported intent categories."""
    # Information seeking intents
    QUESTION = "question"
    SEARCH = "search"
    DEFINITION = "definition"
    EXPLANATION = "explanation"
    COMPARISON = "comparison"
    
    # Task management intents  
    CREATE_TASK = "create_task"
    UPDATE_TASK = "update_task"
    DELETE_TASK = "delete_task"
    LIST_TASKS = "list_tasks"
    SCHEDULE = "schedule"
    REMINDER = "reminder"
    
    # System control intents
    SYSTEM_STATUS = "system_status"
    CONFIGURATION = "configuration"
    HELP = "help"
    
    # Conversation management
    GREETING = "greeting"
    GOODBYE = "goodbye"
    CLARIFICATION = "clarification"
    CONFIRMATION = "confirmation"
    NEGATION = "negation"
    
    # Data operations
    SAVE = "save"
    LOAD = "load"
    DELETE = "delete"
    BACKUP = "backup"
    
    # Unknown/fallback
    UNKNOWN = "unknown"


class EntityType(Enum):
    """Enumeration of supported named entity types."""
    # Person and organization
    PERSON = "person"
    ORGANIZATION = "organization"
    
    # Temporal entities
    DATE = "date"
    TIME = "time"
    DURATION = "duration"
    
    # Location entities
    LOCATION = "location"
    ADDRESS = "address"
    
    # Technical entities
    FILE_PATH = "file_path"
    URL = "url"
    EMAIL = "email"
    PHONE = "phone"
    
    # Task-related entities
    TASK_NAME = "task_name"
    PRIORITY_LEVEL = "priority_level"
    STATUS = "status"
    
    # Numerical entities
    NUMBER = "number"
    PERCENTAGE = "percentage"
    MONEY = "money"
    
    # System entities
    COMMAND = "command"
    APPLICATION = "application"
    SETTING = "setting"


@dataclass
class Entity:
    """Represents a named entity with metadata."""
    text: str
    entity_type: EntityType
    start_pos: int
    end_pos: int
    confidence: float = 1.0
    normalized_value: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Intent:
    """Represents a classified intent with confidence."""
    intent_type: IntentType
    confidence: float
    supporting_features: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Sentiment:
    """Represents sentiment analysis results."""
    polarity: float  # -1.0 (negative) to 1.0 (positive)
    confidence: float
    subjectivity: float  # 0.0 (objective) to 1.0 (subjective)


@dataclass
class NLUResult:
    """Complete NLU analysis result."""
    text: str
    intent: Intent
    entities: List[Entity] = field(default_factory=list)
    sentiment: Optional[Sentiment] = None
    tokens: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class PatternMatcher:
    """Pattern-based entity recognition and intent classification."""
    
    def __init__(self):
        self.intent_patterns = self._load_intent_patterns()
        self.entity_patterns = self._load_entity_patterns()
        
    def _load_intent_patterns(self) -> Dict[IntentType, List[str]]:
        """Load intent recognition patterns."""
        return {
            IntentType.QUESTION: [
                r'\b(what|who|when|where|why|how|which)\b',
                r'\?$',
                r'\b(tell me|explain|describe)\b'
            ],
            IntentType.SEARCH: [
                r'\b(search|find|look for|locate)\b',
                r'\b(show me|display|list)\b'
            ],
            IntentType.CREATE_TASK: [
                r'\b(create|add|new|make)\b.*\b(task|todo|reminder)\b',
                r'\b(remind me|schedule)\b',
                r'\bneed to\b'
            ],
            IntentType.GREETING: [
                r'\b(hello|hi|hey|good morning|good afternoon|good evening)\b',
                r'\bhowdy\b'
            ],
            IntentType.GOODBYE: [
                r'\b(bye|goodbye|see you|farewell|exit|quit)\b',
                r'\bgood night\b'
            ],
            IntentType.HELP: [
                r'\b(help|assist|support)\b',
                r'\bhow do I\b',
                r'\bcan you help\b'
            ],
            IntentType.SYSTEM_STATUS: [
                r'\b(status|health|performance|stats)\b',
                r'\bhow.*doing\b',
                r'\bsystem.*running\b'
            ],
            IntentType.CONFIRMATION: [
                r'\b(yes|yeah|yep|correct|right|exactly|sure)\b',
                r'\bthat\'s right\b'
            ],
            IntentType.NEGATION: [
                r'\b(no|nope|wrong|incorrect|false)\b',
                r'\bthat\'s wrong\b'
            ]
        }
        
    def _load_entity_patterns(self) -> Dict[EntityType, List[str]]:
        """Load entity recognition patterns."""
        return {
            EntityType.DATE: [
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
                r'\b(today|tomorrow|yesterday)\b',
                r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
                r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b'
            ],
            EntityType.TIME: [
                r'\b\d{1,2}:\d{2}\s*(am|pm)?\b',
                r'\b(morning|afternoon|evening|night)\b',
                r'\bnoon\b|\bmidnight\b'
            ],
            EntityType.EMAIL: [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            EntityType.URL: [
                r'https?://[^\s<>"{}|\\^`\[\]]+',
                r'www\.[^\s<>"{}|\\^`\[\]]+'
            ],
            EntityType.PHONE: [
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                r'\(\d{3}\)\s*\d{3}[-.]?\d{4}\b'
            ],
            EntityType.FILE_PATH: [
                r'\b[A-Za-z]:\\[^<>:"|?*\n\r]*',
                r'\/[^<>:"|?*\n\r]*',
                r'\b\w+\.(txt|md|py|js|html|css|json|xml|csv)\b'
            ],
            EntityType.NUMBER: [
                r'\b\d+(\.\d+)?\b'
            ],
            EntityType.PRIORITY_LEVEL: [
                r'\b(high|medium|low|urgent|critical|normal)\b.*\b(priority|importance)\b',
                r'\b(priority|importance)\b.*\b(high|medium|low|urgent|critical|normal)\b'
            ]
        }
        
    def match_intent(self, text: str) -> List[Tuple[IntentType, float]]:
        """Match text against intent patterns."""
        text_lower = text.lower()
        matches = []
        
        for intent_type, patterns in self.intent_patterns.items():
            score = 0.0
            matched_patterns = 0
            
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    matched_patterns += 1
                    # Weight by pattern specificity (longer patterns get higher weight)
                    pattern_weight = len(pattern) / 100.0
                    score += pattern_weight
                    
            if matched_patterns > 0:
                # Normalize score by number of patterns for this intent
                normalized_score = min(1.0, score / len(patterns))
                matches.append((intent_type, normalized_score))
                
        # Sort by confidence
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
        
    def extract_entities(self, text: str) -> List[Entity]:
        """Extract entities using pattern matching."""
        entities = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    entity = Entity(
                        text=match.group(),
                        entity_type=entity_type,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=0.8  # Pattern-based confidence
                    )
                    entities.append(entity)
                    
        # Remove overlapping entities (keep highest confidence)
        entities = self._remove_overlapping_entities(entities)
        return entities
        
    def _remove_overlapping_entities(self, entities: List[Entity]) -> List[Entity]:
        """Remove overlapping entities, keeping those with highest confidence."""
        if not entities:
            return entities
            
        # Sort by position
        entities.sort(key=lambda e: e.start_pos)
        
        filtered = [entities[0]]
        for entity in entities[1:]:
            # Check if overlaps with last added entity
            last_entity = filtered[-1]
            if entity.start_pos >= last_entity.end_pos:
                # No overlap
                filtered.append(entity)
            elif entity.confidence > last_entity.confidence:
                # Higher confidence, replace
                filtered[-1] = entity
                
        return filtered


class SentimentAnalyzer:
    """Simple rule-based sentiment analysis."""
    
    def __init__(self):
        self.positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'like', 'enjoy', 'happy', 'pleased', 'satisfied', 'perfect',
            'awesome', 'brilliant', 'superb', 'outstanding', 'marvelous'
        }
        
        self.negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'angry',
            'frustrated', 'disappointed', 'annoyed', 'upset', 'sad', 'unhappy',
            'poor', 'worst', 'useless', 'broken', 'failed'
        }
        
        self.intensifiers = {
            'very': 1.5, 'really': 1.4, 'extremely': 1.8, 'incredibly': 1.6,
            'quite': 1.2, 'rather': 1.1, 'somewhat': 0.8, 'slightly': 0.7
        }
        
    def analyze(self, text: str) -> Sentiment:
        """Analyze sentiment of text."""
        words = text.lower().split()
        
        positive_score = 0.0
        negative_score = 0.0
        subjectivity_indicators = 0
        
        for i, word in enumerate(words):
            # Clean word
            clean_word = re.sub(r'[^\w]', '', word)
            
            # Check for intensifiers
            intensifier = 1.0
            if i > 0:
                prev_word = re.sub(r'[^\w]', '', words[i-1])
                intensifier = self.intensifiers.get(prev_word, 1.0)
                
            # Score sentiment
            if clean_word in self.positive_words:
                positive_score += 1.0 * intensifier
                subjectivity_indicators += 1
            elif clean_word in self.negative_words:
                negative_score += 1.0 * intensifier
                subjectivity_indicators += 1
                
        # Calculate polarity (-1 to 1)
        total_sentiment = positive_score + negative_score
        if total_sentiment > 0:
            polarity = (positive_score - negative_score) / total_sentiment
        else:
            polarity = 0.0
            
        # Calculate confidence based on strength of sentiment words
        confidence = min(1.0, total_sentiment / max(1, len(words) / 3))
        
        # Calculate subjectivity (0 to 1)
        subjectivity = min(1.0, subjectivity_indicators / max(1, len(words) / 2))
        
        return Sentiment(
            polarity=polarity,
            confidence=confidence,
            subjectivity=subjectivity
        )


class NLUMemoryManager:
    """Memory management for NLU operations."""
    
    def __init__(self, max_memory_mb: int = 20):
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.process = psutil.Process()
        self.baseline_memory = self.process.memory_info().rss
        
    def get_memory_usage(self) -> int:
        """Get current memory usage delta."""
        return self.process.memory_info().rss - self.baseline_memory
        
    def is_within_limits(self) -> bool:
        """Check if memory usage is within limits."""
        return self.get_memory_usage() < self.max_memory_bytes
        
    def cleanup(self):
        """Force memory cleanup."""
        gc.collect()


class NLUEngine:
    """
    Main Natural Language Understanding Engine for ImpressionCore Personal Assistant.
    
    Provides advanced intent recognition, entity extraction, and sentiment analysis
    optimized for GTX 1050 Ti memory constraints.
    """
    
    def __init__(self, max_memory_mb: int = 20):
        self.logger = get_rich_logger("nlu_engine")
        self.memory_manager = NLUMemoryManager(max_memory_mb)
        
        # Core components
        self.pattern_matcher = PatternMatcher()
        self.sentiment_analyzer = SentimentAnalyzer()
        
        # Statistics tracking
        self.stats = {
            "total_analyses": 0,
            "successful_analyses": 0,
            "intent_distribution": {intent.value: 0 for intent in IntentType},
            "average_processing_time": 0.0,
            "entity_counts": {entity.value: 0 for entity in EntityType}
        }
          # Status animation
        self.status_animation = StatusAnimation(total_steps=10, description="NLU Processing")
        
        self.logger.info(f"NLU Engine initialized with {max_memory_mb}MB memory limit")
        
    def analyze(self, text: str, include_sentiment: bool = True) -> NLUResult:
        """
        Perform complete NLU analysis on input text.
        
        Args:
            text: Input text to analyze
            include_sentiment: Whether to include sentiment analysis
            
        Returns:
            NLUResult with intent, entities, and optional sentiment
        """
        start_time = time.time()
        
        try:
            # Memory check
            if not self.memory_manager.is_within_limits():
                self.memory_manager.cleanup()
                self.logger.warning("Memory limit approached, performed cleanup")
            
            with self.status_animation.status(f"Analyzing: {text[:30]}..."):
                # Tokenization (simple whitespace for now)
                tokens = text.split()
                
                # Intent classification
                intent_matches = self.pattern_matcher.match_intent(text)
                if intent_matches:
                    best_intent = Intent(
                        intent_type=intent_matches[0][0],
                        confidence=intent_matches[0][1],
                        supporting_features=[f"pattern_match_{i}" for i, _ in enumerate(intent_matches[:3])]
                    )
                else:
                    best_intent = Intent(
                        intent_type=IntentType.UNKNOWN,
                        confidence=0.1
                    )
                
                # Entity extraction
                entities = self.pattern_matcher.extract_entities(text)
                
                # Sentiment analysis (if requested)
                sentiment = None
                if include_sentiment:
                    sentiment = self.sentiment_analyzer.analyze(text)
                
                # Calculate processing time
                processing_time = time.time() - start_time
                
                # Create result
                result = NLUResult(
                    text=text,
                    intent=best_intent,
                    entities=entities,
                    sentiment=sentiment,
                    tokens=tokens,
                    processing_time=processing_time,
                    metadata={
                        "memory_usage_mb": self.memory_manager.get_memory_usage() / (1024 * 1024),
                        "total_intent_matches": len(intent_matches),
                        "entity_count": len(entities)
                    }
                )
                
                # Update statistics
                self._update_stats(result)
                
                self.logger.debug(f"NLU analysis complete in {processing_time:.3f}s")
                return result
                
        except Exception as e:
            self.logger.error(f"Error during NLU analysis: {e}")
            # Return minimal result on error
            return NLUResult(
                text=text,
                intent=Intent(IntentType.UNKNOWN, 0.0),
                processing_time=time.time() - start_time
            )
            
    def _update_stats(self, result: NLUResult):
        """Update performance statistics."""
        self.stats["total_analyses"] += 1
        self.stats["successful_analyses"] += 1
        
        # Update intent distribution
        intent_value = result.intent.intent_type.value
        self.stats["intent_distribution"][intent_value] += 1
        
        # Update entity counts
        for entity in result.entities:
            entity_value = entity.entity_type.value
            self.stats["entity_counts"][entity_value] += 1
            
        # Update average processing time
        total_successful = self.stats["successful_analyses"]
        current_avg = self.stats["average_processing_time"]
        self.stats["average_processing_time"] = (
            (current_avg * (total_successful - 1) + result.processing_time) / total_successful
        )
        
    def batch_analyze(self, texts: List[str], include_sentiment: bool = True) -> List[NLUResult]:
        """
        Analyze multiple texts efficiently.
        
        Args:
            texts: List of texts to analyze
            include_sentiment: Whether to include sentiment analysis
            
        Returns:
            List of NLUResult objects
        """
        results = []
        
        with self.status_animation.status(f"Batch analyzing {len(texts)} texts..."):
            for text in texts:
                result = self.analyze(text, include_sentiment)
                results.append(result)
                
                # Memory cleanup between analyses if needed
                if not self.memory_manager.is_within_limits():
                    self.memory_manager.cleanup()
                    
        return results
        
    def get_supported_intents(self) -> List[IntentType]:
        """Get list of supported intent types."""
        return list(IntentType)
        
    def get_supported_entities(self) -> List[EntityType]:
        """Get list of supported entity types."""
        return list(EntityType)
        
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        memory_usage_mb = self.memory_manager.get_memory_usage() / (1024 * 1024)
        
        return {
            "analysis_performance": self.stats.copy(),
            "memory_usage": {
                "current_mb": memory_usage_mb,
                "max_allowed_mb": self.memory_manager.max_memory_bytes / (1024 * 1024),
                "within_limits": self.memory_manager.is_within_limits()
            },
            "supported_features": {
                "intent_types": len(IntentType),
                "entity_types": len(EntityType),
                "sentiment_analysis": True
            },
            "configuration": {
                "pattern_based_classification": True,
                "rule_based_sentiment": True,
                "memory_optimized": True
            }
        }
        
    def reset_stats(self):
        """Reset performance statistics."""
        self.stats = {
            "total_analyses": 0,
            "successful_analyses": 0,
            "intent_distribution": {intent.value: 0 for intent in IntentType},
            "average_processing_time": 0.0,
            "entity_counts": {entity.value: 0 for entity in EntityType}
        }
        self.logger.info("Performance statistics reset")
        
    def shutdown(self):
        """Shutdown the NLU engine and cleanup resources."""
        self.memory_manager.cleanup()
        self.logger.info("NLU Engine shutdown complete")


# Utility functions for easy integration

def quick_analyze(text: str, include_sentiment: bool = True) -> NLUResult:
    """Quick analysis utility for simple use cases."""
    engine = NLUEngine()
    try:
        return engine.analyze(text, include_sentiment)
    finally:
        engine.shutdown()


def extract_intent_only(text: str) -> IntentType:
    """Extract just the intent from text."""
    result = quick_analyze(text, include_sentiment=False)
    return result.intent.intent_type


def extract_entities_only(text: str) -> List[Entity]:
    """Extract just entities from text."""
    result = quick_analyze(text, include_sentiment=False)
    return result.entities


if __name__ == "__main__":
    # Example usage and testing
    def test_nlu():
        engine = NLUEngine()
        
        test_texts = [
            "What is the status of Phase 8B implementation?",
            "Create a task to review the documentation",
            "Hello, how are you doing today?",
            "Schedule a meeting for tomorrow at 2:00 PM",
            "I'm really frustrated with this system",
            "The file path is C:\\Projects\\impressioncore\\src\\assistant",
            "Send an email to john.doe@example.com about the meeting"
        ]
        
        print("Testing NLU Engine:")
        print("=" * 50)
        
        for text in test_texts:
            result = engine.analyze(text)
            
            print(f"Text: {text}")
            print(f"Intent: {result.intent.intent_type.value} (confidence: {result.intent.confidence:.2f})")
            print(f"Entities: {len(result.entities)}")
            for entity in result.entities:
                print(f"  - {entity.text} ({entity.entity_type.value})")
            if result.sentiment:
                print(f"Sentiment: polarity={result.sentiment.polarity:.2f}, confidence={result.sentiment.confidence:.2f}")
            print(f"Processing time: {result.processing_time:.3f}s")
            print("-" * 30)
            
        # Show performance stats
        stats = engine.get_performance_stats()
        print("\nPerformance Statistics:")
        print(f"Total analyses: {stats['analysis_performance']['total_analyses']}")
        print(f"Average processing time: {stats['analysis_performance']['average_processing_time']:.3f}s")
        print(f"Memory usage: {stats['memory_usage']['current_mb']:.1f}MB")
        
        engine.shutdown()
    
    # Run test if executed directly
    test_nlu()
