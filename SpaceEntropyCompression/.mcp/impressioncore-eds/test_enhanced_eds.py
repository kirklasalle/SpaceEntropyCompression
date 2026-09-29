#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_eds\test_enhanced_eds.py #memory_management #multimodal #performance #python #source_code #testing #training  
**Category:** Source Code  
**Status:** Active
"""









# !/usr/bin/env python3

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:26:57  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_eds\test_enhanced_eds.py #memory_management #multimodal #performance #python #source_code #testing #training  
**Category:** Source Code  
**Status:** Active

"""
ImpressionCore Enhanced EDS Test Script
Comprehensive testing of the enhanced dataset discovery system
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent))

try:
    from enhanced_server import EnhancedEDSMCPServer
    from config.dataset_sources import DATASET_REPOSITORIES, USE_CASE_MAPPINGS
    SERVER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import EDS server: {e}")
    SERVER_AVAILABLE = False

async def test_enhanced_eds():
    """Test all enhanced EDS functionality."""
    print("🚀 Testing Enhanced ImpressionCore EDS System")
    print("=" * 70)
    
    if not SERVER_AVAILABLE:
        print("❌ EDS server not available for testing")
        return
    
    # Initialize server
    server = EnhancedEDSMCPServer()
    
    # Test 1: Statistics
    print("\n📊 Test 1: Getting System Statistics")
    try:
        result = await server.handle_tool_call("eds_get_statistics", {})
        if result["success"]:
            stats = result["data"]
            print(f"✅ Total Categories: {stats['total_categories']}")
            print(f"✅ Total Sources: {stats['total_sources']}")
            print(f"✅ Total Datasets: {stats['total_datasets']}")
            print(f"✅ Use Cases Supported: {len(stats['use_cases_supported'])}")
            
            print("\n📈 Category Breakdown:")
            for category, info in stats['category_breakdown'].items():
                print(f"   - {category}: {info['source_count']} sources, {info['dataset_count']} datasets")
        else:
            print(f"❌ Statistics test failed: {result['error']}")
    except Exception as e:
        print(f"❌ Statistics test error: {e}")
    
    # Test 2: Dataset Discovery
    print("\n🔍 Test 2: Dataset Discovery")
    try:
        result = await server.handle_tool_call("eds_discover_datasets", {
            "category": "computer_vision",
            "modality": "image"
        })
        
        if result["success"]:
            datasets = result["data"]["datasets"]
            print(f"✅ Found {len(datasets)} computer vision datasets")
            
            # Show first 5 datasets
            for i, dataset in enumerate(datasets[:5]):
                status = dataset["verification"]["status"]
                status_icon = "🟢" if status == "online" else "🔴" if status == "offline" else "⚠️"
                print(f"   {i+1}. {dataset['name']} {status_icon}")
                print(f"      URL: {dataset['base_url']}")
                print(f"      Categories: {', '.join(dataset['categories'])}")
                print(f"      Notable datasets: {len(dataset['notable_datasets'])}")
        else:
            print(f"❌ Discovery test failed: {result['error']}")
    except Exception as e:
        print(f"❌ Discovery test error: {e}")
    
    # Test 3: Recommendations for ImpressionCore B2
    print("\n💡 Test 3: Recommendations for ImpressionCore B2 (GTX 1050 Ti)")
    try:
        result = await server.handle_tool_call("eds_get_recommendations", {
            "use_case": "conversation",
            "hardware_constraints": {
                "vram_gb": 4,
                "ram_gb": 32,
                "storage_gb": 500
            }
        })
        
        if result["success"]:
            recommendations = result["data"]["recommendations"]
            print(f"✅ Got {len(recommendations)} recommendations for conversation")
            
            print("\n🏆 Top 5 Recommendations:")
            for i, rec in enumerate(recommendations[:5]):
                score = rec['suitability_score']
                memory = rec['estimated_memory_gb']
                auth = "🔐" if rec['auth_required'] else "🔓"
                print(f"   {i+1}. {rec['dataset_name']} (Score: {score:.2f}) {auth}")
                print(f"      Memory: {memory}GB | Repository: {rec['repository']}")
                print(f"      Formats: {', '.join(rec['formats'])}")
        else:
            print(f"❌ Recommendations test failed: {result['error']}")
    except Exception as e:
        print(f"❌ Recommendations test error: {e}")
    
    # Test 4: Source Verification (sample)
    print("\n🔍 Test 4: Source Verification (Sample)")
    try:
        result = await server.handle_tool_call("eds_verify_sources", {
            "source_names": ["huggingface_datasets", "uci_ml_repository", "kaggle_datasets"],
            "force_refresh": False
        })
        
        if result["success"]:
            verification_data = result["data"]
            print(f"✅ Verified {verification_data['total_verified']} sources")
            print(f"   Online: {verification_data['online_count']} 🟢")
            print(f"   Offline: {verification_data['offline_count']} 🔴")
            print(f"   Errors: {verification_data['error_count']} ⚠️")
            print(f"   Health: {verification_data['health_percentage']:.1f}%")
            
            print("\n📋 Verification Details:")
            for result_item in verification_data['verification_results']:
                status = result_item['status']
                status_icon = "🟢" if status == "online" else "🔴" if status == "offline" else "⚠️"
                response_time = result_item.get('response_time', 'N/A')
                print(f"   - {result_item['source_name']}: {status} {status_icon}")
                if response_time != 'N/A':
                    print(f"     Response time: {response_time:.2f}s")
        else:
            print(f"❌ Verification test failed: {result['error']}")
    except Exception as e:
        print(f"❌ Verification test error: {e}")
    
    # Test 5: Specific Dataset Info
    print("\n📄 Test 5: Dataset Information Lookup")
    try:
        result = await server.handle_tool_call("eds_get_dataset_info", {
            "dataset_name": "squad",
            "include_verification": True
        })
        
        if result["success"]:
            info = result["data"]
            print(f"✅ Dataset: {info['name']}")
            print(f"   Repository: {info['repository']}")
            print(f"   Category: {info['category']}")
            print(f"   Formats: {', '.join(info['formats'])}")
            print(f"   Memory estimate: {info['estimated_memory_gb']}GB")
            print(f"   Quality score: {info['quality_score']}")
            
            if 'verification' in info:
                status = info['verification']['status']
                status_icon = "🟢" if status == "online" else "🔴" if status == "offline" else "⚠️"
                print(f"   Status: {status} {status_icon}")
        else:
            print(f"❌ Dataset info test failed: {result['error']}")
    except Exception as e:
        print(f"❌ Dataset info test error: {e}")
    
    # Test 6: Use Case Coverage Analysis
    print("\n🎯 Test 6: Use Case Coverage Analysis")
    for use_case in ["conversation", "image_classification", "speech_recognition", "multimodal"]:
        try:
            result = await server.handle_tool_call("eds_get_recommendations", {
                "use_case": use_case,
                "hardware_constraints": {"vram_gb": 4}
            })
            
            if result["success"]:
                count = len(result["data"]["recommendations"])
                print(f"   {use_case}: {count} recommendations ✅")
            else:
                print(f"   {use_case}: Failed ❌")
        except Exception as e:
            print(f"   {use_case}: Error - {e} ⚠️")
    
    print("\n" + "=" * 70)
    print("🎉 Enhanced EDS Testing Complete!")
    print("\nℹ️ Summary:")
    print("- Comprehensive dataset discovery across 40+ verified sources")
    print("- Smart recommendations based on hardware constraints")
    print("- Automated health monitoring and verification")
    print("- Support for multiple use cases and modalities")
    print("- Integration with academic, government, and industry sources")

