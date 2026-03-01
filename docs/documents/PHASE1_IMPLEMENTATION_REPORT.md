# NudgeAI Frontend Integration - Phase 1 Implementation Report

## Executive Summary

This document provides a comprehensive technical specification for integrating your NudgeAI backend MCP server with the React frontend. Phase 1 focuses on establishing robust API connections and creating a complete data display system that showcases all available backend capabilities.

## Current Architecture Analysis

### Backend Stack
- **MCP Server**: `mcp_server.py` - Hugging Face-powered AI assistant with WhiteCircle quality validation
- **API Bridge**: `mcp_api_bridge.py` - FastAPI server exposing MCP tools as HTTP endpoints on port 8003
- **Simple API Server**: `simple_api_server.py` - Basic API server running on port 8001 (currently used by frontend)
- **RAG System**: Vector database with semantic search capabilities
- **Data Sources**: Google Calendar, Drive, Location History, Fitness data

### Frontend Stack
- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router v6
- **HTTP Client**: Axios with interceptors (used by Dashboard, ToolsPanel)
- **Current Port**: 3000 (inconsistent proxy configuration)
- **Current State**: Fragmented API connections - DataDisplay.jsx bypasses proxy to connect directly to port 8003, while other components use axios utility that goes through proxy to port 8001

## Available Backend API Endpoints

### Core Data Endpoints

#### 1. Calendar Events (`/api/calendar`)
**Purpose**: Query calendar events with AI insights
**Parameters**:
- `start_date` (required): Start date in YYYY-MM-DD format
- `end_date` (required): End date in YYYY-MM-DD format  
- `event_type` (optional): Filter by event type (meeting, personal, etc.)

**Response Structure**:
```typescript
{
  success: boolean,
  data: {
    events: Array<{
      id: string,
      title: string,
      start_time: string,
      end_time: string,
      location: string,
      attendees: string[],
      description: string,
      similarity_score: number
    }>,
    insights: string,  // AI-generated insights from Hugging Face
    summary: string
  },
  timestamp: string
}
```

#### 2. Location History (`/api/location`)
**Purpose**: Query location history with pattern analysis
**Parameters**:
- `start_date` (required): Start date in YYYY-MM-DD format
- `end_date` (required): End date in YYYY-MM-DD format
- `location_type` (optional): Filter by location type (home, work, gym, etc.)

**Response Structure**:
```typescript
{
  success: boolean,
  data: {
    locations: Array<{
      id: string,
      timestamp: string,
      place: string,
      location_type: string,
      latitude: number,
      longitude: number,
      accuracy: number,
      similarity_score: number
    }>,
    insights: string,  // AI-generated insights about movement patterns
    summary: string
  },
  timestamp: string
}
```

#### 3. Semantic Search (`/api/semantic-search`)
**Purpose**: Universal search across all indexed data
**Parameters**:
- `query` (required): Natural language search query
- `data_filters` (optional): Comma-separated list of data types
- `max_results` (optional): Maximum results (1-20, default: 5)

**Response Structure**:
```typescript
{
  success: boolean,
  data: {
    query: string,
    results: Array<{
      id: string,
      text: string,
      metadata: object,
      similarity_score: number,
      source_type: string
    }>,
    total_found: number,
    filters_applied: string[]
  },
  timestamp: string
}
```

### AI Analysis Endpoints

#### 4. Habit Analysis (`/api/habits`)
**Purpose**: Analyze behavioral patterns and routines
**Parameters**:
- `time_period` (required): Time period (day, week, month)
- `focus_area` (optional): Specific focus area (exercise, productivity, sleep)

**Response Structure**:
```typescript
{
  success: boolean,
  data: {
    data: {
      period: string,
      focus_area: string,
      summary: string,
      metrics: {
        fitness_activities_count: number,
        calendar_events_count: number,
        location_visits_count: number,
        exercise_frequency: number,
        work_related_events: number
      }
    },
    analysis: string  // AI-generated analysis from Hugging Face
  },
  timestamp: string
}
```

#### 5. Personal Insights (`/api/insights`)
**Purpose**: Multi-source comprehensive insights
**Parameters**:
- `data_sources` (required): Comma-separated list of data sources
- `focus_areas` (required): Comma-separated list of focus areas

**Response Structure**:
```typescript
{
  success: boolean,
  data: {
    data_sources: object,  // Detailed data from each source
    synthesis: string,     // AI-generated cross-domain insights
    focus_areas: string[]
  },
  timestamp: string
}
```

#### 6. Daily Summary (`/api/daily-summary`)
**Purpose**: Comprehensive daily summary with AI enhancement
**Parameters**:
- `date` (optional): Date in YYYY-MM-DD format (defaults to current date)

