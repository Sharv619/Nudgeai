#!/usr/bin/env python3
"""
Test script to verify the codebase analysis functionality works with the MCP server
"""

import asyncio
from mcp_client_connector import OpencodeMCPConnector


async def test_codebase_analysis():
    """
    Test the new codebase analysis tools added to the MCP server
    """
    print("🧪 Testing Codebase Analysis Tools")
    print("=" * 50)

    connector = OpencodeMCPConnector()

    # Test the new query_codebase tool
    print("\n1. Testing query_codebase tool...")
    try:
        result = await connector.call_mcp_tool(
            "query_codebase", {"query": "optimization", "max_results": 3}
        )
        print(f"   ✓ query_codebase returned {result.get('count', 0)} results")
        if result.get("files"):
            print(f"   First file: {result['files'][0]['filename']}")
    except Exception as e:
        print(f"   ❌ query_codebase failed: {e}")

    # Test the new analyze_codebase_patterns tool
    print("\n2. Testing analyze_codebase_patterns tool...")
    try:
        result = await connector.call_mcp_tool("analyze_codebase_patterns", {})
        print(f"   ✓ analyze_codebase_patterns completed")
        print(f"   Found {len(result.get('patterns_found', []))} patterns")
        if result.get("patterns_found"):
            print(f"   First pattern: {result['patterns_found'][0]['pattern']}")
    except Exception as e:
        print(f"   ❌ analyze_codebase_patterns failed: {e}")

    # Test a general optimization query
    print("\n3. Testing optimization query...")
    try:
        result = await connector.call_mcp_tool(
            "query_codebase", {"query": "performance improvements", "max_results": 2}
        )
        print(f"   ✓ Performance query returned {result.get('count', 0)} results")
        print(f"   Analysis preview: {result.get('analysis', '')[:100]}...")
    except Exception as e:
        print(f"   ❌ Optimization query failed: {e}")

    print("\n" + "=" * 50)
    print("✅ Codebase analysis tools test completed!")


def main():
    """
    Main function to run the tests
    """
    print("🚀 Testing MCP Server Codebase Analysis Extensions")
    asyncio.run(test_codebase_analysis())


if __name__ == "__main__":
    main()
