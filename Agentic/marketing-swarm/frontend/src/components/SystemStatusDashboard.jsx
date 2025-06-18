import React from 'react';
import { motion } from 'framer-motion';
import { 
  CheckCircleIcon, 
  XCircleIcon, 
  ExclamationTriangleIcon,
  ArrowPathIcon 
} from '@heroicons/react/24/outline';

const SystemStatusDashboard = ({ healthStatus, launchStatus }) => {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
      case 'complete':
        return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'warning':
      case 'in_progress':
        return <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500" />;
      case 'error':
      case 'pending':
        return <XCircleIcon className="w-5 h-5 text-red-500" />;
      default:
        return <ArrowPathIcon className="w-5 h-5 text-gray-500 animate-spin" />;
    }
  };

  const StatusCard = ({ title, status, details }) => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          <p className="text-sm text-gray-600 mt-1">{details}</p>
        </div>
        {getStatusIcon(status)}
      </div>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Overall Health */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatusCard 
          title="Backend API"
          status={healthStatus?.status || 'unknown'}
          details={`Uptime: ${healthStatus?.uptime || 0}s`}
        />
        <StatusCard 
          title="WebSocket"
          status={healthStatus?.components?.websocket || 'unknown'}
          details="Real-time communication"
        />
        <StatusCard 
          title="OpenAI API"
          status={healthStatus?.components?.openai_api || 'unknown'}
          details="AI connectivity"
        />
        <StatusCard 
          title="Agents"
          status={healthStatus?.components?.agents || 'unknown'}
          details="Marketing team status"
        />
      </div>

      {/* Launch Progression */}
      {launchStatus && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Launch Progression</h2>
          
          {/* Progress Bar */}
          <div className="mb-8">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Overall Progress</span>
              <span>{launchStatus.overall_progress}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <motion.div 
                className="bg-primary-600 h-3 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${launchStatus.percentage}%` }}
                transition={{ duration: 1, ease: "easeOut" }}
              />
            </div>
          </div>

          {/* Phase Status */}
          <div className="space-y-4">
            {Object.entries(launchStatus.phases || {}).map(([phaseId, phase]) => (
              <div key={phaseId} className="border-l-4 border-gray-200 pl-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(phase.status)}
                    <div>
                      <h4 className="font-medium text-gray-900">{phase.name}</h4>
                      {phase.completed && phase.checks && (
                        <p className="text-sm text-gray-600">
                          {phase.completed.length}/{phase.checks.length} checks passed
                        </p>
                      )}
                    </div>
                  </div>
                  <span className={`
                    px-2 py-1 text-xs font-medium rounded-full
                    ${phase.status === 'complete' ? 'bg-green-100 text-green-800' : ''}
                    ${phase.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' : ''}
                    ${phase.status === 'pending' ? 'bg-gray-100 text-gray-800' : ''}
                  `}>
                    {phase.status}
                  </span>
                </div>
                
                {/* Show missing checks if any */}
                {phase.status !== 'complete' && phase.checks && phase.completed && (
                  <div className="mt-2 text-xs text-gray-500">
                    Missing: {phase.checks.filter(c => !phase.completed.includes(c)).join(', ')}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Blocking Issues */}
          {launchStatus.blocking_issues && launchStatus.blocking_issues.length > 0 && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <h3 className="text-sm font-medium text-red-800 mb-2">Blocking Issues</h3>
              <ul className="space-y-1">
                {launchStatus.blocking_issues.map((issue, idx) => (
                  <li key={idx} className="text-sm text-red-700">
                    {issue.phase}: {issue.missing ? issue.missing.join(', ') : 'Unknown issues'}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Demo Readiness */}
          <div className={`
            mt-6 p-4 rounded-lg
            ${launchStatus.ready_for_demo 
              ? 'bg-green-50 border border-green-200' 
              : 'bg-yellow-50 border border-yellow-200'
            }
          `}>
            <div className="flex items-center space-x-2">
              {launchStatus.ready_for_demo ? (
                <>
                  <CheckCircleIcon className="w-5 h-5 text-green-600" />
                  <span className="text-green-800 font-medium">System ready for demo!</span>
                </>
              ) : (
                <>
                  <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600" />
                  <span className="text-yellow-800 font-medium">
                    System not ready for demo - resolve blocking issues first
                  </span>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SystemStatusDashboard;