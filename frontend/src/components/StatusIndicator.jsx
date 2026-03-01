import React from 'react';

const StatusIndicator = ({ status, label, details }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'connected':
      case 'active':
      case 'success':
        return 'bg-green-500';
      case 'disconnected':
      case 'inactive':
      case 'error':
        return 'bg-red-500';
      case 'warning':
      case 'pending':
        return 'bg-yellow-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'connected':
        return 'Connected';
      case 'disconnected':
        return 'Disconnected';
      case 'active':
        return 'Active';
      case 'inactive':
        return 'Inactive';
      case 'loading':
        return 'Loading...';
      case 'error':
        return 'Error';
      default:
        return status;
    }
  };

  return (
    <div className="flex items-center">
      <div className="flex items-center">
        <span className={`w-2 h-2 rounded-full mr-2 ${getStatusColor(status)}`}></span>
        <span className="text-sm font-medium text-gray-700">{label}</span>
      </div>
      {details && (
        <span className="ml-2 text-sm text-gray-500">{details}</span>
      )}
    </div>
  );
};

export default StatusIndicator;