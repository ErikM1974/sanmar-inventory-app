#!/usr/bin/env python
"""
Script to create Caspio tables for the SanMar Inventory App using the Caspio REST API.
"""

import os
import sys
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
        logging.FileHandler("caspio_table_creation.log"),
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

class CaspioAPI:
    """Class to interact with the Caspio API."""
    
    def __init__(self, base_url, client_id, client_secret):
        """Initialize the Caspio API client."""
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expiry = None
    
    def get_access_token(self):
        """Get an access token from the Caspio API."""
        # Check if we already have a valid token
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.access_token
        
        # Get a new token
        auth_url = f"{self.base_url}/oauth/token"
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        try:
            response = requests.post(auth_url, data=payload)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            return self.access_token
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting authentication token: {str(e)}")
            return None
    
    def make_api_request(self, endpoint, method="GET", data=None):
        """Make a request to the Caspio API."""
        # Ensure we don't have double slashes in the URL
        if self.base_url.endswith('/') and endpoint.startswith('/'):
            endpoint = endpoint[1:]
        elif not self.base_url.endswith('/') and not endpoint.startswith('/'):
            endpoint = f"/{endpoint}"
        
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.get_access_token()}',
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
            
            response.raise_for_status()
            
            if response.status_code == 204:  # No content
                return {}
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return None
    
    def get_tables(self):
        """Get a list of tables in the Caspio application."""
        return self.make_api_request("rest/v2/tables")
    
    def table_exists(self, table_name):
        """Check if a table exists in the Caspio application."""
        tables = self.get_tables()
        logger.info(f"Tables response: {tables}")
        
        if not tables:
            return False
        
        # Check if tables is a list or a dict with 'Result' key
        if isinstance(tables, dict) and 'Result' in tables:
            table_list = tables['Result']
        elif isinstance(tables, list):
            table_list = tables
        else:
            logger.error(f"Unexpected response format: {type(tables)}")
            return False
        
        for table in table_list:
            # Check if table is a string or a dict with 'Name' key
            if isinstance(table, dict) and 'Name' in table:
                if table['Name'].lower() == table_name.lower():
                    return True
            elif isinstance(table, str):
                if table.lower() == table_name.lower():
                    return True
        
        return False
    
    def create_table(self, table_definition):
        """Create a table in the Caspio application."""
        logger.info(f"Creating table with definition: {json.dumps(table_definition, indent=2)}")
        return self.make_api_request("rest/v2/tables", method="POST", data=table_definition)

def create_categories_table(caspio_api):
    """Create the Categories table in Caspio."""
    table_name = "Categories"
    
    # Check if table already exists
    if caspio_api.table_exists(table_name):
        logger.info(f"Table '{table_name}' already exists.")
        return True
    
    # Define the table structure
    table_definition = {
        "Name": table_name,
        "Columns": [
            {
                "Name": "CATEGORY_ID",
                "Type": "AutoNumber",
                "Unique": True,
                "UniqueAllowNulls": False,
                "Label": "Category ID",
                "Description": "Primary key for the category",
                "DisplayOrder": 1,
                "OnInsert": True,
                "OnUpdate": False
            },
            {
                "Name": "CATEGORY_NAME",
                "Type": "String",
                "Length": 100,
                "Unique": False,
                "UniqueAllowNulls": False,
                "Label": "Category Name",
                "Description": "Name of the category",
                "DisplayOrder": 2,
                "OnInsert": True,
                "OnUpdate": True,
                "Required": True
            },
            {
                "Name": "PARENT_CATEGORY_ID",
                "Type": "Number",
                "Unique": False,
                "UniqueAllowNulls": False,
                "Label": "Parent Category ID",
                "Description": "Foreign key to parent category (null for top-level categories)",
                "DisplayOrder": 3,
                "OnInsert": True,
                "OnUpdate": True,
                "Required": False
            },
            {
                "Name": "DISPLAY_ORDER",
                "Type": "Number",
                "Unique": False,
                "UniqueAllowNulls": False,
                "Label": "Display Order",
                "Description": "Order to display categories",
                "DisplayOrder": 4,
                "OnInsert": True,
                "OnUpdate": True,
                "Required": False
            }
        ]
    }
    
    # Create the table
    result = caspio_api.create_table(table_definition)
    if result:
        logger.info(f"Successfully created table '{table_name}'.")
        return True
    else:
        logger.error(f"Failed to create table '{table_name}'.")
        return False

