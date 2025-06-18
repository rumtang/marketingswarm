"""
System Health Monitoring Module
Provides real-time health checks and status reporting
"""

import asyncio
import time
import os
from datetime import datetime
from typing import Dict, Set, Any
import logging

from utils.openai_helper import get_openai_client
from loguru import logger
import aiohttp

class SystemHealthMonitor:
    """Comprehensive health monitoring for the marketing swarm system"""
    
    def __init__(self):
        self.health_data = {
            "backend_status": "starting",
            "websocket_status": "starting",
            "api_connectivity": "unknown",
            "agent_statuses": {},
            "current_conversations": 0,
            "api_budget_used": 0.0,
            "last_error": None,
            "uptime": 0,
            "start_time": time.time(),
            "cpu_usage": 0,
            "memory_usage": 0,
            "active_connections": 0
        }
        self.websocket_connections: Set[str] = set()
        self.active_conversations: Dict[str, Dict] = {}
        self.error_history = []
        self.performance_metrics = {
            "avg_response_time": 0,
            "total_api_calls": 0,
            "successful_conversations": 0,
            "failed_conversations": 0
        }
        
    async def continuous_health_check(self):
        """Run continuous health monitoring"""
        while True:
            try:
                # Update uptime
                self.health_data["uptime"] = int(time.time() - self.health_data["start_time"])
                
                # Update system metrics (simplified without psutil)
                self.health_data["cpu_usage"] = 0  # Placeholder
                self.health_data["memory_usage"] = 0  # Placeholder
                
                # Check all components
                await self.check_database_connection()
                await self.check_openai_api_connection()
                await self.check_agent_health()
                await self.check_websocket_health()
                await self.check_performance_thresholds()
                
                # Update overall status
                self.update_overall_status()
                
                # Broadcast health update to admin dashboard
                await self.broadcast_health_update()
                
                # Clean old error history
                self.clean_error_history()
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                await self.report_system_error("health_monitor", str(e))
                await asyncio.sleep(10)  # Wait longer if health check fails

    async def check_database_connection(self):
        """Verify database connectivity"""
        try:
            # Use the global conversation manager if available
            import main
            if hasattr(main, 'conversation_manager') and main.conversation_manager:
                result = await main.conversation_manager.database_health_check()
                if result:
                    self.health_data["backend_status"] = "healthy"
                else:
                    self.health_data["backend_status"] = "error"
                    await self.report_system_error("database", "Health check query failed")
            else:
                # If not available yet, mark as starting
                self.health_data["backend_status"] = "starting"
        except Exception as e:
            self.health_data["backend_status"] = "error"
            await self.report_system_error("database", str(e))

    async def check_openai_api_connection(self):
        """Test OpenAI API connectivity"""
        try:
            # Quick API test with minimal cost
            client = get_openai_client()
            
            # Use a simple, low-cost test
            response = client.models.list()
            if response.data:
                self.health_data["api_connectivity"] = "healthy"
            else:
                self.health_data["api_connectivity"] = "error"
                await self.report_system_error("openai_api", "No models returned")
        except Exception as e:
            self.health_data["api_connectivity"] = "error"
            await self.report_system_error("openai_api", str(e))

    async def check_agent_health(self):
        """Verify all agents are responsive"""
        agent_names = ["sarah", "marcus", "elena", "david", "priya", "alex"]
        
        try:
            # Use the global agent manager if available
            import main
            if hasattr(main, 'agent_manager') and main.agent_manager:
                for agent_name in agent_names:
                    try:
                        # Check if agent exists
                        agent = main.agent_manager.get_agent(agent_name)
                        if agent:
                            # Quick agent health check
                            status = agent.health_check()
                            self.health_data["agent_statuses"][agent_name] = "healthy" if status else "error"
                        else:
                            self.health_data["agent_statuses"][agent_name] = "not_initialized"
                    except Exception as e:
                        self.health_data["agent_statuses"][agent_name] = "error"
                        await self.report_system_error(f"agent_{agent_name}", str(e))
        except Exception as e:
            # If agent manager fails, mark all agents as error
            for agent_name in agent_names:
                self.health_data["agent_statuses"][agent_name] = "error"
            await self.report_system_error("agent_manager", str(e))

    async def check_websocket_health(self):
        """Monitor WebSocket connections"""
        active_connections = len(self.websocket_connections)
        self.health_data["active_connections"] = active_connections
        self.health_data["current_conversations"] = len(self.active_conversations)
        
        if self.health_data["backend_status"] == "healthy":
            if active_connections >= 0:  # At least ready for connections
                self.health_data["websocket_status"] = "healthy"
            else:
                self.health_data["websocket_status"] = "warning"
        else:
            self.health_data["websocket_status"] = "error"

    async def check_performance_thresholds(self):
        """Check if performance is within acceptable limits"""
        # Simplified without psutil - just placeholder
        pass

    def update_overall_status(self):
        """Determine overall system health status"""
        critical_components = ["backend_status", "api_connectivity"]
        critical_healthy = all(
            self.health_data.get(comp) == "healthy" 
            for comp in critical_components
        )
        
        agent_health = list(self.health_data.get("agent_statuses", {}).values())
        agents_healthy = agent_health.count("healthy") >= 4  # At least 4 of 6 agents
        
        if critical_healthy and agents_healthy:
            self.health_data["overall_status"] = "healthy"
        elif critical_healthy:
            self.health_data["overall_status"] = "degraded"
        else:
            self.health_data["overall_status"] = "critical"

    async def report_system_error(self, component: str, error_message: str):
        """Centralized error reporting with classification"""
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "error": error_message,
            "severity": self.classify_error_severity(component, error_message),
            "health_impact": self.assess_health_impact(component)
        }
        
        self.health_data["last_error"] = error_data
        self.error_history.append(error_data)
        
        # Log error with context
        logger.error(f"System Error in {component}: {error_message}", extra=error_data)
        
        # Broadcast error to admin dashboard
        await self.broadcast_error_alert(error_data)
        
        # Trigger automated response if needed
        if error_data["severity"] == "critical":
            await self.trigger_automated_response(error_data)

    def classify_error_severity(self, component: str, error: str) -> str:
        """Classify error severity for appropriate response"""
        critical_components = ["database", "openai_api", "agent_manager"]
        critical_errors = ["connection refused", "authentication failed", "quota exceeded"]
        
        if component in critical_components:
            return "critical"
        
        if any(critical_error in error.lower() for critical_error in critical_errors):
            return "critical"
            
        if "timeout" in error.lower() or "rate limit" in error.lower():
            return "warning"
            
        return "info"

    def assess_health_impact(self, component: str) -> str:
        """Assess the impact of component failure on system health"""
        impact_map = {
            "database": "critical",
            "openai_api": "critical",
            "agent_manager": "high",
            "websocket": "medium",
            "performance": "medium",
            "cache": "low"
        }
        
        for key, impact in impact_map.items():
            if key in component:
                return impact
        
        return "low"

    async def trigger_automated_response(self, error_data: Dict):
        """Trigger automated response for critical errors"""
        try:
            # Import here to avoid circular dependency
            from monitoring.issue_resolver import AutomatedIssueResolver
            resolver = AutomatedIssueResolver()
            
            issue = {
                "type": f"{error_data['component']}_error",
                "severity": error_data["severity"],
                "description": error_data["error"]
            }
            
            await resolver.attempt_resolution(issue)
            
        except Exception as e:
            logger.error(f"Failed to trigger automated response: {e}")

    async def broadcast_health_update(self):
        """Send health update to all admin connections"""
        # This will be called by the WebSocket handler
        # Keeping it here for the interface
        pass

    async def broadcast_error_alert(self, error_data: Dict):
        """Send error alert to admin connections"""
        # This will be called by the WebSocket handler
        # Keeping it here for the interface
        pass

    def clean_error_history(self, max_errors: int = 100):
        """Keep only recent errors to prevent memory growth"""
        if len(self.error_history) > max_errors:
            self.error_history = self.error_history[-max_errors:]

    def reset(self):
        """Reset health monitor to initial state"""
        self.__init__()
        logger.info("Health monitor reset completed")

    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of system health for display"""
        return {
            "status": self.health_data.get("overall_status", "unknown"),
            "uptime": self.health_data.get("uptime", 0),
            "active_connections": self.health_data.get("active_connections", 0),
            "cpu_usage": self.health_data.get("cpu_usage", 0),
            "memory_usage": self.health_data.get("memory_usage", 0),
            "recent_errors": len([
                e for e in self.error_history[-10:] 
                if e["severity"] in ["critical", "warning"]
            ]),
            "api_status": self.health_data.get("api_connectivity", "unknown"),
            "agent_health": f"{list(self.health_data.get('agent_statuses', {}).values()).count('healthy')}/6"
        }