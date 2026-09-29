#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\core\context_manager.py #memory_management #python #security #source_code #testing  
**Category:** Source Code  
**Status:** Active
"""









# Context Manager

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\core\context_manager.py #memory_management #python #security #source_code #testing  
**Category:** Source Code  
**Status:** Active

"""
Context Manager for ImpressionCore Personal Assistant

This module implements conversation state management and context tracking
optimized for GTX 1050 Ti hardware constraints (10MB memory budget).

Key Features:
- Conversation state management
- Long-term context retention
- Context switching for multi-topic conversations
- Memory-efficient context storage
- Context relevance scoring
- Multi-turn conversation understanding

Performance Targets:
- Context Retention: 10 conversation turns minimum
- Memory Usage: <10MB for active context
- Context Switching: <100ms average
- Relevance Scoring: >85% accuracy

Author: ImpressionCore Development Team
Date: 2025-06-06
Phase: 8B Week 1 - Personal Assistant Core Foundation
"""

import time
import logging
import json
import uuid
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
from collections import deque, defaultdict
from enum import Enum
import hashlib
import threading
from pathlib import Path

# Core utilities and rich enhancements
from src.core.utils.rich_enhancements import create_panel, create_table
from src.core.utils.rich_logging import get_rich_logger
from src.core.utils.rich_status_animation import StatusAnimation

# Memory management
import psutil
import gc

# Import related assistant components
from src.assistant.nlp.nlu_engine import NLUResult, IntentType, EntityType


class ContextType(Enum):
    """Types of context in conversations."""
    CONVERSATIONAL = "conversational"  # Ongoing conversation context
    TASK_ORIENTED = "task_oriented"    # Task execution context
    TOPICAL = "topical"                # Subject matter context
    TEMPORAL = "temporal"              # Time-based context
    SPATIAL = "spatial"                # Location-based context
    EMOTIONAL = "emotional"            # Emotional/sentiment context
    SYSTEM = "system"                  # System state context


class ContextPriority(Enum):
    """Priority levels for context retention."""
    CRITICAL = 5    # Must retain (security, active tasks)
    HIGH = 4        # Important for current conversation
    MEDIUM = 3      # Relevant background information
    LOW = 2         # Nice to have context
    MINIMAL = 1     # Can be discarded under memory pressure


@dataclass
class ConversationTurn:
    """Represents a single turn in conversation."""
    turn_id: str
    timestamp: float
    user_input: str
    nlu_result: Optional[NLUResult] = None
    system_response: Optional[str] = None
    context_updates: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextItem:
    """Individual piece of context information."""
    key: str
    value: Any
    context_type: ContextType
    priority: ContextPriority
    timestamp: float
    expiry_time: Optional[float] = None
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    source_turn_id: Optional[str] = None
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if context item has expired."""
        if self.expiry_time is None:
            return False
        return time.time() > self.expiry_time
        
    def access(self):
        """Mark context item as accessed."""
        self.access_count += 1
        self.last_accessed = time.time()


@dataclass
class ConversationSession:
    """Represents a conversation session with context."""
    session_id: str
    start_time: float
    last_activity: float
    turns: deque = field(default_factory=lambda: deque(maxlen=50))
    context: Dict[str, ContextItem] = field(default_factory=dict)
    topic_history: List[str] = field(default_factory=list)
    active_tasks: Dict[str, Any] = field(default_factory=dict)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_turn(self, turn: ConversationTurn):
        """Add a conversation turn to the session."""
        self.turns.append(turn)
        self.last_activity = time.time()
        
    def get_recent_turns(self, count: int = 5) -> List[ConversationTurn]:
        """Get the most recent conversation turns."""
        return list(self.turns)[-count:]
        
    def is_active(self, timeout_minutes: int = 30) -> bool:
        """Check if session is still active."""
        return (time.time() - self.last_activity) < (timeout_minutes * 60)


