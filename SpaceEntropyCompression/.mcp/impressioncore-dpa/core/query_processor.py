#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\core\query_processor.py #cuda #memory_management #python #source_code #testing  
**Category:** Source Code  
**Status:** Active
"""









# Query Processor

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\core\query_processor.py #cuda #memory_management #python #source_code #testing  
**Category:** Source Code  
**Status:** Active

"""
ImpressionCore Query Processor 
===============================================

Natural language query parsing and intent classification system optimized for
GTX 1050 Ti hardware constraints with memory-efficient processing.

Features:
- Intent classification (20+ categories)
- Entity extraction and recognition
- Query preprocessing and normalization
- Memory-optimized operation (<15MB allocation)

Author: ImpressionCore Development Team
Created: 2025-06-06 (Phase 8B Week 1 - Day 1)
Memory Target: 15MB
Hardware Target: NVIDIA GTX 1050 Ti
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import torch
from datetime import datetime

# Import ImpressionCore utilities
try:
    from src.core.utils.rich_enhancements import create_enhanced_panel
    from src.core.utils.rich_logging import get_logger
    from src.core.utils.rich_status_animation import StatusAnimation
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    logging.basicConfig(level=logging.INFO)

class IntentCategory(Enum):
    """Supported intent categories for query classification."""
    # Information Retrieval
    SEARCH = "search"
    QUESTION = "question" 
    DEFINITION = "definition"
    EXPLANATION = "explanation"
    
    # Task Management
    REMINDER = "reminder"
    SCHEDULE = "schedule"
    TODO = "todo"
    DEADLINE = "deadline"
    
    # Communication
    MESSAGE = "message"
    EMAIL = "email"
    CALL = "call"
    
    # System Control
    SETTINGS = "settings"
    PREFERENCES = "preferences"
    SYSTEM_INFO = "system_info"
    
    # Entertainment & Media
    MUSIC = "music"
    VIDEO = "video"
    GAMES = "games"
    
    # Productivity
    CALCULATE = "calculate"
    CONVERT = "convert"
    TRANSLATE = "translate"
    
    # General
    GREETING = "greeting"
    HELP = "help"
    UNKNOWN = "unknown"

@dataclass
class EntityExtraction:
    """Extracted entity with type and confidence."""
    text: str
    entity_type: str
    start_pos: int
    end_pos: int
    confidence: float
    metadata: Dict[str, Any]

@dataclass
class QueryAnalysis:
    """Complete query analysis result."""
    original_query: str
    normalized_query: str
    intent: IntentCategory
    intent_confidence: float
    entities: List[EntityExtraction]
    keywords: List[str]
    sentiment: str
    priority: str
    processing_time_ms: float
    memory_usage_mb: float

