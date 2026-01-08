"""
Redis client setup and caching utilities for GradeMaster.
"""
import os
import json
from typing import Optional, Any, Dict, List
import redis
from redis import Redis

# Redis connection configuration from environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# Create Redis client
try:
    redis_client: Optional[Redis] = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        db=REDIS_DB,
        decode_responses=True,  # Automatically decode responses to strings
        socket_connect_timeout=5,  # 5 second timeout
        socket_timeout=5,
    )
    # Test connection
    redis_client.ping()
except (redis.ConnectionError, redis.TimeoutError) as e:
    print(f"Warning: Redis not available: {e}. App will continue without caching.")
    redis_client = None


def get_redis() -> Optional[Redis]:
    """Get Redis client instance."""
    return redis_client


def is_redis_available() -> bool:
    """Check if Redis is available and connected."""
    if redis_client is None:
        return False
    try:
        redis_client.ping()
        return True
    except:
        return False


# Cache key prefixes
CACHE_KEYS = {
    "student_weak_topics": "student:weak_topics:{student_id}:{grade_level}",
    "recent_question_ids": "student:recent_questions:{student_id}:{grade_level}",
    "student_history": "student:history:{student_id}",
    "question": "question:{question_id}",
    "quiz": "quiz:{quiz_id}",
    "mastery_status": "student:mastery:{student_id}:{grade_level}",
}


def cache_get(key: str) -> Optional[Any]:
    """Get value from Redis cache."""
    if not is_redis_available():
        return None
    
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception:
        return None


def cache_set(key: str, value: Any, ttl: int = 3600) -> bool:
    """
    Set value in Redis cache with TTL (time to live in seconds).
    
    Args:
        key: Cache key
        value: Value to cache (will be JSON serialized)
        ttl: Time to live in seconds (default 1 hour)
    
    Returns:
        True if successful, False otherwise
    """
    if not is_redis_available():
        return False
    
    try:
        json_value = json.dumps(value)
        redis_client.setex(key, ttl, json_value)
        return True
    except Exception:
        return False


def cache_delete(key: str) -> bool:
    """Delete a key from Redis cache."""
    if not is_redis_available():
        return False
    
    try:
        redis_client.delete(key)
        return True
    except Exception:
        return False


def cache_delete_pattern(pattern: str) -> int:
    """
    Delete all keys matching a pattern.
    
    Args:
        pattern: Redis key pattern (e.g., "student:*:123")
    
    Returns:
        Number of keys deleted
    """
    if not is_redis_available():
        return 0
    
    try:
        keys = redis_client.keys(pattern)
        if keys:
            return redis_client.delete(*keys)
        return 0
    except Exception:
        return 0

