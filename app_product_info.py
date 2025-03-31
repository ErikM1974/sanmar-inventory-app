import logging
import json
from zeep import Client
from zeep.transports import Transport
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from dotenv import load_dotenv
import os
from functools import lru_cache
from datetime import datetime
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# SanMar API credentials
USERNAME = os.getenv("SANMAR_USERNAME")
PASSWORD = os.getenv("SANMAR_PASSWORD")
CUSTOMER_NUMBER = os.getenv("SANMAR_CUSTOMER_NUMBER")

# SanMar WSDL URL for product info
PRODUCT_INFO_WSDL = "https://ws.sanmar.com:8080/SanMarWebService/SanMarProductInfoServicePort?wsdl"

# Configure retry strategy
retry_strategy = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504]
)

# Create transport with timeouts and retries
transport = Transport(timeout=15)
transport.session.mount('https://', HTTPAdapter(max_retries=retry_strategy))

# Initialize SOAP client
try:
    product_client = Client(wsdl=PRODUCT_INFO_WSDL, transport=transport)
    logger.info("Successfully initialized Product Info SOAP client")
except Exception as e:
    logger.error(f"Error initializing Product Info SOAP client: {str(e)}")
    product_client = None

# Check if credentials are set
has_credentials = all([USERNAME, PASSWORD, CUSTOMER_NUMBER])
if not has_credentials:
    logger.warning("SanMar API credentials are not set. Using mock data only.")

# Cache for product data (TTL: 24 hours)
PRODUCT_CACHE = {}
CACHE_TTL = 86400  # 24 hours in seconds

@lru_cache(maxsize=50)
def get_product_info_by_category(category_name):
    """
    Get product information for a specific category using the SanMar API.
    
    Args:
        category_name (str): Category name to fetch products for
        
    Returns:
        dict: Dictionary containing product information
    """
    cache_key = f"category_{category_name}"
    
    # Check cache first
    if cache_key in PRODUCT_CACHE:
        cache_entry = PRODUCT_CACHE[cache_key]
        if time.time() - cache_entry['timestamp'] < CACHE_TTL:
            logger.info(f"Using cached product info for category: {category_name}")
            return cache_entry['data']
    
    # If credentials not set or client not initialized, return mock data
    if not has_credentials or not product_client:
        logger.info(f"Using mock data for category: {category_name} (credentials not set or client not initialized)")
        return get_mock_product_info(category_name)
    
    try:
        # Map the category name to the SanMar API category name
        sanmar_category_name = map_category_name(category_name)
        logger.info(f"Fetching product info for category: {category_name} (mapped to: {sanmar_category_name})")
        
        # Create the request for getProductInfoByCategory
        request_data = {
            "arg0": {"category": sanmar_category_name},
            "arg1": {
                "sanMarCustomerNumber": CUSTOMER_NUMBER,
                "sanMarUserName": USERNAME,
                "sanMarUserPassword": PASSWORD
            }
        }
        
        # Log the request for debugging (without credentials)
        debug_request = {
            "arg0": {"category": category_name},
            "arg1": {
                "sanMarCustomerNumber": "REDACTED",
                "sanMarUserName": "REDACTED",
                "sanMarUserPassword": "REDACTED"
            }
        }
        logger.debug(f"Product Info API Request: {debug_request}")
        
        # Make the SOAP call to getProductInfoByCategory
        response = product_client.service.getProductInfoByCategory(**request_data)
        
        # Process the response
        if hasattr(response, 'errorOccured') and response.errorOccured:
            logger.error(f"API error for category {category_name}: {getattr(response, 'message', 'Unknown error')}")
            return None
        
        # Check if we have a listResponse
        if not hasattr(response, 'listResponse') or not response.listResponse:
            logger.warning(f"No listResponse found in API response for category: {category_name}")
            return None
        
        # Convert response to a usable format
        try:
            from zeep.helpers import serialize_object
            response_dict = serialize_object(response)
            
            # Store in cache
            PRODUCT_CACHE[cache_key] = {
                'data': response_dict,
                'timestamp': time.time()
            }
            
            # Log success
            product_count = len(response_dict.get('listResponse', []))
            logger.info(f"Successfully fetched {product_count} products for category: {category_name}")
            
            return response_dict
        except Exception as e:
            logger.error(f"Error serializing API response for category {category_name}: {str(e)}")
            return None
    
    except Exception as e:
        logger.error(f"Error fetching product info for category {category_name}: {str(e)}")
        return get_mock_product_info(category_name)

