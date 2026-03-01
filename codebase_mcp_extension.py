#!/usr/bin/env python3
"""
Extension to MCP server functionality for codebase analysis
This creates a separate module that adds codebase analysis tools
without modifying the original mcp_server.py file.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, EmbeddedResource
import os
import sys

# Add project root to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_ingestion.codebase.code_fetcher import CodeFetcher
from data_ingestion.codebase.code_parser import analyze_codebase
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Hugging Face client
HF_TOKEN = os.getenv("HF_token")
HF_MODEL = os.getenv("HF_MODEL", "google/flan-t5-small")

if not HF_TOKEN:
    raise ValueError("HF_token environment variable is required")

hf_client = InferenceClient(model=HF_MODEL, token=HF_TOKEN)


def _process_with_hf_model(prompt: str) -> str:
    """
    Process text using the Hugging Face model.

    Args:
        prompt: Input prompt to process

    Returns:
        Generated response from the model
    """
    try:
        # Use the Hugging Face Inference API to process the prompt
        # First try the chat completion API
        try:
            response = hf_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7,
            )
            content = response.choices[0].message.content
            return content if content is not None else f"Processed: {prompt[:100]}..."
        except:
            # If chat completion fails, fall back to text generation
            response = hf_client.text_generation(
                prompt=prompt,
                max_new_tokens=500,
                temperature=0.7,
                return_full_text=False,
            )
            return (
                response
                if isinstance(response, str)
                else str(response or f"Processed: {prompt[:100]}...")
            )
    except Exception as e:
        logger.error(f"Error processing with Hugging Face model: {e}")
        # Return a simulated response when API fails
        return f"Simulated AI insights for: {prompt[:100]}..."


def extend_mcp_server_with_codebase_tools():
    """
    Function to extend an existing MCP server with codebase analysis tools.
    This can be called to add the new functionality without modifying the original file.
    """

    def _register_codebase_tools(server: FastMCP):
        """Register codebase analysis tools to the server."""

        @server.tool(
            name="query_codebase",
            description="Search and analyze the local codebase for optimization opportunities",
            title="Codebase Analysis Tool",
        )
        async def query_codebase(
            query: str, file_type: Optional[str] = None, max_results: int = 5
        ) -> Dict[str, Any]:
            """
            Search through the local codebase based on a query and process with Hugging Face model.
            This tool analyzes code files in the current project to identify optimization opportunities.

            Args:
                query: Search query string (e.g., 'optimization', 'performance', 'refactoring')
                file_type: Optional filter for file type (e.g., 'py', 'js', 'ts')
                max_results: Maximum number of results to return (default 5)

            Returns:
                Dictionary with matching code segments and AI-processed analysis
            """
            logger.info(
                f"Searching codebase for: '{query}', type: {file_type}, max: {max_results}"
            )

            # Initialize the code fetcher
            fetcher = CodeFetcher()

            # Define supported file extensions
            if file_type:
                extensions = [f".{file_type}"]
            else:
                extensions = [
                    ".py",
                    ".js",
                    ".ts",
                    ".jsx",
                    ".tsx",
                    ".java",
                    ".cpp",
                    ".c",
                    ".html",
                    ".css",
                    ".md",
                ]

            # Fetch code files from the project
            code_files = fetcher.fetch_files(extensions)

            # Filter and sort files based on relevance to the query
            filtered_files = []
            for file_info in code_files:
                # Look for the query term in filename or content
                if (
                    query.lower() in file_info["filename"].lower()
                    or query.lower() in file_info["content"].lower()
                ):
                    filtered_files.append(file_info)

            # Sort by size and take top results
            filtered_files = sorted(
                filtered_files, key=lambda x: x["size"], reverse=True
            )[:max_results]

            # Process the code content with Hugging Face model to generate analysis
            if filtered_files:
                code_context = "\n".join(
                    [
                        f"File: {f['path']}\nContent Preview: {f['content'][:300]}...\n"
                        for f in filtered_files
                    ]
                )
                prompt = f"""
                Analyze the following codebase files in response to the query '{query}':
                {code_context}
                
                Provide a concise analysis of the code and specific suggestions for:
                1. Optimization opportunities
                2. Performance improvements
                3. Code quality enhancements
                4. Best practices recommendations
                """
            else:
                # If no files match the query, search for files more broadly
                all_files = sorted(code_files, key=lambda x: x["size"], reverse=True)[
                    :max_results
                ]
                if all_files:
                    code_context = "\n".join(
                        [
                            f"File: {f['path']}\nContent Preview: {f['content'][:200]}...\n"
                            for f in all_files
                        ]
                    )
                    prompt = f"""
                    Here are some codebase files. Analyze them in light of the query '{query}':
                    {code_context}
                    
                    Provide a concise analysis of the code and specific suggestions for:
                    1. Performance improvements
                    2. Code quality enhancements
                    3. Best practices recommendations
                    """
                    filtered_files = all_files
                else:
                    prompt = f"No code files were found in the project to analyze for the query '{query}'."

            ai_analysis = _process_with_hf_model(prompt)

            # Prepare simplified file info for response
            result_files = []
            if filtered_files:  # Only process if filtered_files is not empty
                result_files = [
                    {
                        "path": f["path"],
                        "filename": f["filename"],
                        "size": f["size"],
                        "lines": f["lines"],
                    }
                    for f in filtered_files
                ]

            return {
                "files": result_files,
                "analysis": ai_analysis,
                "count": len(result_files),
                "query": query,
            }

        @server.tool(
            name="analyze_codebase_patterns",
            description="Identify patterns in the codebase that may indicate optimization opportunities",
            title="Code Pattern Analysis Tool",
        )
        async def analyze_codebase_patterns() -> Dict[str, Any]:
            """
            Analyze the codebase to identify patterns that may indicate optimization opportunities.
            Looks for common patterns like repeated code, inefficient algorithms, etc.

            Returns:
                Analysis of codebase patterns with optimization suggestions
            """
            logger.info("Analyzing codebase patterns for optimization opportunities")

            # Use the code fetcher and parser to analyze the codebase
            parsed_files = analyze_codebase()

            # Analyze patterns in the code
            pattern_analysis = {
                "total_files": len(parsed_files),
                "total_lines": sum(f.get("lines_of_code", 0) for f in parsed_files),
                "python_files": len(
                    [f for f in parsed_files if f["language"] == "python"]
                ),
                "functions_count": sum(len(f["functions"]) for f in parsed_files),
                "classes_count": sum(len(f["classes"]) for f in parsed_files),
            }

            # Extract patterns found from each parsed file
            patterns_found = []
            for file_info in parsed_files:
                if "potential_issues" in file_info:
                    for issue in file_info["potential_issues"]:
                        patterns_found.append(
                            {
                                "file": file_info["file_path"],
                                "pattern": issue,
                                "language": file_info["language"],
                            }
                        )

            # Process the pattern analysis with Hugging Face model to generate recommendations
            prompt = f"""
            Analyze the following codebase pattern analysis:
            Total files analyzed: {pattern_analysis["total_files"]}
            Total lines of code: {pattern_analysis["total_lines"]}
            Python files: {pattern_analysis["python_files"]}
            Total functions: {pattern_analysis["functions_count"]}
            Total classes: {pattern_analysis["classes_count"]}
            Patterns found that may indicate optimization opportunities:
            {[p["pattern"] + " in " + p["file"] for p in patterns_found[:10]]}  # Show first 10 patterns
            
            Provide specific recommendations for:
            1. Code structure improvements
            2. Performance optimizations
            3. Refactoring opportunities
            4. Best practices to implement
            """

            ai_recommendations = _process_with_hf_model(prompt)

            return {
                "analysis": pattern_analysis,
                "patterns_found": patterns_found,
                "recommendations": ai_recommendations,
            }

    # Return the function that registers the tools
    return _register_codebase_tools


def main():
    """
    Main function demonstrating the extension.
    This would typically be used to extend an existing server.
    """
    print("NudgeAI Codebase Analysis Extension")
    print("This module extends the MCP server with codebase analysis capabilities.")
    print("\nThe extension provides:")
    print("- query_codebase: Search and analyze code for optimization")
    print("- analyze_codebase_patterns: Identify patterns for improvements")

    # Example of how to use this extension:
    print("\nTo use this extension:")
    print("1. Create or get an existing MCP server")
    print("2. Call extend_mcp_server_with_codebase_tools()(server)")
    print("3. The server will now have codebase analysis tools")


if __name__ == "__main__":
    main()
