#!/usr/bin/env python
"""
Script to update SanMar products and categories in Caspio quarterly.
This script is designed to be run as a scheduled task every 3 months.
"""

import os
import sys
import json
import logging
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("quarterly_product_update.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import our custom modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from middleware_client import create_soap_client, categorize_error
    from caspio_client import CaspioClient
except ImportError:
    logger.error("Failed to import custom modules. Make sure middleware_client.py and caspio_client.py are in the same directory.")
    sys.exit(1)

# SanMar API credentials
SANMAR_USERNAME = os.getenv('SANMAR_USERNAME')
SANMAR_PASSWORD = os.getenv('SANMAR_PASSWORD')
SANMAR_CUSTOMER_NUMBER = os.getenv('SANMAR_CUSTOMER_NUMBER')

# Caspio API credentials
CASPIO_BASE_URL = os.getenv('CASPIO_BASE_URL')
CASPIO_CLIENT_ID = os.getenv('CASPIO_CLIENT_ID')
CASPIO_CLIENT_SECRET = os.getenv('CASPIO_CLIENT_SECRET')
CASPIO_ACCESS_TOKEN = os.getenv('CASPIO_ACCESS_TOKEN')
CASPIO_REFRESH_TOKEN = os.getenv('CASPIO_REFRESH_TOKEN')

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
    sys.exit(1)

# SanMar API endpoints
SANMAR_WSDL = {
    'product_info': 'https://ws.sanmar.com:8080/SanMarWebService/SanMarProductInfoServicePort?wsdl',
    'pricing': 'https://ws.sanmar.com:8080/SanMarWebService/SanMarPricingServicePort?wsdl'
}

def refresh_caspio_token():
    """Refresh the Caspio API access token."""
    if not CASPIO_REFRESH_TOKEN:
        logger.error("No refresh token available. Please set CASPIO_REFRESH_TOKEN in your .env file.")
        return False
    
    auth_url = f"{CASPIO_BASE_URL}/oauth/token"
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': CASPIO_REFRESH_TOKEN
    }
    
    try:
        response = requests.post(auth_url, data=payload)
        response.raise_for_status()
        
        token_data = response.json()
        access_token = token_data.get('access_token')
        new_refresh_token = token_data.get('refresh_token')
        
        # Update the .env file
        update_env_file(access_token, new_refresh_token)
        
        # Update the Caspio client
        caspio_client.access_token = access_token
        caspio_client.refresh_token = new_refresh_token
        
        logger.info("Successfully refreshed Caspio access token.")
        return True
    except Exception as e:
        logger.error(f"Error refreshing Caspio access token: {str(e)}")
        logger.info("Continuing with the current access token...")
        return True  # Return True to continue with the current token

def update_env_file(access_token, refresh_token):
    """Update the .env file with the new token data."""
    try:
        # Read the current .env file
        env_lines = []
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                env_lines = f.readlines()
        
        # Update or add the token variables
        access_token_line = f"CASPIO_ACCESS_TOKEN={access_token}\n"
        refresh_token_line = f"CASPIO_REFRESH_TOKEN={refresh_token}\n"
        
        access_token_found = False
        refresh_token_found = False
        
        for i, line in enumerate(env_lines):
            if line.startswith('CASPIO_ACCESS_TOKEN='):
                env_lines[i] = access_token_line
                access_token_found = True
            elif line.startswith('CASPIO_REFRESH_TOKEN='):
                env_lines[i] = refresh_token_line
                refresh_token_found = True
        
        if not access_token_found:
            env_lines.append(access_token_line)
        if not refresh_token_found:
            env_lines.append(refresh_token_line)
        
        # Write the updated .env file
        with open('.env', 'w') as f:
            f.writelines(env_lines)
        
        logger.info("Updated .env file with new token data.")
        return True
    except Exception as e:
        logger.error(f"Error updating .env file: {str(e)}")
        return False
