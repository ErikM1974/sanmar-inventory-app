#!/usr/bin/env python
"""
Script to import SanMar inventory and pricing data into Caspio daily.
This script is designed to be run as a scheduled task at 7 AM every day.
"""

import os
import sys
import json
import logging
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("daily_inventory_pricing_import.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import our custom modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from middleware_client import create_soap_client, categorize_error
    from caspio_client import CaspioClient
    from color_mapper import color_mapper
except ImportError:
    logger.error("Failed to import custom modules. Make sure middleware_client.py, caspio_client.py, and color_mapper.py are in the same directory.")
    sys.exit(1)

# SanMar API credentials
SANMAR_USERNAME = os.getenv('SANMAR_USERNAME')
SANMAR_PASSWORD = os.getenv('SANMAR_PASSWORD')
SANMAR_CUSTOMER_NUMBER = os.getenv('SANMAR_CUSTOMER_NUMBER')

# Caspio API credentials
CASPIO_BASE_URL = os.getenv('CASPIO_BASE_URL')
CASPIO_CLIENT_ID = os.getenv('CASPIO_CLIENT_ID')
CASPIO_CLIENT_SECRET = os.getenv('CASPIO_CLIENT_SECRET')
CASPIO_ACCESS_TOKEN = os.getenv('CASPIO_ACCESS_TOKEN')
CASPIO_REFRESH_TOKEN = os.getenv('CASPIO_REFRESH_TOKEN')

# Initialize Caspio client
caspio_client = None
if CASPIO_CLIENT_ID and CASPIO_CLIENT_SECRET:
    caspio_client = CaspioClient(
        base_url=CASPIO_BASE_URL,
        client_id=CASPIO_CLIENT_ID,
        client_secret=CASPIO_CLIENT_SECRET
    )
elif CASPIO_ACCESS_TOKEN:
    caspio_client = CaspioClient(
        base_url=CASPIO_BASE_URL,
        access_token=CASPIO_ACCESS_TOKEN,
        refresh_token=CASPIO_REFRESH_TOKEN
    )
else:
    logger.error("Caspio API credentials are not properly configured. Please check your .env file.")
    sys.exit(1)

# SanMar API endpoints
SANMAR_WSDL = {
    'inventory': 'https://ws.sanmar.com:8080/promostandards/InventoryServiceBindingV2final?WSDL',
    'pricing': 'https://ws.sanmar.com:8080/SanMarWebService/SanMarPricingServicePort?wsdl',
    'product_info': 'https://ws.sanmar.com:8080/SanMarWebService/SanMarProductInfoServicePort?wsdl'
}

def refresh_caspio_token():
    """Refresh the Caspio API access token."""
    if not CASPIO_REFRESH_TOKEN:
        logger.error("No refresh token available. Please set CASPIO_REFRESH_TOKEN in your .env file.")
        return False
    
    auth_url = f"{CASPIO_BASE_URL}/oauth/token"
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': CASPIO_REFRESH_TOKEN
    }
    
    try:
        response = requests.post(auth_url, data=payload)
        response.raise_for_status()
        
        token_data = response.json()
        access_token = token_data.get('access_token')
        new_refresh_token = token_data.get('refresh_token')
        
        # Update the .env file
        update_env_file(access_token, new_refresh_token)
        
        # Update the Caspio client
        caspio_client.access_token = access_token
        caspio_client.refresh_token = new_refresh_token
        
        logger.info("Successfully refreshed Caspio access token.")
        return True
    except Exception as e:
        logger.error(f"Error refreshing Caspio access token: {str(e)}")
        return False

