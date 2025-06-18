"""
CrewAI Financial Services Marketing Swarm - Main Backend Application
Built with safety, monitoring, and production-readiness in mind
"""

import os
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import logging

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import socketio
import uvicorn
from loguru import logger

# Import our custom modules
from monitoring.health_monitor import SystemHealthMonitor
from monitoring.issue_resolver import AutomatedIssueResolver
from monitoring.launch_tracker import LaunchProgressionTracker
from safety.budget_guard import BudgetGuard
from safety.compliance_filter import ComplianceFilter
from safety.input_sanitizer import InputSanitizer
from emergency.recovery_manager import EmergencyRecovery
from agents.agent_manager import AgentManager
from api.conversation_manager import ConversationManager
from tools.web_search import AgentWebSearchTool
from utils.config import get_settings

# Load environment variables
load_dotenv()

# Initialize settings
settings = get_settings()

# Configure logging
logger.add(
    "logs/system.log",
    rotation="500 MB",
    retention="10 days",
    level=settings.LOG_LEVEL,
    format="{time} {level} {message}",
    enqueue=True
)

# Initialize FastAPI app
app = FastAPI(
    title="Marketing Swarm API",
    description="Multi-agent AI marketing demonstration system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Socket.IO
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=["http://localhost:3000", "http://localhost:3001"],
    logger=True,
    engineio_logger=False
)
socket_app = socketio.ASGIApp(sio, app)

# Initialize system components
health_monitor = SystemHealthMonitor()
issue_resolver = AutomatedIssueResolver()
launch_tracker = LaunchProgressionTracker()
budget_guard = BudgetGuard()
compliance_filter = ComplianceFilter()
input_sanitizer = InputSanitizer()
emergency_recovery = EmergencyRecovery()
agent_manager = AgentManager()
conversation_manager = ConversationManager()

# WebSocket connection tracking
websocket_connections: Dict[str, WebSocket] = {}
active_conversations: Dict[str, Dict] = {}

# Request/Response Models
class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str
    uptime: int
    components: Dict[str, str]

class ConversationRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    user_id: Optional[str] = None
    context: Optional[Dict] = None
    test_mode: bool = False

class ConversationResponse(BaseModel):
    conversation_id: str
    status: str
    message: str

class AgentResponse(BaseModel):
    agent: str
    message: str
    timestamp: str
    has_web_data: bool = False
    thinking_time: float = 0.0

