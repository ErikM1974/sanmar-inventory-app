#!/usr/bin/env python
"""
Script to import data from SanMar APIs to Caspio tables.
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

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

# Import our custom modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from middleware_client import create_session_with_retries, categorize_error
from caspio_client import CaspioClient

# SanMar API credentials
SANMAR_USERNAME = os.getenv('SANMAR_USERNAME')
SANMAR_PASSWORD = os.getenv('SANMAR_PASSWORD')
SANMAR_CUSTOMER_NUMBER = os.getenv('SANMAR_CUSTOMER_NUMBER')

# Caspio API credentials
CASPIO_BASE_URL = os.getenv('CASPIO_BASE_URL')
CASPIO_CLIENT_ID = os.getenv('CASPIO_CLIENT_ID')
CASPIO_CLIENT_SECRET = os.getenv('CASPIO_CLIENT_SECRET')

# Initialize Caspio client
caspio_client = CaspioClient(
    base_url=CASPIO_BASE_URL,
    client_id=CASPIO_CLIENT_ID,
    client_secret=CASPIO_CLIENT_SECRET
)

# SanMar API endpoints
SANMAR_WSDL = {
    'product_info': 'https://ws.sanmar.com:8080/SanMarWebService/SanMarProductInfoServicePort?wsdl',
    'inventory': 'https://ws.sanmar.com:8080/SanMarWebService/SanMarInventoryServicePort?wsdl',
    'pricing': 'https://ws.sanmar.com:8080/SanMarWebService/SanMarPricingServicePort?wsdl'
}

def get_sanmar_categories():
    """Get categories from SanMar API."""
    logger.info("Getting categories from SanMar API...")
    
    try:
        # Create a session with retries
        session = create_session_with_retries()
        
        # Create a SOAP client for the Product Info service
        from zeep import Client
        client = Client(SANMAR_WSDL['product_info'], transport=session.transport)
        
        # Call the getProductCategories method
        response = client.service.getProductCategories(
            username=SANMAR_USERNAME,
            password=SANMAR_PASSWORD,
            customerNumber=SANMAR_CUSTOMER_NUMBER
        )
        
        # Process the response
        categories = []
        for category in response.categories:
            categories.append({
                'CATEGORY_NAME': category.name,
                'PARENT_CATEGORY_ID': None,
                'DISPLAY_ORDER': len(categories) + 1
            })
            
            # Add subcategories
            if hasattr(category, 'subCategories') and category.subCategories:
                for subcategory in category.subCategories:
                    categories.append({
                        'CATEGORY_NAME': subcategory.name,
                        'PARENT_CATEGORY_ID': len(categories),  # Parent category ID
                        'DISPLAY_ORDER': len(categories) + 1
                    })
        
        logger.info(f"Retrieved {len(categories)} categories from SanMar API.")
        return categories
    except Exception as e:
        error_type, error_message = categorize_error(e)
        logger.error(f"Error getting categories from SanMar API: {error_type} - {error_message}")
        return []

def get_sanmar_products_by_category(category_name):
    """Get products for a category from SanMar API."""
    logger.info(f"Getting products for category '{category_name}' from SanMar API...")
    
    try:
        # Create a session with retries
        session = create_session_with_retries()
        
        # Create a SOAP client for the Product Info service
        from zeep import Client
        client = Client(SANMAR_WSDL['product_info'], transport=session.transport)
        
        # Call the getProductInfoByCategory method
        response = client.service.getProductInfoByCategory(
            username=SANMAR_USERNAME,
            password=SANMAR_PASSWORD,
            customerNumber=SANMAR_CUSTOMER_NUMBER,
            categoryName=category_name
        )
        
        # Process the response
        products = []
        for product in response.products:
            # Get basic product info
            style = product.styleNumber
            title = product.title
            brand = product.brand
            
            # Get colors
            for color in product.colors:
                color_name = color.name
                color_square = color.colorSquare if hasattr(color, 'colorSquare') else None
                
                # Get sizes
                for size in color.sizes:
                    size_name = size.name
                    size_index = get_size_index(size_name)
                    
                    # Get product image
                    product_image = None
                    if hasattr(color, 'images') and color.images:
                        for image in color.images:
                            if image.view == 'Front':
                                product_image = image.url
                                break
                    
                    # Add product to list
                    products.append({
                        'STYLE': style,
                        'PRODUCT_TITLE': title,
                        'CATEGORY_NAME': category_name,
                        'COLOR_NAME': color_name,
                        'SIZE': size_name,
                        'SIZE_INDEX': size_index,
                        'BRAND_NAME': brand,
                        'BRAND_LOGO_IMAGE': get_brand_logo_url(brand),
                        'PRODUCT_IMAGE_URL': product_image,
                        'COLOR_SQUARE_IMAGE': color_square,
                        'KEYWORDS': f"{style} {title} {brand} {color_name} {size_name} {category_name}"
                    })
        
        logger.info(f"Retrieved {len(products)} products for category '{category_name}' from SanMar API.")
        return products
    except Exception as e:
        error_type, error_message = categorize_error(e)
        logger.error(f"Error getting products for category '{category_name}' from SanMar API: {error_type} - {error_message}")
        return []

def get_sanmar_pricing(products):
    """Get pricing information for products from SanMar API."""
    logger.info("Getting pricing information from SanMar API...")
    
    try:
        # Create a session with retries
        session = create_session_with_retries()
        
        # Create a SOAP client for the Pricing service
        from zeep import Client
        client = Client(SANMAR_WSDL['pricing'], transport=session.transport)
        
        # Group products by style
        styles = set()
        for product in products:
            styles.add(product['STYLE'])
        
        # Get pricing for each style
        pricing_data = {}
        for style in styles:
            # Call the getPricing method
            response = client.service.getPricing(
                username=SANMAR_USERNAME,
                password=SANMAR_PASSWORD,
                customerNumber=SANMAR_CUSTOMER_NUMBER,
                styleNumber=style
            )
            
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
                            'CASE_SIZE': case_size
                        }
        
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

def get_sanmar_inventory(products):
    """Get inventory information for products from SanMar API."""
    logger.info("Getting inventory information from SanMar API...")
    
    try:
        # Create a session with retries
        session = create_session_with_retries()
        
        # Create a SOAP client for the Inventory service
        from zeep import Client
        client = Client(SANMAR_WSDL['inventory'], transport=session.transport)
        
        # Group products by style
        styles = set()
        for product in products:
            styles.add(product['STYLE'])
        
        # Get inventory for each style
        inventory_data = []
        for style in styles:
            # Call the getInventoryLevels method
            response = client.service.getInventoryLevels(
                username=SANMAR_USERNAME,
                password=SANMAR_PASSWORD,
                customerNumber=SANMAR_CUSTOMER_NUMBER,
                styleNumber=style
            )
            
            # Process the response
            if hasattr(response, 'inventoryLevels') and response.inventoryLevels:
                for inventory_level in response.inventoryLevels:
                    color_name = inventory_level.color
                    
                    for size_inventory in inventory_level.sizeInventory:
                        size_name = size_inventory.size
                        
                        for warehouse in size_inventory.warehouseInventory:
                            warehouse_id = warehouse.warehouseId
                            quantity = int(warehouse.quantity)
                            
                            # Add inventory record
                            inventory_data.append({
                                'STYLE': style,
                                'COLOR_NAME': color_name,
                                'SIZE': size_name,
                                'WAREHOUSE_ID': warehouse_id,
                                'QUANTITY': quantity,
                                'LAST_UPDATED': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            })
        
        logger.info(f"Retrieved {len(inventory_data)} inventory records.")
        return inventory_data
    except Exception as e:
        error_type, error_message = categorize_error(e)
        logger.error(f"Error getting inventory information from SanMar API: {error_type} - {error_message}")
        return []

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

def import_categories_to_caspio(categories):
    """Import categories to Caspio."""
    logger.info("Importing categories to Caspio...")
    
    try:
        # Clear existing categories
        caspio_client.delete_all_records('Categories')
        
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
        
        # Import products in batches
        batch_size = 100
        for i in range(0, len(products), batch_size):
            batch = products[i:i+batch_size]
            for product in batch:
                caspio_client.insert_record('Products', product)
            logger.info(f"Imported {i + len(batch)} of {len(products)} products.")
        
        logger.info(f"Successfully imported {len(products)} products to Caspio.")
        return True
    except Exception as e:
        logger.error(f"Error importing products to Caspio: {str(e)}")
        return False

def import_inventory_to_caspio(inventory_data):
    """Import inventory data to Caspio."""
    logger.info("Importing inventory data to Caspio...")
    
    try:
        # Clear existing inventory data
        caspio_client.delete_all_records('Inventory')
        
        # Import inventory data in batches
        batch_size = 100
        for i in range(0, len(inventory_data), batch_size):
            batch = inventory_data[i:i+batch_size]
            for inventory_record in batch:
                caspio_client.insert_record('Inventory', inventory_record)
            logger.info(f"Imported {i + len(batch)} of {len(inventory_data)} inventory records.")
        
        logger.info(f"Successfully imported {len(inventory_data)} inventory records to Caspio.")
        return True
    except Exception as e:
        logger.error(f"Error importing inventory data to Caspio: {str(e)}")
        return False

def main():
    """Main function to import data from SanMar to Caspio."""
    logger.info("Starting SanMar to Caspio import...")
    
    # Check if SanMar API credentials are set
    if not SANMAR_USERNAME or not SANMAR_PASSWORD or not SANMAR_CUSTOMER_NUMBER:
        logger.error("SanMar API credentials are not properly configured. Please check your .env file.")
        sys.exit(1)
    
    # Check if Caspio API credentials are set
    if not CASPIO_BASE_URL or not CASPIO_CLIENT_ID or not CASPIO_CLIENT_SECRET:
        logger.error("Caspio API credentials are not properly configured. Please check your .env file.")
        sys.exit(1)
    
    # Get categories from SanMar
    categories = get_sanmar_categories()
    if not categories:
        logger.error("Failed to get categories from SanMar API.")
        sys.exit(1)
    
    # Import categories to Caspio
    if not import_categories_to_caspio(categories):
        logger.error("Failed to import categories to Caspio.")
        sys.exit(1)
    
    # Get products for each category
    all_products = []
    for category in categories:
        category_name = category['CATEGORY_NAME']
        products = get_sanmar_products_by_category(category_name)
        all_products.extend(products)
        
        # Sleep to avoid rate limiting
        time.sleep(1)
    
    if not all_products:
        logger.error("Failed to get products from SanMar API.")
        sys.exit(1)
    
    # Get pricing information
    all_products = get_sanmar_pricing(all_products)
    
    # Import products to Caspio
    if not import_products_to_caspio(all_products):
        logger.error("Failed to import products to Caspio.")
        sys.exit(1)
    
    # Get inventory information
    inventory_data = get_sanmar_inventory(all_products)
    if not inventory_data:
        logger.error("Failed to get inventory information from SanMar API.")
        sys.exit(1)
    
    # Import inventory data to Caspio
    if not import_inventory_to_caspio(inventory_data):
        logger.error("Failed to import inventory data to Caspio.")
        sys.exit(1)
    
    logger.info("SanMar to Caspio import completed successfully.")

if __name__ == "__main__":
    main()