def extract_model_image_url(product_data, image_type='frontModel'):
    """
    Extract a specific type of image URL from product data
    
    Args:
        product_data (dict): Product data from SanMar API
        image_type (str): Type of image to extract (frontModel, backModel, etc.)
        
    Returns:
        str: Image URL or None if not found
    """
    if not product_data or 'listResponse' not in product_data:
        return None
    
    # Go through each product in the listResponse
    for product in product_data['listResponse']:
        # Check if this product has image info
        if 'productImageInfo' in product:
            image_info = product['productImageInfo']
            
            # Check if the requested image type exists
            if image_type in image_info and image_info[image_type]:
                image_url = image_info[image_type]
                logger.info(f"Found {image_type} image URL: {image_url}")
                return image_url
    
    # If we get here, no matching image was found
    logger.warning(f"No {image_type} image found in product data")
    return None

# Category-specific fallback images for when API doesn't return valid images
CATEGORY_FALLBACK_IMAGES = {
    # Base categories
    'TSHIRTS': 'https://cdnm.sanmar.com/imglib/mresjpg/2017/f4/29M_white_model_front_032017.jpg',
    'POLOS': 'https://cdnm.sanmar.com/imglib/mresjpg/2017/f3/054X_white_model_front_032017.jpg',
    'OUTERWEAR': 'https://cdnm.sanmar.com/imglib/mresjpg/2021/f6/J730_blackpewter_model_front.jpg',
    'WOVEN_SHIRTS': 'https://cdnm.sanmar.com/imglib/mresjpg/2016/f17/S100_darkbluestonewashed_model_front_102016.jpg',
    'SWEATSHIRTS': 'https://cdnm.sanmar.com/imglib/mresjpg/2017/f4/4662M_ash_model_front_032017.jpg',
    'WORKWEAR': 'https://cdnm.sanmar.com/imglib/mresjpg/2016/f19/J763_duckbrown_model_front_102016.jpg',
    'BAGS': 'https://cdnm.sanmar.com/imglib/mresjpg/B100_Flat_Natural.jpg',
    'ACCESSORIES': 'https://cdnm.sanmar.com/imglib/mresjpg/A500_Black_Model_Front.jpg',
    
    # Problem categories with updated reliable image URLs
    'HEADWEAR': 'https://cdnm.sanmar.com/imglib/mresjpg/2016/f2/C112_navy_model_front_012016.jpg',
    'BOTTOMS': 'https://cdnm.sanmar.com/imglib/mresjpg/2019/f5/PT88_black_model_front.jpg',
    'ACTIVEWEAR': 'https://cdnm.sanmar.com/imglib/mresjpg/2019/f2/ST650_trueblue_model_front_022019.jpg',
    'WOMENS': 'https://cdnm.sanmar.com/imglib/mresjpg/2014/f16/L500_black_model_front_072014.jpg',
    'INFANT_TODDLER': 'https://cdnm.sanmar.com/imglib/mresjpg/2019/f7/3321_white_model_front_072019.jpg',
    'JUNIORS_YOUNG_MEN': 'https://cdnm.sanmar.com/imglib/mresjpg/2019/f8/DT6000_black_model_front_082019.jpg',
    'YOUTH': 'https://cdnm.sanmar.com/imglib/mresjpg/2019/f6/PC61Y_white_model_front_062019.jpg',
    'TALL': 'https://cdnm.sanmar.com/imglib/mresjpg/2022/f2/TLJ754_trueblacktrueblack_model_front.jpg'
}

