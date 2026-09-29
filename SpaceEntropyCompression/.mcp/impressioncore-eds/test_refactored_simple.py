#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_eds\test_refactored_simple.py #api #command_line #memory_management #python #source_code #testing  
**Category:** Source Code  
**Status:** Active
"""









# !/usr/bin/env python3

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_eds\test_refactored_simple.py #api #command_line #memory_management #python #source_code #testing  
**Category:** Source Code  
**Status:** Active

"""
ImpressionCore-EDS Test - Simplified Refactored Version
Testing core functionality without optional dependencies
"""

import asyncio
import aiohttp
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
import hashlib
import os
import re
from dataclasses import dataclass, asdict
import gc
import psutil
from asyncio import Semaphore

# Core imports that should be available
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.progress import Progress
from rich.panel import Panel

console = Console()

# GTX 1050 Ti Configuration
class GTX1050TiConfig:
    MAX_MEMORY_MB = 3584  # 3.5GB max for data processing
    MAX_CONCURRENT_REQUESTS = 8  # Optimized for 4GB VRAM
    
    @classmethod
    def get_memory_usage(cls) -> float:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / (1024 * 1024)
        except:
            return 0.0
    
    @classmethod
    def check_memory_limit(cls) -> bool:
        """Check if we're within memory limits."""
        return cls.get_memory_usage() < cls.MAX_MEMORY_MB

# Simple quality assessment
@dataclass
class ContentQuality:
    educational_value: float
    readability_score: float
    content_length: int
    structure_score: float
    overall_score: float
    
    def meets_b1_threshold(self) -> bool:
        """Check if content meets B1 quality threshold (9.0+)."""
        return self.overall_score >= 9.0

