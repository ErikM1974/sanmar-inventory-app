"""
Test script to check the size formats from SanMar APIs for the L131 style 
to fix the XXL vs 2XL issue
"""

import logging
import os
import sys
from pprint import pprint
from zeep import Client
from zeep.plugins import HistoryPlugin
from zeep.helpers import serialize_object

# Add the current directory to the path to import local modules
sys.path.append('.')

# Import our color mapper and other necessary modules
from color_mapper import color_mapper
import sanmar_inventory
from middleware_client import create_session_with_retries

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_sanmar_credentials():
    """Get SanMar credentials from environment variables"""
    username = os.getenv('SANMAR_USERNAME', 'username')
    password = os.getenv('SANMAR_PASSWORD', 'password')
    return username, password

def test_product_info_sizes():
    """Test the size formats from the Product Info API"""
    logger.info("Testing size formats from Product Info API...")
    
    # Set up the SOAP client for Product Info API
    history = HistoryPlugin()
    
    try:
        # Create a session with retry capabilities
        session = create_session_with_retries()
        
        # Initialize the SOAP client
        client = Client(
            'https://ws.sanmar.com:8080/SanMarWebService/SanMarProductInfoServicePort?wsdl',
            plugins=[history],
            transport=session
        )
        
        # Get credentials
        username, password = get_sanmar_credentials()
        
        # Set up request data
        request_data = {
            'id': username,
            'password': password,
            'style': 'L131',  # The style from the screenshot
            'requestProductInfoList': None  # We want all product info
        }
        
        # Make the API call
        logger.info("Requesting product info for style L131...")
        response = client.service.getProductInfo(**request_data)
        
        # Convert to Python objects
        response_dict = serialize_object(response)
        
        # Extract and analyze size information
        if response_dict.get('errorOccured') == False:
            logger.info("API call successful")
            
            # Get the list response
            list_response = response_dict.get('listResponse', [])
            
            if list_response:
                logger.info(f"Found {len(list_response)} items in response")
                
                # Gather all sizes in the response
                sizes = set()
                for item in list_response:
                    basic_info = item.get('productBasicInfo', {})
                    size = basic_info.get('size')
                    if size:
                        sizes.add(size)
                
                logger.info(f"All sizes found in API response: {sorted(list(sizes))}")
                
                # Check if XXL is used versus 2XL
                if 'XXL' in sizes:
                    logger.info("NOTE: 'XXL' format is used in the Product Info API")
                if '2XL' in sizes:
                    logger.info("NOTE: '2XL' format is used in the Product Info API")
                
                # Find items with specific sizes
                xxl_items = [item for item in list_response 
                             if item.get('productBasicInfo', {}).get('size') == 'XXL']
                two_xl_items = [item for item in list_response 
                                if item.get('productBasicInfo', {}).get('size') == '2XL']
                
                logger.info(f"Found {len(xxl_items)} items with size 'XXL'")
                logger.info(f"Found {len(two_xl_items)} items with size '2XL'")
                
                # Show availability sizes text
                for i, item in enumerate(list_response[:5]):  # Just check first 5 items
                    avail_sizes = item.get('productBasicInfo', {}).get('availableSizes', '')
                    logger.info(f"Item {i} available sizes text: {avail_sizes}")
            else:
                logger.warning("No list response found in API response")
        else:
            logger.error(f"API call failed: {response_dict.get('message')}")
    
    except Exception as e:
        logger.error(f"Error testing Product Info API: {str(e)}")

def test_inventory_sizes():
    """Test the size formats from the Inventory API using sanmar_inventory module"""
    logger.info("Testing size formats from Inventory API...")
    
    try:
        # Use the sanmar_inventory module to get inventory data
        inventory_data = sanmar_inventory.get_inventory("L131")
        
        # Check if we got valid data
        if inventory_data and isinstance(inventory_data, dict):
            logger.info(f"Successfully retrieved inventory data for L131")
            logger.info(f"Inventory data contains {len(inventory_data)} colors")
            
            # Check the size formats for each color
            for color, sizes in inventory_data.items():
                logger.info(f"Color: {color}")
                logger.info(f"Sizes for {color}: {sorted(list(sizes.keys()))}")
                
                # Check if XXL or 2XL is used
                if 'XXL' in sizes:
                    logger.info(f"NOTE: 'XXL' format is used in Inventory API for color {color}")
                if '2XL' in sizes:
                    logger.info(f"NOTE: '2XL' format is used in Inventory API for color {color}")
        else:
            logger.warning("Failed to retrieve inventory data or data is not in expected format")
    
    except Exception as e:
        logger.error(f"Error testing Inventory API: {str(e)}")

def test_size_normalization():
    """Test size normalization with various formats"""
    logger.info("Testing size normalization...")
    
    test_sizes = [
        'XXL', 'XXXL', '2XL', '3XL', 
        'XS', 'S', 'M', 'L', 'XL', 
        '4XL', '5XL', '6XL', 
        'SM', 'MED', 'LG', 'XLG'
    ]
    
    for size in test_sizes:
        normalized = color_mapper.normalize_size(size)
        if normalized != size:
            logger.info(f"Normalized '{size}' to '{normalized}'")
        else:
            logger.info(f"Size '{size}' remains unchanged")

if __name__ == "__main__":
    logger.info("Starting XXL vs 2XL format test...")
    
    # Test the size normalization
    test_size_normalization()
    
    # Test product info API
    test_product_info_sizes()
    
    # Test inventory API
    test_inventory_sizes()
    
    logger.info("Test completed!")