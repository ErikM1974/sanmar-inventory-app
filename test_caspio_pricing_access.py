#!/usr/bin/env python
"""
Script to test access to the Caspio Pricing table.
"""

import os
import logging
import requests
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_caspio_pricing_access.log"),
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

def test_pricing_table_access():
    """Test access to the Pricing table in Caspio."""
    logger.info("Testing access to the Pricing table...")
    
    access_token = get_access_token()
    if not access_token:
        logger.error("Failed to get access token.")
        return False
    
    # First, try to get the table structure
    endpoint = f"{CASPIO_BASE_URL}/rest/v2/tables/Pricing/fields"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        logger.info("Getting Pricing table structure...")
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        
        fields_data = response.json()
        if 'Result' in fields_data and isinstance(fields_data['Result'], list):
            fields = fields_data['Result']
            logger.info(f"Successfully retrieved {len(fields)} fields from Pricing table.")
            
            # Print field details
            logger.info("Fields in Pricing table:")
            for field in fields:
                read_only = field.get('ReadOnly', False)
                auto_increment = field.get('AutoIncrement', False)
                field_type = field.get('Type', 'Unknown')
                field_name = field.get('Name', 'Unknown')
                logger.info(f"- {field_name} ({field_type}): ReadOnly={read_only}, AutoIncrement={auto_increment}")
        else:
            logger.error(f"Unexpected response format: {fields_data}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting Pricing table structure: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return False
    
    # Next, try to get records from the table
    endpoint = f"{CASPIO_BASE_URL}/rest/v2/tables/Pricing/records"
    params = {
        'q.limit': 5  # Just get a few records for testing
    }
    
    try:
        logger.info("Getting records from Pricing table...")
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        
        records_data = response.json()
        if 'Result' in records_data and isinstance(records_data['Result'], list):
            records = records_data['Result']
            logger.info(f"Successfully retrieved {len(records)} records from Pricing table.")
            
            # Print record details
            if records:
                logger.info("Sample record from Pricing table:")
                for key, value in records[0].items():
                    logger.info(f"- {key}: {value}")
            else:
                logger.info("No records found in Pricing table.")
        else:
            logger.error(f"Unexpected response format: {records_data}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting records from Pricing table: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return False
    
    # Finally, try to insert a test record
    test_record = {
        'STYLE': 'TEST002',
        'COLOR_NAME': 'Test Color',
        'SIZE': 'M',
        'PIECE_PRICE': 19.99,
        'CASE_PRICE': 179.91,
        'CASE_SIZE': 10,
        'PROGRAM_PRICE': 17.99
    }
    
    try:
        logger.info("Inserting test record into Pricing table...")
        logger.info(f"Request URL: {endpoint}")
        logger.info(f"Request Headers: {headers}")
        logger.info(f"Request Body: {test_record}")
        
        # Try to make the request with debug information
        response = requests.post(endpoint, headers=headers, json=test_record)
        
        # Log the raw response
        logger.info(f"Response Status Code: {response.status_code}")
        logger.info(f"Response Headers: {response.headers}")
        logger.info(f"Response Content: {response.text}")
        
        # Raise for status after logging
        response.raise_for_status()
        
        logger.info("Successfully inserted test record into Pricing table.")
        
        # Try to parse the response as JSON
        try:
            insert_response = response.json()
            logger.info(f"Parsed JSON Response: {insert_response}")
        except ValueError as e:
            logger.error(f"Error parsing JSON response: {e}")
            insert_response = {}
        if 'InsertedRecords' in insert_response and len(insert_response['InsertedRecords']) > 0:
            record_id = insert_response['InsertedRecords'][0]
            logger.info(f"Inserted record ID: {record_id}")
            
            # Delete the test record
            delete_endpoint = f"{CASPIO_BASE_URL}/rest/v2/tables/Pricing/records/{record_id}"
            delete_response = requests.delete(delete_endpoint, headers=headers)
            delete_response.raise_for_status()
            logger.info("Successfully deleted test record from Pricing table.")
        
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error inserting test record into Pricing table: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return False

def main():
    """Main function to test access to the Caspio Pricing table."""
    logger.info("Starting Caspio Pricing table access test...")
    
    if test_pricing_table_access():
        logger.info("Caspio Pricing table access test completed successfully.")
    else:
        logger.error("Caspio Pricing table access test failed.")

if __name__ == "__main__":
    main()