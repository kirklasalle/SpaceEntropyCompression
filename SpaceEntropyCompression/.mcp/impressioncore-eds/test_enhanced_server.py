#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_eds\test_enhanced_server.py #memory_management #python #source_code #testing  
**Category:** Source Code  
**Status:** Active
"""









# !/usr/bin/env python3

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_eds\test_enhanced_server.py #memory_management #python #source_code #testing  
**Category:** Source Code  
**Status:** Active

"""
Test script for Enhanced EDS MCP Server with annotation and validation support.
"""

import asyncio
import sys
from enhanced_server import EnhancedEDSMCPServer

async def test_server():
    print("🚀 Testing Enhanced EDS MCP Server...")
    
    # Initialize server
    server = EnhancedEDSMCPServer()
    print(f"✅ Server loaded with {len(server.get_tools())} tools")
    
    # List all tools
    print("\n📊 Available tools:")
    for tool in server.get_tools():
        print(f"  - {tool['name']}: {tool['description'][:60]}...")
    
    # Test embedding dataset discovery
    print("\n🎯 Testing embedding dataset discovery...")
    try:
        embedding_datasets = await server.discover_embedding_datasets(
            modality="text",
            use_case="sentence_similarity",
            min_annotation_coverage=0.8,
            require_validation_split=True,
            hardware_constraints={"vram_gb": 4, "max_dataset_size_gb": 10}
        )
        
        print(f"📝 Found {len(embedding_datasets)} embedding-friendly datasets with annotations")
        
        # Show top 3 datasets
        for i, dataset in enumerate(embedding_datasets[:3]):
            print(f"\n{i+1}. {dataset['name']} (Category: {dataset['category']})")
            print(f"   Annotation Types: {dataset.get('annotation_types', [])}")
            print(f"   Embedding Score: {dataset.get('embedding_suitability_score', 'N/A'):.2f}")
            print(f"   Quality Score: {dataset.get('quality_score', 'N/A'):.2f}")
            print(f"   Memory Estimate: {dataset.get('estimated_memory_gb', 'N/A')} GB")
            
    except Exception as e:
        print(f"❌ Error testing embedding discovery: {e}")
    
    # Test regular dataset discovery with annotation filters
    print("\n🔍 Testing annotation-required dataset discovery...")
    try:
        annotated_datasets = await server.discover_datasets(
            annotation_required=True,
            validation_required=True,
            embedding_friendly=False  # All datasets, not just embedding-friendly
        )
        
        print(f"📊 Found {len(annotated_datasets)} datasets with annotations and validation")
        
        # Count by category
        category_counts = {}
        for dataset in annotated_datasets:
            category = dataset['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        print("\n📈 Distribution by category:")
        for category, count in sorted(category_counts.items()):
            print(f"   {category}: {count} datasets")
            
    except Exception as e:
        print(f"❌ Error testing annotation discovery: {e}")
    
    print("\n✅ Enhanced EDS MCP Server testing completed!")

if __name__ == "__main__":
    asyncio.run(test_server())
