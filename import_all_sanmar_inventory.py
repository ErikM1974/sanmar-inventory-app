#!/usr/bin/env python
"""
Script to import SanMar inventory data into Caspio (Test Sample).

This script:
1. Connects to the SanMar API to get all inventory data
2. Processes the data to match the Caspio table structure
3. Imports the data in batches with proper error handling and progress tracking
4. Can be configured for initial test import or daily updates
"""

import os
import sys
import json
import logging
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
import concurrent.futures

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("import_sanmar_inventory_test.log"),
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
except ImportError:
    logger.error("Failed to import custom modules. Make sure middleware_client.py and caspio_client.py are in the same directory.")
    sys.exit(1)

# SanMar API credentials
SANMAR_USERNAME = os.getenv('SANMAR_USERNAME')
SANMAR_PASSWORD = os.getenv('SANMAR_PASSWORD')
SANMAR_CUSTOMER_NUMBER = os.getenv('SANMAR_CUSTOMER_NUMBER')

# Configuration
TEST_MODE = False  # Set to False to import all inventory
MAX_TEST_STYLES = 5  # Number of styles to process in test mode
MAX_TEST_RECORDS = 50  # Approximate number of records to import in test mode

# Caspio API credentials
CASPIO_BASE_URL = os.getenv('CASPIO_BASE_URL')
CASPIO_CLIENT_ID = os.getenv('CASPIO_CLIENT_ID')
CASPIO_CLIENT_SECRET = os.getenv('CASPIO_CLIENT_SECRET')
CASPIO_ACCESS_TOKEN = os.getenv('CASPIO_ACCESS_TOKEN')
CASPIO_REFRESH_TOKEN = os.getenv('CASPIO_REFRESH_TOKEN')

# SanMar API endpoints
SANMAR_WSDL = {
    'inventory': 'https://ws.sanmar.com:8080/promostandards/InventoryServiceBindingV2final?WSDL',
    'product_info': 'https://ws.sanmar.com:8080/SanMarWebService/SanMarProductInfoServicePort?wsdl'
}

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

def get_all_styles_from_sanmar():
    """Get all available styles from SanMar API."""
    logger.info("Getting all available styles from SanMar API...")
    
    try:
        # Create a SOAP client for the Product Info service
        client = create_soap_client(SANMAR_WSDL['product_info'])
        
        # Call the getProductCategories method to get all categories
        response = client.service.getProductCategories(
            username=SANMAR_USERNAME,
            password=SANMAR_PASSWORD,
            customerNumber=SANMAR_CUSTOMER_NUMBER
        )
        
        # Process the response to get all styles
        all_styles = set()
        
        # Process each category
        for category in response.categories:
            category_name = category.name
            logger.info(f"Getting products for category: {category_name}")
            
            # Get products for this category
            try:
                products_response = client.service.getProductInfoByCategory(
                    username=SANMAR_USERNAME,
                    password=SANMAR_PASSWORD,
                    customerNumber=SANMAR_CUSTOMER_NUMBER,
                    categoryName=category_name
                )
                
                # Add styles to the set
                if hasattr(products_response, 'products') and products_response.products:
                    for product in products_response.products:
                        all_styles.add(product.styleNumber)
                
                # Sleep briefly to avoid overwhelming the API
                time.sleep(1)
            except Exception as e:
                error_type, error_message = categorize_error(e)
                logger.error(f"Error getting products for category '{category_name}': {error_type} - {error_message}")
                continue
            
            # Process subcategories if any
            if hasattr(category, 'subCategories') and category.subCategories:
                for subcategory in category.subCategories:
                    subcategory_name = subcategory.name
                    logger.info(f"Getting products for subcategory: {subcategory_name}")
                    
                    # Get products for this subcategory
                    try:
                        subcategory_products_response = client.service.getProductInfoByCategory(
                            username=SANMAR_USERNAME,
                            password=SANMAR_PASSWORD,
                            customerNumber=SANMAR_CUSTOMER_NUMBER,
                            categoryName=subcategory_name
                        )
                        
                        # Add styles to the set
                        if hasattr(subcategory_products_response, 'products') and subcategory_products_response.products:
                            for product in subcategory_products_response.products:
                                all_styles.add(product.styleNumber)
                        
                        # Sleep briefly to avoid overwhelming the API
                        time.sleep(1)
                    except Exception as e:
                        error_type, error_message = categorize_error(e)
                        logger.error(f"Error getting products for subcategory '{subcategory_name}': {error_type} - {error_message}")
                        continue
        
        logger.info(f"Retrieved {len(all_styles)} unique styles from SanMar API.")
        return list(all_styles)
    except Exception as e:
        error_type, error_message = categorize_error(e)
        logger.error(f"Error getting styles from SanMar API: {error_type} - {error_message}")
        return []

