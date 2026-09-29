#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\web_search_mcp\utils\search.py #command_line #python #source_code #web_interface  
**Category:** Source Code  
**Status:** Active
"""









# Search

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\web_search_mcp\utils\search.py #command_line #python #source_code #web_interface  
**Category:** Source Code  
**Status:** Active

import logging
from typing import List, Dict, Any, Optional
import aiohttp
from duckduckgo_search import DDGS

logger = logging.getLogger("web-search-mcp.search")

async def perform_search(
    query: str, 
    num_results: int = 5, 
    safe_search: bool = True,
    timeout: int = 30
) -> List[Dict[str, Any]]:
    """
    Perform a web search using DuckDuckGo.
    
    Args:
        query: Search query
        num_results: Number of results to return
        safe_search: Whether to enable safe search
        timeout: Timeout in seconds
    
    Returns:
        List of dictionaries containing search results
    """
    logger.info(f"Performing search for: {query}")
    results = []
    
    try:
        # Use DuckDuckGo Search
        with DDGS() as ddgs:
            ddg_results = list(ddgs.text(
                query, 
                region='wt-wt',  # Worldwide results
                safesearch=safe_search,
                timelimit=None,  # No time limit
                max_results=num_results
            ))
            
            # Process the results
            for idx, result in enumerate(ddg_results):
                if idx >= num_results:
                    break
                    
                results.append({
                    "title": result.get("title", "No Title"),
                    "content": result.get("body", "No content available"),
                    "url": result.get("href", ""),
                    "citation": None  # Will be filled by citation module
                })
    
    except Exception as e:
        logger.error(f"Search error: {e}")
        # Fallback to basic results
        results.append({
            "title": "Search Error",
            "content": f"Failed to retrieve search results: {str(e)}",
            "url": "",
            "citation": None
        })
    
    logger.info(f"Found {len(results)} results for query: {query}")
    return results

async def fetch_page_content(url: str) -> Optional[str]:
    """
    Fetch the content of a web page for better citation information.
    
    Args:
        url: The URL to fetch
    
    Returns:
        HTML content of the page or None if failed
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"Failed to fetch {url}: Status {response.status}")
                    return None
    except Exception as e:
        logger.warning(f"Error fetching {url}: {e}")
        return None
