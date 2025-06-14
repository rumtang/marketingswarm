"""
Session management for demo narratives
"""

import asyncio
import uuid
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import logging
import json

from .engine import NarrativeEngine
from .models import DemoScenario, SessionState
from .scenarios import DEMO_SCENARIOS

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages narrative sessions for demos"""
    
    def __init__(self):
        self.active_sessions: Dict[str, NarrativeEngine] = {}
        self.session_states: Dict[str, SessionState] = {}
        self.cleanup_task = None
        
    async def start(self):
        """Start the session manager"""
        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_old_sessions())
        logger.info("Session manager started")
        
    async def stop(self):
        """Stop the session manager"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
                
    async def create_session(self, scenario_name: Optional[str] = None) -> tuple[str, NarrativeEngine]:
        """Create a new narrative session"""
        session_id = str(uuid.uuid4())[:8]
        
        # Create narrative engine
        engine = NarrativeEngine(session_id, demo_mode=True)
        
        # Load scenario if specified
        scenario = None
        if scenario_name and scenario_name in DEMO_SCENARIOS:
            scenario = DemoScenario(**DEMO_SCENARIOS[scenario_name])
            logger.info(f"Loading demo scenario: {scenario_name}")
            
        # Create session state
        state = SessionState(
            session_id=session_id,
            started_at=datetime.utcnow(),
            demo_scenario=scenario,
            hospital_context=engine.hospital_context
        )
        
        self.active_sessions[session_id] = engine
        self.session_states[session_id] = state
        
        # Initialize scenario if provided
        if scenario:
            await self._initialize_scenario(engine, scenario)
            
        logger.info(f"Created session {session_id} with scenario: {scenario_name or 'freestyle'}")
        return session_id, engine
        
    async def get_session(self, session_id: str) -> Optional[NarrativeEngine]:
        """Get an active session"""
        return self.active_sessions.get(session_id)
        
    async def end_session(self, session_id: str):
        """End a session and clean up"""
        if session_id in self.active_sessions:
            engine = self.active_sessions[session_id]
            summary = engine.get_session_summary()
            
            logger.info(f"Ending session {session_id}: {summary}")
            
            # Save session summary for analytics
            await self._save_session_summary(session_id, summary)
            
            # Clean up
            del self.active_sessions[session_id]
            del self.session_states[session_id]
            
    async def _initialize_scenario(self, engine: NarrativeEngine, scenario: DemoScenario):
        """Initialize a demo scenario"""
        # Pre-generate some patients
        beds_to_fill = int(scenario.initial_occupancy * 30)  # Assuming ~30 visible beds
        
        units = ["ICU", "CARDIAC", "NEURO", "ORTHO", "MED-SURG"]
        for i in range(beds_to_fill):
            unit = units[i % len(units)]
            bed_id = f"{unit}-{i:03d}"
            
            # Generate patient
            patient = await engine.generate_patient(bed_id, unit)
            
            # Add scenario-specific elements
            if i < len(scenario.scripted_events):
                # This patient will be involved in scripted events
                patient.key_moments.append("Selected for demo scenario")
                
        # Schedule scripted events
        if scenario.scripted_events:
            asyncio.create_task(self._run_scripted_events(engine, scenario))
            
    async def _run_scripted_events(self, engine: NarrativeEngine, scenario: DemoScenario):
        """Run scripted events at specified times"""
        start_time = datetime.utcnow()
        
        for event in scenario.scripted_events:
            # Wait until event time
            wait_minutes = event.get("time_minutes", 0)
            wait_seconds = wait_minutes * 60
            elapsed = (datetime.utcnow() - start_time).seconds
            
            if wait_seconds > elapsed:
                await asyncio.sleep(wait_seconds - elapsed)
                
            # Generate the event
            try:
                await engine.generate_event(
                    trigger=event.get("trigger", "Scheduled event"),
                    patient_id=event.get("patient_id")
                )
            except Exception as e:
                logger.error(f"Error running scripted event: {e}")
                
    async def _cleanup_old_sessions(self):
        """Clean up sessions older than 2 hours"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                cutoff = datetime.utcnow() - timedelta(hours=2)
                sessions_to_remove = []
                
                for session_id, state in self.session_states.items():
                    if state.started_at < cutoff:
                        sessions_to_remove.append(session_id)
                        
                for session_id in sessions_to_remove:
                    await self.end_session(session_id)
                    logger.info(f"Cleaned up old session: {session_id}")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                
    async def _save_session_summary(self, session_id: str, summary: Dict):
        """Save session summary for analytics"""
        try:
            # In production, save to database
            # For now, just log it
            logger.info(f"Session {session_id} summary: {json.dumps(summary, indent=2)}")
        except Exception as e:
            logger.error(f"Error saving session summary: {e}")
            
    def get_active_sessions(self) -> List[Dict]:
        """Get list of active sessions"""
        sessions = []
        for session_id, state in self.session_states.items():
            engine = self.active_sessions.get(session_id)
            if engine:
                sessions.append({
                    "session_id": session_id,
                    "started_at": state.started_at.isoformat(),
                    "duration_minutes": (datetime.utcnow() - state.started_at).seconds // 60,
                    "scenario": state.demo_scenario.name if state.demo_scenario else "Freestyle",
                    "patient_count": len(engine.patient_stories),
                    "event_count": len(engine.event_history),
                    "wow_moments": engine.wow_moments_count
                })
        return sessions