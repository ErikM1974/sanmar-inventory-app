"""
Performance configuration for the SanMar Inventory App
This file contains settings to improve the application's performance
"""

# Caching configuration
CACHE_ENABLED = True
CACHE_TIMEOUT = 24 * 60 * 60  # 24 hours in seconds
BATCH_SIZE = 20  # Number of items to process in a batch
REQUEST_TIMEOUT = 15  # Timeout for API requests in seconds

# API rate limiting to prevent overloading
MAX_REQUESTS_PER_MINUTE = 120
REQUEST_INTERVAL = 0.5  # Minimum time between requests in seconds

# Database connection pooling
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20

# Threading configuration
MAX_THREADS = 8  # Maximum number of worker threads

# Response compression
ENABLE_COMPRESSION = True
COMPRESS_LEVEL = 6  # 1-9, higher means more compression but slower

# Static asset configuration
STATIC_CACHE_TIMEOUT = 7 * 24 * 60 * 60  # 1 week in seconds

# API caching tiers
API_CACHE_TIERS = {
    "short": 60 * 5,           # 5 minutes for frequently changing data
    "medium": 60 * 60 * 2,     # 2 hours for moderately changing data
    "long": 24 * 60 * 60,      # 1 day for rarely changing data
    "very_long": 7 * 24 * 60 * 60  # 1 week for static data
}

# Feature flags
FEATURES = {
    "parallel_api_calls": True,
    "lazy_loading": True,
    "browser_caching": True,
    "color_batch_loading": True,
    "image_optimization": True,
    "price_caching": True
}

# URL whitelist for API requests (security and performance)
API_WHITELIST = [
    "ws.sanmar.com",
    "cdnm.sanmar.com",
    "api-mini-server-919227e25714.herokuapp.com"
]

# Logging configuration - reduce verbose logging in production
LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_TO_FILE = True
LOG_ROTATION = True
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5

# Browser performance optimizations
BROWSER_OPTIMIZATIONS = {
    "minify_js": True,
    "minify_css": True,
    "lazy_load_images": True,
    "defer_non_critical_js": True
}