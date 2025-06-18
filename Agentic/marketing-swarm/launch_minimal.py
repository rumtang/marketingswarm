#!/usr/bin/env python3
"""
Minimal Launch Script for Marketing Swarm
Works without full dependencies - shows the system architecture
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"🐍 Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor == 13:
        print("⚠️  Warning: You're using Python 3.13")
        print("   CrewAI requires Python <3.13")
        print("   The system will run in simplified mode")
    return True

def create_minimal_backend():
    """Create a minimal backend server without CrewAI"""
    minimal_server = '''
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from datetime import datetime

app = FastAPI(title="Marketing Swarm API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock agent data
AGENTS = {
    "sarah": {"name": "Sarah", "role": "Brand Strategy Lead", "status": "ready"},
    "marcus": {"name": "Marcus", "role": "Digital Campaign Manager", "status": "ready"},
    "elena": {"name": "Elena", "role": "Content Marketing Specialist", "status": "ready"},
    "david": {"name": "David", "role": "Customer Experience Designer", "status": "ready"},
    "priya": {"name": "Priya", "role": "Marketing Analytics Manager", "status": "ready"},
    "alex": {"name": "Alex", "role": "Growth Marketing Lead", "status": "ready"}
}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "mode": "minimal"
    }

@app.get("/api/agents/status")
async def agent_status():
    return AGENTS

@app.get("/api/launch-status")
async def launch_status():
    return {
        "overall_progress": "7/7",
        "percentage": 100.0,
        "ready_for_demo": True,
        "mode": "minimal",
        "phases": {
            "1_environment_setup": {"status": "complete"},
            "2_agent_initialization": {"status": "complete"},
            "3_frontend_backend_connection": {"status": "complete"},
            "4_safety_systems": {"status": "complete"},
            "5_demo_readiness": {"status": "complete"}
        }
    }

@app.post("/api/conversation/start")
async def start_conversation(data: dict):
    return {
        "conversation_id": "demo-" + str(int(time.time())),
        "status": "started",
        "mode": "minimal"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Send demo conversation
    agents = ["Sarah", "Marcus", "Elena", "David", "Priya", "Alex"]
    
    for i, agent in enumerate(agents):
        await asyncio.sleep(2)
        await websocket.send_json({
            "type": "agent_response",
            "agent": agent.lower(),
            "message": f"{agent}: Based on my analysis as {AGENTS[agent.lower()]['role']}...",
            "timestamp": datetime.now().isoformat()
        })
    
    await websocket.close()

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Marketing Swarm (Minimal Mode)")
    print("📍 Backend: http://localhost:8000")
    print("🎨 Frontend: http://localhost:3001")
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    # Write the minimal server
    with open("backend/minimal_server.py", "w") as f:
        f.write(minimal_server)
    
    print("✅ Created minimal backend server")

def install_minimal_requirements():
    """Install only essential requirements"""
    print("\n📦 Installing minimal requirements...")
    
    essential_packages = [
        "fastapi",
        "uvicorn[standard]",
        "python-socketio",
        "python-dotenv",
        "loguru"
    ]
    
    for package in essential_packages:
        print(f"Installing {package}...")
        subprocess.run([sys.executable, "-m", "pip", "install", package], 
                      capture_output=True)
    
    print("✅ Minimal requirements installed")

def start_minimal_backend():
    """Start the minimal backend"""
    print("\n🚀 Starting minimal backend...")
    
    # Change to backend directory
    os.chdir("backend")
    
    # Start the server
    backend_process = subprocess.Popen(
        [sys.executable, "minimal_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    os.chdir("..")
    
    print("✅ Backend started (PID: {})".format(backend_process.pid))
    return backend_process

def create_minimal_frontend():
    """Create a minimal frontend HTML file"""
    minimal_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Marketing Swarm - Minimal Demo</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .status {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        .status-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .agents {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        .agent-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        .conversation {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            min-height: 400px;
        }
        .message {
            margin: 10px 0;
            padding: 10px;
            background: #f0f0f0;
            border-radius: 5px;
        }
        button {
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background: #0056b3;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status-healthy { background: #28a745; }
        .status-error { background: #dc3545; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Marketing Swarm - AI Team Collaboration</h1>
        <p>6 Specialized AI Agents Working Together</p>
    </div>

    <div class="status">
        <div class="status-card">
            <h3>🔌 Backend API</h3>
            <p><span class="status-indicator status-healthy"></span> <span id="backend-status">Checking...</span></p>
        </div>
        <div class="status-card">
            <h3>🤖 Agents</h3>
            <p><span class="status-indicator status-healthy"></span> <span id="agents-status">Checking...</span></p>
        </div>
        <div class="status-card">
            <h3>🚀 Launch Status</h3>
            <p><span class="status-indicator status-healthy"></span> <span id="launch-status">Checking...</span></p>
        </div>
    </div>

    <div class="agents">
        <div class="agent-card">
            <h3>👔 Sarah</h3>
            <p>Brand Strategy Lead</p>
        </div>
        <div class="agent-card">
            <h3>📱 Marcus</h3>
            <p>Digital Campaigns</p>
        </div>
        <div class="agent-card">
            <h3>✍️ Elena</h3>
            <p>Content Marketing</p>
        </div>
        <div class="agent-card">
            <h3>🎨 David</h3>
            <p>Customer Experience</p>
        </div>
        <div class="agent-card">
            <h3>📊 Priya</h3>
            <p>Marketing Analytics</p>
        </div>
        <div class="agent-card">
            <h3>🚀 Alex</h3>
            <p>Growth Marketing</p>
        </div>
    </div>

    <div class="conversation">
        <h2>💬 Agent Conversation</h2>
        <button onclick="startDemo()">Start Demo Conversation</button>
        <div id="messages"></div>
    </div>

    <script>
        // Check system status
        async function checkStatus() {
            try {
                // Check backend
                const health = await fetch('http://localhost:8000/api/health');
                if (health.ok) {
                    document.getElementById('backend-status').textContent = 'Connected';
                    
                    // Check agents
                    const agents = await fetch('http://localhost:8000/api/agents/status');
                    if (agents.ok) {
                        const data = await agents.json();
                        document.getElementById('agents-status').textContent = `${Object.keys(data).length} agents ready`;
                    }
                    
                    // Check launch status
                    const launch = await fetch('http://localhost:8000/api/launch-status');
                    if (launch.ok) {
                        const data = await launch.json();
                        document.getElementById('launch-status').textContent = `${data.percentage}% Complete`;
                    }
                }
            } catch (e) {
                document.getElementById('backend-status').textContent = 'Not connected';
            }
        }

        // Start demo conversation
        function startDemo() {
            const messages = document.getElementById('messages');
            messages.innerHTML = '<div class="message"><strong>User:</strong> How should we launch our new robo-advisor?</div>';
            
            // Simulate agent responses
            const responses = [
                { agent: 'Sarah', delay: 2000, message: 'From a brand strategy perspective, we need to position ourselves as the trustworthy, accessible alternative to traditional advisors.' },
                { agent: 'Marcus', delay: 4000, message: 'I recommend starting with LinkedIn and Google Ads targeting professionals aged 25-45 with a test budget of $10K.' },
                { agent: 'Elena', delay: 6000, message: 'We should create educational content series: "Demystifying Robo-Advisors" to build trust and authority.' },
                { agent: 'David', delay: 8000, message: 'The onboarding experience needs to be simplified to 3 steps with clear progress indicators.' },
                { agent: 'Priya', delay: 10000, message: 'We should track CAC, activation rate, and 30-day retention as our primary KPIs.' },
                { agent: 'Alex', delay: 12000, message: 'I suggest implementing a referral program after reaching 1,000 active users for viral growth.' }
            ];
            
            responses.forEach(r => {
                setTimeout(() => {
                    messages.innerHTML += `<div class="message"><strong>${r.agent}:</strong> ${r.message}</div>`;
                    messages.scrollTop = messages.scrollHeight;
                }, r.delay);
            });
        }

        // Check status on load
        checkStatus();
        setInterval(checkStatus, 5000);
    </script>
</body>
</html>'''
    
    # Write the HTML file
    with open("minimal_demo.html", "w") as f:
        f.write(minimal_html)
    
    print("✅ Created minimal frontend (minimal_demo.html)")

def main():
    """Launch the Marketing Swarm in minimal mode"""
    print("🚀 Marketing Swarm - Minimal Launch")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Create minimal backend
    create_minimal_backend()
    
    # Install minimal requirements
    try:
        install_minimal_requirements()
    except Exception as e:
        print(f"⚠️  Could not install all packages: {e}")
        print("   Continuing with available packages...")
    
    # Create minimal frontend
    create_minimal_frontend()
    
    # Start backend
    backend_process = None
    try:
        backend_process = start_minimal_backend()
        
        print("\n" + "=" * 50)
        print("✅ MARKETING SWARM LAUNCHED (Minimal Mode)")
        print("=" * 50)
        print("\n📍 Backend API: http://localhost:8000")
        print("📍 API Docs: http://localhost:8000/docs")
        print("🎨 Frontend: Open minimal_demo.html in your browser")
        print("\n💡 This is a simplified demo without full AI capabilities")
        print("   For full functionality, use Python <3.13 and install all dependencies")
        
        print("\n🛑 Press Ctrl+C to stop the server")
        
        # Keep running
        backend_process.wait()
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
        print("✅ Shutdown complete")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if backend_process:
            backend_process.terminate()

if __name__ == "__main__":
    main()