#!/usr/bin/env python3
"""
Marketing Swarm Backend Startup Helper
Choose which backend implementation to run
"""

import os
import sys
import subprocess

def main():
    print("\n🚀 Marketing Swarm Backend Launcher")
    print("="*50)
    print("\nChoose which backend to run:")
    print("\n1. main_simple.py (Recommended - Socket.IO compatible)")
    print("   - Simplified implementation")
    print("   - Socket.IO support for frontend")
    print("   - Mock agent responses")
    print("   - Runs on port 8001")
    
    print("\n2. main.py (Full featured)")
    print("   - Complete implementation")
    print("   - Requires all dependencies")
    print("   - Full agent system")
    print("   - Runs on port 8001")
    
    print("\n3. minimal_server.py (Basic demo)")
    print("   - Minimal WebSocket demo")
    print("   - Not compatible with React frontend")
    print("   - Use with demo.html instead")
    print("   - Runs on port 8000")
    
    choice = input("\nEnter your choice (1-3, or 'q' to quit): ").strip()
    
    if choice == 'q':
        print("👋 Exiting...")
        return
    
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    
    if choice == '1':
        print("\n✅ Starting main_simple.py...")
        print("📍 Backend will run on: http://localhost:8001")
        print("🎨 Frontend should run on: http://localhost:3001")
        print("\n" + "-"*50)
        subprocess.run([sys.executable, "main_simple.py"])
        
    elif choice == '2':
        print("\n✅ Starting main.py...")
        print("⚠️  Make sure all dependencies are installed!")
        print("📍 Backend will run on: http://localhost:8001")
        print("🎨 Frontend should run on: http://localhost:3001")
        print("\n" + "-"*50)
        subprocess.run([sys.executable, "main.py"])
        
    elif choice == '3':
        print("\n✅ Starting minimal_server.py...")
        print("⚠️  This is not compatible with the React frontend!")
        print("📍 Backend will run on: http://localhost:8000")
        print("🌐 Use demo.html in browser instead")
        print("\n" + "-"*50)
        subprocess.run([sys.executable, "minimal_server.py"])
        
    else:
        print("\n❌ Invalid choice. Please run again and select 1-3.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Shutdown by user")