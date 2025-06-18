import React from 'react';
import { motion } from 'framer-motion';
import { 
  ChatBubbleLeftRightIcon, 
  ChartBarIcon, 
  CommandLineIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon 
} from '@heroicons/react/24/outline';

const Header = ({ 
  currentView, 
  setCurrentView, 
  healthStatus, 
  launchStatus,
  isDemoMode,
  setIsDemoMode 
}) => {
  const navItems = [
    { id: 'conversation', label: 'Conversation', icon: ChatBubbleLeftRightIcon },
    { id: 'status', label: 'System Status', icon: ChartBarIcon },
    { id: 'console', label: 'Dev Console', icon: CommandLineIcon },
  ];

  const getSystemStatus = () => {
    if (!healthStatus) return { color: 'bg-gray-500', text: 'Unknown' };
    if (healthStatus.status === 'healthy') return { color: 'bg-green-500', text: 'Healthy' };
    if (healthStatus.status === 'degraded') return { color: 'bg-yellow-500', text: 'Degraded' };
    return { color: 'bg-red-500', text: 'Error' };
  };

  const systemStatus = getSystemStatus();

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Title */}
          <div className="flex items-center space-x-4">
            <motion.div
              initial={{ rotate: 0 }}
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
              className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center"
            >
              <span className="text-white font-bold text-xl">M</span>
            </motion.div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">Marketing Swarm</h1>
              <p className="text-xs text-gray-500">AI Agent Collaboration Demo</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex items-center space-x-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setCurrentView(item.id)}
                className={`
                  flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors
                  ${currentView === item.id 
                    ? 'bg-primary-100 text-primary-700' 
                    : 'text-gray-600 hover:bg-gray-100'
                  }
                `}
              >
                <item.icon className="w-5 h-5" />
                <span className="text-sm font-medium">{item.label}</span>
              </button>
            ))}
          </nav>

          {/* Status and Controls */}
          <div className="flex items-center space-x-4">
            {/* Demo Mode Toggle */}
            <button
              onClick={() => setIsDemoMode(!isDemoMode)}
              className={`
                px-3 py-1 rounded-full text-xs font-medium transition-colors
                ${isDemoMode 
                  ? 'bg-orange-100 text-orange-700 border border-orange-300' 
                  : 'bg-gray-100 text-gray-600 border border-gray-300'
                }
              `}
            >
              {isDemoMode ? 'Demo Mode ON' : 'Demo Mode OFF'}
            </button>

            {/* System Status */}
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${systemStatus.color} animate-pulse`}></div>
              <span className="text-sm text-gray-600">{systemStatus.text}</span>
            </div>

            {/* Launch Readiness */}
            {launchStatus && (
              <div className="flex items-center space-x-1">
                {launchStatus.ready_for_demo ? (
                  <CheckCircleIcon className="w-5 h-5 text-green-500" />
                ) : (
                  <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500" />
                )}
                <span className="text-sm text-gray-600">
                  {launchStatus.percentage}% Ready
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;