class QueryProcessor:
    """
    Memory-efficient query processor for natural language understanding.
      Optimized for GTX 1050 Ti with <15MB memory allocation target.
    Provides intent classification, entity extraction, and query normalization.
    """
    
    def __init__(self, device: Optional[str] = None, memory_limit_mb: int = 15):
        """
        Initialize query processor with memory constraints.
        
        Args:
            device: Target device ('cuda', 'cpu', or None for auto-detection)
            memory_limit_mb: Maximum memory allocation in MB
        """
        self.memory_limit_mb = memory_limit_mb
        self.logger = get_logger(__name__) if HAS_RICH else logging.getLogger(__name__)
        self.device = self._setup_device(device)
        
        # Memory tracking
        self._memory_usage = 0.0
        self._query_count = 0
        
        # Initialize components
        self._setup_intent_patterns()
        self._setup_entity_patterns()
        self._setup_normalization_rules()
        
        self.logger.info(f"Query Processor initialized on {self.device} with {memory_limit_mb}MB limit")
    
    def _setup_device(self, device: Optional[str]) -> str:
        """Setup computing device with automatic fallback."""
        if device is None:
            if torch.cuda.is_available():
                device = "cuda"
                self.logger.info(f"Using CUDA device: {torch.cuda.get_device_name(0)}")
            else:
                device = "cpu"
                self.logger.info("Using CPU device")
        return device
    
    def _setup_intent_patterns(self) -> None:
        """Setup intent classification patterns."""
        self.intent_patterns = {
            IntentCategory.SEARCH: [
                r"\b(search|find|look for|locate)\b",
                r"\bwhere (is|are|can)\b",
                r"\bshow me\b"
            ],
            IntentCategory.QUESTION: [
                r"\b(what|how|why|when|where|who)\b",
                r"\?\s*$",
                r"\btell me about\b"
            ],
            IntentCategory.DEFINITION: [
                r"\bwhat (is|are|does|means?)\b",
                r"\bdefine\b",
                r"\bmeaning of\b"
            ],
            IntentCategory.REMINDER: [
                r"\bremind me\b",
                r"\bset (a )?reminder\b",
                r"\bdon't forget\b"
            ],
            IntentCategory.SCHEDULE: [
                r"\bschedule\b",
                r"\bappointment\b",
                r"\bmeeting\b",
                r"\bcalendar\b"
            ],
            IntentCategory.CALCULATE: [
                r"\bcalculate\b",
                r"\bcompute\b",
                r"\bmath\b",
                r"[\+\-\*\/\=]"
            ],
            IntentCategory.GREETING: [
                r"\b(hello|hi|hey|good morning|good afternoon|good evening)\b",
                r"\bhow are you\b"
            ],
            IntentCategory.HELP: [
                r"\bhelp\b",
                r"\bassist\b",
                r"\bsupport\b",
                r"\bhow to\b"
            ]
        }
    
    def _setup_entity_patterns(self) -> None:
        """Setup entity extraction patterns."""
        self.entity_patterns = {
            "DATE": [
                r"\b(today|tomorrow|yesterday)\b",
                r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
                r"\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b",
                r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\b"
            ],
            "TIME": [
                r"\b\d{1,2}:\d{2}\s*(am|pm)?\b",
                r"\b(morning|afternoon|evening|night)\b",
                r"\bat\s+\d{1,2}\b"
            ],
            "PERSON": [
                r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b",
                r"\b(mr|mrs|ms|dr|prof)\.?\s+[A-Z][a-z]+\b"
            ],
            "LOCATION": [
                r"\b[A-Z][a-z]+,\s*[A-Z]{2}\b",
                r"\bat\s+[A-Z][a-z\s]+\b"
            ],
            "NUMBER": [
                r"\b\d+\b",
                r"\b(one|two|three|four|five|six|seven|eight|nine|ten)\b"
            ],
            "EMAIL": [
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
            ],
            "PHONE": [
                r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
                r"\(\d{3}\)\s*\d{3}[-.]?\d{4}\b"
            ]
        }
    
    def _setup_normalization_rules(self) -> None:
        """Setup query normalization rules."""
        self.normalization_rules = [
            (r"\s+", " "),  # Multiple spaces to single space
            (r"[^\w\s\?\!\.]", ""),  # Remove special characters except basic punctuation
            (r"\b(please|could you|can you|would you)\b", ""),  # Remove politeness markers
            (r"\b(um|uh|er|ah)\b", ""),  # Remove filler words
        ]
    
    def process_query(self, query: str) -> QueryAnalysis:
        """
        Process a natural language query with full analysis.
        
        Args:
            query: Input query string
            
        Returns:
            QueryAnalysis: Complete analysis results
        """
        start_time = datetime.now()
        
        try:
            # Memory check
            if self._check_memory_limit():
                self.logger.warning(f"Approaching memory limit ({self.memory_limit_mb}MB)")
            
            # Normalize query
            normalized_query = self._normalize_query(query)
            
            # Classify intent
            intent, intent_confidence = self._classify_intent(normalized_query)
            
            # Extract entities
            entities = self._extract_entities(normalized_query)
            
            # Extract keywords
            keywords = self._extract_keywords(normalized_query)
            
            # Analyze sentiment
            sentiment = self._analyze_sentiment(normalized_query)
            
            # Determine priority
            priority = self._determine_priority(intent, entities)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Update counters
            self._query_count += 1
            
            result = QueryAnalysis(
                original_query=query,
                normalized_query=normalized_query,
                intent=intent,
                intent_confidence=intent_confidence,
                entities=entities,
                keywords=keywords,
                sentiment=sentiment,
                priority=priority,
                processing_time_ms=processing_time,
                memory_usage_mb=self._get_memory_usage()
            )
            
            self.logger.info(f"Processed query: {intent.value} ({intent_confidence:.2f}) in {processing_time:.1f}ms")
            return result
            
        except Exception as e:
            self.logger.error(f"Query processing error: {e}")
            # Return safe fallback
            return QueryAnalysis(
                original_query=query,
                normalized_query=query.lower().strip(),
                intent=IntentCategory.UNKNOWN,
                intent_confidence=0.0,
                entities=[],
                keywords=[],
                sentiment="neutral",
                priority="normal",
                processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                memory_usage_mb=self._get_memory_usage()
            )
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query text for processing."""
        normalized = query.lower().strip()
        
        for pattern, replacement in self.normalization_rules:
            normalized = re.sub(pattern, replacement, normalized)
        
        return normalized.strip()
    
    def _classify_intent(self, query: str) -> Tuple[IntentCategory, float]:
        """Classify query intent with confidence score."""
        scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0.0
            for pattern in patterns:
                matches = len(re.findall(pattern, query, re.IGNORECASE))
                score += matches * 0.3  # Base score per match
            
            if score > 0:
                scores[intent] = min(score, 1.0)  # Cap at 1.0
        
        if not scores:
            return IntentCategory.UNKNOWN, 0.0
        
        best_intent = max(scores.keys(), key=lambda x: scores[x])
        confidence = scores[best_intent]
        
        return best_intent, confidence
    
    def _extract_entities(self, query: str) -> List[EntityExtraction]:
        """Extract entities from query."""
        entities = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, query, re.IGNORECASE)
                for match in matches:
                    entity = EntityExtraction(
                        text=match.group(),
                        entity_type=entity_type,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=0.8,  # Simple confidence score
                        metadata={"pattern": pattern}
                    )
                    entities.append(entity)
        
        return entities
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query."""
        # Simple keyword extraction - remove stopwords
        stopwords = {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
            'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
            'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
            'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
            'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
            'while', 'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after',
            'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
            'further', 'then', 'once'
        }
        
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if word not in stopwords and len(word) > 2]
        
        return keywords[:10]  # Limit to top 10 keywords
    
    def _analyze_sentiment(self, query: str) -> str:
        """Simple sentiment analysis."""
        positive_words = ['good', 'great', 'excellent', 'wonderful', 'amazing', 'love', 'like', 'happy', 'pleased']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'angry', 'frustrated', 'upset', 'disappointed']
        
        words = query.lower().split()
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _determine_priority(self, intent: IntentCategory, entities: List[EntityExtraction]) -> str:
        """Determine query priority based on intent and entities."""
        high_priority_intents = {IntentCategory.REMINDER, IntentCategory.SCHEDULE, IntentCategory.DEADLINE}
        
        # Check for time-sensitive entities
        has_time_entity = any(e.entity_type in ['DATE', 'TIME'] for e in entities)
        
        if intent in high_priority_intents or has_time_entity:
            return "high"
        elif intent in {IntentCategory.HELP, IntentCategory.SYSTEM_INFO}:
            return "low"
        else:
            return "normal"
    
    def _check_memory_limit(self) -> bool:
        """Check if approaching memory limit."""
        current_usage = self._get_memory_usage()
        return current_usage > (self.memory_limit_mb * 0.8)
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        if torch.cuda.is_available() and self.device == "cuda":
            return torch.cuda.memory_allocated() / 1024 / 1024
        else:
            # Simplified CPU memory estimation
            return min(self._query_count * 0.1, self.memory_limit_mb * 0.5)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processor statistics."""
        return {
            "queries_processed": self._query_count,
            "memory_usage_mb": self._get_memory_usage(),
            "memory_limit_mb": self.memory_limit_mb,
            "device": self.device,
            "supported_intents": len(self.intent_patterns),
            "supported_entities": len(self.entity_patterns)
        }
    
    def clear_cache(self) -> None:
        """Clear internal caches to free memory."""
        if torch.cuda.is_available() and self.device == "cuda":
            torch.cuda.empty_cache()
        
        self.logger.info("Query processor cache cleared")

def create_query_processor() -> QueryProcessor:
    """
    Factory function to create and configure a QueryProcessor instance.
    
    Returns:
        QueryProcessor: Configured query processor instance
    """
    return QueryProcessor()


# Example usage and testing
if __name__ == "__main__":
    # Initialize processor
    processor = QueryProcessor(memory_limit_mb=15)
    
    # Test queries
    test_queries = [
        "What is machine learning?",
        "Remind me to call John at 3 PM tomorrow",
        "Schedule a meeting with the team next Monday",
        "How do I calculate compound interest?",
        "Search for restaurants near downtown",
        "Hello, how are you today?",
        "Help me with setting up my calendar"
    ]
    
    print("ImpressionCore Query Processor Testing")
    print("=" * 60)
    
    for query in test_queries:
        result = processor.process_query(query)
        print(f"\nQuery: {query}")
        print(f"Intent: {result.intent.value} (confidence: {result.intent_confidence:.2f})")
        print(f"Entities: {[e.text for e in result.entities]}")
        print(f"Keywords: {result.keywords}")
        print(f"Priority: {result.priority}")
        print(f"Processing time: {result.processing_time_ms:.1f}ms")
    
    # Show stats
    stats = processor.get_stats()
    print(f"\nProcessor Stats:")
    print(f"Queries processed: {stats['queries_processed']}")
    print(f"Memory usage: {stats['memory_usage_mb']:.1f}MB / {stats['memory_limit_mb']}MB")
    print(f"Device: {stats['device']}")
