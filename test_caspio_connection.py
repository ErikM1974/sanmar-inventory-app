#!/usr/bin/env python
"""
Script to test the connection to the Caspio API.
"""

import os
import json
import logging
import requests
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_caspio_connection.log"),
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

def get_access_token_from_client_credentials():
    """Get an access token using client credentials."""
    if not CASPIO_CLIENT_ID or not CASPIO_CLIENT_SECRET:
        logger.error("Client ID or Client Secret is not set. Please set CASPIO_CLIENT_ID and CASPIO_CLIENT_SECRET in your .env file.")
        return None
    
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
        expires_in = token_data.get('expires_in', 3600)
        
        logger.info(f"Successfully obtained access token using client credentials. Expires in {expires_in} seconds.")
        
        return access_token
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting access token: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return None

def test_api_connection(access_token):
    """Test the connection to the Caspio API."""
    if not access_token:
        logger.error("No access token available.")
        return False
    
    # Test endpoint - get list of tables
    endpoint = f"{CASPIO_BASE_URL}/rest/v2/tables"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        
        tables_data = response.json()
        if 'Result' in tables_data and isinstance(tables_data['Result'], list):
            table_count = len(tables_data['Result'])
            logger.info(f"Successfully connected to Caspio API. Found {table_count} tables.")
            
            # Print the list of tables
            print("\nAvailable tables:")
            for table in tables_data['Result']:
                print(f"- {table}")
            
            return True
        else:
            logger.error(f"Unexpected response format: {tables_data}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to Caspio API: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return False

def main():
    """Main function to test the connection to the Caspio API."""
    logger.info("Starting Caspio API connection test...")
    
    # Check if access token is available
    access_token = CASPIO_ACCESS_TOKEN
    
    # If no access token is available, try to get one using client credentials
    if not access_token:
        logger.info("No access token found. Trying to get one using client credentials...")
        access_token = get_access_token_from_client_credentials()
    
    # Test the API connection
    if access_token:
        if test_api_connection(access_token):
            logger.info("Caspio API connection test completed successfully.")
        else:
            logger.error("Caspio API connection test failed.")
    else:
        logger.error("No access token available. Cannot test API connection.")

if __name__ == "__main__":
    main()