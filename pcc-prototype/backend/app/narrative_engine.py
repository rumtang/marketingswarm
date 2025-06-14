"""
LLM-Powered Narrative Engine - The Core Data Source for PCC
This replaces ALL synthetic data generation. Every patient, event, and insight
comes from coherent AI-generated narratives.
"""

import asyncio
import json
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import uuid4

from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

from database.client import DatabaseClient
from messaging.producer import HL7Producer as KafkaProducer
from cache import patient_cache

load_dotenv()
logger = logging.getLogger(__name__)

class NarrativeEngine:
    """
    Core data engine - replaces synthetic data generation entirely.
    Maintains session-based patient stories and generates all events.
    """
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid4())
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.db = DatabaseClient()
        self.kafka_producer = KafkaProducer()
        self._db_initialized = False
        
        # Session state
        self.hospital_context = {}
        self.patient_stories = {}
        self.event_history = []
        self.event_queue = asyncio.Queue()
        self.running = False
        
        # Time-based narrative context
        self.session_start = datetime.now()
        self.narrative_phase = self._determine_narrative_phase()
        
        # Model selection tiers
        self.models = {
            "nano": "gpt-3.5-turbo",      # Simple operations (status checks, basic updates)
            "mini": "gpt-4o-mini",        # Standard operations (patient generation, insights)  
            "full": "gpt-4o"              # Complex scenarios (initial context, complex narratives)
        }
        
    def _select_model(self, complexity: str = "mini") -> str:
        """Select appropriate model based on operation complexity"""
        return self.models.get(complexity, self.models["mini"])
    
    def _determine_narrative_phase(self) -> str:
        """Determine narrative context based on time of day"""
        hour = datetime.now().hour
        if 6 <= hour < 10:
            return "morning_surge"
        elif 10 <= hour < 14:
            return "midday_peak"
        elif 14 <= hour < 18:
            return "afternoon_complexity"
        elif 18 <= hour < 22:
            return "evening_transitions"
        else:
            return "night_shift"
    
    async def start(self):
        """Replace the synthetic HL7 generator - this is our main data source"""
        if self.running:
            return
            
        # Initialize database if needed
        if not self._db_initialized:
            await self.db.init_database()
            self._db_initialized = True
            
        self.running = True
        logger.info(f"Starting Narrative Engine for session {self.session_id}")
        
        # Initialize hospital context
        await self._initialize_hospital_context()
        
        # Populate initial patients
        await self._populate_initial_patients()
        
        # Start continuous narrative event generation
        asyncio.create_task(self._narrative_event_loop())
        
    async def stop(self):
        """Gracefully stop the narrative engine"""
        self.running = False
        
    async def _initialize_hospital_context(self):
        """Generate the hospital's personality and current state"""
        prompt = f"""
        Generate a hospital context for a Patient Command Center session.
        Current time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        Narrative phase: {self.narrative_phase}
        
        Create a JSON object with:
        - hospital_type: (academic medical center, community hospital, etc.)
        - current_challenges: List of 2-3 ongoing operational challenges
        - staffing_mood: Overall staff sentiment
        - recent_events: 1-2 recent events affecting operations
        - census_pressure: low/moderate/high
        - special_circumstances: Any unique factors for this session
        
        Make it realistic and medically accurate.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self._select_model("full"),  # Complex operation - hospital context
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            self.hospital_context = json.loads(response.choices[0].message.content)
            logger.info(f"Hospital context initialized: {self.hospital_context}")
            
        except Exception as e:
            logger.error(f"Failed to generate hospital context: {e}")
            # Use fallback context based on narrative phase
            self.hospital_context = self._get_fallback_hospital_context()
            
    def _get_fallback_hospital_context(self) -> Dict[str, Any]:
        """Get fallback hospital context when LLM fails"""
        contexts = {
            "morning_surge": {
                "hospital_type": "academic medical center",
                "current_challenges": ["ED overcrowding from overnight holds", "Multiple scheduled surgeries competing for beds", "Nursing shift change delays"],
                "staffing_mood": "focused but feeling the morning rush",
                "recent_events": ["Two trauma cases arrived simultaneously", "PACU backing up with post-op patients"],
                "census_pressure": "high",
                "special_circumstances": "Joint Commission site visit this week"
            },
            "midday_peak": {
                "hospital_type": "community hospital",
                "current_challenges": ["Peak admission volume", "Discharge transportation delays", "Lab turnaround times increasing"],
                "staffing_mood": "steady but stretched thin",
                "recent_events": ["Cafeteria equipment failure affecting staff morale", "New EMR update causing slowdowns"],
                "census_pressure": "very high",
                "special_circumstances": "Local skilled nursing facilities at capacity"
            },
            "afternoon_complexity": {
                "hospital_type": "regional medical center",
                "current_challenges": ["Complex discharge planning", "Insurance authorization delays", "Specialist consultation backlog"],
                "staffing_mood": "determined but fatigued",
                "recent_events": ["Unexpected ICU transfers", "Pharmacy system briefly offline"],
                "census_pressure": "high",
                "special_circumstances": "Case management short-staffed this week"
            },
            "evening_transitions": {
                "hospital_type": "academic medical center",
                "current_challenges": ["Shift change communication gaps", "After-hours discharge barriers", "ED boarding increasing"],
                "staffing_mood": "transitioning, some confusion",
                "recent_events": ["Day shift running late on handoffs", "Multiple family conferences needed"],
                "census_pressure": "moderate",
                "special_circumstances": "Resident rotation just started"
            },
            "night_shift": {
                "hospital_type": "community hospital",
                "current_challenges": ["Reduced ancillary services", "Limited discharge options", "Covering multiple units"],
                "staffing_mood": "quiet determination",
                "recent_events": ["Unexpected code blue handled well", "IT performing scheduled maintenance"],
                "census_pressure": "stable",
                "special_circumstances": "Skeleton crew for non-clinical services"
            }
        }
        
        return contexts.get(self.narrative_phase, contexts["midday_peak"])
    
    async def _populate_initial_patients(self):
        """Generate initial patient population"""
        # Get all beds from database
        beds = await self.db.get_bed_status()
        
        # Determine initial occupancy based on narrative phase
        occupancy_rates = {
            "morning_surge": 0.85,
            "midday_peak": 0.90,
            "afternoon_complexity": 0.88,
            "evening_transitions": 0.82,
            "night_shift": 0.75
        }
        
        target_occupancy = occupancy_rates.get(self.narrative_phase, 0.80)
        num_occupied = int(len(beds) * target_occupancy)
        
        # Randomly select beds to occupy
        occupied_beds = random.sample(beds, num_occupied)
        
        # Generate patients for occupied beds
        for bed in occupied_beds:
            patient = await self._generate_patient(bed['bed_id'], bed['unit'])
            
            # Create admission event
            event = {
                "event_type": "ADT",
                "sub_type": "ADMISSION",
                "patient_id": patient['patient_id'],
                "patient_name": patient['name'],
                "bed_id": bed['bed_id'],
                "unit": bed['unit'],
                "admission_time": patient['admission_time'],
                "diagnosis": patient['diagnosis'],
                "narrative_context": {
                    "backstory": patient['backstory'],
                    "emotional_state": patient['emotional_state']
                }
            }
            
            # Send to Kafka
            await self.kafka_producer.send_event(event)
            
            # Add to our stories
            self.patient_stories[patient['patient_id']] = patient
            
        logger.info(f"Populated {num_occupied} initial patients")
    
    async def _generate_patient(self, bed_id: str, unit: str) -> Dict[str, Any]:
        """Generate a unique patient with rich narrative"""
        prompt = f"""
        Generate a realistic patient for a {unit} unit bed.
        Hospital context: {json.dumps(self.hospital_context)}
        Narrative phase: {self.narrative_phase}
        
        Create a JSON object with:
        - patient_id: Generate format P{random.randint(10000,99999)}
        - name: Full name
        - age: Appropriate for unit type
        - gender: M/F/Other
        - backstory: 2-3 sentences about their life (job, family, living situation)
        - admission_reason: Medical reason for admission
        - diagnosis: Current working diagnosis
        - medical_history: List of relevant conditions
        - admission_time: ISO timestamp (within last 72 hours)
        - expected_los_hours: Realistic length of stay estimate
        - discharge_barriers: List of 2-4 realistic barriers
        - emotional_state: Current emotional state
        - family_involvement: Description of family support
        - key_concerns: What the patient is worried about
        - narrative_arc: "stable", "improving", "complex", or "critical"
        
        Make the patient memorable and medically accurate for the unit type.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self._select_model("mini"),  # Standard operation - patient generation
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.8
            )
            
            patient = json.loads(response.choices[0].message.content)
            
            # Ensure patient_id is unique
            if not patient.get('patient_id'):
                patient['patient_id'] = f"P{random.randint(10000, 99999)}"
                
            # Add bed assignment
            patient['bed_id'] = bed_id
            patient['unit'] = unit
            
            return patient
            
        except Exception as e:
            logger.error(f"Failed to generate patient: {e}")
            # Use fallback template
            return self._get_fallback_patient(bed_id, unit)
            
    def _get_fallback_patient(self, bed_id: str, unit: str) -> Dict[str, Any]:
        """Get patient from fallback templates when LLM fails"""
        templates = {
            "ICU": [
                {
                    "name": "Robert Martinez",
                    "age": 58,
                    "gender": "M",
                    "backstory": "Construction foreman, married with 3 adult children. Wife stays at bedside constantly.",
                    "admission_reason": "Severe pneumonia with respiratory failure",
                    "diagnosis": "COVID-19 pneumonia, ARDS",
                    "medical_history": ["Type 2 Diabetes", "Hypertension"],
                    "discharge_barriers": ["Requires ventilator weaning", "Needs pulmonary rehab placement", "Insurance authorization pending"],
                    "emotional_state": "Sedated but improving",
                    "family_involvement": "Wife present 24/7, children visit daily",
                    "key_concerns": "Long-term lung function",
                    "narrative_arc": "improving"
                },
                {
                    "name": "Sarah Chen",
                    "age": 45,
                    "gender": "F",
                    "backstory": "Software engineer, single mother of teenage twins. Sister flying in from Seattle.",
                    "admission_reason": "Post-operative complications from emergency surgery",
                    "diagnosis": "Perforated bowel, sepsis",
                    "medical_history": ["Crohn's disease", "Previous bowel resection"],
                    "discharge_barriers": ["Infection control", "Home health setup needed", "Twins need support at home"],
                    "emotional_state": "Anxious about children",
                    "family_involvement": "Sister arriving tomorrow, neighbor checking on kids",
                    "key_concerns": "Getting home to children",
                    "narrative_arc": "complex"
                }
            ],
            "Medical": [
                {
                    "name": "Dorothy Williams",
                    "age": 78,
                    "gender": "F",
                    "backstory": "Retired teacher, lives alone in senior apartment. Daughter lives 2 hours away.",
                    "admission_reason": "Congestive heart failure exacerbation",
                    "diagnosis": "CHF, fluid overload",
                    "medical_history": ["CHF", "Atrial fibrillation", "Osteoarthritis"],
                    "discharge_barriers": ["Medication education needed", "Follow-up appointments to schedule", "Daughter arranging time off work"],
                    "emotional_state": "Worried about independence",
                    "family_involvement": "Daughter calling frequently, planning to stay for a week",
                    "key_concerns": "Maintaining independence at home",
                    "narrative_arc": "stable"
                },
                {
                    "name": "James Thompson",
                    "age": 62,
                    "gender": "M",
                    "backstory": "Recently laid off factory worker, living with brother. No insurance.",
                    "admission_reason": "Uncontrolled diabetes, diabetic ketoacidosis",
                    "diagnosis": "DKA, newly diagnosed Type 1 diabetes",
                    "medical_history": ["Depression", "Back injury"],
                    "discharge_barriers": ["Insulin cost concerns", "Needs diabetes education", "Social work consult for resources"],
                    "emotional_state": "Overwhelmed by diagnosis",
                    "family_involvement": "Brother supportive but works long hours",
                    "key_concerns": "Affording medications",
                    "narrative_arc": "complex"
                }
            ],
            "Surgical": [
                {
                    "name": "Michael O'Brien",
                    "age": 55,
                    "gender": "M",
                    "backstory": "Plumber, self-employed. Wife manages the business. Three teenage kids.",
                    "admission_reason": "Knee replacement surgery",
                    "diagnosis": "Post-op day 2, total knee arthroplasty",
                    "medical_history": ["Osteoarthritis", "Former smoker"],
                    "discharge_barriers": ["Physical therapy clearance needed", "Home safety evaluation", "Stairs at home"],
                    "emotional_state": "Motivated but frustrated with pain",
                    "family_involvement": "Wife present during days, kids visit after school",
                    "key_concerns": "Getting back to work",
                    "narrative_arc": "improving"
                }
            ],
            "Emergency": [
                {
                    "name": "Lisa Johnson",
                    "age": 32,
                    "gender": "F",
                    "backstory": "Elementary school teacher, pregnant with first child. Husband deployed overseas.",
                    "admission_reason": "Severe preeclampsia at 34 weeks",
                    "diagnosis": "Preeclampsia, being monitored for delivery timing",
                    "medical_history": ["First pregnancy", "Anxiety disorder"],
                    "discharge_barriers": ["Blood pressure stabilization", "Fetal monitoring", "Husband trying to get emergency leave"],
                    "emotional_state": "Scared but trying to stay positive",
                    "family_involvement": "Mother-in-law flying in, husband on video calls",
                    "key_concerns": "Baby's health and husband's absence",
                    "narrative_arc": "critical"
                }
            ]
        }
        
        # Get templates for unit or use Medical as default
        unit_templates = templates.get(unit, templates["Medical"])
        
        # Select random template and customize
        template = random.choice(unit_templates).copy()
        
        # Add required fields
        patient = {
            "patient_id": f"P{random.randint(10000, 99999)}",
            "admission_time": (datetime.now() - timedelta(hours=random.randint(6, 72))).isoformat(),
            "expected_los_hours": random.randint(24, 96),
            "bed_id": bed_id,
            "unit": unit
        }
        
        # Merge with template
        patient.update(template)
        
        return patient
    
    async def _narrative_event_loop(self):
        """Generate contextually appropriate events continuously"""
        while self.running:
            try:
                # Update narrative phase
                self.narrative_phase = self._determine_narrative_phase()
                
                # Generate next event based on narrative context
                event = await self._generate_next_narrative_event()
                
                if event:
                    # Send to Kafka
                    await self.kafka_producer.send_event(event)
                    
                    # Track history
                    self.event_history.append(event)
                    
                    # Update patient stories if needed
                    if event.get('patient_id') in self.patient_stories:
                        await self._update_patient_story(event)
                
                # Natural pacing based on narrative phase
                wait_times = {
                    "morning_surge": (5, 15),
                    "midday_peak": (10, 20),
                    "afternoon_complexity": (8, 18),
                    "evening_transitions": (12, 25),
                    "night_shift": (20, 40)
                }
                
                min_wait, max_wait = wait_times.get(self.narrative_phase, (10, 30))
                await asyncio.sleep(random.uniform(min_wait, max_wait))
                
            except Exception as e:
                logger.error(f"Error in narrative event loop: {e}")
                await asyncio.sleep(30)
    
    async def _generate_next_narrative_event(self) -> Optional[Dict[str, Any]]:
        """Generate the next event based on current narrative state"""
        # Get current state
        current_patients = list(self.patient_stories.values())
        recent_events = self.event_history[-10:] if self.event_history else []
        
        prompt = f"""
        Generate the next hospital event based on current context.
        
        Hospital context: {json.dumps(self.hospital_context)}
        Narrative phase: {self.narrative_phase}
        Current patient count: {len(current_patients)}
        Recent events: {len(recent_events)} in last hour
        
        Consider:
        1. Natural flow of hospital operations
        2. Time of day patterns
        3. Existing patient narrative arcs
        4. Hospital challenges
        
        Event types to choose from:
        - New admission (if beds available)
        - Discharge (if patient ready)
        - Clinical update (condition change)
        - Barrier identified
        - Barrier resolved
        - Transfer between units
        - Family update
        
        Generate a JSON object with:
        - event_type: Type of event
        - sub_type: Specific sub-type
        - patient_id: Existing patient ID or new if admission
        - description: What happened
        - clinical_impact: Medical significance
        - operational_impact: Effect on hospital flow
        - narrative_significance: Why this matters to the story
        - triggers_insight: true if AI agents should generate insights
        
        Make it medically realistic and narratively compelling.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self._select_model("mini"),  # Standard operation - event generation
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            event = json.loads(response.choices[0].message.content)
            event['timestamp'] = datetime.now().isoformat()
            event['session_id'] = self.session_id
            
            return event
            
        except Exception as e:
            logger.error(f"Failed to generate narrative event: {e}")
            # Use fallback event generation
            return self._generate_fallback_event(current_patients)
            
    def _generate_fallback_event(self, current_patients: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate fallback event when LLM fails"""
        event_templates = {
            "morning_surge": [
                {
                    "event_type": "ADT",
                    "sub_type": "CLINICAL_UPDATE",
                    "description": "Patient's morning labs show improvement in key markers",
                    "clinical_impact": "Possible discharge candidate if trend continues",
                    "operational_impact": "Bed may become available this afternoon",
                    "narrative_significance": "Recovery milestone reached after difficult night",
                    "triggers_insight": True
                },
                {
                    "event_type": "BARRIER",
                    "sub_type": "BARRIER_IDENTIFIED",
                    "description": "Home health agency unable to start services until Monday",
                    "clinical_impact": "Patient medically ready but needs home support",
                    "operational_impact": "Bed blocked through weekend",
                    "narrative_significance": "System limitations affecting patient flow",
                    "triggers_insight": True
                }
            ],
            "afternoon_complexity": [
                {
                    "event_type": "ADT",
                    "sub_type": "BARRIER_RESOLVED",
                    "description": "Family arranged private duty nursing, discharge can proceed",
                    "clinical_impact": "Safe discharge plan established",
                    "operational_impact": "Bed will be available within 2 hours",
                    "narrative_significance": "Family advocacy overcame system barrier",
                    "triggers_insight": True
                },
                {
                    "event_type": "CLINICAL",
                    "sub_type": "CONDITION_CHANGE",
                    "description": "Post-operative patient developing signs of infection",
                    "clinical_impact": "Requires IV antibiotics, delaying discharge",
                    "operational_impact": "Expected LOS increased by 48-72 hours",
                    "narrative_significance": "Setback in recovery journey",
                    "triggers_insight": True
                }
            ]
        }
        
        # Select appropriate templates
        templates = event_templates.get(self.narrative_phase, event_templates["afternoon_complexity"])
        event_template = random.choice(templates).copy()
        
        # If we have patients, pick one at random
        if current_patients:
            patient = random.choice(current_patients)
            event_template["patient_id"] = patient["patient_id"]
        else:
            event_template["patient_id"] = f"P{random.randint(10000, 99999)}"
            
        # Add timestamp and session
        event_template["timestamp"] = datetime.now().isoformat()
        event_template["session_id"] = self.session_id
        
        return event_template
    
    async def _update_patient_story(self, event: Dict[str, Any]):
        """Update patient narrative based on event"""
        patient_id = event.get('patient_id')
        if not patient_id or patient_id not in self.patient_stories:
            return
            
        patient = self.patient_stories[patient_id]
        
        # Update based on event type
        if event.get('event_type') == 'DISCHARGE':
            patient['narrative_arc'] = 'resolved'
            patient['discharge_time'] = event.get('timestamp')
        elif event.get('sub_type') == 'BARRIER_RESOLVED':
            if event.get('description'):
                # Remove resolved barrier
                patient['discharge_barriers'] = [
                    b for b in patient.get('discharge_barriers', [])
                    if b not in event['description']
                ]
        elif event.get('sub_type') == 'CLINICAL_UPDATE':
            patient['last_update'] = event.get('description')
            if 'improving' in event.get('description', '').lower():
                patient['narrative_arc'] = 'improving'
            elif 'deteriorating' in event.get('description', '').lower():
                patient['narrative_arc'] = 'critical'
    
    async def get_patient_data(self, patient_id: str) -> Dict[str, Any]:
        """Primary interface for all patient data requests with caching"""
        # Check cache first
        cached_patient = await patient_cache.get_patient(patient_id)
        if cached_patient:
            return cached_patient
            
        # Check memory
        if patient_id not in self.patient_stories:
            # Generate on demand if needed
            bed_id = f"BED-{random.randint(100, 999)}"
            unit = random.choice(["ICU", "Medical", "Surgical", "Emergency"])
            self.patient_stories[patient_id] = await self._generate_patient(bed_id, unit)
        
        # Cache the patient data
        patient_data = self.patient_stories[patient_id]
        await patient_cache.set_patient(patient_id, patient_data, ttl=300)  # 5 minute cache
        
        return patient_data
    
    async def get_all_patients_batch(self) -> Dict[str, Dict[str, Any]]:
        """Get all patient data in batch for performance"""
        # Get all patient IDs from stories
        all_patient_ids = list(self.patient_stories.keys())
        
        # Check cache for all patients
        cached_patients, missing_ids = await patient_cache.get_patients_batch(all_patient_ids)
        
        # Get missing patients from memory and cache them
        for patient_id in missing_ids:
            if patient_id in self.patient_stories:
                patient_data = self.patient_stories[patient_id]
                cached_patients[patient_id] = patient_data
                await patient_cache.set_patient(patient_id, patient_data, ttl=300)
                
        return cached_patients
    
    async def get_discharge_barriers(self, patient_id: str) -> List[str]:
        """Get narrative-appropriate discharge barriers"""
        patient = await self.get_patient_data(patient_id)
        return patient.get('discharge_barriers', [])
    
    async def generate_agent_insight(self, agent_type: str, context: Dict[str, Any]) -> str:
        """Generate narrative-aware insights for agents"""
        patient_context = {}
        if context.get('patient_id'):
            patient_context = await self.get_patient_data(context['patient_id'])
        
        prompt = f"""
        Generate an AI insight for the {agent_type} agent.
        
        Context: {json.dumps(context)}
        Patient info: {json.dumps(patient_context) if patient_context else 'N/A'}
        Hospital state: {json.dumps(self.hospital_context)}
        
        The insight should:
        1. Reference specific patient details if applicable
        2. Be actionable and specific
        3. Demonstrate AI intelligence
        4. Be medically accurate
        5. Create a "wow" moment
        
        Keep it under 100 words.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self._select_model("nano"),  # Simple operation - insights
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Failed to generate agent insight: {e}")
            return "Analyzing patterns in patient flow..."
    
    async def get_session_summary(self) -> Dict[str, Any]:
        """Get narrative summary for the session"""
        return {
            "session_id": self.session_id,
            "duration": (datetime.now() - self.session_start).total_seconds() / 60,
            "narrative_phase": self.narrative_phase,
            "total_patients": len(self.patient_stories),
            "events_generated": len(self.event_history),
            "hospital_context": self.hospital_context,
            "memorable_moments": self._extract_memorable_moments()
        }
    
    def _extract_memorable_moments(self) -> List[str]:
        """Extract key narrative moments from the session"""
        moments = []
        
        # Find interesting events
        for event in self.event_history[-20:]:
            if event.get('narrative_significance'):
                moments.append(event['narrative_significance'])
                
        return moments[-5:] if moments else ["Session just started"]


# Global instance management
_narrative_engine_instance = None

async def get_narrative_engine(session_id: Optional[str] = None) -> NarrativeEngine:
    """Get or create the narrative engine instance"""
    global _narrative_engine_instance
    
    if _narrative_engine_instance is None:
        _narrative_engine_instance = NarrativeEngine(session_id)
        # Don't start here - let the app startup complete first
    
    return _narrative_engine_instance