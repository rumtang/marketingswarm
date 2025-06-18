#!/usr/bin/env python3
"""
Backend Connection Test Script
Tests all backend components without modifying existing code
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, List

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test results storage
test_results = {
    "timestamp": datetime.now().isoformat(),
    "tests": {},
    "summary": {
        "total": 0,
        "passed": 0,
        "failed": 0
    }
}

def record_test(test_name: str, passed: bool, details: str = ""):
    """Record test result"""
    test_results["tests"][test_name] = {
        "passed": passed,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    test_results["summary"]["total"] += 1
    if passed:
        test_results["summary"]["passed"] += 1
    else:
        test_results["summary"]["failed"] += 1
    
    # Print result
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details and not passed:
        print(f"    Details: {details}")

async def test_imports():
    """Test if all required modules can be imported"""
    print("\n🔍 Testing imports...")
    
    try:
        import fastapi
        import socketio
        import uvicorn
        from loguru import logger
        record_test("Core imports", True)
    except ImportError as e:
        record_test("Core imports", False, str(e))
        return False
    
    try:
        from utils.config import get_settings, validate_environment
        record_test("Utils imports", True)
    except ImportError as e:
        record_test("Utils imports", False, str(e))
    
    try:
        from safety.budget_guard import BudgetGuard
        from safety.compliance_filter import ComplianceFilter
        from safety.input_sanitizer import InputSanitizer
        record_test("Safety imports", True)
    except ImportError as e:
        record_test("Safety imports", False, str(e))
    
    return True

async def test_environment():
    """Test environment configuration"""
    print("\n🔍 Testing environment...")
    
    try:
        from utils.config import validate_environment
        validate_environment()
        record_test("Environment validation", True)
    except Exception as e:
        record_test("Environment validation", False, str(e))
    
    # Check critical environment variables
    critical_vars = ["OPENAI_API_KEY", "FASTAPI_SECRET_KEY"]
    for var in critical_vars:
        if os.getenv(var):
            record_test(f"Environment var: {var}", True)
        else:
            record_test(f"Environment var: {var}", False, "Not set")

async def test_database():
    """Test database connection"""
    print("\n🔍 Testing database...")
    
    try:
        import sqlite3
        db_path = "test_marketing_swarm.db"
        
        # Test connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        conn.close()
        record_test("Database connection", True, f"Found {len(tables)} tables")
    except Exception as e:
        record_test("Database connection", False, str(e))

async def test_agents():
    """Test agent initialization"""
    print("\n🔍 Testing agents...")
    
    try:
        from agents.sarah_brand import SarahBrandAgent
        from agents.marcus_campaigns import MarcusCampaignAgent
        from agents.elena_content import ElenaContentAgent
        from agents.david_experience import DavidExperienceAgent
        from agents.priya_analytics import PriyaAnalyticsAgent
        from agents.alex_growth import AlexGrowthAgent
        
        agents = {
            "Sarah": SarahBrandAgent,
            "Marcus": MarcusCampaignAgent,
            "Elena": ElenaContentAgent,
            "David": DavidExperienceAgent,
            "Priya": PriyaAnalyticsAgent,
            "Alex": AlexGrowthAgent
        }
        
        for name, AgentClass in agents.items():
            try:
                agent = AgentClass()
                # Test agent has required attributes
                assert hasattr(agent, 'name')
                assert hasattr(agent, 'role')
                assert hasattr(agent, '_generate_analysis_response')
                record_test(f"Agent: {name}", True)
            except Exception as e:
                record_test(f"Agent: {name}", False, str(e))
                
    except Exception as e:
        record_test("Agent imports", False, str(e))

async def test_api_endpoints():
    """Test API endpoints"""
    print("\n🔍 Testing API endpoints...")
    
    import aiohttp
    
    base_url = "http://localhost:8001"
    endpoints = [
        ("/api/health", "GET", None),
        ("/api/agents/status", "GET", None),
        ("/api/launch-status", "GET", None),
        ("/api/conversation/start", "POST", {
            "user_query": "Test query",
            "test_mode": True
        })
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint, method, data in endpoints:
            try:
                url = f"{base_url}{endpoint}"
                
                if method == "GET":
                    async with session.get(url) as response:
                        if response.status == 200:
                            record_test(f"API: {endpoint}", True)
                        else:
                            record_test(f"API: {endpoint}", False, f"Status: {response.status}")
                else:  # POST
                    headers = {"Content-Type": "application/json"}
                    async with session.post(url, json=data, headers=headers) as response:
                        if response.status == 200:
                            record_test(f"API: {endpoint}", True)
                        else:
                            record_test(f"API: {endpoint}", False, f"Status: {response.status}")
                            
            except Exception as e:
                record_test(f"API: {endpoint}", False, str(e))

async def test_websocket():
    """Test WebSocket connectivity"""
    print("\n🔍 Testing WebSocket...")
    
    try:
        import socketio
        
        sio = socketio.AsyncClient()
        connected = False
        
        @sio.event
        async def connect():
            nonlocal connected
            connected = True
        
        @sio.event
        async def connection_established(data):
            pass
        
        try:
            await sio.connect('http://localhost:8001')
            await asyncio.sleep(1)
            
            if connected:
                record_test("WebSocket connection", True)
                await sio.disconnect()
            else:
                record_test("WebSocket connection", False, "Failed to connect")
                
        except Exception as e:
            record_test("WebSocket connection", False, str(e))
            
    except Exception as e:
        record_test("WebSocket imports", False, str(e))

async def test_safety_systems():
    """Test safety systems"""
    print("\n🔍 Testing safety systems...")
    
    try:
        from safety.budget_guard import BudgetGuard
        from safety.compliance_filter import ComplianceFilter
        from safety.input_sanitizer import InputSanitizer
        
        # Test Budget Guard
        try:
            budget_guard = BudgetGuard()
            can_proceed, message = await budget_guard.check_budget_before_search(0.01)
            record_test("Budget Guard", True, f"Can proceed: {can_proceed}")
        except Exception as e:
            record_test("Budget Guard", False, str(e))
        
        # Test Compliance Filter
        try:
            compliance_filter = ComplianceFilter()
            test_query = "How do I invest in stocks?"
            is_compliant, filtered = compliance_filter.filter_query(test_query)
            record_test("Compliance Filter", True, f"Compliant: {is_compliant}")
        except Exception as e:
            record_test("Compliance Filter", False, str(e))
        
        # Test Input Sanitizer
        try:
            input_sanitizer = InputSanitizer()
            test_input = "Test <script>alert('xss')</script> input"
            sanitized = input_sanitizer.sanitize_user_input(test_input)
            record_test("Input Sanitizer", True, f"Sanitized: {sanitized[:50]}...")
        except Exception as e:
            record_test("Input Sanitizer", False, str(e))
            
    except Exception as e:
        record_test("Safety system imports", False, str(e))

async def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Marketing Swarm Backend Connection Tests")
    print("=" * 60)
    
    # Run tests
    await test_imports()
    await test_environment()
    await test_database()
    await test_agents()
    await test_api_endpoints()
    await test_websocket()
    await test_safety_systems()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"Total Tests: {test_results['summary']['total']}")
    print(f"Passed: {test_results['summary']['passed']} ✅")
    print(f"Failed: {test_results['summary']['failed']} ❌")
    
    # Calculate pass rate
    if test_results['summary']['total'] > 0:
        pass_rate = (test_results['summary']['passed'] / test_results['summary']['total']) * 100
        print(f"Pass Rate: {pass_rate:.1f}%")
    
    # Save results
    with open('test_results_backend.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    print(f"\n💾 Results saved to test_results_backend.json")
    
    # Return exit code
    return 0 if test_results['summary']['failed'] == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)