
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
