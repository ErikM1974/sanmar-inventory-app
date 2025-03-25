"""
SanMar Pricing API Module

This module provides functions to interact with SanMar's Pricing API service.
It handles the SOAP requests to fetch product pricing information based on style, color, and size.
"""

import os
import logging
import json
import time
import os
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import zeep
from zeep.transports import Transport
from zeep.cache import SqliteCache
from zeep.helpers import serialize_object

# Set up logging
logger = logging.getLogger(__name__)

# Cache for pricing data with structure:
# {
#    "style_color_size": {
#        "data": pricing_data,
#        "timestamp": timestamp,
#        "expiration": expiration
#    }
# }
PRICING_CACHE = {}
CACHE_EXPIRATION = 60 * 60  # 1 hour in seconds

def get_cache_key(style, color=None, size=None, inventory_key=None, size_index=None):
    """Generate a cache key based on the input parameters."""
    if inventory_key and size_index:
        return f"{inventory_key}_{size_index}"
    elif style and color and size:
        return f"{style}_{color}_{size}".lower()
    elif style and color:
        return f"{style}_{color}".lower()
    else:
        return f"{style}".lower()

def get_from_cache(key):
    """Get pricing data from cache if available and not expired."""
    if key in PRICING_CACHE:
        cache_data = PRICING_CACHE[key]
        now = time.time()
        
        # Check if the cache entry is expired
        if now < cache_data["expiration"]:
            logger.info(f"Cache hit for key: {key}")
            return cache_data["data"]
        else:
            logger.info(f"Cache expired for key: {key}")
            del PRICING_CACHE[key]
    
    logger.info(f"Cache miss for key: {key}")
    return None

def save_to_cache(key, data):
    """Save pricing data to cache with expiration time."""
    now = time.time()
    PRICING_CACHE[key] = {
        "data": data,
        "timestamp": now,
        "expiration": now + CACHE_EXPIRATION
    }
    logger.info(f"Saved data to cache with key: {key}")