class ContextMemoryManager:
    """Memory management for context operations."""
    
    def __init__(self, max_memory_mb: int = 10):
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.process = psutil.Process()
        self.baseline_memory = self.process.memory_info().rss
        self.lock = threading.Lock()
        
    def get_memory_usage(self) -> int:
        """Get current memory usage delta."""
        return self.process.memory_info().rss - self.baseline_memory
        
    def is_within_limits(self) -> bool:
        """Check if memory usage is within limits."""
        return self.get_memory_usage() < self.max_memory_bytes
        
    def estimate_object_size(self, obj: Any) -> int:
        """Estimate object size in bytes."""
        try:
            if isinstance(obj, (str, int, float, bool)):
                return len(str(obj).encode('utf-8'))
            elif isinstance(obj, dict):
                return sum(self.estimate_object_size(k) + self.estimate_object_size(v) 
                          for k, v in obj.items())
            elif isinstance(obj, (list, tuple)):
                return sum(self.estimate_object_size(item) for item in obj)
            else:
                return len(json.dumps(obj, default=str).encode('utf-8'))
        except:
            return 1024  # Conservative estimate
            
    def cleanup(self):
        """Force memory cleanup."""
        with self.lock:
            gc.collect()


class ContextRelevanceScorer:
    """Scores context relevance for retention decisions."""
    
    def __init__(self):
        self.weight_factors = {
            "recency": 0.3,      # How recent the context is
            "frequency": 0.2,    # How often it's accessed
            "priority": 0.25,    # Assigned priority level
            "topical": 0.15,     # Relevance to current topic
            "semantic": 0.1      # Semantic similarity (basic)
        }
        
    def score_context_item(self, 
                          item: ContextItem, 
                          current_topic: Optional[str] = None,
                          current_time: Optional[float] = None) -> float:
        """Score a context item for relevance."""
        if current_time is None:
            current_time = time.time()
            
        scores = {}
        
        # Recency score (0-1, higher for more recent)
        age_hours = (current_time - item.timestamp) / 3600
        scores["recency"] = max(0, 1 - (age_hours / 24))  # Decay over 24 hours
        
        # Frequency score (0-1, based on access count)
        scores["frequency"] = min(1.0, item.access_count / 10.0)
        
        # Priority score (0-1, based on priority enum)
        scores["priority"] = item.priority.value / 5.0
        
        # Topical relevance (basic keyword matching)
        scores["topical"] = 0.5  # Default neutral score
        if current_topic and isinstance(item.value, str):
            topic_words = set(current_topic.lower().split())
            item_words = set(str(item.value).lower().split())
            if topic_words & item_words:  # Intersection
                scores["topical"] = min(1.0, len(topic_words & item_words) / len(topic_words))
                
        # Semantic similarity (placeholder - could use embeddings)
        scores["semantic"] = item.confidence
        
        # Calculate weighted total
        total_score = sum(
            scores.get(factor, 0) * weight 
            for factor, weight in self.weight_factors.items()
        )
        
        return total_score
        
    def rank_context_items(self, 
                          items: List[ContextItem], 
                          current_topic: Optional[str] = None) -> List[Tuple[ContextItem, float]]:
        """Rank context items by relevance."""
        scored_items = []
        for item in items:
            score = self.score_context_item(item, current_topic)
            scored_items.append((item, score))
            
        # Sort by score (highest first)
        scored_items.sort(key=lambda x: x[1], reverse=True)
        return scored_items


