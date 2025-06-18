import React, { useState, useEffect, useRef } from 'react';
// import { motion } from 'framer-motion'; // TODO: Add animations later
import io from 'socket.io-client';
import { format } from 'date-fns';
import { 
  PlayIcon, 
  ArrowPathIcon, 
  TrashIcon,
  BoltIcon 
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const DevelopmentConsole = () => {
  const [logs, setLogs] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState({});
  const [launchStatus, setLaunchStatus] = useState({});
  const [apiCalls, setApiCalls] = useState([]);
  const socketRef = useRef(null);
  const logsEndRef = useRef(null);

  useEffect(() => {
    // Connect to development logging socket
    socketRef.current = io('http://localhost:8000/dev-console', {
      transports: ['websocket'],
    });

    socketRef.current.on('system_log', (logEntry) => {
      setLogs(prev => [...prev.slice(-99), logEntry]); // Keep last 100 logs
    });

    socketRef.current.on('api_call_logged', (callData) => {
      setApiCalls(prev => [...prev.slice(-49), callData]); // Keep last 50 API calls
    });

    socketRef.current.on('connection_status_update', (status) => {
      setConnectionStatus(status);
    });

    // Fetch launch status
    fetchLaunchStatus();
    const statusInterval = setInterval(fetchLaunchStatus, 10000);

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
      clearInterval(statusInterval);
    };
  }, []);

  useEffect(() => {
    // Auto-scroll logs
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const fetchLaunchStatus = async () => {
    try {
      const response = await fetch('/api/launch-status');
      const status = await response.json();
      setLaunchStatus(status);
    } catch (error) {
      console.error('Failed to fetch launch status:', error);
    }
  };

  const runConnectionTests = async () => {
    toast.loading('Running connection tests...');
    
    if (window.connectionTester) {
      const results = await window.connectionTester.runAllTests();
      const failed = Object.values(results).filter(r => r.status === 'fail').length;
      
      if (failed === 0) {
        toast.success('All connection tests passed!');
      } else {
        toast.error(`${failed} connection tests failed`);
      }
    } else {
      toast.error('Connection tester not available');
    }
  };

  const restartAgents = async () => {
    try {
      toast.loading('Restarting agents...');
      const response = await fetch('/api/agents/restart', { method: 'POST' });
      
      if (response.ok) {
        toast.success('Agents restarted successfully');
      } else {
        toast.error('Failed to restart agents');
      }
    } catch (error) {
      toast.error('Error restarting agents');
    }
  };

  const clearLogs = () => {
    setLogs([]);
    toast.success('Logs cleared');
  };

  const ConnectionIndicator = ({ name, status }) => (
    <div className="flex justify-between items-center py-2">
      <span className="text-sm font-mono">{name}:</span>
      <span className={`text-sm font-mono ${
        status === 'connected' ? 'text-green-400' :
        status === 'connecting' ? 'text-yellow-400' : 'text-red-400'
      }`}>
        {status === 'connected' ? '🟢' : 
         status === 'connecting' ? '🟡' : '🔴'} {status?.toUpperCase() || 'UNKNOWN'}
      </span>
    </div>
  );

  return (
    <div className="h-[calc(100vh-12rem)] bg-black text-green-400 font-mono rounded-lg overflow-hidden">
      <div className="flex h-full">
        {/* Launch Status Panel */}
        <div className="w-1/3 border-r border-green-800 p-4 overflow-y-auto">
          <h2 className="text-xl mb-4 text-green-300">🚀 Launch Status</h2>
          
          <div className="mb-4 text-sm">
            <div>Progress: {launchStatus.percentage}% ({launchStatus.overall_progress})</div>
            <div className={launchStatus.ready_for_demo ? 'text-green-400' : 'text-yellow-400'}>
              Demo Ready: {launchStatus.ready_for_demo ? 'YES' : 'NO'}
            </div>
          </div>
          
          {launchStatus.phases && Object.entries(launchStatus.phases).map(([id, phase]) => (
            <div key={id} className="mb-2">
              <div className={`text-sm ${
                phase.status === 'complete' ? 'text-green-400' : 
                phase.status === 'in_progress' ? 'text-yellow-400' : 'text-red-400'
              }`}>
                {phase.status === 'complete' ? '✅' : 
                 phase.status === 'in_progress' ? '🔄' : '❌'} {phase.name}
              </div>
              <div className="text-xs ml-4 text-gray-500">
                {phase.completed.length}/{phase.checks.length} checks
              </div>
            </div>
          ))}

          {launchStatus.blocking_issues && launchStatus.blocking_issues.length > 0 && (
            <div className="mt-4">
              <h3 className="text-red-400 text-sm mb-2">🚨 Blocking Issues:</h3>
              {launchStatus.blocking_issues.map((issue, idx) => (
                <div key={idx} className="text-xs text-red-300 ml-2">
                  {issue.phase}: {issue.missing.join(', ')}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Connection Status Panel */}
        <div className="w-1/3 border-r border-green-800 p-4 overflow-y-auto">
          <h2 className="text-xl mb-4 text-green-300">🔗 Connections</h2>
          
          <div className="space-y-1">
            <ConnectionIndicator name="Backend API" status={connectionStatus.backend_api} />
            <ConnectionIndicator name="WebSocket" status={connectionStatus.websocket} />
            <ConnectionIndicator name="Database" status={connectionStatus.database} />
            <ConnectionIndicator name="OpenAI API" status={connectionStatus.openai_api} />
          </div>

          <div className="mt-6">
            <h3 className="text-sm mb-2 text-green-300">Recent API Calls:</h3>
            <div className="text-xs space-y-1 max-h-40 overflow-y-auto">
              {apiCalls.slice(-10).map((call, idx) => (
                <div key={idx} className={call.success ? 'text-green-400' : 'text-red-400'}>
                  {call.timestamp} - {call.endpoint} ({call.duration}ms)
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Live Logs Panel */}
        <div className="w-1/3 p-4 overflow-y-auto">
          <h2 className="text-xl mb-4 text-green-300">📝 Live Logs</h2>
          <div className="text-xs space-y-1">
            {logs.map((log, idx) => (
              <div key={idx} className={`console-log ${
                log.level === 'ERROR' ? 'console-error' :
                log.level === 'WARN' ? 'console-warn' : 
                log.level === 'INFO' ? 'console-info' : 'console-success'
              }`}>
                [{format(new Date(log.timestamp), 'HH:mm:ss')}] {log.level}: {log.message}
              </div>
            ))}
            <div ref={logsEndRef} />
          </div>
        </div>
      </div>

      {/* Quick Action Buttons */}
      <div className="absolute bottom-4 left-4 flex space-x-2">
        <button 
          className="bg-green-600 text-black px-3 py-1 rounded text-xs flex items-center space-x-1 hover:bg-green-500"
          onClick={runConnectionTests}
        >
          <PlayIcon className="w-4 h-4" />
          <span>Run Tests</span>
        </button>
        <button 
          className="bg-blue-600 text-white px-3 py-1 rounded text-xs flex items-center space-x-1 hover:bg-blue-500"
          onClick={restartAgents}
        >
          <ArrowPathIcon className="w-4 h-4" />
          <span>Restart Agents</span>
        </button>
        <button 
          className="bg-yellow-600 text-black px-3 py-1 rounded text-xs flex items-center space-x-1 hover:bg-yellow-500"
          onClick={clearLogs}
        >
          <TrashIcon className="w-4 h-4" />
          <span>Clear Logs</span>
        </button>
        <button 
          className="bg-red-600 text-white px-3 py-1 rounded text-xs flex items-center space-x-1 hover:bg-red-500"
          onClick={() => fetch('/api/emergency/demo-safe-mode', { method: 'POST' })}
        >
          <BoltIcon className="w-4 h-4" />
          <span>Demo Safe Mode</span>
        </button>
      </div>
    </div>
  );
};

export default DevelopmentConsole;