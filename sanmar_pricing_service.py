import logging
import zeep
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from zeep.transports import Transport
import os
import time
from threading import Lock

# Set up logging
logger = logging.getLogger(__name__)

class PricingCache:
    """Simple in-memory cache for pricing data with TTL"""
    def __init__(self, ttl=900):  # Default TTL: 15 minutes (900 seconds)
        self.cache = {}
        self.lock = Lock()
        self.ttl = ttl
    
    def get(self, key):
        """Get item from cache if it exists and hasn't expired"""
        with self.lock:
            if key in self.cache:
                timestamp, data = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    return data
                else:
                    # Expired item
                    del self.cache[key]
            return None
    
    def set(self, key, data):
        """Store item in cache with current timestamp"""
        with self.lock:
            self.cache[key] = (time.time(), data)
    
    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
    
    def cleanup(self):
        """Remove expired entries"""
        with self.lock:
            now = time.time()
            expired_keys = [k for k, (timestamp, _) in self.cache.items()
                           if now - timestamp >= self.ttl]
            for k in expired_keys:
                del self.cache[k]

class SanmarPricingService:
    """
    Client for the SanMar Pricing Service
    This provides direct pricing information for specific style/color/size combinations
    """
    
    def __init__(self, username, password, customer_number, environment="production"):
        """
        Initialize the SanMar Pricing Service client
        
        Args:
            username (str): SanMar API username
            password (str): SanMar API password
            customer_number (str): SanMar customer number
            environment (str): "production" or "development"
        """
        self.username = username
        self.password = password
        self.customer_number = customer_number
        self.environment = environment
        
        # Initialize cache
        self.cache = PricingCache()
        
        # Configure retry strategy for API calls
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
        
        # Set up transport with retry strategy and timeout
        self.transport = Transport(timeout=30)
        self.transport.session.mount('https://', HTTPAdapter(max_retries=retry_strategy))
        
        # SanMar Pricing Service WSDL URL based on environment
        if environment.lower() == "development":
            self.wsdl_url = "https://edev-ws.sanmar.com:8080/SanMarWebService/SanMarPricingServicePort?wsdl"
            logger.info("Using development environment for SanMar Pricing Service")
        else:
            self.wsdl_url = "https://ws.sanmar.com:8080/SanMarWebService/SanMarPricingServicePort?wsdl"
            logger.info("Using production environment for SanMar Pricing Service")
        
        try:
            # Initialize SOAP client
            self.client = zeep.Client(wsdl=self.wsdl_url, transport=self.transport)
            logger.info("Successfully initialized SanMar Pricing Service client")
            self._ready = True
        except Exception as e:
            logger.error(f"Error initializing SanMar Pricing Service client: {str(e)}")
            self._ready = False
    
    def is_ready(self):
        """Check if the client is initialized and ready to use."""
        return self._ready
    
    def get_pricing(self, style, color=None, size=None, use_cache=True):
        """
        Fetch pricing data directly from SanMar Pricing Service using style/color/size
        
        Args:
            style (str): Product style number (e.g., "PC61")
            color (str, optional): Catalog color name
            size (str, optional): Size code
            use_cache (bool): Whether to use cached data (default: True)
        
        Returns:
            dict: Pricing data for the specified product or None if error
        """
        if not self._ready:
            logger.error("SanMar Pricing Service client not initialized")
            return None
        
        # Generate cache key
        cache_key = f"style:{style}:{color or ''}:{size or ''}"
        
        # Check cache if enabled
        if use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data:
                logger.info(f"Using cached pricing data for {cache_key}")
                return cached_data
        
        # Prepare the request data
        request_data = {
            "arg0": {
                "style": style,
                "color": color if color else "",
                "size": size if size else "",
                "casePrice": None,
                "dozenPrice": None,
                "piecePrice": None,
                "salePrice": None,
                "myPrice": None,
                "inventoryKey": None,
                "sizeIndex": None
            },
            "arg1": {
                "sanMarCustomerNumber": self.customer_number,
                "sanMarUserName": self.username,
                "sanMarUserPassword": self.password
            }
        }
        
        # Log the request for debugging (without credentials)
        debug_request = {
            "arg0": {
                "style": style,
                "color": color if color else "",
                "size": size if size else "",
            }
        }
        logger.info(f"Requesting SanMar pricing for style: {style}, color: {color if color else 'None'}, size: {size if size else 'None'}")
        
        try:
            # Call the API with timeout handling
            try:
                response = self.client.service.getPricing(**request_data)
            except Exception as e:
                if "timeout" in str(e).lower():
                    logger.error(f"Timeout error when fetching SanMar pricing: {str(e)}")
                    return None
                raise  # Re-raise if it's not a timeout error
            
            # Check for errors
            if response.errorOccurred:
                logger.error(f"API error: {response.message}")
                return None
            
            # Create our pricing data structure
            pricing_data = {
                "original_price": {},
                "sale_price": {},
                "program_price": {},
                "case_size": {},
                "color_pricing": {}
            }
            
            # Process the response
            if hasattr(response, 'listResponse') and response.listResponse:
                # Normalize colors and sizes for consistent storage
                colors_seen = set()
                
                # Process each response item
                for item in response.listResponse:
                    # Get the size and color
                    current_size = getattr(item, 'size', 'Unknown')
                    current_color = getattr(item, 'color', None)
                    
                    logger.info(f"Processing pricing for {style}, color: {current_color}, size: {current_size}")
                    
                    # Extract the price values
                    piece_price = None
                    sale_price = None
                    case_price = None
                    case_size = None
                    my_price = None
                    program_price = None
                    
                    # Try to extract the piece price
                    if hasattr(item, 'piecePrice') and item.piecePrice is not None:
                        piece_price = float(item.piecePrice)
                    
                    # Try to extract the sale price
                    if hasattr(item, 'salePrice') and item.salePrice is not None:
                        sale_price = float(item.salePrice)
                    
                    # Try to extract the case price
                    if hasattr(item, 'casePrice') and item.casePrice is not None:
                        case_price = float(item.casePrice)
                    
                    # Try to extract the customer-specific pricing
                    if hasattr(item, 'myPrice') and item.myPrice is not None:
                        my_price = float(item.myPrice)
                        # Use customer-specific pricing if available
                        program_price = my_price
                    else:
                        program_price = piece_price
                    
                    # Use piece price as primary, fall back to case price
                    price_value = piece_price if piece_price is not None else case_price
                    
                    # If we don't have either, skip this item
                    if price_value is None:
                        logger.warning(f"No price found for {style}, color: {current_color}, size: {current_size}")
                        continue
                    
                    # Get case size for this style/size
                    # Use default case sizes based on style and size
                    style_upper = style.upper()
                    if style_upper.startswith('PC61'):
                        if current_size in ['XS', 'S', 'M', 'L', 'XL']:
                            case_size = 72
                        else:  # 2XL and up
                            case_size = 36
                    elif style_upper.startswith('J790'):
                        if current_size in ['XS', 'S', 'M', 'L', 'XL', '2XL']:
                            case_size = 24
                        else:  # 3XL and up
                            case_size = 12
                    elif style_upper == 'C112':
                        case_size = 144  # Special case for caps
                    else:
                        case_size = 24  # Default
                    
                    # Add to general pricing
                    pricing_data["original_price"][current_size] = price_value
                    pricing_data["sale_price"][current_size] = sale_price if sale_price is not None else price_value
                    pricing_data["program_price"][current_size] = program_price if program_price is not None else price_value
                    pricing_data["case_size"][current_size] = case_size
                    
                    # Add color-specific pricing
                    if current_color:
                        # Normalize the color for our data structure
                        colors_seen.add(current_color)
                        
                        # Make sure this color exists in our data structure
                        if current_color not in pricing_data["color_pricing"]:
                            pricing_data["color_pricing"][current_color] = {
                                "original_price": {},
                                "sale_price": {},
                                "program_price": {},
                                "case_size": {}
                            }
                        
                        # Add the pricing data for this color and size
                        pricing_data["color_pricing"][current_color]["original_price"][current_size] = price_value
                        pricing_data["color_pricing"][current_color]["sale_price"][current_size] = sale_price if sale_price is not None else price_value
                        pricing_data["color_pricing"][current_color]["program_price"][current_size] = program_price if program_price is not None else price_value
                        pricing_data["color_pricing"][current_color]["case_size"][current_size] = case_size
                        
                        logger.info(f"Added pricing for {current_color}, size {current_size}: price={price_value}, sale={sale_price}, case_size={case_size}")
                
                # Create color pricing for default if a specific color was requested
                if color and color not in pricing_data["color_pricing"] and len(colors_seen) > 0:
                    # Use the first color we saw in the response as a fallback
                    fallback_color = next(iter(colors_seen))
                    logger.info(f"Requested color {color} not found in response, using {fallback_color} as fallback")
                    
                    pricing_data["color_pricing"][color] = pricing_data["color_pricing"][fallback_color]
                
                # Store in cache if we got valid data
                if use_cache:
                    self.cache.set(cache_key, pricing_data)
                    logger.info(f"Stored pricing data in cache for {cache_key}")
                
                return pricing_data
            else:
                logger.warning(f"No listResponse found in pricing data for style: {style}")
                return None
        
        except Exception as e:
            logger.error(f"Error fetching SanMar pricing: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def get_pricing_by_inventory_key(self, inventory_key, size_index=None, use_cache=True):
        """
        Fetch pricing data using inventory key and size index
        
        Args:
            inventory_key (str): SanMar inventory key
            size_index (str, optional): SanMar size index
            use_cache (bool): Whether to use cached data
            
        Returns:
            dict: Pricing data for the specified product or None if error
        """
        if not self._ready:
            logger.error("SanMar Pricing Service client not initialized")
            return None
        
        # Generate cache key
        cache_key = f"inventoryKey:{inventory_key}:{size_index or ''}"
        
        # Check cache if enabled
        if use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data:
                logger.info(f"Using cached pricing data for {cache_key}")
                return cached_data
        
        # Prepare the request data
        request_data = {
            "arg0": {
                "style": "",
                "color": "",
                "size": "",
                "casePrice": None,
                "dozenPrice": None,
                "piecePrice": None,
                "salePrice": None,
                "myPrice": None,
                "inventoryKey": inventory_key,
                "sizeIndex": size_index if size_index else ""
            },
            "arg1": {
                "sanMarCustomerNumber": self.customer_number,
                "sanMarUserName": self.username,
                "sanMarUserPassword": self.password
            }
        }
        
        logger.info(f"Requesting SanMar pricing for inventory key: {inventory_key}, size index: {size_index if size_index else 'None'}")
        
        try:
            # Call the API with timeout handling
            try:
                response = self.client.service.getPricing(**request_data)
            except Exception as e:
                if "timeout" in str(e).lower():
                    logger.error(f"Timeout error when fetching SanMar pricing: {str(e)}")
                    return None
                raise  # Re-raise if it's not a timeout error
            
            # Check for errors
            if response.errorOccurred:
                logger.error(f"API error: {response.message}")
                return None
            
            # Create our pricing data structure
            pricing_data = {
                "original_price": {},
                "sale_price": {},
                "program_price": {},
                "case_size": {},
                "color_pricing": {}
            }
            
            # Process the response
            if hasattr(response, 'listResponse') and response.listResponse:
                colors_seen = set()
                
                # Process each response item
                for item in response.listResponse:
                    # Get the size, color, and style
                    current_size = getattr(item, 'size', 'Unknown')
                    current_color = getattr(item, 'color', None)
                    current_style = getattr(item, 'style', None)
                    
                    logger.info(f"Processing pricing for inventoryKey: {inventory_key}, color: {current_color}, size: {current_size}")
                    
                    # Extract the price values
                    piece_price = None
                    sale_price = None
                    case_price = None
                    case_size = None
                    
                    # Try to extract various price fields
                    if hasattr(item, 'piecePrice') and item.piecePrice is not None:
                        piece_price = float(item.piecePrice)
                    
                    if hasattr(item, 'salePrice') and item.salePrice is not None:
                        sale_price = float(item.salePrice)
                        
                    if hasattr(item, 'casePrice') and item.casePrice is not None:
                        case_price = float(item.casePrice)
                        
                    if hasattr(item, 'myPrice') and item.myPrice is not None:
                        my_price = float(item.myPrice)
                        # Use customer-specific pricing if available
                        program_price = my_price
                    else:
                        program_price = piece_price
                    
                    # Use piece price as primary, fall back to case price
                    price_value = piece_price if piece_price is not None else case_price
                    
                    # If we don't have either, skip this item
                    if price_value is None:
                        logger.warning(f"No price found for inventoryKey: {inventory_key}, color: {current_color}, size: {current_size}")
                        continue
                    
                    # Get case size for this style/size
                    # Use default case sizes based on style and size if available
                    if current_style:
                        style_upper = current_style.upper()
                        if style_upper.startswith('PC61'):
                            if current_size in ['XS', 'S', 'M', 'L', 'XL']:
                                case_size = 72
                            else:  # 2XL and up
                                case_size = 36
                        elif style_upper.startswith('J790'):
                            if current_size in ['XS', 'S', 'M', 'L', 'XL', '2XL']:
                                case_size = 24
                            else:  # 3XL and up
                                case_size = 12
                        elif style_upper == 'C112':
                            case_size = 144  # Special case for caps
                        else:
                            case_size = 24  # Default
                    else:
                        case_size = 24  # Default case size
                    
                    # Add to general pricing
                    pricing_data["original_price"][current_size] = price_value
                    pricing_data["sale_price"][current_size] = sale_price if sale_price is not None else price_value
                    pricing_data["program_price"][current_size] = program_price
                    pricing_data["case_size"][current_size] = case_size
                    
                    # Add color-specific pricing
                    if current_color:
                        # Normalize the color for our data structure
                        colors_seen.add(current_color)
                        
                        # Make sure this color exists in our data structure
                        if current_color not in pricing_data["color_pricing"]:
                            pricing_data["color_pricing"][current_color] = {
                                "original_price": {},
                                "sale_price": {},
                                "program_price": {},
                                "case_size": {}
                            }
                        
                        # Add the pricing data for this color and size
                        pricing_data["color_pricing"][current_color]["original_price"][current_size] = price_value
                        pricing_data["color_pricing"][current_color]["sale_price"][current_size] = sale_price if sale_price is not None else price_value
                        pricing_data["color_pricing"][current_color]["program_price"][current_size] = program_price
                        pricing_data["color_pricing"][current_color]["case_size"][current_size] = case_size
                        
                        logger.info(f"Added pricing for {current_color}, size {current_size}: price={price_value}, sale={sale_price}, case_size={case_size}")
                
                # Store in cache if we got valid data
                if use_cache:
                    self.cache.set(cache_key, pricing_data)
                    logger.info(f"Stored pricing data in cache for {cache_key}")
                
                return pricing_data
            else:
                logger.warning(f"No listResponse found in pricing data for inventory key: {inventory_key}")
                return None
        
        except Exception as e:
            logger.error(f"Error fetching SanMar pricing: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None