"""
Performance optimizations for the SanMar Inventory App
This module provides functions and decorators to improve application performance
"""

import time
import logging
import functools
import threading
import concurrent.futures
from typing import Dict, List, Any, Callable, Optional
import os
import pickle
import hashlib
from flask import request, Response, make_response
import gzip
import json
from datetime import datetime, timedelta

# Set up logging
logger = logging.getLogger("performance")
logger.setLevel(logging.INFO)

# Create file handler
if not os.path.exists("logs"):
    os.makedirs("logs")
file_handler = logging.FileHandler("logs/performance.log")
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(file_handler)

# Simple cache implementation to replace werkzeug.contrib.cache
class SimpleCache:
    def __init__(self, default_timeout=300):
        self.cache = {}
        self.timeouts = {}
        self.default_timeout = default_timeout
        self._lock = threading.RLock()
        
    def get(self, key):
        with self._lock:
            if key in self.cache:
                timeout = self.timeouts.get(key, 0)
                if timeout > time.time():
                    return self.cache[key]
                else:
                    del self.cache[key]
                    del self.timeouts[key]
            return None
        
    def set(self, key, value, timeout=None):
        with self._lock:
            self.cache[key] = value
            if timeout is None:
                timeout = self.default_timeout
            self.timeouts[key] = time.time() + timeout
        
    def delete(self, key):
        with self._lock:
            if key in self.cache:
                del self.cache[key]
                del self.timeouts[key]

    def clear(self):
        with self._lock:
            self.cache.clear()
            self.timeouts.clear()

# Load configuration
try:
    from performance_config import (
        CACHE_ENABLED, CACHE_TIMEOUT, BATCH_SIZE, MAX_THREADS,
        ENABLE_COMPRESSION, COMPRESS_LEVEL, API_CACHE_TIERS,
        FEATURES, LOG_LEVEL
    )
    logger.setLevel(getattr(logging, LOG_LEVEL))
except ImportError:
    # Default values if config not found
    CACHE_ENABLED = True
    CACHE_TIMEOUT = 24 * 60 * 60  # 24 hours in seconds
    BATCH_SIZE = 20
    MAX_THREADS = 8
    ENABLE_COMPRESSION = True
    COMPRESS_LEVEL = 6
    API_CACHE_TIERS = {
        "short": 60 * 5,           # 5 minutes
        "medium": 60 * 60 * 2,     # 2 hours
        "long": 24 * 60 * 60,      # 1 day
        "very_long": 7 * 24 * 60 * 60  # 1 week
    }
    FEATURES = {
        "parallel_api_calls": True,
        "lazy_loading": True,
        "browser_caching": True
    }
    LOG_LEVEL = "INFO"
    logger.warning("Could not import performance_config, using default values")

# In-memory cache
_memory_cache: Dict[str, Any] = {}
_memory_cache_timestamps: Dict[str, float] = {}
_cache_lock = threading.RLock()

# Initialize memory cache
cache = SimpleCache(default_timeout=CACHE_TIMEOUT)

