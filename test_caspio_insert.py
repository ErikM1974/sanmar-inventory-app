#!/usr/bin/env python
"""
Test script to verify Caspio API connectivity and insert a single record.
"""

import os
import json
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_caspio_insert.log"),
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

def get_table_fields(access_token, table_name):
    """Get the fields of a table."""
    url = f"{CASPIO_BASE_URL}/rest/v2/tables/{table_name}/fields"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"Successfully retrieved fields for table {table_name}.")
        return result.get('Result', [])
    except Exception as e:
        logger.error(f"Error getting table fields: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return []

def insert_record(access_token, table_name, record_data):
    """Insert a record into a table."""
    url = f"{CASPIO_BASE_URL}/rest/v2/tables/{table_name}/records"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        logger.info(f"Inserting record into {table_name}: {json.dumps(record_data, indent=2)}")
        response = requests.post(url, headers=headers, json=record_data)
        
        # Log the raw response
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response headers: {response.headers}")
        logger.info(f"Response content: {response.text}")
        
        response.raise_for_status()
        
        if response.text:
            result = response.json()
            logger.info(f"Successfully inserted record into {table_name}.")
            return result
        else:
            logger.info(f"Record inserted, but no response content returned.")
            return {"success": True}
    except Exception as e:
        logger.error(f"Error inserting record: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return None

def delete_all_records(access_token, table_name):
    """Delete all records from a table."""
    url = f"{CASPIO_BASE_URL}/rest/v2/tables/{table_name}/records"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Try with a query parameter
        params = {'q.where': '1=1'}
        logger.info(f"Deleting all records from {table_name} with params: {params}")
        response = requests.delete(url, headers=headers, params=params)
        
        # Log the raw response
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response headers: {response.headers}")
        logger.info(f"Response content: {response.text}")
        
        response.raise_for_status()
        
        logger.info(f"Successfully deleted all records from {table_name}.")
        return True
    except Exception as e:
        logger.error(f"Error deleting records: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return False

def main():
    """Main function to test Caspio API."""
    logger.info("Starting Caspio API test...")
    
    # Get access token
    access_token = get_access_token()
    if not access_token:
        logger.error("Failed to get access token. Cannot proceed with test.")
        return
    
    # Get table fields
    inventory_fields = get_table_fields(access_token, 'Inventory')
    logger.info(f"Inventory table fields: {json.dumps(inventory_fields, indent=2)}")
    
    # Create a test record
    test_record = {
        'STYLE': 'TEST001',
        'COLOR_NAME': 'TEST',
        'DISPLAY_COLOR': 'Test Color',
        'SIZE': 'M',
        'WAREHOUSE_ID': '1',
        'QUANTITY': 100,
        'LAST_UPDATED': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Insert the test record
    result = insert_record(access_token, 'Inventory', test_record)
    if result:
        logger.info("Test record inserted successfully!")
        
        # If the record was inserted successfully, try to delete all records
        if delete_all_records(access_token, 'Inventory'):
            logger.info("Successfully deleted all records from Inventory table.")
        else:
            logger.error("Failed to delete all records from Inventory table.")
    else:
        logger.error("Failed to insert test record.")
    
    logger.info("Caspio API test completed.")

if __name__ == "__main__":
    main()