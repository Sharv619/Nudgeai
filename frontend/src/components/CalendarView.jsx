import React, { useState, useEffect } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import { mcpApi } from '../utils/api';
import SemanticSearch from './SemanticSearch';

const CalendarView = () => {
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch calendar events from the API
  useEffect(() => {
    const fetchCalendarEvents = async () => {
      try {
        setLoading(true);
        // Fetch all calendar events (no date range specified to get full month)
        const response = await mcpApi.getCalendarEvents();
        const apiEvents = response.data?.result?.events || [];
        
        // Transform API events to FullCalendar format
        const transformedEvents = apiEvents.map((event, index) => ({
          id: event.id || `event-${index}`,
          title: event.summary || event.title || 'Untitled Event',
          start: event.start_time || new Date().toISOString(),
          end: event.end_time || null,
          description: event.description || '',
          location: event.location || '',
          extendedProps: {
            description: event.description || '',
            location: event.location || '',
            type: event.type || 'event',
            attendees: event.attendees || []
          }
        }));
        
        setEvents(transformedEvents);
      } catch (error) {
        console.error('Error fetching calendar events:', error);
        // Fallback to mock data
        setEvents([
          {
            id: 'mock-1',
            title: 'Mistral Worldwide Hackathon - Sydney edition',
            start: '2026-02-28T09:00:00',
            description: 'Major hackathon event at Michael Crouch Innovation Centre, Sydney',
            location: 'Michael Crouch Innovation Centre, Sydney',
            extendedProps: {
              description: 'Major hackathon event at Michael Crouch Innovation Centre, Sydney',
              location: 'Michael Crouch Innovation Centre, Sydney',
              type: 'event'
            }
          },
          {
            id: 'mock-2',
            title: 'WAKE UP LIST',
            start: '2026-03-01T09:00:00',
            description: 'Daily routine tasks',
            location: 'Home',
            extendedProps: {
              description: 'Daily routine tasks',
              location: 'Home',
              type: 'reminder'
            }
          },
          {
            id: 'mock-3',
            title: 'Meeting with Manoj',
            start: '2026-03-02T22:00:00',
            description: 'Project discussion',
            location: 'Online',
            extendedProps: {
              description: 'Project discussion',
              location: 'Online',
              type: 'meeting'
            }
          },
          {
            id: 'mock-4',
            title: 'Atlassian Takeover 2026',
            start: '2026-03-03T18:00:00',
            description: 'Special event for Atlassian',
            location: 'Sydney CBD',
            extendedProps: {
              description: 'Special event for Atlassian',
              location: 'Sydney CBD',
              type: 'event'
            }
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchCalendarEvents();
  }, []);

  // Handle event click
  const handleEventClick = (clickInfo) => {
    setSelectedEvent(clickInfo.event);
  };

  // Handle closing the event modal
  const handleCloseModal = () => {
    setSelectedEvent(null);
  };

  // Handle date selection (for creating new events)
  const handleDateSelect = (selectInfo) => {
    // For now, we just show an alert - in a real implementation, this would open a form to create an event
    alert(`Create new event on ${selectInfo.startStr}`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <span className="ml-3">Loading calendar events...</span>
      </div>
    );
  }

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Calendar View</h2>
      
      {/* Semantic Search Section */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3 text-gray-700">🔍 Smart Search</h3>
        <SemanticSearch />
      </div>
      
      <div className="calendar-container">
        <FullCalendar
          plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
          headerToolbar={{
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
          }}
          initialView="dayGridMonth"
          events={events}
          selectable={true}
          selectMirror={true}
          dayMaxEvents={true}
          weekends={true}
          eventClick={handleEventClick}
          select={handleDateSelect}
          editable={false} // Disable editing for now
          droppable={false} // Disable dragging for now
        />
      </div>

      {/* Event Detail Modal */}
      {selectedEvent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-bold text-gray-800">{selectedEvent.title}</h3>
                <button 
                  onClick={handleCloseModal}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="space-y-3">
                <div>
                  <h4 className="font-medium text-gray-700">Start Time</h4>
                  <p className="text-gray-900">
                    {new Date(selectedEvent.start).toLocaleString()}
                  </p>
                </div>
                
                {selectedEvent.end && (
                  <div>
                    <h4 className="font-medium text-gray-700">End Time</h4>
                    <p className="text-gray-900">
                      {new Date(selectedEvent.end).toLocaleString()}
                    </p>
                  </div>
                )}
                
                {selectedEvent.extendedProps.location && (
                  <div>
                    <h4 className="font-medium text-gray-700">Location</h4>
                    <p className="text-gray-900">{selectedEvent.extendedProps.location}</p>
                  </div>
                )}
                
                {selectedEvent.extendedProps.description && (
                  <div>
                    <h4 className="font-medium text-gray-700">Description</h4>
                    <p className="text-gray-900 whitespace-pre-line">{selectedEvent.extendedProps.description}</p>
                  </div>
                )}
                
                {selectedEvent.extendedProps.attendees && selectedEvent.extendedProps.attendees.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-700">Attendees</h4>
                    <div className="flex flex-wrap gap-1">
                      {selectedEvent.extendedProps.attendees.map((attendee, index) => (
                        <span key={index} className="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs">
                          {attendee}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {selectedEvent.extendedProps.type && (
                  <div>
                    <h4 className="font-medium text-gray-700">Type</h4>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      selectedEvent.extendedProps.type === 'event' || selectedEvent.extendedProps.type === 'default' ? 'bg-blue-100 text-blue-800' :
                      selectedEvent.extendedProps.type === 'meeting' ? 'bg-green-100 text-green-800' :
                      selectedEvent.extendedProps.type === 'reminder' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-purple-100 text-purple-800'
                    }`}>
                      {selectedEvent.extendedProps.type}
                    </span>
                  </div>
                )}
              </div>
              
              <div className="mt-6 flex justify-end">
                <button
                  onClick={handleCloseModal}
                  className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CalendarView;