def get_sanmar_categories_from_caspio():
    """Get categories from Caspio Sanmar_Bulk_251816_Feb2024 table."""
    logger.info("Getting categories from Caspio Sanmar_Bulk_251816_Feb2024 table...")
    
    try:
        # Query the Sanmar_Bulk_251816_Feb2024 table to get unique categories and subcategories
        endpoint = f"rest/v2/tables/Sanmar_Bulk_251816_Feb2024/records"
        params = {
            'select': 'CATEGORY_NAME,SUBCATEGORY_NAME',
            'q.distinct': 'true',
            'q.sort': 'CATEGORY_NAME,SUBCATEGORY_NAME'
        }
        
        # Make the API request
        response = caspio_client.make_api_request(endpoint, params=params)
        
        if not response or 'Result' not in response:
            logger.error("Failed to get categories from Caspio.")
            return []
        
        # Process the response
        category_dict = {}
        for item in response['Result']:
            category_name = item.get('CATEGORY_NAME')
            subcategory_name = item.get('SUBCATEGORY_NAME')
            
            if category_name:
                if category_name not in category_dict:
                    category_dict[category_name] = []
                
                if subcategory_name and subcategory_name not in category_dict[category_name]:
                    category_dict[category_name].append(subcategory_name)
        
        # Convert to the format needed for the Categories table
        categories = []
        display_order = 1
        
        for category_name, subcategories in category_dict.items():
            # Add the main category
            category_id = display_order
            categories.append({
                'CATEGORY_NAME': category_name,
                'PARENT_CATEGORY_ID': None,
                'DISPLAY_ORDER': display_order
            })
            display_order += 1
            
            # Add subcategories
            for subcategory_name in subcategories:
                categories.append({
                    'CATEGORY_NAME': subcategory_name,
                    'PARENT_CATEGORY_ID': category_id,
                    'DISPLAY_ORDER': display_order
                })
                display_order += 1
        
        logger.info(f"Retrieved {len(categories)} categories from Caspio.")
        return categories
    except Exception as e:
        logger.error(f"Error getting categories from Caspio: {str(e)}")
        return []
        return []

def get_brand_logo_url(brand_name):
    """Get the URL for a brand logo."""
    # Define brand logo URLs
    brand_logos = {
        "Port & Company": "https://www.sanmar.com/assets/img/port-and-company-logo.png",
        "Port Authority": "https://www.sanmar.com/assets/img/port-authority-logo.png",
        "Sport-Tek": "https://www.sanmar.com/assets/img/sport-tek-logo.png",
        "District": "https://www.sanmar.com/assets/img/district-logo.png",
        "New Era": "https://www.sanmar.com/assets/img/new-era-logo.png",
        "Nike": "https://www.sanmar.com/assets/img/nike-logo.png",
        "OGIO": "https://www.sanmar.com/assets/img/ogio-logo.png",
        "Eddie Bauer": "https://www.sanmar.com/assets/img/eddie-bauer-logo.png",
        "The North Face": "https://www.sanmar.com/assets/img/the-north-face-logo.png",
        "Red House": "https://www.sanmar.com/assets/img/red-house-logo.png",
        "TravisMathew": "https://www.sanmar.com/assets/img/travismathew-logo.png",
        "Carhartt": "https://www.sanmar.com/assets/img/carhartt-logo.png"
    }
    
    return brand_logos.get(brand_name, "")

def get_size_index(size_name):
    """Get the index for a size to use for sorting."""
    # Define standard size order
    standard_size_order = [
        "XS", "S", "S/M", "M", "M/L", "L", "L/XL", "XL", "XXL", "2XL", "3XL", "4XL", "5XL", "6XL"
    ]
    
    # Check if size is in standard size order
    if size_name in standard_size_order:
        return standard_size_order.index(size_name)
    
    # Handle numeric sizes
    try:
        return int(size_name)
    except ValueError:
        # For other sizes, return a high index
        return 999

