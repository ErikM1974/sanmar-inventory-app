#!/usr/bin/env python
"""
Script to import SanMar inventory data into Caspio daily.
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
        logging.FileHandler("daily_inventory_import.log"),
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
    'inventory': 'https://ws.sanmar.com:8080/SanMarWebService/SanMarInventoryServicePort?wsdl'
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
    """Get all product styles from the Caspio Products table."""
    try:
        # Query the Products table to get all unique styles
        styles = set()
        products = caspio_client.query_records('Products', fields=['STYLE'])
        
        for product in products:
            if 'STYLE' in product:
                styles.add(product['STYLE'])
        
        logger.info(f"Retrieved {len(styles)} unique styles from Caspio Products table.")
        return list(styles)
    except Exception as e:
        logger.error(f"Error getting product styles from Caspio: {str(e)}")
        return []

def get_sanmar_inventory(styles):
    """Get inventory information for products from SanMar API."""
    logger.info("Getting inventory information from SanMar API...")
    
    try:
        # Create a SOAP client for the Inventory service
        client = create_soap_client(SANMAR_WSDL['inventory'])
        
        # Get inventory for each style
        inventory_data = []
        total_styles = len(styles)
        
        for i, style in enumerate(styles):
            logger.info(f"Getting inventory for style {style} ({i+1}/{total_styles})...")
            
            # Call the getInventoryLevels method
            response = client.service.getInventoryLevels(
                username=SANMAR_USERNAME,
                password=SANMAR_PASSWORD,
                customerNumber=SANMAR_CUSTOMER_NUMBER,
                styleNumber=style
            )
            
            # Process the response
            if hasattr(response, 'inventoryLevels') and response.inventoryLevels:
                for inventory_level in response.inventoryLevels:
                    color_name = inventory_level.color
                    
                    for size_inventory in inventory_level.sizeInventory:
                        size_name = size_inventory.size
                        
                        for warehouse in size_inventory.warehouseInventory:
                            warehouse_id = warehouse.warehouseId
                            quantity = int(warehouse.quantity)
                            
                            # Add inventory record
                            inventory_data.append({
                                'STYLE': style,
                                'COLOR_NAME': color_name,
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

def main():
    """Main function to import SanMar inventory data into Caspio."""
    logger.info("Starting daily SanMar inventory import...")
    
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
        logger.error("Failed to get product styles from Caspio. Make sure the Products table is populated.")
        sys.exit(1)
    
    # Get inventory data from SanMar
    logger.info("Getting inventory data from SanMar API...")
    inventory_data = get_sanmar_inventory(styles)
    if not inventory_data:
        logger.error("Failed to get inventory data from SanMar API.")
        sys.exit(1)
    
    # Import inventory data to Caspio
    if import_inventory_to_caspio(inventory_data):
        logger.info("Daily SanMar inventory import completed successfully.")
    else:
        logger.error("Failed to import inventory data to Caspio.")
        sys.exit(1)

if __name__ == "__main__":
    main()