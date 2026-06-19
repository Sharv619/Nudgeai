import React, { useState, useEffect } from 'react';
import { mcpApi } from '../utils/api';

const DataLogs = () => {
  const [logs, setLogs] = useState([]);
  const [selectedSource, setSelectedSource] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLogs();
  }, [selectedSource]); // Load logs when selectedSource changes

  const loadLogs = async () => {
    setLoading(true);
    
    try {
      // Attempt to fetch real system logs from the API
      let fetchedLogs = [];
      
      try {
        // Try to get actual logs from the system - using a general API call as an example
        // Since there may not be a specific logs endpoint, we'll try to get some system status
        const response = await mcpApi.getCalendarEvents(); // Use existing working API call as a test
        if (response) {
          // Generate synthetic logs based on the current system state
          fetchedLogs = [
            {
              id: 1,
              timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
              source: 'MCP Server',
              level: 'INFO',
            message: 'Local prototype check completed',
              details: `Calendar events loaded: ${response.data?.result?.events?.length || 'N/A'}`
            },
            {
              id: 2,
              timestamp: new Date(Date.now() - 60000).toISOString().replace('T', ' ').substring(0, 19), // 1 min ago
              source: 'Google Auth',
              level: 'INFO',
              message: 'API connections active',
              details: 'Calendar, Drive, and Location APIs authenticated'
            },
            {
              id: 3,
              timestamp: new Date(Date.now() - 300000).toISOString().replace('T', ' ').substring(0, 19), // 5 mins ago
              source: 'RAG System',
              level: 'INFO',
              message: 'Knowledge base active',
              details: 'Vector database ready for semantic search'
            },
            {
              id: 4,
              timestamp: new Date(Date.now() - 600000).toISOString().replace('T', ' ').substring(0, 19), // 10 mins ago
              source: 'Data Sync',
              level: 'INFO',
              message: 'Recent sync activity',
              details: 'Location and calendar data synchronized'
            },
            {
              id: 5,
              timestamp: new Date(Date.now() - 900000).toISOString().replace('T', ' ').substring(0, 19), // 15 mins ago
              source: 'MCP Server',
              level: 'INFO',
              message: 'Service started',
              details: 'MCP server initialized successfully'
            }
          ];
        }
      } catch (apiError) {
        console.warn('Could not fetch live system data, showing labelled sample logs:', apiError);
        
        // Labelled sample data for the local prototype. These are not live production logs.
        fetchedLogs = [
          {
            id: 1,
            timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
            source: 'MCP Server',
            level: 'INFO',
            message: 'MCP server started successfully on port 8003',
            details: 'Hugging Face model loaded: mistral-7b-instruct-v0.1.Q4_0.gguf'
          },
          {
            id: 2,
            timestamp: new Date(Date.now() - 60000).toISOString().replace('T', ' ').substring(0, 19), // 1 min ago
            source: 'Google Auth',
            level: 'INFO',
            message: 'Google Calendar API authenticated successfully',
            details: 'User: user@example.com, Scopes: calendar.readonly'
          },
          {
            id: 3,
            timestamp: new Date(Date.now() - 120000).toISOString().replace('T', ' ').substring(0, 19), // 2 mins ago
            source: 'Google Auth',
            level: 'INFO',
            message: 'Google Drive API authenticated successfully',
            details: 'User: user@example.com, Scopes: drive.readonly'
          },
          {
            id: 4,
            timestamp: new Date(Date.now() - 180000).toISOString().replace('T', ' ').substring(0, 19), // 3 mins ago
            source: 'Data Sync',
            level: 'INFO',
            message: 'Calendar events synced: 15 events processed',
            details: 'Time range: 2026-02-28 to 2026-03-07'
          },
          {
            id: 5,
            timestamp: new Date(Date.now() - 240000).toISOString().replace('T', ' ').substring(0, 19), // 4 mins ago
            source: 'Data Sync',
            level: 'INFO',
            message: 'Drive documents synced: 23 documents processed',
            details: 'File types: PDF, DOCX, XLSX, PPTX'
          },
          {
            id: 6,
            timestamp: new Date(Date.now() - 300000).toISOString().replace('T', ' ').substring(0, 19), // 5 mins ago
            source: 'RAG System',
            level: 'INFO',
            message: 'Vector database updated with 38 new embeddings',
            details: 'Index size: 1,247 vectors, Dimension: 384'
          },
          {
            id: 7,
            timestamp: new Date(Date.now() - 360000).toISOString().replace('T', ' ').substring(0, 19), // 6 mins ago
            source: 'Location Sync',
            level: 'INFO',
            message: 'Location history synced: 42 locations processed',
            details: 'Time range: 2026-02-28 to 2026-03-01'
          },
          {
            id: 8,
            timestamp: new Date(Date.now() - 420000).toISOString().replace('T', ' ').substring(0, 19), // 7 mins ago
            source: 'Fitness Sync',
            level: 'INFO',
            message: 'Fitness data synced: 7 days of activity data',
            details: 'Steps, calories, heart rate, sleep data'
          },
          {
            id: 9,
            timestamp: new Date(Date.now() - 480000).toISOString().replace('T', ' ').substring(0, 19), // 8 mins ago
            source: 'MCP Server',
            level: 'WARNING',
            message: 'API rate limit approaching for Google Calendar',
            details: 'Current usage: 85% of daily quota'
          },
          {
            id: 10,
            timestamp: new Date(Date.now() - 540000).toISOString().replace('T', ' ').substring(0, 19), // 9 mins ago
            source: 'RAG System',
            level: 'INFO',
            message: 'Semantic search index optimized',
            details: 'Search latency improved by 15%'
          },
          {
            id: 11,
            timestamp: new Date(Date.now() - 600000).toISOString().replace('T', ' ').substring(0, 19), // 10 mins ago
            source: 'Data Sync',
            level: 'ERROR',
            message: 'Failed to sync Google Fit data',
            details: 'Error: Invalid OAuth token, retrying in 5 minutes'
          },
          {
            id: 12,
            timestamp: new Date(Date.now() - 660000).toISOString().replace('T', ' ').substring(0, 19), // 11 mins ago
            source: 'MCP Server',
            level: 'INFO',
            message: 'Frontend connection established',
            details: 'Client: http://localhost:3000, Protocol: WebSocket'
          },
          {
            id: 13,
            timestamp: new Date(Date.now() - 720000).toISOString().replace('T', ' ').substring(0, 19), // 12 mins ago
            source: 'WhiteCircle',
            level: 'INFO',
            message: 'AI response quality validation passed',
            details: 'Response time: 2.3s, Quality score: 9.2/10'
          },
          {
            id: 14,
            timestamp: new Date(Date.now() - 780000).toISOString().replace('T', ' ').substring(0, 19), // 13 mins ago
            source: 'Data Sync',
            level: 'INFO',
            message: 'Daily summary generated for 2026-03-01',
            details: 'Calendar events: 3, Locations visited: 4, Steps: 8,547'
          },
          {
            id: 15,
            timestamp: new Date(Date.now() - 840000).toISOString().replace('T', ' ').substring(0, 19), // 14 mins ago
            source: 'MCP Server',
            level: 'INFO',
            message: 'System health check completed',
            details: 'Status: All systems operational'
          }
        ];
      }

      // Filter logs based on selected source
      const filteredLogs = selectedSource === 'all' 
        ? fetchedLogs 
        : fetchedLogs.filter(log => log.source.toLowerCase() === selectedSource.toLowerCase());

      setLogs(filteredLogs);
    } catch (error) {
      console.error('Error loading logs:', error);
      
      // Fallback to mock data if there's an error
      const fallbackLogs = [
        {
          id: 1,
          timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
          source: 'System',
          level: 'ERROR',
          message: 'Failed to load system logs',
          details: `Error: ${error.message}`
        }
      ];
      
      setLogs(fallbackLogs);
    } finally {
      setLoading(false);
    }
  };

  const getLogLevelColor = (level) => {
    switch (level) {
      case 'ERROR': return 'bg-red-100 text-red-800 border-red-200';
      case 'WARNING': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'INFO': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'SUCCESS': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getSourceIcon = (source) => {
    switch (source) {
      case 'MCP Server': return '🤖';
      case 'Google Auth': return '🔐';
      case 'Data Sync': return '🔄';
      case 'RAG System': return '🧠';
      case 'Location Sync': return '📍';
      case 'Fitness Sync': return '🏃';
      case 'WhiteCircle': return '⚪';
      default: return '📋';
    }
  };

  const logSources = ['all', 'MCP Server', 'Google Auth', 'Data Sync', 'RAG System', 'Location Sync', 'Fitness Sync', 'WhiteCircle'];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-3 text-gray-600">Loading system logs...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Prototype Logs</h2>
            <p className="text-sm text-gray-600 mt-1">Local prototype/sample log view. This is not live production telemetry.</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center text-sm text-gray-600">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
              Local sample view
            </div>
            <button 
              onClick={loadLogs}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Refresh Logs
            </button>
          </div>
        </div>
      </div>

      {/* Filter Controls */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="flex flex-wrap gap-2">
          {logSources.map(source => (
            <button
              key={source}
              onClick={() => setSelectedSource(source)}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedSource === source
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {source}
            </button>
          ))}
        </div>
      </div>

      {/* Logs Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Log Entries ({logs.length})
          </h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Source</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Level</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Message</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Details</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-mono">
                    {log.timestamp}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center">
                      <span className="mr-2">{getSourceIcon(log.source)}</span>
                      <span className="font-medium">{log.source}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full border ${getLogLevelColor(log.level)}`}>
                      {log.level}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {log.message}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600 max-w-md">
                    <span className="truncate block" title={log.details}>
                      {log.details}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Log Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h4 className="font-medium text-gray-900 mb-2">Total Logs</h4>
          <div className="text-2xl font-bold text-gray-900">{logs.length}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h4 className="font-medium text-gray-900 mb-2">Errors</h4>
          <div className="text-2xl font-bold text-red-600">
            {logs.filter(log => log.level === 'ERROR').length}
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h4 className="font-medium text-gray-900 mb-2">Warnings</h4>
          <div className="text-2xl font-bold text-yellow-600">
            {logs.filter(log => log.level === 'WARNING').length}
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h4 className="font-medium text-gray-900 mb-2">Info</h4>
          <div className="text-2xl font-bold text-blue-600">
            {logs.filter(log => log.level === 'INFO').length}
          </div>
        </div>
      </div>

      {/* Export Options */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Export Logs</h3>
        <div className="flex flex-wrap gap-4">
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            Export as JSON
          </button>
          <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
            Export as CSV
          </button>
          <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
            Export as TXT
          </button>
          <button className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors">
            Clear Logs
          </button>
        </div>
      </div>
    </div>
  );
};

export default DataLogs;
