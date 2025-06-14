import React, { useEffect, useState } from 'react';
import { 
  AlertCircle, TrendingUp, Users, Clock, Sparkles, 
  ChevronRight, Heart, Brain, Zap 
} from 'lucide-react';

export function EnhancedAlertsFeed({ alerts = [] }) {
  const [visibleAlerts, setVisibleAlerts] = useState([]);
  
  useEffect(() => {
    // Animate alerts appearing one by one
    alerts.forEach((alert, index) => {
      setTimeout(() => {
        setVisibleAlerts(prev => {
          const exists = prev.find(a => a.id === alert.id);
          if (!exists) {
            return [alert, ...prev].slice(0, 10); // Keep only 10 most recent
          }
          return prev;
        });
      }, index * 100);
    });
  }, [alerts]);

  const getAlertIcon = (type, severity) => {
    if (severity === 'high' || type === 'narrative_insight') {
      return <Sparkles className="w-5 h-5 text-yellow-500 animate-sparkle" />;
    }
    
    switch (type) {
      case 'capacity_warning':
        return <TrendingUp className="w-5 h-5 text-orange-500" />;
      case 'discharge_opportunity':
        return <Clock className="w-5 h-5 text-green-500" />;
      case 'patient_update':
        return <Heart className="w-5 h-5 text-red-500" />;
      case 'ai_insight':
        return <Brain className="w-5 h-5 text-purple-500" />;
      case 'rapid_response':
        return <Zap className="w-5 h-5 text-red-600" />;
      default:
        return <AlertCircle className="w-5 h-5 text-blue-500" />;
    }
  };

  const getAlertStyle = (severity, type) => {
    if (severity === 'high' || type === 'narrative_insight') {
      return 'bg-gradient-to-r from-yellow-50 to-orange-50 border-yellow-300';
    }
    
    switch (severity) {
      case 'critical':
        return 'bg-gradient-to-r from-red-50 to-pink-50 border-red-300';
      case 'medium':
        return 'bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-300';
      default:
        return 'bg-gradient-to-r from-gray-50 to-slate-50 border-gray-300';
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-hospital-blue" />
          Intelligence Feed
        </h2>
        <span className="text-xs text-gray-500 animate-pulse">
          Live Updates
        </span>
      </div>
      
      <div className="space-y-3 max-h-[400px] overflow-y-auto">
        {visibleAlerts.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Brain className="w-12 h-12 mx-auto mb-2 text-gray-300" />
            <p className="text-sm">AI is monitoring all systems</p>
            <p className="text-xs mt-1">Insights will appear here</p>
          </div>
        ) : (
          visibleAlerts.map((alert, index) => (
            <div
              key={alert.id}
              className={`
                p-4 rounded-lg border-l-4 transition-all duration-500
                ${getAlertStyle(alert.severity, alert.type)}
                ${index === 0 ? 'animate-slide-in-right' : ''}
                hover:shadow-md cursor-pointer group
              `}
              style={{
                animationDelay: `${index * 100}ms`,
                opacity: index === 0 ? 1 : 1 - (index * 0.05)
              }}
            >
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 mt-0.5">
                  {getAlertIcon(alert.type, alert.severity)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 leading-tight">
                    {alert.message}
                  </p>
                  
                  {alert.data?.significance && (
                    <p className="text-xs text-gray-600 mt-1 italic">
                      "{alert.data.significance}"
                    </p>
                  )}
                  
                  {alert.recommendation && (
                    <div className="mt-2 flex items-center gap-1 text-xs text-blue-600">
                      <ChevronRight className="w-3 h-3" />
                      <span>{alert.recommendation}</span>
                    </div>
                  )}
                  
                  <div className="flex items-center gap-3 mt-2">
                    <span className="text-xs text-gray-400">
                      {formatTime(alert.timestamp)}
                    </span>
                    
                    {alert.severity === 'high' && (
                      <span className="text-xs font-semibold text-orange-600 animate-pulse">
                        HIGH PRIORITY
                      </span>
                    )}
                    
                    {alert.type === 'narrative_insight' && (
                      <span className="text-xs font-semibold text-purple-600 flex items-center gap-1">
                        <Sparkles className="w-3 h-3" />
                        AI INSIGHT
                      </span>
                    )}
                  </div>
                </div>
                
                <ChevronRight className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
            </div>
          ))
        )}
      </div>
      
      {visibleAlerts.length > 5 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <button className="text-sm text-hospital-blue hover:text-hospital-dark transition-colors">
            View all {alerts.length} alerts →
          </button>
        </div>
      )}
    </div>
  );
}