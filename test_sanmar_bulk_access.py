#!/usr/bin/env python
"""
Script to test access to the Sanmar_Bulk_251816_Feb2024 table in Caspio.
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
        logging.FileHandler("test_sanmar_bulk_access.log"),
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

def test_sanmar_bulk_access():
    """Test access to the Sanmar_Bulk_251816_Feb2024 table."""
    logger.info("Testing access to Sanmar_Bulk_251816_Feb2024 table...")
    
    # Initialize Caspio client
    caspio_client = None
    if CASPIO_ACCESS_TOKEN:
        caspio_client = CaspioClient(
            base_url=CASPIO_BASE_URL,
            access_token=CASPIO_ACCESS_TOKEN,
            refresh_token=CASPIO_REFRESH_TOKEN
        )
    elif CASPIO_CLIENT_ID and CASPIO_CLIENT_SECRET:
        caspio_client = CaspioClient(
            base_url=CASPIO_BASE_URL,
            client_id=CASPIO_CLIENT_ID,
            client_secret=CASPIO_CLIENT_SECRET
        )
    else:
        logger.error("Caspio API credentials are not properly configured. Please check your .env file.")
        return False
    
    try:
        # Test 1: Check if the table exists
        logger.info("Checking if Sanmar_Bulk_251816_Feb2024 table exists...")
        tables = caspio_client.get_tables()
        if 'Sanmar_Bulk_251816_Feb2024' not in tables:
            logger.error("Sanmar_Bulk_251816_Feb2024 table not found in Caspio.")
            return False
        
        logger.info("Sanmar_Bulk_251816_Feb2024 table exists.")
        
        # Test 2: Get table fields
        logger.info("Getting fields for Sanmar_Bulk_251816_Feb2024 table...")
        fields = caspio_client.get_table_fields('Sanmar_Bulk_251816_Feb2024')
        logger.info(f"Found {len(fields)} fields in Sanmar_Bulk_251816_Feb2024 table.")
        
        # Print the first 10 fields
        for i, field in enumerate(fields[:10]):
            logger.info(f"Field {i+1}: {field.get('Name')} ({field.get('Type')})")
        
        # Test 3: Query records
        logger.info("Querying records from Sanmar_Bulk_251816_Feb2024 table...")
        records = caspio_client.query_records('Sanmar_Bulk_251816_Feb2024', limit=5)
        
        if not records:
            logger.warning("No records found in Sanmar_Bulk_251816_Feb2024 table.")
        else:
            logger.info(f"Successfully retrieved {len(records)} records from Sanmar_Bulk_251816_Feb2024 table.")
            
            # Print the first record
            logger.info("First record:")
            logger.info(json.dumps(records[0], indent=2))
            
            # Check for key fields
            required_fields = ['STYLE', 'PRODUCT_TITLE', 'CATEGORY_NAME', 'COLOR_NAME', 'SIZE']
            missing_fields = [field for field in required_fields if field not in records[0]]
            
            if missing_fields:
                logger.warning(f"Missing required fields in records: {', '.join(missing_fields)}")
            else:
                logger.info("All required fields are present in the records.")
        
        # Test 4: Test a specific query
        logger.info("Testing a specific query on Sanmar_Bulk_251816_Feb2024 table...")
        category_query = caspio_client.query_records(
            'Sanmar_Bulk_251816_Feb2024',
            fields=['CATEGORY_NAME'],
            limit=100,
            order_by='CATEGORY_NAME'
        )
        
        if not category_query:
            logger.warning("No categories found in Sanmar_Bulk_251816_Feb2024 table.")
        else:
            categories = set(record.get('CATEGORY_NAME', '') for record in category_query)
            logger.info(f"Found {len(categories)} unique categories in Sanmar_Bulk_251816_Feb2024 table.")
            logger.info(f"Categories: {', '.join(sorted(list(categories)[:10]))}...")
        
        logger.info("All tests completed successfully.")
        return True
    except Exception as e:
        logger.error(f"Error testing access to Sanmar_Bulk_251816_Feb2024 table: {str(e)}")
        return False

def main():
    """Main function."""
    logger.info("Starting Sanmar_Bulk_251816_Feb2024 table access test...")
    
    if test_sanmar_bulk_access():
        logger.info("Successfully accessed Sanmar_Bulk_251816_Feb2024 table.")
        print("\n✅ SUCCESS: Sanmar_Bulk_251816_Feb2024 table is accessible.")
    else:
        logger.error("Failed to access Sanmar_Bulk_251816_Feb2024 table.")
        print("\n❌ ERROR: Could not access Sanmar_Bulk_251816_Feb2024 table. Check the logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()