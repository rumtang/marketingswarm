from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
import logging
import asyncio

logger = logging.getLogger(__name__)


class DischargeAccelerator:
    """AI Agent for identifying and addressing discharge barriers with narrative awareness"""
    
    def __init__(self, narrative_engine=None):
        self.model_name = "narrative-aware-accelerator"
        self.narrative_engine = narrative_engine
        
        # Common discharge barriers
        self.barrier_types = [
            {
                'type': 'lab_pending',
                'description': 'Waiting for lab results',
                'avg_delay_hours': 4,
                'action': 'Contact lab for expedited processing'
            },
            {
                'type': 'consult_pending',
                'description': 'Specialist consultation needed',
                'avg_delay_hours': 8,
                'action': 'Page consulting service for urgent review'
            },
            {
                'type': 'transport_arranged',
                'description': 'Transportation not arranged',
                'avg_delay_hours': 3,
                'action': 'Contact social services for transport coordination'
            },
            {
                'type': 'medication_reconciliation',
                'description': 'Discharge medications not ready',
                'avg_delay_hours': 2,
                'action': 'Alert pharmacy for priority processing'
            },
            {
                'type': 'placement_needed',
                'description': 'Awaiting facility placement',
                'avg_delay_hours': 24,
                'action': 'Escalate to case management'
            },
            {
                'type': 'insurance_auth',
                'description': 'Insurance authorization pending',
                'avg_delay_hours': 6,
                'action': 'Contact utilization review'
            }
        ]
        
    async def identify_barriers(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify discharge barriers using narrative context"""
        barriers = []
        patient_id = context.get('patient_id')
        
        if not patient_id:
            return barriers
            
        # Get patient narrative data
        try:
            patient_data = context.get('narrative_context')
            if not patient_data and self.narrative_engine:
                patient_data = await self.narrative_engine.get_patient_data(patient_id)
            
            # Use narrative-defined barriers
            narrative_barriers = patient_data.get('discharge_barriers', [])
            
            for idx, barrier_desc in enumerate(narrative_barriers):
                # Match to barrier type or create custom
                barrier_type = self._match_barrier_type(barrier_desc)
                
                barriers.append({
                    'patient_id': patient_id,
                    'type': barrier_type['type'],
                    'description': barrier_desc,  # Use actual narrative description
                    'estimated_delay': barrier_type['avg_delay_hours'],
                    'recommended_action': barrier_type['action'],
                    'identified_at': datetime.now().isoformat(),
                    'status': 'active',
                    'narrative_context': f"For {patient_data.get('name', 'patient')}: {barrier_desc}"
                })
                
        except Exception as e:
            logger.error(f"Error identifying barriers from narrative: {e}")
                
        return barriers
    
    def _match_barrier_type(self, barrier_desc: str) -> Dict[str, Any]:
        """Match narrative barrier to type"""
        barrier_lower = barrier_desc.lower()
        
        # Try to match known types
        for barrier_type in self.barrier_types:
            if any(word in barrier_lower for word in barrier_type['type'].split('_')):
                return barrier_type
                
        # Default for unmatched
        return {
            'type': 'other',
            'description': barrier_desc,
            'avg_delay_hours': 6,
            'action': 'Review patient-specific barrier'
        }
        
    async def analyze_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive analysis of a specific patient's discharge readiness"""
        try:
            patient_id = patient_data['patient_id']
            admission_time = datetime.fromisoformat(patient_data['admission_time'])
            los_days = (datetime.utcnow() - admission_time).days
            
            analysis = {
                'patient_id': patient_id,
                'los_days': los_days,
                'discharge_readiness': 'unknown',
                'barriers': [],
                'recommendations': [],
                'estimated_discharge': None
            }
            
            # Check existing barriers
            existing_barriers = patient_data.get('barriers', [])
            
            # Simulate comprehensive barrier check
            if los_days > 3:  # Longer stay = more likely barriers
                barrier_probability = min(0.8, 0.3 + (los_days * 0.1))
                
                if random.random() < barrier_probability:
                    num_barriers = random.randint(1, min(4, los_days))
                    selected_barriers = random.sample(self.barrier_types, num_barriers)
                    
                    total_delay = 0
                    for barrier in selected_barriers:
                        barrier_detail = {
                            'type': barrier['type'],
                            'description': barrier['description'],
                            'severity': 'high' if barrier['avg_delay_hours'] > 6 else 'medium',
                            'estimated_resolution': (
                                datetime.utcnow() + timedelta(hours=barrier['avg_delay_hours'])
                            ).isoformat(),
                            'action_required': barrier['action'],
                            'status': 'active'
                        }
                        analysis['barriers'].append(barrier_detail)
                        total_delay += barrier['avg_delay_hours']
                        
                    # Generate recommendations
                    analysis['recommendations'] = self._generate_recommendations(
                        analysis['barriers'], los_days
                    )
                    
                    # Estimate discharge time
                    analysis['estimated_discharge'] = (
                        datetime.utcnow() + timedelta(hours=total_delay)
                    ).isoformat()
                    
                    # Determine readiness
                    if total_delay < 4:
                        analysis['discharge_readiness'] = 'ready_with_actions'
                    elif total_delay < 12:
                        analysis['discharge_readiness'] = 'delayed'
                    else:
                        analysis['discharge_readiness'] = 'significant_barriers'
                else:
                    analysis['discharge_readiness'] = 'ready'
                    analysis['estimated_discharge'] = (
                        datetime.utcnow() + timedelta(hours=2)
                    ).isoformat()
                    analysis['recommendations'] = [{
                        'action': 'Initiate discharge process',
                        'priority': 'high',
                        'responsible_party': 'Nursing'
                    }]
            else:
                # Short stay, likely still treating
                analysis['discharge_readiness'] = 'not_ready'
                analysis['estimated_discharge'] = (
                    admission_time + timedelta(days=3)
                ).isoformat()
                
            # Add AI-generated insights
            analysis['ai_insights'] = await self._generate_insights(
                patient_data, analysis['barriers'], los_days
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing patient: {e}")
            return {
                'patient_id': patient_data.get('patient_id'),
                'error': str(e),
                'barriers': []
            }
            
    def _generate_recommendations(self, barriers: List[Dict], los_days: int) -> List[Dict]:
        """Generate actionable recommendations based on barriers"""
        recommendations = []
        
        # Priority actions for long-stay patients
        if los_days > 5:
            recommendations.append({
                'action': 'Schedule multidisciplinary rounds',
                'priority': 'urgent',
                'responsible_party': 'Care Coordination',
                'rationale': f'Patient LOS ({los_days} days) exceeds expected'
            })
            
        # Barrier-specific recommendations
        barrier_types = [b['type'] for b in barriers]
        
        if 'lab_pending' in barrier_types:
            recommendations.append({
                'action': 'Call lab for STAT processing',
                'priority': 'high',
                'responsible_party': 'Nursing',
                'rationale': 'Expedite discharge decision'
            })
            
        if 'placement_needed' in barrier_types:
            recommendations.append({
                'action': 'Escalate to administration',
                'priority': 'urgent',
                'responsible_party': 'Case Management',
                'rationale': 'Complex discharge requiring executive support'
            })
            
        if len(barriers) > 2:
            recommendations.append({
                'action': 'Assign discharge coordinator',
                'priority': 'high',
                'responsible_party': 'Unit Manager',
                'rationale': 'Multiple barriers require dedicated coordination'
            })
            
        return recommendations
        
    async def _generate_insights(self, patient_data: Dict, barriers: List[Dict], los_days: int) -> List[str]:
        """Generate AI-powered insights about the patient's discharge"""
        insights = []
        
        # LOS insights
        if los_days > 7:
            insights.append(
                f"Extended LOS ({los_days} days) suggests complex care needs. "
                "Consider palliative care consultation if appropriate."
            )
        elif los_days < 1:
            insights.append(
                "Recent admission. Focus on early discharge planning to prevent extended stay."
            )
            
        # Barrier pattern insights
        if len(barriers) > 2:
            insights.append(
                "Multiple concurrent barriers detected. "
                "Recommend daily huddle to coordinate resolution efforts."
            )
            
        # Diagnosis-specific insights (mock)
        diagnosis = patient_data.get('diagnosis', '').lower()
        if 'heart' in diagnosis or 'cardiac' in diagnosis:
            insights.append(
                "Cardiac patient: Ensure cardiac rehab referral and "
                "medication teaching completed before discharge."
            )
        elif 'diabetes' in diagnosis:
            insights.append(
                "Diabetic patient: Verify glucose monitoring supplies and "
                "endocrine follow-up scheduled."
            )
            
        # Time-based insights
        current_hour = datetime.utcnow().hour
        if 8 <= current_hour <= 12 and not barriers:
            insights.append(
                "Optimal discharge window. Prioritize this patient for morning discharge."
            )
            
        return insights
        
    async def generate_nudges(self, unit: str) -> List[Dict[str, Any]]:
        """Generate proactive nudges for the care team"""
        nudges = []
        current_time = datetime.utcnow()
        
        # Morning discharge reminder
        if current_time.hour == 7:
            nudges.append({
                'type': 'reminder',
                'message': 'Review discharge-ready patients for morning discharge',
                'unit': unit,
                'priority': 'high',
                'action': 'Print discharge instructions for ready patients'
            })
            
        # Afternoon barrier check
        if current_time.hour == 14:
            nudges.append({
                'type': 'action',
                'message': 'Check status of pending consults and labs',
                'unit': unit,
                'priority': 'medium',
                'action': 'Contact services with outstanding items'
            })
            
        return nudges