def get_color_mappings_from_caspio():
    """Get color mappings from Caspio."""
    try:
        # First try with MAINFRAME_COLOR and DISPLAY_COLOR
        endpoint = f"rest/v2/tables/ColorMapping/records"
        params = {
            'q.select': 'MAINFRAME_COLOR,DISPLAY_COLOR'
        }
        
        response = caspio_client.make_api_request(endpoint, params=params)
        
        if response and 'Result' in response:
            # Create a dictionary of color mappings
            color_mappings = {}
            for mapping in response['Result']:
                if 'MAINFRAME_COLOR' in mapping and 'DISPLAY_COLOR' in mapping:
                    color_mappings[mapping['MAINFRAME_COLOR']] = mapping['DISPLAY_COLOR']
            
            logger.info(f"Retrieved {len(color_mappings)} color mappings from Caspio using MAINFRAME_COLOR field.")
            return color_mappings
        else:
            # Try with API_COLOR_NAME and DISPLAY_COLOR_NAME as fallback
            logger.warning("Failed to get color mappings with MAINFRAME_COLOR. Trying API_COLOR_NAME...")
            params = {
                'q.select': 'API_COLOR_NAME,DISPLAY_COLOR_NAME'
            }
            
            response = caspio_client.make_api_request(endpoint, params=params)
            
            if response and 'Result' in response:
                # Create a dictionary of color mappings
                color_mappings = {}
                for mapping in response['Result']:
                    if 'API_COLOR_NAME' in mapping and 'DISPLAY_COLOR_NAME' in mapping:
                        color_mappings[mapping['API_COLOR_NAME']] = mapping['DISPLAY_COLOR_NAME']
                
                logger.info(f"Retrieved {len(color_mappings)} color mappings from Caspio using API_COLOR_NAME field.")
                return color_mappings
        
        logger.error("Failed to get color mappings from Caspio with any field combination.")
        return {}
    except Exception as e:
        logger.error(f"Error getting color mappings from Caspio: {str(e)}")
        return {}

def get_inventory_for_style(style, color_mappings):
    """Get inventory data for a specific style from SanMar API.
    
    Extracts unique identifiers from the API response if available.
    """
    logger.info(f"Getting inventory for style {style}...")
    
    try:
        # Create a SOAP client for the Inventory service
        client = create_soap_client(SANMAR_WSDL['inventory'])
        
        # Call the getInventoryLevels method using PromoStandards format
        request_data = {
            "wsVersion": "2.0.0",
            "id": SANMAR_USERNAME,
            "password": SANMAR_PASSWORD,
            "productId": style
        }
        
        response = client.service.getInventoryLevels(**request_data)
        
        # Process the response
        inventory_data = []
        
        # Log specific parts of the response to look for unique identifiers
        logger.info(f"Examining SanMar inventory response for style {style} to find unique identifiers...")
        
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
                                        # Look for unique identifiers in the response
                                        unique_key = None
                                        
                                        # Check for partId which might be a unique identifier
                                        if hasattr(part, 'partId'):
                                            unique_key = str(part.partId)
                                            logger.info(f"Found partId as potential unique key: {unique_key}")
                                        
                                        # Check for productId which might be a unique identifier
                                        if hasattr(part, 'productId'):
                                            unique_key = str(part.productId)
                                            logger.info(f"Found productId as potential unique key: {unique_key}")
                                        
                                        # Check for inventoryLevelId which might be a unique identifier
                                        if hasattr(loc, 'inventoryLevelId'):
                                            unique_key = str(loc.inventoryLevelId)
                                            logger.info(f"Found inventoryLevelId as potential unique key: {unique_key}")
                                        
                                        # Log all available attributes for debugging
                                        part_attrs = [attr for attr in dir(part) if not attr.startswith('_') and not callable(getattr(part, attr))]
                                        loc_attrs = [attr for attr in dir(loc) if not attr.startswith('_') and not callable(getattr(loc, attr))]
                                        logger.info(f"Part attributes: {part_attrs}")
                                        logger.info(f"Location attributes: {loc_attrs}")
                                        
                                        # If no unique key found, create one from the fields
                                        if not unique_key:
                                            unique_key = f"{style}_{color_name}_{size_name}_{warehouse_id}"
                                        
                                        # Add inventory record with display color and unique key
                                        inventory_data.append({
                                            'STYLE': style,
                                            'COLOR_NAME': color_name,
                                            'DISPLAY_COLOR': display_color,
                                            'SIZE': size_name,
                                            'WAREHOUSE_ID': warehouse_id,
                                            'QUANTITY': quantity,
                                            'UNIQUE_KEY': unique_key,
                                            'LAST_UPDATED': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                        })
        
        logger.info(f"Retrieved {len(inventory_data)} inventory records for style {style}.")
        return inventory_data
    except Exception as e:
        error_type, error_message = categorize_error(e)
        logger.error(f"Error getting inventory for style {style}: {error_type} - {error_message}")
        return []

