#!/usr/bin/env python
"""
Script to import ALL SanMar inventory data into Caspio.
This script gets styles directly from SanMar API and imports all inventory data.
"""

import os
import sys
import csv
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
        logging.FileHandler("complete_inventory_import.log"),
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
except ImportError:
    logger.error("Failed to import custom modules. Make sure middleware_client.py is in the same directory.")
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
PROGRESS_FILE = "complete_inventory_import_progress.csv"
BATCH_SIZE = 10  # Number of records to insert in each database batch
STYLE_BATCH_SIZE = 50  # Number of styles to process in each batch

# SanMar API endpoints
SANMAR_WSDL = {
    'inventory': 'https://ws.sanmar.com:8080/promostandards/InventoryServiceBindingV2final?WSDL',
    'product_info': 'https://ws.sanmar.com:8080/SanMarWebService/SanMarProductInfoServicePort?wsdl'
}

def get_access_token():
    """Get an access token from the Caspio API."""
    auth_url = f"{CASPIO_BASE_URL}/oauth/token"
    payload = {
        'grant_type': 'client_credentials',
        'client_id': CASPIO_CLIENT_ID,
        'client_secret': CASPIO_CLIENT_SECRET
    }
    
    try:
        response = requests.post(auth_url, data=payload)
        response.raise_for_status()
        
        token_data = response.json()
        access_token = token_data.get('access_token')
        
        logger.info("Successfully obtained access token.")
        return access_token
    except Exception as e:
        logger.error(f"Error getting authentication token: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return None

def get_all_inventory_direct():
    """Try to get all inventory data directly from SanMar API without first getting styles."""
    try:
        logger.info("Attempting to get all inventory data directly from SanMar API...")
        
        # Create a SOAP client for the Inventory service
        client = create_soap_client(SANMAR_WSDL['inventory'])
        
        # Try different approaches to get all inventory
        
        # Approach 1: Try with a wildcard productId
        logger.info("Trying with wildcard productId...")
        request_data = {
            "wsVersion": "2.0.0",
            "id": SANMAR_USERNAME,
            "password": SANMAR_PASSWORD,
            "productId": "*"  # Try wildcard
        }
        
        try:
            response = client.service.getInventoryLevels(**request_data)
            
            # Process the response
            inventory_data = process_inventory_response(response, "wildcard")
            
            if inventory_data:
                logger.info(f"Successfully retrieved {len(inventory_data)} inventory records using wildcard approach.")
                return inventory_data
        except Exception as e:
            logger.warning(f"Wildcard approach failed: {str(e)}")
        
        # Approach 2: Try with an empty productId
        logger.info("Trying with empty productId...")
        request_data = {
            "wsVersion": "2.0.0",
            "id": SANMAR_USERNAME,
            "password": SANMAR_PASSWORD,
            "productId": ""  # Try empty string
        }
        
        try:
            response = client.service.getInventoryLevels(**request_data)
            
            # Process the response
            inventory_data = process_inventory_response(response, "empty")
            
            if inventory_data:
                logger.info(f"Successfully retrieved {len(inventory_data)} inventory records using empty productId approach.")
                return inventory_data
        except Exception as e:
            logger.warning(f"Empty productId approach failed: {str(e)}")
        
        # Approach 3: Try with a special value that might return all inventory
        logger.info("Trying with 'ALL' as productId...")
        request_data = {
            "wsVersion": "2.0.0",
            "id": SANMAR_USERNAME,
            "password": SANMAR_PASSWORD,
            "productId": "ALL"  # Try special value
        }
        
        try:
            response = client.service.getInventoryLevels(**request_data)
            
            # Process the response
            inventory_data = process_inventory_response(response, "ALL")
            
            if inventory_data:
                logger.info(f"Successfully retrieved {len(inventory_data)} inventory records using 'ALL' approach.")
                return inventory_data
        except Exception as e:
            logger.warning(f"'ALL' approach failed: {str(e)}")
        
        logger.warning("All direct approaches failed. Will need to query by individual styles.")
        return []
    except Exception as e:
        error_type, error_message = categorize_error(e)
        logger.error(f"Error getting inventory directly: {error_type} - {error_message}")
        return []

def process_inventory_response(response, approach):
    """Process inventory response from SanMar API."""
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
                    # Extract style, color and size from part
                    style = getattr(part, 'productId', None) or "Unknown"
                    color_name = getattr(part, 'partColor', None)
                    size_name = getattr(part, 'labelSize', None)
                    
                    # Get the partId as the UNIQUE_KEY
                    unique_key = None
                    if hasattr(part, 'partId'):
                        unique_key = str(part.partId)
                    
                    if color_name and size_name and unique_key:
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
                                        'DISPLAY_COLOR': color_name,  # Use color_name as display_color for simplicity
                                        'SIZE': size_name,
                                        'WAREHOUSE_ID': warehouse_id,
                                        'QUANTITY': quantity,
                                        'UNIQUE_KEY': unique_key,
                                        'LAST_UPDATED': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    })
    
    logger.info(f"Processed {len(inventory_data)} inventory records from {approach} approach.")
    return inventory_data

