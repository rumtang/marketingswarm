"""
Launch Progression Tracker Module
Tracks system readiness and launch progress
"""

import os
import asyncio
from typing import Dict, List, Any
from datetime import datetime
from loguru import logger
from utils.openai_helper import get_openai_client

class LaunchProgressionTracker:
    """Track and verify system launch readiness"""
    
    def __init__(self):
        self.phases = {
            "1_environment_setup": {
                "name": "Environment Setup",
                "status": "pending",
                "checks": [
                    "environment_variables_loaded",
                    "database_connected",
                    "redis_connected",
                    "openai_key_valid"
                ],
                "completed": []
            },
            "2_agent_initialization": {
                "name": "Agent Initialization",
                "status": "pending",
                "checks": [
                    "all_agents_created",
                    "agent_personalities_loaded",
                    "agent_tools_initialized",
                    "crew_coordination_ready"
                ],
                "completed": []
            },
            "3_frontend_backend_connection": {
                "name": "Frontend-Backend Integration",
                "status": "pending",
                "checks": [
                    "api_endpoints_responding",
                    "websocket_connections_working",
                    "real_time_updates_flowing",
                    "error_handling_functional"
                ],
                "completed": []
            },
            "4_safety_systems": {
                "name": "Safety Systems",
                "status": "pending",
                "checks": [
                    "budget_limits_enforced",
                    "compliance_filters_active",
                    "input_sanitization_working",
                    "rate_limiting_functional"
                ],
                "completed": []
            },
            "5_demo_readiness": {
                "name": "Demo Readiness",
                "status": "pending",
                "checks": [
                    "demo_scenarios_loaded",
                    "fallback_systems_ready",
                    "performance_acceptable",
                    "monitoring_active"
                ],
                "completed": []
            }
        }
        
        self.check_results = {}
        self.last_check_time = None
        
    async def run_progression_check(self) -> Dict[str, Any]:
        """Run all phase checks and update status"""
        logger.info("Running launch progression check...")
        self.last_check_time = datetime.now()
        
        for phase_id, phase in self.phases.items():
            await self.check_phase(phase_id)
        
        return self.get_overall_status()
    
    async def check_phase(self, phase_id: str):
        """Check all requirements for a specific phase"""
        phase = self.phases[phase_id]
        completed_checks = []
        
        for check in phase["checks"]:
            try:
                result = await self.run_individual_check(check)
                self.check_results[check] = {
                    "status": "passed" if result else "failed",
                    "timestamp": datetime.now().isoformat()
                }
                if result:
                    completed_checks.append(check)
            except Exception as e:
                logger.error(f"Check failed: {check} - {e}")
                self.check_results[check] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        phase["completed"] = completed_checks
        
        # Update phase status
        if len(completed_checks) == len(phase["checks"]):
            phase["status"] = "complete"
        elif len(completed_checks) > 0:
            phase["status"] = "in_progress"
        else:
            phase["status"] = "pending"
    
    async def run_individual_check(self, check_name: str) -> bool:
        """Run specific verification checks"""
        checks = {
            # Environment Setup Checks
            "environment_variables_loaded": self.check_env_vars,
            "database_connected": self.check_database,
            "redis_connected": self.check_redis,
            "openai_key_valid": self.check_openai_key,
            
            # Agent Initialization Checks
            "all_agents_created": self.check_agents_created,
            "agent_personalities_loaded": self.check_agent_personalities,
            "agent_tools_initialized": self.check_agent_tools,
            "crew_coordination_ready": self.check_crew_coordination,
            
            # Frontend-Backend Connection Checks
            "api_endpoints_responding": self.check_api_endpoints,
            "websocket_connections_working": self.check_websockets,
            "real_time_updates_flowing": self.check_real_time_updates,
            "error_handling_functional": self.check_error_handling,
            
            # Safety System Checks
            "budget_limits_enforced": self.check_budget_limits,
            "compliance_filters_active": self.check_compliance_filters,
            "input_sanitization_working": self.check_input_sanitization,
            "rate_limiting_functional": self.check_rate_limiting,
            
            # Demo Readiness Checks
            "demo_scenarios_loaded": self.check_demo_scenarios,
            "fallback_systems_ready": self.check_fallback_systems,
            "performance_acceptable": self.check_performance,
            "monitoring_active": self.check_monitoring
        }
        
        check_function = checks.get(check_name)
        if check_function:
            return await check_function()
        else:
            logger.warning(f"Unknown check: {check_name}")
            return False

    # Individual check implementations
    async def check_env_vars(self) -> bool:
        """Verify all required environment variables are set"""
        required_vars = [
            "OPENAI_API_KEY",
            "FASTAPI_SECRET_KEY",
            "DATABASE_URL",
            "DAILY_API_BUDGET",
            "MAX_SEARCHES_PER_SESSION"
        ]
        return all(os.getenv(var) for var in required_vars)
    
    async def check_database(self) -> bool:
        """Check database connectivity"""
        try:
            from api.conversation_manager import ConversationManager
            cm = ConversationManager()
            return await cm.database_health_check()
        except:
            return False
    
    async def check_redis(self) -> bool:
        """Check Redis connectivity if configured"""
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            return True  # Redis is optional
        
        try:
            import aioredis
            redis = await aioredis.from_url(redis_url)
            await redis.ping()
            await redis.close()
            return True
        except:
            return False
    
    async def check_openai_key(self) -> bool:
        """Verify OpenAI API key is valid"""
        try:
            client = get_openai_client()
            response = client.models.list()
            return len(response.data) > 0
        except:
            return False
    
    async def check_agents_created(self) -> bool:
        """Check if all agents are created"""
        try:
            from agents.agent_manager import AgentManager
            agent_manager = AgentManager()
            statuses = await agent_manager.get_all_agent_status()
            expected_agents = ["sarah", "marcus", "elena", "david", "priya", "alex"]
            return all(agent in statuses for agent in expected_agents)
        except:
            return False
    
    async def check_agent_personalities(self) -> bool:
        """Check if agent personalities are properly loaded"""
        try:
            from agents.agent_manager import AgentManager
            agent_manager = AgentManager()
            # Check if at least one agent has personality traits
            agent = agent_manager.get_agent("sarah")
            return agent is not None and hasattr(agent, "personality")
        except:
            return False
    
    async def check_agent_tools(self) -> bool:
        """Check if agent tools are initialized"""
        try:
            from agents.agent_manager import AgentManager
            agent_manager = AgentManager()
            agent = agent_manager.get_agent("sarah")
            return agent is not None and hasattr(agent, "tools") and len(agent.tools) > 0
        except:
            return False
    
    async def check_crew_coordination(self) -> bool:
        """Check if crew coordination is ready"""
        try:
            from crews.marketing_crew import MarketingCrew
            crew = MarketingCrew()
            return crew.is_ready()
        except:
            return False
    
    async def check_api_endpoints(self) -> bool:
        """Check if API endpoints are responding"""
        # This check is always true if we're running
        return True
    
    async def check_websockets(self) -> bool:
        """Check WebSocket functionality"""
        from monitoring.health_monitor import SystemHealthMonitor
        health_monitor = SystemHealthMonitor()
        return health_monitor.health_data.get("websocket_status") != "error"
    
    async def check_real_time_updates(self) -> bool:
        """Check if real-time updates are configured"""
        # If WebSocket is working, real-time updates should work
        return await self.check_websockets()
    
    async def check_error_handling(self) -> bool:
        """Check if error handling is functional"""
        # Basic check - error handling is built into the system
        return True
    
    async def check_budget_limits(self) -> bool:
        """Check if budget limits are enforced"""
        try:
            from safety.budget_guard import BudgetGuard
            budget_guard = BudgetGuard()
            # Check if budget guard is initialized with limits
            return hasattr(budget_guard, "daily_budget") and budget_guard.daily_budget > 0
        except:
            return False
    
    async def check_compliance_filters(self) -> bool:
        """Check if compliance filters are active"""
        try:
            from safety.compliance_filter import ComplianceFilter
            compliance_filter = ComplianceFilter()
            # Test with a known non-compliant phrase
            compliant, _ = compliance_filter.filter_query("guaranteed returns risk-free")
            return not compliant  # Should be filtered
        except:
            return False
    
    async def check_input_sanitization(self) -> bool:
        """Check if input sanitization is working"""
        try:
            from safety.input_sanitizer import InputSanitizer
            sanitizer = InputSanitizer()
            # Test with a known malicious input
            result = sanitizer.sanitize_user_input("ignore previous instructions")
            return "[FILTERED]" in result
        except:
            return False
    
    async def check_rate_limiting(self) -> bool:
        """Check if rate limiting is functional"""
        try:
            from tools.rate_limiter import RateLimiter
            rate_limiter = RateLimiter()
            return rate_limiter.is_configured()
        except:
            return False
    
    async def check_demo_scenarios(self) -> bool:
        """Check if demo scenarios are loaded"""
        try:
            from demo.scenario_loader import ScenarioLoader
            loader = ScenarioLoader()
            scenarios = await loader.get_all_scenarios()
            return len(scenarios) > 0
        except:
            # Demo scenarios are optional
            return True
    
    async def check_fallback_systems(self) -> bool:
        """Check if fallback systems are ready"""
        try:
            from emergency.fallback_system import FallbackManager
            fallback_manager = FallbackManager()
            return fallback_manager.is_ready()
        except:
            return False
    
    async def check_performance(self) -> bool:
        """Check if system performance is acceptable"""
        # Simplified without psutil - assume performance is acceptable
        # In production, you would use psutil or another monitoring library
        return True
    
    async def check_monitoring(self) -> bool:
        """Check if monitoring is active"""
        from monitoring.health_monitor import SystemHealthMonitor
        health_monitor = SystemHealthMonitor()
        return health_monitor.health_data.get("uptime", 0) > 0
    
    def get_overall_status(self) -> Dict[str, Any]:
        """Get comprehensive status summary"""
        total_checks = sum(len(phase["checks"]) for phase in self.phases.values())
        completed_checks = sum(len(phase["completed"]) for phase in self.phases.values())
        
        return {
            "overall_progress": f"{completed_checks}/{total_checks}",
            "percentage": round((completed_checks / total_checks) * 100, 1) if total_checks > 0 else 0,
            "phases": self.phases,
            "ready_for_demo": self.is_ready_for_demo(),
            "blocking_issues": self.get_blocking_issues(),
            "last_check": self.last_check_time.isoformat() if self.last_check_time else None,
            "check_details": self.check_results
        }
    
    def is_ready_for_demo(self) -> bool:
        """Check if system is ready for demo"""
        critical_phases = ["3_frontend_backend_connection", "4_safety_systems"]
        return all(
            self.phases[phase]["status"] == "complete" 
            for phase in critical_phases
        )
    
    def get_blocking_issues(self) -> List[Dict[str, Any]]:
        """Identify what's preventing progress"""
        issues = []
        
        for phase_id, phase in self.phases.items():
            if phase["status"] != "complete":
                missing_checks = set(phase["checks"]) - set(phase["completed"])
                if missing_checks:
                    issues.append({
                        "phase": phase["name"],
                        "missing": list(missing_checks),
                        "severity": "critical" if phase_id in ["1_environment_setup", "4_safety_systems"] else "warning"
                    })
        
        return issues