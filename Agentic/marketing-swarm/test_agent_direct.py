#!/usr/bin/env python3
"""
Test agent responses directly to verify dynamic conversation system
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from main_simple import SimpleAgentManager

async def test_agents():
    """Test agent responses with dynamic personalities"""
    agent_manager = SimpleAgentManager()
    
    print("🎭 Testing Dynamic Agent Personalities")
    print("=" * 50)
    
    query = "How should we launch our new robo-advisor to compete with Betterment?"
    print(f"Query: {query}\n")
    
    # Test each agent with personality-driven responses
    agents = ["sarah", "marcus", "elena", "david", "priya", "alex"]
    conversation_history = []
    
    for i, agent_id in enumerate(agents):
        agent_data = agent_manager.agents[agent_id]
        
        print(f"👤 {agent_id.upper()} ({agent_data['role']})")
        print(f"   Personality: {agent_data['personality']}")
        print(f"   Assert: {agent_data['assertiveness']}, Contrary: {agent_data['contrarianism']}, Creative: {agent_data['creativity']}")
        
        # Get response with conversation context
        response = await agent_manager.get_agent_response(
            agent_id, query, {}, conversation_history
        )
        
        print(f"   💬 {response}")
        
        # Add to conversation history for context
        conversation_history.append({
            'agent': agent_id,
            'message': response,
            'timestamp': '2025-06-17T22:35:00.000Z'
        })
        
        print()
    
    print("🔗 Testing Agent Interactions & Reactions")
    print("=" * 50)
    
    # Test reactive responses
    test_scenarios = [
        {
            'context': "Marcus just said: 'The data shows premium is dead'",
            'expected_reactor': 'sarah',
            'trigger_words': ['data', 'premium']
        },
        {
            'context': "Sarah mentioned: 'We need emotional trust'", 
            'expected_reactor': 'marcus',
            'trigger_words': ['trust', 'emotional']
        }
    ]
    
    for scenario in test_scenarios:
        print(f"Scenario: {scenario['context']}")
        
        # Create fake previous response to trigger reaction
        fake_response = {
            'agent': 'test',
            'message': scenario['context'],
            'timestamp': '2025-06-17T22:35:00.000Z'
        }
        
        # Test if expected agent reacts
        reaction = agent_manager.get_reaction_response(
            scenario['expected_reactor'], 
            fake_response, 
            query
        )
        
        if reaction:
            print(f"   🔥 {scenario['expected_reactor'].upper()} reacts: {reaction}")
        else:
            print(f"   😐 No reaction from {scenario['expected_reactor']}")
        print()
    
    print("✅ Agent Testing Complete!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_agents())