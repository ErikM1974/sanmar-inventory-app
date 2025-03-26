import requests
import logging
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("middleware_client")

# Middleware API configuration
MIDDLEWARE_API_BASE_URL = "https://api-mini-server-919227e25714.herokuapp.com"
API_TIMEOUT = 15  # seconds

# SanMar API credentials
USERNAME = os.getenv("SANMAR_USERNAME")
PASSWORD = os.getenv("SANMAR_PASSWORD")
CUSTOMER_NUMBER = os.getenv("SANMAR_CUSTOMER_NUMBER")

def create_session_with_retries():
    """
    Create a requests session with retry logic for transient failures
    """
    session = requests.Session()
    retry_strategy = Retry(
        total=3,  # Maximum number of retries
        backoff_factor=0.5,  # Exponential backoff
        status_forcelist=[500, 502, 503, 504],  # Retry on these HTTP status codes
        allowed_methods=["GET", "POST"]  # Retry for these methods
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def categorize_error(exception):
    """
    Categorize request exceptions for better error handling and logging
    """
    if isinstance(exception, requests.ConnectionError):
        return "NETWORK_ERROR"
    elif isinstance(exception, requests.Timeout):
        return "TIMEOUT_ERROR"
    elif isinstance(exception, requests.HTTPError):
        if hasattr(exception, 'response') and exception.response:
            if exception.response.status_code in [401, 403]:
                return "AUTH_ERROR"
            elif exception.response.status_code == 404:
                return "NOT_FOUND_ERROR"
            else:
                return f"HTTP_ERROR_{exception.response.status_code}"
        return "HTTP_ERROR"
    elif isinstance(exception, requests.RequestException):
        return "REQUEST_ERROR"
    else:
        return "UNKNOWN_ERROR"

def fetch_combined_data(style, color=None):
    """
    Fetch combined product, inventory, and pricing data from the middleware API
    
    Args:
        style (str): The product style number
        color (str, optional): The color code or name
        
    Returns:
        dict: The combined data or None if an error occurred
    """
    log_context = {"style": style, "color": color, "source": "middleware"}
    
    # Construct the URL
    url = f"{MIDDLEWARE_API_BASE_URL}/sanmar/combined/{style}"
    if color:
        url += f"/{color}"
    
    session = create_session_with_retries()
    start_time = time.time()
    
    try:
        logger.info(f"Fetching data from middleware: {url}", extra=log_context)
        response = session.get(url, timeout=API_TIMEOUT)
        response.raise_for_status()
        
        duration = time.time() - start_time
        logger.info(f"Successfully fetched data in {duration:.2f}s", 
                   extra={**log_context, "duration": duration})
        
        data = response.json()
        if not data.get('success') or not data.get('data'):
            logger.warning("Middleware returned success=false or no data", 
                         extra=log_context)
            return None
            
        return data.get('data')
        
    except requests.RequestException as e:
        duration = time.time() - start_time
        error_type = categorize_error(e)
        logger.error(f"Failed to fetch data: {e}", 
                    extra={**log_context, "error_type": error_type, "duration": duration})
        return None
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Unexpected error fetching data: {e}", 
                    extra={**log_context, "error_type": "UNEXPECTED_ERROR", "duration": duration})
        return None

def check_middleware_health():
    """
    Check if the middleware API is available
    
    Returns:
        dict: Health status information
    """
    start_time = time.time()
    try:
        # Simple health check endpoint or use the base URL
        response = requests.get(f"{MIDDLEWARE_API_BASE_URL}/health", timeout=5)
        response.raise_for_status()
        
        duration = time.time() - start_time
        return {
            "status": "Connected",
            "latency": f"{duration:.2f}s",
            "timestamp": time.time()
        }
    except Exception as e:
        duration = time.time() - start_time
        error_type = categorize_error(e) if isinstance(e, requests.RequestException) else "UNKNOWN_ERROR"
        return {
            "status": "Error",
            "error": str(e),
            "error_type": error_type,
            "latency": f"{duration:.2f}s",
            "timestamp": time.time()
        }

# Enhanced autocomplete with improved caching
AUTOCOMPLETE_CACHE = {}
CACHE_EXPIRY = 24 * 3600  # 24 hours - increased from 1 hour
MAX_RESULTS = 15  # Increased from 10 to provide more options

def get_cache_key(query):
    """
    Get a cache key for the query
    
    Args:
        query (str): The search query
        
    Returns:
        str: Cache key for the query
    """
    # For shorter queries, use the full query as key
    if len(query) <= 3:
        return query.upper()
    
    # For longer queries, use prefix plus pattern
    return f"{query[:3].upper()}_{len(query)}"

def preload_common_searches():
    """Preload common search prefixes into cache"""
    common_prefixes = ["PC", "K5", "J7", "ST", "NE", "L2", "G2", "BC", "DM", "DT", "CS"]
    logger.info(f"Preloading {len(common_prefixes)} common search prefixes")
    
    for prefix in common_prefixes:
        try:
            # Don't log during preloading to avoid cluttering logs
            fetch_autocomplete(prefix, log_enabled=False)
        except Exception as e:
            logger.warning(f"Failed to preload '{prefix}': {e}")
    
    logger.info(f"Preloading complete. Cache contains {len(AUTOCOMPLETE_CACHE)} entries")

