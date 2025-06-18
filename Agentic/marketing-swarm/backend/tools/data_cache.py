"""
Data Cache Module
Provides caching functionality for API responses and search results
"""

import os
import json
import asyncio
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import redis.asyncio as redis
from loguru import logger

class DataCache:
    """Cache manager for API responses and search results"""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL")
        self.redis_client = None
        self.local_cache = {}  # Fallback in-memory cache
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0
        }
        
        # Initialize Redis connection if available
        if self.redis_url:
            asyncio.create_task(self._init_redis())
    
    async def _init_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed, using in-memory cache: {e}")
            self.redis_client = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            # Try Redis first
            if self.redis_client:
                value = await self.redis_client.get(key)
                if value:
                    self.cache_stats["hits"] += 1
                    return json.loads(value)
            
            # Fall back to local cache
            if key in self.local_cache:
                entry = self.local_cache[key]
                if entry["expires"] > datetime.now():
                    self.cache_stats["hits"] += 1
                    return entry["value"]
                else:
                    # Expired entry
                    del self.local_cache[key]
            
            self.cache_stats["misses"] += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL in seconds"""
        try:
            self.cache_stats["sets"] += 1
            
            # Store in Redis if available
            if self.redis_client:
                await self.redis_client.setex(
                    key,
                    ttl,
                    json.dumps(value)
                )
            
            # Also store in local cache
            self.local_cache[key] = {
                "value": value,
                "expires": datetime.now() + timedelta(seconds=ttl)
            }
            
            # Cleanup old entries
            self._cleanup_local_cache()
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    async def delete(self, key: str):
        """Delete value from cache"""
        try:
            if self.redis_client:
                await self.redis_client.delete(key)
            
            if key in self.local_cache:
                del self.local_cache[key]
                
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    async def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern"""
        try:
            if self.redis_client:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
            
            # Clear from local cache
            keys_to_delete = [k for k in self.local_cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self.local_cache[key]
                
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
    
    def _cleanup_local_cache(self):
        """Remove expired entries from local cache"""
        if len(self.local_cache) > 1000:  # Limit cache size
            # Remove expired entries
            now = datetime.now()
            expired_keys = [
                k for k, v in self.local_cache.items()
                if v["expires"] < now
            ]
            for key in expired_keys:
                del self.local_cache[key]
            
            # If still too large, remove oldest entries
            if len(self.local_cache) > 800:
                sorted_items = sorted(
                    self.local_cache.items(),
                    key=lambda x: x[1]["expires"]
                )
                # Keep newest 800 entries
                self.local_cache = dict(sorted_items[-800:])
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (
            self.cache_stats["hits"] / total_requests * 100 
            if total_requests > 0 else 0
        )
        
        stats = {
            "type": "redis" if self.redis_client else "in-memory",
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "sets": self.cache_stats["sets"],
            "hit_rate": round(hit_rate, 2),
            "local_cache_size": len(self.local_cache)
        }
        
        if self.redis_client:
            try:
                info = await self.redis_client.info()
                stats["redis_memory_used"] = info.get("used_memory_human", "unknown")
                stats["redis_connected"] = True
            except:
                stats["redis_connected"] = False
        
        return stats
    
    async def close(self):
        """Close cache connections"""
        if self.redis_client:
            await self.redis_client.close()

# Global cache clearing function
async def clear_all_caches():
    """Clear all caches system-wide"""
    cache = DataCache()
    
    try:
        # Clear Redis if available
        if cache.redis_client:
            await cache.redis_client.flushdb()
            logger.info("Redis cache cleared")
        
        # Clear local cache
        cache.local_cache.clear()
        logger.info("Local cache cleared")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to clear caches: {e}")
        return False
    finally:
        await cache.close()