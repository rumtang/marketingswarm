from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np
import logging
import asyncio

logger = logging.getLogger(__name__)


class CapacityPredictor:
    """AI Agent for predicting bed capacity with narrative awareness"""
    
    def __init__(self, narrative_engine=None):
        self.model_name = "narrative-aware-predictor"
        self.narrative_engine = narrative_engine
        # Historical patterns (simulated)
        self.discharge_patterns = {
            'morning': 0.6,  # 60% of discharges happen 10am-12pm
            'afternoon': 0.3,  # 30% happen 2pm-5pm
            'evening': 0.1    # 10% happen after 5pm
        }
        self.admission_patterns = {
            'morning': 0.2,
            'afternoon': 0.5,  # Peak admissions 2pm-5pm
            'evening': 0.3
        }
        
    async def predict_capacity(self, current_beds: List[Dict[str, Any]], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Predict bed capacity based on narrative context"""
        try:
            # Get narrative context
            narrative_context = context or {}
            if self.narrative_engine:
                narrative_context.update({
                    'narrative_phase': self.narrative_engine.narrative_phase,
                    'hospital_context': self.narrative_engine.hospital_context
                })
            
            # Calculate current metrics
            total_beds = len(current_beds)
            occupied_beds = len([b for b in current_beds if b['status'] == 'occupied'])
            occupancy_rate = occupied_beds / total_beds if total_beds > 0 else 0
            
            # Analyze length of stay for predictions
            avg_los = await self._calculate_average_los(current_beds)
            
            # Generate hourly predictions
            predictions = []
            current_time = datetime.utcnow()
            
            for hour in range(24):
                forecast_time = current_time + timedelta(hours=hour)
                hour_of_day = forecast_time.hour
                
                # Estimate discharges
                expected_discharges = self._estimate_discharges(
                    occupied_beds, hour_of_day, avg_los
                )
                
                # Estimate admissions
                expected_admissions = self._estimate_admissions(
                    total_beds - occupied_beds, hour_of_day
                )
                
                # Calculate predicted occupancy
                predicted_occupied = max(0, min(total_beds, 
                    occupied_beds - expected_discharges + expected_admissions
                ))
                predicted_occupancy = predicted_occupied / total_beds
                
                predictions.append({
                    'hour': hour,
                    'time': forecast_time.isoformat(),
                    'predicted_occupancy': round(predicted_occupancy, 3),
                    'predicted_available': total_beds - int(predicted_occupied),
                    'expected_discharges': int(expected_discharges),
                    'expected_admissions': int(expected_admissions),
                    'confidence': 0.85 if hour < 6 else 0.75  # Higher confidence for near-term
                })
                
                # Update occupied beds for next iteration
                occupied_beds = predicted_occupied
                
            # Generate AI insights with narrative context
            insights = await self._generate_insights(predictions, current_beds, narrative_context)
            
            return {
                'current_occupancy': round(occupancy_rate, 3),
                'predictions': predictions,
                'insights': insights,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in capacity prediction: {e}")
            return {
                'error': str(e),
                'predictions': [],
                'insights': []
            }
            
    async def _calculate_average_los(self, beds: List[Dict[str, Any]]) -> float:
        """Calculate average length of stay"""
        los_values = []
        current_time = datetime.utcnow()
        
        for bed in beds:
            if bed['status'] == 'occupied' and bed['admission_time']:
                admission_time = datetime.fromisoformat(bed['admission_time'])
                los_hours = (current_time - admission_time).total_seconds() / 3600
                los_values.append(los_hours)
                
        return np.mean(los_values) if los_values else 72.0  # Default 3 days
        
    def _estimate_discharges(self, occupied: int, hour: int, avg_los: float) -> float:
        """Estimate discharges for a given hour"""
        # Base discharge rate from average LOS
        daily_discharge_rate = min(0.3, 24 / avg_los)  # Cap at 30% daily turnover
        hourly_base = occupied * daily_discharge_rate / 24
        
        # Apply time-of-day patterns
        if 10 <= hour <= 12:
            multiplier = 3.0  # Morning discharge peak
        elif 14 <= hour <= 17:
            multiplier = 1.5  # Afternoon discharges
        elif hour < 8 or hour > 20:
            multiplier = 0.1  # Minimal overnight discharges
        else:
            multiplier = 0.8
            
        return hourly_base * multiplier
        
    def _estimate_admissions(self, available: int, hour: int) -> float:
        """Estimate admissions for a given hour"""
        # Base admission rate (targeting 85% occupancy)
        if available > 30:  # Plenty of beds available
            base_rate = 2.0
        elif available > 15:
            base_rate = 1.5
        else:
            base_rate = 0.8  # Slow down when near capacity
            
        # Apply time-of-day patterns
        if 14 <= hour <= 17:
            multiplier = 2.0  # Afternoon admission surge
        elif 10 <= hour <= 14:
            multiplier = 1.2
        elif hour < 8 or hour > 22:
            multiplier = 0.3  # Minimal overnight admissions
        else:
            multiplier = 1.0
            
        return base_rate * multiplier
        
    async def _generate_insights(self, predictions: List[Dict], beds: List[Dict], context: Dict) -> List[Dict]:
        """Generate narrative-aware insights from predictions"""
        insights = []
        
        # Add narrative context to insights
        if context.get('narrative_phase'):
            phase_insights = {
                'morning_surge': "Morning surge expected - prepare for ED admissions",
                'afternoon_complexity': "Complex discharge barriers likely this afternoon",
                'evening_transitions': "Evening shift change may delay discharges",
                'night_shift': "Quieter overnight period expected"
            }
            if context['narrative_phase'] in phase_insights:
                insights.append({
                    'type': 'narrative',
                    'message': phase_insights[context['narrative_phase']],
                    'recommendation': "Adjust staffing based on narrative pattern",
                    'priority': 'medium'
                })
        
        # Find critical periods
        high_occupancy_hours = [p for p in predictions if p['predicted_occupancy'] > 0.9]
        if high_occupancy_hours:
            insights.append({
                'type': 'warning',
                'message': f"High occupancy (>90%) predicted in {len(high_occupancy_hours)} hours",
                'recommendation': "Consider expediting morning discharges and deferring elective admissions",
                'priority': 'high'
            })
            
        # Check for discharge opportunities
        long_stay_patients = [b for b in beds 
                             if b['status'] == 'occupied' 
                             and b['admission_time']
                             and (datetime.utcnow() - datetime.fromisoformat(b['admission_time'])).days > 5]
        if long_stay_patients:
            insights.append({
                'type': 'opportunity',
                'message': f"{len(long_stay_patients)} patients with LOS > 5 days",
                'recommendation': "Review for discharge barriers and care coordination needs",
                'priority': 'medium'
            })
            
        # Staffing recommendations
        peak_admission_hour = max(predictions[:12], key=lambda x: x['expected_admissions'])
        insights.append({
            'type': 'info',
            'message': f"Peak admissions expected at {peak_admission_hour['time'][:16]}",
            'recommendation': "Ensure adequate admission staff coverage",
            'priority': 'medium'
        })
        
        return insights