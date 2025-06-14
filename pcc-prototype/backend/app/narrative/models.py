"""
Data models for the Narrative Engine
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class EmotionalState(str, Enum):
    """Patient emotional states"""
    ANXIOUS = "anxious"
    HOPEFUL = "hopeful"
    FRUSTRATED = "frustrated"
    CONTENT = "content"
    CONFUSED = "confused"
    DETERMINED = "determined"
    WITHDRAWN = "withdrawn"
    OPTIMISTIC = "optimistic"


class DischargeBarrierType(str, Enum):
    """Types of discharge barriers"""
    MEDICAL = "medical"
    SOCIAL = "social"
    LOGISTICAL = "logistical"
    INSURANCE = "insurance"
    EQUIPMENT = "equipment"
    PLACEMENT = "placement"
    THERAPY = "therapy"


class PatientStory(BaseModel):
    """Rich patient narrative with medical and personal context"""
    patient_id: str
    name: str
    age: int
    gender: str
    
    # Personal context
    backstory: str = Field(..., description="Personal history and living situation")
    occupation: Optional[str] = None
    family_situation: str
    emotional_state: EmotionalState
    personal_concerns: List[str] = []
    
    # Medical context
    admission_reason: str
    medical_history: List[str] = []
    current_medications: List[str] = []
    allergies: List[str] = []
    
    # Current status
    current_condition: str
    pain_level: int = Field(ge=0, le=10)
    consciousness_level: str = "Alert and oriented"
    mobility_status: str
    
    # Discharge planning
    discharge_barriers: List[Dict[str, Any]] = []
    expected_discharge: Optional[datetime] = None
    discharge_disposition: str = "Home"
    
    # Care team
    attending_physician: str
    primary_nurse: str
    specialists: List[str] = []
    
    # Narrative elements
    recent_events: List[str] = []
    family_dynamics: str
    key_moments: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "P2024001",
                "name": "Margaret Chen",
                "age": 67,
                "gender": "F",
                "backstory": "Retired elementary school teacher, lives alone in a two-story house. Daughter Emily lives 2 hours away and visits weekly.",
                "occupation": "Retired Teacher",
                "family_situation": "Widowed, one daughter (Emily), two grandchildren",
                "emotional_state": "anxious",
                "personal_concerns": [
                    "Worried about missing granddaughter's recital",
                    "Concerned about who will feed her cat"
                ],
                "admission_reason": "Fall at home while reaching for a book, possible hip fracture",
                "medical_history": ["Type 2 Diabetes", "Mild cognitive impairment", "Osteoporosis"],
                "current_condition": "Stable, awaiting orthopedic evaluation"
            }
        }


class HospitalContext(BaseModel):
    """Hospital personality and current state"""
    hospital_name: str = "St. Mary's Medical Center"
    location: str = "Downtown District"
    specialties: List[str] = ["Cardiac Care", "Orthopedics", "Neurology"]
    current_season: str
    current_shift: str
    
    # Hospital characteristics
    teaching_hospital: bool = True
    trauma_level: int = 2
    bed_capacity: int = 200
    typical_census: float = 0.85
    
    # Current state
    ed_status: str = "Moderate volume"
    or_schedule: str = "Full morning schedule"
    staffing_level: str = "Adequate"
    
    # Recent events affecting hospital
    recent_events: List[str] = []
    community_factors: List[str] = []
    
    # Personality elements
    culture_notes: str = "Patient-centered care with strong community ties"
    notable_programs: List[str] = ["Stroke Center of Excellence", "Joint Replacement Program"]


class DemoScenario(BaseModel):
    """Pre-configured demo scenarios"""
    name: str
    duration_minutes: int = 60
    description: str
    
    # Starting conditions
    initial_occupancy: float = 0.75
    ed_pressure: str = "moderate"
    
    # Scripted events (timing in minutes from start)
    scripted_events: List[Dict[str, Any]] = []
    
    # Key demonstration points
    showcase_features: List[str] = []
    expected_insights: List[str] = []
    
    # Narrative arc
    opening_context: str
    climax_event: Optional[str] = None
    resolution: str


class NarrativeEvent(BaseModel):
    """Contextual event in the patient journey"""
    event_id: str
    timestamp: datetime
    event_type: str
    patient_id: str
    
    # Narrative elements
    narrative: str = Field(..., description="Human-readable story of what happened")
    medical_significance: str
    emotional_impact: Optional[str] = None
    
    # Consequences
    changes_to_status: Dict[str, Any] = {}
    new_barriers: List[str] = []
    resolved_barriers: List[str] = []
    
    # Related staff actions
    staff_involved: List[str] = []
    decisions_made: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "EVT2024001",
                "event_type": "Family Update",
                "patient_id": "P2024001",
                "narrative": "Mrs. Chen's daughter Emily arrived earlier than expected after canceling her morning meetings. She brought Mrs. Chen's favorite blanket from home and spent an hour discussing home modifications with the occupational therapist.",
                "medical_significance": "Family engagement accelerating discharge planning",
                "emotional_impact": "Patient visibly relieved and more cooperative with PT",
                "changes_to_status": {
                    "emotional_state": "hopeful",
                    "discharge_readiness": "improving"
                },
                "resolved_barriers": ["Family availability for discharge teaching"],
                "staff_involved": ["OT Jennifer", "Case Manager Roberts"],
                "decisions_made": ["Schedule home safety eval for tomorrow AM"]
            }
        }


class SessionState(BaseModel):
    """Current state of a demo session"""
    session_id: str
    started_at: datetime
    demo_scenario: Optional[DemoScenario] = None
    
    # Current state
    hospital_context: HospitalContext
    active_patients: Dict[str, PatientStory] = {}
    event_history: List[NarrativeEvent] = []
    
    # Narrative tracking
    story_threads: Dict[str, List[str]] = {}  # Track ongoing narratives
    introduced_characters: Dict[str, str] = {}  # Staff members mentioned
    
    # Metrics for demo
    wow_moments_delivered: int = 0
    errors_gracefully_handled: int = 0