#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\web_search_mcp\test_server.py #python #source_code #testing #web_interface  
**Category:** Source Code  
**Status:** Active
"""









# !/usr/bin/env python3

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\web_search_mcp\test_server.py #python #source_code #testing #web_interface  
**Category:** Source Code  
**Status:** Active

"""
Test script for web-search-mcp server
"""

import asyncio
import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from server import server
    print("✅ Server import successful")
except Exception as e:
    print(f"❌ Server import failed: {e}")
    sys.exit(1)

async def test_list_tools():
    """Test the list_tools functionality"""
    try:
        tools_result = await server._handlers["tools/list"]()
        print(f"✅ Tools list successful: {len(tools_result.tools)} tools found")
        
        for tool in tools_result.tools:
            print(f"  - {tool.name}: {tool.description}")
        
        return True
    except Exception as e:
        print(f"❌ Tools list failed: {e}")
        return False

async def test_call_tool():
    """Test calling a simple tool"""
    try:
        # Test the get_search_suggestions tool with a simple query
        result = await server._handlers["tools/call"]("get_search_suggestions", {"query": "python tutorial"})
        print("✅ Tool call successful")
        
        # Parse the response
        if result.content and len(result.content) > 0:
            content = result.content[0].text
            data = json.loads(content)
            print(f"  - Original query: {data.get('original_query')}")
            print(f"  - Suggestions count: {len(data.get('suggestions', []))}")
        
        return True
    except Exception as e:
        print(f"❌ Tool call failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🔍 Testing Web Search MCP Server...")
    print("=" * 50)
    
    # Test 1: List tools
    print("\n1. Testing tool list...")
    tools_ok = await test_list_tools()
    
    # Test 2: Call a tool
    print("\n2. Testing tool call...")
    call_ok = await test_call_tool()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"  Tools List: {'✅ PASS' if tools_ok else '❌ FAIL'}")
    print(f"  Tool Call:  {'✅ PASS' if call_ok else '❌ FAIL'}")
    
    if tools_ok and call_ok:
        print("\n🎉 All tests passed! The MCP server is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the server implementation.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        sys.exit(1)
