import React, { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Sidebar from './components/Sidebar';

// Optimization: Lazy load route components to enable code splitting.
// Separates heavy dependencies (like FullCalendar in CalendarView) into separate chunks,
// reducing initial bundle size from ~566 kB down to < 100 kB for faster initial page loads.
const Dashboard = lazy(() => import('./pages/Dashboard'));
const ToolsPanel = lazy(() => import('./pages/ToolsPanel'));
const DataLogs = lazy(() => import('./pages/DataLogs'));
const DataDisplay = lazy(() => import('./components/DataDisplay'));
const CalendarView = lazy(() => import('./components/CalendarView'));

const PageLoader = () => (
  <div className="flex h-64 items-center justify-center">
    <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-blue-500"></div>
  </div>
);

function App() {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <Suspense fallback={<PageLoader />}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/tools" element={<ToolsPanel />} />
              <Route path="/data" element={<DataLogs />} />
              <Route path="/display" element={<DataDisplay />} />
              <Route path="/calendar" element={<CalendarView />} />
            </Routes>
          </Suspense>
        </main>
      </div>
    </div>
  );
}

export default App;
