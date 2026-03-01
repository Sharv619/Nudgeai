import React, { useState, useEffect } from 'react';
import { mcpApi } from '../utils/api';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState({
    calendarEvents: [],
    recentDocuments: [],
    locationHistory: [],
    healthStats: {
      steps_today: 0,
      calories_burned: 0,
      active_minutes: 0,
      recent_activities: []
    },
    systemStatus: 'loading'
  });

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch real data from the NudgeAI backend API
      const [calendarResponse, documentsResponse, locationResponse, healthResponse] = await Promise.allSettled([
        mcpApi.getCalendarEvents(),
        mcpApi.searchDocuments(),
        mcpApi.getLocationHistory(),
        mcpApi.getHealthData()
      ]);

      const newData = {
        calendarEvents: [],
        recentDocuments: [],
        locationHistory: [],
        healthStats: {},
        systemStatus: 'connected'
      };

      // Process calendar events
      if (calendarResponse.status === 'fulfilled') {
        const events = calendarResponse.value.data?.result?.events || calendarResponse.value.data?.events || [];
        newData.calendarEvents = events.map((event, index) => ({
          id: event.id || index + 1,
          title: event.summary || event.title || event.name || 'Event',
          time: event.start_time || event.startTime || 'N/A',
          type: event.type || 'event'
        }));
      } else {
        // Fallback to mock if API fails
        newData.calendarEvents = [
          { id: 1, title: 'Mistral Worldwide Hackathon', time: 'Today 9:00 AM', type: 'event' },
          { id: 2, title: 'Wake up list', time: 'Mar 1, 9:00 AM', type: 'reminder' },
          { id: 3, title: 'Meeting with Manoj', time: 'Mar 2, 10:00 PM', type: 'meeting' }
        ];
      }

      // Process documents
      if (documentsResponse.status === 'fulfilled') {
        const docs = documentsResponse.value.data?.result?.documents || documentsResponse.value.data?.documents || [];
        newData.recentDocuments = docs.map((doc, index) => ({
          id: doc.id || index + 1,
          name: doc.title || doc.name || 'Untitled Document',
          modified: doc.modified || doc.lastModified || 'Recently'
        }));
      } else {
        // Fallback to mock if API fails
        newData.recentDocuments = [
          { id: 1, name: 'Marketing Budget 2024.xlsx', modified: '2 hours ago' },
          { id: 2, name: 'Project Plan.docx', modified: '1 day ago' }
        ];
      }

      // Process location history
      if (locationResponse.status === 'fulfilled') {
        const locations = locationResponse.value.data?.result?.locations || locationResponse.value.data?.locations || [];
        newData.locationHistory = locations.map((loc, index) => ({
          id: loc.id || index + 1,
          place: loc.place || loc.address || 'Unknown Location',
          time: loc.time || loc.timestamp || 'N/A',
          duration: loc.duration || 'N/A'
        }));
      } else {
        // Fallback to mock if API fails
        newData.locationHistory = [
          { id: 1, place: 'Home', time: '8:00 AM - 9:00 AM', duration: '1 hr' },
          { id: 2, place: 'Office', time: '9:00 AM - 6:00 PM', duration: '9 hrs' },
          { id: 3, place: 'Gym', time: '6:30 PM - 7:30 PM', duration: '1 hr' }
        ];
      }

      // Process health stats
      if (healthResponse.status === 'fulfilled') {
        const health = healthResponse.value.data?.result?.health || 
                      healthResponse.value.data?.health || 
                      healthResponse.value.data?.result || 
                      {};
        newData.healthStats = {
          stepsToday: health.steps_today || health.stepsToday || health.steps || 0,
          caloriesBurned: health.calories_burned || health.caloriesBurned || health.calories || 0,
          activeMinutes: health.active_minutes || health.activeMinutes || health.active || 0
        };
      } else {
        // Fallback to mock if API fails
        newData.healthStats = {
          stepsToday: 8547,
          caloriesBurned: 420,
          activeMinutes: 65
        };
      }

      setDashboardData(newData);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
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
            <div className="p-2 bg-green-100 rounded-lg">
              <span className="text-2xl">📄</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Recent Docs</p>
              <p className="text-2xl font-semibold text-gray-900">{dashboardData.recentDocuments.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <span className="text-2xl">📍</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Locations</p>
              <p className="text-2xl font-semibold text-gray-900">{dashboardData.locationHistory.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <span className="text-2xl">❤️</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Health</p>
              <p className="text-2xl font-semibold text-gray-900">{dashboardData.healthStats.stepsToday.toLocaleString()}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Calendar Events */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Upcoming Calendar Events</h3>
          <div className="space-y-3">
            {dashboardData.calendarEvents.map(event => (
              <div key={event.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">{event.title}</p>
                  <p className="text-sm text-gray-500">{event.time}</p>
                </div>
                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full capitalize">
                  {event.type}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Documents */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Documents</h3>
          <div className="space-y-3">
            {dashboardData.recentDocuments.map(doc => (
              <div key={doc.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">{doc.name}</p>
                  <p className="text-sm text-gray-500">{doc.modified}</p>
                </div>
                <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                  View
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Location History */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 lg:col-span-2">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Location History</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Place</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {dashboardData.locationHistory.map(loc => (
                  <tr key={loc.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{loc.place}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{loc.time}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{loc.duration}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;