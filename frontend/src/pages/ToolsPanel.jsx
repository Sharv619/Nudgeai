import React, { useState, useEffect } from 'react';
import { mcpApi } from '../utils/api';

const ToolsPanel = () => {
  const [activeTool, setActiveTool] = useState('calendar');
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [ragData, setRagData] = useState(null);
  const [showRagPipeline, setShowRagPipeline] = useState(false);

  const tools = [
    { id: 'calendar', name: 'Calendar', icon: '📅' },
    { id: 'documents', name: 'Documents', icon: '📄' },
    { id: 'location', name: 'Location', icon: '📍' },
    { id: 'health', name: 'Health', icon: '❤️' },
    { id: 'rag-search', name: 'RAG Search', icon: '🔍' }
  ];

  // Load real data from data_sync
  const [calendarData, setCalendarData] = useState([]);
  const [locationData, setLocationData] = useState([]);
  const [fitData, setFitData] = useState([]);

  useEffect(() => {
    // Load calendar data
    fetch('/api/calendar')
      .then(res => res.json())
      .then(data => setCalendarData(data.events || []))
      .catch(err => console.error('Failed to load calendar data:', err));

    // Load location data
    fetch('/api/location')
      .then(res => res.json())
      .then(data => setLocationData(data.locations || []))
      .catch(err => console.error('Failed to load location data:', err));

    // Load fitness data
    fetch('/api/fit')
      .then(res => res.json())
      .then(data => setFitData(data.activities || []))
      .catch(err => console.error('Failed to load fitness data:', err));
  }, []);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch(`/api/semantic-search?query=${encodeURIComponent(query)}&data_filters=document&max_results=5`);
      const data = await response.json();
      setResponse(JSON.stringify(data, null, 2));
      
      // Also fetch RAG pipeline data
      setRagData(data);
      setShowRagPipeline(true);
    } catch (error) {
      console.error('Search failed:', error);
      setResponse(`Search failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleQuerySubmit = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      let result;
      
      // Use unified API methods from mcpApi
      switch(activeTool) {
        case 'calendar':
          result = await mcpApi.getCalendarEvents();
          const events = result.data?.result?.events || result.data?.events || [];
          if (events.length > 0) {
            setResponse(`Calendar events:\n${events.map(event => `- ${event.summary || event.title} (${event.start_time || event.startTime})`).join('\n')}`);
          } else {
            setResponse('No calendar events found.');
          }
          break;
          
        case 'documents':
          result = await mcpApi.searchDocuments(query);
          const docs = result.data?.result?.documents || result.data?.documents || [];
          if (docs.length > 0) {
            setResponse(`Documents found:\n${docs.map(doc => `- ${doc.title || doc.name} (${doc.url || doc.link})`).join('\n')}`);
          } else {
            setResponse('No documents found.');
          }
          break;
          
        case 'location':
          result = await mcpApi.getLocationHistory();
          const locations = result.data?.result?.locations || result.data?.locations || [];
          if (locations.length > 0) {
            setResponse(`Location history:\n${locations.map(loc => `- ${loc.place || loc.address} (${loc.timestamp || loc.time})`).join('\n')}`);
          } else {
            setResponse('No location data found.');
          }
          break;
          
        case 'health':
          result = await mcpApi.getHealthData();
          const healthData = result.data?.result?.health || result.data?.health || {};
          setResponse(`Health metrics:\n${JSON.stringify(healthData, null, 2)}`);
          break;
          
        case 'rag-search':
          result = await mcpApi.searchDocuments(query); // Using document search as basis for RAG
          setResponse(JSON.stringify(result.data, null, 2));
          break;
          
        default:
          throw new Error('Invalid tool selected');
      }
    } catch (error) {
      console.error('API Error:', error);
      setResponse(`Error: ${error.response?.data?.detail || error.message || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleMCPIntegration = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      // Execute tool via MCP server
      const toolMapping = {
        calendar: 'query_calendar',
        documents: 'query_drive',
        location: 'query_location',
        health: 'query_fit'
      };

      const toolName = toolMapping[activeTool];
      if (!toolName) {
        throw new Error('Invalid tool selected');
      }

      const response = await axios.post(`/api/mcp/tools/${toolName}`, {
        query: query
      });
      
      setResponse(JSON.stringify(response.data, null, 2));
    } catch (error) {
      console.error('MCP Integration Error:', error);
      setResponse(`MCP Server Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">MCP Tools Panel</h2>
        
        {/* Tool Selection */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          {tools.map(tool => (
            <button
              key={tool.id}
              onClick={() => setActiveTool(tool.id)}
              className={`flex flex-col items-center p-4 rounded-lg border-2 transition-colors ${
                activeTool === tool.id
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="text-2xl mb-2">{tool.icon}</span>
              <span className="text-sm font-medium">{tool.name}</span>
            </button>
          ))}
        </div>

        {/* Query Input */}
        <div className="mb-6">
          <div className="flex gap-4">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={`Enter your ${tools.find(t => t.id === activeTool)?.name} query...`}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              onKeyPress={(e) => e.key === 'Enter' && handleQuerySubmit()}
            />
            <button
              onClick={handleQuerySubmit}
              disabled={loading}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Processing...' : 'Submit'}
            </button>
          </div>
        </div>

        {/* MCP Server Status */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
            <span className="text-sm text-gray-600">Connected to MCP Server</span>
            <span className="ml-auto text-xs text-gray-500">Tool: {activeTool}</span>
          </div>
        </div>

        {/* Raw Data Display */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          {/* Calendar Data */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-medium text-blue-900 mb-2">📅 Calendar Events ({calendarData.length})</h4>
            <div className="space-y-2 max-h-32 overflow-y-auto text-xs">
              {calendarData.slice(0, 3).map((event, index) => (
                <div key={index} className="bg-white p-2 rounded">
                  <div className="font-medium">{event.metadata?.title || event.text}</div>
                  <div className="text-blue-600">{new Date(event.metadata?.start_time).toLocaleDateString()}</div>
                </div>
              ))}
              {calendarData.length > 3 && (
                <div className="text-center text-blue-600">+{calendarData.length - 3} more</div>
              )}
            </div>
          </div>

          {/* Location Data */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 className="font-medium text-green-900 mb-2">📍 Location History ({locationData.length})</h4>
            <div className="space-y-2 max-h-32 overflow-y-auto text-xs">
              {locationData.slice(0, 3).map((location, index) => (
                <div key={index} className="bg-white p-2 rounded">
                  <div className="font-medium">{location.metadata?.place_name}</div>
                  <div className="text-green-600">{location.metadata?.location_type}</div>
                </div>
              ))}
              {locationData.length > 3 && (
                <div className="text-center text-green-600">+{locationData.length - 3} more</div>
              )}
            </div>
          </div>

          {/* Fitness Data */}
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <h4 className="font-medium text-purple-900 mb-2">🏃 Fitness Activities ({fitData.length})</h4>
            <div className="space-y-2 max-h-32 overflow-y-auto text-xs">
              {fitData.slice(0, 3).map((activity, index) => (
                <div key={index} className="bg-white p-2 rounded">
                  <div className="font-medium">{activity.metadata?.activity_type}</div>
                  <div className="text-purple-600">{activity.metadata?.duration_minutes}min • {activity.metadata?.calories} cal</div>
                </div>
              ))}
              {fitData.length > 3 && (
                <div className="text-center text-purple-600">+{fitData.length - 3} more</div>
              )}
            </div>
          </div>
        </div>

        {/* Response Area */}
        <div className="border border-gray-200 rounded-lg p-4 bg-gray-50 min-h-64">
          <h3 className="text-lg font-medium text-gray-900 mb-3">Response:</h3>
          {loading ? (
            <div className="flex items-center justify-center h-48">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              <span className="ml-3 text-gray-600">Processing with MCP server...</span>
            </div>
          ) : response ? (
            <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono bg-white p-4 rounded border">
              {response}
            </pre>
          ) : (
            <div className="flex items-center justify-center h-48 text-gray-500">
              Enter a query and submit to get results from the MCP server
            </div>
          )}
        </div>

        {/* RAG Pipeline Display */}
        {showRagPipeline && ragData && (
          <div className="mt-6 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-3">🤖 RAG Pipeline Results</h4>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 text-sm">
              <div className="bg-white p-3 rounded border">
                <div className="font-medium text-blue-900 mb-2">Query Processing</div>
                <div className="text-blue-700">Original: {query}</div>
                <div className="text-blue-700 mt-1">Results: {ragData.results?.length || 0} matches</div>
              </div>
              <div className="bg-white p-3 rounded border">
                <div className="font-medium text-green-900 mb-2">Search Results</div>
                <div className="text-green-700">Found {ragData.results?.length || 0} relevant items</div>
                <div className="text-green-700 mt-1">Best match score: {ragData.results?.[0]?.score?.toFixed(4) || 'N/A'}</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* MCP Tools Information */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Available MCP Tools</h3>
          <ul className="space-y-2 text-sm text-gray-600">
            <li>• Calendar Events: Query upcoming events and schedule</li>
            <li>• Document Search: Find relevant documents</li>
            <li>• Location History: Access location patterns</li>
            <li>• Health Data: Retrieve fitness information</li>
            <li>• RAG Search: Semantic search across all data</li>
          </ul>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">MCP Server Status</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Connection:</span>
              <span className="text-sm font-medium text-green-600">Active</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Status:</span>
              <span className="text-sm font-medium text-green-600">Ready</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Response Time:</span>
              <span className="text-sm font-medium text-gray-600">~200ms</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ToolsPanel;