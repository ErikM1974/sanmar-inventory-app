import os
import logging
from functools import lru_cache
from zeep import Client, Settings
from zeep.transports import Transport
from zeep.exceptions import Fault
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from dotenv import load_dotenv

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# --- SanMar API Credentials ---
USERNAME = os.getenv("SANMAR_USERNAME")
PASSWORD = os.getenv("SANMAR_PASSWORD")
CUSTOMER_NUMBER = os.getenv("SANMAR_CUSTOMER_NUMBER")

# --- SanMar WSDL URL for Product Info ---
PRODUCT_INFO_WSDL = "https://ws.sanmar.com:8080/SanMarWebService/SanMarProductInfoServicePort?wsdl"

# --- SanMar Categories (from documentation page 31) ---
SANMAR_CATEGORIES = [
    "Activewear", "Accessories", "Bags", "Bottoms", "Caps",
    "Infant & Toddler", "Juniors & Young Men", "Outerwear",
    "Polos/Knits", "Sweatshirts/Fleece", "T-Shirts", "Tall",
    "Women’s", "Workwear", "Woven Shirts", "Youth"
]

# --- Zeep Client Setup ---
product_info_client = None
try:
    # Configure retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504]
    )
    # Create transport with timeouts and retries
    transport = Transport(timeout=30) # Increased timeout for potentially large category calls
    transport.session.mount('https://', HTTPAdapter(max_retries=retry_strategy))

    # Zeep settings - strict=False might be needed depending on WSDL quirks
    settings = Settings(strict=False, xml_huge_tree=True)

    # Initialize SOAP client
    product_info_client = Client(wsdl=PRODUCT_INFO_WSDL, transport=transport, settings=settings)
    logger.info("Successfully initialized SanMar Product Info SOAP client")
except Exception as e:
    logger.error(f"Error initializing SanMar Product Info SOAP client: {str(e)}")
    product_info_client = None

# --- Authentication Helper ---
def get_auth_details():
    """Returns the authentication dictionary for SanMar standard calls."""
    if not all([CUSTOMER_NUMBER, USERNAME, PASSWORD]):
        logger.warning("SanMar credentials (Customer Number, Username, Password) not fully set.")
        return None
    return {
        'sanMarCustomerNumber': CUSTOMER_NUMBER,
        'sanMarUserName': USERNAME,
        'sanMarUserPassword': PASSWORD
        # 'senderId': '?', # Per docs, do not use
        # 'senderPassword': '?' # Per docs, do not use
    }

# --- Service Functions ---

def get_categories():
    """Returns the list of predefined SanMar categories."""
    return SANMAR_CATEGORIES