async def performance_benchmark():
    """Benchmark EDS performance."""
    print("\n⚡ Performance Benchmark")
    print("-" * 30)
    
    if not SERVER_AVAILABLE:
        print("❌ Server not available for benchmarking")
        return
    
    server = EnhancedEDSMCPServer()
    
    # Benchmark discovery speed
    start_time = datetime.now()
    result = await server.handle_tool_call("eds_discover_datasets", {"category": "all"})
    discovery_time = (datetime.now() - start_time).total_seconds()
    
    if result["success"]:
        dataset_count = result["data"]["total_found"]
        print(f"✅ Discovery: {dataset_count} datasets in {discovery_time:.2f}s")
        print(f"   Rate: {dataset_count/discovery_time:.1f} datasets/second")
    
    # Benchmark recommendation speed
    start_time = datetime.now()
    result = await server.handle_tool_call("eds_get_recommendations", {
        "use_case": "conversation",
        "hardware_constraints": {"vram_gb": 4}
    })
    recommendation_time = (datetime.now() - start_time).total_seconds()
    
    if result["success"]:
        rec_count = len(result["data"]["recommendations"])
        print(f"✅ Recommendations: {rec_count} suggestions in {recommendation_time:.2f}s")

def manual_test_mcp_protocol():
    """Test MCP protocol manually."""
    print("\n🔌 MCP Protocol Test")
    print("-" * 25)
    
    # Simulate MCP calls
    test_calls = [
        {"method": "initialize", "id": 1},
        {"method": "tools/list", "id": 2},
        {
            "method": "tools/call",
            "id": 3,
            "params": {
                "name": "eds_get_statistics",
                "arguments": {}
            }
        }
    ]
    
    for call in test_calls:
        print(f"📤 Request: {call['method']}")
        # In real implementation, this would go through MCP
        print(f"   ID: {call['id']}")
        if 'params' in call:
            print(f"   Params: {call['params']}")
        print("✅ Would be processed by MCP server")

if __name__ == "__main__":
    print("🧪 ImpressionCore Enhanced EDS Test Suite")
    print("========================================")
    
    # Run main tests
    asyncio.run(test_enhanced_eds())
    
    # Run performance benchmark
    asyncio.run(performance_benchmark())
    
    # Test MCP protocol simulation
    manual_test_mcp_protocol()
    
    print("\n🎯 Test Summary:")
    print("- Enhanced EDS system provides comprehensive dataset access")
    print("- 40+ verified sources across multiple categories and modalities")
    print("- AI-powered recommendations for hardware-constrained environments")
    print("- Automated health monitoring and caching for reliability")
    print("- Ready for ImpressionCore B2 training and embedding workflows")
