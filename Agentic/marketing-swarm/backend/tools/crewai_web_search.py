"""
CrewAI-Compatible Web Search Tool
Provides web search capabilities in CrewAI format
"""

import os
import time
import json
import hashlib
from typing import Type, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from openai import OpenAI
from loguru import logger

from safety.budget_guard import BudgetGuard
from tools.data_cache import DataCache
from tools.rate_limiter import RateLimiter


class WebSearchInput(BaseModel):
    """Input schema for web search tool"""
    query: str = Field(description="The search query")
    context: Optional[str] = Field(default="", description="Additional context for the search")
    specialty: Optional[str] = Field(default="general", description="Agent specialty for focused search")


class CrewAIWebSearchTool(BaseTool):
    """Web search tool compatible with CrewAI framework"""
    
    name: str = "web_search"
    description: str = "Search for current market data, trends, and financial services information"
    args_schema: Type[BaseModel] = WebSearchInput
    
    def __init__(self, agent_specialty: str = "general", **kwargs):
        # Set the specialty before calling parent init
        self._specialty = agent_specialty
        super().__init__(**kwargs)
    
    def _get_search_config(self) -> dict:
        """Get search configuration based on agent specialty"""
        configs = {
            "brand strategy": {
                "focus_areas": ["brand positioning", "competitive analysis", "market trends"],
                "sources": ["industry reports", "competitor websites", "financial news"],
                "recency_priority": "high"
            },
            "digital campaign": {
                "focus_areas": ["ad performance", "platform updates", "cost benchmarks"],
                "sources": ["ad platforms", "marketing blogs", "industry benchmarks"],
                "recency_priority": "very high"
            },
            "content marketing": {
                "focus_areas": ["content trends", "SEO updates", "engagement metrics"],
                "sources": ["content marketing blogs", "SEO tools", "social media"],
                "recency_priority": "high"
            },
            "customer experience": {
                "focus_areas": ["UX trends", "conversion optimization", "user behavior"],
                "sources": ["UX research", "design blogs", "case studies"],
                "recency_priority": "medium"
            },
            "marketing analytics": {
                "focus_areas": ["measurement standards", "privacy regulations", "KPIs"],
                "sources": ["analytics platforms", "regulatory sites", "research papers"],
                "recency_priority": "high"
            },
            "growth marketing": {
                "focus_areas": ["growth tactics", "acquisition channels", "viral mechanics"],
                "sources": ["growth blogs", "startup case studies", "marketing forums"],
                "recency_priority": "very high"
            }
        }
        
        # Find matching config
        for key, config in configs.items():
            if key in self._specialty.lower():
                return config
        
        # Default config
        return {
            "focus_areas": ["general marketing", "financial services"],
            "sources": ["general web"],
            "recency_priority": "medium"
        }
    
    def _run(self, query: str, context: str = "", specialty: str = "") -> str:
        """
        Execute the web search tool.
        
        Args:
            query: The search query
            context: Additional context for the search
            specialty: Override the default specialty if needed
            
        Returns:
            Search results as a string
        """
        try:
            # Initialize tools on first use
            if not hasattr(self, '_client'):
                self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                self._cache = DataCache()
                self._rate_limiter = RateLimiter()
                self._budget_guard = BudgetGuard()
                self._search_config = self._get_search_config()
            
            # Use provided specialty or default
            search_specialty = specialty or self._specialty
            
            # Check rate limits (simplified for sync)
            can_proceed, wait_time = self._rate_limiter.check_rate_limit_sync("web_search")
            if not can_proceed:
                logger.warning(f"Rate limit hit, waiting {wait_time}s")
                time.sleep(wait_time)
            
            # Check budget (simplified for sync)
            budget_ok, budget_msg = self._budget_guard.check_budget_sync(0.10)
            if not budget_ok:
                logger.warning(f"Budget check failed: {budget_msg}")
                return f"Budget limit exceeded: {budget_msg}"
            
            # Create cache key
            cache_key = self._generate_cache_key(query, context, search_specialty)
            
            # Check cache (simplified sync version)
            cached_result = self._cache.get_sync(cache_key)
            if cached_result:
                logger.info(f"Cache hit for query: {query[:50]}...")
                return cached_result
            
            # Perform search
            result = self._perform_search(query, context, search_specialty)
            
            # Cache result
            self._cache.set_sync(cache_key, result, ttl=300)
            
            # Record usage
            self._budget_guard.record_usage_sync(0.10, "web_search", agent_name=search_specialty)
            
            return result
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return f"Search failed: {str(e)}. Using fallback data."
    
    def _perform_search(self, query: str, context: str, specialty: str) -> str:
        """Perform the actual search using OpenAI"""
        try:
            # Build search prompt
            config = self._search_config
            system_prompt = f"""You are a {specialty} expert performing targeted research.
Focus on: {', '.join(config['focus_areas'])}
Prioritize: {', '.join(config['sources'])}
Recency: {config['recency_priority']} priority for recent information (2024-2025)

Provide factual, current information with specific dates, numbers, and sources when available.
Keep responses concise and relevant to financial services marketing."""

            user_prompt = f"Search for current information about: {query}"
            if context:
                user_prompt += f"\nContext: {context}"
            
            # Call OpenAI
            response = self._client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return self._get_fallback_response(query, specialty)
    
    def _generate_cache_key(self, query: str, context: str, specialty: str) -> str:
        """Generate a cache key for the search"""
        key_data = f"{specialty}:{query}:{context}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_fallback_response(self, query: str, specialty: str) -> str:
        """Provide fallback response when search fails"""
        fallback_responses = {
            "brand strategy": "Based on current market trends, focus on trust, transparency, and digital-first positioning in financial services.",
            "digital campaign": "Current benchmarks suggest CPCs of $3-8 for financial keywords, with LinkedIn and Google Ads as primary channels.",
            "content marketing": "Financial content performs best with educational, compliance-aware materials focusing on customer empowerment.",
            "customer experience": "Modern fintech UX emphasizes mobile-first design, simplified onboarding, and transparent fee structures.",
            "marketing analytics": "Key metrics include CAC, LTV, activation rate, and regulatory compliance tracking.",
            "growth marketing": "Referral programs and content-led growth strategies are showing strong results in fintech."
        }
        
        for key, response in fallback_responses.items():
            if key in specialty.lower():
                return f"[Fallback Data] {response}"
        
        return f"[Fallback Data] Unable to fetch current data for '{query}'. Please try again later."


