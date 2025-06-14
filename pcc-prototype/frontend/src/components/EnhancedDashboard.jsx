import React from 'react';
import { 
  Activity, Users, Clock, TrendingUp, TrendingDown, 
  Sparkles, AlertCircle, Heart, Brain 
} from 'lucide-react';

export function EnhancedDashboard({ stats }) {
  const metrics = [
    {
      label: 'Total Beds',
      value: stats.totalBeds,
      icon: Users,
      color: 'text-gray-900',
      bgColor: 'bg-gray-100',
      trend: null
    },
    {
      label: 'Occupied',
      value: stats.occupiedBeds,
      icon: Activity,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      trend: stats.occupancyTrend || 'stable',
      trendValue: stats.occupancyChange || '+2'
    },
    {
      label: 'Available',
      value: stats.availableBeds,
      icon: Heart,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      trend: null
    },
    {
      label: 'Occupancy',
      value: `${stats.occupancyRate.toFixed(1)}%`,
      icon: TrendingUp,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      trend: stats.occupancyRate > 85 ? 'high' : 'normal',
      alert: stats.occupancyRate > 90
    },
    {
      label: 'Avg LOS',
      value: `${stats.avgLOS.toFixed(1)}d`,
      icon: Clock,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      trend: stats.losTrend || 'improving',
      trendValue: stats.losChange || '-0.3d'
    }
  ];

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'up':
      case 'increasing':
        return <TrendingUp className="w-3 h-3 text-red-500" />;
      case 'down':
      case 'improving':
        return <TrendingDown className="w-3 h-3 text-green-500" />;
      case 'high':
        return <AlertCircle className="w-3 h-3 text-orange-500" />;
      default:
        return null;
    }
  };

  return (
    <div className="bg-white border-b px-6 py-4">

      <div className="grid grid-cols-5 gap-6">
        {metrics.map((metric, index) => {
          const Icon = metric.icon;
          return (
            <div 
              key={metric.label}
              className="relative animate-fade-in"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              {/* Alert indicator */}
              {metric.alert && (
                <div className="absolute -top-2 -right-2 w-3 h-3 bg-red-500 rounded-full animate-ping" />
              )}
              
              <div className={`
                rounded-lg p-4 transition-all duration-300 hover:shadow-md
                ${metric.bgColor}
              `}>
                <div className="flex items-center justify-between mb-2">
                  <Icon className={`w-5 h-5 ${metric.color}`} />
                  {metric.trend && (
                    <div className="flex items-center gap-1">
                      {getTrendIcon(metric.trend)}
                      {metric.trendValue && (
                        <span className="text-xs text-gray-600">
                          {metric.trendValue}
                        </span>
                      )}
                    </div>
                  )}
                </div>
                
                <div className={`text-3xl font-bold ${metric.color} mb-1`}>
                  {metric.value}
                </div>
                
                <div className="text-sm text-gray-600">
                  {metric.label}
                </div>

                
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
}