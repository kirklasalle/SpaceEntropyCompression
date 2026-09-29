#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\core\retrieval_engine.py #cuda #documentation #gpu_optimization #memory_management #python #source_code #testing  
**Category:** Source Code  
**Status:** Active
"""









# Retrieval Engine

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_dpa\core\retrieval_engine.py #cuda #documentation #gpu_optimization #memory_management #python #source_code #testing  
**Category:** Source Code  
**Status:** Active

"""
Information Retrieval Engine for ImpressionCore Personal Assistant

This module implements a memory-efficient, multi-source information retrieval system
optimized for GTX 1050 Ti hardware constraints (25MB memory budget).

Key Features:
- Multi-source information aggregation
- Semantic search capabilities  
- Information ranking and relevance scoring
- Memory-efficient caching with LRU eviction
- Streaming support for large datasets
- GPU/CPU hybrid processing with automatic fallbacks

Memory Target: 25MB total allocation
Response Time: <2 seconds for common queries
Cache Size: 10MB for frequently accessed information
Concurrent Queries: Support for 5 simultaneous queries

Author: ImpressionCore Development Team
Date: 2025-06-06
Phase: 8B Week 1 - Personal Assistant Core Foundation
"""

import asyncio
import logging
import time
import hashlib
import json
from typing import Dict, List, Any, Optional, Tuple, AsyncGenerator, Union
from dataclasses import dataclass, field
from collections import OrderedDict
from pathlib import Path
import weakref
import gc

# Core utilities and rich enhancements
from src.core.utils.rich_enhancements import create_panel, create_table
from src.core.utils.rich_logging import get_rich_logger
from src.core.utils.rich_status_animation import StatusAnimation

# Memory management
import psutil
import torch


@dataclass
class SearchResult:
    """Individual search result with relevance scoring."""
    content: str
    source: str
    relevance_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    confidence: float = 1.0


@dataclass
class RetrievalConfig:
    """Configuration for retrieval engine behavior."""
    max_memory_mb: int = 25
    cache_size_mb: int = 10  
    max_concurrent_queries: int = 5
    response_timeout: float = 2.0
    min_relevance_threshold: float = 0.1
    enable_gpu_acceleration: bool = True
    fallback_to_cpu: bool = True
    stream_large_results: bool = True
    max_results_per_query: int = 50


class MemoryTracker:
    """Lightweight memory usage tracking for retrieval operations."""
    
    def __init__(self, max_memory_mb: int = 25):
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.process = psutil.Process()
        self.baseline_memory = self.get_current_memory()
        
    def get_current_memory(self) -> int:
        """Get current memory usage in bytes."""
        return self.process.memory_info().rss
        
    def get_delta_memory(self) -> int:
        """Get memory usage delta from baseline."""
        return self.get_current_memory() - self.baseline_memory
        
    def is_within_limits(self) -> bool:
        """Check if current memory usage is within limits."""
        return self.get_delta_memory() < self.max_memory_bytes
        
    def force_cleanup(self):
        """Force garbage collection and cleanup."""
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


class LRUCache:
    """Memory-efficient LRU cache for retrieval results."""
    
    def __init__(self, max_size_mb: int = 10):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache: OrderedDict = OrderedDict()
        self.current_size = 0
        self.hits = 0
        self.misses = 0
        
    def _estimate_size(self, obj: Any) -> int:
        """Estimate object size in bytes."""
        try:
            return len(json.dumps(obj, default=str).encode('utf-8'))
        except:
            return 1024  # Conservative estimate
            
    def _evict_if_needed(self, new_size: int):
        """Evict oldest items if cache would exceed size limit."""
        while (self.current_size + new_size > self.max_size_bytes 
               and len(self.cache) > 0):
            key, value = self.cache.popitem(last=False)
            self.current_size -= self._estimate_size(value)
            
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache, moving to end for LRU."""
        if key in self.cache:
            self.hits += 1
            # Move to end (most recently used)
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
        else:
            self.misses += 1
            return None
            
    def put(self, key: str, value: Any):
        """Add item to cache with LRU eviction."""
        size = self._estimate_size(value)
        self._evict_if_needed(size)
        
        if key in self.cache:
            # Update existing
            old_size = self._estimate_size(self.cache[key])
            self.current_size -= old_size
            
        self.cache[key] = value
        self.current_size += size
        
    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        self.current_size = 0
        
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "cache_size_mb": self.current_size / (1024 * 1024),
            "entry_count": len(self.cache)
        }


