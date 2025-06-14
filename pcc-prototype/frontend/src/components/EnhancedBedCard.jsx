import React, { useState, useEffect } from 'react';
import { Clock, AlertCircle, User, Heart, TrendingUp, Sparkles } from 'lucide-react';
import { cn, getBedStatusColor, formatDuration } from '../lib/utils';

export function EnhancedBedCard({ bed, onClick, narrativeData }) {
  const [isNew, setIsNew] = useState(false);
  const [isUpdated, setIsUpdated] = useState(false);
  const hasBarriers = bed.discharge_barriers && bed.discharge_barriers.length > 0;
  const isOccupied = bed.status === 'occupied';
  
  // Detect new admissions or updates
  useEffect(() => {
    if (bed.lastUpdated) {
      const updateTime = new Date(bed.lastUpdated);
      const now = new Date();
      const diffMinutes = (now - updateTime) / (1000 * 60);
      
      if (diffMinutes < 1) {
        setIsNew(true);
        setTimeout(() => setIsNew(false), 3000);
      } else if (diffMinutes < 5) {
        setIsUpdated(true);
        setTimeout(() => setIsUpdated(false), 3000);
      }
    }
  }, [bed.lastUpdated]);
  
  const calculateLOS = () => {
    if (!bed.admission_time) return null;
    const admissionTime = new Date(bed.admission_time);
    const now = new Date();
    const hours = (now - admissionTime) / (1000 * 60 * 60);
    return hours;
  };

  const los = calculateLOS();
  const emotionalState = narrativeData?.emotional_state;
  const recentEvent = narrativeData?.recent_events?.[0];

  const getEmotionalIcon = () => {
    switch (emotionalState) {
      case 'anxious': return <Heart className="w-3 h-3 text-orange-500" />;
      case 'hopeful': return <TrendingUp className="w-3 h-3 text-green-500" />;
      case 'content': return <Heart className="w-3 h-3 text-blue-500" />;
      default: return null;
    }
  };

  return (
    <div
      onClick={() => onClick(bed)}
      className={cn(
        'relative p-3 rounded-lg border-2 cursor-pointer',
        'transform transition-all duration-300 hover:scale-105 hover:shadow-lg',
        getBedStatusColor(bed.status, hasBarriers),
        isNew && 'animate-glow ring-2 ring-blue-400 ring-opacity-50',
        isUpdated && 'animate-pulse-subtle'
      )}
    >
      {/* New/Updated Badge */}
      {(isNew || isUpdated) && (
        <div className={cn(
          'absolute -top-2 -right-2 px-2 py-0.5 rounded-full text-xs font-bold',
          'animate-bounce-gentle',
          isNew ? 'bg-blue-500 text-white' : 'bg-yellow-500 text-white'
        )}>
          {isNew ? 'NEW' : 'UPDATED'}
        </div>
      )}

      {/* Wow moment indicator */}
      {narrativeData?.wow_moment && (
        <Sparkles className="absolute top-2 left-2 w-4 h-4 text-yellow-500 animate-sparkle" />
      )}

      <div className="flex justify-between items-start mb-2">
        <h3 className="font-bold text-sm">{bed.bed_id}</h3>
        <div className="flex items-center gap-1">
          {getEmotionalIcon()}
          {hasBarriers && (
            <AlertCircle className="w-4 h-4 text-yellow-600" />
          )}
        </div>
      </div>

      {isOccupied ? (
        <>
          <div className="flex items-center gap-1 text-xs text-gray-600 mb-1">
            <User className="w-3 h-3" />
            <span className="truncate font-medium">{bed.patient_name || 'Patient'}</span>
          </div>
          
          {los && (
            <div className="flex items-center gap-1 text-xs text-gray-500">
              <Clock className="w-3 h-3" />
              <span>LOS: {formatDuration(los)}</span>
            </div>
          )}

          {bed.diagnosis && (
            <div className="text-xs text-gray-600 mt-1 truncate">
              {bed.diagnosis}
            </div>
          )}

          {/* Narrative preview */}
          {recentEvent && (
            <div className="mt-2 text-xs text-gray-500 italic truncate animate-fade-in">
              "{recentEvent}"
            </div>
          )}

          {/* Progress indicator */}
          {bed.expected_discharge && (
            <div className="mt-2">
              <div className="flex justify-between text-xs text-gray-500 mb-1">
                <span>Discharge Progress</span>
                <span>{bed.discharge_progress || '60'}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
                <div 
                  className="bg-gradient-to-r from-blue-400 to-green-400 h-full rounded-full transition-all duration-1000"
                  style={{ width: `${bed.discharge_progress || 60}%` }}
                />
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="text-sm text-gray-500 mt-4 flex items-center gap-1">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          Available
        </div>
      )}

      {/* Status indicator with animation */}
      <div className={cn(
        'absolute top-2 right-2 w-2 h-2 rounded-full transition-all duration-300',
        bed.status === 'available' ? 'bg-gray-400' : 
        hasBarriers ? 'bg-yellow-500' : 
        'bg-blue-500'
      )}>
        {hasBarriers && (
          <div className="absolute inset-0 w-2 h-2 rounded-full bg-yellow-500 animate-ping opacity-75" />
        )}
      </div>
    </div>
  );
}