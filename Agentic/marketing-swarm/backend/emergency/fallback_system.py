"""
Fallback System Manager
Provides fallback responses and data when primary systems fail
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger

class FallbackManager:
    """Manages fallback responses and cached data"""
    
    def __init__(self):
        self.is_active = False
        self.fallback_responses = self._load_fallback_responses()
        self.demo_scenarios = self._load_demo_scenarios()
        self.cached_responses = {}
        
    async def activate(self):
        """Activate fallback mode"""
        self.is_active = True
        os.environ["FALLBACK_MODE_ACTIVE"] = "true"
        logger.warning("Fallback mode activated")
        
    async def deactivate(self):
        """Deactivate fallback mode"""
        self.is_active = False
        os.environ["FALLBACK_MODE_ACTIVE"] = "false"
        logger.info("Fallback mode deactivated")
    
    def is_ready(self) -> bool:
        """Check if fallback system is ready"""
        return len(self.fallback_responses) > 0 and len(self.demo_scenarios) > 0
    
    def _load_fallback_responses(self) -> Dict[str, List[Dict]]:
        """Load pre-crafted fallback responses"""
        return {
            "general_marketing": [
                {
                    "agent": "sarah",
                    "response": "In financial services marketing, trust is your most valuable currency. Focus on transparency, social proof, and demonstrating expertise through educational content. Your brand promise should address both functional benefits and emotional security."
                },
                {
                    "agent": "marcus",
                    "response": "For financial services campaigns, expect CPCs between $3-8 depending on the product. Start with targeted audiences who show financial intent signals. Test messaging that balances urgency with trust. Compliance review will add 2-3 days to campaign launch."
                },
                {
                    "agent": "elena",
                    "response": "Financial content that performs best includes calculators, comparison guides, and myth-busting articles. Video explainers for complex products see 3x higher engagement. Always include disclaimers and ensure content is educational, not advisory."
                }
            ],
            "robo_advisor": [
                {
                    "agent": "sarah",
                    "response": "Robo-advisors must differentiate beyond just low fees. Consider positioning around personalization, values-based investing, or integration with broader financial planning. Young professionals and mass affluent segments show highest adoption rates."
                },
                {
                    "agent": "david",
                    "response": "Robo-advisor onboarding should take under 10 minutes with progressive disclosure. Show projected outcomes early, use social proof throughout, and make risk tolerance questions engaging. Mobile-first is essential - 70% start on mobile devices."
                },
                {
                    "agent": "priya",
                    "response": "Track cohort retention carefully - successful robo-advisors see 85%+ retention at 12 months. Key metrics: funded accounts (not just signups), average account size, and contribution frequency. Attribution is complex due to long consideration cycles."
                }
            ],
            "acquisition_cost": [
                {
                    "agent": "marcus",
                    "response": "High CAC usually stems from: 1) Broad targeting, 2) Weak landing pages, 3) Complex products, 4) Long sales cycles. Quick wins: Refine audiences, improve page load speed, add trust signals, and implement retargeting for abandoned signups."
                },
                {
                    "agent": "alex",
                    "response": "Reduce CAC through product-led growth: Free tools that showcase value, referral programs with dual incentives, and content that naturally promotes sharing. Financial calculators and planning tools can become acquisition engines themselves."
                },
                {
                    "agent": "priya",
                    "response": "Analyze CAC by cohort and channel to find hidden efficiencies. Often 20% of keywords drive 80% of quality conversions. Also check time-to-conversion - optimizing for faster conversion can significantly reduce overall CAC."
                }
            ],
            "compliance": [
                {
                    "agent": "sarah",
                    "response": "Every financial marketing message needs compliance review. Build templates for common scenarios, maintain a disclaimer library, and establish clear guidelines for social media. Remember: education is usually safe, specific advice never is."
                },
                {
                    "agent": "elena",
                    "response": "Compliant content focuses on education over promotion. Use phrases like 'many investors' instead of 'you should.' Include required disclosures prominently. Testimonials need disclaimers about non-typical results. When in doubt, run it by legal."
                },
                {
                    "agent": "marcus",
                    "response": "Ad platforms have additional restrictions for financial services. Get whitelisted on Meta, use restricted targeting on Google. Avoid promises about returns, guarantees, or 'risk-free' language. Build pre-approved ad templates to speed launches."
                }
            ],
            "mobile_experience": [
                {
                    "agent": "david",
                    "response": "Financial services mobile UX requires balancing security with convenience. Implement biometric authentication, use progressive disclosure for complex forms, and ensure thumb-friendly tap targets. Test on real devices, not just simulators."
                },
                {
                    "agent": "elena",
                    "response": "Mobile content needs scannable formatting: bullet points, clear headings, and expandable sections for details. Interactive elements like calculators should be touch-optimized. Keep forms short - every field reduces conversion by ~7%."
                },
                {
                    "agent": "marcus",
                    "response": "Mobile campaigns need different creative than desktop. Vertical video for stories, shorter copy, and immediate value props. Mobile users have higher intent but less patience. App install campaigns can reduce long-term CAC if you nail retention."
                }
            ]
        }
    
    def _load_demo_scenarios(self) -> List[Dict[str, Any]]:
        """Load demonstration scenarios"""
        return [
            {
                "id": "robo_advisor_launch",
                "name": "Robo-Advisor Product Launch",
                "description": "Comprehensive marketing strategy for launching a new robo-advisor",
                "triggers": ["robo", "advisor", "launch", "betterment", "wealthfront"],
                "duration": 180  # seconds
            },
            {
                "id": "reduce_cac",
                "name": "Reducing Customer Acquisition Cost",
                "description": "Strategies to cut customer acquisition costs in half",
                "triggers": ["cac", "acquisition cost", "expensive", "reduce cost"],
                "duration": 150
            },
            {
                "id": "content_strategy", 
                "name": "Financial Content Marketing",
                "description": "Building trust through educational content",
                "triggers": ["content", "blog", "seo", "organic", "education"],
                "duration": 120
            },
            {
                "id": "mobile_first",
                "name": "Mobile-First Financial Services",
                "description": "Optimizing for mobile users in financial services",
                "triggers": ["mobile", "app", "responsive", "phone", "ux"],
                "duration": 120
            },
            {
                "id": "compliance_marketing",
                "name": "Compliant Financial Marketing",
                "description": "Marketing effectively within regulatory constraints",
                "triggers": ["compliance", "regulation", "sec", "finra", "legal"],
                "duration": 150
            }
        ]
    
    def get_fallback_response(self, query: str, agent: str) -> Optional[str]:
        """Get appropriate fallback response for query and agent"""
        # Determine category based on query
        category = self._categorize_query(query)
        
        # Get responses for category
        responses = self.fallback_responses.get(category, self.fallback_responses["general_marketing"])
        
        # Find response for specific agent
        for response in responses:
            if response["agent"].lower() == agent.lower():
                return response["response"]
        
        # Default response if agent not found
        return f"As {agent}, I believe we should focus on building trust and delivering value in financial services marketing."
    
    def _categorize_query(self, query: str) -> str:
        """Categorize query to select appropriate fallback responses"""
        query_lower = query.lower()
        
        if any(term in query_lower for term in ["robo", "advisor", "automated investing"]):
            return "robo_advisor"
        elif any(term in query_lower for term in ["cac", "acquisition", "cost", "expensive"]):
            return "acquisition_cost"
        elif any(term in query_lower for term in ["compliance", "regulation", "sec", "finra"]):
            return "compliance"
        elif any(term in query_lower for term in ["mobile", "app", "responsive"]):
            return "mobile_experience"
        else:
            return "general_marketing"
    
    def get_demo_scenario(self, query: str) -> Optional[Dict[str, Any]]:
        """Get matching demo scenario for query"""
        query_lower = query.lower()
        
        for scenario in self.demo_scenarios:
            if any(trigger in query_lower for trigger in scenario["triggers"]):
                return scenario
        
        return None
    
    def get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if available"""
        if cache_key in self.cached_responses:
            cached = self.cached_responses[cache_key]
            # Check if cache is still valid (1 hour)
            if (datetime.now() - cached["timestamp"]).seconds < 3600:
                return cached["response"]
        return None
    
    def cache_response(self, cache_key: str, response: Dict[str, Any]):
        """Cache a response for future use"""
        self.cached_responses[cache_key] = {
            "response": response,
            "timestamp": datetime.now()
        }
        
        # Limit cache size
        if len(self.cached_responses) > 1000:
            # Remove oldest entries
            sorted_keys = sorted(
                self.cached_responses.keys(),
                key=lambda k: self.cached_responses[k]["timestamp"]
            )
            for key in sorted_keys[:200]:  # Remove oldest 200
                del self.cached_responses[key]