def create_products_table(caspio_api):
    """Create the Products table in Caspio."""
    table_name = "Products"
    
    # Check if table already exists
    if caspio_api.table_exists(table_name):
        logger.info(f"Table '{table_name}' already exists.")
        return True
    
    # Define the table structure
    table_definition = {
        "Name": table_name,
        "Columns": [
            {
                "Name": "PRODUCT_ID",
                "Type": "AutoNumber",
                "Unique": True,
                "UniqueAllowNulls": False,
                "Label": "Product ID",
                "Description": "Primary key for the product",
                "DisplayOrder": 1,
                "OnInsert": True,
                "OnUpdate": False
            },
            {
                "Name": "STYLE",
                "Type": "String",
                "Length": 50,
                "Unique": False,
                "UniqueAllowNulls": False,
                "Label": "Style",
                "Description": "SanMar style number",
                "DisplayOrder": 2,
                "OnInsert": True,
                "OnUpdate": True,
                "Required": True
            },
            {
                "Name": "PRODUCT_TITLE",
                "Type": "String",
                "Length": 255,
                "Unique": False,
                "UniqueAllowNulls": False,
                "Label": "Product Title",
                "Description": "Product title",
                "DisplayOrder": 3,
                "OnInsert": True,
                "OnUpdate": True,
                "Required": True
            },
            {
                "Name": "CATEGORY_NAME",
                "Type": "String",
                "Length": 100,
                "Unique": False,
                "UniqueAllowNulls": False,
                "Label": "Category Name",
                "Description": "Category name",
                "DisplayOrder": 4,
                "OnInsert": True,
                "OnUpdate": True,
                "Required": True
            },
            {
                "Name": "COLOR_NAME",
                "Type": "String",
                "Length": 100,
                "Unique": False,
                "UniqueAllowNulls": False,
                "Label": "Color Name",
                "Description": "Color name",
                "DisplayOrder": 5,
                "OnInsert": True,
                "OnUpdate": True,
                "Required": True
            },
            {
                "Name": "SIZE",
                "Type": "String",
                "Length": 20,
                "Unique": False,
                "UniqueAllowNulls": False,
                "Label": "Size",
                "Description": "Size name",
                "DisplayOrder": 6,
                "OnInsert": True,
                "OnUpdate": True,
                "Required": True
            },
            {
                "Name": "SIZE_INDEX",
                "Type": "Number",
                "Unique": False,
                "UniqueAllowNulls": False,
                "Label": "Size Index",
                "Description": "Order to display sizes",
                "DisplayOrder": 7,
                "OnInsert": True,
                "OnUpdate": True,
                "Required": False
            },
            {
                "Name": "BRAND_NAME",
                "Type": "String",
                "Length": 100,
                "Unique": False,
                "UniqueAllowNulls": False,
                "Label": "Brand Name",
                "Description": "Brand name",
                "DisplayOrder": 8,
                "OnInsert": True,
                "OnUpdate": True,
                "Required": False
            },
            {
                "Name": "BRAND_LOGO_IMAGE",
                "Type": "String",
                "Length": 255,
                "Unique": False,
                "UniqueAllowNulls": False,
                "Label": "Brand Logo Image",
                "Description": "URL to brand logo image",
                "DisplayOrder": 9,
                "OnInsert": True,
                "OnUpdate": True,
                "Required": False
            },
            {
                "Name": "PRODUCT_IMAGE_URL",
                "Type": "String",
                "Length": 255,
                "Unique": False,
                "UniqueAllowNulls": False,
                "Label": "Product Image URL",
                "Description": "URL to product image",
                "DisplayOrder": 10,
                "OnInsert": True,
                "OnUpdate": True,
                "Required": False
            },
            {
                "Name": "COLOR_SQUARE_IMAGE",
                "Type": "String",
                "Length": 255,
                "Unique": False,
                "UniqueAllowNulls": False,
                "Label": "Color Square Image",
                "Description": "URL to color swatch image",
                "DisplayOrder": 11,
                "OnInsert": True,
                "OnUpdate": True,
                "Required": False
            },
            {
                "Name": "PRICE",
                "Type": "Currency",
                "Unique": False,
                "UniqueAllowNulls": False,
                "Label": "Price",
                "Description": "Regular price",
                "DisplayOrder": 12,
                "OnInsert": True,
                "OnUpdate": True,
                "Required": False
            },
            {
                "Name": "PIECE_PRICE",
                "Type": "Currency",
                "Unique": False,
                "UniqueAllowNulls": False,
                "Label": "Piece Price",
                "Description": "Price per piece",
                "DisplayOrder": 13,
                "OnInsert": True,
                "OnUpdate": True,
                "Required": False
            },
            {
                "Name": "CASE_PRICE",
                "Type": "Currency",
                "Unique": False,
                "UniqueAllowNulls": False,
                "Label": "Case Price",
                "Description": "Price per case",
                "DisplayOrder": 14,
                "OnInsert": True,
                "OnUpdate": True,
                "Required": False
            },
            {
                "Name": "CASE_SIZE",
                "Type": "Number",
                "Unique": False,
                "UniqueAllowNulls": False,
                "Label": "Case Size",
                "Description": "Number of pieces in a case",
                "DisplayOrder": 15,
                "OnInsert": True,
                "OnUpdate": True,
                "Required": False
            },
            {
                "Name": "KEYWORDS",
                "Type": "String",
                "Length": 255,
                "Unique": False,
                "UniqueAllowNulls": False,
                "Label": "Keywords",
                "Description": "Keywords for search",
                "DisplayOrder": 16,
                "OnInsert": True,
                "OnUpdate": True,
                "Required": False
            }
        ]
    }
    
    # Create the table
    try:
        result = caspio_api.create_table(table_definition)
        if result:
            logger.info(f"Successfully created table '{table_name}'.")
            return True
        else:
            logger.error(f"Failed to create table '{table_name}'. No error message returned.")
            return False
    except Exception as e:
        logger.error(f"Exception creating table '{table_name}': {str(e)}")
        return False
