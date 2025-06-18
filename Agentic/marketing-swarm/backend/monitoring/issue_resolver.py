"""
Automated Issue Resolution Module
Detects and attempts to resolve common system issues
"""

import asyncio
import os
from typing import List, Dict, Callable, Any
from datetime import datetime, timedelta
from loguru import logger

class AutomatedIssueResolver:
    """Intelligent issue detection and automated resolution"""
    
    def __init__(self):
        self.resolution_strategies = {
            "websocket_connection_failed": self.fix_websocket_issues,
            "agent_not_responding": self.restart_agent,
            "api_rate_limit_exceeded": self.enable_fallback_mode,
            "database_connection_lost": self.reconnect_database,
            "memory_usage_high": self.clear_caches,
            "conversation_timeout": self.reset_conversation_state,
            "openai_api_error": self.handle_api_error,
            "performance_degradation": self.optimize_performance,
            "budget_exhausted": self.handle_budget_exhaustion
        }
        
        self.issue_history = []
        self.resolution_history = []
        self.last_scan_time = datetime.now()
        
    async def detect_and_resolve_issues(self):
        """Continuously monitor and auto-resolve common issues"""
        while True:
            try:
                issues = await self.scan_for_issues()
                
                for issue in issues:
                    # Check if we've already tried to fix this recently
                    if not self.should_attempt_resolution(issue):
                        logger.info(f"Skipping resolution for {issue['type']} - recently attempted")
                        continue
                    
                    await self.attempt_resolution(issue)
                
                self.last_scan_time = datetime.now()
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Issue resolver error: {e}")
                await asyncio.sleep(60)  # Wait longer if resolver fails

    async def scan_for_issues(self) -> List[Dict]:
        """Scan system for known issue patterns"""
        issues = []
        
        try:
            # Import here to avoid circular dependency
            from monitoring.health_monitor import SystemHealthMonitor
            health_monitor = SystemHealthMonitor()
            
            # Check WebSocket connections
            if health_monitor.health_data.get("websocket_status") == "error":
                issues.append({
                    "type": "websocket_connection_failed",
                    "severity": "high",
                    "description": "WebSocket connections failing"
                })
            
            # Check agent responsiveness
            agent_statuses = health_monitor.health_data.get("agent_statuses", {})
            for agent_name, status in agent_statuses.items():
                if status == "error":
                    issues.append({
                        "type": "agent_not_responding",
                        "agent": agent_name,
                        "severity": "medium",
                        "description": f"Agent {agent_name} not responding"
                    })
            
            # Check API status
            if health_monitor.health_data.get("api_connectivity") == "error":
                issues.append({
                    "type": "openai_api_error",
                    "severity": "high",
                    "description": "OpenAI API connectivity issues"
                })
            
            # Check memory usage (simplified without psutil)
            # For now, we'll skip this check
            
            # Check budget status
            from safety.budget_guard import BudgetGuard
            budget_guard = BudgetGuard()
            if budget_guard.daily_spend >= float(os.getenv("DAILY_API_BUDGET", 50)):
                issues.append({
                    "type": "budget_exhausted",
                    "severity": "high",
                    "description": "Daily API budget exhausted"
                })
            
        except Exception as e:
            logger.error(f"Issue scanning failed: {e}")
            issues.append({
                "type": "scanner_failure",
                "severity": "low",
                "description": f"Issue scanner error: {str(e)}"
            })
        
        return issues

    def should_attempt_resolution(self, issue: Dict) -> bool:
        """Check if we should attempt to resolve this issue"""
        # Don't try to fix the same issue more than once per 5 minutes
        recent_attempts = [
            r for r in self.resolution_history
            if r["issue_type"] == issue["type"]
            and r["timestamp"] > datetime.now() - timedelta(minutes=5)
        ]
        
        return len(recent_attempts) == 0

    async def attempt_resolution(self, issue: Dict):
        """Try to automatically resolve detected issues"""
        issue_type = issue["type"]
        resolver = self.resolution_strategies.get(issue_type)
        
        if resolver:
            try:
                logger.info(f"Attempting auto-resolution of: {issue['description']}")
                result = await resolver(issue)
                
                # Record resolution attempt
                self.resolution_history.append({
                    "issue_type": issue_type,
                    "timestamp": datetime.now(),
                    "success": result["success"],
                    "details": result
                })
                
                if result["success"]:
                    logger.info(f"Auto-resolved: {issue['description']}")
                    await self.log_successful_resolution(issue, result)
                else:
                    logger.warning(f"Auto-resolution failed: {issue['description']}")
                    await self.escalate_issue(issue)
                    
            except Exception as e:
                logger.error(f"Resolution attempt failed: {e}")
                await self.escalate_issue(issue)
        else:
            logger.warning(f"No resolution strategy for issue type: {issue_type}")

    async def fix_websocket_issues(self, issue: Dict) -> Dict:
        """Attempt to fix WebSocket connection problems"""
        try:
            # For now, log the issue - actual WebSocket restart would be handled by the server
            logger.info("WebSocket issue detected - monitoring for recovery")
            
            # Wait and check if connections recover
            await asyncio.sleep(5)
            
            # Re-check status
            from monitoring.health_monitor import SystemHealthMonitor
            health_monitor = SystemHealthMonitor()
            
            if health_monitor.health_data.get("websocket_status") == "healthy":
                return {"success": True, "action": "WebSocket recovered"}
            else:
                return {"success": False, "reason": "WebSocket still unhealthy"}
                
        except Exception as e:
            return {"success": False, "reason": str(e)}

    async def restart_agent(self, issue: Dict) -> Dict:
        """Restart a problematic agent"""
        try:
            agent_name = issue.get("agent")
            if agent_name:
                from agents.agent_manager import AgentManager
                agent_manager = AgentManager()
                
                # Attempt to restart the agent
                success = await agent_manager.restart_agent(agent_name)
                
                if success:
                    # Verify agent is working
                    await asyncio.sleep(3)
                    if await agent_manager.check_agent_health(agent_name):
                        return {"success": True, "action": f"Agent {agent_name} restarted"}
                    else:
                        return {"success": False, "reason": f"Agent {agent_name} still not responding"}
                else:
                    return {"success": False, "reason": f"Failed to restart agent {agent_name}"}
            else:
                return {"success": False, "reason": "No agent specified"}
                
        except Exception as e:
            return {"success": False, "reason": str(e)}

    async def enable_fallback_mode(self, issue: Dict) -> Dict:
        """Enable fallback mode for API issues"""
        try:
            from emergency.fallback_system import FallbackManager
            fallback_manager = FallbackManager()
            
            await fallback_manager.activate()
            
            return {"success": True, "action": "Fallback mode activated"}
        except Exception as e:
            return {"success": False, "reason": str(e)}

    async def reconnect_database(self, issue: Dict) -> Dict:
        """Attempt to reconnect to database"""
        try:
            from api.conversation_manager import ConversationManager
            cm = ConversationManager()
            
            # Attempt to reinitialize database connection
            await cm.initialize_database()
            
            # Test connection
            if await cm.database_health_check():
                return {"success": True, "action": "Database reconnected"}
            else:
                return {"success": False, "reason": "Database still not responding"}
                
        except Exception as e:
            return {"success": False, "reason": str(e)}

    async def clear_caches(self, issue: Dict) -> Dict:
        """Clear caches to free memory"""
        try:
            # Clear web search cache
            from tools.data_cache import clear_all_caches
            await clear_all_caches()
            
            # Force garbage collection
            import gc
            gc.collect()
            
            return {"success": True, "action": "Caches cleared"}
                
        except Exception as e:
            return {"success": False, "reason": str(e)}

    async def reset_conversation_state(self, issue: Dict) -> Dict:
        """Reset stuck conversation state"""
        try:
            conversation_id = issue.get("conversation_id")
            if conversation_id:
                from api.conversation_manager import ConversationManager
                cm = ConversationManager()
                
                await cm.fail_conversation(conversation_id, "Conversation timeout - reset by system")
                
                return {"success": True, "action": f"Conversation {conversation_id} reset"}
            else:
                return {"success": False, "reason": "No conversation ID provided"}
                
        except Exception as e:
            return {"success": False, "reason": str(e)}

    async def handle_api_error(self, issue: Dict) -> Dict:
        """Handle OpenAI API errors"""
        try:
            # Check if it's a rate limit or quota issue
            error_msg = issue.get("description", "").lower()
            
            if "rate limit" in error_msg:
                # Enable rate limiting mode
                os.environ["API_RATE_LIMIT_MODE"] = "true"
                return {"success": True, "action": "Rate limiting mode enabled"}
            
            elif "quota" in error_msg or "budget" in error_msg:
                # Enable fallback mode
                return await self.enable_fallback_mode(issue)
            
            else:
                # Generic API error - wait and retry
                await asyncio.sleep(30)
                return {"success": False, "reason": "API error persists"}
                
        except Exception as e:
            return {"success": False, "reason": str(e)}

    async def optimize_performance(self, issue: Dict) -> Dict:
        """Optimize system performance"""
        try:
            # Reduce concurrent operations
            os.environ["PERFORMANCE_MODE"] = "conservative"
            
            # Clear caches
            cache_result = await self.clear_caches(issue)
            
            # Reduce agent activity
            from agents.agent_manager import AgentManager
            agent_manager = AgentManager()
            await agent_manager.set_performance_mode("conservative")
            
            return {
                "success": True, 
                "action": "Performance optimization applied",
                "details": cache_result
            }
            
        except Exception as e:
            return {"success": False, "reason": str(e)}

    async def handle_budget_exhaustion(self, issue: Dict) -> Dict:
        """Handle budget exhaustion"""
        try:
            # Immediately enable fallback mode
            fallback_result = await self.enable_fallback_mode(issue)
            
            # Notify admins
            logger.critical("BUDGET EXHAUSTED - Switching to fallback mode")
            
            return fallback_result
            
        except Exception as e:
            return {"success": False, "reason": str(e)}

    async def log_successful_resolution(self, issue: Dict, result: Dict):
        """Log successful resolution for analysis"""
        self.issue_history.append({
            "timestamp": datetime.now(),
            "issue": issue,
            "resolution": result,
            "status": "resolved"
        })
        
        # Keep history size manageable
        if len(self.issue_history) > 1000:
            self.issue_history = self.issue_history[-500:]

    async def escalate_issue(self, issue: Dict):
        """Escalate unresolved issues"""
        self.issue_history.append({
            "timestamp": datetime.now(),
            "issue": issue,
            "status": "escalated"
        })
        
        logger.error(f"Issue escalated: {issue['type']} - {issue['description']}")
        
        # In production, this would notify ops team
        # For now, just log prominently

    def reset(self):
        """Reset issue resolver state"""
        self.issue_history = []
        self.resolution_history = []
        logger.info("Issue resolver reset completed")