# Rate limiting
class SimpleRateLimiter:
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def acquire(self):
        now = time.time()
        # Remove old requests
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        if len(self.requests) >= self.max_requests:
            sleep_time = self.time_window - (now - self.requests[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        self.requests.append(now)

# Simplified EDS Server
class ImpressionCoreEDSTest:
    def __init__(self):
        self.version = "2.1-TEST"
        self.name = "ImpressionCore-EDS-Test"
        
        self.config = {
            'max_concurrent_requests': GTX1050TiConfig.MAX_CONCURRENT_REQUESTS,
            'request_timeout': 30,
            'quality_threshold': 9.0,
            'user_agent': 'ImpressionCore-EDS/2.1-Test (Educational Research)'
        }
        
        self.session = None
        self.semaphore = Semaphore(self.config['max_concurrent_requests'])
        self.rate_limiter = SimpleRateLimiter()
        
        self.stats = {
            'requests_made': 0,
            'successful_scrapes': 0,
            'failed_scrapes': 0,
            'start_time': time.time()
        }
        
        console.print(Panel(
            f"[bold green]🚀 {self.name} v{self.version} Initialized[/bold green]\n"
            f"[cyan]Sacred Covenant Compliant • GTX 1050 Ti Optimized • Test Version[/cyan]\n"
            f"Max Concurrent: {self.config['max_concurrent_requests']} | "
            f"Quality Threshold: {self.config['quality_threshold']}/10",
            style="bold blue"
        ))
    
    async def __aenter__(self):
        """Async context manager entry."""
        connector = aiohttp.TCPConnector(limit=self.config['max_concurrent_requests'])
        timeout = aiohttp.ClientTimeout(total=self.config['request_timeout'])
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': self.config['user_agent']}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def fetch_url(self, url: str) -> Optional[str]:
        """Fetch URL content with rate limiting."""
        await self.rate_limiter.acquire()
        
        async with self.semaphore:
            self.stats['requests_made'] += 1
            
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        self.stats['successful_scrapes'] += 1
                        return html
                    else:
                        console.print(f"[yellow]HTTP {response.status} for {url}[/yellow]")
                        return None
            except Exception as e:
                self.stats['failed_scrapes'] += 1
                console.print(f"[red]Failed to fetch {url}: {e}[/red]")
                return None
    
    def extract_content(self, html: str, url: str) -> Dict[str, Any]:
        """Extract content using BeautifulSoup."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()
        
        # Get main content
        main_content = soup.find('body') or soup
        text = main_content.get_text(separator=' ', strip=True)
        
        # Extract headings
        headings = [h.get_text(strip=True) for h in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
        
        return {
            'text': text,
            'headings': headings,
            'word_count': len(text.split()),
            'extraction_method': 'beautifulsoup_simple'
        }
    
    def assess_quality(self, content: Dict[str, Any]) -> ContentQuality:
        """Simple quality assessment."""
        text = content.get('text', '')
        word_count = len(text.split())
        headings = content.get('headings', [])
        
        # Basic scoring
        if word_count < 50:
            educational_value = 2.0
        elif word_count > 5000:
            educational_value = 6.0
        else:
            educational_value = min(8.0, 4.0 + (word_count / 1000))
        
        # Readability (simple version)
        avg_word_length = sum(len(word) for word in text.split()) / max(1, word_count)
        readability_score = max(1.0, min(10.0, 10 - (avg_word_length - 4)))
        
        # Structure score
        structure_score = min(8.0, len(headings) * 2)
        
        # Overall score
        overall_score = (educational_value * 0.5 + readability_score * 0.3 + structure_score * 0.2)
        
        return ContentQuality(
            educational_value=educational_value,
            readability_score=readability_score,
            content_length=word_count,
            structure_score=structure_score,
            overall_score=overall_score
        )
    
    async def scrape_wikipedia_test(self, topic: str) -> Dict[str, Any]:
        """Test Wikipedia scraping."""
        console.print(f"[cyan]🔍 Testing Wikipedia scraping for: {topic}[/cyan]")
        
        url = f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
        
        try:
            html = await self.fetch_url(url)
            if not html:
                return {"error": "Failed to fetch Wikipedia content"}
            
            content = self.extract_content(html, url)
            quality = self.assess_quality(content)
            
            result = {
                'url': url,
                'topic': topic,
                'content': content,
                'quality': asdict(quality),
                'scraped_at': datetime.now().isoformat()
            }
            
            console.print(f"[green]✅ Wikipedia scraping successful[/green]")
            console.print(f"[blue]Quality Score: {quality.overall_score:.1f}/10[/blue]")
            console.print(f"[blue]Word Count: {content['word_count']}[/blue]")
            
            return result
            
        except Exception as e:
            console.print(f"[red]❌ Wikipedia scraping failed: {e}[/red]")
            return {"error": f"Wikipedia scraping failed: {str(e)}"}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        runtime = time.time() - self.stats['start_time']
        success_rate = self.stats['successful_scrapes'] / max(1, self.stats['requests_made'])
        
        return {
            'runtime_seconds': runtime,
            'requests_made': self.stats['requests_made'],
            'successful_scrapes': self.stats['successful_scrapes'],
            'failed_scrapes': self.stats['failed_scrapes'],
            'success_rate': success_rate,
            'memory_usage_mb': GTX1050TiConfig.get_memory_usage()
        }

# Test function
async def test_eds_refactored():
    """Test the refactored EDS functionality."""
    console.print("[bold blue]🧪 Testing ImpressionCore-EDS Refactored Functionality[/bold blue]")
    
    async with ImpressionCoreEDSTest() as server:
        # Test Wikipedia scraping
        result = await server.scrape_wikipedia_test("Machine_learning")
        
        if 'error' not in result:
            console.print("\n[bold green]✅ SCRAPING TEST SUCCESSFUL![/bold green]")
            console.print(f"Topic: {result.get('topic', 'N/A')}")
            console.print(f"Word Count: {result['content']['word_count']}")
            console.print(f"Quality Score: {result['quality']['overall_score']:.1f}/10")
            console.print(f"Headings Found: {len(result['content']['headings'])}")
            
            # Show first few headings
            headings = result['content']['headings'][:5]
            if headings:
                console.print(f"Sample Headings: {', '.join(headings)}")
            
            # Check if meets B1 threshold
            quality_obj = ContentQuality(**result['quality'])
            if quality_obj.meets_b1_threshold():
                console.print("[bold green]🎉 CONTENT MEETS B1 QUALITY THRESHOLD![/bold green]")
            else:
                console.print("[yellow]⚠️ Content below B1 threshold, but test successful[/yellow]")
        else:
            console.print(f"[red]❌ Test failed: {result['error']}[/red]")
        
        # Display statistics
        stats = server.get_stats()
        console.print(f"\n[cyan]📊 Performance Statistics:[/cyan]")
        console.print(f"Runtime: {stats['runtime_seconds']:.1f}s")
        console.print(f"Requests: {stats['requests_made']}")
        console.print(f"Success Rate: {stats['success_rate']:.1%}")
        console.print(f"Memory: {stats['memory_usage_mb']:.1f}MB")

if __name__ == "__main__":
    asyncio.run(test_eds_refactored())