def get_sanmar_products_from_caspio(category_name=None):
    """Get products for a category from Caspio Sanmar_Bulk_251816_Feb2024 table."""
    logger.info(f"Getting products for category '{category_name if category_name else 'all'}' from Caspio...")
    
    try:
        # Query the Sanmar_Bulk_251816_Feb2024 table to get products
        endpoint = f"rest/v2/tables/Sanmar_Bulk_251816_Feb2024/records"
        
        # Set up query parameters
        params = {
            'q.sort': 'STYLE,COLOR_NAME,SIZE_INDEX',
            'q.limit': 1000  # Adjust as needed
        }
        
        # Add category filter if specified
        if category_name:
            params['q.where'] = f"CATEGORY_NAME='{category_name}'"
        
        # Make the API request
        response = caspio_client.make_api_request(endpoint, params=params)
        
        if not response or 'Result' not in response:
            logger.error(f"Failed to get products for category '{category_name if category_name else 'all'}' from Caspio.")
            return []
        
        # Process the response
        products = []
        for item in response['Result']:
            # Extract product data
            product = {
                'STYLE': item.get('STYLE', ''),
                'PRODUCT_TITLE': item.get('PRODUCT_TITLE', ''),
                'CATEGORY_NAME': item.get('CATEGORY_NAME', ''),
                'SUBCATEGORY_NAME': item.get('SUBCATEGORY_NAME', ''),  # Include the SUBCATEGORY_NAME field
                'COLOR_NAME': item.get('COLOR_NAME', ''),
                'SIZE': item.get('SIZE', ''),
                'SIZE_INDEX': item.get('SIZE_INDEX', 0),
                'BRAND_NAME': item.get('BRAND_NAME', ''),
                'BRAND_LOGO_IMAGE': item.get('BRAND_LOGO_IMAGE', ''),
                'PRODUCT_IMAGE_URL': item.get('FRONT_MODEL', ''),
                'COLOR_SQUARE_IMAGE': item.get('COLOR_SQUARE_IMAGE', ''),
                'PRICE': item.get('PIECE_PRICE', 0),
                'PIECE_PRICE': item.get('PIECE_PRICE', 0),
                'CASE_PRICE': item.get('CASE_PRICE', 0),
                'CASE_SIZE': item.get('CASE_SIZE', 1),
                'PROGRAM_PRICE': item.get('Program_Price', 0),  # Include the Program_Price field
                'KEYWORDS': item.get('KEYWORDS', '')
            }
            
            products.append(product)
        
        logger.info(f"Retrieved {len(products)} products for category '{category_name if category_name else 'all'}' from Caspio.")
        return products
    except Exception as e:
        logger.error(f"Error getting products for category '{category_name if category_name else 'all'}' from Caspio: {str(e)}")
        return []

def get_sanmar_pricing(products):
    """Get pricing information for products from SanMar API."""
    logger.info("Getting pricing information from SanMar API...")
    
    try:
        # Create a SOAP client for the Pricing service
        client = create_soap_client(SANMAR_WSDL['pricing'])
        
        # Group products by style
        styles = set()
        for product in products:
            styles.add(product['STYLE'])
        
        # Get pricing for each style
        pricing_data = {}
        total_styles = len(styles)
        
        for i, style in enumerate(styles):
            logger.info(f"Getting pricing for style {style} ({i+1}/{total_styles})...")
            
            # Create the item array
            item = client.get_type('ns0:item')
            item_instance = item(
                styleNumber=style,
                username=SANMAR_USERNAME,
                password=SANMAR_PASSWORD,
                customerNumber=SANMAR_CUSTOMER_NUMBER
            )
            
            # Create the webServiceUser
            web_service_user = client.get_type('ns0:webServiceUser')
            web_service_user_instance = web_service_user(
                username=SANMAR_USERNAME,
                password=SANMAR_PASSWORD,
                customerNumber=SANMAR_CUSTOMER_NUMBER
            )
            
            # Call the getPricing method with the correct parameters
            response = client.service.getPricing([item_instance], web_service_user_instance)
            
            # Process the response
            if hasattr(response, 'pricingInfo') and response.pricingInfo:
                for pricing_info in response.pricingInfo:
                    color_name = pricing_info.color
                    
                    for size_pricing in pricing_info.sizePricing:
                        size_name = size_pricing.size
                        price = float(size_pricing.price)
                        piece_price = float(size_pricing.piecePrice) if hasattr(size_pricing, 'piecePrice') else price
                        case_price = float(size_pricing.casePrice) if hasattr(size_pricing, 'casePrice') else price
                        case_size = int(size_pricing.caseSize) if hasattr(size_pricing, 'caseSize') else 1
                        
                        # Store pricing data
                        key = f"{style}_{color_name}_{size_name}"
                        pricing_data[key] = {
                            'PRICE': price,
                            'PIECE_PRICE': piece_price,
                            'CASE_PRICE': case_price,
                            'CASE_SIZE': case_size,
                            'PROGRAM_PRICE': price  # Use the price as the program price by default
                        }
            
            # Sleep briefly to avoid overwhelming the API
            time.sleep(0.5)
        
        # Update products with pricing information
        for product in products:
            key = f"{product['STYLE']}_{product['COLOR_NAME']}_{product['SIZE']}"
            if key in pricing_data:
                product.update(pricing_data[key])
        
        logger.info(f"Retrieved pricing information for {len(pricing_data)} product variations.")
        return products
    except Exception as e:
        error_type, error_message = categorize_error(e)
        logger.error(f"Error getting pricing information from SanMar API: {error_type} - {error_message}")
        return products