def update_env_file(access_token, refresh_token):
    """Update the .env file with the new token data."""
    try:
        # Read the current .env file
        env_lines = []
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                env_lines = f.readlines()
        
        # Update or add the token variables
        access_token_line = f"CASPIO_ACCESS_TOKEN={access_token}\n"
        refresh_token_line = f"CASPIO_REFRESH_TOKEN={refresh_token}\n"
        
        access_token_found = False
        refresh_token_found = False
        
        for i, line in enumerate(env_lines):
            if line.startswith('CASPIO_ACCESS_TOKEN='):
                env_lines[i] = access_token_line
                access_token_found = True
            elif line.startswith('CASPIO_REFRESH_TOKEN='):
                env_lines[i] = refresh_token_line
                refresh_token_found = True
        
        if not access_token_found:
            env_lines.append(access_token_line)
        if not refresh_token_found:
            env_lines.append(refresh_token_line)
        
        # Write the updated .env file
        with open('.env', 'w') as f:
            f.writelines(env_lines)
        
        logger.info("Updated .env file with new token data.")
        return True
    except Exception as e:
        logger.error(f"Error updating .env file: {str(e)}")
        return False

def get_product_styles_from_caspio():
    """Get all product styles from the Caspio Sanmar_Bulk table."""
    try:
        # Query the Sanmar_Bulk table to get all unique styles
        styles = set()
        
        # Use the Caspio API to query the Sanmar_Bulk table
        endpoint = f"rest/v2/tables/Sanmar_Bulk_251816_Feb2024/records"
        params = {
            'q.select': 'STYLE',
            'q.distinct': 'true'
        }
        
        response = caspio_client.make_api_request(endpoint, params=params)
        
        if not response or 'Result' not in response:
            logger.error("Failed to get styles from Caspio Sanmar_Bulk table.")
            return []
        
        for product in response['Result']:
            if 'STYLE' in product:
                styles.add(product['STYLE'])
        
        logger.info(f"Retrieved {len(styles)} unique styles from Caspio Sanmar_Bulk table.")
        return list(styles)
    except Exception as e:
        logger.error(f"Error getting product styles from Caspio: {str(e)}")
        return []

