#!/bin/bash

echo "🚀 NudgeAI Docker Setup"

# Check if Docker is installed
if ! [ -x "$(command -v docker)" ]; then
  echo "❌ Docker is not installed. Please install Docker first."
  exit 1
fi

# Check if Docker Compose is installed
if ! [ -x "$(command -v docker-compose)" ]; then
  echo "❌ Docker Compose is not installed. Please install Docker Compose first."
  exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📋 Copying .env.example to .env"
    cp .env.example .env
    echo "⚠️  Please edit .env with your actual API keys before proceeding"
else
    echo "✅ Found existing .env file"
fi

echo "🏗️  Building NudgeAI Docker containers..."

# Build all containers
docker-compose build

echo "🎉 Docker setup complete!"
echo ""
echo "To start NudgeAI in production mode:"
echo "  docker-compose up -d"
echo ""
echo "To start in development mode:"
echo "  docker-compose -f docker-compose.dev.yml up --build"
echo ""
echo "Services will be available at:"
echo "  - Frontend: http://localhost:3000"
echo "  - MCP Server: http://localhost:8000"
echo "  - API Bridge: http://localhost:8001"