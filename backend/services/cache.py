"""
Redis caching service for Recipe App
Provides caching layer to reduce database load for 1000+ concurrent users
"""

import redis
import json
import logging
from functools import wraps
from typing import Any, Optional, Union
import hashlib

logger = logging.getLogger(__name__)

# Redis client configuration
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True,
    max_connections=100,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True
)

def cache_result(expire_time: int = 300, key_prefix: str = ""):
    """
    Decorator to cache function results in Redis
    
    Args:
        expire_time: Cache expiration time in seconds (default: 5 minutes)
        key_prefix: Prefix for cache keys
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = generate_cache_key(func.__name__, args, kwargs, key_prefix)
            
            try:
                # Try to get from cache
                cached = redis_client.get(cache_key)
                if cached:
                    logger.debug(f"Cache HIT for {cache_key}")
                    return json.loads(cached)
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                if result is not None:
                    redis_client.setex(cache_key, expire_time, json.dumps(result, default=str))
                    logger.debug(f"Cache SET for {cache_key}")
                
                return result
                
            except redis.RedisError as e:
                logger.warning(f"Redis error for {cache_key}: {e}")
                # Fallback to function execution
                return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = generate_cache_key(func.__name__, args, kwargs, key_prefix)
            
            try:
                # Try to get from cache
                cached = redis_client.get(cache_key)
                if cached:
                    logger.debug(f"Cache HIT for {cache_key}")
                    return json.loads(cached)
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                if result is not None:
                    redis_client.setex(cache_key, expire_time, json.dumps(result, default=str))
                    logger.debug(f"Cache SET for {cache_key}")
                
                return result
                
            except redis.RedisError as e:
                logger.warning(f"Redis error for {cache_key}: {e}")
                # Fallback to function execution
                return func(*args, **kwargs)
        
        # Return appropriate wrapper based on function type
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # CO_COROUTINE
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def generate_cache_key(func_name: str, args: tuple, kwargs: dict, prefix: str = "") -> str:
    """Generate a unique cache key for function call"""
    # Create a hash of the function call
    key_data = f"{func_name}:{str(args)}:{str(sorted(kwargs.items()))}"
    key_hash = hashlib.md5(key_data.encode()).hexdigest()
    
    if prefix:
        return f"{prefix}:{key_hash}"
    return f"recipe_app:{key_hash}"

def invalidate_cache(pattern: str) -> int:
    """
    Invalidate cache entries matching a pattern
    
    Args:
        pattern: Redis pattern to match (e.g., "recipe_app:user:*")
    
    Returns:
        Number of keys deleted
    """
    try:
        keys = redis_client.keys(pattern)
        if keys:
            deleted = redis_client.delete(*keys)
            logger.info(f"Invalidated {deleted} cache keys matching {pattern}")
            return deleted
        return 0
    except redis.RedisError as e:
        logger.error(f"Error invalidating cache pattern {pattern}: {e}")
        return 0

def clear_all_cache() -> int:
    """Clear all recipe app cache"""
    return invalidate_cache("recipe_app:*")

def get_cache_stats() -> dict:
    """Get cache statistics"""
    try:
        info = redis_client.info()
        return {
            "connected_clients": info.get("connected_clients", 0),
            "used_memory_human": info.get("used_memory_human", "0B"),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "total_commands_processed": info.get("total_commands_processed", 0)
        }
    except redis.RedisError as e:
        logger.error(f"Error getting cache stats: {e}")
        return {}

def cache_user_recipes(user_id: int, recipes: list, expire_time: int = 600):
    """Cache user recipes with specific key"""
    cache_key = f"recipe_app:user_recipes:{user_id}"
    try:
        redis_client.setex(cache_key, expire_time, json.dumps(recipes, default=str))
        logger.debug(f"Cached {len(recipes)} recipes for user {user_id}")
    except redis.RedisError as e:
        logger.warning(f"Failed to cache user recipes for {user_id}: {e}")

def get_cached_user_recipes(user_id: int) -> Optional[list]:
    """Get cached user recipes"""
    cache_key = f"recipe_app:user_recipes:{user_id}"
    try:
        cached = redis_client.get(cache_key)
        if cached:
            logger.debug(f"Cache HIT for user recipes {user_id}")
            return json.loads(cached)
        return None
    except redis.RedisError as e:
        logger.warning(f"Redis error getting user recipes for {user_id}: {e}")
        return None

def invalidate_user_cache(user_id: int) -> int:
    """Invalidate all cache for a specific user"""
    patterns = [
        f"recipe_app:user_recipes:{user_id}",
        f"recipe_app:user_profile:{user_id}",
        f"recipe_app:user_tags:{user_id}"
    ]
    
    total_deleted = 0
    for pattern in patterns:
        total_deleted += invalidate_cache(pattern)
    
    return total_deleted

# Health check function
def check_redis_health() -> bool:
    """Check if Redis is available and responding"""
    try:
        redis_client.ping()
        return True
    except redis.RedisError:
        return False