# Health Check Endpoint
@app.get("/api/health", response_model=HealthCheckResponse)
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        health_data = health_monitor.health_data
        return HealthCheckResponse(
            status=health_data.get("backend_status", "unknown"),
            timestamp=datetime.now().isoformat(),
            uptime=health_data.get("uptime", 0),
            components={
                "websocket": health_data.get("websocket_status", "unknown"),
                "database": health_data.get("backend_status", "unknown"),
                "openai_api": health_data.get("api_connectivity", "unknown"),
                "agents": "healthy" if all(
                    status == "healthy" 
                    for status in health_data.get("agent_statuses", {}).values()
                ) else "degraded"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

# Launch Status Endpoint
@app.get("/api/launch-status")
async def get_launch_status():
    """Check system launch readiness"""
    try:
        status = await launch_tracker.run_progression_check()
        return status
    except Exception as e:
        logger.error(f"Launch status check failed: {e}")
        raise HTTPException(status_code=500, detail="Launch status check failed")

# Agent Status Endpoint
@app.get("/api/agents/status")
async def get_agent_status():
    """Get status of all agents"""
    try:
        return await agent_manager.get_all_agent_status()
    except Exception as e:
        logger.error(f"Agent status check failed: {e}")
        raise HTTPException(status_code=500, detail="Agent status check failed")

# Start Conversation Endpoint
@app.post("/api/conversation/start", response_model=ConversationResponse)
async def start_conversation(request: ConversationRequest):
    """Start a new marketing team conversation"""
    try:
        # Sanitize input
        sanitized_query = input_sanitizer.sanitize_user_input(request.query)
        
        # Check compliance
        compliant, filtered_query = compliance_filter.filter_query(sanitized_query)
        if not compliant:
            return ConversationResponse(
                conversation_id="blocked",
                status="blocked",
                message="Query contains non-compliant content"
            )
        
        # Check budget
        budget_ok, budget_message = await budget_guard.check_budget_before_search(0.10)
        if not budget_ok:
            return ConversationResponse(
                conversation_id="budget_exceeded",
                status="error",
                message=budget_message
            )
        
        # Create conversation
        conversation_id = await conversation_manager.create_conversation(
            user_query=filtered_query,
            user_id=request.user_id,
            context=request.context,
            test_mode=request.test_mode
        )
        
        # Start agent discussion asynchronously
        asyncio.create_task(
            run_agent_conversation(conversation_id, filtered_query, request.test_mode)
        )
        
        return ConversationResponse(
            conversation_id=conversation_id,
            status="started",
            message="Marketing team is discussing your query"
        )
        
    except Exception as e:
        logger.error(f"Failed to start conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time conversation updates
@sio.event
async def connect(sid, environ):
    """Handle new WebSocket connection"""
    logger.info(f"Client connected: {sid}")
    health_monitor.websocket_connections.add(sid)
    await sio.emit('connection_established', {'sid': sid}, to=sid)

@sio.event
async def disconnect(sid):
    """Handle WebSocket disconnection"""
    logger.info(f"Client disconnected: {sid}")
    health_monitor.websocket_connections.discard(sid)

@sio.event
async def join_conversation(sid, data):
    """Join a specific conversation room"""
    conversation_id = data.get('conversation_id')
    if conversation_id:
        sio.enter_room(sid, conversation_id)
        await sio.emit('joined_conversation', {
            'conversation_id': conversation_id,
            'status': 'joined'
        }, to=sid)

@sio.event
async def start_conversation(sid, data):
    """Start a new conversation via WebSocket"""
    try:
        request = ConversationRequest(**data)
        response = await start_conversation(request)
        
        # Join the conversation room
        sio.enter_room(sid, response.conversation_id)
        
        await sio.emit('conversation_started', response.dict(), to=sid)
    except Exception as e:
        await sio.emit('error', {'message': str(e)}, to=sid)

# Admin WebSocket endpoints
@sio.event
async def admin_connect(sid, data):
    """Admin dashboard connection"""
    if data.get('auth_token') == settings.ADMIN_AUTH_TOKEN:
        sio.enter_room(sid, 'admin')
        health_monitor.websocket_connections.add(sid)
        await sio.emit('admin_connected', {'status': 'authorized'}, to=sid)
    else:
        await sio.emit('admin_error', {'status': 'unauthorized'}, to=sid)

@sio.event
async def request_full_status(sid, data):
    """Admin request for full system status"""
    if sid in sio.rooms.get('admin', []):
        await sio.emit('system_health_update', health_monitor.health_data, to=sid)

# Emergency endpoints
@app.post("/api/emergency/demo-safe-mode")
async def activate_demo_safe_mode():
    """Activate demo safe mode"""
    try:
        result = await emergency_recovery.activate_demo_safe_mode()
        return result
    except Exception as e:
        logger.error(f"Failed to activate demo safe mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/emergency/reset-system")
async def emergency_reset():
    """Emergency system reset"""
    try:
        await agent_manager.reset_all_agents()
        await conversation_manager.clear_all_conversations()
        health_monitor.reset()
        return {"status": "success", "message": "System reset completed"}
    except Exception as e:
        logger.error(f"Emergency reset failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Agent conversation orchestration
async def run_agent_conversation(
    conversation_id: str, 
    user_query: str, 
    test_mode: bool = False
):
    """Orchestrate the multi-agent conversation"""
    try:
        # Initialize conversation context
        context = {
            "user_query": user_query,
            "conversation_id": conversation_id,
            "agent_responses": [],
            "start_time": time.time()
        }
        
        # Define agent speaking order
        agent_order = ["sarah", "marcus", "elena", "david", "priya", "alex"]
        
        # Phase 1: Initial Analysis with Web Search (45-60 seconds)
        logger.info(f"Starting Phase 1 for conversation {conversation_id}")
        
        for agent_name in agent_order[:3]:  # First 3 agents
            agent = agent_manager.get_agent(agent_name)
            
            # Simulate thinking time
            thinking_time = 2.5 if not test_mode else 0.5
            await asyncio.sleep(thinking_time)
            
            # Get agent response with web search
            response = agent.analyze_with_current_data(user_query, context)
            
            # Apply compliance filtering
            response = compliance_filter.filter_response(response)
            
            # Emit response to WebSocket
            agent_response = AgentResponse(
                agent=agent_name,
                message=response,
                timestamp=datetime.now().isoformat(),
                has_web_data=True,
                thinking_time=thinking_time
            )
            
            await sio.emit('agent_response', agent_response.dict(), room=conversation_id)
            context["agent_responses"].append(agent_response.dict())
            
            # Update conversation in database
            await conversation_manager.add_agent_response(
                conversation_id, 
                agent_name, 
                response
            )
        
        # Phase 2: Collaborative Ideation (90-120 seconds)
        logger.info(f"Starting Phase 2 for conversation {conversation_id}")
        
        for round_num in range(2):  # 2 rounds of discussion
            for agent_name in agent_order:
                agent = agent_manager.get_agent(agent_name)
                
                # Vary thinking time
                thinking_time = 3.0 + (round_num * 0.5) if not test_mode else 0.5
                await asyncio.sleep(thinking_time)
                
                # Get collaborative response
                response = agent.collaborate(context)
                
                # Apply compliance filtering
                response = compliance_filter.filter_response(response)
                
                # Emit response
                agent_response = AgentResponse(
                    agent=agent_name,
                    message=response,
                    timestamp=datetime.now().isoformat(),
                    has_web_data=False,
                    thinking_time=thinking_time
                )
                
                await sio.emit('agent_response', agent_response.dict(), room=conversation_id)
                context["agent_responses"].append(agent_response.dict())
                
                await conversation_manager.add_agent_response(
                    conversation_id, 
                    agent_name, 
                    response
                )
        
        # Phase 3: Solution Synthesis (60-90 seconds)
        logger.info(f"Starting Phase 3 for conversation {conversation_id}")
        
        # Lead agents provide final recommendations
        for agent_name in ["sarah", "alex", "priya"]:
            agent = agent_manager.get_agent(agent_name)
            
            thinking_time = 4.0 if not test_mode else 0.5
            await asyncio.sleep(thinking_time)
            
            # Get synthesis response
            response = agent.synthesize(context)
            
            # Apply compliance filtering
            response = compliance_filter.filter_response(response)
            
            # Emit final response
            agent_response = AgentResponse(
                agent=agent_name,
                message=response,
                timestamp=datetime.now().isoformat(),
                has_web_data=False,
                thinking_time=thinking_time
            )
            
            await sio.emit('agent_response', agent_response.dict(), room=conversation_id)
            context["agent_responses"].append(agent_response.dict())
            
            await conversation_manager.add_agent_response(
                conversation_id, 
                agent_name, 
                response
            )
        
        # Mark conversation as complete
        await conversation_manager.complete_conversation(conversation_id)
        
        # Emit completion event
        await sio.emit('conversation_complete', {
            'conversation_id': conversation_id,
            'duration': time.time() - context["start_time"],
            'total_responses': len(context["agent_responses"])
        }, room=conversation_id)
        
        logger.info(f"Conversation {conversation_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Conversation {conversation_id} failed: {e}")
        await sio.emit('conversation_error', {
            'conversation_id': conversation_id,
            'error': str(e)
        }, room=conversation_id)
        
        # Update conversation status
        await conversation_manager.fail_conversation(conversation_id, str(e))

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    logger.info("Starting Marketing Swarm Backend...")
    
    try:
        # Initialize database
        await conversation_manager.initialize_database()
        
        # Initialize agents
        await agent_manager.initialize_all_agents()
        
        # Start monitoring systems
        asyncio.create_task(health_monitor.continuous_health_check())
        asyncio.create_task(issue_resolver.detect_and_resolve_issues())
        
        # Run initial health check
        initial_status = await launch_tracker.run_progression_check()
        logger.info(f"Initial system status: {initial_status['percentage']}% ready")
        
        logger.info("Marketing Swarm Backend started successfully!")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Marketing Swarm Backend...")
    
    try:
        # Close all WebSocket connections
        for sid in list(health_monitor.websocket_connections):
            await sio.disconnect(sid)
        
        # Save system state
        await conversation_manager.close()
        
        logger.info("Marketing Swarm Backend shut down successfully")
        
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "main:socket_app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEV_MODE,
        log_level=settings.LOG_LEVEL.lower()
    )