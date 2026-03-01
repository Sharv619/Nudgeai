import React, { useState, useEffect } from 'react';
import { mcpApi } from '../utils/api';
import './DataDisplay.css';

const DataDisplay = () => {
  const [data, setData] = useState({
    calendar: [],
    location: [],
    insights: null,
    summary: null
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    eventType: '',
    locationType: '',
    timePeriod: 'week'
  });

  const loadData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch calendar data
      const calendarResponse = await mcpApi.getCalendarEvents({
        start_date: filters.startDate,
        end_date: filters.endDate,
        event_type: filters.eventType
      });

      // Fetch location data
      const locationResponse = await mcpApi.getLocationHistory({
        start_date: filters.startDate,
        end_date: filters.endDate,
        location_type: filters.locationType
      });

      // Fetch insights - using the executeTool method to call the insights endpoint
      const insightsResponse = await mcpApi.executeTool('get_insights', {
        data_sources: ['calendar', 'location'],
        focus_areas: ['productivity', 'health']
      });

      // Fetch daily summary - using the executeTool method to call the daily summary endpoint
      const summaryResponse = await mcpApi.executeTool('generate_daily_summary', {
        date: filters.startDate || new Date().toISOString().split('T')[0]
      });

      setData({
        calendar: calendarResponse.data?.result?.events || calendarResponse.data?.events || [],
        location: locationResponse.data?.result?.locations || locationResponse.data?.locations || [],
        insights: insightsResponse.data?.result || insightsResponse.data,
        summary: summaryResponse.data?.result || summaryResponse.data
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
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
        <h2>Data Filters</h2>
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
                  <p>{data.insights.patterns || 'Analyzing your data patterns...'}</p>
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
          timePeriod: 'week'
        })} className="clear-btn">
          Clear Filters
        </button>
      </div>
    </div>
  );
};

export default DataDisplay;