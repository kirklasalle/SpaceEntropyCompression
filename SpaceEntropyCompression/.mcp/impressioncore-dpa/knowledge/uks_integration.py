#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\knowledge\uks_integration.py #memory_management #multimodal #python #source_code #testing  
**Category:** Source Code  
**Status:** Active
"""









# Uks Integration

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\knowledge\uks_integration.py #memory_management #multimodal #python #source_code #testing  
**Category:** Source Code  
**Status:** Active

"""
UKS (Unified Knowledge Store) Integration Module for ImpressionCore Personal Assistant

This module provides integration with the Unified Knowledge Store system,
enabling knowledge graph traversal, fact verification, and memory-optimized
knowledge access for GTX 1050 Ti hardware constraints (15MB memory budget).

Key Features:
- Unified Knowledge Store connectivity
- Knowledge graph traversal
- Fact verification and validation
- Knowledge update mechanisms
- Memory-optimized knowledge access
- Semantic relationship mapping

Performance Targets:
- Knowledge Access Time: <500ms average
- Memory Usage: <15MB for active knowledge
- Fact Verification: >85% accuracy
- Graph Traversal: Support for 3-hop queries

Author: ImpressionCore Development Team
Date: 2025-06-06
Phase: 8B Week 1 - Personal Assistant Core Foundation
"""

import time
import logging
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import sqlite3
import threading
from collections import defaultdict

# Core utilities and rich enhancements
from src.core.utils.rich_enhancements import create_panel, create_table
from src.core.utils.rich_logging import get_rich_logger
from src.core.utils.rich_status_animation import StatusAnimation

# Memory management
import psutil
import gc

# Import related assistant components
from src.assistant.nlp.nlu_engine import EntityType, Entity
from src.assistant.core.context_manager import ContextType, ContextPriority


class KnowledgeType(Enum):
    """Types of knowledge in the UKS."""
    FACTUAL = "factual"              # Objective facts and data
    PROCEDURAL = "procedural"        # How-to knowledge and processes
    CONCEPTUAL = "conceptual"        # Abstract concepts and definitions
    TEMPORAL = "temporal"            # Time-based knowledge
    SPATIAL = "spatial"              # Location and spatial relationships
    CAUSAL = "causal"               # Cause-and-effect relationships
    PERSONAL = "personal"           # User-specific knowledge
    SYSTEM = "system"               # System and technical knowledge


class RelationType(Enum):
    """Types of relationships between knowledge nodes."""
    IS_A = "is_a"                   # Inheritance/classification
    PART_OF = "part_of"             # Composition
    RELATED_TO = "related_to"       # General association
    CAUSES = "causes"               # Causal relationship
    LOCATED_AT = "located_at"       # Spatial relationship
    OCCURS_AT = "occurs_at"         # Temporal relationship
    DEPENDS_ON = "depends_on"       # Dependency relationship
    SIMILAR_TO = "similar_to"       # Similarity relationship
    OPPOSITE_OF = "opposite_of"     # Contrast relationship
    USED_FOR = "used_for"          # Purpose/function relationship


@dataclass
class KnowledgeNode:
    """Individual node in the knowledge graph."""
    node_id: str
    name: str
    knowledge_type: KnowledgeType
    content: Dict[str, Any]
    confidence: float = 1.0
    timestamp: float = field(default_factory=time.time)
    source: Optional[str] = None
    verified: bool = False
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def access(self):
        """Mark node as accessed."""
        self.access_count += 1
        self.last_accessed = time.time()


@dataclass
class KnowledgeRelation:
    """Relationship between knowledge nodes."""
    relation_id: str
    source_node_id: str
    target_node_id: str
    relation_type: RelationType
    strength: float = 1.0
    confidence: float = 1.0
    timestamp: float = field(default_factory=time.time)
    bidirectional: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeQuery:
    """Query object for knowledge retrieval."""
    query_text: str
    query_type: str = "general"
    max_nodes: int = 10
    max_hops: int = 2
    min_confidence: float = 0.5
    knowledge_types: Optional[List[KnowledgeType]] = None
    relation_types: Optional[List[RelationType]] = None
    context_filters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeResult:
    """Result from knowledge query."""
    query: KnowledgeQuery
    nodes: List[KnowledgeNode] = field(default_factory=list)
    relations: List[KnowledgeRelation] = field(default_factory=list)
    paths: List[List[str]] = field(default_factory=list)  # Node ID paths
    confidence: float = 0.0
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class UKSMemoryManager:
    """Memory management for UKS operations."""
    
    def __init__(self, max_memory_mb: int = 15):
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
        
    def cleanup(self):
        """Force memory cleanup."""
        with self.lock:
            gc.collect()


class KnowledgeCache:
    """Memory-efficient cache for knowledge nodes and relations."""
    
    def __init__(self, max_size_mb: int = 5):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.node_cache: Dict[str, KnowledgeNode] = {}
        self.relation_cache: Dict[str, KnowledgeRelation] = {}
        self.query_cache: Dict[str, KnowledgeResult] = {}
        self.current_size = 0
        self.cache_stats = {"hits": 0, "misses": 0}
        
    def _estimate_size(self, obj: Any) -> int:
        """Estimate object size in bytes."""
        try:
            return len(json.dumps(obj, default=str).encode('utf-8'))
        except:
            return 1024  # Conservative estimate
            
    def _evict_oldest(self):
        """Evict oldest cached items to make space."""
        # Simple LRU eviction for nodes
        if self.node_cache:
            oldest_node_id = min(
                self.node_cache.keys(),
                key=lambda nid: self.node_cache[nid].last_accessed
            )
            node = self.node_cache.pop(oldest_node_id)
            self.current_size -= self._estimate_size(node)
            
    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """Get cached knowledge node."""
        if node_id in self.node_cache:
            self.cache_stats["hits"] += 1
            node = self.node_cache[node_id]
            node.access()
            return node
        else:
            self.cache_stats["misses"] += 1
            return None
            
    def put_node(self, node: KnowledgeNode):
        """Cache a knowledge node."""
        size = self._estimate_size(node)
        
        # Evict if needed
        while self.current_size + size > self.max_size_bytes and self.node_cache:
            self._evict_oldest()
            
        self.node_cache[node.node_id] = node
        self.current_size += size
        
    def get_query_result(self, query_hash: str) -> Optional[KnowledgeResult]:
        """Get cached query result."""
        if query_hash in self.query_cache:
            self.cache_stats["hits"] += 1
            return self.query_cache[query_hash]
        else:
            self.cache_stats["misses"] += 1
            return None
            
    def put_query_result(self, query_hash: str, result: KnowledgeResult):
        """Cache a query result."""
        size = self._estimate_size(result)
        
        # Only cache if reasonable size
        if size < self.max_size_bytes / 4:
            self.query_cache[query_hash] = result
            self.current_size += size
            
    def clear(self):
        """Clear all caches."""
        self.node_cache.clear()
        self.relation_cache.clear()
        self.query_cache.clear()
        self.current_size = 0
        
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = self.cache_stats["hits"] / total_requests if total_requests > 0 else 0
        
        return {
            "hit_rate": hit_rate,
            "cache_size_mb": self.current_size / (1024 * 1024),
            "node_count": len(self.node_cache),
            "relation_count": len(self.relation_cache),
            "query_count": len(self.query_cache)
        }


class KnowledgeStore:
    """Simple SQLite-based knowledge store for UKS implementation."""
    
    def __init__(self, db_path: str = "knowledge_store.db"):
        self.db_path = db_path
        self.connection = None
        self.lock = threading.Lock()
        self._initialize_db()
        
    def _initialize_db(self):
        """Initialize the knowledge store database."""
        with sqlite3.connect(self.db_path) as conn:
            # Create nodes table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_nodes (
                    node_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    knowledge_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    confidence REAL DEFAULT 1.0,
                    timestamp REAL NOT NULL,
                    source TEXT,
                    verified BOOLEAN DEFAULT FALSE,
                    access_count INTEGER DEFAULT 0,
                    last_accessed REAL,
                    metadata TEXT
                )
            """)
            
            # Create relations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_relations (
                    relation_id TEXT PRIMARY KEY,
                    source_node_id TEXT NOT NULL,
                    target_node_id TEXT NOT NULL,
                    relation_type TEXT NOT NULL,
                    strength REAL DEFAULT 1.0,
                    confidence REAL DEFAULT 1.0,
                    timestamp REAL NOT NULL,
                    bidirectional BOOLEAN DEFAULT FALSE,
                    metadata TEXT,
                    FOREIGN KEY (source_node_id) REFERENCES knowledge_nodes (node_id),
                    FOREIGN KEY (target_node_id) REFERENCES knowledge_nodes (node_id)
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_nodes_type ON knowledge_nodes (knowledge_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_nodes_name ON knowledge_nodes (name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_relations_source ON knowledge_relations (source_node_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_relations_target ON knowledge_relations (target_node_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_relations_type ON knowledge_relations (relation_type)")
            
            conn.commit()
            
    def store_node(self, node: KnowledgeNode) -> bool:
        """Store a knowledge node."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO knowledge_nodes 
                    (node_id, name, knowledge_type, content, confidence, timestamp, 
                     source, verified, access_count, last_accessed, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    node.node_id, node.name, node.knowledge_type.value,
                    json.dumps(node.content), node.confidence, node.timestamp,
                    node.source, node.verified, node.access_count,
                    node.last_accessed, json.dumps(node.metadata)
                ))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Error storing node {node.node_id}: {e}")
            return False
            
    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """Retrieve a knowledge node."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT * FROM knowledge_nodes WHERE node_id = ?",
                    (node_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return KnowledgeNode(
                        node_id=row[0],
                        name=row[1],
                        knowledge_type=KnowledgeType(row[2]),
                        content=json.loads(row[3]),
                        confidence=row[4],
                        timestamp=row[5],
                        source=row[6],
                        verified=bool(row[7]),
                        access_count=row[8],
                        last_accessed=row[9],
                        metadata=json.loads(row[10]) if row[10] else {}
                    )
                return None
        except Exception as e:
            logging.error(f"Error retrieving node {node_id}: {e}")
            return None
            
    def search_nodes(self, 
                    query: str,
                    knowledge_types: Optional[List[KnowledgeType]] = None,
                    limit: int = 10) -> List[KnowledgeNode]:
        """Search for knowledge nodes."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                sql = """
                    SELECT * FROM knowledge_nodes 
                    WHERE name LIKE ? OR content LIKE ?
                """
                params = [f"%{query}%", f"%{query}%"]
                
                if knowledge_types:
                    type_placeholders = ",".join("?" * len(knowledge_types))
                    sql += f" AND knowledge_type IN ({type_placeholders})"
                    params.extend([kt.value for kt in knowledge_types])
                    
                sql += " ORDER BY confidence DESC, access_count DESC LIMIT ?"
                params.append(limit)
                
                cursor = conn.execute(sql, params)
                rows = cursor.fetchall()
                
                nodes = []
                for row in rows:
                    node = KnowledgeNode(
                        node_id=row[0],
                        name=row[1],
                        knowledge_type=KnowledgeType(row[2]),
                        content=json.loads(row[3]),
                        confidence=row[4],
                        timestamp=row[5],
                        source=row[6],
                        verified=bool(row[7]),
                        access_count=row[8],
                        last_accessed=row[9],
                        metadata=json.loads(row[10]) if row[10] else {}
                    )
                    nodes.append(node)
                    
                return nodes
        except Exception as e:
            logging.error(f"Error searching nodes: {e}")
            return []
            
    def get_related_nodes(self, node_id: str, max_hops: int = 2) -> List[Tuple[KnowledgeNode, List[KnowledgeRelation]]]:
        """Get nodes related to a given node through graph traversal."""
        related = []
        visited = set()
        
        def traverse(current_id: str, hop_count: int, path: List[KnowledgeRelation]):
            if hop_count >= max_hops or current_id in visited:
                return
                
            visited.add(current_id)
            
            try:
                with sqlite3.connect(self.db_path) as conn:
                    # Get outgoing relations
                    cursor = conn.execute("""
                        SELECT r.*, n.* FROM knowledge_relations r
                        JOIN knowledge_nodes n ON r.target_node_id = n.node_id
                        WHERE r.source_node_id = ?
                        ORDER BY r.strength DESC
                    """, (current_id,))
                    
                    for row in cursor.fetchall():
                        relation = KnowledgeRelation(
                            relation_id=row[0],
                            source_node_id=row[1],
                            target_node_id=row[2],
                            relation_type=RelationType(row[3]),
                            strength=row[4],
                            confidence=row[5],
                            timestamp=row[6],
                            bidirectional=bool(row[7]),
                            metadata=json.loads(row[8]) if row[8] else {}
                        )
                        
                        target_node = KnowledgeNode(
                            node_id=row[9],
                            name=row[10],
                            knowledge_type=KnowledgeType(row[11]),
                            content=json.loads(row[12]),
                            confidence=row[13],
                            timestamp=row[14],
                            source=row[15],
                            verified=bool(row[16]),
                            access_count=row[17],
                            last_accessed=row[18],
                            metadata=json.loads(row[19]) if row[19] else {}
                        )
                        
                        new_path = path + [relation]
                        related.append((target_node, new_path))
                        
                        # Continue traversal
                        traverse(target_node.node_id, hop_count + 1, new_path)
                        
            except Exception as e:
                logging.error(f"Error in graph traversal: {e}")
                
        traverse(node_id, 0, [])
        return related


class UKSIntegration:
    """
    Main UKS Integration Module for ImpressionCore Personal Assistant.
    
    Provides unified access to knowledge store with memory optimization
    and performance monitoring for GTX 1050 Ti constraints.
    """
    
    def __init__(self, db_path: str = "src/data/knowledge_store.db", max_memory_mb: int = 15):
        self.logger = get_rich_logger("uks_integration")
        self.memory_manager = UKSMemoryManager(max_memory_mb)
        
        # Knowledge store
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_store = KnowledgeStore(db_path)
        
        # Caching system
        self.cache = KnowledgeCache(max_size_mb=5)
        
        # Statistics
        self.stats = {
            "queries_executed": 0,
            "nodes_accessed": 0,
            "cache_hit_rate": 0.0,
            "average_query_time": 0.0,
            "knowledge_base_size": 0
        }
          # Status animation
        self.status_animation = StatusAnimation(
            total_steps=5,
            description="UKS Operations"
        )
        
        # Initialize with some basic knowledge
        self._initialize_basic_knowledge()
        
        self.logger.info(f"UKS Integration initialized with {max_memory_mb}MB memory limit")
        
    def _initialize_basic_knowledge(self):
        """Initialize basic knowledge about ImpressionCore system."""
        basic_nodes = [
            KnowledgeNode(
                node_id="impressioncore_system",
                name="ImpressionCore System",
                knowledge_type=KnowledgeType.SYSTEM,
                content={
                    "description": "Brain-inspired multimodal AI framework",
                    "target_hardware": "GTX 1050 Ti with 4GB VRAM",
                    "capabilities": ["multimodal processing", "memory optimization", "personal assistance"]
                },
                confidence=1.0,
                source="system_initialization",
                verified=True
            ),
            KnowledgeNode(
                node_id="phase_8b",
                name="Phase 8B Development",
                knowledge_type=KnowledgeType.PROCEDURAL,
                content={
                    "description": "Personal assistant core implementation phase",
                    "components": ["query processor", "retrieval engine", "NLU engine", "context manager", "UKS integration"],
                    "timeline": "Week 1 implementation"
                },
                confidence=1.0,
                source="development_roadmap",
                verified=True
            ),
            KnowledgeNode(
                node_id="assistant_capabilities",
                name="Assistant Capabilities",
                knowledge_type=KnowledgeType.CONCEPTUAL,
                content={
                    "description": "Core capabilities of the personal assistant",
                    "features": ["natural language understanding", "context management", "knowledge retrieval", "task assistance"]
                },
                confidence=1.0,
                source="system_specification",
                verified=True
            )
        ]
        
        for node in basic_nodes:
            self.knowledge_store.store_node(node)
            self.cache.put_node(node)
            
        self.logger.debug("Initialized basic knowledge base")
        
    def query_knowledge(self, query: KnowledgeQuery) -> KnowledgeResult:
        """
        Execute a knowledge query with memory optimization.
        
        Args:
            query: KnowledgeQuery object specifying search parameters
            
        Returns:
            KnowledgeResult with matching nodes and relations
        """
        start_time = time.time()
        
        # Check cache first
        query_hash = self._generate_query_hash(query)
        cached_result = self.cache.get_query_result(query_hash)
        if cached_result:
            self.logger.debug(f"Cache hit for query: {query.query_text[:30]}...")
            return cached_result
            
        # Memory check
        if not self.memory_manager.is_within_limits():
            self.memory_manager.cleanup()
            self.logger.warning("Memory limit approached, performed cleanup")
            
        try:
            with self.status_animation.status(f"Querying knowledge: {query.query_text[:30]}..."):
                # Search for relevant nodes
                nodes = self.knowledge_store.search_nodes(
                    query.query_text,
                    query.knowledge_types,
                    query.max_nodes
                )
                
                # Filter by confidence
                nodes = [n for n in nodes if n.confidence >= query.min_confidence]
                
                # Get related nodes if requested
                related_data = []
                if query.max_hops > 0:
                    for node in nodes[:5]:  # Limit graph traversal for performance
                        related = self.knowledge_store.get_related_nodes(node.node_id, query.max_hops)
                        related_data.extend(related)
                        
                # Extract relations and additional nodes
                all_relations = []
                additional_nodes = []
                paths = []
                
                for node, relation_path in related_data:
                    if node.node_id not in [n.node_id for n in nodes]:
                        additional_nodes.append(node)
                    all_relations.extend(relation_path)
                    paths.append([r.target_node_id for r in relation_path])
                    
                # Combine all nodes
                all_nodes = nodes + additional_nodes
                
                # Calculate overall confidence
                if all_nodes:
                    avg_confidence = sum(n.confidence for n in all_nodes) / len(all_nodes)
                else:
                    avg_confidence = 0.0
                    
                # Create result
                result = KnowledgeResult(
                    query=query,
                    nodes=all_nodes,
                    relations=all_relations,
                    paths=paths,
                    confidence=avg_confidence,
                    processing_time=time.time() - start_time,
                    metadata={
                        "nodes_found": len(nodes),
                        "related_nodes": len(additional_nodes),
                        "relations_found": len(all_relations),
                        "memory_usage_mb": self.memory_manager.get_memory_usage() / (1024 * 1024)
                    }
                )
                
                # Cache result
                self.cache.put_query_result(query_hash, result)
                
                # Update statistics
                self._update_stats(result)
                
                # Mark nodes as accessed
                for node in all_nodes:
                    node.access()
                    
                self.logger.debug(f"Knowledge query completed in {result.processing_time:.3f}s")
                return result
                
        except Exception as e:
            self.logger.error(f"Error during knowledge query: {e}")
            return KnowledgeResult(
                query=query,
                processing_time=time.time() - start_time
            )
            
    def _generate_query_hash(self, query: KnowledgeQuery) -> str:
        """Generate hash for query caching."""
        query_str = f"{query.query_text}|{query.query_type}|{query.max_nodes}|{query.max_hops}|{query.min_confidence}"
        if query.knowledge_types:
            query_str += "|" + ",".join(kt.value for kt in query.knowledge_types)
        return hashlib.md5(query_str.encode()).hexdigest()
        
    def _update_stats(self, result: KnowledgeResult):
        """Update performance statistics."""
        self.stats["queries_executed"] += 1
        self.stats["nodes_accessed"] += len(result.nodes)
        
        # Update average query time
        total_queries = self.stats["queries_executed"]
        current_avg = self.stats["average_query_time"]
        self.stats["average_query_time"] = (
            (current_avg * (total_queries - 1) + result.processing_time) / total_queries
        )
        
        # Update cache hit rate
        cache_stats = self.cache.get_stats()
        self.stats["cache_hit_rate"] = cache_stats["hit_rate"]
        
    def add_knowledge_from_entities(self, entities: List[Entity], source: str = "entity_extraction"):
        """Add knowledge nodes from extracted entities."""
        for entity in entities:
            node_id = f"entity_{entity.entity_type.value}_{hashlib.md5(entity.text.encode()).hexdigest()[:8]}"
            
            # Determine knowledge type from entity type
            knowledge_type = self._map_entity_to_knowledge_type(entity.entity_type)
            
            node = KnowledgeNode(
                node_id=node_id,
                name=entity.text,
                knowledge_type=knowledge_type,
                content={
                    "entity_type": entity.entity_type.value,
                    "text": entity.text,
                    "normalized_value": entity.normalized_value,
                    "extraction_confidence": entity.confidence
                },
                confidence=entity.confidence,
                source=source,
                metadata={
                    "start_pos": entity.start_pos,
                    "end_pos": entity.end_pos
                }
            )
            
            # Store and cache
            self.knowledge_store.store_node(node)
            self.cache.put_node(node)
            
        self.logger.debug(f"Added {len(entities)} knowledge nodes from entities")
        
    def _map_entity_to_knowledge_type(self, entity_type: EntityType) -> KnowledgeType:
        """Map entity types to knowledge types."""
        mapping = {
            EntityType.PERSON: KnowledgeType.FACTUAL,
            EntityType.ORGANIZATION: KnowledgeType.FACTUAL,
            EntityType.DATE: KnowledgeType.TEMPORAL,
            EntityType.TIME: KnowledgeType.TEMPORAL,
            EntityType.LOCATION: KnowledgeType.SPATIAL,
            EntityType.FILE_PATH: KnowledgeType.SYSTEM,
            EntityType.TASK_NAME: KnowledgeType.PROCEDURAL,
            EntityType.COMMAND: KnowledgeType.PROCEDURAL
        }
        
        return mapping.get(entity_type, KnowledgeType.FACTUAL)
        
    def verify_fact(self, statement: str, confidence_threshold: float = 0.7) -> Tuple[bool, float, List[KnowledgeNode]]:
        """
        Verify a factual statement against the knowledge base.
        
        Args:
            statement: Factual statement to verify
            confidence_threshold: Minimum confidence for verification
            
        Returns:
            Tuple of (is_verified, confidence_score, supporting_nodes)
        """
        query = KnowledgeQuery(
            query_text=statement,
            query_type="fact_verification",
            max_nodes=5,
            max_hops=1,
            knowledge_types=[KnowledgeType.FACTUAL, KnowledgeType.SYSTEM]
        )
        
        result = self.query_knowledge(query)
        
        # Simple fact verification logic
        supporting_nodes = []
        total_confidence = 0.0
        
        for node in result.nodes:
            # Check if node content supports the statement
            node_text = json.dumps(node.content).lower()
            statement_words = set(statement.lower().split())
            node_words = set(node_text.split())
            
            # Calculate overlap score
            overlap = len(statement_words & node_words) / len(statement_words)
            if overlap > 0.3:  # Arbitrary threshold
                supporting_nodes.append(node)
                total_confidence += node.confidence * overlap
                
        # Calculate overall verification confidence
        if supporting_nodes:
            verification_confidence = total_confidence / len(supporting_nodes)
            is_verified = verification_confidence >= confidence_threshold
        else:
            verification_confidence = 0.0
            is_verified = False
            
        return is_verified, verification_confidence, supporting_nodes
        
    def get_knowledge_summary(self, knowledge_type: Optional[KnowledgeType] = None) -> Dict[str, Any]:
        """Get summary of knowledge base contents."""
        # Simple implementation - in production, this would query the database
        summary = {
            "total_nodes": len(self.cache.node_cache),  # Approximation
            "knowledge_types": {},
            "most_accessed": [],
            "recently_added": [],
            "cache_stats": self.cache.get_stats()
        }
        
        # Get sample nodes for analysis
        if knowledge_type:
            sample_nodes = self.knowledge_store.search_nodes("", [knowledge_type], 20)
        else:
            sample_nodes = self.knowledge_store.search_nodes("", None, 20)
            
        # Analyze knowledge distribution
        type_counts = defaultdict(int)
        for node in sample_nodes:
            type_counts[node.knowledge_type.value] += 1
            
        summary["knowledge_types"] = dict(type_counts)
        summary["most_accessed"] = sorted(sample_nodes, key=lambda n: n.access_count, reverse=True)[:5]
        summary["recently_added"] = sorted(sample_nodes, key=lambda n: n.timestamp, reverse=True)[:5]
        
        return summary
        
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        memory_usage_mb = self.memory_manager.get_memory_usage() / (1024 * 1024)
        
        return {
            "query_performance": self.stats.copy(),
            "memory_usage": {
                "current_mb": memory_usage_mb,
                "max_allowed_mb": self.memory_manager.max_memory_bytes / (1024 * 1024),
                "within_limits": self.memory_manager.is_within_limits()
            },
            "cache_performance": self.cache.get_stats(),
            "knowledge_distribution": self.get_knowledge_summary(),
            "configuration": {
                "database_path": self.knowledge_store.db_path,
                "memory_optimized": True,
                "caching_enabled": True
            }
        }
        
    def shutdown(self):
        """Shutdown the UKS integration and cleanup resources."""
        self.cache.clear()
        self.memory_manager.cleanup()
        self.logger.info("UKS Integration shutdown complete")


# Utility functions for easy integration

def create_knowledge_query(text: str, 
                         knowledge_types: Optional[List[str]] = None,
                         max_results: int = 10) -> KnowledgeQuery:
    """Create a knowledge query from simple parameters."""
    kt_list = None
    if knowledge_types:
        kt_list = [KnowledgeType(kt) for kt in knowledge_types if kt in [kt.value for kt in KnowledgeType]]
        
    return KnowledgeQuery(
        query_text=text,
        max_nodes=max_results,
        knowledge_types=kt_list
    )


def quick_knowledge_search(text: str, max_results: int = 5) -> List[KnowledgeNode]:
    """Quick knowledge search utility."""
    uks = UKSIntegration()
    try:
        query = create_knowledge_query(text, max_results=max_results)
        result = uks.query_knowledge(query)
        return result.nodes
    finally:
        uks.shutdown()


if __name__ == "__main__":
    # Example usage and testing
    def test_uks_integration():
        uks = UKSIntegration()
        
        try:
            # Test basic query
            query = KnowledgeQuery(
                query_text="ImpressionCore system capabilities",
                max_nodes=5,
                max_hops=1
            )
            
            result = uks.query_knowledge(query)
            
            print("UKS Integration Test Results:")
            print("=" * 50)
            print(f"Query: {query.query_text}")
            print(f"Nodes found: {len(result.nodes)}")
            print(f"Processing time: {result.processing_time:.3f}s")
            print(f"Confidence: {result.confidence:.2f}")
            
            for i, node in enumerate(result.nodes):
                print(f"\n{i+1}. {node.name} ({node.knowledge_type.value})")
                print(f"   Confidence: {node.confidence:.2f}")
                print(f"   Content: {node.content}")
                
            # Test fact verification
            print("\n" + "="*50)
            print("Fact Verification Test:")
            
            statement = "ImpressionCore targets GTX 1050 Ti hardware"
            is_verified, confidence, supporting = uks.verify_fact(statement)
            
            print(f"Statement: {statement}")
            print(f"Verified: {is_verified}")
            print(f"Confidence: {confidence:.2f}")
            print(f"Supporting nodes: {len(supporting)}")
            
            # Performance stats
            print("\n" + "="*50)
            print("Performance Statistics:")
            stats = uks.get_performance_stats()
            print(f"Memory usage: {stats['memory_usage']['current_mb']:.1f}MB")
            print(f"Cache hit rate: {stats['cache_performance']['hit_rate']:.2%}")
            print(f"Average query time: {stats['query_performance']['average_query_time']:.3f}s")
            
        finally:
            uks.shutdown()
    
    # Run test if executed directly
    test_uks_integration()