@lru_cache(maxsize=32) # Cache results for up to 32 different categories
def get_products_by_category(category_name):
    """
    Fetches product list (style, title, image) for a given category using SanMar API.

    Args:
        category_name (str): The SanMar category name.

    Returns:
        tuple: A tuple containing (products_list, raw_response_string)
    """
    if not product_info_client:
        logger.error("Product Info client not initialized.")
        return [], "Product Info client not initialized."

    auth_details = get_auth_details()
    if not auth_details:
        logger.error("Authentication details missing, cannot call getProductInfoByCategory.")
        return [], "Authentication details missing."

    logger.info(f"Attempting to fetch products for category: {category_name}")
    
    # Enhanced logging for debugging
    logger.info(f"Category search: '{category_name}' - Starting API call")

    try:
        # Enhanced logging for debugging
        logger.info(f"Category search: '{category_name}' - Starting API call with detailed logging")
        
        # Log the exact category name and check for special characters
        logger.info(f"Category name: '{category_name}', Length: {len(category_name)}, ASCII: {[ord(c) for c in category_name]}")
        
        # Map common category names to SanMar API category names
        category_mapping = {
            "T-SHIRTS": "T-Shirts",
            "POLOS": "Polos/Knits",
            "SWEATSHIRTS": "Sweatshirts/Fleece",
            "FLEECE": "Sweatshirts/Fleece",
            "OUTERWEAR": "Outerwear",
            "WOVEN": "Woven Shirts",
            "CAPS": "Caps",
            "BAGS": "Bags",
            "ACCESSORIES": "Accessories",
            "WORKWEAR": "Workwear",
            "LADIES": "Women's",
            "WOMEN'S": "Women's",
            "YOUTH": "Youth",
            "BOTTOMS": "Bottoms",
            "PROTECTION": "Workwear"  # Map Personal Protection to Workwear as a fallback
        }
        
        # Check if the category is in our mapping
        if category_name.upper() in category_mapping:
            mapped_category = category_mapping[category_name.upper()]
            logger.info(f"Mapped category '{category_name}' to '{mapped_category}'")
            category_name = mapped_category
        # Check if the category is in the predefined list
        elif category_name not in SANMAR_CATEGORIES:
            logger.warning(f"Category '{category_name}' is not in the predefined list: {SANMAR_CATEGORIES}")
            # Try to find a close match
            close_matches = [c for c in SANMAR_CATEGORIES if c.lower() == category_name.lower()]
            if close_matches:
                logger.info(f"Found close match for '{category_name}': '{close_matches[0]}'")
                category_name = close_matches[0]
            else:
                # If no exact match, try to find a partial match
                partial_matches = [c for c in SANMAR_CATEGORIES if category_name.lower() in c.lower() or c.lower() in category_name.lower()]
                if partial_matches:
                    logger.info(f"Found partial match for '{category_name}': '{partial_matches[0]}'")
                    category_name = partial_matches[0]
        
        request_data = {
            'arg0': {'category': category_name},
            'arg1': auth_details
        }
        
        # Log the exact request data being sent
        logger.info(f"Request data: {request_data}")

        # Make the SOAP call
        logger.info(f"Making SOAP call to getProductInfoByCategory with category: {category_name}")
        try:
            response = product_info_client.service.getProductInfoByCategory(**request_data)
            logger.info(f"SOAP call successful for category: {category_name}")
        except Exception as e:
            logger.error(f"SOAP call failed for category: {category_name}, Error: {str(e)}")
            return [], f"SOAP call failed: {str(e)}"

        # Log the raw response for debugging
        logger.info(f"Raw SanMar response for category {category_name}: {response}")

        # Process the response
        products = []
        raw_response_str = str(response) # Store raw response as string

        if response and response.return_ and not response.return_.errorOccured and response.return_.listResponse:
            # Ensure listResponse is iterable (might be single object or list)
            list_responses = response.return_.listResponse
            if not isinstance(list_responses, list):
                list_responses = [list_responses]
                logger.info(f"Converting single listResponse to list for category: {category_name}")
            else:
                logger.info(f"listResponse is already a list with {len(list_responses)} items")

            for idx, item in enumerate(list_responses):
                if hasattr(item, 'productBasicInfo') and hasattr(item, 'productImageInfo'):
                    basic_info = item.productBasicInfo
                    image_info = item.productImageInfo
                    
                    # Log the basic product info for debugging
                    style = getattr(basic_info, 'style', 'N/A')
                    title = getattr(basic_info, 'productTitle', 'N/A')
                    logger.info(f"Processing product {idx+1}/{len(list_responses)}: {style} - {title}")

                    # Prefer front model, fallback to product image, then thumbnail
                    image_url = getattr(image_info, 'frontModel', None)
                    if not image_url:
                        image_url = getattr(image_info, 'productImage', None)
                        if image_url:
                            logger.info(f"Using productImage for {style} (frontModel not available)")
                    if not image_url:
                        image_url = getattr(image_info, 'thumbnailImage', None)
                        if image_url:
                            logger.info(f"Using thumbnailImage for {style} (frontModel and productImage not available)")
                    
                    if not image_url:
                        logger.warning(f"No image URL found for product {style}")
                        # Don't use a placeholder - only use images from the API
                        image_url = ""

                    # Create a product data structure compatible with search_results.html template
                    product_data = {
                        'style': style,
                        'name': title,  # Template uses 'name' not 'title'
                        'image': image_url,  # Template uses 'image' not 'image_url'
                        'brand': getattr(basic_info, 'brand', 'SanMar'),  # Add brand info
                        'colors': []  # Empty colors list for now
                    }
                    products.append(product_data)
                else:
                    logger.warning(f"Item {idx+1} missing productBasicInfo or productImageInfo")

            logger.info(f"Found {len(products)} products for category: {category_name}")
            # Return both products and raw response string
            return products, raw_response_str
        elif response and response.return_ and response.return_.errorOccured:
             error_message = response.return_.message
             logger.error(f"API error fetching category {category_name}: {error_message}")
             # Return empty list and the raw response (which contains the error)
             return [], raw_response_str
        else:
            logger.info(f"No products found or unexpected response structure for category: {category_name}")
            # Return empty list and the raw response
            return [], raw_response_str

    except Fault as fault:
        logger.error(f"SOAP Fault fetching category {category_name}: {fault.message}")
        # Return empty list and error string
        return [], f"SOAP Fault: {fault.message}"
    except Exception as e:
        # Catch potential timeouts or other request errors
        logger.error(f"Error fetching category {category_name}: {str(e)}")
        # Return empty list and error string
        return [], f"Exception: {str(e)}"

# Example usage (for testing)
if __name__ == '__main__':
    print("Available Categories:")
    print(get_categories())

    print("\nFetching products for 'Caps'...")
    caps_products, raw_response = get_products_by_category("Caps")
    if caps_products:
        print(f"Found {len(caps_products)} caps.")
        # print(caps_products[0]) # Print first product as example
    else:
        print("Could not fetch caps.")
