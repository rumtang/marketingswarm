import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { TrendingUp, AlertTriangle, Info } from 'lucide-react';

export function CapacityForecast({ forecast }) {
  if (!forecast || !forecast.predictions) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-bold mb-4">24-Hour Capacity Forecast</h2>
        <p className="text-gray-500">Loading forecast data...</p>
      </div>
    );
  }

  const chartData = forecast.predictions.map(pred => ({
    hour: pred.hour,
    time: new Date(pred.time).getHours() + ':00',
    occupancy: Math.round(pred.predicted_occupancy * 100),
    available: pred.predicted_available,
  }));

  const currentOccupancy = Math.round(forecast.current_occupancy * 100);

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">24-Hour Capacity Forecast</h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">Current:</span>
          <span className={cn(
            'text-lg font-semibold',
            currentOccupancy > 90 ? 'text-red-600' : 
            currentOccupancy > 80 ? 'text-yellow-600' : 
            'text-green-600'
          )}>
            {currentOccupancy}%
          </span>
        </div>
      </div>

      <div className="h-64 mb-4">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis domain={[0, 100]} />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload[0]) {
                  return (
                    <div className="bg-white p-3 border rounded shadow-md">
                      <p className="font-semibold">{payload[0].payload.time}</p>
                      <p className="text-sm">Occupancy: {payload[0].value}%</p>
                      <p className="text-sm">Available beds: {payload[0].payload.available}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <ReferenceLine y={90} stroke="red" strokeDasharray="3 3" />
            <ReferenceLine y={85} stroke="orange" strokeDasharray="3 3" />
            <Line
              type="monotone"
              dataKey="occupancy"
              stroke="#0066CC"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* AI Insights */}
      {forecast.insights && forecast.insights.length > 0 && (
        <div className="space-y-3">
          <h3 className="font-semibold text-sm text-gray-700 mb-2">AI Insights</h3>
          {forecast.insights.map((insight, idx) => (
            <div
              key={idx}
              className={cn(
                'p-3 rounded-lg border flex gap-3',
                insight.priority === 'high' ? 'bg-red-50 border-red-200' :
                insight.priority === 'medium' ? 'bg-yellow-50 border-yellow-200' :
                'bg-blue-50 border-blue-200'
              )}
            >
              <div className="flex-shrink-0">
                {insight.type === 'warning' ? (
                  <AlertTriangle className="w-5 h-5 text-yellow-600" />
                ) : insight.type === 'opportunity' ? (
                  <TrendingUp className="w-5 h-5 text-green-600" />
                ) : (
                  <Info className="w-5 h-5 text-blue-600" />
                )}
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium">{insight.message}</p>
                <p className="text-xs text-gray-600 mt-1">{insight.recommendation}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function cn(...classes) {
  return classes.filter(Boolean).join(' ');
}