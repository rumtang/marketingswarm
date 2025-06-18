#!/usr/bin/env python3
"""
Comprehensive test runner for Marketing Swarm
Handles both backend and integration testing
"""

import subprocess
import sys
import os
import time
import signal
import shutil
from pathlib import Path

class TestRunner:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.test_results = []
        
    def setup_test_environment(self):
        """Setup test environment"""
        print("🔧 Setting up test environment...")
        
        # Copy test env file
        backend_dir = Path("backend")
        if (backend_dir / ".env.test").exists():
            shutil.copy(backend_dir / ".env.test", backend_dir / ".env")
            print("✅ Test configuration loaded")
        else:
            print("⚠️  No .env.test found, using .env.example")
            if (backend_dir / ".env.example").exists():
                shutil.copy(backend_dir / ".env.example", backend_dir / ".env")
            else:
                print("❌ No configuration files found!")
                return False
        
        return True
    
    def start_backend(self):
        """Start backend server"""
        print("\n🚀 Starting backend server...")
        
        # Change to backend directory
        os.chdir("backend")
        
        # Start backend process
        self.backend_process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Change back to root
        os.chdir("..")
        
        # Wait for backend to be ready
        print("⏳ Waiting for backend to start...")
        for i in range(30):
            try:
                import requests
                resp = requests.get("http://localhost:8000/api/health")
                if resp.status_code == 200:
                    print("✅ Backend is ready")
                    return True
            except:
                pass
            time.sleep(1)
            
            # Check if process crashed
            if self.backend_process.poll() is not None:
                stdout, stderr = self.backend_process.communicate()
                print("❌ Backend crashed during startup")
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                return False
        
        print("❌ Backend failed to start within 30 seconds")
        return False
    
    def run_backend_tests(self):
        """Run backend unit tests"""
        print("\n🧪 Running backend tests...")
        
        os.chdir("backend")
        
        # Run basic tests
        print("\n1️⃣ Basic tests:")
        result = subprocess.run(
            [sys.executable, "test_basic.py"],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print(f"Errors: {result.stderr}")
        
        self.test_results.append(("Basic Tests", result.returncode == 0))
        
        os.chdir("..")
        
    def run_integration_tests(self):
        """Run integration tests"""
        print("\n🧪 Running integration tests...")
        
        os.chdir("backend")
        
        result = subprocess.run(
            [sys.executable, "test_integration.py"],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print(f"Errors: {result.stderr}")
        
        self.test_results.append(("Integration Tests", result.returncode == 0))
        
        os.chdir("..")
    
    def cleanup(self):
        """Cleanup test processes"""
        print("\n🧹 Cleaning up...")
        
        if self.backend_process:
            print("Stopping backend...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                self.backend_process.wait()
        
        # Clean up test database
        test_db = Path("backend/test_marketing_swarm.db")
        if test_db.exists():
            test_db.unlink()
            print("✅ Test database cleaned up")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        for test_name, passed in self.test_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{test_name.ljust(30)}: {status}")
        
        total = len(self.test_results)
        passed = sum(1 for _, p in self.test_results if p)
        
        print(f"\nTotal: {passed}/{total} test suites passed")
        
        if passed == total:
            print("\n🎉 All tests passed!")
            print("\nNext steps:")
            print("1. Update backend/.env with your real OpenAI API key")
            print("2. Run: cd backend && python main.py")
            print("3. Run: cd frontend && npm start")
            print("4. Open http://localhost:3000")
            return 0
        else:
            print(f"\n⚠️  {total - passed} test suites failed")
            print("\nTroubleshooting:")
            print("1. Check the error messages above")
            print("2. Ensure all dependencies are installed:")
            print("   - Backend: pip install -r backend/requirements.txt")
            print("   - Frontend: cd frontend && npm install")
            return 1
    
    def run(self):
        """Run all tests"""
        print("🚀 Marketing Swarm Test Suite")
        print("=" * 60)
        
        try:
            # Setup test environment
            if not self.setup_test_environment():
                return 1
            
            # Run backend tests (without server)
            self.run_backend_tests()
            
            # Start backend for integration tests
            if self.start_backend():
                self.run_integration_tests()
            else:
                print("❌ Skipping integration tests - backend failed to start")
                self.test_results.append(("Integration Tests", False))
            
            # Print summary
            return self.print_summary()
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Tests interrupted by user")
            return 1
        finally:
            self.cleanup()

def main():
    """Main entry point"""
    runner = TestRunner()
    
    # Handle signals properly
    def signal_handler(sig, frame):
        print("\n⚠️  Received interrupt signal")
        runner.cleanup()
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run tests
    exit_code = runner.run()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()