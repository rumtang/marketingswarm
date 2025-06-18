#!/usr/bin/env python3
"""
Demonstrate the complete dynamic conversation system
"""

import sys
import os
import asyncio
import random
import time
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from main_simple import SimpleAgentManager

async def simulate_dynamic_conversation():
    """Simulate a complete dynamic conversation with timing and interruptions"""
    agent_manager = SimpleAgentManager()
    
    print("🎭 DYNAMIC SWARM INTELLIGENCE DEMONSTRATION")
    print("=" * 60)
    print("🚀 Marketing Team Discussion: Robo-Advisor Launch Strategy")
    print("=" * 60)
    
    query = "How should we launch our new robo-advisor to compete with Betterment?"
    conversation_history = []
    all_agents = ["sarah", "marcus", "elena", "david", "priya", "alex"]
    agents_spoken = set()
    max_exchanges = 12
    exchange_count = 0
    
    current_agent = "sarah"  # Start with strategy
    
    print(f"💬 User Question: {query}\n")
    
    while exchange_count < max_exchanges and len(agents_spoken) < 6:
        agent_data = agent_manager.agents[current_agent]
        
        # Dynamic thinking time based on personality
        thinking_time = agent_data['patience'] * 3 + random.uniform(0.5, 2.0)
        
        print(f"🤔 {current_agent.upper()} thinking... ({thinking_time:.1f}s)")
        await asyncio.sleep(min(thinking_time / 2, 2))  # Simulate thinking (sped up for demo)
        
        # Get response with conversation context
        response = await agent_manager.get_agent_response(
            current_agent, query, {}, conversation_history
        )
        
        # Check if this is an interruption or reaction
        is_interruption = '[interrupting]' in response or '[talking over]' in response
        is_reaction = any(word in response.lower() for word in ['disagree', 'wrong', 'stop', 'missing'])
        
        # Create response object
        response_obj = {
            'agent': current_agent,
            'message': response,
            'timestamp': datetime.now().isoformat(),
            'thinking_time': thinking_time,
            'interruption': is_interruption,
            'reaction': is_reaction
        }
        
        # Display the response with personality context
        agent_personality = agent_data['personality']
        traits = f"Assert:{agent_data['assertiveness']:.1f} | Contrary:{agent_data['contrarianism']:.1f} | Creative:{agent_data['creativity']:.1f}"
        
        interrupt_flag = "🔥 [INTERRUPTING] " if is_interruption else ""
        reaction_flag = "⚔️ [REACTING] " if is_reaction and not is_interruption else ""
        
        print(f"\n👤 {interrupt_flag}{reaction_flag}{current_agent.upper()} - {agent_data['role']}")
        print(f"   💭 Personality: {agent_personality}")
        print(f"   📊 Traits: {traits}")
        print(f"   💬 \"{response}\"")
        
        # Add to conversation history
        conversation_history.append(response_obj)
        agents_spoken.add(current_agent)
        
        # Determine next agent based on conversation dynamics
        next_agent = get_next_agent_demo(current_agent, conversation_history, all_agents, agents_spoken, agent_manager)
        current_agent = next_agent
        
        exchange_count += 1
        
        # Add brief pause between responses
        await asyncio.sleep(0.5)
        
        # Occasionally jump to different agent (30% chance)
        if random.random() < 0.3:
            available_agents = [a for a in all_agents if a != current_agent]
            current_agent = random.choice(available_agents)
    
    # Ensure remaining agents get to speak
    remaining_agents = [a for a in all_agents if a not in agents_spoken]
    for agent_id in remaining_agents[:2]:
        agent_data = agent_manager.agents[agent_id]
        thinking_time = agent_data['patience'] * 2 + random.uniform(0.5, 1.5)
        
        print(f"\n🤔 {agent_id.upper()} adding final thoughts... ({thinking_time:.1f}s)")
        await asyncio.sleep(min(thinking_time / 2, 1))
        
        response = await agent_manager.get_agent_response(
            agent_id, query, {}, conversation_history
        )
        
        response_obj = {
            'agent': agent_id,
            'message': response,
            'timestamp': datetime.now().isoformat(),
            'thinking_time': thinking_time
        }
        
        agent_personality = agent_data['personality']
        traits = f"Assert:{agent_data['assertiveness']:.1f} | Contrary:{agent_data['contrarianism']:.1f} | Creative:{agent_data['creativity']:.1f}"
        
        print(f"\n👤 {agent_id.upper()} - {agent_data['role']}")
        print(f"   💭 Personality: {agent_personality}")
        print(f"   📊 Traits: {traits}")
        print(f"   💬 \"{response}\"")
        
        conversation_history.append(response_obj)
    
    # Update relationships and show results
    agent_manager.update_agent_relationships(conversation_history)
    
    print("\n" + "=" * 60)
    print("🎯 DYNAMIC CONVERSATION ANALYSIS")
    print("=" * 60)
    
    # Conversation statistics
    total_responses = len(conversation_history)
    interruptions = sum(1 for r in conversation_history if r.get('interruption', False))
    reactions = sum(1 for r in conversation_history if r.get('reaction', False))
    total_duration = sum(r.get('thinking_time', 2) for r in conversation_history)
    
    # Agent participation
    agent_counts = {}
    for response in conversation_history:
        agent = response['agent']
        agent_counts[agent] = agent_counts.get(agent, 0) + 1
    
    print(f"📊 Total Responses: {total_responses}")
    print(f"🔥 Interruptions: {interruptions}")
    print(f"⚔️ Reactions/Conflicts: {reactions}")
    print(f"⏱️ Total Duration: {total_duration:.1f}s")
    print(f"👥 Agents Participated: {len(agents_spoken)}/6")
    print(f"📈 Response Distribution: {agent_counts}")
    
    # Show relationship dynamics
    relationships = agent_manager.get_relationship_summary()
    print(f"\n🔗 RELATIONSHIP DYNAMICS:")
    if relationships['strongest_alliances']:
        print(f"🤝 Strongest Alliances: {relationships['strongest_alliances'][:2]}")
    if relationships['biggest_conflicts']:
        print(f"⚔️ Biggest Conflicts: {relationships['biggest_conflicts'][:2]}")
    if relationships['respect_dynamics']:
        print(f"🎭 Respect Dynamics: {relationships['respect_dynamics']}")
    
    # Show dynamic interaction examples
    print(f"\n✨ DYNAMIC INTERACTIONS DETECTED:")
    for i, response in enumerate(conversation_history):
        if response.get('interruption'):
            print(f"🔥 Interruption #{i+1}: {response['agent']} - \"{response['message'][:80]}...\"")
        elif response.get('reaction'):
            print(f"⚔️ Conflict #{i+1}: {response['agent']} - \"{response['message'][:80]}...\"")
    
    print(f"\n🎉 Dynamic Swarm Intelligence Demonstration Complete!")
    print("This showcases how AI agents can collaborate with creative tension,")
    print("interruptions, and personality-driven conflicts to generate better solutions!")

