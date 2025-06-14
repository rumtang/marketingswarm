import pytest
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.capacity_predictor import CapacityPredictor
from app.agents.discharge_accelerator import DischargeAccelerator
from app.agents.concierge_chat import ConciergeChat


@pytest.mark.asyncio
async def test_capacity_predictor():
    """Test capacity prediction agent"""
    predictor = CapacityPredictor()
    
    # Mock bed data
    mock_beds = [
        {
            'bed_id': 'ICU-001',
            'unit': 'ICU',
            'status': 'occupied',
            'admission_time': (datetime.utcnow() - timedelta(days=2)).isoformat()
        },
        {
            'bed_id': 'ICU-002',
            'unit': 'ICU',
            'status': 'available',
            'admission_time': None
        }
    ]
    
    result = await predictor.predict(mock_beds)
    
    assert 'predictions' in result
    assert 'current_occupancy' in result
    assert len(result['predictions']) == 24  # 24 hour forecast
    assert 0 <= result['current_occupancy'] <= 1


@pytest.mark.asyncio
async def test_discharge_accelerator():
    """Test discharge barrier detection"""
    accelerator = DischargeAccelerator()
    
    # Mock patient data
    mock_patient = {
        'patient_id': 'P001',
        'admission_time': (datetime.utcnow() - timedelta(days=5)).isoformat(),
        'diagnosis': 'Pneumonia',
        'barriers': []
    }
    
    result = await accelerator.analyze_patient(mock_patient)
    
    assert 'patient_id' in result
    assert 'barriers' in result
    assert 'recommendations' in result
    assert result['patient_id'] == 'P001'


@pytest.mark.asyncio
async def test_concierge_chat():
    """Test chat agent responses"""
    chat = ConciergeChat()
    
    # Test visiting hours query
    response = await chat.respond("What are visiting hours?", {})
    
    assert 'response' in response
    assert 'visiting hours' in response['response'].lower()
    assert response['type'] == 'informational'
    
    # Test emergency detection
    emergency_response = await chat.respond("Help! I can't breathe!", {})
    
    assert emergency_response['type'] == 'emergency'
    assert 'nurse call button' in emergency_response['response'].lower()


def test_barrier_types():
    """Test discharge barrier configuration"""
    accelerator = DischargeAccelerator()
    
    assert len(accelerator.barrier_types) > 0
    
    for barrier in accelerator.barrier_types:
        assert 'type' in barrier
        assert 'description' in barrier
        assert 'avg_delay_hours' in barrier
        assert 'action' in barrier