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

# Autocomplete with caching
AUTOCOMPLETE_CACHE = {}
CACHE_EXPIRY = 3600  # 1 hour

def fetch_autocomplete(query):
    """
    Fetch autocomplete suggestions for a product style number
    
    Args:
        query (str): The search query (style number prefix)
        
    Returns:
        list: List of matching style numbers
    """
    if not query or len(query) < 2:
        return []
        
    # Check cache first
    cache_key = query[:3]  # First 3 chars as cache key
    current_time = time.time()
    if cache_key in AUTOCOMPLETE_CACHE and (current_time - AUTOCOMPLETE_CACHE[cache_key]['timestamp'] < CACHE_EXPIRY):
        cached_results = [s for s in AUTOCOMPLETE_CACHE[cache_key]['data'] if s.startswith(query)]
        logger.info(f"Autocomplete cache hit for '{query}'", 
                   extra={"query": query, "cache_key": cache_key, "results_count": len(cached_results)})
        return cached_results[:10]
    
    # Cache miss, fetch from middleware
    log_context = {"query": query, "source": "middleware"}
    start_time = time.time()
    
    try:
        logger.info(f"Fetching autocomplete data for '{query}'", extra=log_context)
        url = f"{MIDDLEWARE_API_BASE_URL}/sanmar/autocomplete?q={query}"
        session = create_session_with_retries()
        response = session.get(url, timeout=API_TIMEOUT)
        response.raise_for_status()
        
        results = response.json()
        duration = time.time() - start_time
        
        # Update cache
        AUTOCOMPLETE_CACHE[cache_key] = {
            "data": results,
            "timestamp": current_time
        }
        
        logger.info(f"Autocomplete request completed in {duration:.2f}s", 
                   extra={**log_context, "duration": duration, "results_count": len(results)})
        
        return results[:10]
        
    except Exception as e:
        duration = time.time() - start_time
        error_type = categorize_error(e) if isinstance(e, requests.RequestException) else "UNEXPECTED_ERROR"
        logger.error(f"Autocomplete error: {e}", 
                    extra={**log_context, "error_type": error_type, "duration": duration})
        
        # Fallback to empty results
        return []
