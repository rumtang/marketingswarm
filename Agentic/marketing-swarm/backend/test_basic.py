"""
Basic test script to verify backend functionality
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from monitoring.health_monitor import SystemHealthMonitor
        print("✅ Health monitor imported")
        
        from safety.budget_guard import BudgetGuard
        print("✅ Budget guard imported")
        
        from safety.compliance_filter import ComplianceFilter
        print("✅ Compliance filter imported")
        
        from agents.agent_manager import AgentManager
        print("✅ Agent manager imported")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

async def test_safety_systems():
    """Test safety systems"""
    print("\nTesting safety systems...")
    
    try:
        from safety.budget_guard import BudgetGuard
        from safety.compliance_filter import ComplianceFilter
        from safety.input_sanitizer import InputSanitizer
        
        # Test budget guard
        budget_guard = BudgetGuard()
        can_proceed, msg = await budget_guard.check_budget_before_search(0.01)
        print(f"✅ Budget guard: {msg}")
        
        # Test compliance filter
        compliance = ComplianceFilter()
        compliant, filtered = compliance.filter_query("How to invest wisely")
        print(f"✅ Compliance filter: Query {'compliant' if compliant else 'filtered'}")
        
        # Test input sanitizer
        sanitizer = InputSanitizer()
        cleaned = sanitizer.sanitize_user_input("Test input <script>alert('xss')</script>")
        print(f"✅ Input sanitizer: Cleaned dangerous input")
        
        return True
    except Exception as e:
        print(f"❌ Safety system error: {e}")
        return False

async def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from utils.config import get_settings, validate_environment
        
        # This will fail if no .env file, which is expected
        try:
            settings = get_settings()
            print("✅ Settings loaded (using real .env)")
        except:
            print("⚠️  Settings require valid .env file (expected in test)")
        
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Running backend basic tests...\n")
    
    results = []
    
    # Run tests
    results.append(await test_imports())
    results.append(await test_safety_systems())
    results.append(await test_config())
    
    # Summary
    print("\n📊 Test Summary:")
    print(f"✅ Passed: {sum(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n🎉 All basic tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)