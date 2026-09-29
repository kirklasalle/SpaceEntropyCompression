#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_eds\real_educational_data_scraper.py #api #command_line #python #source_code #training  
**Category:** Source Code  
**Status:** Active
"""









# !/usr/bin/env python3

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_eds\real_educational_data_scraper.py #api #command_line #python #source_code #training  
**Category:** Source Code  
**Status:** Active

"""
🎓 REAL EDUCATIONAL DATA SCRAPER - WORKING EDITION
HIGH SCHOOL MATHEMATICS FOCUS

This script creates REAL educational datasets for our training pipeline.
License-compliant sources with ethical scraping practices.
"""

import asyncio
import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import aiohttp
from bs4 import BeautifulSoup
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("educational-scraper")

class EducationalContentScraper:
    """Real educational content scraper - working edition"""
    
    def __init__(self):
        self.session = None
        self.scraped_content = []
        
    async def get_session(self):
        """Get HTTP session"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={
                    'User-Agent': 'ImpressionCore Educational Research Bot 1.0'
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session
    
    async def scrape_wikipedia_math(self, topic: str) -> Dict[str, Any]:
        """Scrape Wikipedia math content (CC-BY-SA licensed)"""
        logger.info(f"📚 Scraping Wikipedia math: {topic}")
        
        try:
            session = await self.get_session()
            url = f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
            
            # Ethical delay
            await asyncio.sleep(2)
            
            async with session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch {url}: {response.status}")
                    return {}
                    
                html = await response.text()
                
            # Parse content
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'div.navbox']):
                element.decompose()
            
            # Extract main content
            content_div = soup.find('div', {'id': 'mw-content-text'})
            if not content_div:
                logger.warning(f"No main content found for {topic}")
                return {}
            
            # Get title
            title_elem = soup.find('h1', {'id': 'firstHeading'})
            title = title_elem.get_text().strip() if title_elem else topic
            
            # Extract paragraphs
            paragraphs = []
            for p in content_div.find_all('p'):
                text = p.get_text().strip()
                if len(text) > 50:  # Only substantial paragraphs
                    paragraphs.append(text)
            
            # Create educational Q&A pairs
            qa_pairs = self._create_qa_pairs(title, paragraphs)
            
            content = {
                'source': 'Wikipedia',
                'url': url,
                'title': title,
                'topic': topic,
                'license': 'Creative Commons Attribution-ShareAlike 3.0',
                'paragraphs': paragraphs[:10],  # Limit to first 10 paragraphs
                'qa_pairs': qa_pairs,
                'scrape_time': datetime.now().isoformat(),
                'content_hash': hashlib.sha256(str(paragraphs).encode()).hexdigest()[:16]
            }
            
            logger.info(f"✅ Scraped {len(paragraphs)} paragraphs, created {len(qa_pairs)} Q&A pairs")
            return content
            
        except Exception as e:
            logger.error(f"Error scraping {topic}: {e}")
            return {}
    
    def _create_qa_pairs(self, title: str, paragraphs: List[str]) -> List[Dict[str, str]]:
        """Create educational Q&A pairs from content"""
        qa_pairs = []
        
        if not paragraphs:
            return qa_pairs
        
        # Basic Q&A patterns for educational content
        qa_patterns = [
            {
                'question': f"What is {title}?",
                'answer': paragraphs[0] if paragraphs else f"{title} is a mathematical concept."
            },
            {
                'question': f"Can you explain {title}?",
                'answer': paragraphs[0] if paragraphs else f"{title} is an important topic in mathematics."
            },
            {
                'question': f"How would you describe {title} to a high school student?",
                'answer': paragraphs[0] if paragraphs else f"{title} is a fundamental concept in mathematics."
            }
        ]
        
        # Add more Q&A pairs based on content
        for i, paragraph in enumerate(paragraphs[:3]):  # Use first 3 paragraphs
            if len(paragraph) > 100:  # Substantial content
                qa_pairs.append({
                    'question': f"Tell me more about {title}.",
                    'answer': paragraph
                })
        
        return qa_patterns + qa_pairs
    
    async def create_math_dataset(self, topics: List[str]) -> Dict[str, Any]:
        """Create comprehensive math dataset"""
        logger.info(f"🎓 Creating mathematics dataset with {len(topics)} topics")
        
        all_content = []
        all_qa_pairs = []
        
        for topic in topics:
            content = await self.scrape_wikipedia_math(topic)
            if content:
                all_content.append(content)
                all_qa_pairs.extend(content.get('qa_pairs', []))
        
        # Create dataset
        dataset = {
            'metadata': {
                'creation_date': datetime.now().isoformat(),
                'source': 'Wikipedia Mathematics',
                'license': 'Creative Commons Attribution-ShareAlike 3.0',
                'topics_count': len(topics),
                'articles_scraped': len(all_content),
                'qa_pairs_total': len(all_qa_pairs),
                'scraper_version': '1.0 Working Edition'
            },
            'content': all_content,
            'training_data': all_qa_pairs
        }
        
        logger.info(f"✅ Dataset created: {len(all_content)} articles, {len(all_qa_pairs)} Q&A pairs")
        return dataset
    
    async def close(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()

async def create_high_school_math_dataset():
    """Create a real high school mathematics dataset"""
    
    # High school math topics (license-compliant Wikipedia sources)
    math_topics = [
        "Linear algebra",
        "Quadratic equation",
        "Trigonometry",
        "Calculus",
        "Probability",
        "Statistics",
        "Algebra",
        "Geometry",
        "Polynomial",
        "Function (mathematics)"
    ]
    
    scraper = EducationalContentScraper()
    
    try:
        # Create dataset
        dataset = await scraper.create_math_dataset(math_topics)
        
        # Save to file
        output_file = Path("real_high_school_math_dataset.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        print(f"🎓 HIGH SCHOOL MATH DATASET CREATED!")
        print(f"📁 Saved to: {output_file}")
        print(f"📊 Contains {dataset['metadata']['articles_scraped']} articles")
        print(f"📝 Contains {dataset['metadata']['qa_pairs_total']} Q&A pairs")
        print(f"📜 License: {dataset['metadata']['license']}")
        
        return dataset
        
    finally:
        await scraper.close()

if __name__ == "__main__":
    # Create the dataset
    asyncio.run(create_high_school_math_dataset())
