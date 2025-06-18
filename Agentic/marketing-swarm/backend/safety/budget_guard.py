"""
Budget Guard Module
Prevents API cost overruns with strict budget enforcement
"""

import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
from loguru import logger
import json

class BudgetGuard:
    """Strict API budget enforcement to prevent cost spirals"""
    
    def __init__(self):
        # Load budget limits from environment
        self.daily_budget = float(os.getenv("DAILY_API_BUDGET", 50.00))
        self.max_searches_per_session = int(os.getenv("MAX_SEARCHES_PER_SESSION", 25))
        self.max_searches_per_agent = int(os.getenv("MAX_SEARCHES_PER_AGENT", 5))
        
        # Initialize tracking
        self.daily_spend = 0.0
        self.session_searches = {}
        self.agent_searches = {}
        self.spend_history = []
        self.last_reset_date = datetime.now().date()
        
        # Cost estimates (conservative)
        self.cost_per_search = 0.10  # Estimated cost per web search
        self.cost_per_completion = 0.05  # Estimated cost per completion
        
        # Load persisted state if available
        self._load_state()
        
    async def check_budget_before_search(self, estimated_cost: float) -> Tuple[bool, str]:
        """Check if budget allows for a search operation"""
        # Reset daily budget if new day
        self._check_daily_reset()
        
        # Check daily budget
        if self.daily_spend + estimated_cost > self.daily_budget:
            logger.warning(f"Daily budget exceeded: ${self.daily_spend:.2f} + ${estimated_cost:.2f} > ${self.daily_budget:.2f}")
            return False, f"Daily budget of ${self.daily_budget:.2f} exceeded"
        
        return True, "OK"
    
    async def check_session_limit(self, session_id: str) -> Tuple[bool, str]:
        """Check if session has reached search limit"""
        session_count = self.session_searches.get(session_id, 0)
        
        if session_count >= self.max_searches_per_session:
            logger.warning(f"Session {session_id} reached search limit: {session_count}")
            return False, f"Session search limit of {self.max_searches_per_session} reached"
        
        return True, "OK"
    
    async def check_agent_limit(self, agent_name: str, session_id: str) -> Tuple[bool, str]:
        """Check if agent has reached per-session search limit"""
        agent_key = f"{agent_name}:{session_id}"
        agent_count = self.agent_searches.get(agent_key, 0)
        
        if agent_count >= self.max_searches_per_agent:
            logger.warning(f"Agent {agent_name} reached search limit for session {session_id}: {agent_count}")
            return False, f"Agent search limit of {self.max_searches_per_agent} reached"
        
        return True, "OK"
    
    async def record_api_usage(
        self, 
        cost: float, 
        operation_type: str, 
        session_id: Optional[str] = None,
        agent_name: Optional[str] = None
    ):
        """Record API usage and update spending"""
        self._check_daily_reset()
        
        # Update daily spend
        self.daily_spend += cost
        
        # Update session searches
        if session_id and operation_type == "search":
            self.session_searches[session_id] = self.session_searches.get(session_id, 0) + 1
            
            # Update agent searches
            if agent_name:
                agent_key = f"{agent_name}:{session_id}"
                self.agent_searches[agent_key] = self.agent_searches.get(agent_key, 0) + 1
        
        # Record in history
        self.spend_history.append({
            "timestamp": datetime.now().isoformat(),
            "cost": cost,
            "operation": operation_type,
            "session_id": session_id,
            "agent": agent_name,
            "daily_total": self.daily_spend
        })
        
        # Persist state
        self._save_state()
        
        # Log spending
        logger.info(
            f"API usage recorded: ${cost:.4f} for {operation_type} "
            f"(Daily: ${self.daily_spend:.2f}/${self.daily_budget:.2f})"
        )
        
        # Alert if approaching limit
        if self.daily_spend > self.daily_budget * 0.8:
            logger.warning(f"Approaching daily budget limit: ${self.daily_spend:.2f}/${self.daily_budget:.2f}")
    
    async def get_budget_status(self) -> Dict:
        """Get current budget status"""
        self._check_daily_reset()
        
        return {
            "daily_budget": self.daily_budget,
            "daily_spent": round(self.daily_spend, 2),
            "daily_remaining": round(self.daily_budget - self.daily_spend, 2),
            "percentage_used": round((self.daily_spend / self.daily_budget) * 100, 1),
            "active_sessions": len(self.session_searches),
            "total_searches_today": sum(self.session_searches.values()),
            "status": self._get_budget_health_status()
        }
    
    async def emergency_shutdown(self):
        """Emergency shutdown when budget is critically exceeded"""
        logger.critical(f"EMERGENCY BUDGET SHUTDOWN - Spent ${self.daily_spend:.2f}")
        
        # Set environment flag
        os.environ["BUDGET_EMERGENCY_SHUTDOWN"] = "true"
        
        # Clear all session data to prevent further spending
        self.session_searches.clear()
        self.agent_searches.clear()
        
        # Persist state
        self._save_state()
    
    def _check_daily_reset(self):
        """Reset daily spending if it's a new day"""
        current_date = datetime.now().date()
        
        if current_date > self.last_reset_date:
            logger.info(f"Resetting daily budget - Previous day spent: ${self.daily_spend:.2f}")
            
            # Archive yesterday's spending
            if self.daily_spend > 0:
                self._archive_daily_spending()
            
            # Reset counters
            self.daily_spend = 0.0
            self.session_searches.clear()
            self.agent_searches.clear()
            self.last_reset_date = current_date
            
            # Clear emergency shutdown if set
            if os.getenv("BUDGET_EMERGENCY_SHUTDOWN") == "true":
                os.environ["BUDGET_EMERGENCY_SHUTDOWN"] = "false"
            
            self._save_state()
    
    def _get_budget_health_status(self) -> str:
        """Determine budget health status"""
        percentage = (self.daily_spend / self.daily_budget) * 100
        
        if percentage >= 100:
            return "exhausted"
        elif percentage >= 90:
            return "critical"
        elif percentage >= 75:
            return "warning"
        elif percentage >= 50:
            return "moderate"
        else:
            return "healthy"
    
    def _save_state(self):
        """Persist budget state to file"""
        try:
            state = {
                "daily_spend": self.daily_spend,
                "last_reset_date": self.last_reset_date.isoformat(),
                "session_searches": self.session_searches,
                "agent_searches": self.agent_searches,
                "recent_history": self.spend_history[-100:]  # Keep last 100 entries
            }
            
            with open("budget_state.json", "w") as f:
                json.dump(state, f)
                
        except Exception as e:
            logger.error(f"Failed to save budget state: {e}")
    
    def _load_state(self):
        """Load persisted budget state"""
        try:
            if os.path.exists("budget_state.json"):
                with open("budget_state.json", "r") as f:
                    state = json.load(f)
                
                # Restore state if from today
                saved_date = datetime.fromisoformat(state["last_reset_date"]).date()
                if saved_date == datetime.now().date():
                    self.daily_spend = state["daily_spend"]
                    self.session_searches = state["session_searches"]
                    self.agent_searches = state["agent_searches"]
                    self.spend_history = state.get("recent_history", [])
                    logger.info(f"Restored budget state: ${self.daily_spend:.2f} spent today")
                    
        except Exception as e:
            logger.error(f"Failed to load budget state: {e}")
    
    def _archive_daily_spending(self):
        """Archive daily spending for analysis"""
        try:
            archive_entry = {
                "date": self.last_reset_date.isoformat(),
                "total_spent": round(self.daily_spend, 2),
                "total_searches": sum(self.session_searches.values()),
                "unique_sessions": len(self.session_searches),
                "budget_utilization": round((self.daily_spend / self.daily_budget) * 100, 1)
            }
            
            # Append to archive file
            archive_file = "budget_archive.jsonl"
            with open(archive_file, "a") as f:
                f.write(json.dumps(archive_entry) + "\n")
                
            logger.info(f"Archived daily spending: {archive_entry}")
            
        except Exception as e:
            logger.error(f"Failed to archive daily spending: {e}")
    
    async def get_spending_forecast(self) -> Dict:
        """Forecast remaining budget based on current usage rate"""
        if self.daily_spend == 0:
            return {
                "forecast": "No spending yet today",
                "estimated_total": 0,
                "hours_until_exhaustion": float('inf')
            }
        
        # Calculate spending rate
        hours_elapsed = (datetime.now() - datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )).total_seconds() / 3600
        
        if hours_elapsed > 0:
            hourly_rate = self.daily_spend / hours_elapsed
            estimated_daily_total = hourly_rate * 24
            
            if hourly_rate > 0:
                hours_remaining = (self.daily_budget - self.daily_spend) / hourly_rate
            else:
                hours_remaining = float('inf')
            
            return {
                "hourly_rate": round(hourly_rate, 2),
                "estimated_total": round(estimated_daily_total, 2),
                "hours_until_exhaustion": round(hours_remaining, 1),
                "will_exceed_budget": estimated_daily_total > self.daily_budget
            }
        
        return {
            "forecast": "Insufficient data",
            "estimated_total": self.daily_spend,
            "hours_until_exhaustion": float('inf')
        }