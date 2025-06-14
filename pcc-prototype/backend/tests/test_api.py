import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"


def test_bed_status_endpoint():
    """Test bed status endpoint"""
    response = client.get("/api/bed-status")
    assert response.status_code == 200
    data = response.json()
    assert "beds" in data
    assert "timestamp" in data


def test_capacity_forecast_endpoint():
    """Test capacity forecast endpoint"""
    response = client.get("/api/capacity-forecast")
    assert response.status_code == 200
    data = response.json()
    assert "forecast" in data
    assert "timestamp" in data


def test_chat_endpoint():
    """Test chat endpoint"""
    response = client.post(
        "/api/chat",
        json={
            "message": "What are visiting hours?",
            "context": {}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "timestamp" in data


def test_discharge_barriers_endpoint():
    """Test discharge barriers endpoint"""
    # This will return error for non-existent patient
    response = client.get("/api/discharge-barriers/P999999")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data or "barriers" in data


def test_alerts_endpoint():
    """Test alerts endpoint"""
    response = client.get("/api/alerts")
    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data
    assert "timestamp" in data