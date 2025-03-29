import os
import logging
from zeep import Client
from zeep.transports import Transport
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from dotenv import load_dotenv
from functools import lru_cache
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# SanMar API credentials
SANMAR_USERNAME = os.getenv('SANMAR_USERNAME')
SANMAR_PASSWORD = os.getenv('SANMAR_PASSWORD')

# SanMar WSDL URL for Media Content Service
MEDIA_WSDL = "https://ws.sanmar.com:8080/promostandards/MediaContentServiceBinding?wsdl"

# Configure retry strategy
retry_strategy = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504]
)

# Create transport with timeouts and retries
transport = Transport(timeout=15) # Increased timeout for potentially larger media responses
transport.session.mount('https://', HTTPAdapter(max_retries=retry_strategy))

# Initialize SOAP client for Media Content Service
try:
    media_client = Client(wsdl=MEDIA_WSDL, transport=transport)
    logger.info(f"Available operations: {media_client.service._operations.keys()}")
    logger.info("Successfully initialized Media Content Service SOAP client")
except Exception as e:
    logger.error(f"Error initializing Media Content Service SOAP client: {str(e)}")
    media_client = None

# Check if credentials are set
has_credentials = all([SANMAR_USERNAME, SANMAR_PASSWORD])
if not has_credentials:
    logger.warning("SanMar API credentials are not set. Media service may not function.")

# Flag to force mock data usage (for testing)
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

# Representative products for categories (fallback if API fails)
CATEGORY_REPRESENTATIVE_PRODUCTS = {
    "T-SHIRTS": "PC61",
    "POLOS": "K500",
    "SWEATSHIRTS": "PC78", # Example, replace with actual common sweatshirt
    "FLEECE": "F280", # Example, replace with actual common fleece
    "OUTERWEAR": "J790",
    "WOVEN": "S608", # Example, replace with actual common woven shirt
    "CAPS": "C112",
    "BAGS": "BG400", # Example, replace with actual common bag
    "ACCESSORIES": "TW50", # Example, replace with actual common accessory
    "WORKWEAR": "CS410", # Example, replace with actual common workwear
    "LADIES": "L500",
    "YOUTH": "PC61Y", # Example, replace with actual common youth style
    "BOTTOMS": "PT74", # Example, replace with actual common bottom
    "ACTIVEWEAR": "ST350"
}

# Simple time-based cache (dictionary)
_media_cache = {}
CACHE_DURATION = timedelta(minutes=30)