**Response Structure**:
```typescript
{
  success: boolean,
  data: {
    date: string,
    summary: string,  // AI-enhanced daily summary
    details: {
      calendar: string,
      location: string,
      fitness: string
    },
    rating: number,  // Day rating 1-10
    recommendations: string[]
  },
  timestamp: string
}
```

#### 7. Weekly Insights (`/api/weekly-insights`)
**Purpose**: Weekly trend analysis and predictions
**Parameters**:
- `start_date` (optional): Week start date (YYYY-MM-DD format)

**Response Structure**:
```typescript
{
  success: boolean,
  data: {
    week_starting: string,
    insights: string,  // AI-generated weekly insights
    detailed_summary: {
      daily_summaries: object,
      weekly_insights: string,
      trends: string[]
    },
    recommendations: string[]
  },
  timestamp: string
}
```

### Specialized Endpoints

#### 8. Location-Based Nudges (`/api/location-nudge`)
**Purpose**: Real-time contextual suggestions
**Parameters**:
- `latitude` (required): Current latitude
- `longitude` (required): Current longitude

**Response Structure**:
```typescript
{
  success: boolean,
  data: {
    should_nudge: boolean,
    nudge_message: string,
    location_type: string,
    distance_to_location: number,
    coordinates: [number, number],
    conflicts: string[],
    actionable: boolean
  },
  timestamp: string
}
```

#### 9. Upcoming Events (`/api/upcoming-events`)
**Purpose**: Resource-based display of upcoming events
**Response Structure**:
```typescript
{
  success: boolean,
  data: string  // Formatted text display of events
}
```

#### 10. RAG Statistics (`/api/rag-stats`)
**Purpose**: System performance and statistics
**Response Structure**:
```typescript
{
  success: boolean,
  data: {
    total_documents: number,
    indexed_documents: number,
    total_chunks: number,
    index_size_mb: number,
    last_sync: string,
    performance_metrics: {
      search_latency_ms: number,
      indexing_speed: number
    }
  },
  timestamp: string
}
```

## Phase 1 Implementation Plan

### Step 1: Update API Configuration

#### 1.1 Update Vite Proxy Configuration
**File**: `frontend/vite.config.js`

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8003', // Updated from 8001 to 8003
        changeOrigin: true,
        secure: false,
        // Add error handling for better debugging
        onError: (err, req, res) => {
          console.error('Proxy error:', err);
        },
        onProxyReq: (proxyReq, req, res) => {
          console.log('Proxying request:', req.method, req.url);
        }
      }
    }
  }
})
```

#### 1.2 Enhanced API Utilities
**File**: `frontend/src/utils/api.js`

```javascript
import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

// Request interceptor with enhanced logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
    config.headers['Content-Type'] = 'application/json';
    
    // Add auth token if available
    const token = localStorage.getItem('mcp_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor with detailed error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Error:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      config: error.config
    });
    
    // Handle specific error cases
    if (error.response?.status === 401) {
      console.error('Unauthorized - token may be expired');
      localStorage.removeItem('mcp_token');
    } else if (error.response?.status === 500) {
      console.error('MCP server error:', error.response.data);
    } else if (error.code === 'ECONNABORTED') {
      console.error('Request timeout - server may be slow');
    } else if (error.code === 'ERR_NETWORK') {
      console.error('Network error - MCP server may be unreachable');
    }
    
    return Promise.reject(error);
  }
);

// Enhanced MCP API methods
export const mcpApi = {
  // Health check
  healthCheck: () => api.get('/test-connection'),
  
  // Calendar operations
  getCalendarEvents: (params = {}) => {
    return api.get('/calendar', { params });
  },
  
  // Location operations
  getLocationHistory: (params = {}) => {
    return api.get('/location', { params });
  },
  
  // Semantic search operations
  semanticSearch: (params = {}) => {
    return api.get('/semantic-search', { params });
  },
  
  // Habit analysis operations
  getHabits: (params = {}) => {
    return api.get('/habits', { params });
  },
  
  // Personal insights operations
  getInsights: (params = {}) => {
    return api.get('/insights', { params });
  },
  
  // Daily summary operations
  getDailySummary: (params = {}) => {
    return api.get('/daily-summary', { params });
  },
  
  // Weekly insights operations
  getWeeklyInsights: (params = {}) => {
    return api.get('/weekly-insights', { params });
  },
  
  // Location-based nudges
  getLocationNudge: (params = {}) => {
    return api.get('/location-nudge', { params });
  },
  
  // Upcoming events
  getUpcomingEvents: () => {
    return api.get('/upcoming-events');
  },
  
  // RAG statistics
  getRagStats: () => {
    return api.get('/rag-stats');
  },
  
  // Generic tool execution
  executeTool: async (toolName, params = {}) => {
    try {
      switch(toolName) {
        case 'query_calendar':
          return await mcpApi.getCalendarEvents(params);
        case 'query_location':
          return await mcpApi.getLocationHistory(params);
        case 'semantic_search':
          return await mcpApi.semanticSearch(params);
        case 'analyze_habits':
          return await mcpApi.getHabits(params);
        case 'get_insights':
          return await mcpApi.getInsights(params);
        case 'daily_summary':
          return await mcpApi.getDailySummary(params);
        case 'weekly_insights':
          return await mcpApi.getWeeklyInsights(params);
        case 'location_nudge':
          return await mcpApi.getLocationNudge(params);
        case 'upcoming_events':
          return await mcpApi.getUpcomingEvents();
        case 'rag_stats':
          return await mcpApi.getRagStats();
        default:
          throw new Error(`Unknown tool: ${toolName}`);
      }
    } catch (error) {
      console.error(`Error executing tool ${toolName}:`, error);
      throw error;
    }
  },
};

