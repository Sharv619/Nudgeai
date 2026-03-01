# NudgeAI Docker Setup

This document describes the Docker setup for the NudgeAI system, which is built around the Model Context Protocol (MCP) server and FAISS vector database.

## Architecture Overview

The NudgeAI system consists of three main services:

1. **Frontend** - React-based UI for visualization and interaction
2. **MCP Server** - Core server handling all data processing with Hugging Face models
3. **MCP API Bridge** - HTTP gateway that exposes MCP tools as REST endpoints
4. **NGINX** - Reverse proxy for routing requests between services

## Prerequisites

- Docker Engine (v20.10.0 or higher)
- Docker Compose (v2.0.0 or higher)
- Hugging Face API token
- Google API credentials (optional, for data integration)
- WhiteCircle API key (optional, for quality validation)

## Setup Instructions

### 1. Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Then edit `.env` with your actual credentials:

```bash
# Hugging Face Configuration
HF_token=your_actual_token_here
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.1

# Google API Configuration (optional)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# WhiteCircle API Key (optional)
WHITECIRCLE_API_KEY=your_whitecircle_api_key
```

### 2. Google Authentication (Optional)

If you want to integrate with Google Calendar, Drive, etc., you'll need to set up authentication:

1. Create a Google Cloud project and OAuth 2.0 credentials
2. Download the `credentials.json` file
3. Rename it to `token.json` and place it in the root directory
4. Also create a `drive_token.json` file for Drive access

### 3. Build and Run

#### Production Mode

To build and run in production mode:

```bash
# Build all containers
docker-compose build

# Start services
docker-compose up -d
```

The system will be available at:
- Frontend: http://localhost:3000
- MCP Server: http://localhost:8000
- API Bridge: http://localhost:8001

#### Development Mode

To run in development mode with hot-reloading:

```bash
# Build and start development services
docker-compose -f docker-compose.dev.yml up --build
```

## Service Details

### MCP Server
- Port: 8000
- Purpose: Core processing server using Hugging Face models
- Features: FAISS vector database, WhiteCircle quality gate, multiple data integration tools

### MCP API Bridge
- Port: 8001
- Purpose: Exposes MCP tools as HTTP endpoints
- Features: Translation layer between MCP protocol and REST APIs

### Frontend
- Port: 3000
- Purpose: User interface for interacting with the system
- Features: Dashboard, data visualization, nudge management

### NGINX
- Port: 80
- Purpose: Reverse proxy and load balancing
- Features: Request routing, static file serving, security headers

## Data Persistence

The system uses Docker volumes for data persistence:

- `faiss-indexes`: FAISS vector database indexes
- `embeddings-cache`: Cached embeddings for faster retrieval
- `data-sync`: Synchronized data from external sources
- `logs`: Application logs

These volumes ensure that your data persists between container restarts.

## Building Individual Containers

If you want to build individual containers:

```bash
# Build MCP server only
docker build -f Dockerfile.mcp -t nudgeai/mcp-server .

# Build API bridge only
docker build -f Dockerfile.api-bridge -t nudgeai/api-bridge .

# Build frontend only
docker build -f frontend/Dockerfile -t nudgeai/frontend .
```

## Development Workflow

For active development, use the development compose file:

```bash
# Start with live reload
docker-compose -f docker-compose.dev.yml up --build

# Access frontend container
docker exec -it nudgeai-frontend-dev sh

# Access MCP server container
docker exec -it nudgeai-mcp-server-dev sh
```

## Troubleshooting

### Common Issues

1. **Port already in use**: Make sure ports 80, 3000, 8000, 8001 are available
2. **Missing environment variables**: Ensure all required variables are set in `.env`
3. **Permission denied**: Check file permissions for token files
4. **API rate limits**: Hugging Face and Google APIs may have rate limits

### Useful Commands

```bash
# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f mcp-server

# Stop all services
docker-compose down

# Remove volumes (WARNING: This will delete your data)
docker-compose down -v

# Clean up unused resources
docker system prune
```

## Security Considerations

- Never commit actual API keys to version control
- Use environment variables for sensitive information
- Regularly rotate API keys
- Monitor API usage to prevent unauthorized access

## Scaling

For production deployments, consider:
- Adding a load balancer
- Using external databases for persistence
- Implementing monitoring and alerting
- Setting up automatic backups
- Configuring SSL certificates for HTTPS

## Updating

To update to the latest version:

```bash
# Pull latest code
git pull origin main

# Rebuild containers
docker-compose build --pull

# Restart services
docker-compose up -d
```