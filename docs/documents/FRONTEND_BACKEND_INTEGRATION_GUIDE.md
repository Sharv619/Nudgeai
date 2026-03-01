# NudgeAI Frontend-Backend Integration Guide

## Overview

This guide explains how the NudgeAI frontend and backend are integrated, including the data flow, API structure, and how to use mock data for testing.

## Architecture

### Backend Servers

1. **MCP Server** (`mcp_server.py`)
   - Uses Model Context Protocol (MCP) - not HTTP
   - Provides advanced AI capabilities with Hugging Face integration
   - Runs on MCP protocol, requires special client

2. **Simple API Server** (`simple_api_server.py`)
   - FastAPI HTTP server running on port 8001
   - Acts as a bridge between HTTP frontend and MCP data
   - Provides REST endpoints for frontend consumption

### Frontend

- React/Vite application running on port 3000
- Uses Vite proxy to forward `/api` requests to `http://localhost:8001`
- TypeScript interfaces for type safety
- Mock API utility for offline development

## Data Flow

```
Frontend (port 3000) 
    ↓ (HTTP via Vite proxy)
Simple API Server (port 8001)
    ↓ (Data access)
Backend Data Sources
    ↓ (Response)
Simple API Server
    ↓ (HTTP response)
Frontend
```

## API Endpoints

### Available Endpoints

- `GET /api/mcp/tools/query_calendar` - Calendar events
- `GET /api/mcp/tools/query_drive` - Google Drive documents  
- `GET /api/mcp/tools/query_location` - Location history
- `GET /api/mcp/tools/query_fit` - Health/fitness data

### Data Format

All endpoints return data in the following format:

```json
{
  "result": {
    "events": [...],
    "documents": [...],
    "locations": [...],
    "health": {...},
    "insights": "...",
    "summary": "..."
  }
}
```

## TypeScript Interfaces

The frontend includes comprehensive TypeScript interfaces in `frontend/src/types/index.ts`:

- `CalendarEvent` - Calendar event data structure
- `Document` - Document metadata structure
- `Location` - Location history structure
- `HealthData` - Health and fitness data
- `DashboardData` - Combined dashboard state

## Using Mock Data

### When to Use Mock Data

Use mock data when:
- Backend servers are not running
- Testing frontend components in isolation
- Demonstrating the application without real data

### Mock Data Files

1. **`frontend/src/mocks/mock_response.json`**
   - Contains realistic mock data matching backend schema
   - Includes calendar events, documents, location history, and health data
   - Perfect for testing frontend components

2. **`frontend/src/utils/mockApi.js`**
   - Provides mock API utility with same interface as real API
   - Automatically switches between real and mock API based on backend availability
   - Can be used for offline development

### Using Mock API

```javascript
import { mockApi } from './utils/mockApi';

// Use mock API directly
const calendarData = await mockApi.getCalendarEvents();

// Or use the smart API that switches based on backend availability
import { createApiInstance } from './utils/mockApi';

const api = await createApiInstance();
const calendarData = await api.getCalendarEvents();
```

## Running the Application

### Option 1: Manual Start

```bash
# Terminal 1 - Start the Simple API Server
cd /home/lade/Hackathons/Mistral/Final/nudgeai
source venv/bin/activate
python simple_api_server.py

# Terminal 2 - Start the Frontend
cd /home/lade/Hackathons/Mistral/Final/nudgeai/frontend
npm install  # Only first time
npm run dev
```

### Option 2: Use the Combined Script

```bash
cd /home/lade/Hackathons/Mistral/Final/nudgeai
./start_servers.sh
```

## URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **Health check**: http://localhost:8001/health

## Troubleshooting

### Common Issues

1. **"Connection refused" errors**
   - Ensure the Simple API Server is running on port 8001
   - Check that the frontend proxy is correctly configured

2. **Mock data not loading**
   - Verify `frontend/src/mocks/mock_response.json` exists
   - Check that the mock API utility is properly imported

3. **TypeScript errors**
   - Ensure all TypeScript interfaces are properly imported
   - Check that the data structure matches the interfaces

### Debugging API Calls

1. **Check backend status**:
   ```bash
   curl http://localhost:8001/health
   ```

2. **Test API endpoints**:
   ```bash
   curl http://localhost:8001/api/mcp/tools/query_calendar
   ```

3. **Check frontend console** for API errors and network requests

### Vite Proxy Configuration

The frontend uses Vite proxy to forward API requests:

```javascript
// frontend/vite.config.js
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
    },
  },
})
```

## Testing with Mock Data

### 1. Stop Backend Servers

```bash
# Stop the Simple API Server if running
# (Ctrl+C in the terminal where it's running)
```

### 2. Update Dashboard to Use Mock API

```javascript
// In frontend/src/pages/Dashboard.jsx
import { mockApi } from '../utils/mockApi';

// Replace mcpApi with mockApi in fetchDashboardData
const [calendarResponse, documentsResponse, locationResponse, healthResponse] = await Promise.allSettled([
  mockApi.getCalendarEvents(),
  mockApi.searchDocuments(),
  mockApi.getLocationHistory(),
  mockApi.getHealthData()
]);
```

### 3. Test the Application

The frontend should now load with mock data instead of real backend data.

## Integration Testing

### Test Script

A test script is available to verify all components work together:

```bash
# Run the integration test
cd /home/lade/Hackathons/Mistral/Final/nudgeai
python test_integration.py
```

This script:
- Starts the Simple API Server
- Tests all API endpoints
- Verifies data format consistency
- Confirms frontend-backend communication

## Data Schema Validation

The mock data in `mock_response.json` exactly matches the real backend schema:

- Calendar events include all required fields (id, summary, start_time, type, description, location)
- Documents include proper metadata (id, title, url, modified, type)
- Location data includes coordinates and timestamps
- Health data includes steps, calories, active minutes, and recent activities

This ensures that frontend components work identically with both real and mock data.

## Best Practices

1. **Always use TypeScript interfaces** for type safety
2. **Handle API failures gracefully** with fallback mock data
3. **Test with both real and mock data** to ensure compatibility
4. **Use the mock API utility** for offline development
5. **Verify data format consistency** between backend and frontend

## Conclusion

The NudgeAI frontend-backend integration is designed to be robust and developer-friendly. With proper TypeScript interfaces, comprehensive mock data, and clear documentation, you can easily develop and test the application with or without the backend servers running.