def get_category_image(category_name):
    """
    Get a representative image URL for a category
    
    Args:
        category_name (str): Category name
        
    Returns:
        str: Image URL or None if not found
    """
    # Get product data for this category
    product_data = get_product_info_by_category(category_name)
    
    # Extract the front model image URL
    image_url = extract_model_image_url(product_data, 'frontModel')
    
    # If no front model image, try colorProductImage
    if not image_url:
        image_url = extract_model_image_url(product_data, 'colorProductImage')
    
    # If still no image, try productImage
    if not image_url:
        image_url = extract_model_image_url(product_data, 'productImage')
    
    # If no image found from API, use category-specific fallback
    if not image_url:
        # Check if we have a fallback for this category
        if category_name in CATEGORY_FALLBACK_IMAGES:
            image_url = CATEGORY_FALLBACK_IMAGES[category_name]
            logger.info(f"Using category-specific fallback image for {category_name}: {image_url}")
    
    # Return the image URL or None if not found
    return image_url

def clear_product_cache():
    """Clear the product info cache"""
    global PRODUCT_CACHE
    PRODUCT_CACHE = {}
    get_product_info_by_category.cache_clear()
    logger.info("Product info cache cleared")

# Map our internal category IDs to SanMar API category names
def map_category_name(category_id):
    """
    Map internal category ID to SanMar API category name
    
    Args:
        category_id (str): Internal category ID
        
    Returns:
        str: SanMar API category name
    """
    category_mapping = {
        # Map internal IDs to SanMar category names
        "TSHIRTS": "T-Shirts",
        "POLOS": "Polos/Knits",
        "OUTERWEAR": "Outerwear",
        "WOVEN_SHIRTS": "Woven Shirts",
        "SWEATSHIRTS": "Sweatshirts/Fleece",
        "HEADWEAR": "Caps",
        "WORKWEAR": "Workwear",
        "BAGS": "Bags",
        "ACCESSORIES": "Accessories",
        "BOTTOMS": "Pants",
        "ACTIVEWEAR": "Active",
        # In case SanMar API uses the display names directly
        "T-Shirts": "T-Shirts",
        "Polos/Knits": "Polos/Knits",
        "Outerwear": "Outerwear",
        "Woven Shirts": "Woven Shirts",
        "Sweatshirts/Fleece": "Sweatshirts/Fleece",
        "Caps": "Caps",
        "Workwear": "Workwear",
        "Bags": "Bags",
        "Accessories": "Accessories",
        "Pants": "Pants",
        "Active": "Active"
    }
    
    # Return mapped name or original if no mapping exists
    return category_mapping.get(category_id, category_id)

def get_mock_product_info(category_name):
    """
    Generate mock product data for testing
    
    Args:
        category_name (str): Category name
        
    Returns:
        dict: Mock product data
    """
    # Map of categories to mock style numbers and SanMar category names
    category_style_map = {
        "T-Shirts": "PC61",
        "Polos/Knits": "K500",
        "Outerwear": "J790",
        "Woven Shirts": "S628",
        "Sweatshirts/Fleece": "PC90H",
        "Caps": "C112",
        "Workwear": "SP24",
        "Bags": "BG408",
        "Accessories": "A525"
    }
    
    # Default style for unknown categories
    style = category_style_map.get(category_name, "PC61")
    
    # Create a mock response structure
    return {
        "errorOccured": False,
        "message": "Mock product information",
        "listResponse": [
            {
                "productBasicInfo": {
                    "style": style,
                    "color": "Black",
                    "productTitle": f"Mock {category_name} Product - {style}"
                },
                "productImageInfo": {
                    "frontModel": f"https://www.sanmar.com/products/catalog/2023/f1/port_authority/fullsize/{style}_Black_Model_Front_2023.jpg",
                    "colorProductImage": f"https://www.sanmar.com/products/catalog/2023/f1/port_authority/fullsize/{style}_Black_Model_Front_2023.jpg",
                    "productImage": f"https://www.sanmar.com/catalog/images/{style}.jpg"
                }
            }
        ]
    }