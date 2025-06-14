from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import re
import asyncio

logger = logging.getLogger(__name__)


class ConciergeChat:
    """AI Agent for patient and family chat interactions with narrative awareness"""
    
    def __init__(self, narrative_engine=None):
        self.model_name = "narrative-aware-concierge"
        self.narrative_engine = narrative_engine
        
        # Predefined responses for common queries
        self.response_templates = {
            'visiting_hours': {
                'response': "Visiting hours are 8 AM to 8 PM daily. Immediate family members may visit outside these hours with nurse approval.",
                'category': 'policy'
            },
            'parking': {
                'response': "Visitor parking is available in the main garage. Rates are $5/hour or $20/day. Validation available at the information desk.",
                'category': 'logistics'
            },
            'cafeteria': {
                'response': "The cafeteria is open 6:30 AM to 7 PM on Level 2. Vending machines are available 24/7 on each floor.",
                'category': 'amenities'
            },
            'discharge_time': {
                'response': "Discharge times vary by patient. Your care team will discuss the expected discharge time during morning rounds.",
                'category': 'clinical'
            },
            'test_results': {
                'response': "Test results will be reviewed by your doctor. Please use the nurse call button to request an update from your care team.",
                'category': 'clinical'
            },
            'medication': {
                'response': "For medication questions, please speak with your nurse or pharmacist. Use the call button for immediate assistance.",
                'category': 'clinical'
            },
            'wifi': {
                'response': "Free WiFi is available. Network: 'Guest-WiFi', Password: 'healing2024'. If you have trouble connecting, ask at the nurses' station.",
                'category': 'amenities'
            }
        }
        
        # Intent patterns
        self.intent_patterns = {
            'visiting': ['visit', 'visiting hours', 'see patient', 'come see'],
            'parking': ['park', 'parking', 'garage', 'lot'],
            'food': ['cafeteria', 'food', 'eat', 'meal', 'hungry', 'restaurant'],
            'discharge': ['discharge', 'going home', 'leave', 'release'],
            'results': ['results', 'test', 'lab', 'xray', 'scan'],
            'medication': ['medication', 'medicine', 'drug', 'prescription', 'pill'],
            'wifi': ['wifi', 'internet', 'wireless', 'connect']
        }
        
    async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Process query with narrative awareness"""
        message = query.get('text', '')
        context = query.get('context', {})
        
        try:
            # Clean and lowercase the message
            clean_message = message.lower().strip()
            
            # Detect intent
            intent = self._detect_intent(clean_message)
            
            # Check if it's an emergency
            if self._is_emergency(clean_message):
                return {
                    'response': "I've detected this may be an emergency. Please press the nurse call button immediately or dial the emergency number.",
                    'type': 'emergency',
                    'suggested_actions': ['Call nurse', 'Emergency assistance'],
                    'timestamp': datetime.now().isoformat()
                }
            
            # Get narrative context if available
            narrative_response = ""
            if self.narrative_engine and context.get('session_summary'):
                # Add narrative-aware context
                session = context['session_summary']
                if intent == 'discharge_time':
                    # Check for patients ready for discharge
                    ready_count = sum(1 for p in self.narrative_engine.patient_stories.values() 
                                    if p.get('narrative_arc') == 'improving')
                    if ready_count > 0:
                        narrative_response = f" Currently, {ready_count} patients are showing improvement and may be discharge candidates. "
                
            # Generate appropriate response
            if intent:
                template = self.response_templates.get(intent, {})
                base_response = template.get('response', '')
                
                # Add narrative context
                response = base_response + narrative_response
                
                # Add contextual information from narrative
                if intent == 'discharge_time' and context.get('hospital_state'):
                    challenges = context['hospital_state'].get('current_challenges', [])
                    if any('discharge' in c.lower() for c in challenges):
                        response += " Note: We're currently experiencing some discharge delays hospital-wide."
                    
                return {
                    'response': response,
                    'type': 'informational',
                    'category': template.get('category', 'general'),
                    'confidence': 0.9,
                    'suggested_actions': self._get_suggested_actions(intent),
                    'timestamp': datetime.now().isoformat(),
                    'narrative_aware': True
                }
            else:
                # Use narrative context for AI response
                ai_response = await self._generate_narrative_response(message, context)
                return ai_response
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                'response': "I apologize, but I'm having trouble understanding. Please try rephrasing or press the nurse call button for assistance.",
                'type': 'error',
                'timestamp': datetime.utcnow().isoformat()
            }
            
    def _detect_intent(self, message: str) -> Optional[str]:
        """Detect user intent from message"""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in message:
                    # Map intent to response template key
                    intent_map = {
                        'visiting': 'visiting_hours',
                        'parking': 'parking',
                        'food': 'cafeteria',
                        'discharge': 'discharge_time',
                        'results': 'test_results',
                        'medication': 'medication',
                        'wifi': 'wifi'
                    }
                    return intent_map.get(intent)
        return None
        
    def _is_emergency(self, message: str) -> bool:
        """Check if message indicates emergency"""
        emergency_keywords = [
            'emergency', 'help', 'pain', 'can\'t breathe', 'chest pain',
            'bleeding', 'fell', 'urgent', 'immediately', 'dying'
        ]
        return any(keyword in message for keyword in emergency_keywords)
        
    def _get_suggested_actions(self, intent: str) -> List[str]:
        """Get suggested follow-up actions based on intent"""
        actions_map = {
            'visiting_hours': ['Get directions', 'Visitor policy'],
            'parking': ['Get directions', 'Parking validation'],
            'cafeteria': ['View menu', 'Get directions'],
            'discharge_time': ['Speak to nurse', 'Discharge checklist'],
            'test_results': ['Call nurse', 'Ask doctor'],
            'medication': ['Call nurse', 'Speak to pharmacist'],
            'wifi': ['Tech support', 'Guest services']
        }
        return actions_map.get(intent, ['Speak to staff'])
        
    async def _generate_narrative_response(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI response for complex queries (mock implementation)"""
        # In production, this would call OpenAI API
        # For demo, we'll provide intelligent fallback responses
        
        # Check for common question patterns
        if 'how long' in message or 'when' in message:
            response = (
                "Timing questions are best answered by your care team who has access to your "
                "specific medical information. Please use the nurse call button to get accurate information."
            )
        elif 'why' in message:
            response = (
                "Medical decisions are made by your care team based on your specific condition. "
                "I'd be happy to have a nurse or doctor explain this to you."
            )
        elif 'can i' in message or 'am i allowed' in message:
            response = (
                "For questions about what you're allowed to do, please check with your nurse. "
                "They can provide guidance based on your doctor's orders."
            )
        else:
            response = (
                "I understand you have questions. While I can help with general hospital information, "
                "your care team is the best source for medical and specific care questions. "
                "Would you like me to help you contact them?"
            )
            
        return {
            'response': response,
            'type': 'ai_generated',
            'category': 'general',
            'confidence': 0.7,
            'suggested_actions': ['Call nurse', 'Ask your care team'],
            'timestamp': datetime.utcnow().isoformat()
        }
        
    async def get_conversation_summary(self, patient_id: str) -> Dict[str, Any]:
        """Generate summary of patient conversations for care team"""
        # In production, would retrieve from database
        # Mock implementation for demo
        
        return {
            'patient_id': patient_id,
            'total_messages': 15,
            'common_concerns': [
                'Discharge timing',
                'Pain management',
                'Visitor information'
            ],
            'sentiment': 'neutral',
            'urgent_items': [],
            'last_interaction': datetime.utcnow().isoformat(),
            'summary': "Patient has been asking primarily about discharge timing and visitor policies. No urgent concerns identified."
        }