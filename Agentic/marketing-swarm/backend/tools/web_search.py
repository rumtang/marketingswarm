"""
Web Search Tool Module
Provides real-time web search capabilities for agents using OpenAI
"""

import os
import time
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import hashlib
import json
from loguru import logger
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from safety.budget_guard import BudgetGuard
from tools.data_cache import DataCache
from tools.rate_limiter import RateLimiter

class AgentWebSearchTool:
    """Web search tool with caching, rate limiting, and budget control"""
    
    def __init__(self, agent_specialty: str, openai_api_key: str):
        self.specialty = agent_specialty
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.cache = DataCache()
        self.rate_limiter = RateLimiter()
        self.budget_guard = BudgetGuard()
        
        # Search configuration based on agent specialty
        self.search_config = self._get_search_config()
        
    def _get_search_config(self) -> Dict:
        """Get search configuration based on agent specialty"""
        configs = {
            "brand strategy financial services": {
                "focus_areas": ["brand positioning", "competitive analysis", "market trends"],
                "sources": ["industry reports", "competitor websites", "financial news"],
                "recency_priority": "high"
            },
            "digital campaign manager": {
                "focus_areas": ["ad performance", "platform updates", "cost benchmarks"],
                "sources": ["ad platforms", "marketing blogs", "industry benchmarks"],
                "recency_priority": "very high"
            },
            "content marketing specialist": {
                "focus_areas": ["content trends", "SEO updates", "engagement metrics"],
                "sources": ["content marketing blogs", "SEO tools", "social media"],
                "recency_priority": "high"
            },
            "customer experience designer": {
                "focus_areas": ["UX trends", "conversion optimization", "user behavior"],
                "sources": ["UX research", "design blogs", "case studies"],
                "recency_priority": "medium"
            },
            "marketing analytics manager": {
                "focus_areas": ["measurement standards", "privacy regulations", "KPIs"],
                "sources": ["analytics platforms", "regulatory sites", "research papers"],
                "recency_priority": "high"
            },
            "growth marketing lead": {
                "focus_areas": ["growth tactics", "acquisition channels", "viral mechanics"],
                "sources": ["growth blogs", "startup case studies", "marketing forums"],
                "recency_priority": "very high"
            }
        }
        
        # Return matching config or default
        for key, config in configs.items():
            if key in self.specialty.lower():
                return config
        
        return {
            "focus_areas": ["general marketing", "financial services"],
            "sources": ["general web"],
            "recency_priority": "medium"
        }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def search_current_data(
        self, 
        query: str, 
        context: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search for current data relevant to agent's expertise"""
        
        # Check rate limits
        can_proceed, wait_time = await self.rate_limiter.check_rate_limit("web_search")
        if not can_proceed:
            logger.warning(f"Rate limit hit, waiting {wait_time}s")
            await asyncio.sleep(wait_time)
        
        # Check budget
        budget_ok, budget_msg = await self.budget_guard.check_budget_before_search(0.10)
        if not budget_ok:
            logger.warning(f"Budget check failed: {budget_msg}")
            return self._get_fallback_response(query, "budget_exceeded")
        
        # Create specialized query
        specialized_query = self._create_specialized_query(query, context)
        
        # Check cache first
        cache_key = self._generate_cache_key(specialized_query)
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for query: {query[:50]}...")
            return cached_result
        
        try:
            # Perform web search
            result = await self._perform_web_search(specialized_query, session_id)
            
            # Cache the result
            await self.cache.set(cache_key, result, ttl=300)  # 5 minute cache
            
            # Record usage
            await self.budget_guard.record_api_usage(
                0.10, 
                "search", 
                session_id=session_id,
                agent_name=self.specialty
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return self._get_fallback_response(query, "search_error", str(e))
    
    async def _perform_web_search(self, query: str, session_id: Optional[str]) -> Dict[str, Any]:
        """Perform actual web search using OpenAI"""
        start_time = time.time()
        
        try:
            # Construct search-optimized prompt
            system_prompt = f"""You are a {self.specialty} expert performing targeted web research.
Focus on: {', '.join(self.search_config['focus_areas'])}
Prioritize: {', '.join(self.search_config['sources'])}
Recency: {self.search_config['recency_priority']} priority for recent information (2024-2025)

Provide factual, current information with specific dates, numbers, and sources when available."""

            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Search for current information about: {query}"}
                ],
                temperature=0.3,  # Lower temperature for factual searches
                max_tokens=800,
                tools=[{"type": "web_search"}],
                tool_choice="auto"
            )
            
            # Extract search results
            search_time = time.time() - start_time
            
            return {
                "query": query,
                "results": response.choices[0].message.content,
                "search_time": round(search_time, 2),
                "timestamp": datetime.now().isoformat(),
                "specialty": self.specialty,
                "has_current_data": True
            }
            
        except Exception as e:
            logger.error(f"OpenAI search error: {e}")
            raise
    
    def _create_specialized_query(self, query: str, context: Optional[str]) -> str:
        """Create a specialized search query based on agent expertise"""
        # Add temporal context
        current_year = datetime.now().year
        temporal_context = f"current {current_year} latest"
        
        # Add specialty context
        specialty_keywords = self.search_config['focus_areas'][0]
        
        # Add industry context
        industry_context = "financial services fintech"
        
        # Combine into optimized query
        specialized_query = f"{temporal_context} {specialty_keywords} {industry_context} {query}"
        
        # Add specific context if provided
        if context:
            specialized_query += f" in context of {context}"
        
        return specialized_query
    
    def _generate_cache_key(self, query: str) -> str:
        """Generate a cache key for the query"""
        # Include specialty and date in cache key
        key_components = [
            self.specialty,
            query,
            datetime.now().strftime("%Y-%m-%d-%H")  # Hour-level caching
        ]
        key_string = "|".join(key_components)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_fallback_response(self, query: str, reason: str, error: Optional[str] = None) -> Dict[str, Any]:
        """Get fallback response when search fails"""
        fallback_messages = {
            "budget_exceeded": "Using cached market insights due to budget constraints",
            "rate_limited": "Using recent search results due to rate limiting",
            "search_error": "Using representative data due to search issues",
            "api_error": "Using fallback data due to API limitations"
        }
        
        # Get relevant fallback data based on specialty
        fallback_data = self._get_specialty_fallback_data(query)
        
        return {
            "query": query,
            "results": f"{fallback_messages.get(reason, 'Using fallback data')}. {fallback_data}",
            "search_time": 0,
            "timestamp": datetime.now().isoformat(),
            "specialty": self.specialty,
            "has_current_data": False,
            "fallback_reason": reason,
            "error": error
        }
    
    def _get_specialty_fallback_data(self, query: str) -> str:
        """Get specialty-specific fallback data"""
        fallback_responses = {
            "brand strategy": """Based on recent financial services branding trends:
- Trust and security remain paramount in brand messaging
- Digital-first positioning is now table stakes
- ESG considerations increasingly influence brand perception
- Personalization at scale is the key differentiator""",
            
            "digital campaign": """Current digital advertising landscape:
- Financial services CPCs range from $3-8 depending on product
- Video content showing 40% higher engagement rates
- Mobile-first campaigns essential (70%+ traffic)
- Privacy changes require first-party data strategies""",
            
            "content marketing": """Content marketing best practices:
- Educational content drives 3x more engagement
- Video explainers crucial for complex products
- SEO focusing on intent-based keywords
- Compliance-approved content libraries essential""",
            
            "customer experience": """UX trends in financial services:
- Biometric authentication becoming standard
- One-click actions for common tasks
- Progressive disclosure for complex products
- Accessibility compliance non-negotiable""",
            
            "marketing analytics": """Analytics standards:
- Multi-touch attribution still challenging
- Privacy-safe measurement solutions emerging
- Real-time dashboards expected by stakeholders
- Predictive analytics for churn prevention""",
            
            "growth marketing": """Growth tactics in fintech:
- Referral programs averaging 25% of new acquisitions
- Embedded finance partnerships accelerating
- Community-led growth strategies emerging
- Product-led growth for B2B fintech"""
        }
        
        # Find matching fallback
        for key, response in fallback_responses.items():
            if key in self.specialty.lower():
                return response
        
        return "Using general market insights based on recent industry trends."
    
    async def get_competitor_intelligence(self, competitor: str) -> Dict[str, Any]:
        """Specialized method for competitive intelligence"""
        query = f"latest marketing campaigns strategies {competitor} financial services"
        return await self.search_current_data(query, context="competitive analysis")
    
    async def get_trend_analysis(self, trend_topic: str) -> Dict[str, Any]:
        """Specialized method for trend analysis"""
        query = f"emerging trends {trend_topic} financial services marketing {datetime.now().year}"
        return await self.search_current_data(query, context="trend analysis")
    
    async def get_regulatory_updates(self) -> Dict[str, Any]:
        """Specialized method for regulatory updates"""
        query = f"latest SEC FINRA marketing compliance updates financial services {datetime.now().year}"
        return await self.search_current_data(query, context="regulatory compliance")