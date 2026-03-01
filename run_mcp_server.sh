#!/bin/bash
# Script to run the NudgeAI MCP Server with Hugging Face integration

# Activate virtual environment
source venv/bin/activate

echo "Starting NudgeAI MCP Server with Hugging Face Integration..."
echo "Using Hugging Face model: ${HF_MODEL:-mistralai/Mistral-7B-Instruct-v0.1}"

# Run the MCP server
python mcp_server.py

echo "NudgeAI MCP Server stopped."