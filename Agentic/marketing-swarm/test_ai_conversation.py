#!/usr/bin/env python3
"""
Test AI-powered conversation via WebSocket
"""

import asyncio
import json
import socketio
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Socket.IO client
sio = socketio.AsyncClient()

# Track conversation
conversation_data = {
    'connected': False,
    'conversation_id': None,
    'responses': [],
    'start_time': None,
    'end_time': None
}

@sio.event
async def connect():
    print("✅ Connected to server")
    conversation_data['connected'] = True

@sio.event
async def disconnect():
    print("❌ Disconnected from server")
    conversation_data['connected'] = False

@sio.event
async def connection_established(data):
    print(f"🔗 Connection established: {data}")

@sio.event
async def conversation_started(data):
    print(f"🎬 Conversation started: {data}")
    conversation_data['conversation_id'] = data.get('conversation_id')
    conversation_data['start_time'] = datetime.now()

@sio.event
async def agent_response(data):
    agent = data.get('agent', 'unknown')
    message = data.get('message', '')
    is_interruption = data.get('interruption', False)
    
    conversation_data['responses'].append(data)
    
    interrupt_flag = "🔥 [INTERRUPTING] " if is_interruption else ""
    print(f"\n{interrupt_flag}👤 {agent.upper()}")
    print(f"💬 {message[:200]}{'...' if len(message) > 200 else ''}")

@sio.event
async def conversation_phase(data):
    print(f"\n📊 Phase: {data.get('phase')} - {data.get('goal')}")

@sio.event
async def conversation_complete(data):
    print(f"\n✅ Conversation complete!")
    print(f"📋 Total responses: {data.get('total_responses')}")
    print(f"👥 Agents participated: {data.get('agents_participated')}")
    
    # Check if we have a briefing document
    if 'briefing_document' in data:
        print("\n📄 Briefing Document Generated!")
        briefing = data['briefing_document']
        print(f"Title: {briefing.get('title')}")
        print(f"Executive Summary: {briefing.get('executive_summary', '')[:200]}...")
    
    conversation_data['end_time'] = datetime.now()

@sio.event
async def error(data):
    print(f"❌ Error: {data}")

@sio.event
async def conversation_error(data):
    print(f"❌ Conversation Error: {data}")

async def test_ai_conversation():
    """Test AI-powered conversation"""
    
    print("🤖 AI CONVERSATION TEST")
    print("=" * 60)
    
    try:
        # Connect to server
        print("🔌 Connecting to WebSocket server...")
        await sio.connect('http://localhost:8001')
        
        # Wait for connection
        await asyncio.sleep(1)
        
        if not conversation_data['connected']:
            print("❌ Failed to connect to server")
            return
        
        # Test queries
        test_queries = [
            "How should we launch our new robo-advisor to compete with Betterment?",
            "What's the best strategy to reduce our customer acquisition cost?",
            "Should we focus on brand building or performance marketing?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'='*60}")
            print(f"📝 Test {i}: {query}")
            print(f"{'='*60}")
            
            # Start conversation
            await sio.emit('start_conversation', {
                'query': query,
                'test_mode': False
            })
            
            # Wait for conversation to complete (max 30 seconds)
            wait_time = 0
            while wait_time < 30:
                await asyncio.sleep(1)
                wait_time += 1
                
                if conversation_data['end_time']:
                    break
            
            # Analyze results
            print(f"\n📊 ANALYSIS:")
            print(f"- Responses received: {len(conversation_data['responses'])}")
            print(f"- Unique agents: {len(set(r['agent'] for r in conversation_data['responses']))}")
            print(f"- Has interruptions: {any(r.get('interruption') for r in conversation_data['responses'])}")
            print(f"- Duration: {(conversation_data['end_time'] - conversation_data['start_time']).total_seconds():.1f}s")
            
            # Check AI quality
            ai_indicators = []
            for response in conversation_data['responses']:
                msg = response.get('message', '')
                # Look for AI indicators (varied language, specific details)
                if any(word in msg for word in ['specifically', 'particularly', 'framework', 'leverage', 'strategic']):
                    ai_indicators.append(response['agent'])
            
            print(f"- AI quality indicators found in: {len(set(ai_indicators))} agents")
            
            # Reset for next test
            conversation_data['responses'] = []
            conversation_data['end_time'] = None
            
            # Wait between tests
            if i < len(test_queries):
                await asyncio.sleep(2)
        
        # Disconnect
        await sio.disconnect()
        
        print(f"\n{'='*60}")
        print("✅ AI CONVERSATION TEST COMPLETE")
        print("🎯 AI is working if:")
        print("  - Each test had 6+ responses")
        print("  - Responses varied between tests")
        print("  - Language was sophisticated and contextual")
        print("  - Interruptions and reactions occurred")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ai_conversation())