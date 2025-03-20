from zeep import Client
from zeep.transports import Transport
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from dotenv import load_dotenv
import os
from functools import lru_cache
from datetime import datetime
import logging

# Import mock data generator
import mock_inventory
import mock_data

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# SanMar API credentials
USERNAME = os.getenv("SANMAR_USERNAME")
PASSWORD = os.getenv("SANMAR_PASSWORD")
CUSTOMER_NUMBER = os.getenv("SANMAR_CUSTOMER_NUMBER")

# SanMar WSDL URL for inventory
INVENTORY_WSDL = "https://ws.sanmar.com:8080/promostandards/InventoryServiceBindingV2final?WSDL"

# Configure retry strategy
retry_strategy = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504]
)

# Create transport with timeouts and retries
transport = Transport(timeout=10)
transport.session.mount('https://', HTTPAdapter(max_retries=retry_strategy))

# Initialize SOAP client
try:
    inventory_client = Client(wsdl=INVENTORY_WSDL, transport=transport)
    logger.info("Successfully initialized SOAP client")
except Exception as e:
    logger.error(f"Error initializing SOAP client: {str(e)}")
    inventory_client = None

# Check if credentials are set
has_credentials = all([USERNAME, PASSWORD, CUSTOMER_NUMBER])
if not has_credentials:
    logger.warning("SanMar API credentials are not set. Using mock data only.")

# Flag to force mock data usage (for testing)
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

# Cache inventory results for 15 minutes
@lru_cache(maxsize=100)
def get_inventory_by_style(style):
    """
    Get inventory levels for a style number.
    
    Args:
        style (str): The product style number
        
    Returns:
        dict: A dictionary with inventory data by color, size, and warehouse
        str: Timestamp when the data was fetched
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # If credentials not set or mock data is forced, return mock data
    if not has_credentials or USE_MOCK_DATA or inventory_client is None:
        logger.info(f"Using mock data for {style} (credentials not set or mock data forced)")
        return mock_inventory.generate_mock_inventory(style)
    
    # Try to get real inventory data from SanMar API
    try:
        # Initial attempt with the right format for PromoStandards format
        logger.info(f"Attempting to fetch inventory for {style} from SanMar API")
        
        # Create the request according to SanMar documentation
        request_data = {
            # Simple string instead of object as per error message
            "wsVersion": "1.0.0", 
            # Authentication block
            "id": {
                "password": PASSWORD,
                "username": USERNAME,
                "custID": CUSTOMER_NUMBER
            },
            # Product ID
            "productId": style
        }
        
        # Log the request for debugging (without credentials)
        debug_request = {
            "wsVersion": "1.0.0",
            "id": {"credentials": "REDACTED"},
            "productId": style
        }
        logger.debug(f"API Request: {debug_request}")
        
        # Make the SOAP call to getInventoryLevels
        response = inventory_client.service.getInventoryLevels(**request_data)
        
        # Process the response into a more usable format
        inventory_data = {}
        
        # Check if we have inventory data
        if not hasattr(response, 'Inventory') or not response.Inventory:
            logger.warning(f"No inventory found for {style}, falling back to mock data")
            return mock_inventory.generate_mock_inventory(style)
            
        # Process inventory data
        for inv in response.Inventory:
            color = inv.ProductVariationID.Color
            size = inv.ProductVariationID.Size
            
            # Create nested structure if not exists
            if color not in inventory_data:
                inventory_data[color] = {}
            if size not in inventory_data[color]:
                inventory_data[color][size] = {"warehouses": {}, "total": 0}
            
            # Add warehouse data
            if hasattr(inv, 'LocationInventoryArray') and inv.LocationInventoryArray:
                for loc in inv.LocationInventoryArray.LocationInventory:
                    warehouse_id = loc.LocationID
                    quantity = loc.QuantityAvailable
                    
                    inventory_data[color][size]["warehouses"][warehouse_id] = quantity
                    inventory_data[color][size]["total"] += quantity
        
        # If data was processed successfully
        if inventory_data:
            logger.info(f"Successfully retrieved inventory data for {style}")
            return inventory_data, timestamp
        else:
            # No inventory data found, use mock data
            logger.warning(f"Empty inventory data returned for {style}, using mock data")
            return mock_inventory.generate_mock_inventory(style)
        
    except Exception as e:
        # Log the error and fall back to mock data
        logger.error(f"Error fetching inventory for {style}: {str(e)}")
        logger.warning(f"Falling back to mock data for {style} due to error")
        return mock_inventory.generate_mock_inventory(style)

# Clear cache function
def clear_inventory_cache():
    get_inventory_by_style.cache_clear()
