#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\web_search_mcp\utils\citation.py #api #command_line #python #source_code #web_interface  
**Category:** Source Code  
**Status:** Active
"""









# Citation

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\web_search_mcp\utils\citation.py #api #command_line #python #source_code #web_interface  
**Category:** Source Code  
**Status:** Active

import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger("web-search-mcp.citation")

async def generate_citations(search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate citations for search results.
    
    Args:
        search_results: List of search result dictionaries
        
    Returns:
        The same list with citation fields filled
    """
    logger.info(f"Generating citations for {len(search_results)} results")
    
    for result in search_results:
        url = result.get("url", "")
        if not url:
            continue
            
        try:
            citation = await create_citation(
                title=result["title"],
                url=url
            )
            result["citation"] = citation
        except Exception as e:
            logger.error(f"Citation generation error for {url}: {e}")
            result["citation"] = f"{result['title']}. Retrieved from {url}"
    
    return search_results

async def create_citation(title: str, url: str) -> str:
    """
    Create a citation for a web page in APA format.
    
    Args:
        title: The title of the page
        url: The URL of the page
        
    Returns:
        A formatted citation string
    """
    # Extract domain for publisher info
    domain = urlparse(url).netloc
    domain = domain.replace("www.", "")
    
    # Get current date for "Retrieved on" part
    today = datetime.now().strftime("%B %d, %Y")
    
    # Try to extract more info from the page
    author = await extract_author(url)
    published_date = await extract_publication_date(url)
    
    # Format the citation in APA style
    if author and published_date:
        year = published_date.split(",")[0] if "," in published_date else published_date
        citation = f"{author}. ({year}). {title}. {domain.capitalize()}. Retrieved on {today} from {url}"
    elif author:
        citation = f"{author}. (n.d.). {title}. {domain.capitalize()}. Retrieved on {today} from {url}"
    elif published_date:
        year = published_date.split(",")[0] if "," in published_date else published_date
        citation = f"{title}. ({year}). {domain.capitalize()}. Retrieved on {today} from {url}"
    else:
        citation = f"{title}. (n.d.). {domain.capitalize()}. Retrieved on {today} from {url}"
    
    return citation

async def extract_author(url: str) -> Optional[str]:
    """
    Try to extract author information from a web page.
    
    Args:
        url: The URL of the page
        
    Returns:
        Author name or None if not found
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status != 200:
                    return None
                html = await response.text()
                
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for common author metadata
        author = None
        
        # Check meta tags
        meta_author = soup.find('meta', {'name': 'author'}) or soup.find('meta', {'property': 'article:author'})
        if meta_author and meta_author.get('content'):
            author = meta_author.get('content')
        
        # Check schema.org markup
        if not author:
            author_elem = soup.find(['span', 'div', 'a'], {'itemprop': 'author'})
            if author_elem:
                name_elem = author_elem.find({'itemprop': 'name'})
                if name_elem:
                    author = name_elem.text.strip()
                else:
                    author = author_elem.text.strip()
        
        # Check common author classes/IDs
        if not author:
            for selector in ['.author', '.byline', '.entry-author', '#author']:
                author_elem = soup.select_one(selector)
                if author_elem:
                    author = author_elem.text.strip()
                    break
        
        # Clean up author text
        if author:
            # Remove "By" or "Author:" prefixes
            author = re.sub(r'^(By|Author|Written by)\s*:?\s*', '', author, flags=re.IGNORECASE)
            # Remove extra spaces
            author = re.sub(r'\s+', ' ', author).strip()
            
        return author
    except Exception as e:
        logger.warning(f"Error extracting author from {url}: {e}")
        return None

async def extract_publication_date(url: str) -> Optional[str]:
    """
    Try to extract publication date from a web page.
    
    Args:
        url: The URL of the page
        
    Returns:
        Publication date or None if not found
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status != 200:
                    return None
                html = await response.text()
                
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for common date metadata
        date = None
        
        # Check meta tags
        for meta_name in ['published_time', 'article:published_time', 'date', 'publication-date']:
            meta_date = soup.find('meta', {'property': meta_name}) or soup.find('meta', {'name': meta_name})
            if meta_date and meta_date.get('content'):
                date_str = meta_date.get('content')
                # Extract year from ISO date format
                match = re.search(r'(\d{4})', date_str)
                if match:
                    date = match.group(1)
                    break
        
        # Check time elements
        if not date:
            time_elem = soup.find('time')
            if time_elem and time_elem.get('datetime'):
                date_str = time_elem.get('datetime')
                match = re.search(r'(\d{4})', date_str)
                if match:
                    date = match.group(1)
        
        # Check common date classes
        if not date:
            for selector in ['.date', '.published', '.publish-date', '.post-date']:
                date_elem = soup.select_one(selector)
                if date_elem:
                    date_text = date_elem.text.strip()
                    # Extract year from text
                    match = re.search(r'(\d{4})', date_text)
                    if match:
                        date = match.group(1)
                        break
        
        return date
    except Exception as e:
        logger.warning(f"Error extracting date from {url}: {e}")
        return None
