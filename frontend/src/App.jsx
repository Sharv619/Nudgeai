import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import ToolsPanel from './pages/ToolsPanel';
import DataLogs from './pages/DataLogs';
import DataDisplay from './components/DataDisplay';
import CalendarView from './components/CalendarView';
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
            <Route path="/data" element={<DataLogs />} />
            <Route path="/display" element={<DataDisplay />} />
            <Route path="/calendar" element={<CalendarView />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;
