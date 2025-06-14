import React, { useState, useEffect } from 'react';
import { X, User, Clock, AlertCircle, CheckCircle, MessageSquare } from 'lucide-react';
import { formatDuration, formatTimestamp } from '../lib/utils';

export function PatientDetailsModal({ bed, onClose }) {
  const [barriers, setBarriers] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (bed && bed.patient_id) {
      fetchBarriers();
    }
  }, [bed]);

  const fetchBarriers = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/discharge-barriers/${bed.patient_id}`
      );
      const data = await response.json();
      setBarriers(data);
    } catch (error) {
      console.error('Error fetching barriers:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!bed) return null;

  const calculateLOS = () => {
    if (!bed.admission_time) return null;
    const admissionTime = new Date(bed.admission_time);
    const now = new Date();
    const hours = (now - admissionTime) / (1000 * 60 * 60);
    return hours;
  };

  const los = calculateLOS();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full m-4 max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b p-4 flex justify-between items-center">
          <h2 className="text-xl font-bold">Bed {bed.bed_id} Details</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Patient Information */}
          {bed.status === 'occupied' ? (
            <>
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <User className="w-5 h-5" />
                  Patient Information
                </h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Name:</span>
                    <p className="font-medium">{bed.patient_name || 'Unknown'}</p>
                  </div>
                  <div>
                    <span className="text-gray-600">ID:</span>
                    <p className="font-medium">{bed.patient_id}</p>
                  </div>
                  <div>
                    <span className="text-gray-600">Diagnosis:</span>
                    <p className="font-medium">{bed.diagnosis || 'Pending'}</p>
                  </div>
                  <div>
                    <span className="text-gray-600">Unit:</span>
                    <p className="font-medium">{bed.unit}</p>
                  </div>
                </div>
              </div>

              {/* Length of Stay */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <Clock className="w-5 h-5" />
                  Length of Stay
                </h3>
                <div className="text-sm space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Admission:</span>
                    <span className="font-medium">{formatTimestamp(bed.admission_time)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Current LOS:</span>
                    <span className="font-medium">{los ? formatDuration(los) : 'N/A'}</span>
                  </div>
                  {bed.expected_discharge && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Expected Discharge:</span>
                      <span className="font-medium">{formatTimestamp(bed.expected_discharge)}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Discharge Barriers */}
              {loading ? (
                <div className="text-center py-4">Loading discharge analysis...</div>
              ) : barriers && barriers.barriers && barriers.barriers.length > 0 ? (
                <div className="bg-yellow-50 p-4 rounded-lg">
                  <h3 className="font-semibold mb-3 flex items-center gap-2">
                    <AlertCircle className="w-5 h-5 text-yellow-600" />
                    Discharge Barriers
                  </h3>
                  <div className="space-y-3">
                    {barriers.barriers.map((barrier, idx) => (
                      <div key={idx} className="border-l-4 border-yellow-400 pl-3 py-2">
                        <p className="font-medium text-sm">{barrier.description}</p>
                        <p className="text-xs text-gray-600 mt-1">
                          Action: {barrier.action_required}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          Est. resolution: {formatTimestamp(barrier.estimated_resolution)}
                        </p>
                      </div>
                    ))}
                  </div>
                  
                  {barriers.recommendations && barriers.recommendations.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-yellow-200">
                      <h4 className="font-medium text-sm mb-2">Recommendations:</h4>
                      <ul className="space-y-1">
                        {barriers.recommendations.map((rec, idx) => (
                          <li key={idx} className="text-xs text-gray-700 flex items-start gap-2">
                            <CheckCircle className="w-3 h-3 text-green-600 mt-0.5 flex-shrink-0" />
                            <span>{rec.action} ({rec.responsible_party})</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <div className="bg-green-50 p-4 rounded-lg">
                  <h3 className="font-semibold mb-2 flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    Ready for Discharge
                  </h3>
                  <p className="text-sm text-gray-700">
                    No barriers detected. Patient can be discharged.
                  </p>
                </div>
              )}

              {/* AI Insights */}
              {barriers && barriers.ai_insights && barriers.ai_insights.length > 0 && (
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h3 className="font-semibold mb-3 flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-blue-600" />
                    AI Insights
                  </h3>
                  <ul className="space-y-2">
                    {barriers.ai_insights.map((insight, idx) => (
                      <li key={idx} className="text-sm text-gray-700">
                        • {insight}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p className="text-lg">This bed is currently available</p>
              <p className="text-sm mt-2">Click on an occupied bed to view patient details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}