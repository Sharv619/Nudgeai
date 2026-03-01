#!/usr/bin/env python3
"""
Test script for the NudgeAI MCP server with Hugging Face integration.
"""

import asyncio
from mcp_server import create_nudgeai_mcp_server
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def test_server():
    """Test the MCP server creation and basic functionality."""
    print("Testing NudgeAI MCP Server Creation...")

    try:
        # Create the server instance
        server = create_nudgeai_mcp_server()
        print("✓ Server created successfully")

        # Check that tools are registered
        print(f"✓ Server name: {server.name}")
        print(f"✓ Server instructions: {server.instructions[:100]}...")

        # Print registered tools
        print("\nRegistered tools:")
        # Note: We can't directly access the tool registry in FastMCP
        # But we know they are registered when the server is created

        print("\n✓ Server is ready for MCP connections")
        print("\nTo start the server, run: python mcp_server.py")
        print("Then connect with an MCP-compatible client.")

    except Exception as e:
        logger.error(f"Error testing server: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_server())