def generate_cache_key(func_name: str, args: tuple, kwargs: Dict[str, Any]) -> str:
    """Generate a unique cache key based on function name and arguments"""
    key_parts = [func_name]
    
    # Add positional arguments
    for arg in args:
        if isinstance(arg, (str, int, float, bool, type(None))):
            key_parts.append(str(arg))
        else:
            # For complex objects, use their repr or hash
            try:
                key_parts.append(hash(arg))
            except TypeError:
                key_parts.append(str(id(arg)))
    
    # Add keyword arguments in sorted order
    for key in sorted(kwargs.keys()):
        value = kwargs[key]
        if isinstance(value, (str, int, float, bool, type(None))):
            key_parts.append(f"{key}:{value}")
        else:
            try:
                key_parts.append(f"{key}:{hash(value)}")
            except TypeError:
                key_parts.append(f"{key}:{id(value)}")
    
    # Join parts and hash the result
    key_string = ":".join(str(p) for p in key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()

def cache_result(timeout: Optional[int] = None):
    """
    Decorator to cache function results in memory
    Args:
        timeout: Cache timeout in seconds (None for default)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not CACHE_ENABLED:
                return func(*args, **kwargs)
            
            # Generate cache key
            cache_key = generate_cache_key(func.__name__, args, kwargs)
            
            # Try to get from cache
            with _cache_lock:
                if cache_key in _memory_cache:
                    timestamp = _memory_cache_timestamps.get(cache_key, 0)
                    current_time = time.time()
                    cache_timeout = timeout or CACHE_TIMEOUT
                    
                    # Check if cache is still valid
                    if current_time - timestamp < cache_timeout:
                        logger.debug(f"Cache hit for {func.__name__}")
                        return _memory_cache[cache_key]
            
            # Cache miss, calculate result
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            # Store in cache
            with _cache_lock:
                _memory_cache[cache_key] = result
                _memory_cache_timestamps[cache_key] = time.time()
            
            logger.debug(f"Cache miss for {func.__name__}, took {elapsed:.2f}s")
            return result
        return wrapper
    return decorator

def clear_cache(prefix: Optional[str] = None):
    """
    Clear all cached results or those matching a prefix
    Args:
        prefix: Optional prefix to match cache keys
    """
    with _cache_lock:
        if prefix:
            keys_to_remove = [k for k in _memory_cache.keys() if k.startswith(prefix)]
            for key in keys_to_remove:
                del _memory_cache[key]
                if key in _memory_cache_timestamps:
                    del _memory_cache_timestamps[key]
        else:
            _memory_cache.clear()
            _memory_cache_timestamps.clear()
    logger.info(f"Cleared cache {'with prefix '+prefix if prefix else 'completely'}")

def parallel_map(func: Callable, items: List[Any], max_workers: Optional[int] = None) -> List[Any]:
    """
    Execute a function on a list of items in parallel
    Args:
        func: Function to execute
        items: List of items to process
        max_workers: Maximum number of worker threads
    Returns:
        List of results
    """
    if not items:
        return []
    
    if max_workers is None:
        max_workers = min(MAX_THREADS, len(items))
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(func, items))

def batch_process(items: List[Any], batch_size: Optional[int] = None) -> List[List[Any]]:
    """
    Split a list of items into batches for processing
    Args:
        items: List of items to batch
        batch_size: Size of each batch
    Returns:
        List of batches
    """
    if not items:
        return []
    
    if batch_size is None:
        batch_size = BATCH_SIZE
    
    return [items[i:i+batch_size] for i in range(0, len(items), batch_size)]

def timed_execution(func):
    """Decorator to measure and log execution time of functions"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        # Log based on performance thresholds
        if execution_time > 2.0:
            logger.warning(f"VERY SLOW: {func.__name__} took {execution_time:.2f}s")
        elif execution_time > 1.0:
            logger.warning(f"Slow function: {func.__name__} took {execution_time:.2f}s")
        else:
            logger.debug(f"Function {func.__name__} executed in {execution_time:.2f}s")
        
        return result
    return wrapper

def retry(max_attempts: int = 3, delay: float = 0.5, backoff: float = 2.0):
    """
    Decorator to retry a function on failure with exponential backoff
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Retry {attempt}/{max_attempts} for {func.__name__}: {str(e)}")
                    
                    if attempt < max_attempts:
                        time.sleep(current_delay)
                        current_delay *= backoff
            
            # If we get here, all attempts failed
            logger.error(f"All {max_attempts} retries failed for {func.__name__}")
            raise last_exception
        return wrapper
    return decorator

def compress_response(response_data: str, level: Optional[int] = None) -> bytes:
    """
    Compress response data using gzip
    Args:
        response_data: Data to compress
        level: Compression level (1-9)
    Returns:
        Compressed data
    """
    if not ENABLE_COMPRESSION:
        return response_data.encode()
    
    compress_level = level or COMPRESS_LEVEL
    return gzip.compress(response_data.encode(), compress_level)

def compressed_response(func):
    """Decorator to compress HTTP responses"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not ENABLE_COMPRESSION:
            return func(*args, **kwargs)
        
        result = func(*args, **kwargs)
        
        # Only compress if result is a Flask Response or string
        if isinstance(result, (Response, str)):
            if isinstance(result, str):
                compressed_data = compress_response(result)
                response = make_response(compressed_data)
            else:
                # Already a Response object
                response = result
                if response.content_type == 'application/json':
                    response.data = compress_response(response.get_data(as_text=True))
            
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Vary'] = 'Accept-Encoding'
            return response
        
        return result
    return wrapper

def thread_local_singleton(cls):
    """
    Decorator to create thread-local singleton classes
    This ensures each thread has its own instance while still acting like a singleton
    """
    instances = threading.local()
    
    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if not hasattr(instances, 'instance'):
            instances.instance = cls(*args, **kwargs)
        return instances.instance
    
    return get_instance

def lazy_load(func):
    """
    Decorator to lazily load resources only when needed
    This is useful for expensive initializations
    """
    loaded = False
    result = None
    lock = threading.Lock()
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal loaded, result
        if not loaded:
            with lock:
                if not loaded:  # Double-check lock pattern
                    result = func(*args, **kwargs)
                    loaded = True
        return result
    
    return wrapper

# Cache API responses
def api_cache(tier: str = 'medium'):
    """
    Decorator to cache API responses based on configured tiers
    Args:
        tier: Cache tier (short, medium, long, very_long)
    """
    timeout = API_CACHE_TIERS.get(tier, API_CACHE_TIERS['medium'])
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not CACHE_ENABLED:
                return func(*args, **kwargs)
            
            # Use request path and query parameters as part of the cache key
            cache_key = f"api:{request.path}:{request.query_string.decode()}"
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"API cache hit for {request.path}")
                return cached_value
            
            # Cache miss, execute API call
            result = func(*args, **kwargs)
            
            # Cache the result
            cache.set(cache_key, result, timeout=timeout)
            logger.debug(f"API cache miss for {request.path}, cached for {timeout}s")
            
            return result
        return wrapper
    return decorator

def init_performance_optimizations():
    """Initialize performance optimizations at application startup"""
    logger.info("Initializing performance optimizations")
    
    # Log active features
    for feature, enabled in FEATURES.items():
        logger.info(f"Feature '{feature}' is {'enabled' if enabled else 'disabled'}")
    
    # Warm up caches for frequently accessed data
    # This runs in a background thread to avoid delaying startup
    def warm_up_caches():
        logger.info("Warming up caches...")
        # Add code to pre-populate caches with common data
        
    warm_up_thread = threading.Thread(target=warm_up_caches)
    warm_up_thread.daemon = True
    warm_up_thread.start()
    
    logger.info("Performance optimizations initialized")

# Initialize optimizations when this module is imported
init_performance_optimizations()