#!/usr/bin/env python
"""
Script to set up Caspio tables for the SanMar Inventory App.
"""

import logging
import os
import sys
import time
from caspio_client import caspio_api

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("caspio_setup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_table_exists(table_name):
    """Check if a table exists in Caspio"""
    logger.info(f"Checking if table '{table_name}' exists...")
    
    try:
        endpoint = "rest/v2/tables"
        response = caspio_api._make_api_request(endpoint, "GET")
        
        if response and 'Result' in response:
            for table in response['Result']:
                if table['Name'].lower() == table_name.lower():
                    logger.info(f"Table '{table_name}' already exists.")
                    return True
        
        logger.info(f"Table '{table_name}' does not exist.")
        return False
    except Exception as e:
        logger.error(f"Error checking if table '{table_name}' exists: {str(e)}")
        return False

def create_table(table_name, fields):
    """Create a table in Caspio"""
    logger.info(f"Creating table '{table_name}'...")
    
    try:
        endpoint = "rest/v2/tables"
        data = {
            "Name": table_name,
            "Fields": fields
        }
        
        response = caspio_api._make_api_request(endpoint, "POST", data=data)
        
        if response:
            logger.info(f"Successfully created table '{table_name}'.")
            return True
        else:
            logger.error(f"Failed to create table '{table_name}'.")
            return False
    except Exception as e:
        logger.error(f"Error creating table '{table_name}': {str(e)}")
        return False

def setup_products_table():
    """Set up the Products table in Caspio"""
    table_name = "Products"
    
    # Check if table exists
    if check_table_exists(table_name):
        return True
    
    # Define fields for Products table
    fields = [
        {
            "Name": "STYLE",
            "Type": "String",
            "Length": 50,
            "Required": True
        },
        {
            "Name": "PRODUCT_TITLE",
            "Type": "String",
            "Length": 255,
            "Required": True
        },
        {
            "Name": "CATEGORY_NAME",
            "Type": "String",
            "Length": 100,
            "Required": True
        },
        {
            "Name": "COLOR_NAME",
            "Type": "String",
            "Length": 50,
            "Required": True
        },
        {
            "Name": "SIZE",
            "Type": "String",
            "Length": 20,
            "Required": True
        },
        {
            "Name": "SIZE_INDEX",
            "Type": "Integer",
            "Required": False
        },
        {
            "Name": "PRICE",
            "Type": "Decimal",
            "Required": False
        },
        {
            "Name": "BRAND_NAME",
            "Type": "String",
            "Length": 100,
            "Required": False
        },
        {
            "Name": "BRAND_LOGO_IMAGE",
            "Type": "String",
            "Length": 255,
            "Required": False
        },
        {
            "Name": "PRODUCT_IMAGE_URL",
            "Type": "String",
            "Length": 255,
            "Required": False
        },
        {
            "Name": "COLOR_SQUARE_IMAGE",
            "Type": "String",
            "Length": 255,
            "Required": False
        },
        {
            "Name": "KEYWORDS",
            "Type": "String",
            "Length": 500,
            "Required": False
        },
        {
            "Name": "PIECE_PRICE",
            "Type": "Decimal",
            "Required": False
        },
        {
            "Name": "CASE_PRICE",
            "Type": "Decimal",
            "Required": False
        },
        {
            "Name": "CASE_SIZE",
            "Type": "Integer",
            "Required": False
        }
    ]
    
    # Create table
    return create_table(table_name, fields)

def setup_inventory_table():
    """Set up the Inventory table in Caspio"""
    table_name = "Inventory"
    
    # Check if table exists
    if check_table_exists(table_name):
        return True
    
    # Define fields for Inventory table
    fields = [
        {
            "Name": "INVENTORY_ID",
            "Type": "AutoNumber",
            "Required": True
        },
        {
            "Name": "STYLE",
            "Type": "String",
            "Length": 50,
            "Required": True
        },
        {
            "Name": "COLOR_NAME",
            "Type": "String",
            "Length": 50,
            "Required": True
        },
        {
            "Name": "SIZE",
            "Type": "String",
            "Length": 20,
            "Required": True
        },
        {
            "Name": "WAREHOUSE_ID",
            "Type": "String",
            "Length": 20,
            "Required": True
        },
        {
            "Name": "QUANTITY",
            "Type": "Integer",
            "Required": True
        },
        {
            "Name": "LAST_UPDATED",
            "Type": "DateTime",
            "Required": True
        }
    ]
    
    # Create table
    return create_table(table_name, fields)

def setup_categories_table():
    """Set up the Categories table in Caspio"""
    table_name = "Categories"
    
    # Check if table exists
    if check_table_exists(table_name):
        return True
    
    # Define fields for Categories table
    fields = [
        {
            "Name": "CATEGORY_ID",
            "Type": "AutoNumber",
            "Required": True
        },
        {
            "Name": "CATEGORY_NAME",
            "Type": "String",
            "Length": 100,
            "Required": True
        },
        {
            "Name": "PARENT_CATEGORY_ID",
            "Type": "Integer",
            "Required": False
        },
        {
            "Name": "DISPLAY_ORDER",
            "Type": "Integer",
            "Required": False
        }
    ]
    
    # Create table
    return create_table(table_name, fields)

def create_indexes():
    """Create indexes on the tables for better performance"""
    logger.info("Creating indexes on tables...")
    
    try:
        # Create index on Products table
        endpoint = "rest/v2/tables/Products/indexes"
        data = {
            "Name": "IDX_PRODUCTS_STYLE_COLOR_SIZE",
            "Fields": ["STYLE", "COLOR_NAME", "SIZE"],
            "Unique": True
        }
        
        response = caspio_api._make_api_request(endpoint, "POST", data=data)
        
        if response:
            logger.info("Successfully created index on Products table.")
        else:
            logger.error("Failed to create index on Products table.")
        
        # Create index on Inventory table
        endpoint = "rest/v2/tables/Inventory/indexes"
        data = {
            "Name": "IDX_INVENTORY_STYLE_COLOR_SIZE_WAREHOUSE",
            "Fields": ["STYLE", "COLOR_NAME", "SIZE", "WAREHOUSE_ID"],
            "Unique": True
        }
        
        response = caspio_api._make_api_request(endpoint, "POST", data=data)
        
        if response:
            logger.info("Successfully created index on Inventory table.")
        else:
            logger.error("Failed to create index on Inventory table.")
        
        # Create index on Categories table
        endpoint = "rest/v2/tables/Categories/indexes"
        data = {
            "Name": "IDX_CATEGORIES_NAME",
            "Fields": ["CATEGORY_NAME"],
            "Unique": True
        }
        
        response = caspio_api._make_api_request(endpoint, "POST", data=data)
        
        if response:
            logger.info("Successfully created index on Categories table.")
        else:
            logger.error("Failed to create index on Categories table.")
        
        return True
    except Exception as e:
        logger.error(f"Error creating indexes: {str(e)}")
        return False

def main():
    """Main function to set up Caspio tables"""
    logger.info("Starting Caspio table setup...")
    
    # Check if Caspio API is properly configured
    if not caspio_api.client_id or not caspio_api.client_secret:
        logger.error("Caspio API is not properly configured. Please check your .env file.")
        sys.exit(1)
    
    # Test Caspio API connection
    logger.info("Testing Caspio API connection...")
    test_response = caspio_api._get_access_token()
    if not test_response:
        logger.error("Failed to connect to Caspio API. Please check your credentials.")
        sys.exit(1)
    
    logger.info("Successfully connected to Caspio API.")
    
    # Set up tables
    products_success = setup_products_table()
    inventory_success = setup_inventory_table()
    categories_success = setup_categories_table()
    
    if products_success and inventory_success and categories_success:
        logger.info("Successfully set up all tables.")
        
        # Create indexes
        if create_indexes():
            logger.info("Successfully created indexes.")
        else:
            logger.warning("Failed to create indexes.")
    else:
        logger.error("Failed to set up all tables.")
    
    logger.info("Caspio table setup completed.")

if __name__ == "__main__":
    main()