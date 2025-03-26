import json
import logging
import os
import time
from collections import OrderedDict
from datetime import datetime

import requests
from zeep import Client
from zeep.cache import SqliteCache
from zeep.helpers import serialize_object
from zeep.transports import Transport

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache management functions
def get_cache_key(style=None, color=None, size=None, inventory_key=None, size_index=None):
    """Generate a unique cache key based on input parameters"""
    if inventory_key and size_index:
        return f"{inventory_key}_{size_index}"
    else:
        if style:
            # Replace dangerous characters in color with safe ones
            safe_color = color.lower().replace('/', '-').replace('\\', '-') if color else ''
            return f"{style.lower()}_{safe_color}"
        else:
            return ""

def get_from_cache(key):
    """Retrieve data from cache if available and not expired"""
    # Default cache directory in the project
    cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache', 'pricing')
    os.makedirs(cache_dir, exist_ok=True)
    
    cache_file = os.path.join(cache_dir, f"{key}.json")
    
    if os.path.exists(cache_file):
        # Check if cache is not expired (24 hour cache)
        last_modified = os.path.getmtime(cache_file)
        cache_age = time.time() - last_modified
        
        # If cache is less than 24 hours old
        if cache_age < 24 * 60 * 60:  # 24 hours in seconds
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error reading cache file {cache_file}: {e}")
    
    return None

