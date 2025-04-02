#!/usr/bin/env python
"""
Script to test the Caspio API connection using the bearer token.
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
        logging.FileHandler("test_caspio_bearer_token.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Caspio API credentials
CASPIO_BASE_URL = os.getenv('CASPIO_BASE_URL')
CASPIO_ACCESS_TOKEN = os.getenv('CASPIO_ACCESS_TOKEN')

def test_caspio_connection():
    """Test the connection to the Caspio API using the bearer token."""
    if not CASPIO_BASE_URL or not CASPIO_ACCESS_TOKEN:
        logger.error("Caspio API credentials are not properly configured. Please check your .env file.")
        sys.exit(1)
    
    # Test the connection by getting a list of tables
    url = f"{CASPIO_BASE_URL}/rest/v2/tables"
    headers = {
        'Authorization': f'Bearer {CASPIO_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        tables = response.json().get('Result', [])
        logger.info(f"Successfully connected to Caspio API. Found {len(tables)} tables.")
        
        # Print the table names
        logger.info("\nAvailable tables:")
        for table in tables:
            logger.info(f"- {table}")
        
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to Caspio API: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return False

def test_sanmar_bulk_table():
    """Test access to the Sanmar_Bulk_251816_Feb2024 table."""
    if not CASPIO_BASE_URL or not CASPIO_ACCESS_TOKEN:
        logger.error("Caspio API credentials are not properly configured. Please check your .env file.")
        sys.exit(1)
    
    # Test access to the Sanmar_Bulk_251816_Feb2024 table
    url = f"{CASPIO_BASE_URL}/rest/v2/tables/Sanmar_Bulk_251816_Feb2024/records?q.limit=1"
    headers = {
        'Authorization': f'Bearer {CASPIO_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        result = response.json().get('Result', [])
        if result:
            logger.info(f"Successfully accessed the Sanmar_Bulk_251816_Feb2024 table.")
            logger.info(f"Sample record: {json.dumps(result[0], indent=2)}")
        else:
            logger.warning("The Sanmar_Bulk_251816_Feb2024 table is empty.")
        
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error accessing the Sanmar_Bulk_251816_Feb2024 table: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return False

def main():
    """Main function to test the Caspio API connection."""
    logger.info("Starting Caspio API connection test...")
    
    # Test the connection to the Caspio API
    if not test_caspio_connection():
        logger.error("Failed to connect to the Caspio API.")
        sys.exit(1)
    
    # Test access to the Sanmar_Bulk_251816_Feb2024 table
    if not test_sanmar_bulk_table():
        logger.error("Failed to access the Sanmar_Bulk_251816_Feb2024 table.")
        sys.exit(1)
    
    logger.info("Caspio API connection test completed successfully.")

if __name__ == "__main__":
    main()