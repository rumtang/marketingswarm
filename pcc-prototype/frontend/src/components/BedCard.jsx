import React from 'react';
import { Clock, AlertCircle, User } from 'lucide-react';
import { cn, getBedStatusColor, formatDuration } from '../lib/utils';

export function BedCard({ bed, onClick }) {
  const hasBarriers = bed.discharge_barriers && bed.discharge_barriers.length > 0;
  const isOccupied = bed.status === 'occupied';
  
  const calculateLOS = () => {
    if (!bed.admission_time) return null;
    const admissionTime = new Date(bed.admission_time);
    const now = new Date();
    const hours = (now - admissionTime) / (1000 * 60 * 60);
    return hours;
  };

  const los = calculateLOS();

  return (
    <div
      onClick={() => onClick(bed)}
      className={cn(
        'relative p-3 rounded-lg border-2 cursor-pointer card-hover',
        getBedStatusColor(bed.status, hasBarriers),
        'transition-all duration-200'
      )}
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-bold text-sm">{bed.bed_id}</h3>
        {hasBarriers && (
          <AlertCircle className="w-4 h-4 text-yellow-600" />
        )}
      </div>

      {isOccupied ? (
        <>
          <div className="flex items-center gap-1 text-xs text-gray-600 mb-1">
            <User className="w-3 h-3" />
            <span className="truncate">{bed.patient_name || 'Patient'}</span>
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
        </>
      ) : (
        <div className="text-sm text-gray-500 mt-4">
          Available
        </div>
      )}

      {/* Status indicator dot */}
      <div className={cn(
        'absolute top-2 right-2 w-2 h-2 rounded-full',
        bed.status === 'available' ? 'bg-gray-400' : 
        hasBarriers ? 'bg-yellow-500 animate-pulse' : 
        'bg-blue-500'
      )} />
    </div>
  );
}