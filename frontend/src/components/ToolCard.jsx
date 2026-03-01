import React from 'react';

const ToolCard = ({ title, icon, description, onClick, isActive = false }) => {
  return (
    <div
      onClick={onClick}
      className={`p-6 rounded-lg border-2 cursor-pointer transition-all transform hover:scale-105 ${
        isActive
          ? 'border-blue-500 bg-blue-50 shadow-md'
          : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
      }`}
    >
      <div className="flex items-center mb-3">
        <span className="text-2xl mr-3">{icon}</span>
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
      </div>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  );
};

export default ToolCard;