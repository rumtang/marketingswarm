"""
Emergency Recovery Manager
Handles system recovery and emergency procedures
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger

class EmergencyRecovery:
    """Emergency recovery system for critical failures"""
    
    def __init__(self):
        self.recovery_modes = {
            "demo_safe_mode": self.activate_demo_safe_mode,
            "api_fallback_mode": self.activate_api_fallback_mode,
            "minimal_operation_mode": self.activate_minimal_mode,
            "emergency_shutdown": self.emergency_shutdown
        }
        self.current_mode = "normal"
        self.fallback_conversations = {}
        self.cached_market_data = {}
        
    async def activate_demo_safe_mode(self):
        """Activate mode for critical demos with pre-recorded responses"""
        logger.info("🚨 ACTIVATING DEMO SAFE MODE")
        
        # Disable all real API calls
        os.environ["OPENAI_API_DISABLED"] = "true"
        os.environ["USE_FALLBACK_MODE"] = "true"
        
        # Set system status
        self.current_mode = "demo_safe"
        
        # Load pre-recorded conversations
        await self.load_fallback_conversations()
        
        # Broadcast system status
        await self.broadcast_system_message(
            "System in Demo Safe Mode - Using Pre-recorded Responses",
            "warning"
        )
        
        logger.info("Demo safe mode activated successfully")
        
        return {
            "status": "success",
            "mode": "demo_safe",
            "message": "System now using pre-recorded responses for stability"
        }

    async def activate_api_fallback_mode(self):
        """Use cached data instead of live API calls"""
        logger.info("⚠️ ACTIVATING API FALLBACK MODE")
        
        # Enable cached response mode
        os.environ["USE_CACHED_RESPONSES"] = "true"
        self.current_mode = "api_fallback"
        
        # Load recent cached data
        await self.load_cached_market_data()
        
        await self.broadcast_system_message(
            "Using cached data due to API limitations",
            "info"
        )
        
        return {
            "status": "success",
            "mode": "api_fallback",
            "message": "System using cached market data"
        }

    async def activate_minimal_mode(self):
        """Minimal functionality with basic responses"""
        logger.info("🔧 ACTIVATING MINIMAL OPERATION MODE")
        
        # Disable non-essential features
        os.environ["MINIMAL_MODE"] = "true"
        self.current_mode = "minimal"
        
        await self.disable_non_essential_agents()
        await self.reduce_conversation_complexity()
        
        await self.broadcast_system_message(
            "System in minimal operation mode",
            "warning"
        )
        
        return {
            "status": "success",
            "mode": "minimal",
            "message": "Running with reduced functionality"
        }

    async def emergency_shutdown(self):
        """Complete system shutdown with user notification"""
        logger.critical("🛑 EMERGENCY SHUTDOWN INITIATED")
        
        # Notify all connected users
        await self.broadcast_system_message(
            "System maintenance in progress - Please try again later",
            "error"
        )
        
        # Save current state
        await self.save_emergency_state()
        
        # Graceful shutdown
        await asyncio.sleep(5)  # Give time for messages to send
        
        logger.critical("Emergency shutdown completed")
        sys.exit(1)

    async def load_fallback_conversations(self):
        """Load pre-recorded high-quality conversations"""
        # These would be loaded from files in production
        self.fallback_conversations = {
            "robo_advisor_launch": {
                "query": "How should we launch our new robo-advisor to compete with Betterment?",
                "responses": [
                    {
                        "agent": "sarah",
                        "message": "From a strategic perspective, we need to differentiate beyond just features. Betterment has strong brand recognition, so we should position ourselves as the 'next generation' robo-advisor. I'm seeing three key angles: 1) Enhanced personalization using behavioral finance, 2) Social responsibility focus for ESG-conscious investors, and 3) Integration with broader financial wellness. What's our unique value proposition that Betterment can't easily copy?",
                        "timestamp": "2024-01-15T10:00:00Z"
                    },
                    {
                        "agent": "marcus",
                        "message": "Looking at current campaign data, Betterment's CPCs are around $4-6 for robo-advisor keywords. We'll need a $2-3M launch budget across channels. I recommend a phased approach: Start with lookalike audiences from our existing customers on Meta, then expand to Google's in-market audiences. LinkedIn will be crucial for the professional segment. We should also negotiate exclusive partnerships with personal finance influencers before Betterment locks them up.",
                        "timestamp": "2024-01-15T10:00:15Z"
                    },
                    {
                        "agent": "elena",
                        "message": "Building on Sarah's differentiation strategy, our content needs to educate while showcasing our unique approach. I propose a 'Smarter Investing' content series that addresses Betterment's weaknesses - like tax optimization for crypto investors or ESG portfolio customization. We should create interactive tools that let users see personalized projections, not just generic calculators. Video content showing real customer journeys will build trust faster than Betterment's text-heavy approach.",
                        "timestamp": "2024-01-15T10:00:30Z"
                    }
                ]
            },
            "high_cac_problem": {
                "query": "Our customer acquisition cost has doubled. What's our action plan?",
                "responses": [
                    {
                        "agent": "priya",
                        "message": "The data shows our CAC increased from $125 to $250 over six months. Breaking it down by channel: Google Ads CAC went from $95 to $210 (121% increase), Meta from $110 to $240 (118% increase), but organic channels only increased 15%. The problem is concentrated in paid channels. Our conversion rate dropped from 3.2% to 1.8%, suggesting the issue is partly quality, not just competition. We need immediate optimization while building sustainable acquisition channels.",
                        "timestamp": "2024-01-15T10:01:00Z"
                    },
                    {
                        "agent": "marcus",
                        "message": "That conversion drop is killing us. I'm seeing three immediate fixes: 1) Pause broad match keywords - they're bringing unqualified traffic, 2) Implement negative keywords from search term reports, 3) Shift 40% of budget to retargeting where CAC is still $80. Longer term, we need to test TikTok and Reddit where financial services CAC is 60% lower. Also, our landing pages need work - competitors are using dynamic personalization.",
                        "timestamp": "2024-01-15T10:01:20Z"
                    },
                    {
                        "agent": "alex",
                        "message": "Yes, and we're thinking too linearly about acquisition. High CAC often signals market saturation of traditional channels. Let's flip the model: 1) Launch a referral program with progressive rewards - current customers can cut our CAC by 70%, 2) Create viral financial literacy content that naturally leads to our product, 3) Partner with employers for financial wellness programs - B2B2C acquisition at scale. Robinhood cut their CAC by 80% with similar strategies.",
                        "timestamp": "2024-01-15T10:01:40Z"
                    }
                ]
            }
        }
    
    async def load_cached_market_data(self):
        """Load cached market data for API fallback"""
        self.cached_market_data = {
            "competitor_analysis": {
                "timestamp": "2024-01-15T09:00:00Z",
                "data": {
                    "betterment": {
                        "recent_campaigns": "Focus on tax-loss harvesting messaging",
                        "estimated_spend": "$2M/month",
                        "primary_channels": ["Google", "Meta", "Podcast advertising"]
                    },
                    "wealthfront": {
                        "recent_campaigns": "Self-driving money campaign",
                        "estimated_spend": "$1.5M/month",
                        "primary_channels": ["Google", "LinkedIn", "Content marketing"]
                    }
                }
            },
            "channel_benchmarks": {
                "timestamp": "2024-01-15T09:00:00Z",
                "data": {
                    "google_ads": {
                        "avg_cpc": "$4.50",
                        "avg_conversion_rate": "2.8%",
                        "avg_cac": "$160"
                    },
                    "meta_ads": {
                        "avg_cpc": "$2.80",
                        "avg_conversion_rate": "2.2%",
                        "avg_cac": "$127"
                    }
                }
            }
        }
    
    async def disable_non_essential_agents(self):
        """Disable non-essential agents for minimal mode"""
        from agents.agent_manager import AgentManager
        agent_manager = AgentManager()
        await agent_manager.set_performance_mode("minimal")
    
    async def reduce_conversation_complexity(self):
        """Simplify conversations for minimal mode"""
        os.environ["MAX_CONVERSATION_EXCHANGES"] = "20"
        os.environ["MAX_SEARCHES_PER_SESSION"] = "5"
    
    async def save_emergency_state(self):
        """Save system state before shutdown"""
        state = {
            "timestamp": datetime.now().isoformat(),
            "mode": self.current_mode,
            "active_conversations": 0,  # Would get from conversation manager
            "last_error": "Emergency shutdown triggered"
        }
        
        try:
            with open("emergency_state.json", "w") as f:
                json.dump(state, f, indent=2)
            logger.info("Emergency state saved")
        except Exception as e:
            logger.error(f"Failed to save emergency state: {e}")
    
    async def broadcast_system_message(self, message: str, level: str = "info"):
        """Broadcast message to all connected clients"""
        # This would integrate with the WebSocket system
        logger.info(f"Broadcasting system message: {message}")
        # In production, this would emit to all WebSocket connections
    
    def get_fallback_response(self, query: str) -> Optional[Dict]:
        """Get a fallback response for a query"""
        # Simple matching - in production this would be more sophisticated
        for key, conversation in self.fallback_conversations.items():
            if any(word in query.lower() for word in key.split('_')):
                return conversation
        
        # Default fallback
        return {
            "query": query,
            "responses": [
                {
                    "agent": "sarah",
                    "message": "I understand you're looking for marketing guidance. While we're experiencing some technical limitations, I can share that successful financial services marketing requires a balance of trust-building, compliance, and innovation. Let's focus on your core objectives and work within proven frameworks.",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
    
    def is_in_emergency_mode(self) -> bool:
        """Check if system is in any emergency mode"""
        return self.current_mode != "normal"
    
    def get_current_mode(self) -> Dict[str, Any]:
        """Get current emergency mode status"""
        return {
            "mode": self.current_mode,
            "is_emergency": self.is_in_emergency_mode(),
            "available_modes": list(self.recovery_modes.keys()),
            "restrictions": self._get_mode_restrictions()
        }
    
    def _get_mode_restrictions(self) -> Dict[str, bool]:
        """Get restrictions for current mode"""
        restrictions = {
            "normal": {
                "api_calls_allowed": True,
                "all_agents_active": True,
                "real_time_data": True,
                "full_conversations": True
            },
            "demo_safe": {
                "api_calls_allowed": False,
                "all_agents_active": True,
                "real_time_data": False,
                "full_conversations": False
            },
            "api_fallback": {
                "api_calls_allowed": False,
                "all_agents_active": True,
                "real_time_data": False,
                "full_conversations": True
            },
            "minimal": {
                "api_calls_allowed": True,
                "all_agents_active": False,
                "real_time_data": True,
                "full_conversations": False
            }
        }
        
        return restrictions.get(self.current_mode, restrictions["normal"])