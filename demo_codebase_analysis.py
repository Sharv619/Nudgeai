#!/usr/bin/env python3
"""
Demo script to showcase the codebase analysis functionality with the MCP server
"""

import asyncio
from codebase_mcp_extension import extend_mcp_server_with_codebase_tools
from mcp_server import create_nudgeai_mcp_server


async def demo_codebase_analysis():
    """
    Demonstrate how to use the codebase analysis tools
    """
    print("🧪 Demonstrating Codebase Analysis Capabilities")
    print("=" * 60)

    # Create the base server
    print("Creating base NudgeAI MCP server...")
    server = create_nudgeai_mcp_server()

    # Extend the server with codebase analysis tools
    print("Extending server with codebase analysis tools...")
    extend_mcp_server_with_codebase_tools()(server)

    print("✅ Server extended with codebase analysis tools!")
    print("\nAvailable tools:")
    print("- query_codebase: Search and analyze code for optimization")
    print("- analyze_codebase_patterns: Identify patterns for improvements")
    print("- Plus all existing tools:")
    print("  - query_calendar")
    print("  - query_location_history")
    print("  - query_drive_documents")
    print("  - analyze_habits")
    print("  - get_personal_insights")

    # Simulate using the new tools
    print("\n" + "=" * 60)
    print("🔍 SIMULATED OUTPUT: Querying codebase for 'optimization'")
    print("-" * 60)
    print("Found 2 files matching 'optimization':")
    print("  • mcp_server.py (1,200 lines)")
    print("  • ragsystem/embedding/example.py (450 lines)")
    print("\nAI Analysis: Found several opportunities for optimization:")
    print("  1. The _process_with_hf_model function could benefit from caching")
    print("  2. Multiple loops in data processing could be optimized")
    print("  3. Consider using async/await patterns for better performance")
    print("  4. Memory usage could be reduced by streaming large files")

    print("\n" + "=" * 60)
    print("🔍 SIMULATED OUTPUT: Analyzing codebase patterns")
    print("-" * 60)
    print("Pattern Analysis Results:")
    print("  • 15 Python files analyzed")
    print("  • 1,247 total lines of code")
    print("  • 32 functions identified")
    print("  • 8 classes defined")
    print("\nPatterns Found:")
    print("  1. Multiple files with similar error handling patterns")
    print("  2. Repetitive configuration loading across modules")
    print("  3. Several large functions that could be refactored")

    print("\n" + "=" * 60)
    print("🎯 Codebase analysis capabilities are now available!")
    print("   The MCP server can help analyze and optimize your codebase.")


def main():
    """
    Main function to run the demo
    """
    print("🚀 NudgeAI Codebase Analysis Demo")
    print("This demonstrates how the MCP server can analyze codebases")
    print()

    # Run the demonstration
    asyncio.run(demo_codebase_analysis())

    print("\n📋 To implement full functionality:")
    print("1. Fix the mcp_server.py file (currently has syntax issues)")
    print("2. Add the codebase analysis tools directly to mcp_server.py")
    print("3. The codebase_mcp_extension.py shows the implementation approach")
    print("4. The data ingestion modules are ready in data_ingestion/codebase/")


if __name__ == "__main__":
    main()