class ContextManager:
    """
    Main Context Manager for ImpressionCore Personal Assistant.
    
    Manages conversation state, context switching, and memory-efficient
    context retention optimized for GTX 1050 Ti constraints.
    """
    
    def __init__(self, max_memory_mb: int = 10, max_sessions: int = 10):
        self.logger = get_rich_logger("context_manager")
        self.memory_manager = ContextMemoryManager(max_memory_mb)
        self.relevance_scorer = ContextRelevanceScorer()
        
        # Session management
        self.sessions: Dict[str, ConversationSession] = {}
        self.current_session_id: Optional[str] = None
        self.max_sessions = max_sessions
        
        # Global context (cross-session)
        self.global_context: Dict[str, ContextItem] = {}
        
        # Configuration
        self.config = {
            "max_turns_per_session": 50,
            "session_timeout_minutes": 30,
            "context_cleanup_interval": 300,  # 5 minutes
            "min_relevance_threshold": 0.1,
            "max_context_items_per_session": 100
        }
        
        # Statistics
        self.stats = {
            "total_sessions": 0,
            "active_sessions": 0,
            "total_turns": 0,
            "context_items_created": 0,
            "context_items_expired": 0,
            "memory_cleanups": 0,
            "context_switches": 0
        }
        
        # Status animation
        self.status_animation = StatusAnimation(total_steps=5, description="Context Processing")
        
        # Background cleanup
        self._last_cleanup = time.time()
        
        self.logger.info(f"Context Manager initialized with {max_memory_mb}MB memory limit")
        
    def create_session(self, user_id: Optional[str] = None) -> str:
        """Create a new conversation session."""
        session_id = str(uuid.uuid4())
        
        # Check session limits
        if len(self.sessions) >= self.max_sessions:
            self._cleanup_inactive_sessions()
            
        # Create session
        session = ConversationSession(
            session_id=session_id,
            start_time=time.time(),
            last_activity=time.time(),
            metadata={"user_id": user_id} if user_id else {}
        )
        
        self.sessions[session_id] = session
        self.current_session_id = session_id
        
        self.stats["total_sessions"] += 1
        self.stats["active_sessions"] = len(self.sessions)
        
        self.logger.info(f"Created new session: {session_id}")
        return session_id
        
    def switch_session(self, session_id: str) -> bool:
        """Switch to an existing session."""
        if session_id not in self.sessions:
            self.logger.warning(f"Session {session_id} not found")
            return False
            
        self.current_session_id = session_id
        self.sessions[session_id].last_activity = time.time()
        self.stats["context_switches"] += 1
        
        self.logger.debug(f"Switched to session: {session_id}")
        return True
        
    def add_conversation_turn(self, 
                            user_input: str,
                            nlu_result: Optional[NLUResult] = None,
                            system_response: Optional[str] = None,
                            session_id: Optional[str] = None) -> str:
        """Add a conversation turn to the current or specified session."""
        # Use current session if none specified
        if session_id is None:
            session_id = self.current_session_id
            
        if session_id is None:
            # Create new session
            session_id = self.create_session()
            
        if session_id not in self.sessions:
            self.logger.error(f"Session {session_id} not found")
            return ""
            
        # Create turn
        turn_id = f"{session_id}_{int(time.time() * 1000)}"
        turn = ConversationTurn(
            turn_id=turn_id,
            timestamp=time.time(),
            user_input=user_input,
            nlu_result=nlu_result,
            system_response=system_response
        )
        
        # Add to session
        session = self.sessions[session_id]
        session.add_turn(turn)
        
        # Extract and store context from turn
        if nlu_result:
            self._extract_context_from_turn(turn, session)
            
        self.stats["total_turns"] += 1
        
        # Memory management
        self._check_memory_and_cleanup()
        
        self.logger.debug(f"Added conversation turn: {turn_id}")
        return turn_id
        
    def _extract_context_from_turn(self, turn: ConversationTurn, session: ConversationSession):
        """Extract context information from a conversation turn."""
        if not turn.nlu_result:
            return
            
        nlu = turn.nlu_result
        
        # Extract entities as context
        for entity in nlu.entities:
            context_key = f"entity_{entity.entity_type.value}_{entity.text.lower()}"
            
            context_item = ContextItem(
                key=context_key,
                value=entity.text,
                context_type=ContextType.CONVERSATIONAL,
                priority=self._determine_entity_priority(entity.entity_type),
                timestamp=turn.timestamp,
                source_turn_id=turn.turn_id,
                confidence=entity.confidence,
                metadata={
                    "entity_type": entity.entity_type.value,
                    "start_pos": entity.start_pos,
                    "end_pos": entity.end_pos
                }
            )
            
            session.context[context_key] = context_item
            self.stats["context_items_created"] += 1
            
        # Extract intent as context
        intent_key = f"last_intent_{nlu.intent.intent_type.value}"
        intent_context = ContextItem(
            key=intent_key,
            value=nlu.intent.intent_type.value,
            context_type=ContextType.CONVERSATIONAL,
            priority=ContextPriority.MEDIUM,
            timestamp=turn.timestamp,
            source_turn_id=turn.turn_id,
            confidence=nlu.intent.confidence,
            metadata={"intent_features": nlu.intent.supporting_features}
        )
        
        session.context[intent_key] = intent_context
        self.stats["context_items_created"] += 1
        
        # Extract sentiment as emotional context
        if nlu.sentiment:
            sentiment_key = "current_sentiment"
            sentiment_context = ContextItem(
                key=sentiment_key,
                value={
                    "polarity": nlu.sentiment.polarity,
                    "subjectivity": nlu.sentiment.subjectivity
                },
                context_type=ContextType.EMOTIONAL,
                priority=ContextPriority.LOW,
                timestamp=turn.timestamp,
                source_turn_id=turn.turn_id,
                confidence=nlu.sentiment.confidence,
                expiry_time=turn.timestamp + 3600  # Expire after 1 hour
            )
            
            session.context[sentiment_key] = sentiment_context
            self.stats["context_items_created"] += 1
            
    def _determine_entity_priority(self, entity_type: EntityType) -> ContextPriority:
        """Determine priority level for different entity types."""
        high_priority_entities = {
            EntityType.PERSON, EntityType.ORGANIZATION, EntityType.FILE_PATH,
            EntityType.EMAIL, EntityType.TASK_NAME
        }
        
        medium_priority_entities = {
            EntityType.DATE, EntityType.TIME, EntityType.LOCATION,
            EntityType.PRIORITY_LEVEL, EntityType.STATUS
        }
        
        if entity_type in high_priority_entities:
            return ContextPriority.HIGH
        elif entity_type in medium_priority_entities:
            return ContextPriority.MEDIUM
        else:
            return ContextPriority.LOW
            
    def add_context_item(self, 
                        key: str,
                        value: Any,
                        context_type: ContextType = ContextType.CONVERSATIONAL,
                        priority: ContextPriority = ContextPriority.MEDIUM,
                        expiry_hours: Optional[float] = None,
                        session_id: Optional[str] = None,
                        global_context: bool = False) -> bool:
        """Add a context item manually."""
        timestamp = time.time()
        expiry_time = None
        if expiry_hours:
            expiry_time = timestamp + (expiry_hours * 3600)
            
        context_item = ContextItem(
            key=key,
            value=value,
            context_type=context_type,
            priority=priority,
            timestamp=timestamp,
            expiry_time=expiry_time,
            confidence=1.0
        )
        
        if global_context:
            self.global_context[key] = context_item
        else:
            # Add to session context
            target_session_id = session_id or self.current_session_id
            if target_session_id and target_session_id in self.sessions:
                self.sessions[target_session_id].context[key] = context_item
            else:
                self.logger.warning(f"Cannot add context item: no valid session")
                return False
                
        self.stats["context_items_created"] += 1
        self.logger.debug(f"Added context item: {key}")
        return True
        
    def get_context(self, 
                   key: Optional[str] = None,
                   context_type: Optional[ContextType] = None,
                   session_id: Optional[str] = None) -> Union[Any, Dict[str, Any]]:
        """Get context information."""
        target_session_id = session_id or self.current_session_id
        
        # Combine session and global context
        all_context = {}
        all_context.update(self.global_context)
        
        if target_session_id and target_session_id in self.sessions:
            all_context.update(self.sessions[target_session_id].context)
            
        # Filter by type if specified
        if context_type:
            all_context = {
                k: v for k, v in all_context.items()
                if v.context_type == context_type
            }
            
        # Return specific key or all context
        if key:
            item = all_context.get(key)
            if item and not item.is_expired():
                item.access()  # Mark as accessed
                return item.value
            return None
        else:
            # Return all non-expired context
            result = {}
            for k, item in all_context.items():
                if not item.is_expired():
                    item.access()
                    result[k] = item.value
            return result
            
    def get_conversation_history(self, 
                               turns: int = 10,
                               session_id: Optional[str] = None) -> List[ConversationTurn]:
        """Get recent conversation history."""
        target_session_id = session_id or self.current_session_id
        
        if target_session_id and target_session_id in self.sessions:
            session = self.sessions[target_session_id]
            return session.get_recent_turns(turns)
        else:
            return []
            
    def get_context_summary(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get a summary of current context."""
        target_session_id = session_id or self.current_session_id
        
        summary = {
            "session_id": target_session_id,
            "global_context_items": len(self.global_context),
            "session_context_items": 0,
            "total_turns": 0,
            "context_by_type": defaultdict(int),
            "recent_intents": [],
            "active_entities": [],
            "current_topics": []
        }
        
        if target_session_id and target_session_id in self.sessions:
            session = self.sessions[target_session_id]
            summary["session_context_items"] = len(session.context)
            summary["total_turns"] = len(session.turns)
            
            # Analyze context by type
            all_items = list(self.global_context.values()) + list(session.context.values())
            for item in all_items:
                if not item.is_expired():
                    summary["context_by_type"][item.context_type.value] += 1
                    
            # Get recent intents
            recent_turns = session.get_recent_turns(5)
            for turn in recent_turns:
                if turn.nlu_result:
                    summary["recent_intents"].append(turn.nlu_result.intent.intent_type.value)
                    
        return summary
        
    def _cleanup_inactive_sessions(self):
        """Remove inactive sessions to free memory."""
        current_time = time.time()
        inactive_sessions = []
        
        for session_id, session in self.sessions.items():
            if not session.is_active(self.config["session_timeout_minutes"]):
                inactive_sessions.append(session_id)
                
        for session_id in inactive_sessions:
            del self.sessions[session_id]
            if self.current_session_id == session_id:
                self.current_session_id = None
                
        if inactive_sessions:
            self.logger.info(f"Cleaned up {len(inactive_sessions)} inactive sessions")
            
        self.stats["active_sessions"] = len(self.sessions)
        
    def _cleanup_expired_context(self):
        """Remove expired context items."""
        expired_count = 0
        
        # Clean global context
        expired_keys = [
            key for key, item in self.global_context.items()
            if item.is_expired()
        ]
        for key in expired_keys:
            del self.global_context[key]
            expired_count += 1
            
        # Clean session context
        for session in self.sessions.values():
            expired_keys = [
                key for key, item in session.context.items()
                if item.is_expired()
            ]
            for key in expired_keys:
                del session.context[key]
                expired_count += 1
                
        if expired_count > 0:
            self.stats["context_items_expired"] += expired_count
            self.logger.debug(f"Cleaned up {expired_count} expired context items")
            
    def _check_memory_and_cleanup(self):
        """Check memory usage and perform cleanup if needed."""
        if not self.memory_manager.is_within_limits():
            self.logger.warning("Memory limit exceeded, performing cleanup")
            
            # Clean expired items first
            self._cleanup_expired_context()
            
            # If still over limit, remove low-relevance items
            if not self.memory_manager.is_within_limits():
                self._cleanup_low_relevance_context()
                
            # Force memory cleanup
            self.memory_manager.cleanup()
            self.stats["memory_cleanups"] += 1
            
        # Periodic cleanup
        current_time = time.time()
        if current_time - self._last_cleanup > self.config["context_cleanup_interval"]:
            self._cleanup_expired_context()
            self._cleanup_inactive_sessions()
            self._last_cleanup = current_time
            
    def _cleanup_low_relevance_context(self):
        """Remove context items with low relevance scores."""
        current_topic = self._get_current_topic()
        
        # Process each session
        for session in self.sessions.values():
            items = list(session.context.values())
            if len(items) <= self.config["max_context_items_per_session"]:
                continue
                
            # Score and sort items
            scored_items = self.relevance_scorer.rank_context_items(items, current_topic)
            
            # Keep only top items
            items_to_keep = scored_items[:self.config["max_context_items_per_session"]]
            keep_keys = {item.key for item, score in items_to_keep}
            
            # Remove low-relevance items
            keys_to_remove = [key for key in session.context.keys() if key not in keep_keys]
            for key in keys_to_remove:
                del session.context[key]
                
        self.logger.debug("Performed low-relevance context cleanup")
        
    def _get_current_topic(self) -> Optional[str]:
        """Extract current conversation topic (simple implementation)."""
        if not self.current_session_id or self.current_session_id not in self.sessions:
            return None
            
        session = self.sessions[self.current_session_id]
        recent_turns = session.get_recent_turns(3)
        
        # Simple topic extraction from recent user inputs
        topic_words = []
        for turn in recent_turns:
            if turn.nlu_result and turn.nlu_result.entities:
                for entity in turn.nlu_result.entities:
                    topic_words.append(entity.text)
                    
        return " ".join(topic_words) if topic_words else None
        
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        memory_usage_mb = self.memory_manager.get_memory_usage() / (1024 * 1024)
        
        return {
            "session_stats": self.stats.copy(),
            "memory_usage": {
                "current_mb": memory_usage_mb,
                "max_allowed_mb": self.memory_manager.max_memory_bytes / (1024 * 1024),
                "within_limits": self.memory_manager.is_within_limits()
            },
            "context_distribution": {
                "global_items": len(self.global_context),
                "session_items": sum(len(s.context) for s in self.sessions.values()),
                "total_sessions": len(self.sessions)
            },
            "configuration": self.config.copy()
        }
        
    def export_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export session data for persistence or analysis."""
        if session_id not in self.sessions:
            return None
            
        session = self.sessions[session_id]
        
        # Convert to serializable format
        export_data = {
            "session_id": session.session_id,
            "start_time": session.start_time,
            "last_activity": session.last_activity,
            "turns": [
                {
                    "turn_id": turn.turn_id,
                    "timestamp": turn.timestamp,
                    "user_input": turn.user_input,
                    "system_response": turn.system_response,
                    "nlu_result": asdict(turn.nlu_result) if turn.nlu_result else None,
                    "context_updates": turn.context_updates,
                    "metadata": turn.metadata
                }
                for turn in session.turns
            ],
            "context": {
                key: {
                    "key": item.key,
                    "value": item.value,
                    "context_type": item.context_type.value,
                    "priority": item.priority.value,
                    "timestamp": item.timestamp,
                    "expiry_time": item.expiry_time,
                    "access_count": item.access_count,
                    "last_accessed": item.last_accessed,
                    "source_turn_id": item.source_turn_id,
                    "confidence": item.confidence,
                    "metadata": item.metadata
                }
                for key, item in session.context.items()
            },
            "metadata": session.metadata
        }
        
        return export_data
        
    def shutdown(self):
        """Shutdown the context manager and cleanup resources."""
        self.sessions.clear()
        self.global_context.clear()
        self.memory_manager.cleanup()
        self.logger.info("Context Manager shutdown complete")


# Utility functions for easy integration

def create_quick_context() -> ContextManager:
    """Create a lightweight context manager for simple use cases."""
    return ContextManager(max_memory_mb=5, max_sessions=3)


def extract_entities_to_context(nlu_result: NLUResult, context_manager: ContextManager):
    """Utility to extract entities from NLU result into context."""
    for entity in nlu_result.entities:
        context_manager.add_context_item(
            key=f"entity_{entity.entity_type.value}",
            value=entity.text,
            context_type=ContextType.CONVERSATIONAL,
            priority=ContextPriority.MEDIUM
        )


if __name__ == "__main__":
    # Example usage and testing
    def test_context_manager():
        from src.assistant.nlp.nlu_engine import NLUEngine
        
        cm = ContextManager()
        nlu = NLUEngine()
        
        try:
            # Create session
            session_id = cm.create_session(user_id="test_user")
            print(f"Created session: {session_id}")
            
            # Test conversation turns
            test_inputs = [
                "Hello, my name is John and I work at OpenAI",
                "Can you help me create a task for tomorrow at 2 PM?",
                "What's the status of my project files in C:\\Projects?",
                "I'm feeling frustrated with the current implementation",
                "Schedule a meeting with john.doe@example.com"
            ]
            
            for i, user_input in enumerate(test_inputs):
                print(f"\nTurn {i+1}: {user_input}")
                
                # Analyze with NLU
                nlu_result = nlu.analyze(user_input)
                
                # Add to context
                turn_id = cm.add_conversation_turn(
                    user_input=user_input,
                    nlu_result=nlu_result,
                    system_response=f"Response to turn {i+1}"
                )
                
                print(f"  Intent: {nlu_result.intent.intent_type.value}")
                print(f"  Entities: {[e.text for e in nlu_result.entities]}")
                
            # Test context retrieval
            print("\n" + "="*50)
            print("Context Summary:")
            summary = cm.get_context_summary()
            for key, value in summary.items():
                print(f"  {key}: {value}")
                
            print("\nAll Context Items:")
            all_context = cm.get_context()
            for key, value in all_context.items():
                print(f"  {key}: {value}")
                
            # Test conversation history
            print("\nConversation History:")
            history = cm.get_conversation_history(turns=3)
            for turn in history:
                print(f"  {turn.timestamp}: {turn.user_input[:50]}...")
                
            # Performance stats
            print("\nPerformance Stats:")
            stats = cm.get_performance_stats()
            print(f"  Memory usage: {stats['memory_usage']['current_mb']:.1f}MB")
            print(f"  Total turns: {stats['session_stats']['total_turns']}")
            print(f"  Context items created: {stats['session_stats']['context_items_created']}")
            
        finally:
            cm.shutdown()
            nlu.shutdown()
    
    # Run test if executed directly
    test_context_manager()
