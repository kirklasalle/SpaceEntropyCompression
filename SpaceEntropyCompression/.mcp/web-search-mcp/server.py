#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\web_search_mcp\server.py #python #source_code #web_interface  
**Category:** Source Code  
**Status:** Active
"""





import asyncio
import json
import logging
import os
import sys
import time
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlparse, urljoin
import traceback

# Chronology loader (shared)
try:
    from assistant.chronology_loader import load_chronology, query_chronology, load_delta  # type: ignore
    HAS_CHRONOLOGY = True
except Exception:
    HAS_CHRONOLOGY = False

# Add the project root to Python path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, project_root)

try:
    from mcp.server import FastMCP
except ImportError as e:
    print(f"ERROR: MCP library import failed: {e}")
    print("Run: pip install mcp")
    sys.exit(1)

# Third-party imports for search functionality
try:
    import requests
    from bs4 import BeautifulSoup
    from googlesearch import search as google_search
    from ddgs import DDGS
except ImportError as e:
    print(f"ERROR: Search library import failed: {e}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Web Search MCP Server")

# Rate limiting state
class RateLimiter:
    def __init__(self):
        self.requests = []
        self.max_requests = 10
        self.time_window = 60  # seconds
    
    def can_make_request(self):
        now = time.time()
        # Remove requests older than time window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False

# Constants
RATE_LIMIT_ERROR = 'Rate limit exceeded. Please wait before making another request.'

rate_limiter = RateLimiter()

def safe_get_text(element, default=""):
    """Safely extract text from BeautifulSoup element."""
    try:
        return element.get_text(strip=True) if element else default
    except Exception:
        return default

def extract_page_content(html: str, url: str) -> Dict[str, Any]:
    """Extract structured content from HTML."""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        # Extract metadata
        title = safe_get_text(soup.find('title'), 'No title')
        description = ""
        
        # Try different meta description selectors
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc:
            meta_desc = soup.find('meta', attrs={'property': 'og:description'})
        if meta_desc:
            description = meta_desc.get('content', '')
        
        # Extract main content
        content_selectors = [
            'main', 'article', '[role="main"]', 
            '.content', '#content', '.main-content',
            '.post-content', '.entry-content'
        ]
        
        main_content = ""
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                main_content = safe_get_text(element)
                break
        
        # Fallback to body if no main content found
        if not main_content:
            main_content = safe_get_text(soup.find('body'))
        
        # Limit content length
        if len(main_content) > 2000:
            main_content = main_content[:2000] + "..."
        
        return {
            'url': url,
            'title': title,
            'description': description,
            'content': main_content,
            'word_count': len(main_content.split()),
            'extraction_time': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {e}")
        return {
            'url': url,
            'title': 'Error extracting content',
            'description': f'Error: {str(e)}',
            'content': '',
            'word_count': 0,
            'extraction_time': time.strftime('%Y-%m-%d %H:%M:%S')
        }

@mcp.tool()
def web_search(query: str, num_results: int = 10, use_google: bool = True) -> str:
    """
    Perform comprehensive web search using Google and DuckDuckGo with advanced operators.
    
    Args:
        query: Search query (can include Google operators like site:, intitle:, filetype:, etc.)
        num_results: Number of results to return (default: 10, max: 20)
        use_google: Whether to use Google search (default: True)
    
    Returns:
        JSON string with search results including titles, URLs, snippets, and metadata
    """
    if not rate_limiter.can_make_request():
        return json.dumps({
            'error': RATE_LIMIT_ERROR,
            'status': 'rate_limited'
        })
    
    try:
        # Limit num_results
        num_results = min(num_results, 20)
        
        results = []
        
        if use_google:
            try:
                # Use googlesearch library
                google_urls = list(google_search(query, num_results=num_results, sleep_interval=2))
                
                for i, url in enumerate(google_urls):
                    results.append({
                        'rank': i + 1,
                        'title': f'Google Result {i + 1}',
                        'url': url,
                        'snippet': 'Google search result',
                        'source': 'Google'
                    })
            except Exception as e:
                logger.warning(f"Google search failed: {e}")
        
        # Add DuckDuckGo results if Google failed or as supplementary
        try:
            with DDGS() as ddgs:
                ddg_results = list(ddgs.text(query, max_results=min(num_results, 10)))
                
                start_rank = len(results) + 1
                for i, result in enumerate(ddg_results):
                    results.append({
                        'rank': start_rank + i,
                        'title': result.get('title', 'No title'),
                        'url': result.get('href', ''),
                        'snippet': result.get('body', 'No description'),
                        'source': 'DuckDuckGo'
                    })
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed: {e}")
        
        if not results:
            return json.dumps({
                'error': 'No search results found',
                'status': 'no_results',
                'query': query
            })
        
        return json.dumps({
            'query': query,
            'total_results': len(results),
            'results': results[:num_results],
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'success'
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return json.dumps({
            'error': f'Search failed: {str(e)}',
            'status': 'error',
            'query': query
        })

@mcp.tool()
def fetch_webpage(url: str, extract_content: bool = True) -> str:
    """
    Fetch and extract content from a specific webpage URL.
    
    Args:
        url: The webpage URL to fetch
        extract_content: Whether to extract and parse content (default: True)
    
    Returns:
        JSON string with webpage content including title, description, and main text
    """
    if not rate_limiter.can_make_request():
        return json.dumps({
            'error': RATE_LIMIT_ERROR,
            'status': 'rate_limited'
        })
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        if extract_content:
            content_data = extract_page_content(response.text, url)
            return json.dumps(content_data, indent=2)
        else:
            return json.dumps({
                'url': url,
                'status_code': response.status_code,
                'content_length': len(response.text),
                'content_type': response.headers.get('content-type', 'unknown'),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'success'
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return json.dumps({
            'url': url,
            'error': f'Failed to fetch webpage: {str(e)}',
            'status': 'error'
        })

@mcp.tool()
def search_with_filters(query: str, filter_type: str = "academic", num_results: int = 10) -> str:
    """
    Advanced search with pre-configured filters for academic, technical, or news content.
    
    Args:
        query: Base search query
        filter_type: Type of filter ('academic', 'technical', 'news', 'recent')
        num_results: Number of results to return
    
    Returns:
        JSON string with filtered search results
    """
    if not rate_limiter.can_make_request():
        return json.dumps({
            'error': RATE_LIMIT_ERROR,
            'status': 'rate_limited'
        })
    
    # Define filter configurations
    filters = {
        'academic': {
            'sites': ['edu', 'org'],
            'filetypes': ['pdf'],
            'operators': ['site:*.edu OR site:*.org', 'filetype:pdf']
        },
        'technical': {
            'sites': ['github.com', 'stackoverflow.com', 'readthedocs.io'],
            'operators': ['site:github.com OR site:stackoverflow.com OR site:readthedocs.io']
        },
        'news': {
            'sites': ['reuters.com', 'bbc.com', 'ap.org'],
            'operators': ['site:reuters.com OR site:bbc.com OR site:ap.org']
        },
        'recent': {
            'operators': ['after:2023-01-01']
        }
    }
    
    if filter_type not in filters:
        return json.dumps({
            'error': f'Unknown filter type: {filter_type}',
            'available_filters': list(filters.keys()),
            'status': 'error'
        })
    
    # Build filtered query
    filter_config = filters[filter_type]
    filtered_query = query
    
    if 'operators' in filter_config:
        filtered_query = f"{query} {' '.join(filter_config['operators'])}"
    
    # Use the web_search function with the filtered query
    return web_search(filtered_query, num_results)

@mcp.tool()
def get_search_suggestions(query: str) -> str:
    """
    Get search suggestions and query optimization recommendations.
    
    Args:
        query: Initial search query
    
    Returns:
        JSON string with search suggestions and optimization tips
    """
    try:
        suggestions = {
            'original_query': query,
            'suggestions': [],
            'operators': [],
            'tips': []
        }
        
        # Basic query analysis
        words = query.lower().split()
        
        # Suggest operators based on query content
        if any(word in ['research', 'study', 'academic'] for word in words):
            suggestions['operators'].append('site:*.edu - Search academic institutions')
            suggestions['operators'].append('filetype:pdf - Find research papers')
            
        if any(word in ['code', 'programming', 'development'] for word in words):
            suggestions['operators'].append('site:github.com - Find code repositories')
            suggestions['operators'].append('site:stackoverflow.com - Find programming help')
            
        if any(word in ['news', 'current', 'recent'] for word in words):
            suggestions['operators'].append('after:2023-01-01 - Find recent content')
            
        # Query improvement suggestions
        if len(words) < 3:
            suggestions['tips'].append('Consider adding more specific terms to narrow results')
            
        if len(words) > 8:
            suggestions['tips'].append('Consider using quotes for exact phrases')
            
        # Alternative query formulations
        suggestions['suggestions'] = [
            f'"{query}"',  # Exact phrase
            f'{query} tutorial',  # Add tutorial
            f'{query} guide',  # Add guide
            f'{query} examples'  # Add examples
        ]
        
        return json.dumps(suggestions, indent=2)
        
    except Exception as e:
        return json.dumps({
            'error': f'Failed to generate suggestions: {str(e)}',
            'status': 'error'
        })

@mcp.tool()
def bulk_url_fetch(urls: List[str], max_urls: int = 5) -> str:
    """
    Fetch content from multiple URLs efficiently.
    
    Args:
        urls: List of URLs to fetch
        max_urls: Maximum number of URLs to process (default: 5)
    
    Returns:
        JSON string with content from all URLs
    """
    if not rate_limiter.can_make_request():
        return json.dumps({
            'error': RATE_LIMIT_ERROR,
            'status': 'rate_limited'
        })
    
    try:
        # Limit the number of URLs
        urls = urls[:max_urls]
        results = []
        
        for url in urls:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                content_data = extract_page_content(response.text, url)
                results.append(content_data)
                
                # Small delay between requests
                time.sleep(1)
                
            except Exception as e:
                results.append({
                    'url': url,
                    'error': str(e),
                    'status': 'error'
                })
        
        return json.dumps({
            'total_urls': len(urls),
            'successful_fetches': len([r for r in results if 'error' not in r]),
            'results': results,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'success'
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            'error': f'Bulk fetch failed: {str(e)}',
            'status': 'error'
        })

@mcp.tool()
def chronology_snapshot(kind: str = "all", limit: int = 40, reverse: bool = False) -> str:
    """Chronology snapshot (docs/source/mcp/root/all) creation-ordered."""
    if not HAS_CHRONOLOGY:
        return json.dumps({"error": "chronology_loader_not_available"})
    try:
        data = load_chronology()
        items = query_chronology(data, kind=kind, limit=limit, reverse=reverse)
        return json.dumps({
            'kind': kind,
            'limit': limit,
            'reverse': reverse,
            'count': len(items),
            'items': items,
            'generated': data.get('generated'),
            'ordering': data.get('ordering'),
            'schema_version': data.get('schema_version')
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": "chronology_snapshot_failed", "detail": str(e)})

@mcp.tool()
def chronology_delta(include: Optional[List[str]] = None, limit: int = 200) -> str:
    """Chronology delta (added/removed/changed) if diff present."""
    if not HAS_CHRONOLOGY:
        return json.dumps({"error": "chronology_loader_not_available"})
    try:
        diff = load_delta()
        if not diff:
            return json.dumps({"error": "delta_not_available", "hint": "Generate chronology with --delta in IDS."})
        include = include or ['added','removed','changed']
        payload: Dict[str, Any] = {'generated': diff.get('generated'), 'counts': diff.get('counts', {})}
        for key in ['added','removed','changed']:
            if key in include and key in diff:
                data_slice = diff[key]
                payload[key] = data_slice[:limit] if limit else data_slice
        return json.dumps(payload, indent=2)
    except Exception as e:
        return json.dumps({"error": "chronology_delta_failed", "detail": str(e)})

@mcp.tool()
def chronology_stats() -> str:
    """Chronology statistics (counts per category + delta counts)."""
    if not HAS_CHRONOLOGY:
        return json.dumps({"error": "chronology_loader_not_available"})
    try:
        data = load_chronology()
        stats: Dict[str, Any] = {
            'documents': len(data.get('documents', [])),
            'source': len(data.get('source', [])),
            'mcp': len(data.get('mcp', [])),
            'root': len(data.get('root', [])),
            'generated': data.get('generated'),
            'ordering': data.get('ordering'),
            'schema_version': data.get('schema_version')
        }
        diff = load_delta()
        if diff and diff.get('counts'):
            stats['delta'] = diff['counts']
        return json.dumps(stats, indent=2)
    except Exception as e:
        return json.dumps({"error": "chronology_stats_failed", "detail": str(e)})

def main():
    """Main entry point for the MCP server."""
    try:
        logger.info("🔍 Starting Web Search MCP Server...")
        logger.info("Available tools:")
        logger.info("  - web_search: Comprehensive web search with Google operators")
        logger.info("  - fetch_webpage: Fetch and extract content from URLs")
        logger.info("  - search_with_filters: Advanced search with predefined filters")
        logger.info("  - get_search_suggestions: Query optimization recommendations")
        logger.info("  - bulk_url_fetch: Fetch multiple URLs efficiently")
        
        # Run the FastMCP server
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    main()