// Type definitions for better TypeScript support
export interface CalendarEvent {
  id: string;
  title: string;
  start_time: string;
  end_time: string;
  location: string;
  attendees: string[];
  description: string;
  similarity_score: number;
}

export interface LocationData {
  id: string;
  timestamp: string;
  place: string;
  location_type: string;
  latitude: number;
  longitude: number;
  accuracy: number;
  similarity_score: number;
}

export interface SearchResults {
  query: string;
  results: Array<{
    id: string;
    text: string;
    metadata: object;
    similarity_score: number;
    source_type: string;
  }>;
  total_found: number;
  filters_applied: string[];
}

export interface HabitAnalysis {
  period: string;
  focus_area: string;
  summary: string;
  metrics: {
    fitness_activities_count: number;
    calendar_events_count: number;
    location_visits_count: number;
    exercise_frequency: number;
    work_related_events: number;
  };
}

export interface DailySummary {
  date: string;
  summary: string;
  details: {
    calendar: string;
    location: string;
    fitness: string;
  };
  rating: number;
  recommendations: string[];
}

export default api;
```

### Step 2: Enhanced DataDisplay Component

**File**: `frontend/src/components/DataDisplay.jsx`

```jsx
import React, { useState, useEffect } from 'react';
import { mcpApi } from '../utils/api';
import './DataDisplay.css';