def get_next_agent_demo(current_agent: str, conversation_history, all_agents, agents_spoken, agent_manager):
    """Determine next agent based on conversation dynamics"""
    import random
    
    current_agent_data = agent_manager.agents[current_agent]
    last_message = conversation_history[-1]['message'] if conversation_history else ""
    
    # High-assertiveness agents trigger contrarian responses
    if current_agent_data['assertiveness'] > 0.8:
        contrarian_agents = [a for a in all_agents 
                           if agent_manager.agents[a]['contrarianism'] > 0.7 and a != current_agent]
        if contrarian_agents and random.random() < 0.6:
            return random.choice(contrarian_agents)
    
    # Keyword triggers for domain experts
    keyword_triggers = {
        ('data', 'metric', 'analytics'): 'priya',
        ('user', 'experience', 'ux'): 'david', 
        ('creative', 'content', 'story'): 'elena',
        ('growth', 'viral', 'scale'): 'alex',
        ('brand', 'positioning', 'strategy'): 'sarah',
        ('campaign', 'advertising', 'paid'): 'marcus'
    }
    
    for keywords, expert_agent in keyword_triggers.items():
        if any(keyword in last_message.lower() for keyword in keywords):
            if expert_agent in all_agents and random.random() < 0.4:
                return expert_agent
    
    # Prefer unspoken agents
    unspoken_agents = [a for a in all_agents if a not in agents_spoken and a != current_agent]
    if unspoken_agents:
        return max(unspoken_agents, key=lambda a: agent_manager.agents[a]['assertiveness'])
    
    # Random selection weighted by assertiveness
    available_agents = [a for a in all_agents if a != current_agent]
    weights = [agent_manager.agents[a]['assertiveness'] for a in available_agents]
    return random.choices(available_agents, weights=weights)[0]

if __name__ == "__main__":
    asyncio.run(simulate_dynamic_conversation())