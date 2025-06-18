#!/usr/bin/env python3
"""
Demo script for Marketing Swarm
Shows how the multi-agent system works together
"""

import asyncio
import os
import sys
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Use test configuration
os.environ["MOCK_API_RESPONSES"] = "true"
os.environ["DEV_MODE"] = "true"

from agents.sarah_brand import SarahBrandAgent
from agents.marcus_campaigns import MarcusCampaignsAgent
from agents.elena_content import ElenaContentAgent
from agents.david_experience import DavidExperienceAgent
from agents.priya_analytics import PriyaAnalyticsAgent
from agents.alex_growth import AlexGrowthAgent

class MarketingSwarmDemo:
    """Demo the marketing swarm in action"""
    
    def __init__(self):
        self.agents = {
            "sarah": SarahBrandAgent(),
            "marcus": MarcusCampaignsAgent(),
            "elena": ElenaContentAgent(),
            "david": DavidExperienceAgent(),
            "priya": PriyaAnalyticsAgent(),
            "alex": AlexGrowthAgent()
        }
        
    async def simulate_conversation(self, user_query: str):
        """Simulate a multi-agent conversation"""
        print(f"\n{'='*60}")
        print(f"USER QUERY: {user_query}")
        print(f"{'='*60}\n")
        
        # Context that builds throughout conversation
        context = {
            "user_query": user_query,
            "timestamp": datetime.now().isoformat(),
            "insights": [],
            "recommendations": []
        }
        
        # Phase 1: Analysis (all agents analyze the query)
        print("📊 PHASE 1: ANALYSIS")
        print("-" * 40)
        
        for agent_name, agent in self.agents.items():
            print(f"\n🤖 {agent_name.upper()} is analyzing...")
            await asyncio.sleep(1)  # Simulate thinking time
            
            analysis = await agent.analyze_with_current_data(user_query, context)
            context["insights"].append({
                "agent": agent_name,
                "analysis": analysis
            })
            print(f"💡 {agent_name}: {analysis[:150]}...")
        
        # Phase 2: Collaboration (agents build on each other's ideas)
        print(f"\n\n🤝 PHASE 2: COLLABORATION")
        print("-" * 40)
        
        # Simulate natural conversation flow
        collaboration_order = [
            ("sarah", "marcus"),  # Brand strategy informs campaigns
            ("marcus", "elena"),  # Campaigns need content
            ("elena", "david"),   # Content impacts experience
            ("david", "priya"),   # Experience generates analytics
            ("priya", "alex")     # Analytics drives growth
        ]
        
        for speaker, responder in collaboration_order:
            print(f"\n💬 {speaker.upper()} → {responder.upper()}")
            await asyncio.sleep(1.5)
            
            response = await self.agents[responder].collaborate(context)
            context["insights"].append({
                "agent": responder,
                "collaboration": response
            })
            print(f"   {responder}: {response[:150]}...")
        
        # Phase 3: Synthesis (create actionable recommendations)
        print(f"\n\n🎯 PHASE 3: SYNTHESIS")
        print("-" * 40)
        
        synthesis_agents = ["sarah", "priya", "alex"]  # Key decision makers
        
        for agent_name in synthesis_agents:
            print(f"\n📋 {agent_name.upper()} synthesizing...")
            await asyncio.sleep(1)
            
            synthesis = await self.agents[agent_name].synthesize(context)
            context["recommendations"].append({
                "agent": agent_name,
                "recommendation": synthesis
            })
            print(f"✅ {agent_name}: {synthesis[:150]}...")
        
        # Final summary
        print(f"\n\n{'='*60}")
        print("📊 CONVERSATION SUMMARY")
        print(f"{'='*60}")
        print(f"\n🎯 Key Recommendations:")
        for i, rec in enumerate(context["recommendations"], 1):
            print(f"\n{i}. From {rec['agent'].upper()}:")
            print(f"   {rec['recommendation'][:200]}...")
        
        return context

async def main():
    """Run the demo"""
    print("🚀 Marketing Swarm Demo")
    print("=" * 60)
    print("This demonstrates how AI agents collaborate like a real marketing team")
    print("Note: Using mock responses for demo - no API calls made\n")
    
    demo = MarketingSwarmDemo()
    
    # Demo scenarios
    scenarios = [
        "How should we launch our new robo-advisor to compete with Betterment?",
        # "Our customer acquisition cost has doubled. What's our action plan?",
        # "We need a content strategy that builds trust with Gen Z about retirement planning."
    ]
    
    for query in scenarios:
        try:
            await demo.simulate_conversation(query)
            
            print("\n\n⏸️  Press Enter for next scenario...")
            input()
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Error in demo: {e}")
            print("This is a simplified demo. For full functionality, run the complete system.")
    
    print("\n\n🎉 Demo complete!")
    print("\nTo run the full system:")
    print("1. Install all dependencies")
    print("2. Add your OpenAI API key to backend/.env")
    print("3. Start backend: cd backend && python main.py")
    print("4. Start frontend: cd frontend && npm start")
    print("5. Open http://localhost:3000")

if __name__ == "__main__":
    asyncio.run(main())