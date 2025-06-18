"""
Rate Limiter Module
Prevents API abuse and ensures fair usage
"""

import time
import asyncio
from typing import Dict, Tuple, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
from loguru import logger

class RateLimiter:
    """Token bucket rate limiter for API calls"""
    
    def __init__(self):
        # Rate limit configurations
        self.limits = {
            "web_search": {
                "tokens": 60,  # Max tokens
                "refill_rate": 1,  # Tokens per second
                "max_tokens": 60  # Bucket capacity
            },
            "completion": {
                "tokens": 100,
                "refill_rate": 2,
                "max_tokens": 100
            },
            "conversation": {
                "tokens": 20,
                "refill_rate": 0.5,
                "max_tokens": 20
            }
        }
        
        # Token buckets
        self.buckets = defaultdict(lambda: {
            "tokens": 0,
            "last_refill": time.time()
        })
        
        # Initialize buckets
        for limit_type, config in self.limits.items():
            self.buckets[limit_type] = {
                "tokens": config["max_tokens"],
                "last_refill": time.time()
            }
        
        # Track rate limit hits
        self.rate_limit_stats = defaultdict(int)
        
    async def check_rate_limit(self, limit_type: str, tokens_needed: int = 1) -> Tuple[bool, float]:
        """
        Check if request can proceed under rate limit
        Returns: (can_proceed, wait_time_if_not)
        """
        if limit_type not in self.limits:
            logger.warning(f"Unknown rate limit type: {limit_type}")
            return True, 0
        
        config = self.limits[limit_type]
        bucket = self.buckets[limit_type]
        
        # Refill tokens based on time elapsed
        current_time = time.time()
        time_elapsed = current_time - bucket["last_refill"]
        tokens_to_add = time_elapsed * config["refill_rate"]
        
        # Update bucket
        bucket["tokens"] = min(
            bucket["tokens"] + tokens_to_add,
            config["max_tokens"]
        )
        bucket["last_refill"] = current_time
        
        # Check if we have enough tokens
        if bucket["tokens"] >= tokens_needed:
            bucket["tokens"] -= tokens_needed
            return True, 0
        else:
            # Calculate wait time
            tokens_short = tokens_needed - bucket["tokens"]
            wait_time = tokens_short / config["refill_rate"]
            
            self.rate_limit_stats[limit_type] += 1
            logger.warning(
                f"Rate limit hit for {limit_type}: "
                f"need {tokens_needed} tokens, have {bucket['tokens']:.2f}, "
                f"wait {wait_time:.2f}s"
            )
            
            return False, wait_time
    
    async def wait_if_needed(self, limit_type: str, tokens_needed: int = 1) -> bool:
        """Wait if rate limited and then proceed"""
        can_proceed, wait_time = await self.check_rate_limit(limit_type, tokens_needed)
        
        if not can_proceed and wait_time > 0:
            logger.info(f"Rate limited - waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
            # Check again after waiting
            can_proceed, _ = await self.check_rate_limit(limit_type, tokens_needed)
        
        return can_proceed
    
    def get_current_capacity(self, limit_type: str) -> Dict[str, float]:
        """Get current capacity for a rate limit type"""
        if limit_type not in self.limits:
            return {"error": "Unknown limit type"}
        
        config = self.limits[limit_type]
        bucket = self.buckets[limit_type]
        
        # Calculate current tokens with refill
        current_time = time.time()
        time_elapsed = current_time - bucket["last_refill"]
        tokens_to_add = time_elapsed * config["refill_rate"]
        current_tokens = min(
            bucket["tokens"] + tokens_to_add,
            config["max_tokens"]
        )
        
        return {
            "current_tokens": round(current_tokens, 2),
            "max_tokens": config["max_tokens"],
            "refill_rate": config["refill_rate"],
            "percentage": round((current_tokens / config["max_tokens"]) * 100, 1)
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        stats = {
            "rate_limit_hits": dict(self.rate_limit_stats),
            "current_capacity": {}
        }
        
        for limit_type in self.limits:
            stats["current_capacity"][limit_type] = self.get_current_capacity(limit_type)
        
        return stats
    
    def reset_bucket(self, limit_type: str):
        """Reset a specific bucket to full capacity"""
        if limit_type in self.limits:
            config = self.limits[limit_type]
            self.buckets[limit_type] = {
                "tokens": config["max_tokens"],
                "last_refill": time.time()
            }
            logger.info(f"Reset rate limit bucket for {limit_type}")
    
    def is_configured(self) -> bool:
        """Check if rate limiter is properly configured"""
        return len(self.limits) > 0 and all(
            config["max_tokens"] > 0 and config["refill_rate"] > 0
            for config in self.limits.values()
        )
    
    def set_custom_limit(self, limit_type: str, max_tokens: int, refill_rate: float):
        """Set a custom rate limit"""
        self.limits[limit_type] = {
            "tokens": max_tokens,
            "refill_rate": refill_rate,
            "max_tokens": max_tokens
        }
        
        # Initialize bucket
        self.buckets[limit_type] = {
            "tokens": max_tokens,
            "last_refill": time.time()
        }
        
        logger.info(
            f"Set custom rate limit for {limit_type}: "
            f"{max_tokens} tokens, {refill_rate} tokens/s"
        )

# Per-user rate limiting
class UserRateLimiter:
    """Rate limiter for per-user request limiting"""
    
    def __init__(self):
        self.user_requests = defaultdict(list)
        self.limits = {
            "requests_per_minute": 20,
            "requests_per_hour": 200,
            "requests_per_day": 1000
        }
    
    async def check_user_limit(self, user_id: str) -> Tuple[bool, Optional[str]]:
        """Check if user is within rate limits"""
        now = datetime.now()
        
        # Clean old requests
        self._clean_old_requests(user_id)
        
        # Get user's request timestamps
        user_timestamps = self.user_requests[user_id]
        
        # Check per-minute limit
        minute_ago = now - timedelta(minutes=1)
        recent_minute = [ts for ts in user_timestamps if ts > minute_ago]
        if len(recent_minute) >= self.limits["requests_per_minute"]:
            return False, f"Rate limit exceeded: {self.limits['requests_per_minute']} requests per minute"
        
        # Check per-hour limit
        hour_ago = now - timedelta(hours=1)
        recent_hour = [ts for ts in user_timestamps if ts > hour_ago]
        if len(recent_hour) >= self.limits["requests_per_hour"]:
            return False, f"Rate limit exceeded: {self.limits['requests_per_hour']} requests per hour"
        
        # Check per-day limit
        day_ago = now - timedelta(days=1)
        recent_day = [ts for ts in user_timestamps if ts > day_ago]
        if len(recent_day) >= self.limits["requests_per_day"]:
            return False, f"Rate limit exceeded: {self.limits['requests_per_day']} requests per day"
        
        # Record this request
        user_timestamps.append(now)
        
        return True, None
    
    def _clean_old_requests(self, user_id: str):
        """Remove request timestamps older than 24 hours"""
        day_ago = datetime.now() - timedelta(days=1)
        self.user_requests[user_id] = [
            ts for ts in self.user_requests[user_id]
            if ts > day_ago
        ]
    
    def get_user_stats(self, user_id: str) -> Dict[str, int]:
        """Get usage statistics for a user"""
        self._clean_old_requests(user_id)
        
        now = datetime.now()
        user_timestamps = self.user_requests[user_id]
        
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        return {
            "requests_last_minute": len([ts for ts in user_timestamps if ts > minute_ago]),
            "requests_last_hour": len([ts for ts in user_timestamps if ts > hour_ago]),
            "requests_last_day": len(user_timestamps),
            "limits": self.limits
        }