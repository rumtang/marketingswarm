import React, { useState, useEffect } from 'react';
import { Activity, Users, Clock, TrendingUp, LogIn } from 'lucide-react';
import { useWebSocket } from './hooks/useWebSocket';
import { EnhancedBedCard } from './components/EnhancedBedCard';
import { CapacityForecast } from './components/CapacityForecast';
import { EnhancedAlertsFeed } from './components/EnhancedAlertsFeed';
import { PatientDetailsModal } from './components/PatientDetailsModal';
import { ChatInterface } from './components/ChatInterface';
import { ConnectionStatus } from './components/ConnectionStatus';
import { EnhancedDashboard } from './components/EnhancedDashboard';
import ErrorBoundary from './components/ErrorBoundary';
import { isAuthenticated, loginWithDemoCredentials, authenticatedFetch, logout } from './utils/auth';

function App() {
  const [beds, setBeds] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [selectedBed, setSelectedBed] = useState(null);
  const [narrativeData, setNarrativeData] = useState({});
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [loginError, setLoginError] = useState(null);
  const [stats, setStats] = useState({
    totalBeds: 200,
    occupiedBeds: 0,
    availableBeds: 0,
    occupancyRate: 0,
    avgLOS: 0,
  });

  const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
  const { isConnected, connectionStatus, lastMessage, reconnectAttempts } = useWebSocket(wsUrl);

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      if (isAuthenticated()) {
        setIsLoggedIn(true);
      } else {
        // Auto-login with demo credentials
        setIsLoggingIn(true);
        const result = await loginWithDemoCredentials();
        if (result.success) {
          setIsLoggedIn(true);
          setLoginError(null);
        } else {
          setLoginError(result.error);
        }
        setIsLoggingIn(false);
      }
    };
    checkAuth();
  }, []);

  // Fetch initial data when authenticated
  useEffect(() => {
    if (isLoggedIn) {
      fetchBedStatus();
      fetchCapacityForecast();
      fetchAlerts();
    }
  }, [isLoggedIn]);

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      if (lastMessage.type === 'initial_status') {
        updateBedStatus(lastMessage.data.bed_status);
      } else if (lastMessage.type === 'bed_update') {
        updateBedStatus(lastMessage.data.bed_status);
        if (lastMessage.data.prediction) {
          setForecast(lastMessage.data.prediction);
        }
        if (lastMessage.data.barriers && lastMessage.data.barriers.length > 0) {
          // Add barrier alerts
          const newAlert = {
            id: Date.now().toString(),
            type: 'barrier_detected',
            severity: 'medium',
            message: `New barriers detected for patient ${lastMessage.data.event.patient_id}`,
            timestamp: new Date().toISOString(),
          };
          setAlerts((prev) => [newAlert, ...prev].slice(0, 20));
        }
      } else if (lastMessage.type === 'narrative_update') {
        // Handle narrative updates for enhanced UI
        const { bed_id, narrative_data } = lastMessage.data;
        setNarrativeData(prev => ({
          ...prev,
          [bed_id]: narrative_data
        }));
      } else if (lastMessage.type === 'narrative_insight') {
        // Add AI-generated narrative insights
        const newAlert = {
          id: Date.now().toString(),
          type: 'narrative_insight',
          severity: 'high',
          message: lastMessage.data.message,
          recommendation: lastMessage.data.recommendation,
          timestamp: new Date().toISOString(),
          data: {
            significance: lastMessage.data.significance,
            bed_id: lastMessage.data.bed_id
          }
        };
        setAlerts((prev) => [newAlert, ...prev].slice(0, 20));
      }
    }
  }, [lastMessage]);


  const fetchBedStatus = async () => {
    try {
      const response = await authenticatedFetch(`${import.meta.env.VITE_API_URL}/api/bed-status`);
      if (response.status === 401) {
        // Token expired, re-login
        setIsLoggedIn(false);
        return;
      }
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      // Validate data before setting state
      if (data && data.beds && Array.isArray(data.beds)) {
        updateBedStatus(data.beds);
      } else {
        console.error('Invalid bed status data:', data);
        setBeds([]);
      }
    } catch (error) {
      console.error('Error fetching bed status:', error);
      setBeds([]);
    }
  };

  const fetchCapacityForecast = async () => {
    try {
      const response = await authenticatedFetch(`${import.meta.env.VITE_API_URL}/api/capacity-forecast`);
      if (response.status === 401) {
        setIsLoggedIn(false);
        return;
      }
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (data && data.forecast) {
        setForecast(data.forecast);
      }
    } catch (error) {
      console.error('Error fetching forecast:', error);
    }
  };

  const fetchAlerts = async () => {
    try {
      const response = await authenticatedFetch(`${import.meta.env.VITE_API_URL}/api/alerts`);
      if (response.status === 401) {
        setIsLoggedIn(false);
        return;
      }
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (data && data.alerts && Array.isArray(data.alerts)) {
        setAlerts(data.alerts);
      }
    } catch (error) {
      console.error('Error fetching alerts:', error);
    }
  };

  const updateBedStatus = (bedData) => {
    setBeds(bedData);
    
    // Calculate stats
    const occupied = bedData.filter((b) => b.status === 'occupied').length;
    const available = bedData.filter((b) => b.status === 'available').length;
    
    // Calculate average LOS
    let totalLOS = 0;
    let losCount = 0;
    bedData.forEach((bed) => {
      if (bed.status === 'occupied' && bed.admission_time) {
        const admissionTime = new Date(bed.admission_time);
        const now = new Date();
        const hours = (now - admissionTime) / (1000 * 60 * 60);
        totalLOS += hours;
        losCount++;
      }
    });
    
    setStats({
      totalBeds: bedData.length,
      occupiedBeds: occupied,
      availableBeds: available,
      occupancyRate: bedData.length > 0 ? (occupied / bedData.length) * 100 : 0,
      avgLOS: losCount > 0 ? totalLOS / losCount / 24 : 0, // Convert to days
    });
  };

  // Group beds by unit (ensure beds is an array)
  const bedsByUnit = (beds && Array.isArray(beds) ? beds : []).reduce((acc, bed) => {
    if (!acc[bed.unit]) {
      acc[bed.unit] = [];
    }
    acc[bed.unit].push(bed);
    return acc;
  }, {});

  // Show login screen if not authenticated
  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-xl shadow-lg max-w-md w-full">
          <div className="text-center mb-6">
            <Activity className="w-16 h-16 text-hospital-blue mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900">Patient Command Center</h1>
            <p className="text-gray-600 mt-2">AI-Powered Healthcare Management</p>
          </div>
          
          {isLoggingIn ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-hospital-blue mx-auto"></div>
              <p className="mt-4 text-gray-600">Logging in with demo credentials...</p>
            </div>
          ) : loginError ? (
            <div className="text-center py-8">
              <p className="text-red-600 mb-4">Authentication failed: {loginError}</p>
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-hospital-blue text-white rounded hover:bg-blue-600 transition-colors"
              >
                Retry
              </button>
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-600">Preparing authentication...</p>
            </div>
          )}
          
          <div className="mt-6 text-center text-sm text-gray-500">
            Demo Mode • Username: admin • Password: admin123
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 animate-fade-in">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="px-6 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Activity className="w-8 h-8 text-hospital-blue" />
              Patient Command Center
              <span className="ml-2 px-2 py-1 text-xs font-medium bg-purple-100 text-purple-700 rounded-full animate-pulse">
                AI-Powered
              </span>
            </h1>
            <div className="flex items-center gap-4">
              <ConnectionStatus 
                connectionStatus={connectionStatus} 
                reconnectAttempts={reconnectAttempts} 
              />
              <button
                onClick={() => {
                  logout();
                  setIsLoggedIn(false);
                  window.location.reload();
                }}
                className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 transition-colors"
                title="Logout"
              >
                <LogIn className="w-4 h-4" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Enhanced Dashboard */}
      <EnhancedDashboard stats={stats} />

      {/* Main Content */}
      <div className="flex">
        {/* Left Panel - Bed Grid */}
        <div className="flex-1 p-6">
          <div className="space-y-6">
            {Object.entries(bedsByUnit).map(([unit, unitBeds]) => (
              <div key={unit} className="bg-white rounded-xl shadow-lg p-5 animate-fade-in" style={{ animationDelay: `${Object.keys(bedsByUnit).indexOf(unit) * 100}ms` }}>
                <h2 className="text-lg font-semibold mb-4 flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    {unit}
                    {unit === 'ICU' && stats.occupancyRate > 85 && (
                      <span className="px-2 py-0.5 text-xs bg-red-100 text-red-700 rounded-full animate-pulse">
                        High Acuity
                      </span>
                    )}
                  </span>
                  <span className="text-sm font-normal text-gray-600">
                    {unitBeds.filter(b => b.status === 'occupied').length}/{unitBeds.length} occupied
                  </span>
                </h2>
                <div className="bed-grid">
                  {unitBeds.map((bed) => (
                    <EnhancedBedCard
                      key={bed.bed_id}
                      bed={bed}
                      onClick={setSelectedBed}
                      narrativeData={narrativeData[bed.bed_id]}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Panel - Analytics */}
        <div className="w-[450px] p-6 space-y-6">
          <ErrorBoundary>
            <CapacityForecast forecast={forecast} />
          </ErrorBoundary>
          <ErrorBoundary>
            <EnhancedAlertsFeed alerts={alerts} />
          </ErrorBoundary>
        </div>
      </div>

      {/* Patient Details Modal */}
      {selectedBed && (
        <PatientDetailsModal
          bed={selectedBed}
          onClose={() => setSelectedBed(null)}
        />
      )}

      {/* Chat Interface */}
      <ChatInterface />
    </div>
  );
}

export default App;