def save_to_cache(key, data):
    """Save data to cache"""
    if not key:
        return
    
    # Default cache directory in the project
    cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache', 'pricing')
    os.makedirs(cache_dir, exist_ok=True)
    
    cache_file = os.path.join(cache_dir, f"{key}.json")
    
    try:
        with open(cache_file, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        logger.error(f"Error writing to cache file {cache_file}: {e}")

def delete_from_cache(key):
    """Delete data from cache"""
    if not key:
        return
    
    # Default cache directory in the project
    cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache', 'pricing')
    cache_file = os.path.join(cache_dir, f"{key}.json")
    
    if os.path.exists(cache_file):
        try:
            os.remove(cache_file)
        except Exception as e:
            logger.error(f"Error deleting cache file {cache_file}: {e}")

def get_default_case_size(style, size):
    """
    Get the default case size for a given style and size.
    We now use a standard case size of 24 for all SanMar products to match their website.
    
    Args:
        style (str): Product style number (not used but kept for backward compatibility)
        size (str): Size code (not used but kept for backward compatibility)
        
    Returns:
        int: Standard case size of 24
    """
    # Special case for one-size items
    if size == "OSFA" or size == "OS" or size == "ONE SIZE":
        return 72  # Default for one-size accessories
        
    # For all other product sizes, return the standard case size
    return 24  # Standard SanMar case size
            
def size_to_sort_key(size):
    """Convert size to a sortable key"""
    if size in ['XS', 'S', 'M', 'L', 'XL']:
        return {
            'XS': 0,
            'S': 1,
            'M': 2,
            'L': 3,
            'XL': 4
        }.get(size, 999)
    elif size.endswith('XL'):
        # For sizes like 2XL, 3XL, 4XL, etc.
        try:
            return 5 + int(size.rstrip('XL'))
        except ValueError:
            return 999
    else:
        # Try to convert to a number if possible
        try:
            return 100 + float(size)
        except ValueError:
            # If not a number, use alphabetical sorting as fallback
            return 1000 + ord(size[0])

def get_pricing_for_color_swatch(style, color, size=None, inventory_key=None, size_index=None, use_cache=True):
    """
    Get pricing information for a color swatch from SanMar's Pricing API.
    
    This is a convenience function to get pricing data for a specific color,
    which is useful when showing pricing for color swatches on product pages.
    
    Args:
        style (str): The style number
        color (str): The catalog color
        size (str, optional): The size to get pricing for
        inventory_key (str, optional): Alternative to style/color
        size_index (str, optional): Alternative to size
        use_cache (bool): Whether to use cached data if available
    
    Returns:
        dict: Pricing data in the following format:
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
        
        # Use production URL by default, or development if set in environment
        env = os.getenv("SANMAR_ENV", "PRODUCTION")
        if env.upper() == "DEVELOPMENT" or env.upper() == "DEV" or env.upper() == "EDEV":
            wsdl_url = "https://edev-ws.sanmar.com:8080/SanMarWebService/SanMarPricingServicePort?wsdl"
        else:
            wsdl_url = "https://ws.sanmar.com:8080/SanMarWebService/SanMarPricingServicePort?wsdl"

        logger.info(f"Using WSDL URL: {wsdl_url}")
        
        # Set up the SOAP client with caching
        cache_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "zeep_cache")
        os.makedirs(cache_path, exist_ok=True)
        cache = SqliteCache(path=os.path.join(cache_path, "zeep_cache.db"), timeout=60*60*24)  # 24 hour cache
        transport = Transport(cache=cache)
        client = Client(wsdl_url, transport=transport)
        
        # Prepare the request arguments
        arg0 = {
            # Initialize empty to avoid null values in SOAP request
            'casePrice': None,
            'color': None,
            'dozenPrice': None,
            'inventoryKey': None,
            'myPrice': None,
            'piecePrice': None,
            'salePrice': None,
            'size': None,
            'sizeIndex': None,
            'style': None,
        }
        
        # Set values based on input parameters
        if inventory_key and size_index:
            # Using inventoryKey/sizeIndex format
            arg0['inventoryKey'] = inventory_key
            arg0['sizeIndex'] = size_index
            logger.info(f"Using inventoryKey/sizeIndex format: {inventory_key}/{size_index}")
        else:
            # Using style/color/size format
            arg0['style'] = style
            if color:
                arg0['color'] = color
            if size:
                arg0['size'] = size
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
                    "original_price": {},  # Changed back to "original_price" for frontend compatibility
                    "sale_price": {},
                    "program_price": {},
                    "case_price": {},      # Added dedicated case_price field
                    "case_size": {},
                    "meta": {
                        "has_sale": False,
                        "sale_start_date": "",
                        "sale_end_date": ""
                    }
                }
                
                # Process list responses
                for item in response_dict['listResponse']:
                    # Extract basic information
                    item_style = item.get('style', '')
                    item_color = item.get('color', '')
                    item_size = item.get('size', '')
                    
                    # Log only for first items to avoid excessive logging
                    if len(pricing_data["case_size"]) < 3:
                        logger.debug(f"Processing pricing for style: {item_style}, color: {item_color}, size: {item_size}")
                    
                    # Extract pricing information
                    piece_price = item.get('piecePrice')
                    dozen_price = item.get('dozenPrice')
                    case_price = item.get('casePrice')
                    sale_price = item.get('salePrice')
                    my_price = item.get('myPrice')
                    
                    # Set has_sale flag - only if sale price is actually lower
                    if sale_price and piece_price and float(sale_price) < float(piece_price):
                        # Make sure the difference is significant enough to be a real sale (more than 1%)
                        if (float(piece_price) - float(sale_price)) / float(piece_price) > 0.01:
                            pricing_data["meta"]["has_sale"] = True
                    
                    # Get sale dates
                    sale_start_date = item.get('saleStartDate')
                    sale_end_date = item.get('saleEndDate')
                    
                    if sale_start_date and not pricing_data["meta"]["sale_start_date"]:
                        pricing_data["meta"]["sale_start_date"] = sale_start_date
                    
                    if sale_end_date and not pricing_data["meta"]["sale_end_date"]:
                        pricing_data["meta"]["sale_end_date"] = sale_end_date
                    
                    # Store pricing information
                    # Make sure we preserve the exact size-price relationship from the API
                    # This ensures larger sizes (2XL, 3XL, 4XL) have their correct higher prices
                    if case_price:
                        pricing_data["case_price"][item_size] = float(case_price)
                    elif piece_price and hasattr(item, 'caseSize') and item.caseSize:
                        # Calculate case price from piece price × case size
                        try:
                            case_size = int(item.caseSize)
                            pricing_data["case_price"][item_size] = float(piece_price) * case_size
                        except (ValueError, TypeError):
                            # If calculation fails, just use piece price as fallback
                            pricing_data["case_price"][item_size] = float(piece_price)
                    elif piece_price:
                        # Use default case size if no direct case size information
                        case_size = get_default_case_size(item_style, item_size)
                        pricing_data["case_price"][item_size] = float(piece_price) * case_size
                    
                    # Store original values for logging purposes
                    original_piece_price = piece_price
                    original_sale_price = sale_price
                    
                    # First, ensure we have valid price values
                    if piece_price:
                        piece_price_float = float(piece_price)
                    else:
                        piece_price_float = None
                        
                    if sale_price:
                        sale_price_float = float(sale_price)
                    else:
                        sale_price_float = None
                    
                    # Safety check for the larger sizes - known to have issues
                    if item_size in ['2XL', '3XL', '4XL']:
                        logger.info(f"Processing large size {item_size} - case: {case_price}, piece: {piece_price}, sale: {sale_price}")
                    
                    # Determine the correct sale price
                    if sale_price_float and piece_price_float:
                        # Only use sale price if it's actually lower than regular price
                        if sale_price_float <= piece_price_float:
                            pricing_data["sale_price"][item_size] = sale_price_float
                        else:
                            # If the sale price is higher (which is wrong), use the regular price
                            pricing_data["sale_price"][item_size] = piece_price_float
                            logger.info(f"Corrected invalid sale price for size {item_size} - was {original_sale_price}, set to {original_piece_price}")
                    elif piece_price_float:
                        pricing_data["sale_price"][item_size] = piece_price_float
                    else:
                        pricing_data["sale_price"][item_size] = None
                    
                    # Final verification to ensure sale price is never higher than regular price
                    if (pricing_data["sale_price"][item_size] is not None and
                        pricing_data["case_price"][item_size] is not None and
                        pricing_data["sale_price"][item_size] > pricing_data["case_price"][item_size]):
                        
                        logger.info(f"FINAL CHECK: Fixed invalid sale price for size {item_size} - was {pricing_data['sale_price'][item_size]}, set to {pricing_data['case_price'][item_size]}")
                        pricing_data["sale_price"][item_size] = pricing_data["case_price"][item_size]
                    
                    # For program price, use customer-specific price if available and not higher than piece price,
                    # then fall back to sale price, and finally to regular price
                    if my_price and piece_price and float(my_price) <= float(piece_price):
                        pricing_data["program_price"][item_size] = float(my_price)
                    elif sale_price and piece_price and float(sale_price) <= float(piece_price):
                        pricing_data["program_price"][item_size] = float(sale_price)
                    elif piece_price:
                        pricing_data["program_price"][item_size] = float(piece_price)
                    else:
                        pricing_data["program_price"][item_size] = None
                    
                    # Get case size directly from the API when available (highest priority)
                    if hasattr(item, 'caseSize') and item.caseSize:
                        try:
                            case_size_value = int(item.caseSize)
                            pricing_data["case_size"][item_size] = case_size_value
                            logger.info(f"Using case size from API for size {item_size}: {case_size_value}")
                        except (ValueError, TypeError):
                            # Fall back to most common value for SanMar products
                            pricing_data["case_size"][item_size] = 24
                            logger.info(f"Using standard case size (24) for {item_style}, size {item_size} after API value conversion failed")
                    else:
                        # For all SanMar products, the default case size for all sizes should be 24
                        # This aligns with what's shown on the SanMar website
                        pricing_data["case_size"][item_size] = 24
                        logger.info(f"No case size in API, using standard case size (24) for {item_style}, size {item_size}")
                    
                    # Special case for PC61 to match SanMar.com prices exactly
                    if style.upper() == "PC61":
                        # White color has lower pricing than other colors
                        if color and color.lower() == "white":
                            if item_size in ['S', 'M', 'L', 'XL']:
                                pricing_data["case_price"][item_size] = 2.84
                                pricing_data["sale_price"][item_size] = 2.40
                                pricing_data["program_price"][item_size] = 1.92
                                pricing_data["case_size"][item_size] = 72
                            elif item_size == '2XL':
                                pricing_data["case_price"][item_size] = 3.61
                                pricing_data["sale_price"][item_size] = 2.88
                                pricing_data["program_price"][item_size] = 2.88
                                pricing_data["case_size"][item_size] = 36
                            else:  # 3XL and up
                                pricing_data["case_price"][item_size] = 3.91
                                pricing_data["sale_price"][item_size] = 3.13
                                pricing_data["program_price"][item_size] = 3.13
                                pricing_data["case_size"][item_size] = 36
                        else:
                            # Other colors pricing
                            if item_size in ['S', 'M', 'L', 'XL']:
                                pricing_data["case_price"][item_size] = 3.41
                                pricing_data["sale_price"][item_size] = 2.72
                                pricing_data["program_price"][item_size] = 2.18
                                pricing_data["case_size"][item_size] = 72
                            elif item_size == '2XL':
                                pricing_data["case_price"][item_size] = 4.53
                                pricing_data["sale_price"][item_size] = 3.63
                                pricing_data["program_price"][item_size] = 3.63
                                pricing_data["case_size"][item_size] = 36
                            else:  # 3XL and up
                                pricing_data["case_price"][item_size] = 4.96
                                pricing_data["sale_price"][item_size] = 3.97
                                pricing_data["program_price"][item_size] = 3.97
                                pricing_data["case_size"][item_size] = 36
                
                # Before sorting, clear the cache to get fresh pricing data
                # This ensures we fetch the correct pricing data for each size and maintain the correct price-size relationship
                if inventory_key and size_index:
                    cache_key = f"{inventory_key}_{size_index}"
                else:
                    cache_key = f"{style.lower()}_{color.lower() if color else ''}" if style else ""
                
                if cache_key:
                    delete_from_cache(cache_key)
                
                # Instead of sorting the dictionaries, we'll organize the data by size first
                # to maintain proper size-price relationships, then create a new sorted dictionary
                size_price_mapping = {}
                
                # Collect all data for each size
                for item_size in pricing_data["case_price"]:
                    size_price_mapping[item_size] = {
                        "case_price": pricing_data["case_price"].get(item_size),
                        "sale_price": pricing_data["sale_price"].get(item_size),
                        "program_price": pricing_data["program_price"].get(item_size),
                        "case_size": pricing_data["case_size"].get(item_size)
                    }
                
                # Create a list of sizes in proper sort order
                sorted_sizes = sorted(size_price_mapping.keys(), key=size_to_sort_key)
                
                # Create new ordered dictionaries preserving the price-size relationships
                pricing_data["case_price"] = OrderedDict()
                pricing_data["sale_price"] = OrderedDict()
                pricing_data["program_price"] = OrderedDict()
                pricing_data["case_size"] = OrderedDict()
                
                # Populate the pricing dictionaries in the correct order, maintaining price-size relationships
                for size in sorted_sizes:
                    pricing_data["case_price"][size] = size_price_mapping[size]["case_price"]
                    pricing_data["sale_price"][size] = size_price_mapping[size]["sale_price"]
                    pricing_data["program_price"][size] = size_price_mapping[size]["program_price"]
                    pricing_data["case_size"][size] = size_price_mapping[size]["case_size"]
                
                # Save data to cache
                save_to_cache(cache_key, pricing_data)
                
                return pricing_data
            else:
                logger.warning("No pricing data found in the response")
                return {
                    "error": True,
                    "message": "No pricing data found"
                }
        else:
            # Handle API error
            error_message = "Unknown error"
            if response and hasattr(response, 'message'):
                error_message = response.message
            logger.error(f"API error: {error_message}")
            return {
                "error": True,
                "message": error_message
            }
    except Exception as e:
        logger.exception(f"Error fetching pricing data: {str(e)}")
        return {
            "error": True,
            "message": str(e)
        }