const DataDisplay = () => {
  const [data, setData] = useState({
    calendar: [],
    location: [],
    insights: null,
    summary: null,
    habits: null,
    searchResults: null
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    eventType: '',
    locationType: '',
    timePeriod: 'week',
    focusArea: '',
    searchQuery: ''
  });

  const fetchData = async (endpoint, params = {}) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await endpoint(params);
      
      if (!response.data.success) {
        throw new Error(response.data.error || 'API call failed');
      }
      
      return response.data.data;
    } catch (err) {
      console.error(`Error fetching data:`, err);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const loadData = async () => {
    try {
      // Fetch all data types in parallel
      const [
        calendarData,
        locationData,
        insightsData,
        summaryData,
        habitsData
      ] = await Promise.allSettled([
        fetchData(() => mcpApi.getCalendarEvents({
          start_date: filters.startDate,
          end_date: filters.endDate,
          event_type: filters.eventType
        })),
        fetchData(() => mcpApi.getLocationHistory({
          start_date: filters.startDate,
          end_date: filters.endDate,
          location_type: filters.locationType
        })),
        fetchData(() => mcpApi.getInsights({
          data_sources: 'calendar,location',
          focus_areas: 'productivity,health'
        })),
        fetchData(() => mcpApi.getDailySummary({
          date: filters.startDate || new Date().toISOString().split('T')[0]
        })),
        fetchData(() => mcpApi.getHabits({
          time_period: filters.timePeriod,
          focus_area: filters.focusArea
        }))
      ]);

      setData({
        calendar: calendarData.status === 'fulfilled' ? calendarData.value?.events || [] : [],
        location: locationData.status === 'fulfilled' ? locationData.value?.locations || [] : [],
        insights: insightsData.status === 'fulfilled' ? insightsData.value : null,
        summary: summaryData.status === 'fulfilled' ? summaryData.value : null,
        habits: habitsData.status === 'fulfilled' ? habitsData.value : null,
        searchResults: null
      });
    } catch (err) {
      setError(err.message);
    }
  };

  const handleSearch = async () => {
    if (!filters.searchQuery.trim()) return;
    
    try {
      const searchResults = await fetchData(() => mcpApi.semanticSearch({
        query: filters.searchQuery,
        data_filters: ['calendar', 'location', 'document'],
        max_results: 10
      }));
      
      setData(prev => ({ ...prev, searchResults }));
    } catch (err) {
      console.error('Search failed:', err);
    }
  };

  useEffect(() => {
    loadData();
  }, [filters]);

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return isNaN(date.getTime()) ? dateString : date.toLocaleString();
  };

  const formatDuration = (minutes) => {
    if (!minutes) return '0 min';
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  };

  return (
    <div className="data-display">
      {/* Filters Section */}
      <div className="filters-section">
        <h2>Data Filters & Controls</h2>
        <div className="filter-grid">
          <div className="filter-group">
            <label>Start Date</label>
            <input
              type="date"
              value={filters.startDate}
              onChange={(e) => setFilters({...filters, startDate: e.target.value})}
            />
          </div>
          <div className="filter-group">
            <label>End Date</label>
            <input
              type="date"
              value={filters.endDate}
              onChange={(e) => setFilters({...filters, endDate: e.target.value})}
            />
          </div>
          <div className="filter-group">
            <label>Event Type</label>
            <input
              type="text"
              placeholder="e.g., meeting, call"
              value={filters.eventType}
              onChange={(e) => setFilters({...filters, eventType: e.target.value})}
            />
          </div>
          <div className="filter-group">
            <label>Location Type</label>
            <input
              type="text"
              placeholder="e.g., home, work, gym"
              value={filters.locationType}
              onChange={(e) => setFilters({...filters, locationType: e.target.value})}
            />
          </div>
          <div className="filter-group">
            <label>Time Period</label>
            <select
              value={filters.timePeriod}
              onChange={(e) => setFilters({...filters, timePeriod: e.target.value})}
            >
              <option value="day">Day</option>
              <option value="week">Week</option>
              <option value="month">Month</option>
            </select>
          </div>
          <div className="filter-group">
            <label>Focus Area</label>
            <input
              type="text"
              placeholder="e.g., exercise, productivity"
              value={filters.focusArea}
              onChange={(e) => setFilters({...filters, focusArea: e.target.value})}
            />
          </div>
        </div>
        
        {/* Search Section */}
        <div className="search-section">
          <div className="search-group">
            <label>Semantic Search</label>
            <div className="search-input-group">
              <input
                type="text"
                placeholder="Search across all your data..."
                value={filters.searchQuery}
                onChange={(e) => setFilters({...filters, searchQuery: e.target.value})}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <button onClick={handleSearch} className="search-btn">
                Search
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Status Indicator */}
      <div className="status-section">
        <div className={`status-indicator ${loading ? 'loading' : 'ready'}`}>
          {loading ? 'Loading...' : 'Ready'}
        </div>
        {error && <div className="error-message">Error: {error}</div>}
      </div>

      {/* Data Grid */}
      <div className="data-grid">
        {/* Calendar Events */}
        <div className="data-card">
          <h3>📅 Calendar Events</h3>
          <div className="data-content">
            {loading ? (
              <div className="loading">Loading calendar data...</div>
            ) : data.calendar.length > 0 ? (
              data.calendar.map((event, index) => (
                <div key={index} className="data-item">
                  <div className="item-header">
                    <h4>{event.title}</h4>
                    <span className="similarity-score">Similarity: {event.similarity_score}</span>
                  </div>
                  <div className="item-details">
                    <div className="detail-row">
                      <span className="label">Time:</span>
                      <span className="value">{formatDate(event.start_time)} - {formatDate(event.end_time)}</span>
                    </div>
                    <div className="detail-row">
                      <span className="label">Location:</span>
                      <span className="value">{event.location}</span>
                    </div>
                    <div className="detail-row">
                      <span className="label">Attendees:</span>
                      <span className="value">{event.attendees?.join(', ') || 'N/A'}</span>
                    </div>
                    <div className="detail-row">
                      <span className="label">Description:</span>
                      <span className="value">{event.description}</span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-data">No calendar events found for the selected period.</div>
            )}
          </div>
        </div>

        {/* Location History */}
        <div className="data-card">
          <h3>📍 Location History</h3>
          <div className="data-content">
            {loading ? (
              <div className="loading">Loading location data...</div>
            ) : data.location.length > 0 ? (
              data.location.map((location, index) => (
                <div key={index} className="data-item">
                  <div className="item-header">
                    <h4>{location.place}</h4>
                    <span className="similarity-score">Similarity: {location.similarity_score}</span>
                  </div>
                  <div className="item-details">
                    <div className="detail-row">
                      <span className="label">Type:</span>
                      <span className="value">{location.location_type}</span>
                    </div>
                    <div className="detail-row">
                      <span className="label">Time:</span>
                      <span className="value">{formatDate(location.timestamp)}</span>
                    </div>
                    <div className="detail-row">
                      <span className="label">Coordinates:</span>
                      <span className="value">{location.latitude}, {location.longitude}</span>
                    </div>
                    <div className="detail-row">
                      <span className="label">Accuracy:</span>
                      <span className="value">{location.accuracy}m</span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-data">No location data found for the selected period.</div>
            )}
          </div>
        </div>

        {/* Insights */}
        <div className="data-card insights-card">
          <h3>💡 AI Insights</h3>
          <div className="data-content">
            {loading ? (
              <div className="loading">Generating insights...</div>
            ) : data.insights ? (
              <div className="insights-content">
                <div className="insight-item">
                  <h4>Pattern Analysis</h4>
                  <p>{data.insights.synthesis || 'Analyzing your data patterns...'}</p>
                </div>
                <div className="insight-item">
                  <h4>Recommendations</h4>
                  <p>{data.insights.recommendations || 'Generating personalized recommendations...'}</p>
                </div>
                <div className="insight-item">
                  <h4>Summary</h4>
                  <p>{data.insights.summary || 'Creating data summary...'}</p>
                </div>
              </div>
            ) : (
              <div className="no-data">No insights available yet. Try adjusting your filters.</div>
            )}
          </div>
        </div>

        {/* Daily Summary */}
        <div className="data-card summary-card">
          <h3>📊 Daily Summary</h3>
          <div className="data-content">
            {loading ? (
              <div className="loading">Generating summary...</div>
            ) : data.summary ? (
              <div className="summary-content">
                <div className="summary-item">
                  <h4>📅 Calendar</h4>
                  <p>{data.summary.details?.calendar || 'No calendar data'}</p>
                </div>
                <div className="summary-item">
                  <h4>📍 Location</h4>
                  <p>{data.summary.details?.location || 'No location data'}</p>
                </div>
                <div className="summary-item">
                  <h4>🏃 Fitness</h4>
                  <p>{data.summary.details?.fitness || 'No fitness data'}</p>
                </div>
                <div className="summary-item">
                  <h4>⭐ Rating</h4>
                  <p>{data.summary.rating || 'N/A'}/10</p>
                </div>
                <div className="summary-item">
                  <h4>🎯 Recommendations</h4>
                  <ul>
                    {data.summary.recommendations?.map((rec, index) => (
                      <li key={index}>{rec}</li>
                    )) || <li>No recommendations available</li>}
                  </ul>
                </div>
              </div>
            ) : (
              <div className="no-data">No summary available yet.</div>
            )}
          </div>
        </div>

        {/* Habit Analysis */}
        <div className="data-card habit-card">
          <h3>📈 Habit Analysis</h3>
          <div className="data-content">
            {loading ? (
              <div className="loading">Analyzing habits...</div>
            ) : data.habits ? (
              <div className="habit-content">
                <div className="habit-item">
                  <h4>📊 Metrics</h4>
                  <div className="metrics-grid">
                    <div className="metric">
                      <span className="metric-label">Fitness Activities</span>
                      <span className="metric-value">{data.habits.data?.metrics?.fitness_activities_count || 0}</span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Calendar Events</span>
                      <span className="metric-value">{data.habits.data?.metrics?.calendar_events_count || 0}</span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Location Visits</span>
                      <span className="metric-value">{data.habits.data?.metrics?.location_visits_count || 0}</span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Exercise Frequency</span>
                      <span className="metric-value">{data.habits.data?.metrics?.exercise_frequency || 0}</span>
                    </div>
                  </div>
                </div>
                <div className="habit-item">
                  <h4>🔍 Analysis</h4>
                  <p>{data.habits.analysis || 'Analyzing your habits...'}</p>
                </div>
              </div>
            ) : (
              <div className="no-data">No habit data available yet.</div>
            )}
          </div>
        </div>

        {/* Search Results */}
        {data.searchResults && (
          <div className="data-card search-card">
            <h3>🔍 Search Results</h3>
            <div className="data-content">
              <div className="search-info">
                <p><strong>Query:</strong> {data.searchResults.query}</p>
                <p><strong>Results:</strong> {data.searchResults.total_found}</p>
              </div>
              {data.searchResults.results.map((result, index) => (
                <div key={index} className="search-result-item">
                  <div className="result-header">
                    <span className="source-type">{result.source_type}</span>
                    <span className="similarity-score">Score: {result.similarity_score}</span>
                  </div>
                  <div className="result-content">
                    <p>{result.text}</p>
                  </div>
                  <div className="result-metadata">
                    <pre>{JSON.stringify(result.metadata, null, 2)}</pre>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="actions-section">
        <button onClick={loadData} disabled={loading} className="refresh-btn">
          {loading ? 'Refreshing...' : 'Refresh Data'}
        </button>
        <button onClick={() => setFilters({
          startDate: '',
          endDate: '',
          eventType: '',
          locationType: '',
          timePeriod: 'week',
          focusArea: '',
          searchQuery: ''
        })} className="clear-btn">
          Clear Filters
        </button>
        <button onClick={handleSearch} disabled={!filters.searchQuery.trim()} className="search-btn">
          Quick Search
        </button>
      </div>
    </div>
  );
};

export default DataDisplay;
```

### Step 3: Enhanced CSS Styling

**File**: `frontend/src/components/DataDisplay.css`

```css
.data-display {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

/* Filters Section */
.filters-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.filters-section h2 {
  margin: 0 0 1rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.filter-group input,
.filter-group select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.filter-group input:focus,
.filter-group select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Search Section */
.search-section {
  border-top: 1px solid #e5e7eb;
  padding-top: 1rem;
}

.search-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.search-input-group {
  display: flex;
  gap: 0.5rem;
}

.search-input-group input {
  flex: 1;
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
}

.search-btn {
  padding: 0.5rem 1rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.search-btn:hover {
  background-color: #2563eb;
}

.search-btn:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

/* Status Section */
.status-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.status-indicator {
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  font-weight: 500;
  font-size: 0.875rem;
}

.status-indicator.ready {
  background-color: #dcfce7;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.status-indicator.loading {
  background-color: #e0f2fe;
  color: #0369a1;
  border: 1px solid #b3e5fc;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.error-message {
  color: #dc2626;
  font-size: 0.875rem;
  font-weight: 500;
}

/* Data Grid */
.data-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.data-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.data-card h3 {
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
}

.data-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Data Items */
.data-item {
  background: #f9fafb;
  border-radius: 8px;
  padding: 1rem;
  border-left: 4px solid #3b82f6;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.item-header h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

.similarity-score {
  font-size: 0.75rem;
  color: #6b7280;
  background: #e5e7eb;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
  font-weight: 500;
}

.item-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
}

.detail-row .label {
  color: #6b7280;
  font-weight: 500;
}

.detail-row .value {
  color: #1f2937;
  font-weight: 400;
}

/* Special Card Styles */
.insights-card {
  grid-column: span 2;
}

.summary-card {
  grid-column: span 2;
}

.habit-card {
  grid-column: span 2;
}

.search-card {
  grid-column: span 2;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-top: 1rem;
}

.metric {
  background: #f3f4f6;
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
}

.metric-label {
  display: block;
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.metric-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
}

/* Content Sections */
.insights-content,
.summary-content,
.habit-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.insight-item,
.summary-item,
.habit-item {
  background: #f9fafb;
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid #10b981;
}

.insight-item h4,
.summary-item h4,
.habit-item h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

.insight-item p,
.summary-item p,
.habit-item p {
  margin: 0;
  color: #374151;
  line-height: 1.5;
}

.summary-item ul {
  margin: 0.5rem 0 0 1rem;
  padding: 0;
}

.summary-item li {
  color: #374151;
  margin-bottom: 0.25rem;
}

/* Search Results */
.search-info {
  background: #f3f4f6;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.search-info p {
  margin: 0.25rem 0;
  font-size: 0.875rem;
  color: #374151;
}

.search-result-item {
  background: #f9fafb;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  border-left: 4px solid #8b5cf6;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.source-type {
  font-size: 0.75rem;
  color: #6b7280;
  background: #e5e7eb;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
  font-weight: 500;
}

.result-content {
  margin-bottom: 1rem;
}

.result-content p {
  margin: 0;
  color: #374151;
  line-height: 1.5;
}

.result-metadata {
  background: #1f2937;
  color: #f9fafb;
  padding: 1rem;
  border-radius: 6px;
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
}

.result-metadata pre {
  margin: 0;
  overflow-x: auto;
}

/* Actions Section */
.actions-section {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  justify-content: center;
}

.refresh-btn,
.clear-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #d1d5db;
}

.refresh-btn {
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.refresh-btn:hover:not(:disabled) {
  background-color: #2563eb;
  border-color: #2563eb;
}

.refresh-btn:disabled {
  background-color: #9ca3af;
  border-color: #9ca3af;
  cursor: not-allowed;
}

.clear-btn {
  background-color: white;
  color: #374151;
}

.clear-btn:hover {
  background-color: #f3f4f6;
  border-color: #9ca3af;
}

/* Loading and No Data States */
.loading {
  text-align: center;
  color: #6b7280;
  font-size: 0.875rem;
  padding: 2rem;
}

.no-data {
  text-align: center;
  color: #9ca3af;
  font-size: 0.875rem;
  padding: 2rem;
  border: 2px dashed #e5e7eb;
  border-radius: 8px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .data-display {
    padding: 1rem;
  }
  
  .data-grid {
    grid-template-columns: 1fr;
  }
  
  .insights-card,
  .summary-card,
  .habit-card,
  .search-card {
    grid-column: span 1;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
```

### Step 4: Enhanced App Component

**File**: `frontend/src/App.jsx`

```jsx
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import ToolsPanel from './pages/ToolsPanel';
import DataVisualization from './pages/DataVisualization';
import DataDisplay from './components/DataDisplay';
import Header from './components/Header';
import Sidebar from './components/Sidebar';

function App() {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/tools" element={<ToolsPanel />} />
            <Route path="/data" element={<DataVisualization />} />
            <Route path="/display" element={<DataDisplay />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;
```

### Step 5: Enhanced Dashboard Component

**File**: `frontend/src/pages/Dashboard.jsx`

```jsx
import React, { useState, useEffect } from 'react';
import { mcpApi } from '../utils/api';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState({
    calendarEvents: [],
    locationHistory: [],
    insights: null,
    summary: null,
    habits: null,
    systemStatus: 'loading'
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch real data from the NudgeAI backend API
      const [calendarResponse, locationResponse, insightsResponse, summaryResponse, habitsResponse] = await Promise.allSettled([
        mcpApi.getCalendarEvents({
          start_date: new Date().toISOString().split('T')[0],
          end_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
        }),
        mcpApi.getLocationHistory({
          start_date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          end_date: new Date().toISOString().split('T')[0]
        }),
        mcpApi.getInsights({
          data_sources: 'calendar,location',
          focus_areas: 'productivity,health'
        }),
        mcpApi.getDailySummary(),
        mcpApi.getHabits({ time_period: 'week' })
      ]);

      const newData = {
        calendarEvents: [],
        locationHistory: [],
        insights: null,
        summary: null,
        habits: null,
        systemStatus: 'connected'
      };

      // Process calendar events
      if (calendarResponse.status === 'fulfilled') {
        const events = calendarResponse.value.data?.events || [];
        newData.calendarEvents = events.map((event, index) => ({
          id: event.id || index + 1,
          title: event.title || event.summary || 'Event',
          time: event.start_time || 'N/A',
          type: event.type || 'event'
        }));
      }

      // Process location history
      if (locationResponse.status === 'fulfilled') {
        const locations = locationResponse.value.data?.locations || [];
        newData.locationHistory = locations.map((loc, index) => ({
          id: loc.id || index + 1,
          place: loc.place || loc.address || 'Unknown Location',
          time: loc.time || loc.timestamp || 'N/A',
          duration: loc.duration || 'N/A'
        }));
      }

      // Process insights
      if (insightsResponse.status === 'fulfilled') {
        newData.insights = insightsResponse.value.data;
      }

      // Process summary
      if (summaryResponse.status === 'fulfilled') {
        newData.summary = summaryResponse.value.data;
      }

      // Process habits
      if (habitsResponse.status === 'fulfilled') {
        newData.habits = habitsResponse.value.data;
      }

      setDashboardData(newData);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError(error.message);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <span className="text-2xl">📅</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Upcoming Events</p>
              <p className="text-2xl font-semibold text-gray-900">{dashboardData.calendarEvents.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <span className="text-2xl">📍</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Recent Locations</p>
              <p className="text-2xl font-semibold text-gray-900">{dashboardData.locationHistory.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <span className="text-2xl">💡</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">AI Insights</p>
              <p className="text-2xl font-semibold text-gray-900">{dashboardData.insights ? 'Available' : 'Processing'}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 rounded-lg">
              <span className="text-2xl">📊</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Daily Summary</p>
              <p className="text-2xl font-semibold text-gray-900">{dashboardData.summary ? 'Ready' : 'Generating'}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <p className="text-red-600 font-medium">Connection Error</p>
            <button 
              onClick={fetchDashboardData}
              className="text-red-600 hover:text-red-700 font-medium"
            >
              Retry
            </button>
          </div>
          <p className="text-red-500 text-sm mt-1">{error}</p>
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Calendar Events */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Upcoming Calendar Events</h3>
          <div className="space-y-3">
            {dashboardData.calendarEvents.length > 0 ? (
              dashboardData.calendarEvents.map(event => (
                <div key={event.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{event.title}</p>
                    <p className="text-sm text-gray-500">{event.time}</p>
                  </div>
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full capitalize">
                    {event.type}
                  </span>
                </div>
              ))
            ) : (
              <div className="text-center text-gray-500 py-4">
                No upcoming events found
              </div>
            )}
          </div>
        </div>

        {/* Location History */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Location History</h3>
          <div className="space-y-3">
            {dashboardData.locationHistory.length > 0 ? (
              dashboardData.locationHistory.map(loc => (
                <div key={loc.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{loc.place}</p>
                    <p className="text-sm text-gray-500">{loc.time}</p>
                  </div>
                  <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
                    {loc.duration}
                  </span>
                </div>
              ))
            ) : (
              <div className="text-center text-gray-500 py-4">
                No location data found
              </div>
            )}
          </div>
        </div>

        {/* AI Insights */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 lg:col-span-2">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Insights</h3>
          {dashboardData.insights ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-semibold text-blue-900 mb-2">Pattern Analysis</h4>
                <p className="text-blue-800 text-sm">{dashboardData.insights.synthesis || 'Analyzing patterns...'}</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="font-semibold text-green-900 mb-2">Recommendations</h4>
                <p className="text-green-800 text-sm">{dashboardData.insights.recommendations || 'Generating recommendations...'}</p>
              </div>
              <div className="bg-orange-50 p-4 rounded-lg">
                <h4 className="font-semibold text-orange-900 mb-2">Summary</h4>
                <p className="text-orange-800 text-sm">{dashboardData.insights.summary || 'Creating summary...'}</p>
              </div>
            </div>
          ) : (
            <div className="text-center text-gray-500 py-8">
              AI insights are being generated...
            </div>
          )}
        </div>

        {/* Daily Summary */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 lg:col-span-2">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Summary</h3>
          {dashboardData.summary ? (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-semibold text-blue-900 mb-2">Calendar</h4>
                <p className="text-blue-800 text-sm">{dashboardData.summary.details?.calendar || 'No data'}</p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <h4 className="font-semibold text-purple-900 mb-2">Location</h4>
                <p className="text-purple-800 text-sm">{dashboardData.summary.details?.location || 'No data'}</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="font-semibold text-green-900 mb-2">Fitness</h4>
                <p className="text-green-800 text-sm">{dashboardData.summary.details?.fitness || 'No data'}</p>
              </div>
              <div className="bg-orange-50 p-4 rounded-lg">
                <h4 className="font-semibold text-orange-900 mb-2">Rating</h4>
                <p className="text-orange-800 text-sm">{dashboardData.summary.rating || 'N/A'}/10</p>
              </div>
            </div>
          ) : (
            <div className="text-center text-gray-500 py-8">
              Daily summary is being generated...
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
```

## Implementation Checklist

### Phase 1: Core Integration (Priority: High)

- [ ] **Update Vite Configuration**
  - Change proxy target from port 8001 to 8003
  - Add enhanced error handling and logging

- [ ] **Enhance API Utilities**
  - Add all MCP endpoint methods
  - Implement proper error handling
  - Add TypeScript interfaces
  - Create generic tool execution method

- [ ] **Update DataDisplay Component**
  - Integrate with MCP API endpoints
  - Add semantic search functionality
  - Implement habit analysis display
  - Add proper loading states and error handling

- [ ] **Enhance Dashboard Component**
  - Connect to real MCP data sources
  - Display AI insights and summaries
  - Add error handling and retry mechanisms
  - Show system status indicators

- [ ] **Update CSS Styling**
  - Create responsive design
  - Add proper loading states
  - Style search results and insights
  - Ensure accessibility compliance

### Phase 2: Advanced Features (Priority: Medium)

- [ ] **Real-time Updates**
  - Implement WebSocket connections
  - Add data polling for live updates
  - Create notification system

- [ ] **Advanced Visualizations**
  - Chart.js integration for data charts
  - Map integration for location data
  - Timeline views for calendar events

- [ ] **Search Interface**
  - Advanced semantic search UI
  - Filter and sort capabilities
  - Search history and favorites

### Phase 3: Polish & Optimization (Priority: Low)

- [ ] **Performance Optimization**
  - Implement data caching
  - Add virtualization for long lists
  - Optimize image loading

- [ ] **Accessibility**
  - Screen reader support
  - Keyboard navigation
  - Color contrast compliance

- [ ] **Mobile Optimization**
  - Touch-friendly interface
  - Responsive design improvements
  - Mobile-specific features

## Testing Strategy

### Unit Tests
- API utility functions
- Component rendering
- Data transformation logic

### Integration Tests
- End-to-end API calls
- Error handling scenarios
- Data flow validation

### Manual Testing
- Cross-browser compatibility
- Mobile responsiveness
- Performance testing

## Deployment Considerations

### Development Environment
- Local MCP server on port 8003
- Frontend on port 3000 with proxy
- CORS configuration for local development

### Production Environment
- Docker containerization
- Environment variable management
- SSL/TLS configuration
- Load balancing considerations

## Next Steps

1. **Start with Phase 1 implementation** - Focus on core API integration
2. **Test each component individually** - Ensure API connections work
3. **Gradual rollout** - Implement features incrementally
4. **Monitor performance** - Track API response times and user experience

This comprehensive implementation plan provides a solid foundation for integrating your NudgeAI backend with a modern, responsive frontend that showcases all the powerful AI capabilities of your MCP server.