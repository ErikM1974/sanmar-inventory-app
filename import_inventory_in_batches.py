#!/usr/bin/env python
"""
Script to import SanMar inventory data into Caspio in smaller batches with checkpointing.
This script processes styles in batches and saves progress after each batch.
"""

import os
import sys
import json
import logging
import requests
import time
import pickle
from datetime import datetime
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("inventory_batch_import.log"),
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

# Caspio API credentials
CASPIO_BASE_URL = os.getenv('CASPIO_BASE_URL')
CASPIO_CLIENT_ID = os.getenv('CASPIO_CLIENT_ID')
CASPIO_CLIENT_SECRET = os.getenv('CASPIO_CLIENT_SECRET')

# Configuration
BATCH_SIZE = 10  # Number of styles to process in each batch
CHECKPOINT_FILE = "inventory_import_checkpoint.pkl"
RECORDS_PER_BATCH = 100  # Number of records to insert in each database batch

# SanMar API endpoints
SANMAR_WSDL = {
    'inventory': 'https://ws.sanmar.com:8080/promostandards/InventoryServiceBindingV2final?WSDL'
}

# Initialize Caspio client
caspio_client = None
if CASPIO_CLIENT_ID and CASPIO_CLIENT_SECRET:
    caspio_client = CaspioClient(
        base_url=CASPIO_BASE_URL,
        client_id=CASPIO_CLIENT_ID,
        client_secret=CASPIO_CLIENT_SECRET
    )
else:
    logger.error("Caspio API credentials are not properly configured. Please check your .env file.")
    sys.exit(1)

def get_styles_from_caspio():
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

def get_inventory_for_style(style, color_mappings=None):
    """Get inventory data for a specific style from SanMar API."""
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
        
        # Check if we have a valid response
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
                        
                        # Get the partId as the UNIQUE_KEY
                        unique_key = None
                        if hasattr(part, 'partId'):
                            unique_key = str(part.partId)
                            logger.debug(f"Found partId as UNIQUE_KEY: {unique_key}")
                        
                        if color_name and size_name and unique_key:
                            # Map the color name to display color name if mappings are provided
                            display_color = color_mappings.get(color_name, color_name) if color_mappings else color_name
                            
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

def clear_inventory_table():
    """Clear the Inventory table in Caspio."""
    try:
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
        return True
    except Exception as e:
        logger.error(f"Error clearing inventory data: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return False

def import_inventory_batch(inventory_data):
    """Import a batch of inventory data to Caspio."""
    try:
        # Import inventory data in smaller batches
        batch_size = RECORDS_PER_BATCH
        total_records = len(inventory_data)
        records_inserted = 0
        
        for i in range(0, total_records, batch_size):
            batch = inventory_data[i:i+batch_size]
            batch_success = 0
            
            # Insert each record in the batch
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
        
        return records_inserted
    except Exception as e:
        logger.error(f"Error importing inventory batch: {str(e)}")
        return 0

def save_checkpoint(processed_styles, total_records_inserted):
    """Save checkpoint of processed styles and total records inserted."""
    try:
        checkpoint_data = {
            'processed_styles': processed_styles,
            'total_records_inserted': total_records_inserted,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(CHECKPOINT_FILE, 'wb') as f:
            pickle.dump(checkpoint_data, f)
        
        logger.info(f"Saved checkpoint: {len(processed_styles)} styles processed, {total_records_inserted} records inserted.")
        return True
    except Exception as e:
        logger.error(f"Error saving checkpoint: {str(e)}")
        return False

def load_checkpoint():
    """Load checkpoint of processed styles and total records inserted."""
    try:
        if os.path.exists(CHECKPOINT_FILE):
            with open(CHECKPOINT_FILE, 'rb') as f:
                checkpoint_data = pickle.load(f)
            
            processed_styles = checkpoint_data.get('processed_styles', [])
            total_records_inserted = checkpoint_data.get('total_records_inserted', 0)
            timestamp = checkpoint_data.get('timestamp', 'unknown')
            
            logger.info(f"Loaded checkpoint from {timestamp}: {len(processed_styles)} styles processed, {total_records_inserted} records inserted.")
            return processed_styles, total_records_inserted
        else:
            logger.info("No checkpoint file found. Starting from scratch.")
            return [], 0
    except Exception as e:
        logger.error(f"Error loading checkpoint: {str(e)}")
        return [], 0

def main():
    """Main function to import SanMar inventory data into Caspio in batches."""
    logger.info("Starting SanMar inventory import in batches...")
    
    # Check if SanMar API credentials are set
    if not SANMAR_USERNAME or not SANMAR_PASSWORD:
        logger.error("SanMar API credentials are not properly configured. Please check your .env file.")
        sys.exit(1)
    
    # Get all styles from Caspio
    all_styles = get_styles_from_caspio()
    if not all_styles:
        logger.error("Failed to get product styles from Caspio. Make sure the Sanmar_Bulk table is populated.")
        sys.exit(1)
    
    # Load checkpoint if exists
    processed_styles, total_records_inserted = load_checkpoint()
    
    # Filter out already processed styles
    styles_to_process = [style for style in all_styles if style not in processed_styles]
    
    # Ask user if they want to clear the table before importing
    if not processed_styles:  # Only ask if starting from scratch
        clear_table = input("Do you want to clear the Inventory table before importing? (y/n): ").lower() == 'y'
        if clear_table:
            if not clear_inventory_table():
                logger.error("Failed to clear inventory table. Aborting import.")
                sys.exit(1)
    
    logger.info(f"Processing {len(styles_to_process)} styles in batches of {BATCH_SIZE}...")
    
    # Process styles in batches
    for i in range(0, len(styles_to_process), BATCH_SIZE):
        batch = styles_to_process[i:i+BATCH_SIZE]
        logger.info(f"Processing batch {i//BATCH_SIZE + 1}/{(len(styles_to_process) + BATCH_SIZE - 1)//BATCH_SIZE}: {len(batch)} styles")
        
        # Get inventory data for each style in the batch
        batch_inventory_data = []
        for style in batch:
            style_inventory = get_inventory_for_style(style)
            batch_inventory_data.extend(style_inventory)
            processed_styles.append(style)
            
            # Sleep briefly to avoid overwhelming the API
            time.sleep(0.5)
        
        # Import the batch inventory data
        if batch_inventory_data:
            records_inserted = import_inventory_batch(batch_inventory_data)
            total_records_inserted += records_inserted
            logger.info(f"Imported {records_inserted} records in this batch. Total: {total_records_inserted}")
        else:
            logger.warning(f"No inventory data found for batch {i//BATCH_SIZE + 1}")
        
        # Save checkpoint after each batch
        save_checkpoint(processed_styles, total_records_inserted)
        
        logger.info(f"Completed batch {i//BATCH_SIZE + 1}. Sleeping before next batch...")
        time.sleep(5)  # Sleep between batches to avoid overwhelming the API
    
    logger.info("SanMar inventory import completed successfully.")
    logger.info(f"Total styles processed: {len(processed_styles)}")
    logger.info(f"Total records inserted: {total_records_inserted}")
    
    # Clean up checkpoint file if all styles were processed
    if len(processed_styles) == len(all_styles):
        try:
            os.remove(CHECKPOINT_FILE)
            logger.info("Removed checkpoint file as all styles were processed.")
        except Exception as e:
            logger.error(f"Error removing checkpoint file: {str(e)}")

if __name__ == "__main__":
    main()