def get_pricing_for_color_swatch(style, color=None, size=None, inventory_key=None, size_index=None):
    """
    Fetch pricing data from SanMar's Pricing API for a given style, color, and size.
    
    This function supports both style/color/size and inventoryKey/sizeIndex request formats.
    It handles XML parsing, caching, and error recovery.
    
    Args:
        style (str): The product style code (e.g., "PC61")
        color (str, optional): The product color (e.g., "Blue")
        size (str, optional): The product size (e.g., "XL")
        inventory_key (str, optional): The SanMar inventory key
        size_index (str, optional): The SanMar size index
    
    Returns:
        dict: A dictionary containing pricing information with the following structure:
        {
            "original_price": {
                "S": 4.41,
                "M": 4.41,
                ...
            },
            "sale_price": {
                "S": 3.99,
                "M": 3.99,
                ...
            },
            "program_price": {
                "S": 3.79,
                "M": 3.79,
                ...
            },
            "case_size": {
                "S": 72,
                "M": 72,
                ...
            },
            "meta": {
                "has_sale": true,
                "sale_start_date": "2025-03-24",
                "sale_end_date": "2025-03-30"
            }
        }
    """
    try:
        # Check if data is available in cache
        cache_key = get_cache_key(style, color, size, inventory_key, size_index)
        cached_data = get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        # Get credentials from environment variables
        import os  # Import here to ensure it's available in this scope
        username = os.getenv("SANMAR_USERNAME")
        password = os.getenv("SANMAR_PASSWORD")
        customer_number = os.getenv("SANMAR_CUSTOMER_NUMBER")
        
        if not all([username, password, customer_number]):
            logger.error("SanMar API credentials not set in environment variables")
            return {
                "error": True,
                "message": "SanMar API credentials not configured",
            }
        
        # Determine which environment to use
        is_dev = os.getenv("SANMAR_DEV_MODE", "0") == "1"
        base_url = "https://edev-ws.sanmar.com:8080" if is_dev else "https://ws.sanmar.com:8080"
        
        # Set up WSDL URL
        wsdl_url = f"{base_url}/SanMarWebService/SanMarPricingServicePort?wsdl"
        logger.info(f"Using WSDL URL: {wsdl_url}")
        
        # Configure transport with retries
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount('https://', adapter)
        
        # Create transport with caching and session
        try:
            # Try to create a cache in a platform-appropriate location
            import tempfile
            import os
            cache_dir = os.path.join(tempfile.gettempdir(), "zeep_cache")
            os.makedirs(cache_dir, exist_ok=True)
            cache_path = os.path.join(cache_dir, "zeep_cache.db")
            logger.info(f"Using SQLite cache at: {cache_path}")
            cache = SqliteCache(path=cache_path, timeout=60 * 60 * 24)  # 24 hour cache
            transport = Transport(session=session, cache=cache, timeout=30)
        except Exception as e:
            # Fall back to no caching if there's an issue
            logger.warning(f"Unable to create SQLite cache: {str(e)}. Proceeding without cache.")
            transport = Transport(session=session, timeout=30)
        
        # Create SOAP client
        client = zeep.Client(wsdl=wsdl_url, transport=transport)
        
        # Prepare request arguments
        arg0 = {}
        
        # Determine which request format to use
        if inventory_key and size_index:
            # Use inventoryKey/sizeIndex format
            arg0 = {
                "inventoryKey": inventory_key,
                "sizeIndex": size_index,
                "piecePrice": None,
                "dozenPrice": None,
                "casePrice": None,
                "salePrice": None,
                "myPrice": None,
                "style": None,
                "color": None,
                "size": None,
            }
            logger.info(f"Using inventoryKey/sizeIndex format: {inventory_key}/{size_index}")
        else:
            # Use style/color/size format
            arg0 = {
                "style": style,
                "color": color if color else "",
                "size": size if size else "",
                "piecePrice": None,
                "dozenPrice": None,
                "casePrice": None,
                "salePrice": None,
                "myPrice": None,
                "inventoryKey": None,
                "sizeIndex": None,
            }
            logger.info(f"Using style/color/size format: {style}/{color if color else 'None'}/{size if size else 'None'}")
        
        # Prepare authentication
        arg1 = {
            "sanMarCustomerNumber": customer_number,
            "sanMarUserName": username,
            "sanMarUserPassword": password,
        }
        
        # Log the request (without sensitive credentials)
        safe_request = {
            "style": style,
            "color": color,
            "size": size,
            "inventoryKey": inventory_key,
            "sizeIndex": size_index,
        }
        logger.info(f"Sending pricing request: {json.dumps(safe_request)}")
        
        # Make the SOAP call
        start_time = time.time()
        response = client.service.getPricing(arg0, arg1)
        elapsed = time.time() - start_time
        logger.info(f"Pricing API call completed in {elapsed:.2f} seconds")
        
        # Process the response
        if response and hasattr(response, 'errorOccurred') and not response.errorOccurred:
            # Convert response to dictionary
            response_dict = serialize_object(response)
            logger.info(f"Pricing API response received with message: {response_dict.get('message', 'No message')}")
            
            # Check if we have list responses
            if 'listResponse' in response_dict and response_dict['listResponse']:
                # Initialize pricing data structure
                pricing_data = {
                    "original_price": {},
                    "sale_price": {},
                    "program_price": {},
                    "case_size": {},
                    "meta": {
                        "has_sale": False,
                        "sale_start_date": None,
                        "sale_end_date": None,
                    }
                }
                
                # Process each item in the response
                list_responses = response_dict['listResponse']
                if not isinstance(list_responses, list):
                    list_responses = [list_responses]
                
                for item in list_responses:
                    # Extract size (could be directly provided or derived from sizeIndex)
                    item_size = item.get('size', 'Unknown')
                    
                    # Extract pricing information
                    piece_price = item.get('piecePrice')
                    sale_price = item.get('salePrice')
                    my_price = item.get('myPrice')  # Customer-specific pricing
                    case_price = item.get('casePrice')
                    dozen_price = item.get('dozenPrice')
                    
                    # Check if this item is on sale
                    is_on_sale = sale_price and float(sale_price) > 0 and (
                        not piece_price or float(sale_price) < float(piece_price)
                    )
                    
                    if is_on_sale:
                        pricing_data["meta"]["has_sale"] = True
                        sale_start_date = item.get('saleStartDate')
                        sale_end_date = item.get('saleEndDate')
                        
                        if sale_start_date and not pricing_data["meta"]["sale_start_date"]:
                            pricing_data["meta"]["sale_start_date"] = sale_start_date
                        
                        if sale_end_date and not pricing_data["meta"]["sale_end_date"]:
                            pricing_data["meta"]["sale_end_date"] = sale_end_date
                    
                    # Store pricing information
                    pricing_data["original_price"][item_size] = float(piece_price) if piece_price else None
                    pricing_data["sale_price"][item_size] = float(sale_price) if sale_price else (
                        float(piece_price) if piece_price else None
                    )
                    pricing_data["program_price"][item_size] = float(my_price) if my_price else (
                        float(sale_price) if sale_price else (
                            float(piece_price) if piece_price else None
                        )
                    )
                    
                    # Determine case size based on available information
                    # Note: We don't have direct case size in the response, 
                    # but we can estimate it from pricing relationships
                    est_case_size = 72  # Default case size for many SanMar products
                    
                    if piece_price and case_price:
                        # If both prices are available, estimate case size based on price difference
                        price_ratio = float(piece_price) / float(case_price)
                        if price_ratio <= 1.2:  # Small discount indicates large case size
                            est_case_size = 72
                        else:
                            est_case_size = 36
                    
                    # For larger sizes, case size is typically smaller
                    if item_size in ['2XL', '3XL', '4XL', '5XL', '6XL']:
                        est_case_size = 36
                    
                    pricing_data["case_size"][item_size] = est_case_size
                
                # Save data to cache
                save_to_cache(cache_key, pricing_data)
                
                return pricing_data
            else:
                logger.warning("No pricing data found in the response")
                return {
                    "error": True,
                    "message": "No pricing data found",
                }
        else:
            # Handle error in response
            error_message = "Unknown error"
            if response and hasattr(response, 'message'):
                error_message = response.message
            
            logger.error(f"Error from pricing API: {error_message}")
            return {
                "error": True,
                "message": error_message,
            }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return {
            "error": True,
            "message": f"Network error: {str(e)}",
        }
    except zeep.exceptions.Fault as e:
        logger.error(f"SOAP fault: {str(e)}")
        return {
            "error": True,
            "message": f"SOAP fault: {str(e)}",
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "error": True,
            "message": f"Unexpected error: {str(e)}",
        }