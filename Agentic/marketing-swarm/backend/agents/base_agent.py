"""
Base Agent Module
Foundation for all marketing agents with personality and capabilities
"""

import os
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime
from loguru import logger
from crewai import Agent
from langchain_openai import ChatOpenAI

from tools.crewai_web_search import CrewAIWebSearchTool

class BaseMarketingAgent(ABC):
    """Base class for all marketing agents"""
    
    def __init__(self, name: str, role: str, goal: str, backstory: str, personality: Dict[str, str]):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.personality = personality
        
        # Initialize tools
        self.web_search_tool = CrewAIWebSearchTool(
            agent_specialty=role
        )
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize CrewAI agent
        self.agent = Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
            tools=[self.web_search_tool]
        )
        
        # Agent state
        self.conversation_history = []
        self.last_response_time = None
        self.total_responses = 0
        
    @abstractmethod
    def get_initial_analysis_prompt(self, user_query: str) -> str:
        """Get agent-specific initial analysis prompt"""
        pass
    
    @abstractmethod
    def get_collaboration_prompt(self, context: Dict) -> str:
        """Get agent-specific collaboration prompt"""
        pass
    
    @abstractmethod
    def get_synthesis_prompt(self, context: Dict) -> str:
        """Get agent-specific synthesis prompt"""
        pass
    
    def analyze_with_current_data(self, user_query: str, context: Dict) -> str:
        """Analyze query with web search for current data"""
        try:
            # Search for current data using CrewAI tool
            search_results = self.web_search_tool._run(
                query=user_query,
                context=self.role,
                specialty=self.role
            )
            
            # Create analysis prompt with search results
            prompt = self.get_initial_analysis_prompt(user_query)
            
            if search_results and "fallback" not in search_results.lower():
                prompt += f"\n\nCurrent market data:\n{search_results}"
            
            # Get agent's analysis
            response = self._generate_response(prompt, context)
            
            # Add personality flair
            response = self._add_personality_to_response(response)
            
            # Track response
            self._track_response(response, "analysis")
            
            return response
            
        except Exception as e:
            logger.error(f"Agent {self.name} analysis error: {e}")
            return self._get_error_response("analysis")
    
    def collaborate(self, context: Dict) -> str:
        """Generate collaborative response based on conversation context"""
        try:
            # Get collaboration prompt
            prompt = self.get_collaboration_prompt(context)
            
            # Add recent conversation context
            recent_responses = context.get("agent_responses", [])[-5:]
            if recent_responses:
                prompt += "\n\nRecent discussion:"
                for resp in recent_responses:
                    prompt += f"\n{resp['agent']}: {resp['message'][:200]}..."
            
            # Generate response
            response = self._generate_response(prompt, context)
            
            # Add personality and ensure collaboration
            response = self._ensure_collaborative_tone(response)
            response = self._add_personality_to_response(response)
            
            # Track response
            self._track_response(response, "collaboration")
            
            return response
            
        except Exception as e:
            logger.error(f"Agent {self.name} collaboration error: {e}")
            return self._get_error_response("collaboration")
    
    def synthesize(self, context: Dict) -> str:
        """Generate synthesis response to conclude discussion"""
        try:
            # Get synthesis prompt
            prompt = self.get_synthesis_prompt(context)
            
            # Add full conversation context
            all_responses = context.get("agent_responses", [])
            key_insights = self._extract_key_insights(all_responses)
            
            prompt += f"\n\nKey insights from discussion:\n{key_insights}"
            
            # Generate response
            response = self._generate_response(prompt, context)
            
            # Ensure actionable recommendations
            response = self._ensure_actionable_recommendations(response)
            response = self._add_personality_to_response(response)
            
            # Track response
            self._track_response(response, "synthesis")
            
            return response
            
        except Exception as e:
            logger.error(f"Agent {self.name} synthesis error: {e}")
            return self._get_error_response("synthesis")
    
    def _generate_response(self, prompt: str, context: Dict) -> str:
        """Generate response using the LLM"""
        try:
            # Add personality context to system message
            system_message = f"""You are {self.name}, a {self.role}.
Personality traits: {', '.join(f'{k}: {v}' for k, v in self.personality.items())}
Your goal: {self.goal}

Respond naturally and conversationally, building on others' ideas when appropriate.
Keep responses concise but insightful (2-3 paragraphs max).
Reference specific data, metrics, or examples when possible."""

            # Combine system message with prompt for LangChain
            full_prompt = f"{system_message}\n\n{prompt}"
            
            # Use sync predict method
            response = self.llm.predict(full_prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"LLM generation error for {self.name}: {e}")
            raise
    
    def _add_personality_to_response(self, response: str) -> str:
        """Add personality-specific phrases and style"""
        # This is a simplified version - each agent subclass can override for more personality
        personality_phrases = {
            "strategic": ["From a strategic perspective,", "The bigger picture here is"],
            "analytical": ["The data suggests", "Looking at the numbers"],
            "creative": ["Here's a creative approach:", "What if we"],
            "practical": ["In practical terms,", "The implementation would"],
            "empathetic": ["Understanding the user's perspective,", "This resonates with"],
            "innovative": ["Pushing the boundaries,", "A cutting-edge approach would"]
        }
        
        # Add a personality phrase if not already present
        for trait, phrases in personality_phrases.items():
            if trait in str(self.personality.values()).lower():
                # Occasionally add personality phrase (not every time)
                import random
                if random.random() < 0.3:  # 30% chance
                    phrase = random.choice(phrases)
                    if phrase.lower() not in response.lower():
                        response = f"{phrase} {response}"
                        break
        
        return response
    
    def _ensure_collaborative_tone(self, response: str) -> str:
        """Ensure response builds on previous ideas"""
        collaborative_phrases = [
            "Building on that,",
            "That's a great point,",
            "To add to that,",
            "I agree, and also",
            "Expanding on that idea,",
            "Yes, and we could also"
        ]
        
        # Check if response already has collaborative tone
        has_collaborative = any(phrase.lower() in response.lower() for phrase in collaborative_phrases)
        
        if not has_collaborative:
            import random
            phrase = random.choice(collaborative_phrases)
            response = f"{phrase} {response}"
        
        return response
    
    def _ensure_actionable_recommendations(self, response: str) -> str:
        """Ensure synthesis includes actionable recommendations"""
        action_keywords = ["recommend", "suggest", "should", "action", "next step", "implement"]
        
        has_actions = any(keyword in response.lower() for keyword in action_keywords)
        
        if not has_actions:
            response += "\n\nKey actions to consider: "
        
        return response
    
    def _extract_key_insights(self, responses: List[Dict]) -> str:
        """Extract key insights from conversation"""
        insights = []
        
        # Simple keyword extraction for insights
        insight_keywords = ["important", "key", "critical", "essential", "recommend", "suggest", "data shows", "trend"]
        
        for resp in responses:
            message = resp.get("message", "")
            sentences = message.split(".")
            
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in insight_keywords):
                    insights.append(f"- {sentence.strip()}")
        
        # Limit to top 5 insights
        return "\n".join(insights[:5]) if insights else "Various strategic points were discussed"
    
    def _track_response(self, response: str, response_type: str):
        """Track agent responses for analytics"""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": response_type,
            "response": response[:500]  # Store preview
        })
        
        self.last_response_time = datetime.now()
        self.total_responses += 1
        
        # Keep history manageable
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-50:]
    
    def _get_error_response(self, stage: str) -> str:
        """Get appropriate error response"""
        error_responses = {
            "analysis": f"I apologize, but I'm having trouble accessing current data for analysis. Based on my expertise in {self.role}, I'd suggest focusing on proven strategies while we resolve this.",
            "collaboration": f"I'm experiencing some technical difficulties, but I agree with the direction of this discussion. {self.name} here - let me add that we should continue exploring these ideas.",
            "synthesis": f"While I'm having some technical issues, the key takeaway from our discussion is clear: we need a comprehensive approach that addresses all the points raised."
        }
        
        return error_responses.get(stage, "I'm experiencing technical difficulties but remain committed to helping with this marketing challenge.")
    
    def health_check(self) -> bool:
        """Check if agent is healthy and responsive"""
        try:
            # Simple health check - verify LLM is working
            test_prompt = f"You are {self.name}. Respond with 'healthy' if you're operational"
            test_response = self.llm.predict(test_prompt)
            
            return "healthy" in test_response.lower()
            
        except Exception as e:
            logger.error(f"Agent {self.name} health check failed: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            "name": self.name,
            "role": self.role,
            "total_responses": self.total_responses,
            "last_response": self.last_response_time.isoformat() if self.last_response_time else None,
            "health": "healthy"  # Will be updated by health check
        }