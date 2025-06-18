"""
Demo Scenario Loader
Loads and manages demonstration scenarios
"""

import json
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from loguru import logger

class ScenarioLoader:
    """Loads and manages demo scenarios"""
    
    def __init__(self):
        self.scenarios = self._load_scenarios()
        
    def _load_scenarios(self) -> List[Dict[str, Any]]:
        """Load demo scenarios from configuration"""
        return [
            {
                "id": "robo_advisor_launch",
                "name": "Robo-Advisor Product Launch",
                "description": "Launch strategy for competing with Betterment",
                "query": "How should we launch our new robo-advisor to compete with Betterment?",
                "tags": ["product launch", "robo-advisor", "competitive strategy"],
                "expected_duration": 180,
                "talking_points": [
                    "Brand differentiation beyond features",
                    "Target audience segmentation", 
                    "Multi-channel campaign strategy",
                    "Content marketing approach",
                    "User experience optimization",
                    "Performance metrics and KPIs"
                ]
            },
            {
                "id": "high_cac_solution",
                "name": "Solving High Customer Acquisition Cost",
                "description": "Action plan for reducing doubled CAC",
                "query": "Our customer acquisition cost has doubled. What's our action plan?",
                "tags": ["cost optimization", "acquisition", "performance"],
                "expected_duration": 150,
                "talking_points": [
                    "Channel-by-channel CAC analysis",
                    "Immediate optimization tactics",
                    "Alternative acquisition channels",
                    "Conversion rate optimization",
                    "Referral program design",
                    "Long-term CAC reduction strategy"
                ]
            },
            {
                "id": "compliance_marketing",
                "name": "Compliant Complex Product Marketing",
                "description": "Marketing derivatives to retail investors",
                "query": "How do we market complex derivatives to retail investors compliantly?",
                "tags": ["compliance", "complex products", "education"],
                "expected_duration": 180,
                "talking_points": [
                    "Regulatory requirements overview",
                    "Educational content strategy",
                    "Risk disclosure best practices",
                    "Visual explanation techniques",
                    "Compliant advertising channels",
                    "Success measurement within constraints"
                ]
            },
            {
                "id": "gen_z_retirement",
                "name": "Gen Z Retirement Planning Content",
                "description": "Building trust with younger investors",
                "query": "We need a content strategy that builds trust with Gen Z about retirement planning.",
                "tags": ["content strategy", "demographics", "trust building"],
                "expected_duration": 150,
                "talking_points": [
                    "Gen Z financial behaviors and values",
                    "Platform and format preferences",
                    "Trust-building content themes",
                    "Influencer and community strategies",
                    "Gamification opportunities",
                    "Long-term engagement tactics"
                ]
            },
            {
                "id": "mobile_conversion",
                "name": "Mobile Conversion Optimization",
                "description": "Improving 2% mobile conversion rate",
                "query": "Our mobile app conversion rate is 2%. Industry average is 8%. Help.",
                "tags": ["mobile", "conversion", "UX optimization"],
                "expected_duration": 120,
                "talking_points": [
                    "Mobile UX audit findings",
                    "Onboarding flow optimization",
                    "Trust signals for mobile",
                    "Form simplification strategies",
                    "A/B testing priorities",
                    "Quick wins vs long-term fixes"
                ]
            },
            {
                "id": "rate_change_response",
                "name": "Interest Rate Change Marketing",
                "description": "Rapid response to rate changes",
                "query": "Interest rates just changed. How do we adjust our mortgage marketing immediately?",
                "tags": ["reactive marketing", "mortgages", "market conditions"],
                "expected_duration": 120,
                "talking_points": [
                    "Immediate messaging updates",
                    "Channel-specific adjustments",
                    "Competitor response analysis",
                    "Customer communication strategy",
                    "Landing page optimization",
                    "Performance tracking adjustments"
                ]
            }
        ]
    
    async def get_all_scenarios(self) -> List[Dict[str, Any]]:
        """Get all available scenarios"""
        return self.scenarios
    
    async def get_scenario(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific scenario by ID"""
        for scenario in self.scenarios:
            if scenario["id"] == scenario_id:
                return scenario
        return None
    
    async def find_matching_scenario(self, query: str) -> Optional[Dict[str, Any]]:
        """Find a scenario that matches the query"""
        query_lower = query.lower()
        
        # Check for exact query matches first
        for scenario in self.scenarios:
            if scenario["query"].lower() == query_lower:
                return scenario
        
        # Check for keyword matches
        for scenario in self.scenarios:
            keywords = scenario["id"].split("_") + scenario["tags"]
            if any(keyword in query_lower for keyword in keywords):
                return scenario
        
        return None
    
    def get_scenario_summary(self) -> List[Dict[str, str]]:
        """Get summary of all scenarios for display"""
        return [
            {
                "id": s["id"],
                "name": s["name"],
                "description": s["description"],
                "query": s["query"][:100] + "..." if len(s["query"]) > 100 else s["query"]
            }
            for s in self.scenarios
        ]