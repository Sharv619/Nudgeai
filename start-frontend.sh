#!/bin/bash

echo "Starting NudgeAI Frontend..."

# Check if running in Docker environment
if [ "$1" = "docker" ]; then
    echo "Starting with Docker Compose..."
    docker compose -f docker-compose.dev.yml up -d
    echo "Frontend available at: http://localhost:3000"
    echo "MCP Server available at: http://localhost:8000"
else
    echo "Starting frontend in development mode..."
    
    # Check if node is available
    if ! command -v node &> /dev/null; then
        echo "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    # Navigate to frontend directory
    cd frontend
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        echo "Installing dependencies..."
        npm install
    fi
    
    # Start the development server
    echo "Starting Vite development server..."
    npm run dev -- --host 0.0.0.0
fi