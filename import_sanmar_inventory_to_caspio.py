#!/usr/bin/env python
"""
Script to import SanMar inventory data into Caspio.

This script:
1. Connects to the SanMar API to get inventory data
2. Processes the data
3. Inserts it into the Caspio Inventory table
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sanmar_to_caspio_import.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# SanMar API credentials
SANMAR_USERNAME = os.getenv('SANMAR_USERNAME')
SANMAR_PASSWORD = os.getenv('SANMAR_PASSWORD')

# Caspio API credentials
CASPIO_BASE_URL = os.getenv('CASPIO_BASE_URL', 'https://c3eku948.caspio.com')
CASPIO_ACCESS_TOKEN = os.getenv('CASPIO_ACCESS_TOKEN')
CASPIO_REFRESH_TOKEN = os.getenv('CASPIO_REFRESH_TOKEN')

class SanMarAPI:
    """Class to interact with the SanMar API."""
    
    def __init__(self, username, password):
        """Initialize the SanMar API client."""
        self.username = username
        self.password = password
        self.session = None
    
    def create_session(self):
        """Create a session with the SanMar API."""
        # This is a placeholder. In a real implementation, you would use the SanMar API
        # to create a session. The actual implementation depends on the SanMar API documentation.
        logger.info("Creating session with SanMar API...")
        self.session = "sample_session"
        return self.session
    
    def get_inventory(self, style=None, color=None, size=None):
        """Get inventory data from SanMar."""
        # This is a placeholder. In a real implementation, you would use the SanMar API
        # to get inventory data. The actual implementation depends on the SanMar API documentation.
        logger.info("Getting inventory data from SanMar API...")
        
        # Simulate API call with sample data
        inventory_data = []
        
        # Sample styles, colors, sizes, and warehouses
        styles = ["PC61", "K500", "L500", "DT5000"] if style is None else [style]
        colors = ["White", "Black", "Navy", "Red"] if color is None else [color]
        sizes = ["S", "M", "L", "XL", "2XL"] if size is None else [size]
        warehouses = ["1", "2", "3", "4", "5", "6", "7"]
        
        # Generate sample inventory data
        for style_code in styles:
            for color_name in colors:
                for size_name in sizes:
                    for warehouse_id in warehouses:
                        # Generate a random quantity between 0 and 200
                        quantity = int(hash(f"{style_code}{color_name}{size_name}{warehouse_id}") % 200)
                        
                        # Add to inventory data
                        inventory_data.append({
                            "STYLE": style_code,
                            "COLOR_NAME": color_name,
                            "SIZE": size_name,
                            "WAREHOUSE_ID": warehouse_id,
                            "QUANTITY": quantity,
                            "LAST_UPDATED": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
        
        return inventory_data

class CaspioAPI:
    """Class to interact with the Caspio API."""
    
    def __init__(self, base_url, access_token=None, refresh_token=None):
        """Initialize the Caspio API client."""
        self.base_url = base_url
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expiry = None
    
    def refresh_access_token(self):
        """Refresh the access token using the refresh token."""
        if not self.refresh_token:
            logger.error("No refresh token available.")
            return False
        
        auth_url = f"{self.base_url}/oauth/token"
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        
        try:
            response = requests.post(auth_url, data=payload)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')
            expires_in = token_data.get('expires_in', 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            logger.info("Successfully refreshed access token.")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error refreshing access token: {str(e)}")
            return False
    
    def make_api_request(self, endpoint, method="GET", data=None):
        """Make a request to the Caspio API."""
        # Ensure we don't have double slashes in the URL
        if self.base_url.endswith('/') and endpoint.startswith('/'):
            endpoint = endpoint[1:]
        elif not self.base_url.endswith('/') and not endpoint.startswith('/'):
            endpoint = f"/{endpoint}"
        
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None
            
            response.raise_for_status()
            
            if response.status_code == 204:  # No content
                return {}
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return None
    
    def insert_record(self, table_name, record_data):
        """Insert a record into a Caspio table."""
        endpoint = f"rest/v2/tables/{table_name}/records"
        return self.make_api_request(endpoint, method="POST", data=record_data)
    
    def insert_records(self, table_name, records_data):
        """Insert multiple records into a Caspio table."""
        endpoint = f"rest/v2/tables/{table_name}/records"
        return self.make_api_request(endpoint, method="POST", data=records_data)
    
    def delete_all_records(self, table_name):
        """Delete all records from a Caspio table."""
        endpoint = f"rest/v2/tables/{table_name}/records"
        return self.make_api_request(endpoint, method="DELETE")

def process_inventory_data(inventory_data):
    """Process inventory data for insertion into Caspio."""
    # In a real implementation, you might need to transform the data
    # to match the Caspio table structure. For this example, we'll
    # assume the data is already in the correct format.
    return inventory_data

def import_inventory_to_caspio(sanmar_api, caspio_api, batch_size=100):
    """Import SanMar inventory data into Caspio."""
    logger.info("Starting import of SanMar inventory data to Caspio...")
    
    # Create session with SanMar API
    sanmar_api.create_session()
    
    # Get inventory data from SanMar
    inventory_data = sanmar_api.get_inventory()
    logger.info(f"Retrieved {len(inventory_data)} inventory records from SanMar.")
    
    # Process inventory data
    processed_data = process_inventory_data(inventory_data)
    
    # Delete existing records (optional)
    # Uncomment the following line if you want to delete all existing records
    # caspio_api.delete_all_records("Inventory")
    
    # Insert records in batches
    total_records = len(processed_data)
    records_inserted = 0
    
    for i in range(0, total_records, batch_size):
        batch = processed_data[i:i+batch_size]
        result = caspio_api.insert_records("Inventory", batch)
        
        if result:
            records_inserted += len(batch)
            logger.info(f"Inserted batch {i//batch_size + 1} ({len(batch)} records).")
        else:
            logger.error(f"Failed to insert batch {i//batch_size + 1}.")
        
        # Sleep briefly to avoid overwhelming the API
        time.sleep(1)
    
    logger.info(f"Import completed. {records_inserted} out of {total_records} records inserted.")
    return records_inserted

def main():
    """Main function to import SanMar inventory data into Caspio."""
    logger.info("Starting SanMar to Caspio import...")
    
    # Check if SanMar API is properly configured
    if not SANMAR_USERNAME or not SANMAR_PASSWORD:
        logger.error("SanMar API is not properly configured. Please check your .env file.")
        sys.exit(1)
    
    # Check if Caspio API is properly configured
    if not CASPIO_BASE_URL or not CASPIO_ACCESS_TOKEN:
        logger.error("Caspio API is not properly configured. Please check your .env file.")
        sys.exit(1)
    
    # Initialize SanMar API client
    sanmar_api = SanMarAPI(SANMAR_USERNAME, SANMAR_PASSWORD)
    
    # Initialize Caspio API client
    caspio_api = CaspioAPI(CASPIO_BASE_URL, CASPIO_ACCESS_TOKEN, CASPIO_REFRESH_TOKEN)
    
    # Import inventory data
    import_inventory_to_caspio(sanmar_api, caspio_api)
    
    logger.info("SanMar to Caspio import completed.")

if __name__ == "__main__":
    main()