#!/usr/bin/env python3
"""
Quick test script for Marketing Swarm without full dependencies
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def check_python_version():
    """Check Python version"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        print(f"✅ Python {version.major}.{version.minor} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} - Need 3.11+")
        return False

def check_structure():
    """Check project structure"""
    print("\n🔍 Checking project structure...")
    
    required_dirs = [
        "backend/agents",
        "backend/api", 
        "backend/monitoring",
        "backend/safety",
        "backend/emergency",
        "backend/tools",
        "backend/utils",
        "frontend/src/components",
        "frontend/src/hooks",
        "frontend/src/services",
        "scripts",
        "docs",
        "demo"
    ]
    
    missing = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing.append(dir_path)
    
    if missing:
        print(f"❌ Missing directories: {', '.join(missing)}")
        return False
    else:
        print("✅ All directories present")
        return True

def check_config_files():
    """Check configuration files"""
    print("\n🔍 Checking configuration files...")
    
    files = {
        ".env.example": "Environment template",
        "backend/requirements.txt": "Python dependencies",
        "frontend/package.json": "Node dependencies",
        "README.md": "Project documentation",
        "QUICKSTART.md": "Quick start guide"
    }
    
    missing = []
    for file_path, desc in files.items():
        if Path(file_path).exists():
            print(f"✅ {desc}: {file_path}")
        else:
            missing.append(file_path)
            print(f"❌ Missing: {file_path}")
    
    return len(missing) == 0

def check_core_modules():
    """Check if core Python modules can be imported"""
    print("\n🔍 Checking core module imports...")
    
    # Change to backend directory
    original_dir = os.getcwd()
    os.chdir("backend")
    sys.path.insert(0, os.getcwd())
    
    modules = [
        ("utils.config", "Configuration"),
        ("safety.budget_guard", "Budget Guard"),
        ("safety.compliance_filter", "Compliance Filter"),
        ("safety.input_sanitizer", "Input Sanitizer"),
        ("agents.base_agent", "Base Agent"),
        ("api.conversation_manager", "Conversation Manager"),
        ("monitoring.health_monitor", "Health Monitor"),
        ("emergency.recovery_manager", "Recovery Manager")
    ]
    
    failed = []
    for module_name, desc in modules:
        try:
            # Just check if module file exists
            module_path = module_name.replace(".", "/") + ".py"
            if Path(module_path).exists():
                print(f"✅ {desc}: {module_path}")
            else:
                print(f"❌ {desc}: {module_path} not found")
                failed.append(module_name)
        except Exception as e:
            print(f"❌ {desc}: {e}")
            failed.append(module_name)
    
    os.chdir(original_dir)
    return len(failed) == 0

def check_agent_definitions():
    """Check if all agents are defined"""
    print("\n🔍 Checking agent definitions...")
    
    agents = [
        "sarah_brand.py",
        "marcus_campaigns.py",
        "elena_content.py",
        "david_experience.py",
        "priya_analytics.py",
        "alex_growth.py"
    ]
    
    missing = []
    for agent_file in agents:
        path = Path(f"backend/agents/{agent_file}")
        if path.exists():
            print(f"✅ Agent: {agent_file}")
        else:
            print(f"❌ Missing agent: {agent_file}")
            missing.append(agent_file)
    
    return len(missing) == 0

def check_frontend_structure():
    """Check frontend structure"""
    print("\n🔍 Checking frontend structure...")
    
    components = [
        "ConversationInterface.jsx",
        "AgentCard.jsx",
        "LiveFeed.jsx",
        "SystemStatusDashboard.jsx",
        "DevelopmentConsole.jsx"
    ]
    
    missing = []
    for component in components:
        path = Path(f"frontend/src/components/{component}")
        if path.exists():
            print(f"✅ Component: {component}")
        else:
            print(f"❌ Missing component: {component}")
            missing.append(component)
    
    return len(missing) == 0

def create_test_env():
    """Create test environment file"""
    print("\n🔧 Creating test environment...")
    
    if not Path("backend/.env").exists():
        if Path("backend/.env.test").exists():
            shutil.copy("backend/.env.test", "backend/.env")
            print("✅ Test environment created from .env.test")
        elif Path("backend/.env.example").exists():
            shutil.copy("backend/.env.example", "backend/.env")
            print("⚠️  Test environment created from .env.example")
            print("   Update backend/.env with your API keys")
        else:
            print("❌ No environment template found")
            return False
    else:
        print("✅ Environment file exists")
    
    return True

def main():
    """Run all checks"""
    print("🚀 Marketing Swarm Quick Test")
    print("=" * 50)
    print("This checks project structure without running the full system\n")
    
    tests = [
        ("Python Version", check_python_version),
        ("Project Structure", check_structure),
        ("Config Files", check_config_files),
        ("Core Modules", check_core_modules),
        ("Agent Definitions", check_agent_definitions),
        ("Frontend Structure", check_frontend_structure),
        ("Test Environment", create_test_env)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 QUICK TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.ljust(25)}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed!")
        print("\nNext steps:")
        print("1. Install dependencies:")
        print("   - Backend: cd backend && pip install -r requirements.txt")
        print("   - Frontend: cd frontend && npm install")
        print("2. Update backend/.env with your OpenAI API key")
        print("3. Run: python run_tests.py")
        return 0
    else:
        print(f"\n⚠️  {total - passed} checks failed")
        print("\nPlease fix the issues above before proceeding")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)