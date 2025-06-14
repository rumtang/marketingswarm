"""
Caching module for performance optimization
Implements in-memory caching with TTL for patient data and API responses
"""

import time
import asyncio
from typing import Dict, Any, Optional, Callable, TypeVar, List
from datetime import datetime, timedelta
import logging
from functools import wraps
import json
import hashlib

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CacheEntry:
    """Represents a single cache entry with TTL"""
    def __init__(self, value: Any, ttl_seconds: int):
        self.value = value
        self.created_at = time.time()
        self.ttl_seconds = ttl_seconds
        
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        return time.time() - self.created_at > self.ttl_seconds
        
    def time_remaining(self) -> float:
        """Get seconds remaining before expiry"""
        return max(0, self.ttl_seconds - (time.time() - self.created_at))


class InMemoryCache:
    """
    Thread-safe in-memory cache with TTL support
    """
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "sets": 0
        }
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        async with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if not entry.is_expired():
                    self._stats["hits"] += 1
                    logger.debug(f"Cache hit for key: {key}")
                    return entry.value
                else:
                    # Remove expired entry
                    del self._cache[key]
                    self._stats["evictions"] += 1
                    
            self._stats["misses"] += 1
            logger.debug(f"Cache miss for key: {key}")
            return None
            
    async def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Set value in cache with TTL (default 5 minutes)"""
        async with self._lock:
            self._cache[key] = CacheEntry(value, ttl_seconds)
            self._stats["sets"] += 1
            logger.debug(f"Cache set for key: {key}, TTL: {ttl_seconds}s")
            
    async def delete(self, key: str):
        """Remove key from cache"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                
    async def clear(self):
        """Clear all cache entries"""
        async with self._lock:
            self._cache.clear()
            logger.info("Cache cleared")
            
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        async with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0
            
            return {
                **self._stats,
                "size": len(self._cache),
                "hit_rate": hit_rate,
                "total_requests": total_requests
            }
            
    async def cleanup_expired(self):
        """Remove all expired entries"""
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items() 
                if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
                self._stats["evictions"] += 1
                
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")


class PatientCache:
    """
    Specialized cache for patient data with batch operations
    """
    def __init__(self, cache: InMemoryCache):
        self.cache = cache
        self.patient_prefix = "patient:"
        self.batch_prefix = "batch:patients:"
        
    async def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Get single patient from cache"""
        return await self.cache.get(f"{self.patient_prefix}{patient_id}")
        
    async def set_patient(self, patient_id: str, data: Dict[str, Any], ttl: int = 300):
        """Cache single patient data"""
        await self.cache.set(f"{self.patient_prefix}{patient_id}", data, ttl)
        
    async def get_patients_batch(self, patient_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get multiple patients, returning cached ones and IDs that need fetching"""
        result = {}
        missing_ids = []
        
        for patient_id in patient_ids:
            cached = await self.get_patient(patient_id)
            if cached:
                result[patient_id] = cached
            else:
                missing_ids.append(patient_id)
                
        return result, missing_ids
        
    async def set_patients_batch(self, patients: Dict[str, Dict[str, Any]], ttl: int = 300):
        """Cache multiple patients at once"""
        for patient_id, data in patients.items():
            await self.set_patient(patient_id, data, ttl)
            
    async def invalidate_patient(self, patient_id: str):
        """Remove patient from cache"""
        await self.cache.delete(f"{self.patient_prefix}{patient_id}")


class APICache:
    """
    Cache for API responses with request-based keys
    """
    def __init__(self, cache: InMemoryCache):
        self.cache = cache
        self.api_prefix = "api:"
        
    def _generate_key(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Generate cache key from endpoint and parameters"""
        key_data = {"endpoint": endpoint}
        if params:
            key_data.update(params)
            
        # Create deterministic key from parameters
        key_str = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()[:8]
        return f"{self.api_prefix}{endpoint}:{key_hash}"
        
    async def get_response(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """Get cached API response"""
        key = self._generate_key(endpoint, params)
        return await self.cache.get(key)
        
    async def set_response(self, endpoint: str, response: Any, 
                          params: Optional[Dict[str, Any]] = None, ttl: int = 60):
        """Cache API response (default 60 seconds)"""
        key = self._generate_key(endpoint, params)
        await self.cache.set(key, response, ttl)


def cached_api_response(ttl: int = 60):
    """
    Decorator for caching API endpoint responses
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request info for cache key
            request = kwargs.get('request') or (args[0] if args else None)
            if not request:
                return await func(*args, **kwargs)
                
            # Generate cache key
            endpoint = request.url.path
            params = dict(request.query_params)
            
            # Check cache
            cached = await api_cache.get_response(endpoint, params)
            if cached is not None:
                logger.info(f"Returning cached response for {endpoint}")
                return cached
                
            # Call original function
            response = await func(*args, **kwargs)
            
            # Cache successful responses
            if response and getattr(response, 'status_code', 200) == 200:
                await api_cache.set_response(endpoint, response, params, ttl)
                
            return response
            
        return wrapper
    return decorator


# Global cache instances
_main_cache = InMemoryCache()
patient_cache = PatientCache(_main_cache)
api_cache = APICache(_main_cache)


async def get_cache_stats() -> Dict[str, Any]:
    """Get global cache statistics"""
    return await _main_cache.get_stats()


async def clear_all_caches():
    """Clear all caches"""
    await _main_cache.clear()


# Background task to cleanup expired entries periodically
async def cache_cleanup_task():
    """Run periodic cache cleanup"""
    while True:
        await asyncio.sleep(300)  # Run every 5 minutes
        await _main_cache.cleanup_expired()