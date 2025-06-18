"""
Base Marketing Agent (Simplified without CrewAI)
Foundation for all marketing agents in the swarm
"""

from typing import Dict, List, Any, Union
from datetime import datetime
import asyncio
from abc import ABC, abstractmethod
from utils.openai_helper import get_openai_client
from tools.web_search import AgentWebSearchTool

class BaseMarketingAgent(ABC):
    """Base class for all marketing agents"""
    
    def __init__(self, name: str, role: str, goal: str, backstory: str, personality: Dict):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.personality = personality
        # Extract expertise from goal/backstory for web search
        self.expertise = self._extract_expertise(goal, backstory)
        self.web_search = AgentWebSearchTool(
            agent_specialty=self.expertise,
            openai_api_key=""  # Will use mock in dev mode
        )
        self.conversation_history = []
        self.current_context = {}
        
    async def analyze_with_current_data(self, user_query: str, context: Dict = None) -> str:
        """
        Phase 1: Analyze the user's query with current market data
        """
        # In production, this would search for real-time data
        # For now, return a thoughtful analysis based on role
        
        analysis_prompt = f"""
        As {self.name}, a {self.role} with expertise in {self.expertise},
        analyze this query: {user_query}
        
        Consider your unique perspective and {self.personality} personality.
        Provide insights that only someone in your role would think of.
        """
        
        # Simulate thinking time
        await asyncio.sleep(2)
        
        # In production, would call OpenAI API
        # For demo, return role-specific response
        return self._generate_analysis_response(user_query)
    
    async def collaborate(self, context: Dict) -> str:
        """
        Phase 2: Build on other agents' ideas
        """
        # Extract insights from other agents
        other_insights = context.get("insights", [])
        
        collaboration_prompt = f"""
        As {self.name}, respond to these insights from other team members:
        {other_insights}
        
        Build on their ideas from your {self.role} perspective.
        """
        
        # Simulate collaboration time
        await asyncio.sleep(1.5)
        
        return self._generate_collaboration_response(context)
    
    async def synthesize(self, context: Dict) -> str:
        """
        Phase 3: Create actionable recommendations
        """
        all_insights = context.get("insights", [])
        
        synthesis_prompt = f"""
        As {self.name}, synthesize all team insights into actionable recommendations.
        Focus on your area of {self.expertise}.
        """
        
        # Simulate synthesis time
        await asyncio.sleep(1)
        
        return self._generate_synthesis_response(context)
    
    @abstractmethod
    def _generate_analysis_response(self, query: str) -> str:
        """Generate role-specific analysis response"""
        pass
    
    @abstractmethod
    def _generate_collaboration_response(self, context: Dict) -> str:
        """Generate role-specific collaboration response"""
        pass
    
    @abstractmethod
    def _generate_synthesis_response(self, context: Dict) -> str:
        """Generate role-specific synthesis response"""
        pass
    
    async def search_current_data(self, query: str) -> Dict:
        """Search for current market data (mocked in dev mode)"""
        try:
            results = await self.web_search.search_current_data(query)
            return results
        except Exception as e:
            # Return mock data if search fails
            return {
                "status": "mock_data",
                "results": f"Mock search results for: {query}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_expertise(self, goal: str, backstory: str) -> str:
        """Extract expertise from goal and backstory for web search context"""
        # Simple extraction - in production would use NLP
        expertise_keywords = {
            "brand": "brand strategy and positioning",
            "campaign": "digital marketing campaigns",
            "content": "content marketing and SEO",
            "experience": "user experience and design",
            "analytics": "marketing analytics and ROI",
            "growth": "growth marketing and acquisition"
        }
        
        combined_text = (goal + " " + backstory).lower()
        for keyword, expertise in expertise_keywords.items():
            if keyword in combined_text:
                return expertise
        
        return "marketing strategy"
    
    def add_to_memory(self, interaction: Dict):
        """Add interaction to agent's memory"""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "interaction": interaction
        })
        
        # Keep only last 10 interactions
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def get_agent_info(self) -> Dict:
        """Get agent information for display"""
        return {
            "name": self.name,
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "personality": self.personality,
            "expertise": self.expertise,
            "status": "ready"
        }