def extract_color_mappings_from_sanmar(styles):
    """Extract color mappings from SanMar API for the given styles."""
    logger.info("Extracting color mappings from SanMar API...")
    
    try:
        # Create a SOAP client for the Product Info service
        client = create_soap_client(SANMAR_WSDL['product_info'])
        
        # Get color mappings for each style
        color_mappings = {}
        total_styles = len(styles)
        
        for i, style in enumerate(styles[:10]):  # Limit to 10 styles for testing
            logger.info(f"Getting color mappings for style {style} ({i+1}/{min(10, total_styles)})...")
            
            # Call the getProductInfo method
            request_data = {
                "style": style,
                "sanMarCustomerNumber": SANMAR_CUSTOMER_NUMBER,
                "sanMarUserName": SANMAR_USERNAME,
                "sanMarUserPassword": SANMAR_PASSWORD
            }
            
            response = client.service.getProductInfo(request_data)
            
            # Process the response
            from zeep.helpers import serialize_object
            response_dict = serialize_object(response)
            
            if response and hasattr(response, 'errorOccurred') and not response.errorOccurred:
                # Extract color mappings from the response
                if hasattr(response, 'colorArray') and response.colorArray:
                    for color in response.colorArray:
                        if hasattr(color, 'colorName') and hasattr(color, 'colorDisplayName'):
                            api_color = color.colorName
                            display_color = color.colorDisplayName
                            
                            # Add to color mappings dictionary if not already present
                            if api_color and display_color and api_color not in color_mappings:
                                color_mappings[api_color] = display_color
            
            # Sleep briefly to avoid overwhelming the API
            time.sleep(0.5)
        
        # Convert dictionary to list of records
        color_mapping_records = []
        for api_color, display_color in color_mappings.items():
            color_mapping_records.append({
                'API_COLOR_NAME': api_color,
                'DISPLAY_COLOR_NAME': display_color,
                'LAST_UPDATED': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        logger.info(f"Extracted {len(color_mapping_records)} color mappings from SanMar API.")
        return color_mapping_records
    except Exception as e:
        error_type, error_message = categorize_error(e)
        logger.error(f"Error extracting color mappings from SanMar API: {error_type} - {error_message}")
        return []

def import_color_mappings_to_caspio(color_mapping_records):
    """Import color mappings to Caspio."""
    logger.info("Importing color mappings to Caspio...")
    
    try:
        # Clear existing color mappings
        caspio_client.delete_all_records('ColorMapping')
        logger.info("Cleared existing color mappings from Caspio.")
        
        # Import color mappings
        records_inserted = 0
        for mapping in color_mapping_records:
            caspio_client.insert_record('ColorMapping', mapping)
            records_inserted += 1
        
        logger.info(f"Successfully imported {records_inserted} color mappings to Caspio.")
        return True
    except Exception as e:
        logger.error(f"Error importing color mappings to Caspio: {str(e)}")
        return False

def get_color_mappings_from_caspio():
    """Get color mappings from Caspio."""
    try:
        # Query the ColorMapping table
        endpoint = f"rest/v2/tables/ColorMapping/records"
        params = {
            'q.select': 'API_COLOR_NAME,DISPLAY_COLOR_NAME'
        }
        
        response = caspio_client.make_api_request(endpoint, params=params)
        
        if not response or 'Result' not in response:
            logger.error("Failed to get color mappings from Caspio.")
            return {}
        
        # Create a dictionary of color mappings
        color_mappings = {}
        for mapping in response['Result']:
            if 'API_COLOR_NAME' in mapping and 'DISPLAY_COLOR_NAME' in mapping:
                color_mappings[mapping['API_COLOR_NAME']] = mapping['DISPLAY_COLOR_NAME']
        
        logger.info(f"Retrieved {len(color_mappings)} color mappings from Caspio.")
        return color_mappings
    except Exception as e:
        logger.error(f"Error getting color mappings from Caspio: {str(e)}")
        return {}

def get_sanmar_inventory(styles):
    """Get inventory information for products from SanMar API."""
    logger.info("Getting inventory information from SanMar API...")
    
    try:
        # Create a SOAP client for the Inventory service
        client = create_soap_client(SANMAR_WSDL['inventory'])
        
        # Get inventory for each style
        inventory_data = []
        total_styles = len(styles)
        
        # Get color mappings from Caspio
        color_mappings = get_color_mappings_from_caspio()
        
        for i, style in enumerate(styles):
            logger.info(f"Getting inventory for style {style} ({i+1}/{total_styles})...")
            
            # Call the getInventoryLevels method using PromoStandards format
            request_data = {
                "wsVersion": "2.0.0",
                "id": SANMAR_USERNAME,
                "password": SANMAR_PASSWORD,
                "productId": style
            }
            
            response = client.service.getInventoryLevels(**request_data)
            
            # Process the response for PromoStandards format
            if hasattr(response, 'Inventory') and response.Inventory:
                # Check if this is the SanMar-specific structure
                if hasattr(response.Inventory, 'PartInventoryArray') and response.Inventory.PartInventoryArray:
                    # Process each part in the PartInventoryArray
                    if hasattr(response.Inventory.PartInventoryArray, 'PartInventory'):
                        part_inventory_list = response.Inventory.PartInventoryArray.PartInventory
                        # Handle if it's a single item or a list
                        if not isinstance(part_inventory_list, list):
                            part_inventory_list = [part_inventory_list]
                        
                        for part in part_inventory_list:
                            # Extract color and size from part
                            color_name = getattr(part, 'partColor', None)
                            size_name = getattr(part, 'labelSize', None)
                            
                            if color_name and size_name:
                                # Map the color name to display color name
                                display_color = color_mappings.get(color_name, color_name)
                                
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
                                                        # Convert Decimal to int
                                                        quantity = int(loc.inventoryLocationQuantity.Quantity.value)
                                                    except (ValueError, TypeError):
                                                        quantity = 0
                                        
                                        if warehouse_id:
                                            # Add inventory record with display color
                                            inventory_data.append({
                                                'STYLE': style,
                                                'COLOR_NAME': color_name,
                                                'DISPLAY_COLOR': display_color,
                                                'SIZE': size_name,
                                                'WAREHOUSE_ID': warehouse_id,
                                                'QUANTITY': quantity,
                                                'LAST_UPDATED': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                            })
            
            # Sleep briefly to avoid overwhelming the API
            time.sleep(0.5)
        
        logger.info(f"Retrieved {len(inventory_data)} inventory records from SanMar API.")
        return inventory_data
    except Exception as e:
        error_type, error_message = categorize_error(e)
        logger.error(f"Error getting inventory information from SanMar API: {error_type} - {error_message}")
        return []

def get_sanmar_pricing(styles):
    """Get pricing information for products from SanMar API."""
    logger.info("Getting pricing information from SanMar API...")
    
    try:
        # Create a SOAP client for the Pricing service
        client = create_soap_client(SANMAR_WSDL['pricing'])
        
        # Get pricing for each style
        pricing_data = []
        total_styles = len(styles)
        
        # Get color mappings from Caspio
        color_mappings = get_color_mappings_from_caspio()
        
        for i, style in enumerate(styles):
            logger.info(f"Getting pricing for style {style} ({i+1}/{total_styles})...")
            
            # Prepare the request arguments for getPricing
            arg0 = {
                'style': style,
                'color': None,
                'size': None,
                'inventoryKey': None,
                'sizeIndex': None,
                'casePrice': None,
                'dozenPrice': None,
                'myPrice': None,
                'piecePrice': None,
                'salePrice': None
            }
            
            # Prepare authentication
            arg1 = {
                "sanMarCustomerNumber": SANMAR_CUSTOMER_NUMBER,
                "sanMarUserName": SANMAR_USERNAME,
                "sanMarUserPassword": SANMAR_PASSWORD,
            }
            
            # Make the SOAP call
            response = client.service.getPricing(arg0, arg1)
            
            # Process the response
            from zeep.helpers import serialize_object
            response_dict = serialize_object(response)
            
            # Log the response for debugging
            logger.info(f"Pricing API response for style {style}: {response_dict.get('message', 'No message')}")
            
            if response and hasattr(response, 'errorOccurred') and not response.errorOccurred:
                # Check if we have list responses
                if 'listResponse' in response_dict and response_dict['listResponse']:
                    for item in response_dict['listResponse']:
                        # Extract basic information
                        item_style = item.get('style', '')
                        item_color = item.get('color', '')
                        item_size = item.get('size', '')
                        
                        # Map the color name to display color name
                        display_color = color_mappings.get(item_color, item_color)
                        
                        # Extract pricing information
                        piece_price = item.get('piecePrice')
                        case_price = item.get('casePrice')
                        sale_price = item.get('salePrice')
                        my_price = item.get('myPrice')  # Customer-specific price
                        
                        # Determine the program price (customer-specific or sale price)
                        if my_price and piece_price and float(my_price) <= float(piece_price):
                            program_price = float(my_price)
                        elif sale_price and piece_price and float(sale_price) <= float(piece_price):
                            program_price = float(sale_price)
                        elif piece_price:
                            program_price = float(piece_price)
                        else:
                            program_price = None
                        # Get case size
                        case_size = 144  # Default case size
                        if hasattr(item, 'caseSize') and item.caseSize:
                            try:
                                case_size = int(item.caseSize)
                                logger.info(f"Using case size from API for style {item_style}, color {item_color}, size {item_size}: {case_size}")
                            except (ValueError, TypeError):
                                logger.warning(f"Invalid case size from API for style {item_style}, color {item_color}, size {item_size}: {item.caseSize}. Using default: {case_size}")
                        else:
                            # Use product-specific default case sizes based on style and size
                            if item_style.upper().startswith('PC61'):
                                if item_size in ['S', 'M', 'L', 'XL']:
                                    case_size = 72
                                    logger.info(f"Using PC61-specific case size for size {item_size}: {case_size}")
                                else:  # 2XL and up
                                    case_size = 36
                                    logger.info(f"Using PC61-specific case size for size {item_size}: {case_size}")
                            elif item_size in ["OSFA", "OS", "ONE SIZE"]:
                                case_size = 144  # Default for one-size accessories
                                logger.info(f"Using one-size case size for style {item_style}, size {item_size}: {case_size}")
                            else:
                                logger.info(f"Using default case size for style {item_style}, color {item_color}, size {item_size}: {case_size}")
                                pass
                        
                        # Add pricing record with display color
                        pricing_data.append({
                            'STYLE': item_style,
                            'COLOR_NAME': item_color,
                            'DISPLAY_COLOR': display_color,
                            'SIZE': item_size,
                            'PIECE_PRICE': float(piece_price) if piece_price else 0,
                            'CASE_PRICE': float(case_price) if case_price else 0,
                            'PROGRAM_PRICE': program_price if program_price else 0
                        })
            
            # Sleep briefly to avoid overwhelming the API
            time.sleep(0.5)
        
        logger.info(f"Retrieved {len(pricing_data)} pricing records from SanMar API.")
        return pricing_data
    except Exception as e:
        error_type, error_message = categorize_error(e)
        logger.error(f"Error getting pricing information from SanMar API: {error_type} - {error_message}")
        return []

def import_inventory_to_caspio(inventory_data):
    """Import inventory data to Caspio."""
    logger.info("Importing inventory data to Caspio...")
    
    try:
        # Clear existing inventory data
        caspio_client.delete_all_records('Inventory')
        logger.info("Cleared existing inventory data from Caspio.")
        
        # Import inventory data in batches
        batch_size = 100
        total_records = len(inventory_data)
        records_inserted = 0
        
        for i in range(0, total_records, batch_size):
            batch = inventory_data[i:i+batch_size]
            for inventory_record in batch:
                caspio_client.insert_record('Inventory', inventory_record)
            
            records_inserted += len(batch)
            logger.info(f"Imported {records_inserted} of {total_records} inventory records ({(records_inserted/total_records)*100:.1f}%).")
            
            # Sleep briefly to avoid overwhelming the API
            time.sleep(0.5)
        
        logger.info(f"Successfully imported {records_inserted} inventory records to Caspio.")
        return True
    except Exception as e:
        logger.error(f"Error importing inventory data to Caspio: {str(e)}")
        return False

def import_pricing_to_caspio(pricing_data):
    """Import pricing data to Caspio."""
    logger.info("Importing pricing data to Caspio...")
    
    try:
        # Clear existing pricing data
        caspio_client.delete_all_records('Pricing')
        logger.info("Cleared existing pricing data from Caspio.")
        
        # Import pricing data in batches
        batch_size = 100
        total_records = len(pricing_data)
        records_inserted = 0
        
        for i in range(0, total_records, batch_size):
            batch = pricing_data[i:i+batch_size]
            for pricing_record in batch:
                caspio_client.insert_record('Pricing', pricing_record)
            
            records_inserted += len(batch)
            logger.info(f"Imported {records_inserted} of {total_records} pricing records ({(records_inserted/total_records)*100:.1f}%).")
            
            # Sleep briefly to avoid overwhelming the API
            time.sleep(0.5)
        
        logger.info(f"Successfully imported {records_inserted} pricing records to Caspio.")
        return True
    except Exception as e:
        logger.error(f"Error importing pricing data to Caspio: {str(e)}")
        return False

def update_inventory_with_pricing(inventory_data, pricing_data):
    """Update inventory records with pricing information."""
    logger.info("Updating inventory records with pricing information...")
    
    try:
        # Create a dictionary of pricing data for quick lookup
        pricing_lookup = {}
        for pricing in pricing_data:
            key = f"{pricing['STYLE']}_{pricing['COLOR_NAME']}_{pricing['SIZE']}"
            pricing_lookup[key] = pricing
        
        # Update inventory records with pricing information
        for inventory in inventory_data:
            key = f"{inventory['STYLE']}_{inventory['COLOR_NAME']}_{inventory['SIZE']}"
            if key in pricing_lookup:
                inventory['Case_Price'] = pricing_lookup[key]['CASE_PRICE']
                inventory['Program_Price'] = pricing_lookup[key]['PROGRAM_PRICE']
        
        logger.info(f"Updated {len(inventory_data)} inventory records with pricing information.")
        return inventory_data
    except Exception as e:
        logger.error(f"Error updating inventory records with pricing information: {str(e)}")
        return inventory_data

def main():
    """Main function to import SanMar inventory and pricing data into Caspio."""
    logger.info("Starting daily SanMar inventory and pricing import...")
    
    # Check if SanMar API credentials are set
    if not SANMAR_USERNAME or not SANMAR_PASSWORD or not SANMAR_CUSTOMER_NUMBER:
        logger.error("SanMar API credentials are not properly configured. Please check your .env file.")
        sys.exit(1)
    
    # Refresh Caspio token if using token-based authentication
    if CASPIO_ACCESS_TOKEN and CASPIO_REFRESH_TOKEN:
        refresh_caspio_token()
    
    # Get product styles from Caspio
    styles = get_product_styles_from_caspio()
    if not styles:
        logger.error("Failed to get product styles from Caspio. Make sure the Sanmar_Bulk table is populated.")
        sys.exit(1)
    
    # Extract and import color mappings
    color_mapping_records = extract_color_mappings_from_sanmar(styles)
    if color_mapping_records:
        if import_color_mappings_to_caspio(color_mapping_records):
            logger.info("Successfully imported color mappings to Caspio.")
        else:
            logger.error("Failed to import color mappings to Caspio.")
            # Continue with default color mappings
    else:
        logger.warning("No color mappings extracted from SanMar API. Using default color mappings.")
    
    # Get inventory data from SanMar
    logger.info("Getting inventory data from SanMar API...")
    inventory_data = get_sanmar_inventory(styles)
    if not inventory_data:
        logger.error("Failed to get inventory data from SanMar API.")
        sys.exit(1)
    
    # Get pricing data from SanMar
    logger.info("Getting pricing data from SanMar API...")
    pricing_data = get_sanmar_pricing(styles)
    if not pricing_data:
        logger.error("Failed to get pricing data from SanMar API.")
        sys.exit(1)
    
    # Option 1: Separate Pricing Table (Recommended)
    # Import inventory data to Caspio
    if import_inventory_to_caspio(inventory_data):
        logger.info("Successfully imported inventory data to Caspio.")
    else:
        logger.error("Failed to import inventory data to Caspio.")
        sys.exit(1)
    
    # Import pricing data to Caspio
    if import_pricing_to_caspio(pricing_data):
        logger.info("Successfully imported pricing data to Caspio.")
    else:
        logger.error("Failed to import pricing data to Caspio.")
        sys.exit(1)
    
    # Option 2: Keep Pricing in Inventory Table
    # Uncomment the following code if you prefer to keep pricing in the Inventory table
    """
    # Update inventory records with pricing information
    inventory_data = update_inventory_with_pricing(inventory_data, pricing_data)
    
    # Import inventory data (with pricing) to Caspio
    if import_inventory_to_caspio(inventory_data):
        logger.info("Successfully imported inventory data with pricing to Caspio.")
    else:
        logger.error("Failed to import inventory data with pricing to Caspio.")
        sys.exit(1)
    """
    
    logger.info("Daily SanMar inventory and pricing import completed successfully.")

if __name__ == "__main__":
    main()