def fetch_autocomplete(query, log_enabled=True):
    """
    Fetch autocomplete suggestions for a product style number
    with enhanced caching and performance
    
    Args:
        query (str): The search query (style number prefix)
        log_enabled (bool): Whether to log cache hits/misses
        
    Returns:
        list: List of matching style numbers
    """
    if not query or len(query) < 2:
        return []
        
    # Normalize query for cache lookup
    query_upper = query.upper()
    cache_key = get_cache_key(query_upper)
    current_time = time.time()
    
    # Check cache first
    if cache_key in AUTOCOMPLETE_CACHE and (current_time - AUTOCOMPLETE_CACHE[cache_key]['timestamp'] < CACHE_EXPIRY):
        all_results = AUTOCOMPLETE_CACHE[cache_key]['data']
        
        # Filter the cached results to match the current query
        cached_results = [s for s in all_results if s.startswith(query_upper)]
        
        if log_enabled:
            logger.info(f"Autocomplete cache hit for '{query}'",
                       extra={"query": query, "cache_key": cache_key, "results_count": len(cached_results)})
        
        return cached_results[:MAX_RESULTS]
    
    # Try to get partial matches from cache for prefixes
    if len(query) >= 3:
        prefix_key = query_upper[:2]
        if prefix_key in AUTOCOMPLETE_CACHE and (current_time - AUTOCOMPLETE_CACHE[prefix_key]['timestamp'] < CACHE_EXPIRY):
            all_results = AUTOCOMPLETE_CACHE[prefix_key]['data']
            prefix_matches = [s for s in all_results if s.startswith(query_upper)]
            
            if prefix_matches and log_enabled:
                logger.info(f"Autocomplete partial cache hit for '{query}'",
                           extra={"query": query, "partial_key": prefix_key, "results_count": len(prefix_matches)})
                
                return prefix_matches[:MAX_RESULTS]
    
    # Check local mock data first for exact match
    from mock_data import get_mock_autocomplete, COMMON_STYLES
    
    # If the entire query exactly matches a known style, return it immediately
    if query_upper in COMMON_STYLES:
        results = [query_upper]
        if log_enabled:
            logger.info(f"Exact style match for '{query}' in local data",
                       extra={"query": query, "results_count": 1})
        return results
    
    # Get local matches based on our enhanced mock data
    local_results = get_mock_autocomplete(query)
    
    # If we have good local results, return them immediately
    if len(local_results) >= 3:
        if log_enabled:
            logger.info(f"Using local data matches for '{query}'",
                       extra={"query": query, "results_count": len(local_results)})
        
        # Also cache these results
        AUTOCOMPLETE_CACHE[cache_key] = {
            "data": local_results,
            "timestamp": current_time
        }
        
        return local_results[:MAX_RESULTS]
    
    # Cache miss, fetch from middleware
    log_context = {"query": query, "source": "middleware"}
    start_time = time.time()
    
    try:
        if log_enabled:
            logger.info(f"Fetching autocomplete data for '{query}'", extra=log_context)
            
        url = f"{MIDDLEWARE_API_BASE_URL}/sanmar/autocomplete?q={query}"
        session = create_session_with_retries()
        response = session.get(url, timeout=API_TIMEOUT)
        response.raise_for_status()
        
        results = response.json()
        duration = time.time() - start_time
        
        # If API returned no results but we have local results, use those
        if not results and local_results:
            if log_enabled:
                logger.info(f"API returned no results, using local results for '{query}'",
                          extra={**log_context, "results_count": len(local_results)})
            results = local_results
        
        # Add the exact query if it's valid and not already in results
        if len(query) >= 4 and query_upper not in results:
            results.append(query_upper)
            if log_enabled:
                logger.info(f"Added exact query '{query}' to results",
                          extra={**log_context})
        
        # Update cache - store all results
        AUTOCOMPLETE_CACHE[cache_key] = {
            "data": results,
            "timestamp": current_time
        }
        
        # Also store in a prefix cache if appropriate
        if len(query) >= 3 and query_upper[:2] not in AUTOCOMPLETE_CACHE:
            AUTOCOMPLETE_CACHE[query_upper[:2]] = {
                "data": results,
                "timestamp": current_time
            }
        
        if log_enabled:
            logger.info(f"Autocomplete request completed in {duration:.2f}s",
                       extra={**log_context, "duration": duration, "results_count": len(results)})
        
        return results[:MAX_RESULTS]
        
    except Exception as e:
        duration = time.time() - start_time
        error_type = categorize_error(e) if isinstance(e, requests.RequestException) else "UNEXPECTED_ERROR"
        
        if log_enabled:
            logger.error(f"Autocomplete error: {e}",
                        extra={**log_context, "error_type": error_type, "duration": duration})
        
        # We already checked local_results above, but return them here as fallback
        if local_results:
            return local_results[:MAX_RESULTS]
            
        # If we have no local results, try to generate some based on what we know
        if len(query) >= 4:
            # For longer queries, assume it might be a valid style number and include it
            return [query_upper]
            
        # Final fallback to empty list
        return []
