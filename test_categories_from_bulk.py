#!/usr/bin/env python
"""
Script to test extracting category and subcategory information directly from the Sanmar_Bulk_251816_Feb2024 table.
This script verifies that separate tables for categories and subcategories are not needed.
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_categories_from_bulk.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import Caspio client
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from caspio_client import CaspioClient
except ImportError:
    logger.error("Failed to import CaspioClient. Make sure caspio_client.py is in the same directory.")
    sys.exit(1)

# Caspio API credentials
CASPIO_BASE_URL = os.getenv('CASPIO_BASE_URL')
CASPIO_ACCESS_TOKEN = os.getenv('CASPIO_ACCESS_TOKEN')
CASPIO_REFRESH_TOKEN = os.getenv('CASPIO_REFRESH_TOKEN')
CASPIO_CLIENT_ID = os.getenv('CASPIO_CLIENT_ID')
CASPIO_CLIENT_SECRET = os.getenv('CASPIO_CLIENT_SECRET')

def get_caspio_client():
    """Initialize and return a Caspio client."""
    if CASPIO_ACCESS_TOKEN:
        return CaspioClient(
            base_url=CASPIO_BASE_URL,
            access_token=CASPIO_ACCESS_TOKEN,
            refresh_token=CASPIO_REFRESH_TOKEN
        )
    elif CASPIO_CLIENT_ID and CASPIO_CLIENT_SECRET:
        return CaspioClient(
            base_url=CASPIO_BASE_URL,
            client_id=CASPIO_CLIENT_ID,
            client_secret=CASPIO_CLIENT_SECRET
        )
    else:
        logger.error("Caspio API credentials are not properly configured. Please check your .env file.")
        return None

def test_get_categories():
    """Test getting distinct categories from the Sanmar_Bulk_251816_Feb2024 table."""
    logger.info("Testing getting distinct categories from Sanmar_Bulk_251816_Feb2024 table...")
    
    caspio_client = get_caspio_client()
    if not caspio_client:
        return False
    
    try:
        # Query distinct categories
        endpoint = "rest/v2/tables/Sanmar_Bulk_251816_Feb2024/records"
        params = {
            'q.select': 'CATEGORY_NAME',
            'q.distinct': 'true',
            'q.sort': 'CATEGORY_NAME'
        }
        
        response = caspio_client.make_api_request(endpoint, params=params)
        
        if not response or 'Result' not in response:
            logger.error("Failed to get categories from Sanmar_Bulk_251816_Feb2024 table.")
            return False
        
        categories = [item['CATEGORY_NAME'] for item in response['Result']]
        
        logger.info(f"Successfully retrieved {len(categories)} distinct categories from Sanmar_Bulk_251816_Feb2024 table.")
        logger.info(f"Categories: {', '.join(categories)}")
        
        return True
    except Exception as e:
        logger.error(f"Error getting categories from Sanmar_Bulk_251816_Feb2024 table: {str(e)}")
        return False

def test_get_subcategories_for_category(category_name):
    """Test getting distinct subcategories for a specific category from the Sanmar_Bulk_251816_Feb2024 table."""
    logger.info(f"Testing getting distinct subcategories for category '{category_name}' from Sanmar_Bulk_251816_Feb2024 table...")
    
    caspio_client = get_caspio_client()
    if not caspio_client:
        return False
    
    try:
        # Query distinct subcategories for the specified category
        endpoint = "rest/v2/tables/Sanmar_Bulk_251816_Feb2024/records"
        params = {
            'q.select': 'SUBCATEGORY_NAME',
            'q.where': f"CATEGORY_NAME='{category_name}'",
            'q.distinct': 'true',
            'q.sort': 'SUBCATEGORY_NAME'
        }
        
        response = caspio_client.make_api_request(endpoint, params=params)
        
        if not response or 'Result' not in response:
            logger.error(f"Failed to get subcategories for category '{category_name}' from Sanmar_Bulk_251816_Feb2024 table.")
            return False
        
        subcategories = [item['SUBCATEGORY_NAME'] for item in response['Result']]
        
        logger.info(f"Successfully retrieved {len(subcategories)} distinct subcategories for category '{category_name}' from Sanmar_Bulk_251816_Feb2024 table.")
        logger.info(f"Subcategories: {', '.join(subcategories)}")
        
        return True
    except Exception as e:
        logger.error(f"Error getting subcategories for category '{category_name}' from Sanmar_Bulk_251816_Feb2024 table: {str(e)}")
        return False

def test_get_products_for_category_and_subcategory(category_name, subcategory_name):
    """Test getting products for a specific category and subcategory from the Sanmar_Bulk_251816_Feb2024 table."""
    logger.info(f"Testing getting products for category '{category_name}' and subcategory '{subcategory_name}' from Sanmar_Bulk_251816_Feb2024 table...")
    
    caspio_client = get_caspio_client()
    if not caspio_client:
        return False
    
    try:
        # Query products for the specified category and subcategory
        endpoint = "rest/v2/tables/Sanmar_Bulk_251816_Feb2024/records"
        params = {
            'q.select': 'STYLE,PRODUCT_TITLE,BRAND_NAME',
            'q.where': f"CATEGORY_NAME='{category_name}' AND SUBCATEGORY_NAME='{subcategory_name}'",
            'q.distinct': 'true',
            'q.sort': 'PRODUCT_TITLE',
            'q.limit': 10
        }
        
        response = caspio_client.make_api_request(endpoint, params=params)
        
        if not response or 'Result' not in response:
            logger.error(f"Failed to get products for category '{category_name}' and subcategory '{subcategory_name}' from Sanmar_Bulk_251816_Feb2024 table.")
            return False
        
        products = response['Result']
        
        logger.info(f"Successfully retrieved {len(products)} products for category '{category_name}' and subcategory '{subcategory_name}' from Sanmar_Bulk_251816_Feb2024 table.")
        
        # Print the first few products
        for i, product in enumerate(products[:5]):
            logger.info(f"Product {i+1}: {product['PRODUCT_TITLE']} (Style: {product['STYLE']}, Brand: {product['BRAND_NAME']})")
        
        return True
    except Exception as e:
        logger.error(f"Error getting products for category '{category_name}' and subcategory '{subcategory_name}' from Sanmar_Bulk_251816_Feb2024 table: {str(e)}")
        return False

def main():
    """Main function."""
    logger.info("Starting test to extract category and subcategory information from Sanmar_Bulk_251816_Feb2024 table...")
    
    # Test 1: Get distinct categories
    if not test_get_categories():
        logger.error("Failed to get categories from Sanmar_Bulk_251816_Feb2024 table.")
        print("\n❌ ERROR: Could not get categories from Sanmar_Bulk_251816_Feb2024 table. Check the logs for details.")
        sys.exit(1)
    
    # Get a sample category for further testing
    caspio_client = get_caspio_client()
    if not caspio_client:
        sys.exit(1)
    
    try:
        endpoint = "rest/v2/tables/Sanmar_Bulk_251816_Feb2024/records"
        params = {
            'q.select': 'CATEGORY_NAME',
            'q.distinct': 'true',
            'q.limit': 1
        }
        
        response = caspio_client.make_api_request(endpoint, params=params)
        
        if not response or 'Result' not in response or not response['Result']:
            logger.error("Failed to get a sample category from Sanmar_Bulk_251816_Feb2024 table.")
            print("\n❌ ERROR: Could not get a sample category from Sanmar_Bulk_251816_Feb2024 table. Check the logs for details.")
            sys.exit(1)
        
        sample_category = response['Result'][0]['CATEGORY_NAME']
        
        # Test 2: Get subcategories for the sample category
        if not test_get_subcategories_for_category(sample_category):
            logger.error(f"Failed to get subcategories for category '{sample_category}' from Sanmar_Bulk_251816_Feb2024 table.")
            print(f"\n❌ ERROR: Could not get subcategories for category '{sample_category}' from Sanmar_Bulk_251816_Feb2024 table. Check the logs for details.")
            sys.exit(1)
        
        # Get a sample subcategory for further testing
        params = {
            'q.select': 'SUBCATEGORY_NAME',
            'q.where': f"CATEGORY_NAME='{sample_category}'",
            'q.distinct': 'true',
            'q.limit': 1
        }
        
        response = caspio_client.make_api_request(endpoint, params=params)
        
        if not response or 'Result' not in response or not response['Result']:
            logger.error(f"Failed to get a sample subcategory for category '{sample_category}' from Sanmar_Bulk_251816_Feb2024 table.")
            print(f"\n❌ ERROR: Could not get a sample subcategory for category '{sample_category}' from Sanmar_Bulk_251816_Feb2024 table. Check the logs for details.")
            sys.exit(1)
        
        sample_subcategory = response['Result'][0]['SUBCATEGORY_NAME']
        
        # Test 3: Get products for the sample category and subcategory
        if not test_get_products_for_category_and_subcategory(sample_category, sample_subcategory):
            logger.error(f"Failed to get products for category '{sample_category}' and subcategory '{sample_subcategory}' from Sanmar_Bulk_251816_Feb2024 table.")
            print(f"\n❌ ERROR: Could not get products for category '{sample_category}' and subcategory '{sample_subcategory}' from Sanmar_Bulk_251816_Feb2024 table. Check the logs for details.")
            sys.exit(1)
        
        logger.info("All tests completed successfully.")
        print("\n✅ SUCCESS: Successfully extracted category and subcategory information from Sanmar_Bulk_251816_Feb2024 table.")
        print("\n🔍 CONCLUSION: Separate tables for categories and subcategories are NOT needed as this information can be directly queried from the Sanmar_Bulk_251816_Feb2024 table.")
        
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        print(f"\n❌ ERROR: An error occurred in the main function: {str(e)}. Check the logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()