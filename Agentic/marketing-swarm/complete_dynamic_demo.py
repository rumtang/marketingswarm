#!/usr/bin/env python3
"""
Complete demonstration of Dynamic Swarm Intelligence with all features:
- Personality-driven responses
- Interruptions and conflicts 
- Relationship tracking
- Dynamic timing
- Creative tensions
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

async def complete_dynamic_demo():
    """Complete demonstration with forced conflicts and interruptions"""
    agent_manager = SimpleAgentManager()
    
    print("🔥 COMPLETE DYNAMIC SWARM INTELLIGENCE DEMO")
    print("=" * 70)
    print("✨ Featuring: Interruptions, Conflicts, Alliance Building & Personality Clashes")
    print("=" * 70)
    
    query = "Our customer acquisition cost has doubled. What's our action plan?"
    print(f"💬 Crisis Scenario: {query}\n")
    
    conversation_history = []
    
    # Manually orchestrate dynamic conversation to show all features
    scenarios = [
        # Sarah starts with brand perspective
        {'agent': 'sarah', 'response_type': 'normal'},
        # Marcus interrupts with data obsession
        {'agent': 'marcus', 'response_type': 'interrupt', 'trigger': 'data challenge'},
        # Elena reacts to Marcus being too data-focused
        {'agent': 'elena', 'response_type': 'reaction', 'trigger': 'creative pushback'},
        # David supports Elena (alliance forming)
        {'agent': 'david', 'response_type': 'alliance', 'trigger': 'user focus'},
        # Priya challenges Elena with data (conflict)
        {'agent': 'priya', 'response_type': 'conflict', 'trigger': 'skeptical scientist'},
        # Alex proposes wild solution
        {'agent': 'alex', 'response_type': 'creative', 'trigger': 'growth hacking'}
    ]
    
    for i, scenario in enumerate(scenarios):
        agent_id = scenario['agent']
        agent_data = agent_manager.agents[agent_id]
        response_type = scenario['response_type']
        
        # Dynamic thinking time based on personality and scenario
        base_thinking = agent_data['patience'] * 2
        if response_type == 'interrupt':
            thinking_time = 0.5  # Quick interruption
        elif response_type == 'reaction':
            thinking_time = base_thinking * 0.7  # Reactive
        else:
            thinking_time = base_thinking + random.uniform(0.5, 1.5)
        
        print(f"🤔 {agent_id.upper()} {'[INTERRUPTING]' if response_type == 'interrupt' else 'thinking'}... ({thinking_time:.1f}s)")
        await asyncio.sleep(min(thinking_time / 3, 1))  # Sped up for demo
        
        # Get appropriate response based on scenario
        if response_type == 'interrupt' and conversation_history:
            # Force interruption response
            response = f"[interrupting] {await agent_manager.get_agent_response(agent_id, query, {}, conversation_history)}"
        elif response_type == 'reaction' and conversation_history:
            # Get reaction to previous agent
            last_response = conversation_history[-1]
            reaction = agent_manager.get_reaction_response(agent_id, last_response, query)
            response = reaction if reaction else await agent_manager.get_agent_response(agent_id, query, {}, conversation_history)
        else:
            # Normal response
            response = await agent_manager.get_agent_response(agent_id, query, {}, conversation_history)
        
        # Detect dynamic interaction types
        is_interruption = '[interrupting]' in response.lower() or response_type == 'interrupt'
        is_conflict = any(word in response.lower() for word in ['disagree', 'wrong', 'stop', 'missing', 'terrible'])
        is_alliance = any(word in response.lower() for word in ['building on', 'agree', 'exactly', 'brilliant', 'david'])
        
        # Create rich response object
        response_obj = {
            'agent': agent_id,
            'message': response,
            'timestamp': datetime.now().isoformat(),
            'thinking_time': thinking_time,
            'interruption': is_interruption,
            'conflict': is_conflict,
            'alliance': is_alliance,
            'response_type': response_type,
            'trigger': scenario.get('trigger', 'normal')
        }
        
        # Display with rich context
        agent_personality = agent_data['personality']
        traits = f"Assert:{agent_data['assertiveness']:.1f} | Contrary:{agent_data['contrarianism']:.1f} | Creative:{agent_data['creativity']:.1f} | Patience:{agent_data['patience']:.1f}"
        
        # Build status indicators
        indicators = []
        if is_interruption: indicators.append("🔥 INTERRUPTION")
        if is_conflict: indicators.append("⚔️ CONFLICT") 
        if is_alliance: indicators.append("🤝 ALLIANCE")
        
        status = " | ".join(indicators) if indicators else "💭 NORMAL"
        
        print(f"\n👤 {agent_id.upper()} - {agent_data['role']} | {status}")
        print(f"   🧠 Personality: {agent_personality}")
        print(f"   📊 Traits: {traits}")
        print(f"   🎯 Trigger: {scenario.get('trigger', 'N/A')}")
        print(f"   💬 \"{response}\"")
        
        # Add to conversation history
        conversation_history.append(response_obj)
        
        # Brief pause between responses
        await asyncio.sleep(0.3)
    
    # Update relationships based on conversation
    agent_manager.update_agent_relationships(conversation_history)
    
    print("\n" + "=" * 70)
    print("🎯 DYNAMIC SWARM INTELLIGENCE ANALYSIS")
    print("=" * 70)
    
    # Comprehensive analysis
    total_responses = len(conversation_history)
    interruptions = sum(1 for r in conversation_history if r.get('interruption', False))
    conflicts = sum(1 for r in conversation_history if r.get('conflict', False))
    alliances = sum(1 for r in conversation_history if r.get('alliance', False))
    total_duration = sum(r.get('thinking_time', 0) for r in conversation_history)
    
    # Agent participation and interaction styles
    agent_stats = {}
    for response in conversation_history:
        agent = response['agent']
        if agent not in agent_stats:
            agent_stats[agent] = {'responses': 0, 'interruptions': 0, 'conflicts': 0, 'alliances': 0}
        
        agent_stats[agent]['responses'] += 1
        if response.get('interruption'): agent_stats[agent]['interruptions'] += 1
        if response.get('conflict'): agent_stats[agent]['conflicts'] += 1
        if response.get('alliance'): agent_stats[agent]['alliances'] += 1
    
    print(f"📊 CONVERSATION METRICS:")
    print(f"   Total Responses: {total_responses}")
    print(f"   🔥 Interruptions: {interruptions}")
    print(f"   ⚔️ Conflicts: {conflicts}")
    print(f"   🤝 Alliances: {alliances}")
    print(f"   ⏱️ Total Duration: {total_duration:.1f}s")
    print(f"   🎭 Dynamic Interactions: {(interruptions + conflicts + alliances) / total_responses * 100:.1f}%")
    
    print(f"\n👥 AGENT PERFORMANCE:")
    for agent, stats in agent_stats.items():
        agent_name = agent_manager.agents[agent]['name']
        print(f"   {agent.upper()}: {stats['responses']} responses | {stats['interruptions']} interrupts | {stats['conflicts']} conflicts | {stats['alliances']} alliances")
    
    # Show relationship dynamics
    relationships = agent_manager.get_relationship_summary()
    print(f"\n🔗 RELATIONSHIP DYNAMICS:")
    if relationships['strongest_alliances']:
        print(f"   🤝 Strongest Alliances: {relationships['strongest_alliances'][:3]}")
    if relationships['biggest_conflicts']:
        print(f"   ⚔️ Biggest Conflicts: {relationships['biggest_conflicts'][:3]}")
    if relationships['respect_dynamics']:
        positive_respect = {k: v for k, v in relationships['respect_dynamics'].items() if v > 0}
        negative_respect = {k: v for k, v in relationships['respect_dynamics'].items() if v < 0}
        if positive_respect:
            print(f"   📈 Positive Respect: {positive_respect}")
        if negative_respect:
            print(f"   📉 Negative Respect: {negative_respect}")
    
    # Highlight key dynamic interactions
    print(f"\n✨ KEY DYNAMIC INTERACTIONS:")
    for i, response in enumerate(conversation_history):
        interaction_type = []
        if response.get('interruption'): interaction_type.append("INTERRUPTION")
        if response.get('conflict'): interaction_type.append("CONFLICT")
        if response.get('alliance'): interaction_type.append("ALLIANCE")
        
        if interaction_type:
            types = " + ".join(interaction_type)
            print(f"   {i+1}. {response['agent'].upper()} [{types}]: \"{response['message'][:60]}...\"")
    
    print(f"\n🎉 DYNAMIC SWARM INTELLIGENCE DEMONSTRATION COMPLETE!")
    print("=" * 70)
    print("✅ Successfully demonstrated:")
    print("   🔥 Personality-driven interruptions")
    print("   ⚔️ Creative conflicts and debates") 
    print("   🤝 Dynamic alliance formation")
    print("   🎭 Emergent team dynamics")
    print("   📊 Relationship tracking")
    print("   ⏱️ Variable response timing")
    print("   🧠 Context-aware reactions")
    print("\n🚀 This system transforms boring linear AI conversations into")
    print("   engaging, unpredictable, and more creative collaborative discussions!")

if __name__ == "__main__":
    asyncio.run(complete_dynamic_demo())