def create_inventory_table(caspio_api):
    """Create the Inventory table in Caspio."""
    table_name = "Inventory"
    
    # Check if table already exists
    if caspio_api.table_exists(table_name):
        logger.info(f"Table '{table_name}' already exists.")
        return True
    
    # Define the table structure based on the Products table structure
    table_definition = {
        "Name": table_name,
        "Columns": [
            {
                "Name": "INVENTORY_ID",
                "Type": "AutoNumber",
                "Unique": True,
                "UniqueAllowNulls": False,
                "Label": "Inventory ID",
                "Description": "Primary key for inventory record",
                "DisplayOrder": 1,
                "OnInsert": True,
                "OnUpdate": False
            },
            {
                "Name": "STYLE",
                "Type": "String",
                "Length": 255,
                "Unique": False,
                "UniqueAllowNulls": False,
                "Label": "Style",
                "Description": "SanMar style number",
                "DisplayOrder": 2,
                "OnInsert": True,
                "OnUpdate": True,
                "Required": True
            },
            {
                "Name": "COLOR_NAME",
                "Type": "String",
                "Length": 255,
                "Unique": False,
                "UniqueAllowNulls": False,
                "Label": "Color Name",
                "Description": "Color name",
                "DisplayOrder": 3,
                "OnInsert": True,
                "OnUpdate": True,
                "Required": True
            },
            {
                "Name": "SIZE",
                "Type": "String",
                "Length": 255,
                "Unique": False,
                "UniqueAllowNulls": False,
                "Label": "Size",
                "Description": "Size name",
                "DisplayOrder": 4,
                "OnInsert": True,
                "OnUpdate": True,
                "Required": True
            },
            {
                "Name": "WAREHOUSE_ID",
                "Type": "String",
                "Length": 255,
                "Unique": False,
                "UniqueAllowNulls": False,
                "Label": "Warehouse ID",
                "Description": "Warehouse ID",
                "DisplayOrder": 5,
                "OnInsert": True,
                "OnUpdate": True,
                "Required": True
            },
            {
                "Name": "QUANTITY",
                "Type": "Number",
                "Unique": False,
                "UniqueAllowNulls": False,
                "Label": "Quantity",
                "Description": "Quantity available",
                "DisplayOrder": 6,
                "OnInsert": True,
                "OnUpdate": True,
                "Required": True
            },
            {
                "Name": "LAST_UPDATED",
                "Type": "DateTime",
                "Unique": False,
                "UniqueAllowNulls": False,
                "Label": "Last Updated",
                "Description": "Last update timestamp",
                "DisplayOrder": 7,
                "OnInsert": True,
                "OnUpdate": True,
                "Required": True
            }
        ]
    }
    
    # Create the table
    try:
        result = caspio_api.create_table(table_definition)
        if result:
            logger.info(f"Successfully created table '{table_name}'.")
            return True
        else:
            logger.error(f"Failed to create table '{table_name}'. No error message returned.")
            return False
    except Exception as e:
        logger.error(f"Exception creating table '{table_name}': {str(e)}")
        return False
        return False

