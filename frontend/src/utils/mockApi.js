import mockResponse from '../mocks/mock_response.json';

/**
 * Mock API utility for testing frontend when backend server is offline
 * This provides the same interface as the real API but returns mock data
 */

export const mockApi = {
  // Health check
  healthCheck: () => Promise.resolve({ data: { status: 'healthy' } }),
  
  // Calendar operations - return mock data
  getCalendarEvents: async (params = {}) => {
    return Promise.resolve(mockResponse.calendarResponse);
  },
  
  // Document operations - return mock data
  searchDocuments: async (query = "") => {
    return Promise.resolve(mockResponse.documentResponse);
  },
  
  // Location operations - return mock data
  getLocationHistory: async (params = {}) => {
    return Promise.resolve(mockResponse.locationResponse);
  },
  
  // Health/Fitness operations - return mock data
  getHealthData: async (params = {}) => {
    return Promise.resolve(mockResponse.healthResponse);
  },
  
  // RAG search - return mock data
  ragSearch: async (context) => {
    return Promise.resolve({ 
      data: { 
        context, 
        results: mockResponse.calendarResponse.result.events.slice(0, 3) 
      } 
    });
  },
  
  // Generic tool execution - map to mock responses
  executeTool: async (toolName, params = {}) => {
    switch(toolName) {
      case 'query_calendar':
        return await mockApi.getCalendarEvents(params);
      case 'query_drive':
        return await mockApi.searchDocuments(params.query || '');
      case 'query_location':
        return await mockApi.getLocationHistory(params);
      case 'query_fit':
        return await mockApi.getHealthData(params);
      case 'proactive-nudge':
        return await mockApi.ragSearch(params.context || '');
      default:
        throw new Error(`Unknown tool: ${toolName}`);
    }
  },
  
  // Get available tools
  getAvailableTools: () => {
    return Promise.resolve({
      data: [
        { name: 'query_calendar', description: 'Query calendar events' },
        { name: 'query_drive', description: 'Search Google Drive documents' },
        { name: 'query_location', description: 'Get location history' },
        { name: 'query_fit', description: 'Get fitness data' },
        { name: 'proactive-nudge', description: 'Get proactive nudges' }
      ]
    });
  },
};

// Utility to check if backend is available and switch between real and mock API
export const createApiInstance = () => {
  // Try to make a simple health check to see if backend is available
  return fetch('/api/health')
    .then(response => {
      if (response.ok) {
        // Backend is available, use real API
        return import('./api').then(module => module.mcpApi);
      } else {
        // Backend is not available, use mock API
        return mockApi;
      }
    })
    .catch(() => {
      // Network error, use mock API
      return mockApi;
    });
};