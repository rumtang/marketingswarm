"""
Marketing Crew Module
Coordinates the marketing agent team using CrewAI
"""

from typing import List, Dict, Any
from crewai import Crew, Task
from loguru import logger

class MarketingCrew:
    """Manages the marketing agent crew coordination"""
    
    def __init__(self):
        self.crew = None
        self.agents = []
        self.is_initialized = False
        
    def initialize_crew(self, agents: List[Any]):
        """Initialize the crew with agents"""
        try:
            self.agents = agents
            
            # Create CrewAI crew
            self.crew = Crew(
                agents=[agent.agent for agent in agents],
                verbose=True,
                process="sequential",  # Agents work in sequence
                memory=True  # Enable crew memory
            )
            
            self.is_initialized = True
            logger.info("Marketing crew initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize crew: {e}")
            self.is_initialized = False
    
    def is_ready(self) -> bool:
        """Check if crew is ready to operate"""
        return self.is_initialized and self.crew is not None and len(self.agents) > 0
    
    async def run_marketing_discussion(self, user_query: str, context: Dict[str, Any]) -> List[Dict]:
        """Run a full marketing team discussion"""
        if not self.is_ready():
            raise Exception("Crew not initialized")
        
        responses = []
        
        try:
            # Create task for the discussion
            marketing_task = Task(
                description=f"""
                Analyze and provide comprehensive marketing recommendations for: {user_query}
                
                Each agent should:
                1. Provide initial analysis from their perspective
                2. Build on previous agents' ideas
                3. Offer specific, actionable recommendations
                
                Focus on practical, implementable strategies for financial services.
                """,
                expected_output="Comprehensive marketing strategy with specific recommendations from each expert perspective"
            )
            
            # Execute the crew task
            result = await self.crew.kickoff(inputs={"query": user_query})
            
            # Parse and structure the results
            # In practice, this would parse the actual crew output
            responses = self._parse_crew_output(result)
            
            return responses
            
        except Exception as e:
            logger.error(f"Crew execution failed: {e}")
            raise
    
    def _parse_crew_output(self, crew_output: Any) -> List[Dict]:
        """Parse crew output into structured responses"""
        # This is a simplified parser - in production would handle actual CrewAI output
        responses = []
        
        if hasattr(crew_output, 'raw_output'):
            # Split by agent responses
            raw_text = crew_output.raw_output
            agent_sections = raw_text.split("\n\n")
            
            for section in agent_sections:
                # Extract agent name and response
                if ":" in section:
                    agent_name, response = section.split(":", 1)
                    responses.append({
                        "agent": agent_name.strip().lower(),
                        "response": response.strip()
                    })
        
        return responses
    
    def get_crew_stats(self) -> Dict[str, Any]:
        """Get crew performance statistics"""
        if not self.is_ready():
            return {"status": "not_initialized"}
        
        return {
            "status": "ready",
            "agent_count": len(self.agents),
            "process_type": "sequential",
            "memory_enabled": True,
            "total_executions": 0  # Would track actual executions
        }