def get_all_inventory_data(styles, color_mappings, max_workers=5, test_mode=True, max_test_styles=5, max_test_records=50):
    """Get inventory data for all styles using parallel processing.
    
    Args:
        styles: List of style codes to process
        color_mappings: Dictionary mapping API color names to display color names
        max_workers: Maximum number of parallel workers
        test_mode: If True, limit to a small test sample
        max_test_styles: Maximum number of styles to process in test mode
        max_test_records: Approximate maximum number of records to retrieve in test mode
    """
    # Limit styles in test mode
    if test_mode:
        styles = styles[:max_test_styles]
        logger.info(f"TEST MODE: Limited to {len(styles)} styles")
    
    logger.info(f"Getting inventory data for {len(styles)} styles...")
    
    all_inventory_data = []
    record_limit_reached = False
    total_styles = len(styles)
    processed_styles = 0
    
    # Process styles in batches to avoid overwhelming the API
    batch_size = 20
    for i in range(0, total_styles, batch_size):
        batch_styles = styles[i:i+batch_size]
        
        # Use ThreadPoolExecutor for parallel processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit tasks for each style in the batch
            future_to_style = {executor.submit(get_inventory_for_style, style, color_mappings): style for style in batch_styles}
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_style):
                style = future_to_style[future]
                try:
                    inventory_data = future.result()
                    # In test mode, limit the total number of records
                    if test_mode and len(all_inventory_data) + len(inventory_data) > max_test_records:
                        # Only add enough records to reach the limit
                        records_to_add = max_test_records - len(all_inventory_data)
                        all_inventory_data.extend(inventory_data[:records_to_add])
                        record_limit_reached = True
                        logger.info(f"TEST MODE: Reached record limit of {max_test_records}")
                    else:
                        all_inventory_data.extend(inventory_data)
                    
                    processed_styles += 1
                    logger.info(f"Processed {processed_styles}/{total_styles} styles. Total records so far: {len(all_inventory_data)}")
                except Exception as e:
                    logger.error(f"Error processing style {style}: {str(e)}")
        
        # Check if we've reached the record limit in test mode
        if record_limit_reached:
            logger.info("TEST MODE: Stopping processing as record limit reached")
            break
            
        # Sleep briefly between batches to avoid overwhelming the API
        logger.info(f"Completed batch {i//batch_size + 1}/{(total_styles + batch_size - 1)//batch_size}. Sleeping before next batch...")
        time.sleep(5)
    
    logger.info(f"Retrieved a total of {len(all_inventory_data)} inventory records for {processed_styles} styles.")
    return all_inventory_data

