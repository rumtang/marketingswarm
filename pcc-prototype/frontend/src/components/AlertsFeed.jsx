import React from 'react';
import { Bell, AlertCircle, CheckCircle, Info, Clock } from 'lucide-react';
import { formatTimestamp } from '../lib/utils';

export function AlertsFeed({ alerts }) {
  const getAlertIcon = (type) => {
    switch (type) {
      case 'barrier_detected':
        return <AlertCircle className="w-4 h-4 text-yellow-600" />;
      case 'discharge_ready':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'high_occupancy':
        return <Bell className="w-4 h-4 text-red-600" />;
      default:
        return <Info className="w-4 h-4 text-blue-600" />;
    }
  };

  const getAlertStyle = (severity) => {
    switch (severity) {
      case 'high':
        return 'border-red-200 bg-red-50';
      case 'medium':
        return 'border-yellow-200 bg-yellow-50';
      default:
        return 'border-blue-200 bg-blue-50';
    }
  };

  // Mock alerts if none provided
  const displayAlerts = alerts || [
    {
      id: '1',
      type: 'barrier_detected',
      severity: 'medium',
      message: 'Lab results pending for 3 discharge-ready patients',
      timestamp: new Date().toISOString(),
    },
    {
      id: '2',
      type: 'high_occupancy',
      severity: 'high',
      message: 'ICU occupancy at 95% - consider transfers',
      timestamp: new Date(Date.now() - 15 * 60000).toISOString(),
    },
    {
      id: '3',
      type: 'discharge_ready',
      severity: 'low',
      message: '5 patients ready for morning discharge',
      timestamp: new Date(Date.now() - 30 * 60000).toISOString(),
    },
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
        <Bell className="w-5 h-5" />
        Real-time Alerts
      </h2>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {displayAlerts.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No active alerts</p>
        ) : (
          displayAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-3 rounded-lg border flex gap-3 ${getAlertStyle(alert.severity)}`}
            >
              <div className="flex-shrink-0 mt-0.5">
                {getAlertIcon(alert.type)}
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium">{alert.message}</p>
                <div className="flex items-center gap-1 mt-1 text-xs text-gray-500">
                  <Clock className="w-3 h-3" />
                  <span>{formatTimestamp(alert.timestamp)}</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}