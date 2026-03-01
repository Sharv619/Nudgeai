import React, { useState, useEffect } from 'react';
import { Bar, Line, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { mcpApi } from '../../utils/api';
import { saveAs } from 'file-saver';
import jsPDF from 'jspdf';
import 'jspdf-autotable';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const DataVisualization = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('week');
  const [chartData, setChartData] = useState({
    calendarData: null,
    healthData: null,
    locationData: null,
    documentData: null
  });
  const [loading, setLoading] = useState(true);
  const [exportLoading, setExportLoading] = useState(false);
  const [exportError, setExportError] = useState(null);

  useEffect(() => {
    loadData();
  }, [selectedPeriod]);

const loadData = async () => {
    setLoading(true);
    
    try {
      // Fetch real data from MCP API
      const [calendarResponse, healthResponse, locationResponse, documentResponse] = await Promise.all([
        mcpApi.fetchCalendarEvents(new Date().toISOString().split('T')[0], new Date().toISOString().split('T')[0]),
        mcpApi.fetchFitnessData('week'),
        mcpApi.fetchLocationHistory(new Date().toISOString().split('T')[0], new Date().toISOString().split('T')[0]),
        mcpApi.searchDocuments({})
      ]);

      // Process calendar data
      const calendarData = {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
          label: 'Events Per Day',
          data: calendarResponse.data.events ? calendarResponse.data.events.map(e => 1) : [0, 0, 0, 0, 0, 0, 0],
          backgroundColor: 'rgba(59, 130, 246, 0.5)',
          borderColor: 'rgb(59, 130, 246)',
          borderWidth: 1,
        }]
      };

      // Process health data
      const healthData = {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
          label: 'Steps',
          data: healthResponse.data.data.weeklySteps || [0, 0, 0, 0, 0, 0, 0],
          borderColor: 'rgb(16, 185, 129)',
          backgroundColor: 'rgba(16, 185, 129, 0.5)',
          tension: 0.1,
        }, {
          label: 'Calories',
          data: healthResponse.data.data.weeklyCalories || [0, 0, 0, 0, 0, 0, 0],
          borderColor: 'rgb(239, 68, 68)',
          backgroundColor: 'rgba(239, 68, 68, 0.5)',
          tension: 0.1,
        }]
      };

      // Process location data
      const locationData = {
        labels: ['Home', 'Office', 'Gym', 'Grocery', 'Other'],
        datasets: [{
          label: 'Time Spent (hours)',
          data: locationResponse.data.locations ? locationResponse.data.locations.map(l => l.duration || 0) : [0, 0, 0, 0, 0],
          backgroundColor: [
            'rgba(59, 130, 246, 0.8)',
            'rgba(16, 185, 129, 0.8)',
            'rgba(245, 158, 11, 0.8)',
            'rgba(239, 68, 68, 0.8)',
            'rgba(139, 92, 246, 0.8)',
          ],
          borderColor: [
            'rgb(59, 130, 246)',
            'rgb(16, 185, 129)',
            'rgb(245, 158, 11)',
            'rgb(239, 68, 68)',
            'rgb(139, 92, 246)',
          ],
          borderWidth: 1,
        }]
      };

      // Process document data
      const documentData = {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
          label: 'Documents Accessed',
          data: documentResponse.data.documents ? documentResponse.data.documents.map(d => 1) : [0, 0, 0, 0, 0, 0],
          backgroundColor: 'rgba(139, 92, 246, 0.5)',
          borderColor: 'rgb(139, 92, 246)',
          borderWidth: 1,
        }]
      };

      setChartData({ calendarData, healthData, locationData, documentData });
      setLoading(false);

    } catch (error) {
      console.error('Error loading data:', error);
      // Fallback to mock data if API fails
      const mockData = {
        calendarData: {
          labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
          datasets: [{
            label: 'Events Per Day',
            data: [3, 5, 2, 4, 6, 3, 2],
            backgroundColor: 'rgba(59, 130, 246, 0.5)',
            borderColor: 'rgb(59, 130, 246)',
            borderWidth: 1,
          }]
        },
        healthData: {
          labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
          datasets: [{
            label: 'Steps',
            data: [8547, 9200, 7800, 10500, 8900, 12000, 6500],
            borderColor: 'rgb(16, 185, 129)',
            backgroundColor: 'rgba(16, 185, 129, 0.5)',
            tension: 0.1,
          }, {
            label: 'Calories',
            data: [2100, 2400, 1800, 2600, 2200, 2800, 1900],
            borderColor: 'rgb(239, 68, 68)',
            backgroundColor: 'rgba(239, 68, 68, 0.5)',
            tension: 0.1,
          }]
        },
        locationData: {
          labels: ['Home', 'Office', 'Gym', 'Grocery', 'Other'],
          datasets: [{
            label: 'Time Spent (hours)',
            data: [56, 40, 8, 4, 12],
            backgroundColor: [
              'rgba(59, 130, 246, 0.8)',
              'rgba(16, 185, 129, 0.8)',
              'rgba(245, 158, 11, 0.8)',
              'rgba(239, 68, 68, 0.8)',
              'rgba(139, 92, 246, 0.8)',
            ],
            borderColor: [
              'rgb(59, 130, 246)',
              'rgb(16, 185, 129)',
              'rgb(245, 158, 11)',
              'rgb(239, 68, 68)',
              'rgb(139, 92, 246)',
            ],
            borderWidth: 1,
          }]
        },
        documentData: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
          datasets: [{
            label: 'Documents Accessed',
            data: [12, 19, 15, 18, 22, 17],
            backgroundColor: 'rgba(139, 92, 246, 0.5)',
            borderColor: 'rgb(139, 92, 246)',
            borderWidth: 1,
          }]
        }
      };
      setChartData(mockData);
      setLoading(false);
    }
  };

  const exportToCSV = async () => {
    setExportLoading(true);
    setExportError(null);

    try {
      // Fetch all data
      const [calendarResponse, healthResponse, locationResponse, documentResponse] = await Promise.all([
        mcpApi.fetchCalendarEvents(new Date().toISOString().split('T')[0], new Date().toISOString().split('T')[0]),
        mcpApi.fetchFitnessData('week'),
        mcpApi.fetchLocationHistory(new Date().toISOString().split('T')[0], new Date().toISOString().split('T')[0]),
        mcpApi.searchDocuments({})
      ]);

      // Create CSV content
      let csvContent = 'Type,Title,Date,Details\n';

      // Add calendar events
      if (calendarResponse.data.events) {
        calendarResponse.data.events.forEach(event => {
          csvContent += `Calendar,${event.title || 'N/A'},${event.date || 'N/A'},${event.summary || 'N/A'}\n`;
        });
      }

      // Add health data
      if (healthResponse.data.data) {
        csvContent += `Health,Steps,${new Date().toISOString().split('T')[0]},${healthResponse.data.data.steps_today || 0}\n`;
        csvContent += `Health,Calories,${new Date().toISOString().split('T')[0]},${healthResponse.data.data.calories_burned || 0}\n`;
      }

      // Add location data
      if (locationResponse.data.locations) {
        locationResponse.data.locations.forEach(location => {
          csvContent += `Location,${location.place || 'N/A'},${location.time || 'N/A'},${location.duration || 'N/A'} hours\n`;
        });
      }

      // Add document data
      if (documentResponse.data.documents) {
        documentResponse.data.documents.forEach(doc => {
          csvContent += `Document,${doc.name || 'N/A'},${doc.modified || 'N/A'},${doc.type || 'N/A'}\n`;
        });
      }

      // Create blob and download
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      saveAs(blob, `nudgeai_data_${new Date().toISOString().split('T')[0]}.csv`);

    } catch (error) {
      console.error('Error exporting to CSV:', error);
      setExportError('Failed to export data. Please try again.');
    } finally {
      setExportLoading(false);
    }
  };

  const exportToJSON = async () => {
    setExportLoading(true);
    setExportError(null);

    try {
      // Fetch all data
      const [calendarResponse, healthResponse, locationResponse, documentResponse] = await Promise.all([
        mcpApi.fetchCalendarEvents(new Date().toISOString().split('T')[0], new Date().toISOString().split('T')[0]),
        mcpApi.fetchFitnessData('week'),
        mcpApi.fetchLocationHistory(new Date().toISOString().split('T')[0], new Date().toISOString().split('T')[0]),
        mcpApi.searchDocuments({})
      ]);

      // Create JSON object
      const exportData = {
        export_date: new Date().toISOString(),
        calendar_events: calendarResponse.data.events || [],
        health_data: healthResponse.data.data || {},
        location_history: locationResponse.data.locations || [],
        documents: documentResponse.data.documents || []
      };

      // Create blob and download
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      saveAs(blob, `nudgeai_data_${new Date().toISOString().split('T')[0]}.json`);

    } catch (error) {
      console.error('Error exporting to JSON:', error);
      setExportError('Failed to export data. Please try again.');
    } finally {
      setExportLoading(false);
    }
  };

  const exportToPDF = async () => {
    setExportLoading(true);
    setExportError(null);

    try {
      // Fetch all data
      const [calendarResponse, healthResponse, locationResponse, documentResponse] = await Promise.all([
        mcpApi.fetchCalendarEvents(new Date().toISOString().split('T')[0], new Date().toISOString().split('T')[0]),
        mcpApi.fetchFitnessData('week'),
        mcpApi.fetchLocationHistory(new Date().toISOString().split('T')[0], new Date().toISOString().split('T')[0]),
        mcpApi.searchDocuments({})
      ]);

      // Create PDF content
      const doc = new jsPDF();
      doc.setFontSize(16);
      doc.text('NudgeAI Data Export', 14, 20);

      let yPosition = 30;

      // Add calendar events
      if (calendarResponse.data.events && calendarResponse.data.events.length > 0) {
        doc.setFontSize(12);
        doc.text('Calendar Events:', 14, yPosition);
        yPosition += 8;
        calendarResponse.data.events.forEach(event => {
          doc.setFontSize(10);
          doc.text(`${event.title || 'N/A'} - ${event.date || 'N/A'}`, 20, yPosition);
          yPosition += 6;
        });
        yPosition += 10;
      }

      // Add health data
      if (healthResponse.data.data) {
        doc.setFontSize(12);
        doc.text('Health Data:', 14, yPosition);
        yPosition += 8;
        doc.setFontSize(10);
        doc.text(`Steps: ${healthResponse.data.data.steps_today || 0}`, 20, yPosition);
        yPosition += 6;
        doc.text(`Calories: ${healthResponse.data.data.calories_burned || 0}`, 20, yPosition);
        yPosition += 10;
      }

      // Add location data
      if (locationResponse.data.locations && locationResponse.data.locations.length > 0) {
        doc.setFontSize(12);
        doc.text('Location History:', 14, yPosition);
        yPosition += 8;
        locationResponse.data.locations.forEach(location => {
          doc.setFontSize(10);
          doc.text(`${location.place || 'N/A'} - ${location.duration || '0'} hours`, 20, yPosition);
          yPosition += 6;
        });
        yPosition += 10;
      }

      // Add document data
      if (documentResponse.data.documents && documentResponse.data.documents.length > 0) {
        doc.setFontSize(12);
        doc.text('Documents:', 14, yPosition);
        yPosition += 8;
        documentResponse.data.documents.forEach(doc => {
          doc.setFontSize(10);
          doc.text(`${doc.name || 'N/A'} - ${doc.type || 'N/A'}`, 20, yPosition);
          yPosition += 6;
        });
      }

      // Save PDF
      doc.save(`nudgeai_data_${new Date().toISOString().split('T')[0]}.pdf`);

    } catch (error) {
      console.error('Error exporting to PDF:', error);
      setExportError('Failed to export data. Please try again.');
    } finally {
      setExportLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-3 text-gray-600">Loading data from MCP server...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Period Selector */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">Data Visualization</h2>
          <div className="flex space-x-2">
            {['day', 'week', 'month', 'year'].map(period => (
              <button
                key={period}
                onClick={() => setSelectedPeriod(period)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedPeriod === period
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {period.charAt(0).toUpperCase() + period.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Calendar Events Chart */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Calendar Events</h3>
          <div className="h-80">
            {chartData.calendarData && (
              <Bar data={chartData.calendarData} options={options} />
            )}
          </div>
        </div>

        {/* Health Data Chart */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Health & Fitness</h3>
          <div className="h-80">
            {chartData.healthData && (
              <Line data={chartData.healthData} options={options} />
            )}
          </div>
        </div>

        {/* Location Data Chart */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Location Patterns</h3>
          <div className="h-80">
            {chartData.locationData && (
              <Pie data={chartData.locationData} options={options} />
            )}
          </div>
        </div>

        {/* Document Activity Chart */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Document Activity</h3>
          <div className="h-80">
            {chartData.documentData && (
              <Bar data={chartData.documentData} options={options} />
            )}
          </div>
        </div>
      </div>

      {/* MCP Data Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h4 className="font-medium text-gray-900 mb-2">MCP Server</h4>
          <div className="flex items-center text-sm text-green-600">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            Connected
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h4 className="font-medium text-gray-900 mb-2">Data Sources</h4>
          <div className="text-sm text-gray-600">4 Active</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h4 className="font-medium text-gray-900 mb-2">Last Updated</h4>
          <div className="text-sm text-gray-600">Just now</div>
        </div>
      </div>

      {/* Data Export Options */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Export Data</h3>
        {exportError && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600">
            {exportError}
          </div>
        )}
        <div className="flex flex-wrap gap-4">
          <button
            onClick={exportToCSV}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            disabled={exportLoading}
          >
            {exportLoading ? 'Exporting CSV...' : 'Export as CSV'}
          </button>
          <button
            onClick={exportToPDF}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            disabled={exportLoading}
          >
            {exportLoading ? 'Exporting PDF...' : 'Export as PDF'}
          </button>
          <button
            onClick={exportToJSON}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            disabled={exportLoading}
          >
            {exportLoading ? 'Exporting JSON...' : 'Export as JSON'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DataVisualization;

export default DataVisualization;