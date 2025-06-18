import React, { useState, useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import { useQuery } from 'react-query';
import axios from 'axios';

// Components
import Header from './components/Header';
import ConversationInterface from './components/ConversationInterface';
import EnhancedConversation from './components/EnhancedConversation';
import SystemStatusDashboard from './components/SystemStatusDashboard';
import DevelopmentConsole from './components/DevelopmentConsole';

// Utils
import { ConnectionTester } from './utils/ConnectionTester';

function App() {
  const [currentView, setCurrentView] = useState('conversation');
  const [isDemoMode, setIsDemoMode] = useState(false);
  
  // Check system health on mount
  const { data: healthStatus, isLoading: healthLoading } = useQuery(
    'health',
    async () => {
      const response = await axios.get('/api/health');
      return response.data;
    },
    {
      refetchInterval: 30000, // Check every 30 seconds
    }
  );

  // Check launch status
  const { data: launchStatus } = useQuery(
    'launchStatus',
    async () => {
      const response = await axios.get('/api/launch-status');
      return response.data;
    },
    {
      refetchInterval: 10000, // Check every 10 seconds
    }
  );

  // Run connection tests in development
  useEffect(() => {
    if (process.env.NODE_ENV === 'development' && window.connectionTester) {
      window.connectionTester = new ConnectionTester();
      // Run tests after 2 seconds to let everything initialize
      setTimeout(() => {
        window.connectionTester.runAllTests();
      }, 2000);
    }
  }, []);

  const renderView = () => {
    switch (currentView) {
      case 'conversation':
        return <EnhancedConversation isDemoMode={isDemoMode} />;
      case 'status':
        return <SystemStatusDashboard healthStatus={healthStatus} launchStatus={launchStatus} />;
      case 'console':
        return <DevelopmentConsole />;
      default:
        return <EnhancedConversation isDemoMode={isDemoMode} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
      
      <Header 
        currentView={currentView}
        setCurrentView={setCurrentView}
        healthStatus={healthStatus}
        launchStatus={launchStatus}
        isDemoMode={isDemoMode}
        setIsDemoMode={setIsDemoMode}
      />
      
      <main className="container mx-auto px-4 py-8">
        {healthLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Initializing Marketing Swarm...</p>
            </div>
          </div>
        ) : (
          renderView()
        )}
      </main>
    </div>
  );
}

export default App;