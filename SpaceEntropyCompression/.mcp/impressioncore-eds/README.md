# 🔥 Educational Data Scraper MCP Server 🔥

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_eds\readme.md #api #documentation #testing #training  
**Category:** Documentation  
**Status:** Active

## Overview

This MCP server provides **BADASS** educational content scraping capabilities while maintaining strict license compliance. All scraped content is compatible with MIT/Apache licensing requirements.

## Features

### ✅ License-Compliant Sources
- **MIT OpenCourseWare**: Creative Commons licensed
- **Khan Academy**: Creative Commons licensed  
- **Wikipedia**: CC-BY-SA licensed
- **arXiv Papers**: Open access academic content
- **Government Resources**: Public domain content

### 🚀 Capabilities
- Real-time educational content scraping
- License compliance verification  
- Multi-source dataset creation
- Quality assessment and filtering
- Training-ready data formatting

## Installation

```bash
cd .mcp/educational-data-scraper
pip install -r requirements.txt
```

## Usage

### Start the Server
```bash
python server.py
```

### Available Tools

#### 1. `scrape_mit_ocw`
Scrape MIT OpenCourseWare content
```json
{
  "course_id": "6.00",
  "topic": "computer science fundamentals"
}
```

#### 2. `scrape_khan_academy`
Scrape Khan Academy educational content
```json
{
  "subject": "mathematics", 
  "topic": "calculus limits"
}
```

#### 3. `scrape_wikipedia_educational`
Extract educational content from Wikipedia
```json
{
  "topic": "machine learning"
}
```

#### 4. `scrape_arxiv_papers`
Get academic papers from arXiv
```json
{
  "query": "natural language processing",
  "max_results": 10
}
```

#### 5. `create_training_dataset`
Create comprehensive training dataset
```json
{
  "topics": [
    "calculus",
    "programming", 
    "physics",
    "machine learning"
  ]
}
```

#### 6. `verify_license_compliance`
Verify source license compliance
```json
{
  "source": "MIT OCW",
  "url": "https://ocw.mit.edu/courses/"
}
```

## License Compliance

### ✅ SAFE SOURCES
- MIT OpenCourseWare (CC-BY-NC-SA)
- Khan Academy (CC-BY-NC-SA)
- Wikipedia (CC-BY-SA)
- arXiv (Open Access)
- Government (.gov) resources

### ❌ AVOIDED SOURCES
- Copyrighted commercial content
- Restricted educational platforms
- Non-open-access academic content

## Output Format

All scraped content includes:
```json
{
  "source": "Source Name",
  "license": "License Type",
  "content": [...],
  "license_compliant": true,
  "educational_value": 9.2,
  "scraped_at": "2025-06-13T23:40:00Z"
}
```

## Integration with ImpressionCore

This server integrates seamlessly with:
- Training pipeline scripts
- Dataset generation tools
- Quality assessment systems
- License compliance checking

## Development

### Adding New Sources
1. Verify license compatibility
2. Implement scraper method
3. Add license verification
4. Test compliance checking

### Quality Standards
- Educational value >= 8.0
- License compliance verified
- Content structure standardized
- Metadata complete

## 🚀 READY FOR WORLD-CLASS TRAINING!

This MCP server enables ImpressionCore to access the highest quality educational content while maintaining strict license compliance. 

**LET'S MAKE AI EDUCATION BADASS AND LEGAL!** 🔥
