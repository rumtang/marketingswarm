#!/usr/bin/env python3
"""
Test Socket.IO connection to the Marketing Swarm backend
"""

import socketio
import asyncio

async def test_socketio_connection():
    """Test Socket.IO connection"""
    # Create a Socket.IO client
    sio = socketio.AsyncClient()
    
    # Event handlers
    @sio.event
    async def connect():
        print("✅ Connected to Socket.IO server")
        
    @sio.event
    async def connection_established(data):
        print(f"✅ Connection established: {data}")
        
    @sio.event
    async def disconnect():
        print("❌ Disconnected from Socket.IO server")
        
    @sio.event
    async def error(data):
        print(f"❌ Error: {data}")
        
    @sio.event
    async def agent_response(data):
        print(f"🤖 Agent {data['agent']}: {data['message'][:50]}...")
        
    @sio.event
    async def conversation_complete(data):
        print(f"✅ Conversation complete in {data['duration']}s")
        
    try:
        # Connect to the server
        print("🔌 Connecting to http://localhost:8001...")
        await sio.connect('http://localhost:8001')
        
        # Test starting a conversation
        print("📨 Starting conversation...")
        await sio.emit('start_conversation', {
            'query': 'How should we launch our new robo-advisor?',
            'test_mode': True
        })
        
        # Wait for the conversation to complete
        await asyncio.sleep(35)  # Wait for conversation to finish
        
        # Disconnect
        await sio.disconnect()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n⚠️  Make sure the backend is running:")
        print("   cd backend && python main_simple.py")

if __name__ == "__main__":
    asyncio.run(test_socketio_connection())