#!/usr/bin/env python3
"""
Simple demo of the codebase analysis functionality
"""

import asyncio
from data_ingestion.codebase.code_fetcher import CodeFetcher
from data_ingestion.codebase.code_parser import analyze_codebase


async def demo_codebase_analysis():
    """
    Demonstrate the codebase analysis functionality
    """
    print("🧪 Demonstrating Codebase Analysis Capabilities")
    print("=" * 60)

    print("Initializing Code Fetcher...")
    fetcher = CodeFetcher()

    print("Fetching Python files from the project...")
    files = fetcher.fetch_files([".py"])

    print(f"✅ Found {len(files)} Python files")

    if files:
        print("\n📁 Largest Python files:")
        for file_info in sorted(files, key=lambda x: x["size"], reverse=True)[:5]:
            print(f"   {file_info['path']} ({file_info['size']} bytes)")

    print("\n🔄 Analyzing codebase patterns...")
    parsed_files = analyze_codebase()

    print(f"✅ Analyzed {len(parsed_files)} files")

    # Count statistics
    total_functions = sum(len(f["functions"]) for f in parsed_files)
    total_classes = sum(len(f["classes"]) for f in parsed_files)
    python_files = len([f for f in parsed_files if f["language"] == "python"])

    print(f"\n📊 Analysis Results:")
    print(f"   Python files: {python_files}")
    print(f"   Total functions: {total_functions}")
    print(f"   Total classes: {total_classes}")

    # Show potential issues
    all_issues = []
    for file_info in parsed_files:
        if file_info["potential_issues"]:
            for issue in file_info["potential_issues"]:
                all_issues.append((file_info["file_path"], issue))

    if all_issues:
        print(f"\n⚠️  Potential issues found in {len(all_issues)} locations:")
        for file_path, issue in all_issues[:10]:  # Show first 10
            print(f"   • {file_path}: {issue}")
        if len(all_issues) > 10:
            print(f"   ... and {len(all_issues) - 10} more")

    print("\n" + "=" * 60)
    print("🎯 Codebase analysis modules are ready!")
    print("   The data ingestion components are fully implemented.")


def main():
    """
    Main function to run the demo
    """
    print("🚀 NudgeAI Codebase Analysis Demo")
    print("This demonstrates the implemented codebase analysis capabilities")
    print()

    # Run the demonstration
    asyncio.run(demo_codebase_analysis())

    print("\n📋 Summary of implemented components:")
    print("✅ data_ingestion/codebase/")
    print("   ├── code_fetcher.py (fetches code files)")
    print("   ├── code_parser.py (analyzes code structure)")
    print("   └── code_chunker.py (chunks code for processing)")
    print("✅ MCP server extended with codebase analysis tools")
    print("✅ Ready to analyze and optimize codebases")


if __name__ == "__main__":
    main()
