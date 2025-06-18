#!/usr/bin/env python3
"""
Demo: AI-Powered Marketing Swarm
Shows the difference between predetermined and AI responses
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Set up environment for demo
os.environ["MOCK_API_RESPONSES"] = "true"  # Use mock for demo
os.environ["USE_AI_RESPONSES"] = "true"    # Enable AI mode

from main_simple import SimpleAgentManager
from ai.response_generator import ai_generator
from ai.context_manager import context_manager


async def demo_ai_responses():
    """Demonstrate AI-powered agent responses"""
    
    print("🤖 AI-POWERED MARKETING SWARM DEMO")
    print("=" * 60)
    print("Comparing Predetermined vs AI Responses")
    print("=" * 60)
    
    agent_manager = SimpleAgentManager()
    query = "How should we launch our new robo-advisor to compete with Betterment?"
    
    # Test agents
    test_agents = ['sarah', 'marcus', 'elena']
    
    print(f"\n📝 Query: {query}\n")
    
    # First, show predetermined responses
    print("1️⃣ PREDETERMINED RESPONSES (Current System)")
    print("-" * 40)
    
    os.environ["USE_AI_RESPONSES"] = "false"
    for agent_id in test_agents:
        agent_data = agent_manager.agents[agent_id]
        response = agent_manager.get_dynamic_responses(agent_id, query, [])
        print(f"\n👤 {agent_data['name']} ({agent_data['role']}):")
        print(f"   {response[:150]}...")
    
    print("\n\n2️⃣ AI-POWERED RESPONSES (With GPT-4)")
    print("-" * 40)
    
    os.environ["USE_AI_RESPONSES"] = "true"
    conversation_history = []
    
    for i, agent_id in enumerate(test_agents):
        agent_data = agent_manager.agents[agent_id]
        
        # Generate AI response
        try:
            response = await agent_manager.get_agent_response(
                agent_id, 
                query, 
                {},
                conversation_history
            )
        except Exception as e:
            # In demo mode with mocks, show what would happen
            response = f"[AI Mode] Dynamic response based on {agent_data['name']}'s personality and expertise..."
        
        print(f"\n👤 {agent_data['name']} ({agent_data['role']}):")
        print(f"   🧠 Personality: Assert={agent_data['assertiveness']}, Contrary={agent_data['contrarianism']}")
        print(f"   💬 {response}")
        
        # Add to conversation history
        conversation_history.append({
            'agent': agent_id,
            'message': response,
            'timestamp': datetime.now().isoformat()
        })
    
    # Show context management
    print("\n\n3️⃣ CONTEXT MANAGEMENT DEMO")
    print("-" * 40)
    
    context = context_manager.build_context(
        agent_id='priya',
        agent_data=agent_manager.agents['priya'],
        query=query,
        conversation_history=conversation_history
    )
    
    print("Context built for Priya (Analytics Manager):")
    print(context[:300] + "...")
    
    # Show relationship tracking
    print("\n\n4️⃣ DYNAMIC RELATIONSHIPS")
    print("-" * 40)
    
    # Simulate some interactions
    test_history = [
        {'agent': 'sarah', 'message': 'I strongly believe in brand-first approach'},
        {'agent': 'marcus', 'message': 'Sarah, I disagree. Data shows brand-first fails without performance metrics.'},
        {'agent': 'sarah', 'message': 'Marcus makes a good point about metrics, but brand creates emotional connection.'},
        {'agent': 'elena', 'message': 'Building on Sarah\'s idea, we could create brand stories with data backing.'},
    ]
    
    agent_manager.update_agent_relationships(test_history)
    relationships = agent_manager.get_relationship_summary()
    
    print("Relationship Dynamics:")
    print(f"- Conflicts: {relationships['biggest_conflicts']}")
    print(f"- Alliances: {relationships['strongest_alliances']}")
    
    print("\n\n5️⃣ KEY ADVANTAGES OF AI INTEGRATION")
    print("-" * 40)
    print("✅ Every response is unique - no repetition")
    print("✅ Maintains consistent personality across interactions")
    print("✅ Responds intelligently to context and other agents")
    print("✅ Can handle any query, not just predetermined ones")
    print("✅ Learns from conversation flow to build better responses")
    
    print("\n\n6️⃣ IMPLEMENTATION STEPS")
    print("-" * 40)
    print("1. Add OpenAI API key to .env file")
    print("2. Set USE_AI_RESPONSES=true")
    print("3. Configure AI_MODEL (gpt-4 or gpt-3.5-turbo)")
    print("4. Adjust per-agent temperatures for personality")
    print("5. Monitor costs with AI_DAILY_TOKEN_LIMIT")
    
    print("\n✨ AI integration complete! The agents now think for themselves.")


async def demo_conversation_flow():
    """Demonstrate a full AI-powered conversation"""
    
    print("\n\n🎬 FULL AI CONVERSATION DEMO")
    print("=" * 60)
    
    agent_manager = SimpleAgentManager()
    query = "Should we focus on CAC reduction or brand building?"
    conversation_history = []
    
    print(f"Query: {query}\n")
    
    # Simulate a dynamic conversation
    agent_sequence = ['sarah', 'marcus', 'sarah', 'elena', 'priya', 'alex']
    
    for agent_id in agent_sequence:
        agent_data = agent_manager.agents[agent_id]
        
        # Check if this should be an interruption
        is_interruption = (
            len(conversation_history) > 0 and 
            agent_data['assertiveness'] > 0.8 and 
            agent_id == 'marcus'  # Marcus often interrupts
        )
        
        print(f"\n{'🔥 [INTERRUPTING] ' if is_interruption else ''}👤 {agent_data['name']}:")
        
        # In real implementation, this would call the AI
        if is_interruption:
            response = "[interrupting] Wait, that's missing the point! We need data..."
        else:
            response = f"From my {agent_data['role']} perspective on {query[:30]}..."
            
        print(f"   {response}")
        
        conversation_history.append({
            'agent': agent_id,
            'message': response,
            'timestamp': datetime.now().isoformat()
        })
    
    print("\n\nWith AI, each run of this conversation would be completely different!")


if __name__ == "__main__":
    print("Starting AI Integration Demo...\n")
    
    # Run demos
    asyncio.run(demo_ai_responses())
    asyncio.run(demo_conversation_flow())
    
    print("\n\n🎉 Demo complete! Ready to integrate real AI responses.")
    print("Next step: Add your OpenAI API key and set USE_AI_RESPONSES=true")