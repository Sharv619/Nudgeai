import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const navItems = [
  { path: '/', label: 'Nudges', icon: 'N' },
  { path: '/tools', label: 'Experimental Tools', icon: 'T' },
  { path: '/data', label: 'Prototype Logs', icon: 'L' },
  { path: '/display', label: 'Data Display', icon: 'D' },
  { path: '/calendar', label: 'Calendar View', icon: 'C' },
];

const Sidebar = () => {
  const location = useLocation();

  return (
    <aside className="flex w-64 flex-col border-r border-gray-200 bg-white shadow-sm">
      <div className="p-6">
        <h2 className="text-lg font-semibold text-gray-900">NudgeAI</h2>
        <p className="mt-1 text-sm text-gray-500">Manual nudge MVP</p>
      </div>

      <nav className="flex-1 px-4 py-6">
        <ul className="space-y-2">
          {navItems.map((item) => (
            <li key={item.path}>
              <Link
                to={item.path}
                className={`flex items-center rounded-lg px-4 py-3 transition-colors ${
                  location.pathname === item.path
                    ? 'border-r-2 border-blue-700 bg-blue-50 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <span className="mr-3 flex h-6 w-6 items-center justify-center rounded bg-gray-100 text-xs font-semibold text-gray-700">
                  {item.icon}
                </span>
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      <div className="border-t border-gray-200 p-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500">Status</span>
          <span className="flex items-center">
            <span className="mr-2 h-2 w-2 rounded-full bg-green-500"></span>
            <span className="text-green-600">Local MVP</span>
          </span>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
