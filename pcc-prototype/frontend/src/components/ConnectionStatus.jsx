import React from 'react';
import { Wifi, WifiOff, RefreshCw, AlertCircle } from 'lucide-react';

export function ConnectionStatus({ connectionStatus, reconnectAttempts }) {
  const getStatusConfig = () => {
    switch (connectionStatus) {
      case 'connected':
        return {
          icon: <Wifi className="w-4 h-4" />,
          text: 'Connected',
          bgColor: 'bg-green-100',
          textColor: 'text-green-700',
          dotColor: 'bg-green-500',
          pulse: false,
        };
      case 'connecting':
        return {
          icon: <RefreshCw className="w-4 h-4 animate-spin" />,
          text: 'Connecting...',
          bgColor: 'bg-yellow-100',
          textColor: 'text-yellow-700',
          dotColor: 'bg-yellow-500',
          pulse: true,
        };
      case 'reconnecting':
        return {
          icon: <RefreshCw className="w-4 h-4 animate-spin" />,
          text: `Reconnecting... (${reconnectAttempts})`,
          bgColor: 'bg-orange-100',
          textColor: 'text-orange-700',
          dotColor: 'bg-orange-500',
          pulse: true,
        };
      case 'error':
        return {
          icon: <AlertCircle className="w-4 h-4" />,
          text: 'Connection Error',
          bgColor: 'bg-red-100',
          textColor: 'text-red-700',
          dotColor: 'bg-red-500',
          pulse: false,
        };
      default:
        return {
          icon: <WifiOff className="w-4 h-4" />,
          text: 'Disconnected',
          bgColor: 'bg-gray-100',
          textColor: 'text-gray-700',
          dotColor: 'bg-gray-500',
          pulse: false,
        };
    }
  };

  const config = getStatusConfig();

  return (
    <div 
      className={`
        flex items-center gap-2 px-3 py-1.5 rounded-full transition-all duration-300
        ${config.bgColor} ${config.textColor}
      `}
    >
      <div className="relative">
        <div 
          className={`
            w-2 h-2 rounded-full ${config.dotColor}
            ${config.pulse ? 'animate-pulse' : ''}
          `} 
        />
        {config.pulse && (
          <div 
            className={`
              absolute inset-0 w-2 h-2 rounded-full ${config.dotColor}
              animate-ping opacity-75
            `}
          />
        )}
      </div>
      <div className="flex items-center gap-1.5">
        {config.icon}
        <span className="text-sm font-medium">{config.text}</span>
      </div>
    </div>
  );
}