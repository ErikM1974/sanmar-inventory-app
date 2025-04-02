#!/usr/bin/env python
"""
Test script to create a simple table in Caspio.
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
        logging.FileHandler("caspio_test.log"),
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

def make_api_request(endpoint, method="GET", data=None):
    """Make a request to the Caspio API."""
    # Ensure we don't have double slashes in the URL
    if CASPIO_BASE_URL.endswith('/') and endpoint.startswith('/'):
        endpoint = endpoint[1:]
    elif not CASPIO_BASE_URL.endswith('/') and not endpoint.startswith('/'):
        endpoint = f"/{endpoint}"
    
    url = f"{CASPIO_BASE_URL}{endpoint}"
    headers = {
        'Authorization': f'Bearer {get_access_token()}',
        'Content-Type': 'application/json'
    }
    
    logger.info(f"Making API request to: {url}")
    logger.info(f"Method: {method}")
    logger.info(f"Headers: {headers}")
    if data:
        logger.info(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            logger.info("Sending POST request with data")
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            logger.error(f"Unsupported HTTP method: {method}")
            return None
        
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response content: {response.text}")
        
        response.raise_for_status()
        
        if response.status_code == 204:  # No content
            return {}
        
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API request error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return None

def get_tables():
    """Get a list of tables in the Caspio application."""
    return make_api_request("rest/v2/tables")

def create_test_table():
    """Create a test table in Caspio."""
    table_name = "TestTable"
    
    # Define the table structure
    table_definition = {
        "Name": table_name,
        "Columns": [
            {
                "Name": "ID",
                "Type": "AutoNumber",
                "Label": "ID"
            },
            {
                "Name": "NAME",
                "Type": "String",
                "Length": 50,
                "Label": "Name"
            }
        ]
    }
    
    # Create the table
    result = make_api_request("rest/v2/tables", method="POST", data=table_definition)
    if result:
        logger.info(f"Successfully created table '{table_name}'.")
        return True
    else:
        logger.error(f"Failed to create table '{table_name}'.")
        return False

def main():
    """Main function to test Caspio API."""
    logger.info("Starting Caspio API test...")
    
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
    
    # Get tables
    logger.info("Getting tables...")
    tables = get_tables()
    logger.info(f"Tables: {tables}")
    
    # Create test table
    logger.info("Creating test table...")
    create_test_table()
    
    logger.info("Caspio API test completed.")

if __name__ == "__main__":
    main()