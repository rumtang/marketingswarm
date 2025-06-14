"""
Core Narrative Engine for generating coherent healthcare stories
"""

import os
import json
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from openai import OpenAI

from .models import (
    PatientStory, HospitalContext, NarrativeEvent, 
    EmotionalState, DischargeBarrierType, DemoScenario
)
from .prompts import (
    PATIENT_GENERATION_PROMPT, EVENT_GENERATION_PROMPT,
    INSIGHT_GENERATION_PROMPT, HOSPITAL_CONTEXT_PROMPT
)

logger = logging.getLogger(__name__)


class NarrativeEngine:
    """
    Maintains hospital state and generates coherent patient stories using LLM
    """
    
    def __init__(self, session_id: str, demo_mode: bool = True):
        self.session_id = session_id
        self.demo_mode = demo_mode
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Model selection tiers
        self.models = {
            "nano": "gpt-3.5-turbo",      # Simple operations
            "mini": "gpt-4o-mini",        # Standard operations
            "full": "gpt-4o"              # Complex scenarios
        }
        
        # Initialize hospital context
        self.hospital_context = self._generate_hospital_personality()
        
        # Session state
        self.patient_stories: Dict[str, PatientStory] = {}
        self.event_history: List[NarrativeEvent] = []
        self.story_threads: Dict[str, List[str]] = {}
        self.staff_characters: Dict[str, str] = self._initialize_staff()
        
        # Demo tracking
        self.wow_moments_count = 0
        self.session_start = datetime.utcnow()
        
    def _select_model(self, complexity: str = "mini") -> str:
        """Select appropriate model based on operation complexity"""
        return self.models.get(complexity, self.models["mini"])
    
    def _initialize_staff(self) -> Dict[str, str]:
        """Create recurring staff characters for continuity"""
        return {
            "charge_nurse": "Sarah Martinez, RN - 15 years experience, known for her calm demeanor",
            "hospitalist": "Dr. James Thompson - Thorough and patient-focused",
            "case_manager": "Lisa Roberts, LCSW - Expert at complex discharge planning",
            "pt_lead": "Mike O'Brien, DPT - Motivational and innovative",
            "night_nurse": "Ahmed Hassan, RN - Exceptional at patient comfort",
            "social_worker": "Rachel Green, MSW - Advocate for vulnerable patients",
            "pharmacist": "Dr. Emily Watson - Medication optimization specialist"
        }
        
    def _generate_hospital_personality(self) -> HospitalContext:
        """Generate unique hospital context for this session"""
        try:
            # Get current time-based context
            now = datetime.utcnow()
            hour = now.hour
            
            # Determine shift
            if 7 <= hour < 15:
                shift = "Day Shift"
                ed_status = "Moderate to busy"
            elif 15 <= hour < 23:
                shift = "Evening Shift"
                ed_status = "Peak volume"
            else:
                shift = "Night Shift"
                ed_status = "Steady flow"
            
            # Seasonal factors
            month = now.month
            if month in [12, 1, 2]:
                season = "Winter"
                community_factors = ["Flu season active", "Icy conditions increasing falls"]
            elif month in [6, 7, 8]:
                season = "Summer"
                community_factors = ["Heat-related admissions", "Vacation season affecting staffing"]
            else:
                season = "Spring" if month in [3, 4, 5] else "Fall"
                community_factors = ["Typical seasonal patterns"]
            
            context = HospitalContext(
                current_season=season,
                current_shift=shift,
                ed_status=ed_status,
                community_factors=community_factors,
                recent_events=[
                    "New telemetry unit opened last month",
                    "Recent Joint Commission accreditation with commendation"
                ]
            )
            
            # Use LLM to add personality
            if self.demo_mode:
                response = self.client.chat.completions.create(
                    model=self._select_model("full"),  # Complex operation
                    messages=[
                        {"role": "system", "content": HOSPITAL_CONTEXT_PROMPT},
                        {"role": "user", "content": f"Generate additional personality details for a hospital during {season} {shift}"}
                    ],
                    temperature=0.7,
                    max_tokens=200
                )
                
                # Parse and add details
                additional_context = json.loads(response.choices[0].message.content)
                context.culture_notes = additional_context.get("culture_notes", context.culture_notes)
                context.notable_programs.extend(additional_context.get("programs", []))
                
        except Exception as e:
            logger.warning(f"Could not enhance hospital context with LLM: {e}")
            
        return context
        
    async def generate_patient(self, bed_id: str, unit: str) -> PatientStory:
        """Generate unique patient with medical history and current situation"""
        try:
            # Build context from current state
            context = {
                "hospital_context": self.hospital_context.model_dump(),
                "unit_type": unit,
                "bed_id": bed_id,
                "current_patients": len(self.patient_stories),
                "recent_events": [e.narrative for e in self.event_history[-5:]],
                "session_duration": (datetime.utcnow() - self.session_start).seconds // 60
            }
            
            # Generate patient story
            response = self.client.chat.completions.create(
                model=self._select_model("mini"),  # Standard operation
                messages=[
                    {"role": "system", "content": PATIENT_GENERATION_PROMPT},
                    {"role": "user", "content": json.dumps(context)}
                ],
                temperature=0.8,
                max_tokens=1000
            )
            
            patient_data = json.loads(response.choices[0].message.content)
            
            # Ensure unique patient ID
            patient_id = f"P{self.session_id[:4]}{random.randint(1000, 9999)}"
            patient_data["patient_id"] = patient_id
            
            # Add staff assignments
            patient_data["attending_physician"] = self._assign_physician(unit)
            patient_data["primary_nurse"] = self._assign_nurse()
            
            # Create patient story
            patient = PatientStory(**patient_data)
            self.patient_stories[patient_id] = patient
            
            # Track narrative threads
            self._track_story_thread(patient_id, f"Admitted: {patient.admission_reason}")
            
            logger.info(f"Generated patient {patient.name} with rich backstory")
            return patient
            
        except Exception as e:
            logger.error(f"Error generating patient: {e}")
            # Fallback to simple generation
            return self._generate_fallback_patient(bed_id, unit)
            
    def _generate_fallback_patient(self, bed_id: str, unit: str) -> PatientStory:
        """Simple fallback patient generation"""
        names = ["John Smith", "Mary Johnson", "Robert Davis", "Patricia Brown"]
        conditions = ["Pneumonia", "CHF Exacerbation", "Post-op recovery", "Chest pain"]
        
        patient_id = f"P{random.randint(1000, 9999)}"
        return PatientStory(
            patient_id=patient_id,
            name=random.choice(names),
            age=random.randint(45, 85),
            gender=random.choice(["M", "F"]),
            backstory="Local resident with family support",
            family_situation="Married with children",
            emotional_state=EmotionalState.ANXIOUS,
            admission_reason=random.choice(conditions),
            medical_history=["Hypertension", "Type 2 Diabetes"],
            current_condition="Stable, improving",
            pain_level=random.randint(2, 6),
            mobility_status="Limited mobility",
            attending_physician=self._assign_physician(unit),
            primary_nurse=self._assign_nurse(),
            family_dynamics="Supportive family, involved in care"
        )
        
    async def generate_event(self, trigger: str, patient_id: Optional[str] = None) -> NarrativeEvent:
        """Generate contextually appropriate event"""
        try:
            # Build context
            if patient_id and patient_id in self.patient_stories:
                patient = self.patient_stories[patient_id]
                patient_context = patient.model_dump()
            else:
                # Pick a patient with interesting story potential
                patient_id, patient = self._select_patient_for_event()
                patient_context = patient.model_dump() if patient else {}
                
            context = {
                "trigger": trigger,
                "patient": patient_context,
                "hospital_state": self.hospital_context.model_dump(),
                "recent_events": [e.narrative for e in self.event_history[-3:]],
                "time_in_session": (datetime.utcnow() - self.session_start).seconds // 60,
                "story_threads": self.story_threads.get(patient_id, [])
            }
            
            # Generate event
            response = self.client.chat.completions.create(
                model=self._select_model("mini"),  # Standard operation
                messages=[
                    {"role": "system", "content": EVENT_GENERATION_PROMPT},
                    {"role": "user", "content": json.dumps(context)}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            event_data = json.loads(response.choices[0].message.content)
            
            # Create event
            event_id = f"EVT{self.session_id[:4]}{len(self.event_history):04d}"
            event = NarrativeEvent(
                event_id=event_id,
                timestamp=datetime.utcnow(),
                patient_id=patient_id,
                **event_data
            )
            
            # Update patient story based on event
            if patient_id in self.patient_stories:
                self._apply_event_to_patient(patient_id, event)
                
            self.event_history.append(event)
            self._track_story_thread(patient_id, event.narrative)
            
            # Check for wow moment
            if "breakthrough" in event.narrative.lower() or "unexpected" in event.narrative.lower():
                self.wow_moments_count += 1
                
            return event
            
        except Exception as e:
            logger.error(f"Error generating event: {e}")
            return self._generate_fallback_event(trigger, patient_id)
            
    def _generate_fallback_event(self, trigger: str, patient_id: str) -> NarrativeEvent:
        """Simple fallback event generation"""
        events = [
            {
                "event_type": "Clinical Update",
                "narrative": "Patient showing signs of improvement after medication adjustment",
                "medical_significance": "Positive response to treatment"
            },
            {
                "event_type": "Family Visit",
                "narrative": "Family member arrived to discuss discharge planning",
                "medical_significance": "Discharge planning progressing"
            }
        ]
        
        event_data = random.choice(events)
        return NarrativeEvent(
            event_id=f"EVT{random.randint(1000, 9999)}",
            timestamp=datetime.utcnow(),
            patient_id=patient_id,
            **event_data
        )
        
    async def generate_insight(self, agent_type: str, query_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate agent insights that reference the narrative"""
        try:
            # Gather relevant patient stories
            relevant_patients = self._get_relevant_patients(query_context)
            
            context = {
                "agent_type": agent_type,
                "query": query_context,
                "patients": [p.model_dump() for p in relevant_patients[:5]],
                "recent_events": [e.model_dump() for e in self.event_history[-10:]],
                "hospital_context": self.hospital_context.model_dump(),
                "wow_moments_delivered": self.wow_moments_count,
                "target_wow_moments": 3
            }
            
            # Generate insight
            response = self.client.chat.completions.create(
                model=self._select_model("nano"),  # Simple operation - insights
                messages=[
                    {"role": "system", "content": INSIGHT_GENERATION_PROMPT.format(agent_type=agent_type)},
                    {"role": "user", "content": json.dumps(context)}
                ],
                temperature=0.6,
                max_tokens=1000
            )
            
            insight_data = json.loads(response.choices[0].message.content)
            
            # Track if this is a wow moment
            if insight_data.get("wow_factor", False):
                self.wow_moments_count += 1
                logger.info(f"Wow moment #{self.wow_moments_count} delivered!")
                
            return insight_data
            
        except Exception as e:
            logger.error(f"Error generating insight: {e}")
            return self._generate_fallback_insight(agent_type)
            
    def _generate_fallback_insight(self, agent_type: str) -> Dict[str, Any]:
        """Fallback insights"""
        insights = {
            "capacity_predictor": {
                "prediction": "Based on current patterns, expect 3-5 discharges by 2 PM",
                "confidence": 0.75,
                "factors": ["Morning rounds complete", "PT evaluations scheduled"]
            },
            "discharge_accelerator": {
                "barriers_identified": 2,
                "recommendations": ["Early social work consult", "Coordinate with family"],
                "time_saved": "4-6 hours"
            },
            "concierge_chat": {
                "response": "I understand your concern. Let me connect you with your care team.",
                "sentiment": "empathetic",
                "follow_up_needed": True
            }
        }
        return insights.get(agent_type, {"status": "Processing"})
        
    def _select_patient_for_event(self) -> tuple[str, Optional[PatientStory]]:
        """Select patient most suitable for narrative development"""
        if not self.patient_stories:
            return "", None
            
        # Prioritize patients with unresolved barriers or emotional needs
        candidates = [
            (pid, p) for pid, p in self.patient_stories.items()
            if p.discharge_barriers or p.emotional_state in [EmotionalState.ANXIOUS, EmotionalState.FRUSTRATED]
        ]
        
        if candidates:
            return random.choice(candidates)
        return random.choice(list(self.patient_stories.items()))
        
    def _apply_event_to_patient(self, patient_id: str, event: NarrativeEvent):
        """Update patient story based on event"""
        if patient_id not in self.patient_stories:
            return
            
        patient = self.patient_stories[patient_id]
        
        # Apply status changes
        for key, value in event.changes_to_status.items():
            if hasattr(patient, key):
                setattr(patient, key, value)
                
        # Update barriers
        patient.discharge_barriers = [
            b for b in patient.discharge_barriers 
            if b.get("description") not in event.resolved_barriers
        ]
        
        for barrier in event.new_barriers:
            patient.discharge_barriers.append({
                "type": DischargeBarrierType.MEDICAL,
                "description": barrier,
                "severity": "moderate"
            })
            
        # Add to recent events
        patient.recent_events.append(event.narrative)
        if len(patient.recent_events) > 5:
            patient.recent_events.pop(0)
            
    def _track_story_thread(self, patient_id: str, narrative: str):
        """Track ongoing story threads"""
        if patient_id not in self.story_threads:
            self.story_threads[patient_id] = []
        self.story_threads[patient_id].append(narrative)
        
        # Keep last 10 events per patient
        if len(self.story_threads[patient_id]) > 10:
            self.story_threads[patient_id].pop(0)
            
    def _assign_physician(self, unit: str) -> str:
        """Assign physician based on unit"""
        physicians = {
            "ICU": "Dr. Sarah Chen, Critical Care",
            "CARDIAC": "Dr. Michael Ross, Cardiology",
            "NEURO": "Dr. Jennifer Park, Neurology",
            "ORTHO": "Dr. Robert Anderson, Orthopedics"
        }
        return physicians.get(unit, self.staff_characters["hospitalist"].split(" - ")[0])
        
    def _assign_nurse(self) -> str:
        """Assign nurse from staff pool"""
        nurses = [v.split(" - ")[0] for k, v in self.staff_characters.items() if "nurse" in k]
        return random.choice(nurses)
        
    def _get_relevant_patients(self, query_context: Dict[str, Any]) -> List[PatientStory]:
        """Get patients relevant to the current query"""
        # Sort by narrative interest
        patients = list(self.patient_stories.values())
        
        # Prioritize patients with active stories
        patients.sort(key=lambda p: (
            len(p.recent_events),
            len(p.discharge_barriers),
            p.emotional_state == EmotionalState.ANXIOUS
        ), reverse=True)
        
        return patients
        
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of session for handoff or review"""
        return {
            "session_id": self.session_id,
            "duration_minutes": (datetime.utcnow() - self.session_start).seconds // 60,
            "patients_created": len(self.patient_stories),
            "events_generated": len(self.event_history),
            "wow_moments": self.wow_moments_count,
            "story_threads_active": len([t for t in self.story_threads.values() if len(t) > 2]),
            "most_complex_patient": max(
                self.patient_stories.values(),
                key=lambda p: len(p.discharge_barriers) + len(p.recent_events),
                default=None
            ),
            "narrative_quality": "High" if self.wow_moments_count >= 3 else "Building"
        }