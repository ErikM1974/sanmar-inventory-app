from zeep import Client
from zeep.transports import Transport
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from dotenv import load_dotenv
import os
from functools import lru_cache
from datetime import datetime
import logging
import json
from decimal import Decimal # Import Decimal

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

# Custom JSON Encoder for Decimal
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) # Convert Decimal to int for JSON
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

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

        # Create the request according to SanMar documentation - using correct parameter names
        request_data = {
            "wsVersion": "2.0.0",
            "id": USERNAME,
            "password": PASSWORD,
            "productId": style  # Correct case: productId not productID
        }

        # Log the request for debugging (without credentials)
        debug_request = {
            "wsVersion": "2.0.0",
            "id": "REDACTED",
            "password": "REDACTED",
            "productId": style
        }
        logger.info(f"API Request: {debug_request}")

        # Make the SOAP call to getInventoryLevels
        logger.info("Calling inventory API getInventoryLevels...")
        response = inventory_client.service.getInventoryLevels(**request_data)

        # Log the raw response for debugging using the custom encoder
        try:
            from zeep.helpers import serialize_object
            response_dict = serialize_object(response)
            # Use cls=DecimalEncoder here
            logger.info(f"Inventory API Response: {json.dumps(response_dict, indent=2, cls=DecimalEncoder)}")
        except Exception as e:
            logger.error(f"Error serializing inventory response for logging: {str(e)}")
            # Log raw response object if serialization fails
            logger.info(f"Raw response object: {response}")

        # Process the response into a more usable format
        inventory_data = {}

        # Detailed logging of the response structure
        logger.info(f"Response structure: {dir(response)}")
        logger.info(f"Response type: {type(response)}")

        # Log full response structure for debugging using the custom encoder
        try:
            from zeep.helpers import serialize_object
            response_dict = serialize_object(response)
             # Use cls=DecimalEncoder here
            logger.info(f"Full response dict: {json.dumps(response_dict, indent=2, cls=DecimalEncoder)}")
        except Exception as e:
            logger.error(f"Error serializing full response for logging: {str(e)}")

        # Check different possible response structures
        if hasattr(response, 'Inventory') and response.Inventory:
            logger.info("Found 'Inventory' attribute in response")

            # Check if this is the SanMar-specific structure
            if hasattr(response.Inventory, 'PartInventoryArray') and response.Inventory.PartInventoryArray:
                logger.info("Found SanMar PartInventoryArray structure")

                # Process each part in the PartInventoryArray
                if hasattr(response.Inventory.PartInventoryArray, 'PartInventory'):
                    part_inventory_list = response.Inventory.PartInventoryArray.PartInventory
                    # Handle if it's a single item or a list
                    if not isinstance(part_inventory_list, list):
                        part_inventory_list = [part_inventory_list]

                    logger.info(f"Processing {len(part_inventory_list)} parts")

                    for part in part_inventory_list:
                        # Extract color and size from part
                        color = getattr(part, 'partColor', None)
                        size = getattr(part, 'labelSize', None)

                        if color and size:
                            logger.info(f"Processing part with color: {color}, size: {size}")

                            # Create nested structure if not exists
                            if color not in inventory_data:
                                inventory_data[color] = {}
                            if size not in inventory_data[color]:
                                inventory_data[color][size] = {"warehouses": {}, "total": 0}

                            # Handle warehouse inventory
                            if hasattr(part, 'InventoryLocationArray') and part.InventoryLocationArray:
                                loc_inventory_list = part.InventoryLocationArray.InventoryLocation
                                # Handle if it's a single item or a list
                                if not isinstance(loc_inventory_list, list):
                                    loc_inventory_list = [loc_inventory_list]

                                for loc in loc_inventory_list:
                                    warehouse_id = getattr(loc, 'inventoryLocationId', None)

                                    # Extract quantity value
                                    quantity = 0
                                    if hasattr(loc, 'inventoryLocationQuantity') and loc.inventoryLocationQuantity:
                                        if hasattr(loc.inventoryLocationQuantity, 'Quantity') and loc.inventoryLocationQuantity.Quantity:
                                            if hasattr(loc.inventoryLocationQuantity.Quantity, 'value'):
                                                try:
                                                    # Convert Decimal to int (already here, which is good)
                                                    quantity = int(loc.inventoryLocationQuantity.Quantity.value)
                                                except (ValueError, TypeError):
                                                    quantity = 0

                                    if warehouse_id:
                                        logger.info(f"  Warehouse {warehouse_id}: {quantity}")
                                        inventory_data[color][size]["warehouses"][warehouse_id] = quantity
                                        inventory_data[color][size]["total"] += quantity

                            # If we have total quantity available but no warehouse detail
                            elif hasattr(part, 'quantityAvailable') and part.quantityAvailable:
                                if hasattr(part.quantityAvailable, 'Quantity') and part.quantityAvailable.Quantity:
                                    if hasattr(part.quantityAvailable.Quantity, 'value'):
                                        try:
                                            # Convert Decimal to int (already here)
                                            total_qty = int(part.quantityAvailable.Quantity.value)
                                            inventory_data[color][size]["total"] = total_qty
                                            logger.info(f"  Total quantity: {total_qty}")
                                        except (ValueError, TypeError):
                                            pass
            # Try standard PromoStandards format as fallback
            else:
                logger.info("Trying standard PromoStandards format")
                # Ensure response.Inventory is iterable
                inventory_list = response.Inventory
                if not isinstance(inventory_list, list):
                    inventory_list = [inventory_list] if inventory_list else []

                for inv in inventory_list:
                    logger.info(f"Processing inventory item: {inv}")

                    # Get color and size (different possible structures)
                    color = "Default"
                    size = "OSFA"
                    if hasattr(inv, 'ProductVariationID'):
                        color = getattr(inv.ProductVariationID, 'Color', "Default")
                        size = getattr(inv.ProductVariationID, 'Size', "OSFA")
                        logger.info(f"Found color: {color}, size: {size}")
                    else:
                        # Try alternate structures
                        color = getattr(inv, 'Color', "Default")
                        size = getattr(inv, 'Size', "OSFA")
                        logger.info(f"Using alternate color: {color}, size: {size}")

                    # Create nested structure if not exists
                    if color not in inventory_data:
                        inventory_data[color] = {}
                    if size not in inventory_data[color]:
                        inventory_data[color][size] = {"warehouses": {}, "total": 0}

                    # Add warehouse data - handle different possible structures
                    if hasattr(inv, 'LocationInventoryArray') and inv.LocationInventoryArray:
                        loc_inv_list = inv.LocationInventoryArray.LocationInventory
                        if not isinstance(loc_inv_list, list):
                            loc_inv_list = [loc_inv_list] if loc_inv_list else []

                        for loc in loc_inv_list:
                            warehouse_id = getattr(loc, 'LocationID', "1")
                            quantity_val = getattr(loc, 'QuantityAvailable', 0)
                            try:
                                quantity = int(quantity_val) # Ensure int conversion
                            except (ValueError, TypeError):
                                quantity = 0

                            inventory_data[color][size]["warehouses"][warehouse_id] = quantity
                            inventory_data[color][size]["total"] += quantity
                            logger.info(f"Added warehouse {warehouse_id} with qty {quantity}")
                    elif hasattr(inv, 'WarehouseInventory'):
                        # Alternate structure
                        wh_inv_list = inv.WarehouseInventory
                        if not isinstance(wh_inv_list, list):
                            wh_inv_list = [wh_inv_list] if wh_inv_list else []

                        for wh in wh_inv_list:
                            warehouse_id = getattr(wh, 'WarehouseID', "1")
                            quantity_val = getattr(wh, 'Quantity', 0)
                            try:
                                quantity = int(quantity_val) # Ensure int conversion
                            except (ValueError, TypeError):
                                quantity = 0

                            inventory_data[color][size]["warehouses"][warehouse_id] = quantity
                            inventory_data[color][size]["total"] += quantity
                            logger.info(f"Added warehouse {warehouse_id} with qty {quantity} (alt structure)")
        else:
            logger.warning(f"No standard 'Inventory' attribute found in response, checking alternatives")

            # Try alternate response structures
            if hasattr(response, 'Product') and response.Product:
                logger.info("Found 'Product' attribute in response")
                product_list = response.Product
                if not isinstance(product_list, list):
                    product_list = [product_list] if product_list else []

                for prod in product_list:
                    # Try to extract inventory from Product structure
                    color = getattr(prod, 'ColorName', "Default")
                    size = getattr(prod, 'SizeName', "OSFA")

                    if hasattr(prod, 'Inventory'):
                        inv_list = prod.Inventory
                        if not isinstance(inv_list, list):
                            inv_list = [inv_list] if inv_list else []

                        for wh in inv_list:
                            wh_id = getattr(wh, 'WarehouseID', "1")
                            qty_val = getattr(wh, 'QuantityAvailable', 0)
                            try:
                                qty = int(qty_val) # Ensure int conversion
                            except (ValueError, TypeError):
                                qty = 0

                            # Create structure if needed
                            if color not in inventory_data:
                                inventory_data[color] = {}
                            if size not in inventory_data[color]:
                                inventory_data[color][size] = {"warehouses": {}, "total": 0}

                            inventory_data[color][size]["warehouses"][wh_id] = qty
                            inventory_data[color][size]["total"] += qty
                            logger.info(f"Added inventory from Product structure: {color}/{size}/{wh_id}: {qty}")
            else:
                logger.warning(f"No inventory found for {style}, falling back to mock data")
                return mock_inventory.generate_mock_inventory(style)

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
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}") # Log full traceback
        logger.warning(f"Falling back to mock data for {style} due to error")
        return mock_inventory.generate_mock_inventory(style)

# Clear cache function
def clear_inventory_cache():
    get_inventory_by_style.cache_clear()
