// TypeScript interfaces for NudgeAI backend data structures

export interface CalendarEvent {
  id: string;
  summary: string;
  start_time: string;
  type: string;
  description: string;
  location: string;
}

export interface Document {
  id: string;
  title: string;
  url: string;
  modified: string;
  type: string;
}

export interface Location {
  id: string;
  place: string;
  time: string;
  duration: string;
  type: string;
  coordinates: {
    lat: number;
    lng: number;
  };
}

export interface HealthActivity {
  type: string;
  duration: number;
  steps: number;
  calories: number;
  timestamp: string;
}

export interface HealthData {
  steps_today: number;
  calories_burned: number;
  active_minutes: number;
  heart_rate_avg?: number;
  recent_activities: HealthActivity[];
}

export interface CalendarResponse {
  result: {
    events: CalendarEvent[];
    insights?: string;
    summary?: string;
  };
}

export interface DocumentResponse {
  result: {
    documents: Document[];
    summary?: string;
    count?: number;
  };
}

export interface LocationResponse {
  result: {
    locations: Location[];
    insights?: string;
    summary?: string;
  };
}

export interface HealthResponse {
  result: {
    health: HealthData;
  };
}

export interface DashboardData {
  calendarEvents: CalendarEvent[];
  recentDocuments: Document[];
  locationHistory: Location[];
  healthStats: HealthData;
  systemStatus: 'connected' | 'disconnected' | 'loading';
}

export interface ToolResponse {
  result: {
    events?: CalendarEvent[];
    documents?: Document[];
    locations?: Location[];
    health?: HealthData;
    insights?: string;
    summary?: string;
    count?: number;
  };
}