def import_categories_to_caspio(categories):
    """Import categories to Caspio."""
    logger.info("Importing categories to Caspio...")
    
    try:
        # Clear existing categories
        caspio_client.delete_all_records('Categories')
        logger.info("Cleared existing categories from Caspio.")
        
        # Import categories
        for category in categories:
            caspio_client.insert_record('Categories', category)
        
        logger.info(f"Successfully imported {len(categories)} categories to Caspio.")
        return True
    except Exception as e:
        logger.error(f"Error importing categories to Caspio: {str(e)}")
        return False

def import_products_to_caspio(products):
    """Import products to Caspio."""
    logger.info("Importing products to Caspio...")
    
    try:
        # Clear existing products
        caspio_client.delete_all_records('Products')
        logger.info("Cleared existing products from Caspio.")
        
        # Import products in batches
        batch_size = 100
        total_records = len(products)
        records_inserted = 0
        
        for i in range(0, total_records, batch_size):
            batch = products[i:i+batch_size]
            for product in batch:
                caspio_client.insert_record('Products', product)
            
            records_inserted += len(batch)
            logger.info(f"Imported {records_inserted} of {total_records} products ({(records_inserted/total_records)*100:.1f}%).")
            
            # Sleep briefly to avoid overwhelming the API
            time.sleep(0.5)
        
        logger.info(f"Successfully imported {records_inserted} products to Caspio.")
        return True
    except Exception as e:
        logger.error(f"Error importing products to Caspio: {str(e)}")
        return False

def main():
    """Main function to update SanMar products and categories in Caspio."""
    logger.info("Starting quarterly SanMar product and category update...")
    
    # Check if SanMar API credentials are set
    if not SANMAR_USERNAME or not SANMAR_PASSWORD or not SANMAR_CUSTOMER_NUMBER:
        logger.error("SanMar API credentials are not properly configured. Please check your .env file.")
        sys.exit(1)
    
    # Refresh Caspio token if using token-based authentication
    if CASPIO_ACCESS_TOKEN and CASPIO_REFRESH_TOKEN:
        refresh_caspio_token()
    
    # Get categories from Caspio Sanmar_Bulk_251816_Feb2024 table
    categories = get_sanmar_categories_from_caspio()
    if not categories:
        logger.error("Failed to get categories from Caspio.")
        sys.exit(1)
    
    # Import categories to Caspio Categories table
    if not import_categories_to_caspio(categories):
        logger.error("Failed to import categories to Caspio Categories table.")
        sys.exit(1)
    
    # Get all products from Caspio Sanmar_Bulk_251816_Feb2024 table
    all_products = get_sanmar_products_from_caspio()
    if not all_products:
        logger.error("Failed to get products from Caspio.")
        sys.exit(1)
    
    # Get fresh pricing information from SanMar API
    logger.info("Getting fresh pricing information from SanMar API...")
    all_products = get_sanmar_pricing(all_products)
    
    # Import products to Caspio Products table
    if import_products_to_caspio(all_products):
        logger.info("Quarterly SanMar product and category update completed successfully.")
    else:
        logger.error("Failed to import products to Caspio Products table.")
        sys.exit(1)

if __name__ == "__main__":
    main()