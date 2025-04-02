#!/usr/bin/env python
"""
Script to add a UNIQUE_KEY column to the Inventory table in Caspio.
"""

import os
import logging
import requests
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("add_unique_key.log"),
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
        
        logger.info("Successfully obtained access token.")
        return access_token
    except Exception as e:
        logger.error(f"Error getting authentication token: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return None

def add_column_to_table(access_token, table_name, column_definition):
    """Add a column to a table."""
    url = f"{CASPIO_BASE_URL}/rest/v2/tables/{table_name}/fields"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        logger.info(f"Adding column to {table_name}: {column_definition}")
        response = requests.post(url, headers=headers, json=column_definition)
        
        # Log the raw response
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response headers: {response.headers}")
        logger.info(f"Response content: {response.text}")
        
        response.raise_for_status()
        
        logger.info(f"Successfully added column to {table_name}.")
        return True
    except Exception as e:
        logger.error(f"Error adding column: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return False

def main():
    """Main function to add UNIQUE_KEY column to Inventory table."""
    logger.info("Starting to add UNIQUE_KEY column to Inventory table...")
    
    # Get access token
    access_token = get_access_token()
    if not access_token:
        logger.error("Failed to get access token. Cannot proceed.")
        return
    
    # Define the column to add
    column_definition = {
        "Name": "UNIQUE_KEY",
        "Type": "STRING",
        "Length": 255,
        "Unique": False,
        "UniqueAllowNulls": False,
        "Label": "Unique Key",
        "Description": "Unique identifier from SanMar API (partId)",
        "DisplayOrder": 9,  # After LAST_UPDATED
        "OnInsert": True,
        "OnUpdate": True,
        "Required": False
    }
    
    # Add the column to the Inventory table
    if add_column_to_table(access_token, "Inventory", column_definition):
        logger.info("Successfully added UNIQUE_KEY column to Inventory table.")
    else:
        logger.error("Failed to add UNIQUE_KEY column to Inventory table.")
    
    logger.info("Completed adding UNIQUE_KEY column to Inventory table.")

if __name__ == "__main__":
    main()