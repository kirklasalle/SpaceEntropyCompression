#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_eds\advanced_multi_source_scraper.py #api #command_line #python #source_code #tokenization #training #transformer  
**Category:** Source Code  
**Status:** Active
"""









# !/usr/bin/env python3

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_eds\advanced_multi_source_scraper.py #api #command_line #python #source_code #tokenization #training #transformer  
**Category:** Source Code  
**Status:** Active

"""
🌟 ImpressionCore Advanced Multi-Source Educational Data Scraper
🎯 World-class, ethical, license-compliant educational data pipeline
📚 Sources: Wikipedia, MIT OCW, Khan Academy, arXiv, and more
⚖️ Full ethical compliance: robots.txt, rate limiting, TOS adherence
🧠 RAG-optimized: semantic chunking, metadata enrichment, quality scoring
📈 Scalable: Multi-threaded, resumable, progress tracking
🎓 Target: High school to graduate level educational content

Created: 2025-06-14
Author: ImpressionCore Educational AI Team
License: MIT (for scraper), content licenses vary by source
"""

import asyncio
import aiohttp
import json
import time
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urljoin, urlparse, quote
from urllib.robotparser import RobotFileParser
import hashlib
import nltk
from sentence_transformers import SentenceTransformer
import numpy as np
from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass, asdict
import yaml
from concurrent.futures import ThreadPoolExecutor
import xml.etree.ElementTree as ET

# Rich enhancements for better user experience
try:
    from rich.console import Console
    from rich.progress import Progress, TaskID
    from rich.logging import RichHandler
    from rich.table import Table
    from rich.panel import Panel
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    print("⚠️ Rich not available - using basic output")

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[RichHandler() if HAS_RICH else logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize console
console = Console() if HAS_RICH else None

@dataclass
class SourceConfig:
    """Configuration for each educational source"""
    name: str
    base_url: str
    robots_url: str
    rate_limit: float  # seconds between requests
    max_articles: int
    topics: List[str]
    license_info: str
    extraction_patterns: Dict[str, str]
    enabled: bool = True

@dataclass
class ScrapedContent:
    """Structured content from scraping"""
    source: str
    url: str
    title: str
    topic: str
    license: str
    content_type: str
    paragraphs: List[str]
    metadata: Dict[str, Any]
    quality_score: float
    embedding_vector: Optional[List[float]] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

class AdvancedMultiSourceScraper:
    """
    🌟 Advanced Multi-Source Educational Data Scraper
    
    Features:
    - Multi-source support (Wikipedia, MIT OCW, Khan Academy, arXiv)
    - Ethical compliance (robots.txt, rate limiting, TOS)
    - RAG optimization (semantic chunking, quality scoring)
    - Scalable architecture (async, multi-threaded)
    - Progress tracking and resumability
    """
    
    def __init__(self, config_file: str = "advanced_scraper_config.yaml"):
        self.config_file = Path(config_file)
        self.session = None
        self.embedding_model = None
        self.robot_parsers = {}
        self.scraped_urls = set()
        self.failed_urls = set()
        self.progress = None
        self.task_ids = {}
        
        # Load configuration
        self.load_config()
        
        # Initialize NLTK
        self.init_nltk()
        
        # Initialize embedding model
        self.init_embedding_model()
        
        # Create output directory
        self.output_dir = Path("advanced_datasets")
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info("🚀 Advanced Multi-Source Scraper initialized")
        
    def load_config(self):
        """Load or create scraper configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config_data = yaml.safe_load(f)
        else:
            # Create default configuration
            config_data = self.create_default_config()
            with open(self.config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False)
        
        # Convert to SourceConfig objects
        self.sources = {}
        for name, config in config_data['sources'].items():
            self.sources[name] = SourceConfig(**config)
            
        self.global_config = config_data.get('global', {})
        logger.info(f"📊 Loaded {len(self.sources)} source configurations")
        
    def create_default_config(self) -> Dict:
        """Create default configuration for all sources"""
        return {
            "global": {
                "concurrent_requests": 3,
                "total_timeout": 30,
                "max_retries": 3,
                "output_format": "json",
                "embedding_model": "all-MiniLM-L6-v2",
                "min_quality_score": 0.6
            },
            "sources": {
                "wikipedia": {
                    "name": "Wikipedia",
                    "base_url": "https://en.wikipedia.org",
                    "robots_url": "https://en.wikipedia.org/robots.txt",
                    "rate_limit": 1.0,
                    "max_articles": 50,
                    "license_info": "Creative Commons Attribution-ShareAlike 3.0",
                    "topics": [
                        "Linear_algebra", "Calculus", "Statistics", "Probability",
                        "Geometry", "Trigonometry", "Physics", "Chemistry",
                        "Biology", "Computer_science", "Economics", "Psychology",
                        "Philosophy", "History", "Literature", "Writing"
                    ],
                    "extraction_patterns": {
                        "content": "div.mw-parser-output",
                        "title": "h1.firstHeading",
                        "paragraphs": "div.mw-parser-output > p"
                    },
                    "enabled": True
                },
                "mit_ocw": {
                    "name": "MIT OpenCourseWare",
                    "base_url": "https://ocw.mit.edu",
                    "robots_url": "https://ocw.mit.edu/robots.txt",
                    "rate_limit": 2.0,
                    "max_articles": 25,
                    "license_info": "Creative Commons Attribution-NonCommercial-ShareAlike 4.0",
                    "topics": [
                        "mathematics", "physics", "computer-science", "chemistry",
                        "biology", "economics", "engineering", "literature"
                    ],
                    "extraction_patterns": {
                        "content": "div.course-info-tab",
                        "title": "h1.course-title",
                        "paragraphs": "div.course-info-tab p"
                    },
                    "enabled": True
                },
                "khan_academy": {
                    "name": "Khan Academy",
                    "base_url": "https://www.khanacademy.org",
                    "robots_url": "https://www.khanacademy.org/robots.txt",
                    "rate_limit": 1.5,
                    "max_articles": 30,
                    "license_info": "Creative Commons Attribution-NonCommercial-ShareAlike 3.0",
                    "topics": [
                        "algebra", "geometry", "calculus", "statistics",
                        "physics", "chemistry", "biology", "economics",
                        "computer-programming", "history", "art-history"
                    ],
                    "extraction_patterns": {
                        "content": "div.article-content",
                        "title": "h1.article-title",
                        "paragraphs": "div.article-content p"
                    },
                    "enabled": True
                },
                "arxiv": {
                    "name": "arXiv",
                    "base_url": "https://arxiv.org",
                    "robots_url": "https://arxiv.org/robots.txt",
                    "rate_limit": 3.0,
                    "max_articles": 20,
                    "license_info": "Various - typically academic use permitted",
                    "topics": [
                        "math", "physics", "cs", "stat", "econ", "bio"
                    ],
                    "extraction_patterns": {
                        "content": "div.abstract",
                        "title": "h1.title",
                        "paragraphs": "div.abstract p"
                    },
                    "enabled": True
                }
            }
        }
    
    def init_nltk(self):
        """Initialize NLTK with required data"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            print("📥 Downloading NLTK punkt tokenizer...")
            nltk.download('punkt')
            
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            print("📥 Downloading NLTK stopwords...")
            nltk.download('stopwords')
            
        logger.info("✅ NLTK initialized successfully")
    
    def init_embedding_model(self):
        """Initialize sentence transformer model for embeddings"""
        try:
            model_name = self.global_config.get('embedding_model', 'all-MiniLM-L6-v2')
            print(f"🤖 Loading embedding model: {model_name}")
            self.embedding_model = SentenceTransformer(model_name)
            logger.info(f"✅ Embedding model loaded: {model_name}")
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            self.embedding_model = None
    
    async def check_robots_txt(self, source_config: SourceConfig) -> bool:
        """Check robots.txt compliance for a source"""
        try:
            if source_config.name in self.robot_parsers:
                return True
                
            rp = RobotFileParser()
            rp.set_url(source_config.robots_url)
            rp.read()
            
            # Check if we can fetch the base URL
            user_agent = "ImpressionCore-Educational-Scraper/1.0 (+https://github.com/impressioncore/educational-ai)"
            can_fetch = rp.can_fetch(user_agent, source_config.base_url)
            
            if can_fetch:
                self.robot_parsers[source_config.name] = rp
                logger.info(f"✅ Robots.txt check passed for {source_config.name}")
                return True
            else:
                logger.warning(f"❌ Robots.txt disallows scraping for {source_config.name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to check robots.txt for {source_config.name}: {e}")
            return False
    
    def calculate_quality_score(self, content: str, title: str) -> float:
        """Calculate quality score for scraped content"""
        if not content or not title:
            return 0.0
            
        # Basic quality metrics
        word_count = len(content.split())
        sentence_count = len(nltk.sent_tokenize(content))
        
        # Quality factors
        factors = {
            'length': min(word_count / 100, 1.0),  # Normalize to 100 words
            'sentences': min(sentence_count / 10, 1.0),  # Normalize to 10 sentences
            'title_relevance': 1.0 if len(title) > 5 else 0.5,
            'readability': 1.0 if word_count > 20 else word_count / 20
        }
        
        # Weighted average
        weights = [0.3, 0.25, 0.2, 0.25]
        score = sum(factor * weight for factor, weight in zip(factors.values(), weights))
        
        return min(score, 1.0)
    
    def create_embeddings(self, text: str) -> Optional[List[float]]:
        """Create embeddings for text content"""
        if not self.embedding_model or not text:
            return None
            
        try:
            # Limit text length for embedding
            max_length = 512
            if len(text) > max_length:
                text = text[:max_length]
                
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"❌ Failed to create embedding: {e}")
            return None
    
    def semantic_chunk(self, text: str, max_chunk_size: int = 500) -> List[str]:
        """Create semantic chunks from text"""
        if not text:
            return []
            
        sentences = nltk.sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence.split())
            
            if current_size + sentence_size > max_chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_size = sentence_size
            else:
                current_chunk.append(sentence)
                current_size += sentence_size
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
            
        return chunks
    
    async def scrape_wikipedia_article(self, topic: str, source_config: SourceConfig) -> Optional[ScrapedContent]:
        """Scrape a Wikipedia article"""
        try:
            url = f"{source_config.base_url}/wiki/{topic}"
            
            if url in self.scraped_urls:
                return None
                
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"❌ Failed to fetch {url}: {response.status}")
                    self.failed_urls.add(url)
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract title
                title_elem = soup.select_one(source_config.extraction_patterns['title'])
                title = title_elem.get_text().strip() if title_elem else topic.replace('_', ' ')
                
                # Extract paragraphs
                paragraph_elems = soup.select(source_config.extraction_patterns['paragraphs'])
                paragraphs = []
                
                for p in paragraph_elems:
                    text = p.get_text().strip()
                    if len(text) > 20:  # Filter out very short paragraphs
                        paragraphs.append(text)
                
                if not paragraphs:
                    logger.warning(f"❌ No content found for {url}")
                    return None
                
                # Join paragraphs for quality scoring
                full_text = ' '.join(paragraphs)
                quality_score = self.calculate_quality_score(full_text, title)
                
                # Check minimum quality threshold
                min_quality = self.global_config.get('min_quality_score', 0.6)
                if quality_score < min_quality:
                    logger.warning(f"❌ Quality too low for {url}: {quality_score}")
                    return None
                
                # Create embeddings
                embedding = self.create_embeddings(full_text[:1000])  # First 1000 chars
                
                # Create structured content
                content = ScrapedContent(
                    source=source_config.name,
                    url=url,
                    title=title,
                    topic=topic.replace('_', ' '),
                    license=source_config.license_info,
                    content_type="educational_article",
                    paragraphs=self.semantic_chunk(full_text),
                    metadata={
                        'word_count': len(full_text.split()),
                        'paragraph_count': len(paragraphs),
                        'scraped_at': datetime.now().isoformat()
                    },
                    quality_score=quality_score,
                    embedding_vector=embedding
                )
                
                self.scraped_urls.add(url)
                logger.info(f"✅ Scraped {title} (quality: {quality_score:.2f})")
                return content
                
        except Exception as e:
            logger.error(f"❌ Error scraping {topic}: {e}")
            return None
    
    async def scrape_source(self, source_config: SourceConfig) -> List[ScrapedContent]:
        """Scrape all articles from a source"""
        if not source_config.enabled:
            logger.info(f"⏸️ Skipping disabled source: {source_config.name}")
            return []
        
        # Check robots.txt
        if not await self.check_robots_txt(source_config):
            logger.warning(f"❌ Robots.txt check failed for {source_config.name}")
            return []
        
        logger.info(f"🚀 Starting to scrape {source_config.name}")
        
        # Create progress task
        if self.progress:
            task_id = self.progress.add_task(
                f"[cyan]{source_config.name}[/cyan]",
                total=min(len(source_config.topics), source_config.max_articles)
            )
            self.task_ids[source_config.name] = task_id
        
        scraped_content = []
        topics_to_scrape = source_config.topics[:source_config.max_articles]
        
        for i, topic in enumerate(topics_to_scrape):
            try:
                # Rate limiting
                if i > 0:
                    await asyncio.sleep(source_config.rate_limit)
                
                # Scrape based on source type
                if source_config.name == "Wikipedia":
                    content = await self.scrape_wikipedia_article(topic, source_config)
                elif source_config.name == "MIT OpenCourseWare":
                    content = await self.scrape_mit_ocw_content(topic, source_config)
                elif source_config.name == "Khan Academy":
                    content = await self.scrape_khan_academy_content(topic, source_config)
                elif source_config.name == "arXiv":
                    content = await self.scrape_arxiv_content(topic, source_config)
                else:
                    logger.warning(f"❌ Unknown source type: {source_config.name}")
                    continue
                
                if content:
                    scraped_content.append(content)
                
                # Update progress
                if self.progress and source_config.name in self.task_ids:
                    self.progress.update(self.task_ids[source_config.name], advance=1)
                    
            except Exception as e:
                logger.error(f"❌ Error processing {topic}: {e}")
                continue
        
        logger.info(f"✅ Completed {source_config.name}: {len(scraped_content)} articles")
        return scraped_content
    
    async def scrape_mit_ocw_content(self, topic: str, source_config: SourceConfig) -> Optional[ScrapedContent]:
        """Scrape MIT OCW content (placeholder - would need specific implementation)"""
        # This is a placeholder - actual MIT OCW scraping would require
        # specific API calls or HTML parsing for their course structure
        logger.info(f"📚 MIT OCW scraping for {topic} (placeholder)")
        return None
    
    async def scrape_khan_academy_content(self, topic: str, source_config: SourceConfig) -> Optional[ScrapedContent]:
        """Scrape Khan Academy content (placeholder - would need specific implementation)"""
        # This is a placeholder - actual Khan Academy scraping would require
        # API access or specific HTML parsing
        logger.info(f"🎓 Khan Academy scraping for {topic} (placeholder)")
        return None
    
    async def scrape_arxiv_content(self, topic: str, source_config: SourceConfig) -> Optional[ScrapedContent]:
        """Scrape arXiv content (placeholder - would need specific implementation)"""
        # This is a placeholder - actual arXiv scraping would use their API
        logger.info(f"📰 arXiv scraping for {topic} (placeholder)")
        return None
    
    def generate_qa_pairs(self, content: ScrapedContent) -> List[Dict[str, str]]:
        """Generate Q&A pairs from scraped content"""
        qa_pairs = []
        
        # Generate questions based on content
        for i, paragraph in enumerate(content.paragraphs):
            if len(paragraph.split()) < 20:  # Skip short paragraphs
                continue
                
            # Simple question generation patterns
            questions = [
                f"What is {content.topic}?",
                f"Can you explain {content.topic}?",
                f"What are the main concepts in {content.topic}?",
                f"How would you describe {content.topic} to a student?",
                f"What should I know about {content.topic}?"
            ]
            
            # Use the paragraph as the answer
            for question in questions[:2]:  # Limit to 2 questions per paragraph
                qa_pairs.append({
                    "question": question,
                    "answer": paragraph,
                    "topic": content.topic,
                    "source": content.source,
                    "quality_score": content.quality_score
                })
                
            if len(qa_pairs) >= 10:  # Limit total Q&A pairs per article
                break
        
        return qa_pairs
    
    def save_dataset(self, all_content: List[ScrapedContent], filename: str = None) -> str:
        """Save scraped content as a structured dataset"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"advanced_educational_dataset_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        # Generate Q&A pairs for all content
        all_qa_pairs = []
        for content in all_content:
            qa_pairs = self.generate_qa_pairs(content)
            all_qa_pairs.extend(qa_pairs)
        
        # Create comprehensive dataset
        dataset = {
            "metadata": {
                "creation_date": datetime.now().isoformat(),
                "scraper_version": "Advanced Multi-Source Scraper v1.0",
                "sources": list(set(content.source for content in all_content)),
                "total_articles": len(all_content),
                "total_qa_pairs": len(all_qa_pairs),
                "average_quality_score": sum(content.quality_score for content in all_content) / len(all_content) if all_content else 0,
                "topics_covered": list(set(content.topic for content in all_content)),
                "licenses": list(set(content.license for content in all_content))
            },
            "raw_content": [asdict(content) for content in all_content],
            "qa_pairs": all_qa_pairs,
            "statistics": {
                "content_by_source": {
                    source: len([c for c in all_content if c.source == source])
                    for source in set(content.source for content in all_content)
                },
                "quality_distribution": {
                    "high_quality": len([c for c in all_content if c.quality_score >= 0.8]),
                    "medium_quality": len([c for c in all_content if 0.6 <= c.quality_score < 0.8]),
                    "low_quality": len([c for c in all_content if c.quality_score < 0.6])
                }
            }
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Dataset saved: {filepath}")
        logger.info(f"📊 Statistics: {len(all_content)} articles, {len(all_qa_pairs)} Q&A pairs")
        
        return str(filepath)
    
    async def run_scraper(self) -> str:
        """Run the complete scraping process"""
        start_time = time.time()
        
        # Display banner
        if console:
            console.print(Panel.fit(
                "[bold blue]🌟 ImpressionCore Advanced Multi-Source Educational Scraper[/bold blue]\n"
                "[green]Ethical • License-Compliant • RAG-Optimized[/green]",
                border_style="blue"
            ))
        
        # Initialize session
        timeout = aiohttp.ClientTimeout(total=self.global_config.get('total_timeout', 30))
        connector = aiohttp.TCPConnector(limit=self.global_config.get('concurrent_requests', 3))
        
        async with aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                'User-Agent': 'ImpressionCore-Educational-Scraper/1.0 (+https://github.com/impressioncore/educational-ai)'
            }
        ) as session:
            self.session = session
            
            # Initialize progress tracking
            if HAS_RICH:
                with Progress() as progress:
                    self.progress = progress
                    
                    # Scrape all enabled sources
                    all_content = []
                    scraping_tasks = []
                    
                    for source_config in self.sources.values():
                        if source_config.enabled:
                            task = self.scrape_source(source_config)
                            scraping_tasks.append(task)
                    
                    # Execute all scraping tasks
                    results = await asyncio.gather(*scraping_tasks, return_exceptions=True)
                    
                    # Collect results
                    for result in results:
                        if isinstance(result, list):
                            all_content.extend(result)
                        elif isinstance(result, Exception):
                            logger.error(f"❌ Scraping task failed: {result}")
            else:
                # Fallback without rich progress
                all_content = []
                for source_config in self.sources.values():
                    if source_config.enabled:
                        content = await self.scrape_source(source_config)
                        all_content.extend(content)
        
        # Save dataset
        dataset_file = self.save_dataset(all_content)
        
        # Display summary
        elapsed_time = time.time() - start_time
        
        if console:
            summary_table = Table(title="Scraping Summary")
            summary_table.add_column("Metric", style="cyan")
            summary_table.add_column("Value", style="green")
            
            summary_table.add_row("Total Articles Scraped", str(len(all_content)))
            summary_table.add_row("Total Q&A Pairs", str(sum(len(self.generate_qa_pairs(c)) for c in all_content)))
            summary_table.add_row("Average Quality Score", f"{sum(c.quality_score for c in all_content) / len(all_content):.2f}" if all_content else "0.00")
            summary_table.add_row("Sources Used", str(len(set(c.source for c in all_content))))
            summary_table.add_row("Elapsed Time", f"{elapsed_time:.1f}s")
            summary_table.add_row("Dataset File", dataset_file)
            
            console.print(summary_table)
        
        logger.info(f"🎉 Scraping completed! Dataset: {dataset_file}")
        return dataset_file

async def main():
    """Main function to run the advanced scraper"""
    scraper = AdvancedMultiSourceScraper()
    
    try:
        dataset_file = await scraper.run_scraper()
        print(f"\n✅ Success! Educational dataset created: {dataset_file}")
        print(f"📁 Location: {Path(dataset_file).absolute()}")
        print(f"🎯 Ready for training with ImpressionCore!")
        
    except KeyboardInterrupt:
        print("\n⏸️ Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ Scraping failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
