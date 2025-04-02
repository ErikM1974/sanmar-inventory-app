#!/usr/bin/env python
"""
Simplified script to test importing data from SanMar to Caspio.
This script focuses on authentication and basic API calls.
"""

import os
import sys
import json
import logging
import requests
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_import.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Caspio API credentials
CASPIO_BASE_URL = os.getenv('CASPIO_BASE_URL', 'https://c3eku948.caspio.com')
CASPIO_ACCESS_TOKEN = os.getenv('CASPIO_ACCESS_TOKEN')
CASPIO_CLIENT_ID = os.getenv('CASPIO_CLIENT_ID')
CASPIO_CLIENT_SECRET = os.getenv('CASPIO_CLIENT_SECRET')

def get_access_token():
    """Get an access token for the Caspio API."""
    # First try to use the existing access token
    if CASPIO_ACCESS_TOKEN:
        logger.info("Using existing access token.")
        return CASPIO_ACCESS_TOKEN
    
    # If no access token is available, try to get one using client credentials
    if CASPIO_CLIENT_ID and CASPIO_CLIENT_SECRET:
        logger.info("Getting access token using client credentials...")
        
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
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting access token: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return None
    
    logger.error("No valid authentication method available.")
    return None

def get_styles_from_sanmar_bulk():
    """Get all styles from the Sanmar_Bulk_251816_Feb2024 table."""
    logger.info("Getting styles from Sanmar_Bulk_251816_Feb2024 table...")
    
    access_token = get_access_token()
    if not access_token:
        logger.error("Failed to get access token.")
        return []
    
    endpoint = f"{CASPIO_BASE_URL}/rest/v2/tables/Sanmar_Bulk_251816_Feb2024/records"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    params = {
        'q.select': 'STYLE',
        'q.distinct': 'true',
        'q.limit': 10  # Just get a few styles for testing
    }
    
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        if 'Result' in data and isinstance(data['Result'], list):
            styles = [item['STYLE'] for item in data['Result']]
            logger.info(f"Retrieved {len(styles)} styles from Sanmar_Bulk_251816_Feb2024 table.")
            return styles
        else:
            logger.error(f"Unexpected response format: {data}")
            return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting styles: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return []

def get_table_fields(table_name):
    """Get the fields of a table."""
    logger.info(f"Getting fields for {table_name} table...")
    
    access_token = get_access_token()
    if not access_token:
        logger.error("Failed to get access token.")
        return []
    
    endpoint = f"{CASPIO_BASE_URL}/rest/v2/tables/{table_name}/fields"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if 'Result' in data and isinstance(data['Result'], list):
            fields = data['Result']
            logger.info(f"Retrieved {len(fields)} fields from {table_name} table.")
            
            # Print field details
            logger.info(f"Fields in {table_name} table:")
            for field in fields:
                read_only = field.get('ReadOnly', False)
                auto_increment = field.get('AutoIncrement', False)
                field_type = field.get('Type', 'Unknown')
                field_name = field.get('Name', 'Unknown')
                logger.info(f"- {field_name} ({field_type}): ReadOnly={read_only}, AutoIncrement={auto_increment}")
            
            return fields
        else:
            logger.error(f"Unexpected response format: {data}")
            return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting fields: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return []

def test_insert_inventory():
    """Test inserting a record into the Inventory table."""
    logger.info("Testing insert into Inventory table...")
    
    access_token = get_access_token()
    if not access_token:
        logger.error("Failed to get access token.")
        return False
    
    # Create a test record
    test_record = {
        'STYLE': 'TEST001',
        'COLOR_NAME': 'Test Color',
        'SIZE': 'M',
        'WAREHOUSE_ID': 'TEST',
        'QUANTITY': 100,
        'LAST_UPDATED': '2025-04-02T09:00:00'
    }
    
    endpoint = f"{CASPIO_BASE_URL}/rest/v2/tables/Inventory/records"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(endpoint, headers=headers, json=test_record)
        response.raise_for_status()
        
        logger.info("Successfully inserted test record into Inventory table.")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error inserting test record: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return False

def test_insert_pricing():
    """Test inserting a record into the Pricing table."""
    logger.info("Testing insert into Pricing table...")
    
    access_token = get_access_token()
    if not access_token:
        logger.error("Failed to get access token.")
        return False
    
    # Create a test record with minimal fields
    test_record = {
        'STYLE': 'TEST001',
        'COLOR_NAME': 'Test Color',
        'SIZE': 'M',
        'PIECE_PRICE': 19.99,
        'CASE_PRICE': 179.91,
        'CASE_SIZE': 10,
        'PROGRAM_PRICE': 17.99
        # Omitting LAST_UPDATED to see if it's causing the issue
    }
    
    endpoint = f"{CASPIO_BASE_URL}/rest/v2/tables/Pricing/records"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(endpoint, headers=headers, json=test_record)
        response.raise_for_status()
        
        logger.info("Successfully inserted test record into Pricing table.")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error inserting test record: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return False

def main():
    """Main function to test the import process."""
    logger.info("Starting import test...")
    
    # Check the fields of the Pricing table to see which ones are read-only
    logger.info("Checking Pricing table fields...")
    pricing_fields = get_table_fields('Pricing')
    
    # Test getting styles from Sanmar_Bulk
    styles = get_styles_from_sanmar_bulk()
    if not styles:
        logger.error("Failed to get styles from Sanmar_Bulk_251816_Feb2024 table.")
        return
    
    # Print the styles we found
    logger.info("Styles found:")
    for style in styles:
        logger.info(f"- {style}")
    
    # Test inserting into Inventory table
    if not test_insert_inventory():
        logger.error("Failed to insert test record into Inventory table.")
        return
    
    # Test inserting into Pricing table
    if not test_insert_pricing():
        logger.error("Failed to insert test record into Pricing table.")
        return
    
    logger.info("Import test completed successfully.")

if __name__ == "__main__":
    main()