def create_indexes(caspio_api):
    """Create indexes on the tables for better performance."""
    logger.info("Creating indexes on tables...")
    
    # Create index on Products table
    products_index = {
        "Name": "IDX_PRODUCTS_STYLE_COLOR_SIZE",
        "Fields": ["STYLE", "COLOR_NAME", "SIZE"],
        "Unique": True
    }
    
    result = caspio_api.make_api_request(
        "rest/v2/tables/Products/indexes",
        method="POST",
        data=products_index
    )
    
    if result:
        logger.info("Successfully created index on Products table.")
    else:
        logger.error("Failed to create index on Products table.")
    
    # Create index on Inventory table
    inventory_index = {
        "Name": "IDX_INVENTORY_STYLE_COLOR_SIZE_WAREHOUSE",
        "Fields": ["STYLE", "COLOR_NAME", "SIZE", "WAREHOUSE_ID"],
        "Unique": True
    }
    
    result = caspio_api.make_api_request(
        "rest/v2/tables/Inventory/indexes",
        method="POST",
        data=inventory_index
    )
    
    if result:
        logger.info("Successfully created index on Inventory table.")
    else:
        logger.error("Failed to create index on Inventory table.")
    
    # Create index on Categories table
    categories_index = {
        "Name": "IDX_CATEGORIES_NAME",
        "Fields": ["CATEGORY_NAME"],
        "Unique": True
    }
    
    result = caspio_api.make_api_request(
        "rest/v2/tables/Categories/indexes",
        method="POST",
        data=categories_index
    )
    
    if result:
        logger.info("Successfully created index on Categories table.")
    else:
        logger.error("Failed to create index on Categories table.")
    
    return True

def main():
    """Main function to create Caspio tables."""
    logger.info("Starting Caspio table creation...")
    
    # Check if Caspio API is properly configured
    if not CASPIO_BASE_URL or not CASPIO_CLIENT_ID or not CASPIO_CLIENT_SECRET:
        logger.error("Caspio API is not properly configured. Please check your .env file.")
        sys.exit(1)
    
    # Initialize Caspio API client
    caspio_api = CaspioAPI(CASPIO_BASE_URL, CASPIO_CLIENT_ID, CASPIO_CLIENT_SECRET)
    
    # Test Caspio API connection
    logger.info("Testing Caspio API connection...")
    token = caspio_api.get_access_token()
    if not token:
        logger.error("Failed to connect to Caspio API. Please check your credentials.")
        sys.exit(1)
    
    logger.info("Successfully connected to Caspio API.")
    
    # Create tables
    categories_success = create_categories_table(caspio_api)
    products_success = create_products_table(caspio_api)
    inventory_success = create_inventory_table(caspio_api)
    
    if categories_success and products_success and inventory_success:
        logger.info("Successfully created all tables.")
        
        # Create indexes
        if create_indexes(caspio_api):
            logger.info("Successfully created indexes.")
        else:
            logger.warning("Failed to create indexes.")
    else:
        logger.error("Failed to create all tables.")
    
    logger.info("Caspio table creation completed.")

if __name__ == "__main__":
    main()