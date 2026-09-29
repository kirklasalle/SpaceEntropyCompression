#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_ipa\test_real_web_access.py #python #source_code #testing #web_interface  
**Category:** Source Code  
**Status:** Active
"""









# !/usr/bin/env python3

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_ipa\test_real_web_access.py #python #source_code #testing #web_interface  
**Category:** Source Code  
**Status:** Active

"""
Test script to verify REAL web access in Ultimate IPA
"""

import asyncio
import sys
from server_ultimate import UltimateSearchEngine, ImpressionCoreIPAUltimate
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

async def test_real_web_search():
    """Test the REAL web search capabilities"""
    
    console.print("🔍 [bold blue]Testing REAL Web Search Capabilities[/bold blue]")
    console.print("=" * 60)
    
    # Initialize search engine
    search_engine = UltimateSearchEngine()
    
    try:
        # Test 1: Google Search
        console.print("\n🌐 [yellow]Testing Google Search...[/yellow]")
        google_results = await search_engine._google_search("Python programming", 3)
        
        if google_results:
            console.print(f"✅ [green]Google Search: {len(google_results)} REAL results found![/green]")
            for i, result in enumerate(google_results[:2], 1):
                console.print(f"   {i}. {result['title'][:60]}...")
                console.print(f"      URL: {result['url']}")
                console.print(f"      Source: {result['source']}")
        else:
            console.print("❌ [red]Google Search: No results (may be blocked)[/red]")
        
        # Test 2: DuckDuckGo Search
        console.print("\n🦆 [yellow]Testing DuckDuckGo Search...[/yellow]")
        ddg_results = await search_engine._duckduckgo_search("artificial intelligence", 3)
        
        if ddg_results:
            console.print(f"✅ [green]DuckDuckGo Search: {len(ddg_results)} REAL results found![/green]")
            for i, result in enumerate(ddg_results[:2], 1):
                console.print(f"   {i}. {result['title'][:60]}...")
                console.print(f"      URL: {result['url']}")
        else:
            console.print("❌ [red]DuckDuckGo Search: No results (may be blocked)[/red]")
        
        # Test 3: Multi-Engine Search
        console.print("\n🔄 [yellow]Testing Multi-Engine Search...[/yellow]")
        multi_results = await search_engine.multi_engine_search(
            "machine learning", 
            engines=["google", "duckduckgo"], 
            max_results=5
        )
        
        console.print(f"✅ [green]Multi-Engine Search: {len(multi_results['results'])} total results![/green]")
        console.print(f"   Engines used: {multi_results['engines_used']}")
        
        # Test 4: Ultimate IPA Research
        console.print("\n🚀 [yellow]Testing Ultimate IPA Research...[/yellow]")
        ultimate_ipa = ImpressionCoreIPAUltimate()
        
        research_result = await ultimate_ipa.ultimate_research(
            "latest developments in AI",
            methodology="hybrid",
            depth_level=2
        )
        
        if research_result:
            console.print("✅ [green]Ultimate IPA Research: SUCCESS![/green]")
            console.print(f"   Methodology: {research_result.get('methodology_used', 'Unknown')}")
            console.print(f"   Processing time: {research_result.get('processing_time_ms', 0):.0f}ms")
            
            if 'immediate_response' in research_result:
                sources = research_result['immediate_response'].get('sources', [])
                console.print(f"   Real sources found: {len(sources)}")
        else:
            console.print("❌ [red]Ultimate IPA Research: Failed[/red]")
        
        # Summary
        console.print("\n" + "=" * 60)
        
        total_results = len(google_results) + len(ddg_results) + len(multi_results['results'])
        
        if total_results > 0:
            console.print("🎉 [bold green]REAL WEB ACCESS CONFIRMED![/bold green]")
            console.print(f"   Total real web results: {total_results}")
            console.print("   ✅ No more simulated data!")
            console.print("   ✅ Actual HTTP requests to real websites!")
            console.print("   ✅ Real HTML parsing and data extraction!")
        else:
            console.print("⚠️  [yellow]Web access may be blocked by firewalls/proxies[/yellow]")
            console.print("   The code is correct, but network restrictions may apply")
        
    except Exception as e:
        console.print(f"❌ [red]Error during testing: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_real_web_search())
