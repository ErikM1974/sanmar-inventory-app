#!/usr/bin/env python
"""
Script to create the Inventory table in Caspio.
"""

import os
import json
import logging
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("inventory_table_creation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Caspio API credentials
CASPIO_BASE_URL = os.getenv('CASPIO_BASE_URL')
CASPIO_CLIENT_ID = os.getenv('CASPIO_CLIENT_ID')
CASPIO_CLIENT_SECRET = os.getenv('CASPIO_CLIENT_SECRET')

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
        
        return access_token
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting authentication token: {str(e)}")
        return None

def create_inventory_table():
    """Create the Inventory table in Caspio."""
    # Ensure we don't have double slashes in the URL
    if CASPIO_BASE_URL.endswith('/'):
        url = f"{CASPIO_BASE_URL}rest/v2/tables"
    else:
        url = f"{CASPIO_BASE_URL}/rest/v2/tables"
    headers = {
        'Authorization': f'Bearer {get_access_token()}',
        'Content-Type': 'application/json'
    }
    
    # Define the table structure
    table_definition = {
        "Name": "Inventory",
        "Columns": [
            {
                "Name": "INVENTORY_ID",
                "Type": "AutoNumber",
                "Unique": True,
                "Label": "Inventory ID"
            },
            {
                "Name": "STYLE",
                "Type": "Text",
                "Length": 50,
                "Label": "Style"
            },
            {
                "Name": "COLOR_NAME",
                "Type": "Text",
                "Length": 100,
                "Label": "Color Name"
            },
            {
                "Name": "SIZE",
                "Type": "Text",
                "Length": 20,
                "Label": "Size"
            },
            {
                "Name": "WAREHOUSE_ID",
                "Type": "Text",
                "Length": 20,
                "Label": "Warehouse ID"
            },
            {
                "Name": "QUANTITY",
                "Type": "Number",
                "Label": "Quantity"
            },
            {
                "Name": "LAST_UPDATED",
                "Type": "DateTime",
                "Label": "Last Updated"
            }
        ]
    }
    
    logger.info(f"Creating table with definition: {json.dumps(table_definition, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=table_definition)
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response content: {response.text}")
        
        response.raise_for_status()
        
        logger.info("Successfully created Inventory table.")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating Inventory table: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return False

def main():
    """Main function to create the Inventory table."""
    logger.info("Starting Inventory table creation...")
    
    # Check if Caspio API is properly configured
    if not CASPIO_BASE_URL or not CASPIO_CLIENT_ID or not CASPIO_CLIENT_SECRET:
        logger.error("Caspio API is not properly configured. Please check your .env file.")
        return
    
    # Test Caspio API connection
    logger.info("Testing Caspio API connection...")
    token = get_access_token()
    if not token:
        logger.error("Failed to connect to Caspio API. Please check your credentials.")
        return
    
    logger.info("Successfully connected to Caspio API.")
    
    # Create Inventory table
    create_inventory_table()
    
    logger.info("Inventory table creation completed.")

if __name__ == "__main__":
    main()