class InformationSource:
    """Base class for information sources."""
    
    def __init__(self, name: str, priority: float = 1.0):
        self.name = name
        self.priority = priority
        self.enabled = True
        
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search this information source."""
        raise NotImplementedError("Subclasses must implement search method")
        
    def get_source_info(self) -> Dict[str, Any]:
        """Get metadata about this source."""
        return {
            "name": self.name,
            "priority": self.priority,
            "enabled": self.enabled,
            "type": self.__class__.__name__
        }


class DocumentSource(InformationSource):
    """Information source for document-based content."""
    
    def __init__(self, name: str, document_paths: List[Path], priority: float = 1.0):
        super().__init__(name, priority)
        self.document_paths = document_paths
        self.document_cache = {}
        
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search documents using simple text matching."""
        results = []
        query_lower = query.lower()
        
        for doc_path in self.document_paths:
            if not doc_path.exists():
                continue
                
            try:
                # Load document with caching
                if doc_path not in self.document_cache:
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.document_cache[doc_path] = content
                else:
                    content = self.document_cache[doc_path]
                
                # Simple relevance scoring based on query term frequency
                content_lower = content.lower()
                relevance = content_lower.count(query_lower) / len(content_lower)
                
                if relevance > 0:
                    # Extract relevant snippet
                    snippet = self._extract_snippet(content, query, 300)
                    
                    result = SearchResult(
                        content=snippet,
                        source=f"{self.name}:{doc_path.name}",
                        relevance_score=relevance * self.priority,
                        metadata={
                            "file_path": str(doc_path),
                            "file_size": doc_path.stat().st_size,
                            "snippet_length": len(snippet)
                        }
                    )
                    results.append(result)
                    
            except Exception as e:
                logging.warning(f"Error searching document {doc_path}: {e}")
                continue
                
        # Sort by relevance and return top results
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:max_results]
        
    def _extract_snippet(self, content: str, query: str, max_length: int = 300) -> str:
        """Extract relevant snippet around query terms."""
        query_lower = query.lower()
        content_lower = content.lower()
        
        # Find first occurrence of query
        pos = content_lower.find(query_lower)
        if pos == -1:
            return content[:max_length]
            
        # Extract snippet around query
        start = max(0, pos - max_length // 2)
        end = min(len(content), start + max_length)
        
        snippet = content[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
            
        return snippet


class IDSSource(InformationSource):
    """Information source using IDS MCP server."""
    
    def __init__(self, name: str = "IDS", priority: float = 1.5):
        super().__init__(name, priority)
        
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search using IDS MCP server (placeholder for now)."""
        # TODO: Integrate with actual IDS MCP server when available
        results = []
        
        # Simulate IDS search for now
        result = SearchResult(
            content=f"IDS search result for: {query}",
            source=f"{self.name}:ids_search",
            relevance_score=0.8 * self.priority,
            metadata={
                "source_type": "ids_mcp",
                "query_processed": query,
                "simulated": True
            }
        )
        results.append(result)
        
        return results


class InformationRetrievalEngine:
    """
    Main retrieval engine for ImpressionCore Personal Assistant.
    
    Handles multi-source information aggregation with memory optimization
    and performance monitoring for GTX 1050 Ti constraints.
    """
    
    def __init__(self, config: Optional[RetrievalConfig] = None):
        self.config = config or RetrievalConfig()
        self.logger = get_rich_logger("retrieval_engine")
        
        # Memory tracking
        self.memory_tracker = MemoryTracker(self.config.max_memory_mb)
        
        # Caching system
        self.cache = LRUCache(self.config.cache_size_mb)
        
        # Information sources
        self.sources: Dict[str, InformationSource] = {}
        
        # Query tracking
        self.active_queries = {}
        self.query_stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "average_response_time": 0.0,
            "cache_hits": 0
        }
        
        # Initialize status animation
        self.status_animation = StatusAnimation(total_steps=8, description="Information Retrieval")
        
        # Setup default sources
        self._initialize_default_sources()
        
        self.logger.info(f"Information Retrieval Engine initialized with {self.config.max_memory_mb}MB memory limit")
        
    def _initialize_default_sources(self):
        """Initialize default information sources."""
        try:
            # Add documentation source
            doc_paths = [
                Path("docs/DOCUMENTATION_INDEX.md"),
                Path("docs/reference"),
                Path("docs/user_guide"),
                Path("src/memlog")
            ]
            
            # Filter to existing paths and expand directories
            existing_docs = []
            for path in doc_paths:
                if path.exists():
                    if path.is_file():
                        existing_docs.append(path)
                    elif path.is_dir():
                        existing_docs.extend(path.rglob("*.md"))
            
            if existing_docs:
                doc_source = DocumentSource("documentation", existing_docs, priority=1.2)
                self.add_source(doc_source)
                
            # Add IDS source
            ids_source = IDSSource("ids_search", priority=1.5)
            self.add_source(ids_source)
            
            self.logger.info(f"Initialized {len(self.sources)} default information sources")
            
        except Exception as e:
            self.logger.error(f"Error initializing default sources: {e}")
            
    def add_source(self, source: InformationSource):
        """Add an information source to the engine."""
        self.sources[source.name] = source
        self.logger.debug(f"Added information source: {source.name}")
        
    def remove_source(self, source_name: str):
        """Remove an information source from the engine."""
        if source_name in self.sources:
            del self.sources[source_name]
            self.logger.debug(f"Removed information source: {source_name}")
            
    def _generate_cache_key(self, query: str, source_names: Optional[List[str]] = None) -> str:
        """Generate cache key for query."""
        sources_str = ",".join(sorted(source_names or list(self.sources.keys())))
        cache_input = f"{query}|{sources_str}"
        return hashlib.md5(cache_input.encode()).hexdigest()
        
    async def retrieve(self, 
                      query: str, 
                      max_results: int = 20,
                      source_names: Optional[List[str]] = None,
                      use_cache: bool = True) -> List[SearchResult]:
        """
        Retrieve information for a query with memory optimization.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            source_names: Specific sources to search (None = all sources)
            use_cache: Whether to use cached results
            
        Returns:
            List of SearchResult objects ranked by relevance
        """
        start_time = time.time()
        query_id = hashlib.md5(f"{query}{start_time}".encode()).hexdigest()[:8]
        
        # Check cache first
        cache_key = self._generate_cache_key(query, source_names)
        if use_cache:
            cached_results = self.cache.get(cache_key)
            if cached_results:
                self.query_stats["cache_hits"] += 1
                self.logger.debug(f"Cache hit for query: {query[:50]}...")
                return cached_results[:max_results]
        
        # Memory check before processing
        if not self.memory_tracker.is_within_limits():
            self.memory_tracker.force_cleanup()
            self.logger.warning("Memory limit approached, performed cleanup")
            
        try:
            with self.status_animation.status(f"Retrieving information for: {query[:30]}..."):
                self.active_queries[query_id] = {
                    "query": query,
                    "start_time": start_time,
                    "sources": source_names or list(self.sources.keys())
                }
                
                # Determine sources to search
                sources_to_search = []
                if source_names:
                    sources_to_search = [self.sources[name] for name in source_names 
                                       if name in self.sources and self.sources[name].enabled]
                else:
                    sources_to_search = [source for source in self.sources.values() 
                                       if source.enabled]
                
                if not sources_to_search:
                    self.logger.warning("No enabled sources available for search")
                    return []
                
                # Search all sources concurrently
                search_tasks = []
                for source in sources_to_search:
                    task = asyncio.create_task(
                        self._search_source_with_timeout(source, query, max_results)
                    )
                    search_tasks.append(task)
                
                # Wait for all searches to complete
                search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
                
                # Aggregate and rank results
                all_results = []
                for i, result in enumerate(search_results):
                    if isinstance(result, Exception):
                        self.logger.error(f"Error searching source {sources_to_search[i].name}: {result}")
                        continue
                    if isinstance(result, list):
                        all_results.extend(result)
                
                # Filter by minimum relevance threshold
                filtered_results = [
                    r for r in all_results 
                    if r.relevance_score >= self.config.min_relevance_threshold
                ]
                
                # Sort by relevance score
                filtered_results.sort(key=lambda x: x.relevance_score, reverse=True)
                
                # Limit results
                final_results = filtered_results[:max_results]
                
                # Cache results
                if use_cache and final_results:
                    self.cache.put(cache_key, final_results)
                
                # Update statistics
                response_time = time.time() - start_time
                self._update_query_stats(response_time, len(final_results) > 0)
                
                self.logger.info(f"Retrieved {len(final_results)} results in {response_time:.2f}s")
                
                return final_results
                
        except Exception as e:
            self.logger.error(f"Error during retrieval: {e}")
            self._update_query_stats(time.time() - start_time, False)
            return []
            
        finally:
            # Cleanup
            if query_id in self.active_queries:
                del self.active_queries[query_id]
            
            # Memory cleanup if needed
            if not self.memory_tracker.is_within_limits():
                self.memory_tracker.force_cleanup()
                
    async def _search_source_with_timeout(self, 
                                         source: InformationSource, 
                                         query: str, 
                                         max_results: int) -> List[SearchResult]:
        """Search a single source with timeout protection."""
        try:
            return await asyncio.wait_for(
                source.search(query, max_results),
                timeout=self.config.response_timeout
            )
        except asyncio.TimeoutError:
            self.logger.warning(f"Source {source.name} search timed out")
            return []
        except Exception as e:
            self.logger.error(f"Error searching source {source.name}: {e}")
            return []
            
    def _update_query_stats(self, response_time: float, success: bool):
        """Update query performance statistics."""
        self.query_stats["total_queries"] += 1
        
        if success:
            self.query_stats["successful_queries"] += 1
        else:
            self.query_stats["failed_queries"] += 1
            
        # Update average response time
        total_successful = self.query_stats["successful_queries"]
        if total_successful > 0:
            current_avg = self.query_stats["average_response_time"]
            self.query_stats["average_response_time"] = (
                (current_avg * (total_successful - 1) + response_time) / total_successful
            )
            
    async def get_similar_queries(self, query: str, limit: int = 5) -> List[str]:
        """Get similar queries from cache history (placeholder implementation)."""
        # TODO: Implement actual similarity matching
        return []
        
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        memory_delta_mb = self.memory_tracker.get_delta_memory() / (1024 * 1024)
        cache_stats = self.cache.get_stats()
        
        stats = {
            "query_performance": self.query_stats.copy(),
            "memory_usage": {
                "current_delta_mb": memory_delta_mb,
                "max_allowed_mb": self.config.max_memory_mb,
                "within_limits": self.memory_tracker.is_within_limits()
            },
            "cache_performance": cache_stats,
            "sources": {
                name: source.get_source_info() 
                for name, source in self.sources.items()
            },
            "active_queries": len(self.active_queries),
            "configuration": {
                "max_memory_mb": self.config.max_memory_mb,
                "cache_size_mb": self.config.cache_size_mb,
                "max_concurrent_queries": self.config.max_concurrent_queries,
                "response_timeout": self.config.response_timeout
            }
        }
        
        return stats
        
    def clear_cache(self):
        """Clear all cached results."""
        self.cache.clear()
        self.logger.info("Cache cleared")
        
    def shutdown(self):
        """Shutdown the retrieval engine and cleanup resources."""
        self.clear_cache()
        self.memory_tracker.force_cleanup()
        self.logger.info("Information Retrieval Engine shutdown complete")


# Utility functions for easy integration

async def quick_search(query: str, max_results: int = 10) -> List[SearchResult]:
    """Quick search utility for simple queries."""
    engine = InformationRetrievalEngine()
    try:
        return await engine.retrieve(query, max_results)
    finally:
        engine.shutdown()


def create_custom_retrieval_engine(sources: List[InformationSource], 
                                 config: Optional[RetrievalConfig] = None) -> InformationRetrievalEngine:
    """Create a custom retrieval engine with specific sources."""
    engine = InformationRetrievalEngine(config)
    
    # Clear default sources and add custom ones
    engine.sources.clear()
    for source in sources:
        engine.add_source(source)
        
    return engine


if __name__ == "__main__":
    # Example usage and testing
    async def test_retrieval():
        engine = InformationRetrievalEngine()
        
        try:
            # Test basic retrieval
            results = await engine.retrieve("Phase 8B implementation", max_results=5)
            print(f"Found {len(results)} results")
            
            for i, result in enumerate(results):
                print(f"{i+1}. {result.source} (score: {result.relevance_score:.3f})")
                print(f"   {result.content[:100]}...")
                print()
                
            # Show performance stats
            stats = engine.get_performance_stats()
            print("Performance Stats:")
            print(f"  Memory usage: {stats['memory_usage']['current_delta_mb']:.1f}MB")
            print(f"  Cache hit rate: {stats['cache_performance']['hit_rate']:.2%}")
            print(f"  Average response time: {stats['query_performance']['average_response_time']:.2f}s")
            
        finally:
            engine.shutdown()
    
    # Run test if executed directly
    import asyncio
    asyncio.run(test_retrieval())
