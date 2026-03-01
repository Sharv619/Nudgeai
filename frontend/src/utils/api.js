import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api', // Will be proxied to MCP API bridge via Vite
  timeout: 30000, // 30 second timeout,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any request headers here
    config.headers['Content-Type'] = 'application/json';
    // Add auth token if available
    const token = localStorage.getItem('mcp_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle specific error cases
    if (error.response?.status === 401) {
      // Unauthorized - maybe redirect to login
      console.error('Unauthorized access - token may be expired');
    } else if (error.response?.status === 500) {
      // Server error
      console.error('MCP server error:', error.response.data);
    } else if (error.code === 'ECONNABORTED' || error.code === 'ERR_NETWORK') {
      // Network error
      console.error('Network error - MCP server may be unreachable');
    }
    return Promise.reject(error);
  }
);

// NudgeAI Backend API methods - connect to the backend data API server
export const mcpApi = {
  // Health check
  healthCheck: () => api.get('/health'),
  
  // Calendar operations - fetch real data from backend API
  getCalendarEvents: async (params = {}) => {
    try {
      // Format date parameters if provided
      const formattedParams = { ...params };
      if (params.start_date) {
        formattedParams.start_date = new Date(params.start_date).toISOString();
      }
      if (params.end_date) {
        formattedParams.end_date = new Date(params.end_date).toISOString();
      }
      
      const response = await api.get('/mcp/tools/query_calendar', { params: formattedParams });
      return response;
    } catch (error) {
      console.error('Error fetching calendar events:', error);
      // Fallback to mock data if API fails
      return { data: mockData.calendarEvents };
    }
  },
  
  // Document operations - fetch real data from backend API
  searchDocuments: async (params = {}) => {
    try {
      const response = await api.get('/mcp/tools/query_drive', { params });
      return response;
    } catch (error) {
      console.error('Error searching documents:', error);
      return { data: mockData.documents };
    }
  },
  
  // Location operations - fetch real data from backend API
  getLocationHistory: async (params = {}) => {
    try {
      const response = await api.get('/mcp/tools/query_location', { params });
      return response;
    } catch (error) {
      console.error('Error fetching location history:', error);
      return { data: mockData.locationHistory };
    }
  },
  
  // Health/Fitness operations - fetch real data from backend API
  getHealthData: async (params = {}) => {
    try {
      const response = await api.get('/mcp/tools/query_fit', { params });
      return response;
    } catch (error) {
      console.error('Error fetching health data:', error);
      return { data: mockData.healthData };
    }
  },
  
  // RAG search - using real RAG system
  ragSearch: async (context) => {
    try {
      const response = await api.get('/mcp/tools/query_calendar', { params: { context } });
      return response;
    } catch (error) {
      console.error('Error in RAG search:', error);
      return { data: { context, results: [] } };
    }
  },
  
  // New: Direct JSON data fetching for calendar events (using correct endpoint)
  fetchCalendarEvents: async (startDate, endDate, eventType = null) => {
    try {
      const response = await api.get('/mcp/tools/query_calendar', {
        params: {
          start_date: startDate,
          end_date: endDate,
          event_type: eventType
        }
      });
      return response;
    } catch (error) {
      console.error('Error fetching calendar events via MCP:', error);
      return { data: { events: [], insights: 'No data available', summary: 'No events found' } };
    }
  },
  
  // New: Direct JSON data fetching for location history (using correct endpoint)
  fetchLocationHistory: async (startDate, endDate, locationType = null) => {
    try {
      const response = await api.get('/mcp/tools/query_location', {
        params: {
          start_date: startDate,
          end_date: endDate,
          location_type: locationType
        }
      });
      return response;
    } catch (error) {
      console.error('Error fetching location history via MCP:', error);
      return { data: { locations: [], insights: 'No data available', summary: 'No locations found' } };
    }
  },
  
  // New: Direct JSON data fetching for fitness data (using correct endpoint)
  fetchFitnessData: async (timePeriod = 'week', focusArea = null) => {
    try {
      const response = await api.get('/mcp/tools/query_fit', {
        params: {
          time_period: timePeriod,
          focus_area: focusArea
        }
      });
      return response;
    } catch (error) {
      console.error('Error fetching fitness data via MCP:', error);
      return { data: { data: {}, analysis: 'No data available' } };
    }
  },
  
  // New: Semantic search across all data (using correct endpoint)
  semanticSearch: async (query, dataFilters = null, maxResults = 5) => {
    try {
      const response = await api.get('/mcp/tools/query_calendar', {
        params: {
          query: query,
          data_filters: dataFilters ? dataFilters.join(',') : null,
          max_results: maxResults
        }
      });
      return response;
    } catch (error) {
      console.error('Error in semantic search:', error);
      return { data: { query, results: [], total_found: 0, filters_applied: [] } };
    }
  },
  
  // Generic tool execution - map to backend API endpoints
  executeTool: async (toolName, params = {}) => {
    try {
      switch(toolName) {
        case 'query_calendar':
          return await mcpApi.fetchCalendarEvents(
            params.start_date || new Date().toISOString().split('T')[0],
            params.end_date || new Date().toISOString().split('T')[0],
            params.event_type || null
          );
        case 'query_drive':
          return await mcpApi.searchDocuments(params);
        case 'query_location':
          return await mcpApi.fetchLocationHistory(
            params.start_date || new Date().toISOString().split('T')[0],
            params.end_date || new Date().toISOString().split('T')[0],
            params.location_type || null
          );
        case 'query_fit':
          return await mcpApi.fetchFitnessData(
            params.time_period || 'week',
            params.focus_area || null
          );
        case 'semantic_search':
          // Handle semantic search
          const queryParams = {
            query: params.query || '',
            k: params.k || 5
          };
          return await api.get('/mcp/tools/semantic_search', { params: queryParams });
        case 'ask_question':
          // Handle general questions using semantic search
          const questionParams = {
            question: params.question || ''
          };
          return await api.get('/api/ask-question', { params: questionParams });
        case 'proactive-nudge':
          return await mcpApi.ragSearch(params.context || '');
        case 'get_insights':
          return await api.get('/insights', { 
            params: { 
              data_sources: params.data_sources || 'calendar,location',
              focus_areas: params.focus_areas || 'productivity,health'
            } 
          });
        case 'generate_daily_summary':
          return await api.get('/daily-summary', { 
            params: { 
              date: params.date || new Date().toISOString().split('T')[0]
            } 
          });
        case 'query_daily_summary':
          return await api.get('/daily-summary', { 
            params: { 
              date: params.date || new Date().toISOString().split('T')[0]
            } 
          });
        case 'query_insights':
          return await api.get('/insights', { 
            params: { 
              data_sources: Array.isArray(params.data_sources) ? params.data_sources.join(',') : params.data_sources || 'calendar,location',
              focus_areas: Array.isArray(params.focus_areas) ? params.focus_areas.join(',') : params.focus_areas || 'productivity,health'
            } 
          });
        case 'query_habits':
          return await api.get('/habits', { 
            params: { 
              time_period: params.time_period || 'week',
              focus_area: params.focus_area || ''
            } 
          });
        default:
          throw new Error(`Unknown tool: ${toolName}`);
      }
    } catch (error) {
      console.error(`Error executing tool ${toolName}:`, error);
      throw error;
    }
  },
  
  // Get available tools
  getAvailableTools: () => {
    // For now, return a static list of tools
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

// Mock data for fallback when backend API is not available
export const mockData = {
  calendarEvents: [
    { id: 1, title: 'Mistral Worldwide Hackathon - Sydney edition', start: '2026-02-28T09:00:00+11:00', type: 'event' },
    { id: 2, title: 'WAKE UP LIST', start: '2026-03-01T09:00:00+11:00', type: 'reminder' },
    { id: 3, title: 'Meeting with Manoj', start: '2026-03-02T22:00:00+11:00', type: 'meeting' },
    { id: 4, title: 'Room inspection with Bish', start: '2026-03-02T20:00:00+11:00', type: 'meeting' },
    { id: 5, title: 'Research about Next by 360', start: '2026-03-01T18:00:00+11:00', type: 'task' },
    { id: 6, title: 'Atlassian Takeover 2026', start: '2026-03-03T18:00:00+11:00', type: 'event' }
  ],
  
  documents: [
    { id: 1, name: 'Marketing Budget 2024.xlsx', modified: '2026-02-27T14:30:00', type: 'spreadsheet' },
    { id: 2, name: 'Project Plan.docx', modified: '2026-02-26T10:15:00', type: 'document' },
    { id: 3, name: 'Meeting Notes.pdf', modified: '2026-02-25T16:45:00', type: 'document' },
    { id: 4, name: 'Research Paper.doc', modified: '2026-02-24T11:20:00', type: 'document' }
  ],
  
  locationHistory: [
    { id: 1, place: 'Home', time: '2026-02-28T08:00:00', type: 'home', duration: '16h' },
    { id: 2, place: 'Office', time: '2026-02-28T09:00:00', type: 'work', duration: '9h' },
    { id: 3, place: 'Gym', time: '2026-02-28T18:30:00', type: 'exercise', duration: '1h' },
    { id: 4, place: 'Coffee Shop', time: '2026-02-27T15:00:00', type: 'social', duration: '30m' },
    { id: 5, place: 'Park', time: '2026-02-27T07:30:00', type: 'exercise', duration: '1h' }
  ],
  
  healthData: {
    stepsToday: 8547,
    caloriesBurned: 2100,
    activeMinutes: 65,
    heartRateAvg: 72,
    weeklySteps: [7200, 8547, 6800, 9200, 7800, 8100, 7500],
    weeklyCalories: [1900, 2100, 1800, 2300, 2000, 2150, 1950]
  }
};

// Utility function - now always tries real API by default
export const useMockData = () => {
  return process.env.REACT_APP_USE_MOCK_DATA === 'true';
};

export default api;