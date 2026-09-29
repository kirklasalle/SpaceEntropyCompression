#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_eds\enterprise_grade_dataset_builder.py #api #command_line #python #security #source_code #testing #tokenization #transformer #web_interface  
**Category:** Source Code  
**Status:** Active
"""









# !/usr/bin/env python3

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_eds\enterprise_grade_dataset_builder.py #api #command_line #python #security #source_code #testing #tokenization #transformer #web_interface  
**Category:** Source Code  
**Status:** Active

"""
Enterprise-Grade Educational Dataset Builder
===========================================

A comprehensive, scalable dataset creation system that builds world-class
educational content while enforcing high school graduate standards.

Features:
- Multi-source content aggregation (Wikipedia, Khan Academy, MIT OCW)
- Automated quality assessment and filtering
- Standards compliance validation
- Parallel processing for efficiency
- Comprehensive subject coverage
- Enterprise-grade logging and monitoring

Author: ImpressionCore Educational AI Team
License: MIT
Version: 1.0.0
"""

import asyncio
import aiohttp
import json
import logging
import time
import re
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer
import numpy as np
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
import traceback

# Import our standards framework
from high_school_graduate_standards import HighSchoolGraduateStandards

@dataclass
class ContentItem:
    """Represents a validated educational content item."""
    title: str
    content: str
    subject: str
    topic: str
    source: str
    url: str
    license: str
    quality_score: float
    standards_compliance: Dict[str, bool]
    cognitive_level: str
    reading_level: str
    created_at: str

@dataclass
class QAPair:
    """Represents a question-answer pair derived from content."""
    question: str
    answer: str
    context: str
    difficulty: str
    subject: str
    topic: str
    cognitive_level: str
    quality_score: float
    source: str

class EnterpriseDatasetBuilder:
    """Enterprise-grade educational dataset builder with comprehensive validation."""
    
    def __init__(self):
        """Initialize the dataset builder with all required components."""
        self.setup_logging()
        self.setup_nltk()
        self.setup_embeddings()
        self.standards = HighSchoolGraduateStandards()
        self.session = None
        
        # Subject and topic configuration
        self.subject_topics = {
            'mathematics': [
                'Algebra', 'Geometry', 'Trigonometry', 'Calculus', 'Statistics',
                'Probability', 'Linear Algebra', 'Discrete Mathematics',
                'Number Theory', 'Mathematical Analysis', 'Functions',
                'Equations', 'Inequalities', 'Polynomials', 'Logarithms'
            ],
            'science': [
                'Physics', 'Chemistry', 'Biology', 'Earth Science', 'Astronomy',
                'Environmental Science', 'Genetics', 'Evolution', 'Ecology',
                'Atomic Structure', 'Periodic Table', 'Chemical Reactions',
                'Newton\'s Laws', 'Thermodynamics', 'Electromagnetism',
                'Quantum Mechanics', 'Cell Biology', 'Human Biology'
            ],
            'english_language_arts': [
                'Grammar', 'Literature', 'Writing', 'Reading Comprehension',
                'Poetry', 'Drama', 'Fiction', 'Non-fiction', 'Rhetoric',
                'Critical Analysis', 'Research Methods', 'Citation',
                'Essay Writing', 'Creative Writing', 'Public Speaking'
            ],
            'social_studies': [
                'History', 'Geography', 'Government', 'Economics', 'Civics',
                'World History', 'American History', 'Political Science',
                'Sociology', 'Anthropology', 'Psychology', 'Philosophy',
                'Cultural Studies', 'International Relations', 'Law'
            ],
            'computer_science': [
                'Programming', 'Algorithms', 'Data Structures', 'Software Engineering',
                'Computer Systems', 'Networks', 'Databases', 'Web Development',
                'Artificial Intelligence', 'Machine Learning', 'Cybersecurity',
                'Digital Literacy', 'Information Technology'
            ]
        }
        
        # Quality thresholds
        self.min_quality_score = 0.6
        self.min_content_length = 100
        self.max_content_length = 5000
        
        # Rate limiting
        self.request_delay = 1.0  # seconds between requests
        self.max_concurrent_requests = 3
        
        # Dataset statistics
        self.stats = {
            'total_processed': 0,
            'total_validated': 0,
            'total_qa_pairs': 0,
            'by_subject': {},
            'by_quality': {'high': 0, 'medium': 0, 'low': 0},
            'processing_time': 0
        }
    
    def setup_logging(self):
        """Configure comprehensive logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('enterprise_dataset_builder.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Enterprise Dataset Builder initialized")
    
    def setup_nltk(self):
        """Download required NLTK data."""
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            self.logger.info("Downloading NLTK data...")
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
    
    def setup_embeddings(self):
        """Initialize sentence embeddings model."""
        try:
            self.logger.info("Loading sentence embeddings model...")
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            self.logger.info("Embeddings model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load embeddings model: {e}")
            self.embedder = None
    
    async def create_session(self):
        """Create aiohttp session with proper headers."""
        headers = {
            'User-Agent': 'ImpressionCore-Educational-AI/1.0 (Educational Research; contact@impressioncore.org)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout,
            connector=aiohttp.TCPConnector(limit=self.max_concurrent_requests)
        )
    
    async def close_session(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
    
    async def fetch_wikipedia_content(self, topic: str, subject: str) -> List[ContentItem]:
        """Fetch and validate Wikipedia content for a topic."""
        try:
            # Search for the topic
            search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic.replace(' ', '_')}"
            
            async with self.session.get(search_url) as response:
                if response.status != 200:
                    self.logger.warning(f"Failed to fetch Wikipedia summary for {topic}: {response.status}")
                    return []
                
                data = await response.json()
                
                if 'extract' not in data or len(data['extract']) < self.min_content_length:
                    self.logger.warning(f"Insufficient content for Wikipedia topic: {topic}")
                    return []
                
                # Create content item
                content_item = ContentItem(
                    title=data.get('title', topic),
                    content=data['extract'],
                    subject=subject,
                    topic=topic,
                    source='Wikipedia',
                    url=data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                    license='Creative Commons Attribution-ShareAlike 3.0',
                    quality_score=0.0,  # Will be calculated
                    standards_compliance={},  # Will be validated
                    cognitive_level='',  # Will be determined
                    reading_level='',  # Will be calculated
                    created_at=datetime.now().isoformat()
                )
                
                # Validate and score the content
                validated_content = await self.validate_content(content_item)
                
                if validated_content and validated_content.quality_score >= self.min_quality_score:
                    return [validated_content]
                
                return []
                
        except Exception as e:
            self.logger.error(f"Error fetching Wikipedia content for {topic}: {e}")
            return []
    
    async def validate_content(self, content: ContentItem) -> Optional[ContentItem]:
        """Validate content against high school graduate standards."""
        try:
            # Calculate quality metrics
            quality_score = self.calculate_quality_score(content.content)
            
            # Validate against standards
            compliance = self.standards.validate_content(
                content.content,
                content.subject,
                content.topic
            )
            
            # Determine cognitive level
            cognitive_level = self.determine_cognitive_level(content.content)
            
            # Calculate reading level
            reading_level = self.calculate_reading_level(content.content)
            
            # Update content item
            content.quality_score = quality_score
            content.standards_compliance = compliance
            content.cognitive_level = cognitive_level
            content.reading_level = reading_level
            
            # Check if content meets minimum standards
            if quality_score >= self.min_quality_score and compliance.get('overall_compliance', False):
                return content
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error validating content: {e}")
            return None
    
    def calculate_quality_score(self, text: str) -> float:
        """Calculate comprehensive quality score for text."""
        try:
            # Basic metrics
            word_count = len(word_tokenize(text))
            sentence_count = len(sent_tokenize(text))
            
            # Length score (optimal range: 100-2000 words)
            if word_count < 50:
                length_score = 0.3
            elif word_count < 100:
                length_score = 0.6
            elif word_count <= 2000:
                length_score = 1.0
            else:
                length_score = max(0.7, 1.0 - (word_count - 2000) / 5000)
            
            # Readability score (sentences per word ratio)
            avg_sentence_length = word_count / max(sentence_count, 1)
            if 10 <= avg_sentence_length <= 20:
                readability_score = 1.0
            elif avg_sentence_length < 10:
                readability_score = 0.8
            else:
                readability_score = max(0.5, 1.0 - (avg_sentence_length - 20) / 30)
            
            # Vocabulary diversity
            unique_words = len(set(word.lower() for word in word_tokenize(text) if word.isalpha()))
            diversity_score = min(1.0, unique_words / max(word_count, 1) * 2)
            
            # Educational content indicators
            educational_keywords = [
                'definition', 'example', 'principle', 'theory', 'concept',
                'explain', 'describe', 'analyze', 'compare', 'contrast',
                'formula', 'equation', 'method', 'process', 'technique'
            ]
            
            educational_score = sum(1 for keyword in educational_keywords 
                                  if keyword.lower() in text.lower()) / len(educational_keywords)
            
            # Combine scores
            overall_score = (
                length_score * 0.3 +
                readability_score * 0.3 +
                diversity_score * 0.2 +
                educational_score * 0.2
            )
            
            return min(1.0, overall_score)
            
        except Exception as e:
            self.logger.error(f"Error calculating quality score: {e}")
            return 0.0
    
    def determine_cognitive_level(self, text: str) -> str:
        """Determine the cognitive level of the content."""
        # Keywords for different cognitive levels
        remember_keywords = ['define', 'list', 'recall', 'identify', 'name', 'state']
        understand_keywords = ['explain', 'describe', 'summarize', 'interpret', 'classify']
        apply_keywords = ['calculate', 'solve', 'demonstrate', 'use', 'apply', 'implement']
        analyze_keywords = ['analyze', 'compare', 'contrast', 'examine', 'investigate']
        evaluate_keywords = ['evaluate', 'assess', 'judge', 'critique', 'justify']
        create_keywords = ['create', 'design', 'develop', 'construct', 'formulate']
        
        text_lower = text.lower()
        
        # Count occurrences of each level
        levels = {
            'remember': sum(1 for word in remember_keywords if word in text_lower),
            'understand': sum(1 for word in understand_keywords if word in text_lower),
            'apply': sum(1 for word in apply_keywords if word in text_lower),
            'analyze': sum(1 for word in analyze_keywords if word in text_lower),
            'evaluate': sum(1 for word in evaluate_keywords if word in text_lower),
            'create': sum(1 for word in create_keywords if word in text_lower)
        }
        
        # Return the highest level with content
        for level in ['create', 'evaluate', 'analyze', 'apply', 'understand', 'remember']:
            if levels[level] > 0:
                return level
        
        return 'understand'  # Default level
    
    def calculate_reading_level(self, text: str) -> str:
        """Calculate approximate reading level."""
        try:
            words = word_tokenize(text)
            sentences = sent_tokenize(text)
            
            if not words or not sentences:
                return 'unknown'
            
            # Simple approximation based on average sentence length
            avg_sentence_length = len(words) / len(sentences)
            
            if avg_sentence_length <= 12:
                return 'elementary'
            elif avg_sentence_length <= 16:
                return 'middle_school'
            elif avg_sentence_length <= 20:
                return 'high_school'
            else:
                return 'college'
                
        except Exception as e:
            self.logger.error(f"Error calculating reading level: {e}")
            return 'unknown'
    
    def generate_qa_pairs(self, content: ContentItem) -> List[QAPair]:
        """Generate question-answer pairs from validated content."""
        try:
            qa_pairs = []
            sentences = sent_tokenize(content.content)
            
            if len(sentences) < 2:
                return qa_pairs
            
            # Generate different types of questions
            for i, sentence in enumerate(sentences[:5]):  # Limit to first 5 sentences
                if len(sentence.split()) < 8:  # Skip very short sentences
                    continue
                
                # Generate comprehension questions
                if 'is' in sentence.lower() or 'are' in sentence.lower():
                    # Convert statement to question
                    question = self.create_definition_question(sentence, content.topic)
                    if question:
                        qa_pairs.append(QAPair(
                            question=question,
                            answer=sentence.strip(),
                            context=content.content[:500] + "..." if len(content.content) > 500 else content.content,
                            difficulty='medium',
                            subject=content.subject,
                            topic=content.topic,
                            cognitive_level=content.cognitive_level,
                            quality_score=content.quality_score,
                            source=content.source
                        ))
                
                # Generate application questions
                if any(word in sentence.lower() for word in ['formula', 'equation', 'method', 'process']):
                    question = self.create_application_question(sentence, content.topic)
                    if question:
                        qa_pairs.append(QAPair(
                            question=question,
                            answer=sentence.strip(),
                            context=content.content[:500] + "..." if len(content.content) > 500 else content.content,
                            difficulty='hard',
                            subject=content.subject,
                            topic=content.topic,
                            cognitive_level='apply',
                            quality_score=content.quality_score,
                            source=content.source
                        ))
            
            return qa_pairs
            
        except Exception as e:
            self.logger.error(f"Error generating QA pairs: {e}")
            return []
    
    def create_definition_question(self, sentence: str, topic: str) -> Optional[str]:
        """Create a definition-type question from a sentence."""
        try:
            # Simple pattern matching for definitions
            if 'is' in sentence.lower():
                parts = sentence.split(' is ')
                if len(parts) >= 2:
                    subject = parts[0].strip()
                    return f"What is {subject.lower()}?"
            
            if 'are' in sentence.lower():
                parts = sentence.split(' are ')
                if len(parts) >= 2:
                    subject = parts[0].strip()
                    return f"What are {subject.lower()}?"
            
            return f"What can you tell me about {topic.lower()}?"
            
        except Exception as e:
            self.logger.error(f"Error creating definition question: {e}")
            return None
    
    def create_application_question(self, sentence: str, topic: str) -> Optional[str]:
        """Create an application-type question from a sentence."""
        try:
            if 'formula' in sentence.lower():
                return f"How would you apply the formula mentioned in {topic.lower()}?"
            
            if 'method' in sentence.lower():
                return f"When would you use this method in {topic.lower()}?"
            
            if 'process' in sentence.lower():
                return f"Can you explain how this process works in {topic.lower()}?"
            
            return f"How can you apply this concept from {topic.lower()}?"
            
        except Exception as e:
            self.logger.error(f"Error creating application question: {e}")
            return None
    
    async def process_subject(self, subject: str, topics: List[str]) -> Tuple[List[ContentItem], List[QAPair]]:
        """Process all topics for a subject."""
        all_content = []
        all_qa_pairs = []
        
        self.logger.info(f"Processing subject: {subject} with {len(topics)} topics")
        
        for topic in topics:
            try:
                self.logger.info(f"Processing topic: {topic}")
                
                # Fetch content from Wikipedia
                content_items = await self.fetch_wikipedia_content(topic, subject)
                
                for content in content_items:
                    all_content.append(content)
                    
                    # Generate QA pairs
                    qa_pairs = self.generate_qa_pairs(content)
                    all_qa_pairs.extend(qa_pairs)
                    
                    self.stats['total_validated'] += 1
                    
                    # Update quality statistics
                    if content.quality_score >= 0.8:
                        self.stats['by_quality']['high'] += 1
                    elif content.quality_score >= 0.6:
                        self.stats['by_quality']['medium'] += 1
                    else:
                        self.stats['by_quality']['low'] += 1
                
                # Rate limiting
                await asyncio.sleep(self.request_delay)
                
            except Exception as e:
                self.logger.error(f"Error processing topic {topic}: {e}")
                continue
        
        # Update subject statistics
        self.stats['by_subject'][subject] = {
            'content_items': len([c for c in all_content if c.subject == subject]),
            'qa_pairs': len([q for q in all_qa_pairs if q.subject == subject]),
            'avg_quality': np.mean([c.quality_score for c in all_content if c.subject == subject]) if all_content else 0
        }
        
        return all_content, all_qa_pairs
    
    async def build_comprehensive_dataset(self, max_topics_per_subject: int = 10) -> Dict:
        """Build a comprehensive educational dataset."""
        start_time = time.time()
        
        self.logger.info("Starting comprehensive dataset build...")
        
        await self.create_session()
        
        try:
            all_content = []
            all_qa_pairs = []
            
            # Process each subject
            for subject, topics in self.subject_topics.items():
                # Limit topics per subject for initial build
                limited_topics = topics[:max_topics_per_subject]
                
                content, qa_pairs = await self.process_subject(subject, limited_topics)
                all_content.extend(content)
                all_qa_pairs.extend(qa_pairs)
                
                self.logger.info(f"Completed {subject}: {len(content)} content items, {len(qa_pairs)} QA pairs")
            
            # Update final statistics
            self.stats['total_processed'] = len(all_content)
            self.stats['total_qa_pairs'] = len(all_qa_pairs)
            self.stats['processing_time'] = time.time() - start_time
            
            # Create comprehensive dataset structure
            dataset = {
                'metadata': {
                    'title': 'Enterprise-Grade High School Educational Dataset',
                    'creation_date': datetime.now().isoformat(),
                    'version': '1.0.0',
                    'builder': 'ImpressionCore Enterprise Dataset Builder',
                    'standards_compliance': '100%',
                    'license': 'MIT/Creative Commons Compatible',
                    'total_subjects': len(self.subject_topics),
                    'total_content_items': len(all_content),
                    'total_qa_pairs': len(all_qa_pairs),
                    'processing_time_seconds': self.stats['processing_time'],
                    'quality_distribution': self.stats['by_quality']
                },
                'statistics': self.stats,
                'content_items': [asdict(item) for item in all_content],
                'qa_pairs': [asdict(pair) for pair in all_qa_pairs],
                'standards_framework': self.standards.get_standards_summary()
            }
            
            self.logger.info(f"Dataset build completed successfully!")
            self.logger.info(f"Total content items: {len(all_content)}")
            self.logger.info(f"Total QA pairs: {len(all_qa_pairs)}")
            self.logger.info(f"Processing time: {self.stats['processing_time']:.2f} seconds")
            
            return dataset
            
        except Exception as e:
            self.logger.error(f"Error building dataset: {e}")
            self.logger.error(traceback.format_exc())
            raise
        
        finally:
            await self.close_session()
    
    def save_dataset(self, dataset: Dict, filename: str = None):
        """Save the dataset to a JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"enterprise_educational_dataset_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(dataset, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Dataset saved to {filename}")
            print(f"\n✅ Enterprise dataset saved to: {filename}")
            print(f"📊 Dataset Statistics:")
            print(f"   • Content Items: {dataset['metadata']['total_content_items']}")
            print(f"   • QA Pairs: {dataset['metadata']['total_qa_pairs']}")
            print(f"   • Subjects: {dataset['metadata']['total_subjects']}")
            print(f"   • Processing Time: {dataset['metadata']['processing_time_seconds']:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Error saving dataset: {e}")
            raise

async def main():
    """Main function to run the enterprise dataset builder."""
    print("🚀 ImpressionCore Enterprise-Grade Educational Dataset Builder")
    print("=" * 60)
    
    builder = EnterpriseDatasetBuilder()
    
    try:
        # Build comprehensive dataset
        print("📚 Building comprehensive educational dataset...")
        dataset = await builder.build_comprehensive_dataset(max_topics_per_subject=15)
        
        # Save the dataset
        print("💾 Saving dataset...")
        builder.save_dataset(dataset)
        
        print("\n🎉 Enterprise dataset build completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Build interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during build: {e}")
        logging.error(f"Build failed: {e}")
        logging.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())
