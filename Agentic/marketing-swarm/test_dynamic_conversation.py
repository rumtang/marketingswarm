#!/usr/bin/env python3
"""
Test the dynamic conversation system with real-time WebSocket monitoring
"""

import asyncio
import json
import time
from datetime import datetime
import socketio

# Connect to the backend
sio = socketio.AsyncClient(logger=False)

conversation_data = []
conversation_complete = False

@sio.event
async def connect():
    print("🔗 Connected to dynamic conversation system")
    
@sio.event 
async def conversation_started(data):
    print("🚀 Dynamic Marketing Team Discussion Started")
    print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
    conversation_data.clear()

@sio.event
async def agent_response(data):
    agent = data['agent']
    message = data['message']
    thinking_time = data.get('thinking_time', 0)
    interruption = data.get('interruption', False)
    timestamp = data.get('timestamp', datetime.now().isoformat())
    
    conversation_data.append(data)
    
    # Show agent personality traits
    personality_traits = {
        'sarah': 'Visionary idealist (Assert:0.8, Contrary:0.4, Creative:0.7)',
        'marcus': 'Aggressive data evangelist (Assert:0.9, Contrary:0.8, Creative:0.3)', 
        'elena': 'Creative rebel (Assert:0.7, Contrary:0.7, Creative:0.9)',
        'david': 'User zealot (Assert:0.6, Contrary:0.6, Creative:0.5)',
        'priya': 'Skeptical scientist (Assert:0.7, Contrary:0.9, Creative:0.2)',
        'alex': 'Risk-taking experimenter (Assert:0.8, Contrary:0.5, Creative:1.0)'
    }
    
    interrupt_indicator = " 🔥[INTERRUPTION]" if interruption else ""
    
    print(f"\n👤 {agent.upper()}{interrupt_indicator}")
    print(f"   Role: {personality_traits.get(agent, 'Unknown')}")
    print(f"   Thinking: {thinking_time:.1f}s")
    print(f"   💬 {message}")
    
@sio.event
async def conversation_complete(data):
    global conversation_complete
    conversation_complete = True
    
    print(f"\n✅ Conversation Complete!")
    print(f"   Total responses: {data.get('total_responses', 0)}")
    print(f"   Duration: {data.get('duration', 0):.1f}s")
    print(f"   Agents participated: {data.get('agents_participated', 0)}/6")
    
    # Show relationship insights
    insights = data.get('relationship_insights', {})
    if insights:
        print(f"\n🔗 Relationship Dynamics:")
        if insights.get('strongest_alliances'):
            print(f"   Alliances: {insights['strongest_alliances']}")
        if insights.get('biggest_conflicts'):
            print(f"   Conflicts: {insights['biggest_conflicts']}")
        if insights.get('respect_dynamics'):
            print(f"   Respect: {insights['respect_dynamics']}")

async def test_dynamic_conversation():
    """Test the dynamic conversation system"""
    try:
        # Connect to backend
        await sio.connect('http://localhost:8001')
        
        print("🎭 Testing Dynamic Swarm Intelligence Conversation System")
        print("=" * 60)
        
        # Test scenario: Robo-advisor launch
        query = "How should we launch our new robo-advisor to compete with Betterment?"
        print(f"📝 Query: {query}")
        print("=" * 60)
        
        # Start the conversation
        await sio.emit('start_conversation', {
            'query': query,
            'test_mode': True
        })
        
        # Wait for conversation to complete
        timeout = 120  # 2 minutes max
        start_time = time.time()
        
        while not conversation_complete and (time.time() - start_time) < timeout:
            await asyncio.sleep(0.5)
            
        if not conversation_complete:
            print("\n⚠️ Conversation timed out")
        
        # Wait a moment for final messages
        await asyncio.sleep(2)
        
        print("\n" + "=" * 60)
        print("🎯 Dynamic Conversation Analysis:")
        
        # Analyze conversation dynamics
        interruptions = sum(1 for r in conversation_data if r.get('interruption', False))
        total_responses = len(conversation_data)
        
        # Count agent participation
        agent_counts = {}
        for response in conversation_data:
            agent = response['agent']
            agent_counts[agent] = agent_counts.get(agent, 0) + 1
            
        avg_thinking_time = sum(r.get('thinking_time', 0) for r in conversation_data) / len(conversation_data) if conversation_data else 0
        
        print(f"   📊 Total responses: {total_responses}")
        print(f"   🔥 Interruptions: {interruptions}")
        print(f"   ⏱️  Average thinking time: {avg_thinking_time:.1f}s")
        print(f"   👥 Agent distribution: {agent_counts}")
        
        # Show examples of dynamic interactions
        print(f"\n🎭 Dynamic Interactions Detected:")
        for i, response in enumerate(conversation_data):
            if response.get('interruption'):
                print(f"   🔥 Interruption #{i+1}: {response['agent']} - {response['message'][:80]}...")
            elif any(word in response['message'].lower() for word in ['disagree', 'wrong', 'stop']):
                print(f"   ⚔️  Conflict #{i+1}: {response['agent']} - {response['message'][:80]}...")
                
        print(f"\n✅ Dynamic Swarm Intelligence Test Complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        await sio.disconnect()

if __name__ == "__main__":
    asyncio.run(test_dynamic_conversation())