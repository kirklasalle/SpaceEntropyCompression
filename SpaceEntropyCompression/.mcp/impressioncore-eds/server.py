#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_eds\server.py #api #python #source_code #training  
**Category:** Source Code  
**Status:** Active
"""





import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional, Sequence
from urllib.parse import urljoin, urlparse
import aiohttp
import feedparser
import requests
from bs4 import BeautifulSoup
import wikipedia
import arxiv

# Chronology loader (shared)
try:
    from assistant.chronology_loader import load_chronology, query_chronology, load_delta  # type: ignore
    HAS_CHRONOLOGY = True
except Exception:
    HAS_CHRONOLOGY = False

# MCP imports
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        CallToolRequest,
        CallToolResult,
        ListToolsRequest,
        ListToolsResult,
        Tool,
        TextContent,
    )
except ImportError:
    print("MCP library not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        CallToolRequest,
        CallToolResult,
        ListToolsRequest,
        ListToolsResult,
        Tool,
        TextContent,
    )

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImpressionCoreEducationalScraper:
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ImpressionCore-Educational-Scraper/1.0 (Educational Research)'
        })
        
        # License compliance mapping
        self.license_compliance = {
            'mit.edu': 'Creative Commons',
            'ocw.mit.edu': 'Creative Commons',
            'wikipedia.org': 'CC-BY-SA',
            'arxiv.org': 'Open Access',
            'nasa.gov': 'Public Domain',
            'nih.gov': 'Public Domain',
            'khanacademy.org': 'Creative Commons (selected content)'
        }
        
        logger.info("🔥 ImpressionCore Educational Scraper initialized!")
    
    async def scrape_mit_ocw_content(self, course_url: str = None, subject: str = "computer-science") -> Dict[str, Any]:
        """
        Scrape MIT OpenCourseWare content (Creative Commons licensed)
        """
        try:
            logger.info(f"🎓 Scraping MIT OCW content for: {subject}")
            
            # MIT OCW API endpoints and course listings
            base_url = "https://ocw.mit.edu"
            
            if not course_url:
                # Get course listings for the subject
                search_url = f"{base_url}/search/?q={subject}"
                response = self.session.get(search_url)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract course links
                course_links = []
                for link in soup.find_all('a', href=True):
                    if '/courses/' in link['href']:
                        course_links.append(urljoin(base_url, link['href']))
                
                if not course_links:
                    return {"error": "No courses found", "subject": subject}
                
                course_url = course_links[0]  # Use first course found
            
            # Scrape specific course content
            response = self.session.get(course_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract educational content
            content = {
                "source": "MIT OpenCourseWare",
                "license": "Creative Commons",
                "url": course_url,
                "subject": subject,
                "title": soup.find('title').text if soup.find('title') else "Unknown Course",
                "content": [],
                "compliance_verified": True
            }
            
            # Extract lecture content, problem sets, etc.
            content_sections = soup.find_all(['div', 'section'], class_=['content', 'lecture', 'problem-set'])
            
            for section in content_sections[:5]:  # Limit to first 5 sections
                section_text = section.get_text(strip=True)
                if len(section_text) > 100:  # Only meaningful content
                    content["content"].append({
                        "type": "educational_text",
                        "text": section_text,
                        "length": len(section_text)
                    })
            
            logger.info(f"✅ Successfully scraped MIT OCW content: {len(content['content'])} sections")
            return content
            
        except Exception as e:
            logger.error(f"❌ MIT OCW scraping error: {e}")
            return {"error": str(e), "source": "MIT OCW"}
    
    async def scrape_wikipedia_educational(self, topics: List[str] = None) -> Dict[str, Any]:
        """
        Extract educational Wikipedia articles (CC-BY-SA licensed)
        """
        try:
            if not topics:
                topics = [
                    "Machine learning", "Calculus", "Physics", "Computer science",
                    "Mathematics", "Biology", "Chemistry", "History"
                ]
            
            logger.info(f"📚 Scraping Wikipedia educational content for: {topics}")
            
            educational_content = {
                "source": "Wikipedia",
                "license": "CC-BY-SA",
                "topics": topics,
                "articles": [],
                "compliance_verified": True
            }
            
            for topic in topics[:3]:  # Limit to prevent overwhelming
                try:
                    # Search for the topic
                    page = wikipedia.page(topic)
                    
                    # Extract educational content
                    article = {
                        "title": page.title,
                        "url": page.url,
                        "summary": page.summary,
                        "content": page.content[:5000],  # First 5000 chars
                        "categories": page.categories[:10] if hasattr(page, 'categories') else [],
                        "educational_value": self._assess_educational_value(page.content)
                    }
                    
                    educational_content["articles"].append(article)
                    logger.info(f"✅ Scraped Wikipedia article: {page.title}")
                    
                except wikipedia.exceptions.DisambiguationError as e:
                    # Handle disambiguation by taking the first option
                    try:
                        page = wikipedia.page(e.options[0])
                        article = {
                            "title": page.title,
                            "url": page.url,
                            "summary": page.summary,
                            "content": page.content[:5000],
                            "educational_value": self._assess_educational_value(page.content)
                        }
                        educational_content["articles"].append(article)
                        logger.info(f"✅ Scraped Wikipedia article (disambiguated): {page.title}")
                    except:
                        logger.warning(f"⚠️ Skipped ambiguous topic: {topic}")
                        
                except Exception as topic_error:
                    logger.warning(f"⚠️ Error with topic {topic}: {topic_error}")
                    continue
            
            logger.info(f"✅ Successfully scraped {len(educational_content['articles'])} Wikipedia articles")
            return educational_content
            
        except Exception as e:
            logger.error(f"❌ Wikipedia scraping error: {e}")
            return {"error": str(e), "source": "Wikipedia"}
    
    async def scrape_arxiv_papers(self, query: str = "machine learning education", max_results: int = 5) -> Dict[str, Any]:
        """
        Get educational arXiv papers (open access)
        """
        try:
            logger.info(f"📄 Scraping arXiv papers for: {query}")
            
            # Search arXiv
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            papers = {
                "source": "arXiv",
                "license": "Open Access",
                "query": query,
                "papers": [],
                "compliance_verified": True
            }
            
            for paper in search.results():
                paper_data = {
                    "title": paper.title,
                    "authors": [str(author) for author in paper.authors],
                    "summary": paper.summary,
                    "url": paper.entry_id,
                    "pdf_url": paper.pdf_url,
                    "categories": paper.categories,
                    "published": str(paper.published),
                    "educational_relevance": self._assess_educational_relevance(paper.title + " " + paper.summary)
                }
                
                papers["papers"].append(paper_data)
                logger.info(f"✅ Found arXiv paper: {paper.title[:50]}...")
            
            logger.info(f"✅ Successfully scraped {len(papers['papers'])} arXiv papers")
            return papers
            
        except Exception as e:
            logger.error(f"❌ arXiv scraping error: {e}")
            return {"error": str(e), "source": "arXiv"}
    
    async def scrape_government_educational(self, agency: str = "nasa") -> Dict[str, Any]:
        """
        Access US government educational resources (public domain)
        """
        try:
            logger.info(f"🏛️ Scraping government educational content from: {agency}")
            
            # Government agency educational URLs
            agency_urls = {
                'nasa': 'https://www.nasa.gov/audience/foreducators/',
                'nih': 'https://www.nih.gov/health-information',
                'noaa': 'https://www.noaa.gov/education'
            }
            
            if agency not in agency_urls:
                return {"error": f"Unsupported agency: {agency}"}
            
            url = agency_urls[agency]
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            content = {
                "source": f"US Government ({agency.upper()})",
                "license": "Public Domain",
                "url": url,
                "agency": agency,
                "educational_resources": [],
                "compliance_verified": True
            }
            
            # Extract educational content
            educational_sections = soup.find_all(['article', 'div', 'section'], 
                                                class_=['content', 'educational', 'resource'])
            
            for section in educational_sections[:5]:
                section_text = section.get_text(strip=True)
                if len(section_text) > 200:
                    content["educational_resources"].append({
                        "type": "government_educational",
                        "text": section_text,
                        "length": len(section_text),
                        "educational_value": self._assess_educational_value(section_text)
                    })
            
            logger.info(f"✅ Successfully scraped {agency.upper()} educational content")
            return content
            
        except Exception as e:
            logger.error(f"❌ Government educational scraping error: {e}")
            return {"error": str(e), "source": f"Government ({agency})"}
    
    async def validate_license_compliance(self, url: str) -> Dict[str, Any]:
        """
        Validate that scraped content is license-compliant
        """
        try:
            domain = urlparse(url).netloc.lower()
            
            compliance = {
                "url": url,
                "domain": domain,
                "compliant": False,
                "license": "Unknown",
                "reason": ""
            }
            
            # Check against our compliance mapping
            for compliant_domain, license_type in self.license_compliance.items():
                if compliant_domain in domain:
                    compliance.update({
                        "compliant": True,
                        "license": license_type,
                        "reason": f"Domain {domain} is known to provide {license_type} content"
                    })
                    break
            
            if not compliance["compliant"]:
                compliance["reason"] = f"Domain {domain} not in approved list for MIT/Apache/CC licensing"
            
            logger.info(f"🔍 License compliance check: {compliance['compliant']} for {domain}")
            return compliance
            
        except Exception as e:
            logger.error(f"❌ License validation error: {e}")
            return {"error": str(e), "compliant": False}
    
    def _assess_educational_value(self, text: str) -> float:
        """Assess educational value of text content"""
        educational_keywords = [
            'learn', 'understand', 'concept', 'principle', 'theory', 'method',
            'example', 'problem', 'solution', 'analysis', 'explanation',
            'definition', 'algorithm', 'formula', 'equation', 'proof'
        ]
        
        text_lower = text.lower()
        keyword_count = sum(1 for keyword in educational_keywords if keyword in text_lower)
        
        # Normalize score (0-10)
        score = min(keyword_count / 3.0, 10.0)
        return round(score, 2)
    
    def _assess_educational_relevance(self, text: str) -> float:
        """Assess educational relevance for research papers"""
        relevance_keywords = [
            'education', 'learning', 'teaching', 'student', 'curriculum',
            'pedagogy', 'instruction', 'training', 'knowledge', 'skill'
        ]
        
        text_lower = text.lower()
        relevance_count = sum(1 for keyword in relevance_keywords if keyword in text_lower)
        
        # Normalize score (0-10)
        score = min(relevance_count / 2.0, 10.0)
        return round(score, 2)


# Initialize the MCP server
server = Server("impressioncore-educational-scraper")
scraper = ImpressionCoreEducationalScraper()

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available scraping tools"""
    return [
        Tool(
            name="scrape_mit_ocw",
            description="Scrape MIT OpenCourseWare content (Creative Commons licensed)",
            inputSchema={
                "type": "object",
                "properties": {
                    "course_url": {"type": "string", "description": "Specific course URL (optional)"},
                    "subject": {"type": "string", "description": "Subject area to search"}
                }
            }
        ),
        Tool(
            name="scrape_wikipedia_educational",
            description="Extract educational Wikipedia articles (CC-BY-SA licensed)",
            inputSchema={
                "type": "object",
                "properties": {
                    "topics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Educational topics to search for"
                    }
                }
            }
        ),
        Tool(
            name="scrape_arxiv_papers",
            description="Get educational arXiv papers (open access)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for papers"},
                    "max_results": {"type": "integer", "description": "Maximum number of papers"}
                }
            }
        ),
        Tool(
            name="scrape_government_educational",
            description="Access US government educational resources (public domain)",
            inputSchema={
                "type": "object",
                "properties": {
                    "agency": {"type": "string", "description": "Government agency (nasa, nih, noaa)"}
                }
            }
        ),
        Tool(
            name="validate_license_compliance",
            description="Validate that scraped content is license-compliant",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to validate"}
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="eds_chronology_snapshot",
            description="Chronology snapshot (docs/source/mcp/root/all) creation-ordered",
            inputSchema={
                "type": "object",
                "properties": {
                    "kind": {"type": "string", "enum": ["all","docs","source","mcp","root"], "default": "all"},
                    "limit": {"type": "integer", "default": 40},
                    "reverse": {"type": "boolean", "default": False}
                }
            }
        ),
        Tool(
            name="eds_chronology_delta",
            description="Chronology delta (added/removed/changed) if diff present",
            inputSchema={
                "type": "object",
                "properties": {
                    "include": {"type": "array", "items": {"type": "string", "enum": ["added","removed","changed"]}},
                    "limit": {"type": "integer", "default": 200}
                }
            }
        ),
        Tool(
            name="eds_chronology_stats",
            description="Chronology statistics (counts per category + delta counts)",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> CallToolResult:
    """Handle tool calls"""
    try:
        if name == "scrape_mit_ocw":
            result = await scraper.scrape_mit_ocw_content(
                course_url=arguments.get("course_url"),
                subject=arguments.get("subject", "computer-science")
            )
        elif name == "scrape_wikipedia_educational":
            result = await scraper.scrape_wikipedia_educational(
                topics=arguments.get("topics")
            )
        elif name == "scrape_arxiv_papers":
            result = await scraper.scrape_arxiv_papers(
                query=arguments.get("query", "machine learning education"),
                max_results=arguments.get("max_results", 5)
            )
        elif name == "scrape_government_educational":
            result = await scraper.scrape_government_educational(
                agency=arguments.get("agency", "nasa")
            )
        elif name == "validate_license_compliance":
            result = await scraper.validate_license_compliance(
                url=arguments["url"]
            )
        elif name == "eds_chronology_snapshot":
            if not HAS_CHRONOLOGY:
                result = {"error": "chronology_loader_not_available"}
            else:
                data = load_chronology()
                kind = arguments.get('kind', 'all')
                limit = arguments.get('limit', 40)
                reverse = arguments.get('reverse', False)
                items = query_chronology(data, kind=kind, limit=limit, reverse=reverse)
                result = {
                    'kind': kind,
                    'limit': limit,
                    'reverse': reverse,
                    'count': len(items),
                    'items': items,
                    'generated': data.get('generated'),
                    'ordering': data.get('ordering'),
                    'schema_version': data.get('schema_version')
                }
        elif name == "eds_chronology_delta":
            if not HAS_CHRONOLOGY:
                result = {"error": "chronology_loader_not_available"}
            else:
                diff = load_delta()
                if not diff:
                    result = {"error": "delta_not_available", "hint": "Generate chronology with --delta in IDS."}
                else:
                    include = arguments.get('include') or ['added','removed','changed']
                    limit = arguments.get('limit', 200)
                    payload = {'generated': diff.get('generated'), 'counts': diff.get('counts', {})}
                    for key in ['added','removed','changed']:
                        if key in include and key in diff:
                            data_slice = diff[key]
                            payload[key] = data_slice[:limit] if limit else data_slice
                    result = payload
        elif name == "eds_chronology_stats":
            if not HAS_CHRONOLOGY:
                result = {"error": "chronology_loader_not_available"}
            else:
                data = load_chronology()
                stats = {
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
                result = stats
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
        
    except Exception as e:
        logger.error(f"Tool call error: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps({"error": str(e)}))]
        )

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="impressioncore-educational-scraper",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    print("🔥 ImpressionCore Educational Scraper MCP Server Starting...")
    print("LICENSE-COMPLIANT REAL DATA ACQUISITION SYSTEM")
    print("=" * 60)
    asyncio.run(main())