def get_styles_from_bulk_table():
    """Get all styles from the Sanmar_Bulk_251816_Feb2024 table."""
    try:
        logger.info("Getting styles from Sanmar_Bulk_251816_Feb2024 table...")
        
        access_token = get_access_token()
        if not access_token:
            logger.error("Failed to get access token. Cannot proceed.")
            return []
        
        styles = set()
        page_size = 1000
        page = 1
        total_records = 0
        
        # Query the Sanmar_Bulk table with pagination
        while True:
            logger.info(f"Getting styles from page {page} (records {(page-1)*page_size + 1}-{page*page_size})...")
            
            endpoint = f"rest/v2/tables/Sanmar_Bulk_251816_Feb2024/records"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            params = {
                'q.select': 'STYLE',
                'q.distinct': 'true',
                'q.pageSize': str(page_size),
                'q.pageNumber': str(page)
            }
            url = f"{CASPIO_BASE_URL}/{endpoint}"
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or 'Result' not in data or not data['Result']:
                # No more records
                break
            
            # Extract styles from the response
            for record in data['Result']:
                if 'STYLE' in record:
                    styles.add(record['STYLE'])
            
            total_records += len(data['Result'])
            
            # Check if we've reached the end of the records
            if len(data['Result']) < page_size:
                break
            
            # Move to the next page
            page += 1
            
            # Sleep briefly to avoid overwhelming the API
            time.sleep(1)
        
        styles_list = list(styles)
        logger.info(f"Retrieved {len(styles_list)} unique styles from {total_records} records in Sanmar_Bulk table.")
        return styles_list
    except Exception as e:
        logger.error(f"Error getting styles from Sanmar_Bulk table: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return []

def get_inventory_for_style(style):
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
                        
                        if color_name and size_name and unique_key:
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
                                            'DISPLAY_COLOR': color_name,  # Use color_name as display_color for simplicity
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

def insert_inventory_records(inventory_records):
    """Insert inventory records into Caspio."""
    try:
        access_token = get_access_token()
        if not access_token:
            logger.error("Failed to get access token. Cannot proceed.")
            return 0
        
        records_inserted = 0
        
        # Process records in batches
        for i in range(0, len(inventory_records), BATCH_SIZE):
            batch = inventory_records[i:i+BATCH_SIZE]
            batch_success = 0
            
            # Insert each record in the batch
            for record in batch:
                try:
                    # Use direct API request
                    endpoint = f"rest/v2/tables/Inventory/records"
                    headers = {
                        'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/json'
                    }
                    url = f"{CASPIO_BASE_URL}/{endpoint}"
                    
                    response = requests.post(url, headers=headers, json=record)
                    
                    if response.status_code in [200, 201, 204]:
                        batch_success += 1
                    else:
                        logger.error(f"Error inserting record. Status code: {response.status_code}")
                        logger.error(f"Response content: {response.text}")
                        logger.error(f"Record data: {json.dumps(record)}")
                except Exception as e:
                    logger.error(f"Error inserting record: {str(e)}")
                    logger.error(f"Record data: {json.dumps(record)}")
            
            records_inserted += batch_success
            logger.info(f"Inserted {batch_success} of {len(batch)} records in this batch.")
            
            # Sleep briefly to avoid overwhelming the API
            time.sleep(1)
        
        return records_inserted
    except Exception as e:
        logger.error(f"Error inserting inventory records: {str(e)}")
        return 0

def clear_inventory_table():
    """Clear the Inventory table in Caspio."""
    try:
        logger.info("Clearing existing inventory data from Caspio...")
        
        access_token = get_access_token()
        if not access_token:
            logger.error("Failed to get access token. Cannot proceed.")
            return False
        
        # Use direct API request with query parameter
        endpoint = f"rest/v2/tables/Inventory/records"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        params = {'q.where': '1=1'}
        url = f"{CASPIO_BASE_URL}/{endpoint}"
        
        response = requests.delete(url, headers=headers, params=params)
        response.raise_for_status()
        
        logger.info(f"Cleared existing inventory data from Caspio. Response: {response.text}")
        return True
    except Exception as e:
        logger.error(f"Error clearing inventory data: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return False

def load_progress():
    """Load progress from CSV file."""
    processed_styles = []
    total_records = 0
    
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', newline='') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 2:
                        processed_styles.append(row[0])
                        total_records += int(row[1])
            
            logger.info(f"Loaded progress: {len(processed_styles)} styles processed, {total_records} records inserted.")
        except Exception as e:
            logger.error(f"Error loading progress: {str(e)}")
    else:
        logger.info("No progress file found. Starting from scratch.")
    
    return processed_styles, total_records

def save_progress(style, records_inserted, total_records):
    """Save progress to CSV file."""
    try:
        file_exists = os.path.exists(PROGRESS_FILE)
        
        with open(PROGRESS_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            
            if not file_exists:
                writer.writerow(['Style', 'Records', 'Timestamp', 'Total'])
            
            writer.writerow([
                style,
                records_inserted,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                total_records
            ])
        
        logger.info(f"Saved progress for style {style}: {records_inserted} records inserted. Total: {total_records}")
        return True
    except Exception as e:
        logger.error(f"Error saving progress: {str(e)}")
        return False

def main():
    """Main function to import ALL SanMar inventory data into Caspio."""
    logger.info("Starting COMPLETE SanMar inventory import...")
    
    # Check if SanMar API credentials are set
    if not SANMAR_USERNAME or not SANMAR_PASSWORD:
        logger.error("SanMar API credentials are not properly configured. Please check your .env file.")
        sys.exit(1)
    
    # Check if Caspio API credentials are set
    if not CASPIO_CLIENT_ID or not CASPIO_CLIENT_SECRET:
        logger.error("Caspio API credentials are not properly configured. Please check your .env file.")
        sys.exit(1)
    
    # Load progress
    processed_styles, total_records_inserted = load_progress()
    
    # Ask user if they want to clear the table before importing
    if not processed_styles:  # Only ask if starting from scratch
        clear_table = input("Do you want to clear the Inventory table before importing? (y/n): ").lower() == 'y'
        if clear_table:
            if not clear_inventory_table():
                logger.error("Failed to clear inventory table. Aborting import.")
                sys.exit(1)
    
    # Get all styles from Sanmar_Bulk table
    logger.info("Getting all styles from Sanmar_Bulk table...")
    all_styles = get_styles_from_bulk_table()
    if not all_styles:
        logger.error("Failed to get styles from SanMar API. Cannot proceed.")
        sys.exit(1)
    
    # Filter out already processed styles
    styles_to_process = [style for style in all_styles if style not in processed_styles]
    
    logger.info(f"Processing {len(styles_to_process)} styles out of {len(all_styles)} total styles...")
    
    # Process styles in batches
    for i in range(0, len(styles_to_process), STYLE_BATCH_SIZE):
        style_batch = styles_to_process[i:i+STYLE_BATCH_SIZE]
        logger.info(f"Processing batch {i//STYLE_BATCH_SIZE + 1}/{(len(styles_to_process) + STYLE_BATCH_SIZE - 1)//STYLE_BATCH_SIZE}: {len(style_batch)} styles")
        
        # Process each style in the batch
        for j, style in enumerate(style_batch):
            logger.info(f"Processing style {i+j+1}/{len(styles_to_process)}: {style}")
            
            # Get inventory data for the style
            inventory_data = get_inventory_for_style(style)
            
            if inventory_data:
                # Insert inventory data
                records_inserted = insert_inventory_records(inventory_data)
                total_records_inserted += records_inserted
                
                # Save progress
                save_progress(style, records_inserted, total_records_inserted)
                
                logger.info(f"Processed style {style}: {records_inserted} records inserted. Total: {total_records_inserted}")
            else:
                logger.warning(f"No inventory data found for style {style}")
                save_progress(style, 0, total_records_inserted)
            
            # Sleep briefly to avoid overwhelming the API
            time.sleep(2)
        
        logger.info(f"Completed batch {i//STYLE_BATCH_SIZE + 1}. Sleeping before next batch...")
        time.sleep(10)  # Sleep between batches to avoid overwhelming the API
    
    logger.info("COMPLETE SanMar inventory import completed successfully.")
    logger.info(f"Total styles processed: {len(processed_styles) + len(styles_to_process)}")
    logger.info(f"Total records inserted: {total_records_inserted}")

if __name__ == "__main__":
    main()