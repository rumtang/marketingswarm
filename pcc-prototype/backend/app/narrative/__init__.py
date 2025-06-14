"""
Narrative Engine for generating dynamic, coherent patient stories
"""

from .engine import NarrativeEngine
from .models import PatientStory, HospitalContext, DemoScenario
from .session_manager import SessionManager

__all__ = [
    'NarrativeEngine',
    'PatientStory',
    'HospitalContext',
    'DemoScenario',
    'SessionManager'
]