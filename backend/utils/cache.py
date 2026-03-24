"""
Simple in-memory caching utility for the financial risk analysis system.
"""
import time
from typing import Optional, Any, Callable
from functools import wraps
from cachetools import TTLCache
from threading import Lock


class CacheManager:
    """
    Thread-safe in-memory cache with TTL support.
    
    Attributes:
        _cache: The underlying TTL cache storage
        _lock: Thread lock for safe concurrent access
    """
    
    def __init__(self, maxsize: int = 100, ttl: int = 300):
        """
        Initialize the cache manager.
        
        Args:
            maxsize: Maximum number of items in cache
            ttl: Time to live in seconds
        """
        self._cache: TTLCache = TTLCache(maxsize=maxsize, ttl=ttl)
        self._lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve an item from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """
        Store an item in cache.
        
        Args:
            key: Cache key
            value: Value to store
        """
        with self._lock:
            self._cache[key] = value
    
    def delete(self, key: str) -> None:
        """
        Remove an item from cache.
        
        Args:
            key: Cache key to remove
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self) -> None:
        """Clear all cached items."""
        with self._lock:
            self._cache.clear()
    
    def get_or_set(
        self, 
        key: str, 
        factory: Callable[[], Any]
    ) -> Any:
        """
        Get from cache or compute and store if not present.
        
        Args:
            key: Cache key
            factory: Callable to generate value if not cached
            
        Returns:
            Cached or newly computed value
        """
        value = self.get(key)
        if value is None:
            value = factory()
            self.set(key, value)
        return value


def cached(ttl: int = 300, maxsize: int = 100):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds
        maxsize: Maximum cache size
        
    Returns:
        Decorated function with caching
    """
    cache_instance = CacheManager(maxsize=maxsize, ttl=ttl)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key from function name and arguments
            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = "|".join(key_parts)
            
            return cache_instance.get_or_set(
                cache_key, 
                lambda: func(*args, **kwargs)
            )
        return wrapper
    return decorator


# Global cache instance
cache = CacheManager()