def import_inventory_to_caspio(inventory_data, clear_existing=True):
    """Import inventory data to Caspio.
    
    Args:
        inventory_data: List of inventory records to import
        clear_existing: If True, clear existing inventory data before import
    """
    logger.info("Importing inventory data to Caspio...")
    
    try:
        # Clear existing inventory data if requested
        if clear_existing:
            logger.info("Clearing existing inventory data from Caspio...")
            # Use direct API request with query parameter
            endpoint = f"rest/v2/tables/Inventory/records"
            headers = {
                'Authorization': f'Bearer {caspio_client.get_access_token()}',
                'Content-Type': 'application/json'
            }
            params = {'q.where': '1=1'}
            url = f"{caspio_client.base_url}/{endpoint}"
            
            response = requests.delete(url, headers=headers, params=params)
            response.raise_for_status()
            
            logger.info(f"Cleared existing inventory data from Caspio. Response: {response.text}")
        else:
            logger.info("Skipping clearing existing inventory data (incremental update mode).")
        
        # Import inventory data in batches
        batch_size = 10  # Smaller batch size for testing
        total_records = len(inventory_data)
        records_inserted = 0
        
        # Debug: Print the first record to see its structure
        if total_records > 0:
            logger.info(f"Sample record structure: {json.dumps(inventory_data[0], indent=2)}")
        
        # Now insert the records
        for i in range(0, total_records, batch_size):
            batch = inventory_data[i:i+batch_size]
            
            # Insert each record in the batch
            batch_success = 0
            for inventory_record in batch:
                try:
                    # Use direct API request
                    endpoint = f"rest/v2/tables/Inventory/records"
                    headers = {
                        'Authorization': f'Bearer {caspio_client.get_access_token()}',
                        'Content-Type': 'application/json'
                    }
                    url = f"{caspio_client.base_url}/{endpoint}"
                    
                    response = requests.post(url, headers=headers, json=inventory_record)
                    
                    if response.status_code in [200, 201, 204]:
                        batch_success += 1
                    else:
                        logger.error(f"Error inserting record. Status code: {response.status_code}")
                        logger.error(f"Response content: {response.text}")
                        logger.error(f"Record data: {json.dumps(inventory_record)}")
                except Exception as e:
                    logger.error(f"Error inserting record: {str(e)}")
                    logger.error(f"Record data: {json.dumps(inventory_record)}")
            
            records_inserted += batch_success
            logger.info(f"Imported {records_inserted} of {total_records} inventory records ({(records_inserted/total_records)*100:.1f}%).")
            
            # Sleep briefly to avoid overwhelming the API
            time.sleep(1)
        
        logger.info(f"Successfully imported {records_inserted} inventory records to Caspio.")
        return records_inserted
    except Exception as e:
        logger.error(f"Error importing inventory data to Caspio: {str(e)}")
        return 0

def main():
    """Main function to import SanMar inventory data into Caspio."""
    if TEST_MODE:
        logger.info("Starting TEST IMPORT of SanMar inventory data to Caspio...")
        logger.info(f"Test configuration: Max {MAX_TEST_STYLES} styles, approximately {MAX_TEST_RECORDS} records")
    else:
        logger.info("Starting FULL IMPORT of all SanMar inventory data to Caspio...")
    
    # Check if SanMar API credentials are set
    if not SANMAR_USERNAME or not SANMAR_PASSWORD or not SANMAR_CUSTOMER_NUMBER:
        logger.error("SanMar API credentials are not properly configured. Please check your .env file.")
        sys.exit(1)
    
    # Get color mappings from Caspio
    color_mappings = get_color_mappings_from_caspio()
    if not color_mappings:
        logger.warning("No color mappings found in Caspio. Using default color mappings.")
    
    # Get all styles from Caspio or SanMar
    styles = get_product_styles_from_caspio()
    if not styles:
        logger.warning("No styles found in Caspio. Getting all styles from SanMar API...")
        styles = get_all_styles_from_sanmar()
    
    if not styles:
        logger.error("Failed to get any styles. Cannot proceed with import.")
        sys.exit(1)
    
    logger.info(f"Found {len(styles)} styles to process.")
    
    # Get inventory data for styles
    inventory_data = get_all_inventory_data(
        styles,
        color_mappings,
        test_mode=TEST_MODE,
        max_test_styles=MAX_TEST_STYLES,
        max_test_records=MAX_TEST_RECORDS
    )
    
    if not inventory_data:
        logger.error("Failed to get any inventory data. Cannot proceed with import.")
        sys.exit(1)
    
    logger.info(f"Retrieved {len(inventory_data)} inventory records in total.")
    
    # Import inventory data to Caspio (clear existing data for initial import)
    records_inserted = import_inventory_to_caspio(inventory_data, clear_existing=True)
    
    logger.info(f"Import completed. {records_inserted} out of {len(inventory_data)} records inserted.")
    
    # Summary
    logger.info("=== Import Summary ===")
    if TEST_MODE:
        logger.info("TEST MODE: Limited import for verification")
    logger.info(f"Total styles processed: {len(styles) if len(inventory_data) > 0 else 0}")
    logger.info(f"Total inventory records retrieved: {len(inventory_data)}")
    logger.info(f"Total records inserted into Caspio: {records_inserted}")
    if len(inventory_data) > 0:
        logger.info(f"Success rate: {(records_inserted/len(inventory_data))*100:.1f}%")
    logger.info("=====================")
    
    if TEST_MODE and records_inserted > 0:
        logger.info("TEST IMPORT SUCCESSFUL! To import all inventory data:")
        logger.info("1. Set TEST_MODE = False in the script")
        logger.info("2. Run the script again")

if __name__ == "__main__":
    main()