# Simplified sync methods for cache and budget guard
def add_sync_methods():
    """Add synchronous methods to async classes for CrewAI compatibility"""
    
    # Add to DataCache
    def get_sync(self, key: str) -> Optional[Any]:
        """Synchronous cache get"""
        if key in self.local_cache:
            entry = self.local_cache[key]
            if entry["expires"] > datetime.now():
                self.cache_stats["hits"] += 1
                return entry["value"]
        self.cache_stats["misses"] += 1
        return None
    
    def set_sync(self, key: str, value: Any, ttl: int = 300):
        """Synchronous cache set"""
        from datetime import timedelta
        self.local_cache[key] = {
            "value": value,
            "expires": datetime.now() + timedelta(seconds=ttl)
        }
        self._cleanup_local_cache()
    
    # Add to RateLimiter
    def check_rate_limit_sync(self, endpoint: str) -> tuple[bool, float]:
        """Synchronous rate limit check"""
        import time
        
        if endpoint not in self.limits:
            return True, 0
        
        current_time = time.time()
        bucket = self.buckets[endpoint]
        
        # Refill tokens
        time_passed = current_time - bucket["last_refill"]
        tokens_to_add = time_passed * bucket["refill_rate"]
        bucket["tokens"] = min(bucket["max_tokens"], bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = current_time
        
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True, 0
        else:
            wait_time = (1 - bucket["tokens"]) / bucket["refill_rate"]
            return False, wait_time
    
    # Add to BudgetGuard
    def check_budget_sync(self, estimated_cost: float) -> tuple[bool, str]:
        """Synchronous budget check"""
        if self.daily_spend + estimated_cost > self.daily_budget:
            return False, "Daily budget exceeded"
        if self.session_searches >= self.max_searches_per_session:
            return False, "Session search limit reached"
        return True, "OK"
    
    def record_usage_sync(self, cost: float, operation: str, **kwargs):
        """Synchronous usage recording"""
        self.daily_spend += cost
        self.session_searches += 1
        self.usage_history.append({
            "timestamp": datetime.now(),
            "cost": cost,
            "operation": operation,
            **kwargs
        })
    
    # Monkey patch the methods
    DataCache.get_sync = get_sync
    DataCache.set_sync = set_sync
    DataCache._cleanup_local_cache = DataCache._cleanup_local_cache
    
    RateLimiter.check_rate_limit_sync = check_rate_limit_sync
    
    BudgetGuard.check_budget_sync = check_budget_sync
    BudgetGuard.record_usage_sync = record_usage_sync


# Apply sync methods when module loads
add_sync_methods()