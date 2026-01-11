"""
Redis cache utilities for caching student history and other frequently accessed data.
"""
import json
import redis
import os
from typing import Optional, Any
from functools import wraps

# Redis connection - use environment variable or default to localhost
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# Cache TTL (Time To Live) in seconds
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes default

# Try to connect to Redis, but don't fail if Redis is unavailable
try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2
    )
    # Test connection
    redis_client.ping()
    REDIS_AVAILABLE = True
except (redis.ConnectionError, redis.TimeoutError, Exception) as e:
    print(f"⚠️  Redis not available: {e}. Caching will be disabled.")
    redis_client = None
    REDIS_AVAILABLE = False


def get_cache_key(student_id: str, grade_level: Optional[int] = None, prefix: str = "history") -> str:
    """Generate a cache key for student history."""
    if grade_level:
        return f"{prefix}:{student_id}:grade:{grade_level}"
    return f"{prefix}:{student_id}:all"


def get_from_cache(key: str) -> Optional[Any]:
    """Get data from Redis cache."""
    if not REDIS_AVAILABLE or not redis_client:
        return None
    
    try:
        cached_data = redis_client.get(key)
        if cached_data:
            return json.loads(cached_data)
    except Exception as e:
        print(f"⚠️  Error reading from cache: {e}")
    return None


def set_cache(key: str, data: Any, ttl: int = CACHE_TTL) -> bool:
    """Store data in Redis cache."""
    if not REDIS_AVAILABLE or not redis_client:
        return False
    
    try:
        redis_client.setex(key, ttl, json.dumps(data, default=str))
        return True
    except Exception as e:
        print(f"⚠️  Error writing to cache: {e}")
    return False


def invalidate_student_cache(student_id: str) -> bool:
    """
    Invalidate all cache entries for a student.
    This includes history, mastery status, recent questions, and admin views.
    """
    if not REDIS_AVAILABLE or not redis_client:
        return False
    
    try:
        # Find all keys matching various student patterns
        patterns = [
            f"history:{student_id}:*",
            f"admin_history:{student_id}:*",
            f"mastery:{student_id}:*",
            f"recent_questions:{student_id}:*"  # Critical: invalidate recent questions cache
        ]
        
        all_keys = []
        for pattern in patterns:
            keys = redis_client.keys(pattern)
            if keys:
                all_keys.extend(keys)
        
        # Also invalidate admin student list (since stats changed)
        admin_list_key = "admin:students:list"
        if redis_client.exists(admin_list_key):
            all_keys.append(admin_list_key)
        
        if all_keys:
            redis_client.delete(*all_keys)
        return True
    except Exception as e:
        print(f"⚠️  Error invalidating cache: {e}")
    return False


def invalidate_all_cache() -> bool:
    """Invalidate all cache entries (use with caution)."""
    if not REDIS_AVAILABLE or not redis_client:
        return False
    
    try:
        redis_client.flushdb()
        return True
    except Exception as e:
        print(f"⚠️  Error flushing cache: {e}")
    return False


def cache_decorator(ttl: int = CACHE_TTL, key_prefix: str = "cache"):
    """
    Decorator to cache function results.
    
    Usage:
        @cache_decorator(ttl=300, key_prefix="history")
        def get_student_history(student_id: str, grade_level: int = None):
            # ... function implementation
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key_parts = [key_prefix, func.__name__]
            
            # Add args and kwargs to cache key
            for arg in args:
                if isinstance(arg, (str, int, float)):
                    cache_key_parts.append(str(arg))
            
            for k, v in sorted(kwargs.items()):
                if isinstance(v, (str, int, float, type(None))):
                    cache_key_parts.append(f"{k}:{v}")
            
            cache_key = ":".join(cache_key_parts)
            
            # Try to get from cache
            cached_result = get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            set_cache(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator
