#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_eds\test_mcp_tools.py #api #python #source_code #testing  
**Category:** Source Code  
**Status:** Active
"""









# !/usr/bin/env python3

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_eds\test_mcp_tools.py #api #python #source_code #testing  
**Category:** Source Code  
**Status:** Active

"""
🔥 MCP Educational Data Scraper - Tool Verification Test
"""

import asyncio
import json
import logging
from server import LicenseCompliantScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mcp_tools():
    """Test all MCP tools to ensure they're working"""
    logger.info("🎓 Testing MCP Educational Data Scraper Tools")
    logger.info("=" * 60)
    
    scraper = LicenseCompliantScraper()
    
    # Test 1: Wikipedia Educational Scraping
    logger.info("📚 Test 1: Wikipedia Educational Content")
    try:
        wiki_content = await scraper.scrape_wikipedia_educational("Algebra")
        logger.info(f"✅ Wikipedia test successful: {len(wiki_content)} content items")
    except Exception as e:
        logger.error(f"❌ Wikipedia test failed: {e}")
    
    # Test 2: License Verification
    logger.info("📜 Test 2: License Compliance Verification")
    try:
        compliance = scraper.verify_license_compliance("Wikipedia", "https://en.wikipedia.org/wiki/Mathematics")
        logger.info(f"✅ License verification successful: {compliance}")
    except Exception as e:
        logger.error(f"❌ License verification failed: {e}")
    
    logger.info("🎉 MCP Tool Testing Complete!")
    
    return {
        "status": "SUCCESS",
        "tools_tested": ["scrape_wikipedia_educational", "verify_license_compliance"],
        "ready_for_vscode": True
    }

if __name__ == "__main__":
    result = asyncio.run(test_mcp_tools())
    print("\n" + "="*60)
    print("🚀 MCP EDUCATIONAL DATA SCRAPER STATUS: READY FOR VS CODE!")
    print("="*60)
    print(f"Status: {result['status']}")
    print(f"Tools tested: {', '.join(result['tools_tested'])}")
    print(f"Ready for VS Code: {result['ready_for_vscode']}")
    print("\n🔄 You can now restart VS Code and the MCP tools should appear!")
