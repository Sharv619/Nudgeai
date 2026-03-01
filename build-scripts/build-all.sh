#!/bin/bash
set -e

echo "Building NudgeAI Docker containers..."

# Build MCP server
echo "Building MCP server..."
docker build -f Dockerfile.mcp -t nudgeai/mcp-server .

# Build API bridge
echo "Building MCP API bridge..."
docker build -f Dockerfile.api-bridge -t nudgeai/api-bridge .

# Build frontend
echo "Building frontend..."
docker build -f frontend/Dockerfile -t nudgeai/frontend .

echo "All containers built successfully!"

echo "To run in production:"
echo "  docker-compose up -d"
echo ""
echo "To run in development:"
echo "  docker-compose -f docker-compose.dev.yml up --build"