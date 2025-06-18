"""
Agent Manager Module
Manages all marketing agents and their interactions
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger

from agents.sarah_brand import SarahBrandAgent
from agents.marcus_campaigns import MarcusCampaignAgent
from agents.elena_content import ElenaContentAgent
from agents.david_experience import DavidExperienceAgent
from agents.priya_analytics import PriyaAnalyticsAgent
from agents.alex_growth import AlexGrowthAgent

class AgentManager:
    """Manages all marketing agents"""
    
    def __init__(self):
        self.agents = {}
        self.agent_classes = {
            "sarah": SarahBrandAgent,
            "marcus": MarcusCampaignAgent,
            "elena": ElenaContentAgent,
            "david": DavidExperienceAgent,
            "priya": PriyaAnalyticsAgent,
            "alex": AlexGrowthAgent
        }
        self.performance_mode = "normal"
        self.initialization_status = {}
        
    async def initialize_all_agents(self):
        """Initialize all marketing agents"""
        logger.info("Initializing marketing agent team...")
        
        initialization_tasks = []
        for agent_name, agent_class in self.agent_classes.items():
            initialization_tasks.append(self._initialize_agent(agent_name, agent_class))
        
        # Initialize all agents concurrently
        results = await asyncio.gather(*initialization_tasks, return_exceptions=True)
        
        # Check results
        for agent_name, result in zip(self.agent_classes.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"Failed to initialize {agent_name}: {result}")
                self.initialization_status[agent_name] = "failed"
            else:
                self.initialization_status[agent_name] = "ready"
        
        # Log summary
        ready_count = sum(1 for status in self.initialization_status.values() if status == "ready")
        logger.info(f"Agent initialization complete: {ready_count}/{len(self.agent_classes)} agents ready")
        
        return ready_count == len(self.agent_classes)
    
    async def _initialize_agent(self, agent_name: str, agent_class):
        """Initialize a single agent"""
        try:
            logger.info(f"Initializing agent: {agent_name}")
            agent = agent_class()
            
            # Verify agent is responsive
            health_ok = agent.health_check()
            if not health_ok:
                raise Exception(f"Agent {agent_name} failed health check")
            
            self.agents[agent_name] = agent
            logger.info(f"Agent {agent_name} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize {agent_name}: {e}")
            raise
    
    def get_agent(self, agent_name: str) -> Optional[Any]:
        """Get a specific agent"""
        return self.agents.get(agent_name)
    
    async def get_all_agent_status(self) -> Dict[str, Dict]:
        """Get status of all agents"""
        status = {}
        
        for agent_name in self.agent_classes.keys():
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                try:
                    health_ok = await agent.health_check()
                    stats = agent.get_stats()
                    status[agent_name] = {
                        "status": "ready" if health_ok else "unhealthy",
                        "stats": stats,
                        "tools": ["web_search"],
                        "last_response": stats.get("last_response")
                    }
                except Exception as e:
                    logger.error(f"Error getting status for {agent_name}: {e}")
                    status[agent_name] = {
                        "status": "error",
                        "error": str(e)
                    }
            else:
                status[agent_name] = {
                    "status": "not_initialized",
                    "initialization_status": self.initialization_status.get(agent_name, "unknown")
                }
        
        return status
    
    async def check_agent_health(self, agent_name: str) -> bool:
        """Check if specific agent is healthy"""
        agent = self.get_agent(agent_name)
        if not agent:
            return False
        
        try:
            return await agent.health_check()
        except Exception as e:
            logger.error(f"Health check failed for {agent_name}: {e}")
            return False
    
    async def restart_agent(self, agent_name: str) -> bool:
        """Restart a specific agent"""
        try:
            logger.info(f"Restarting agent: {agent_name}")
            
            # Remove existing agent
            if agent_name in self.agents:
                del self.agents[agent_name]
            
            # Reinitialize
            agent_class = self.agent_classes.get(agent_name)
            if not agent_class:
                logger.error(f"Unknown agent: {agent_name}")
                return False
            
            await self._initialize_agent(agent_name, agent_class)
            return agent_name in self.agents
            
        except Exception as e:
            logger.error(f"Failed to restart {agent_name}: {e}")
            return False
    
    async def reset_all_agents(self):
        """Reset all agents to initial state"""
        logger.info("Resetting all agents...")
        
        # Clear existing agents
        self.agents.clear()
        self.initialization_status.clear()
        
        # Reinitialize
        await self.initialize_all_agents()
    
    async def set_performance_mode(self, mode: str):
        """Set performance mode for all agents"""
        valid_modes = ["normal", "conservative", "minimal"]
        if mode not in valid_modes:
            logger.warning(f"Invalid performance mode: {mode}")
            return
        
        self.performance_mode = mode
        logger.info(f"Performance mode set to: {mode}")
        
        # In conservative mode, we might limit agent capabilities
        if mode == "conservative":
            # Reduce concurrent operations, simplify responses, etc.
            pass
        elif mode == "minimal":
            # Only essential agents active
            essential_agents = ["sarah", "priya"]  # Brand strategy and analytics only
            for agent_name in list(self.agents.keys()):
                if agent_name not in essential_agents:
                    logger.info(f"Disabling non-essential agent: {agent_name}")
                    del self.agents[agent_name]
    
    def get_agent_order(self, scenario: str = "default") -> List[str]:
        """Get recommended agent speaking order for different scenarios"""
        orders = {
            "default": ["sarah", "marcus", "elena", "david", "priya", "alex"],
            "brand_focus": ["sarah", "elena", "david", "marcus", "priya", "alex"],
            "performance_focus": ["marcus", "priya", "alex", "sarah", "elena", "david"],
            "content_focus": ["elena", "sarah", "david", "marcus", "priya", "alex"],
            "growth_focus": ["alex", "marcus", "priya", "sarah", "elena", "david"]
        }
        
        return orders.get(scenario, orders["default"])
    
    async def test_agent(self, agent_name: str) -> bool:
        """Test a specific agent with a simple query"""
        agent = self.get_agent(agent_name)
        if not agent:
            return False
        
        try:
            test_context = {
                "user_query": "Test query for agent functionality",
                "conversation_id": "test_" + datetime.now().isoformat()
            }
            
            response = await agent.analyze_with_current_data(
                "How can we improve customer acquisition?",
                test_context
            )
            
            return len(response) > 50  # Basic check that response is substantial
            
        except Exception as e:
            logger.error(f"Agent test failed for {agent_name}: {e}")
            return False