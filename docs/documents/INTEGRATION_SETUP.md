# NudgeAI Frontend Integration Guide

## Server Architecture

NudgeAI has two backend servers:
- `mcp_server.py` - MCP Protocol server (not HTTP)
- `simple_api_server.py` - FastAPI bridge server (HTTP on port 8001) - **This is what the frontend connects to**

## Frontend Configuration

The frontend is correctly configured with:
- Vite proxy to forward `/api` requests to `http://localhost:8001`
- API endpoints that match the simple API server
- Proper TypeScript interfaces for data structures

## Setup Instructions

### 1. Start the Simple API Server
```bash
cd /home/lade/Hackathons/Mistral/Final/nudgeai
source venv/bin/activate
python simple_api_server.py
```

The server will run on `http://localhost:8001`

### 2. Start the Frontend Development Server
```bash
cd /home/lade/Hackathons/Mistral/Final/nudgeai/frontend
npm install  # If you haven't installed dependencies yet
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 3. Alternative: Use the Combined Startup Script
```bash
chmod +x start_servers.sh
./start_servers.sh
```

This will start both servers simultaneously.

## API Endpoints Used by Frontend

The frontend connects to these endpoints via the Vite proxy:

- `GET /api/mcp/tools/query_calendar` - Get calendar events
- `GET /api/mcp/tools/query_drive` - Search documents
- `GET /api/mcp/tools/query_location` - Get location history
- `GET /api/mcp/tools/query_fit` - Get health/fitness data
- `POST /api/mcp/tools/proactive-nudge` - RAG search

These endpoints are mapped to the simple API server running on port 8001.

## Expected Data Format

The backend returns data in this format:
```json
{
  "result": {
    "events": [...],
    "documents": [...],
    "locations": [...],
    "health": {...}
  }
}
```

The frontend is already configured to handle this nested structure.

## Troubleshooting

1. **If frontend shows mock data instead of real data:**
   - Verify that `simple_api_server.py` is running on port 8001
   - Check browser network tab for failed API requests
   - Look at the console for error messages

2. **If API requests are failing:**
   - Confirm that the proxy in `vite.config.js` points to port 8001
   - Check that CORS is properly configured in the simple API server
   - Verify the backend endpoints match the frontend calls

3. **To test API directly:**
   - Visit `http://localhost:8001/api/mcp/tools/query_calendar` in your browser
   - All endpoints should return JSON data

## Mock Data File

A sample response file is provided at `mock_response.json` that matches the expected backend format. This can be used for testing when the backend server is unavailable.