class SanMarMediaService:
    def __init__(self):
        if not media_client:
            logger.error("Media Content Service client is not initialized.")

    def _get_from_cache(self, key):
        """Check cache for valid data."""
        if key in _media_cache:
            data, timestamp = _media_cache[key]
            if datetime.now() - timestamp < CACHE_DURATION:
                logger.info(f"Cache hit for key: {key}")
                return data
            else:
                logger.info(f"Cache expired for key: {key}")
                del _media_cache[key]
        return None

    def _set_cache(self, key, data):
        """Set data in cache with timestamp."""
        _media_cache[key] = (data, datetime.now())
        logger.info(f"Cache set for key: {key}")

    @lru_cache(maxsize=200) # Use LRU cache for individual product media calls
    def get_media_content(self, product_id, media_type="Image", part_id=None, class_type=None):
        """
        Get media content for a product from SanMar API.

        Args:
            product_id (str): SanMar product ID (style number)
            media_type (str): Type of media (Image or Document)
            part_id (str, optional): Specific part ID (unique key)
            class_type (int, optional): Specific class type ID

        Returns:
            list: List of media content dictionaries, or None if error
        """
        cache_key = f"media_{product_id}_{media_type}_{part_id}_{class_type}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        if not has_credentials or USE_MOCK_DATA or media_client is None:
            logger.warning(f"Using mock/fallback for media content for {product_id} (no credentials/mock forced/client error)")
            # Return a basic fallback structure or None
            return None

        try:
            logger.info(f"Fetching media content for product {product_id} (Type: {media_type})")
            request_data = {
                "wsVersion": "1.1.0",
                "id": SANMAR_USERNAME,
                "password": SANMAR_PASSWORD,
                "mediaType": media_type,
                "productId": product_id,
            }
            if part_id:
                request_data["partId"] = part_id
            if class_type:
                request_data["classType"] = class_type

            response = media_client.service.getMediaContent(**request_data)

            if response and hasattr(response, 'MediaContentArray') and response.MediaContentArray:
                from zeep.helpers import serialize_object
                media_list = serialize_object(response.MediaContentArray.MediaContent)
                # Handle case where only one item is returned (not as a list)
                if not isinstance(media_list, list):
                    media_list = [media_list] if media_list else []

                self._set_cache(cache_key, media_list)
                return media_list
            else:
                logger.warning(f"No media content found for product {product_id}")
                self._set_cache(cache_key, []) # Cache empty result
                return []

        except Exception as e:
            logger.error(f"Error fetching media content for {product_id}: {str(e)}")
            return None # Return None on error

    def get_best_image_for_product(self, product_id, preferred_type=None):
        """
        Get the best available image URL for a product, handling potential None responses.

        Args:
            product_id (str): SanMar product ID (style number)
            preferred_type (str, optional): Preferred image type ('primary', 'front', 'high', 'rear', 'swatch', 'custom')

        Returns:
            str: URL of the best image, or a fallback URL.
        """
        fallback_url = f"https://cdnm.sanmar.com/catalog/images/{product_id}.jpg"
        try:
            media_array = self.get_media_content(product_id, media_type="Image")

            # If API call failed or returned None/empty
            if media_array is None or not media_array:
                logger.warning(f"No media array returned for {product_id}, using fallback.")
                return fallback_url

            # Define priority order for class types
            class_type_priority = {
                '1006': 1,  # Primary
                '1007': 2,  # Front
                '2001': 3,  # High
                '1008': 4,  # Rear
                '1004': 5,  # Swatch
                '500': 6,   # Custom (Treat all custom types similarly for priority)
                '502': 6,
                '503': 6,
                '504': 6,
            }

            # Map preferred_type to class type ID
            preferred_type_map = {
                'primary': '1006',
                'front': '1007',
                'high': '2001',
                'rear': '1008',
                'swatch': '1004',
                'custom': '500' # Base custom type
            }

            # If preferred type is specified, try to find that type first
            if preferred_type and preferred_type.lower() in preferred_type_map:
                preferred_class_id = preferred_type_map[preferred_type.lower()]

                for media in media_array:
                    # Robust check for media and nested structure
                    if not media: continue # Skip if media item is None

                    class_type_array_obj = media.get('ClassTypeArray')
                    if not class_type_array_obj: continue

                    class_type_list = class_type_array_obj.get('ClassType')
                    if not class_type_list: continue

                    # Handle if ClassType is not a list
                    if not isinstance(class_type_list, list):
                        class_type_list = [class_type_list]

                    if class_type_list and class_type_list[0] and class_type_list[0].get('classTypeId') == preferred_class_id:
                        image_url = media.get('url')
                        if image_url:
                            return image_url
                        else:
                            logger.warning(f"Preferred media type {preferred_class_id} found for {product_id} but URL is missing.")

            # If preferred type not found or not specified, sort by priority
            def get_sort_key(media_item):
                """Safely get the sort key (priority) for a media item."""
                if not media_item: return 999 # Low priority for None items
                class_type_array_obj = media_item.get('ClassTypeArray')
                if not class_type_array_obj: return 999
                class_type_list = class_type_array_obj.get('ClassType')
                if not class_type_list: return 999
                if not isinstance(class_type_list, list):
                    class_type_list = [class_type_list]
                if class_type_list and class_type_list[0]:
                    class_id = class_type_list[0].get('classTypeId')
                    return class_type_priority.get(class_id, 999) # Use get with default
                return 999 # Default low priority

            # Filter out None items before sorting
            valid_media_array = [m for m in media_array if m is not None]

            if not valid_media_array:
                 logger.warning(f"No valid media items found after filtering for {product_id}, using fallback.")
                 return fallback_url

            sorted_media = sorted(valid_media_array, key=get_sort_key)

            # Return the URL of the highest priority image
            if sorted_media:
                best_image_url = sorted_media[0].get('url')
                if best_image_url:
                    return best_image_url
                else:
                     logger.warning(f"Highest priority media found for {product_id} but URL is missing, using fallback.")
                     return fallback_url

            # If no image found after sorting, use fallback
            logger.warning(f"Could not determine best image for {product_id} after sorting, using fallback.")
            return fallback_url

        except Exception as e:
            logger.error(f"Error getting best image for product {product_id}: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}") # Log full traceback
            return fallback_url # Return fallback on any exception

    def get_representative_product_for_category(self, category):
        """
        Get a representative product ID for a category.

        Args:
            category (str): Category name

        Returns:
            str: Product ID
        """
        # Normalize category name
        category_upper = category.upper()

        # Return the representative product for the category
        return CATEGORY_REPRESENTATIVE_PRODUCTS.get(category_upper, 'PC61') # Default to PC61 if not found

# Create a singleton instance
_service = SanMarMediaService()

# Expose methods at the module level
def get_best_image_for_product(product_id, preferred_type=None):
    """
    Get the best available image for a product.

    Args:
        product_id (str): SanMar product ID (style number)
        preferred_type (str, optional): Preferred image type ('primary', 'front', 'high', 'rear', 'swatch')

    Returns:
        str: URL of the best image
    """
    return _service.get_best_image_for_product(product_id, preferred_type)

def get_representative_product_for_category(category):
    """
    Get a representative product ID for a category.

    Args:
        category (str): Category name

    Returns:
        str: Product ID
    """
    return _service.get_representative_product_for_category(category)