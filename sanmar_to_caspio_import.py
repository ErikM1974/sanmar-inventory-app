"""
Script to export data from SanMar API and format it for Caspio import.

This script fetches product data from the SanMar API, formats it according to the
Caspio database structure defined in caspio-implementation-plan.md, and saves it
to a CSV file that can be imported into Caspio.
"""

import os
import csv
import json
import time
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv
import zeep
from zeep.transports import Transport
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Load environment variables
load_dotenv()

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

# SanMar API credentials
SANMAR_USERNAME = os.getenv("SANMAR_USERNAME")
SANMAR_PASSWORD = os.getenv("SANMAR_PASSWORD")
SANMAR_CUSTOMER_NUMBER = os.getenv("SANMAR_CUSTOMER_NUMBER")

# Check if credentials are set
if not all([SANMAR_USERNAME, SANMAR_PASSWORD, SANMAR_CUSTOMER_NUMBER]):
    logger.error("SanMar API credentials not set in .env file.")
    exit(1)

# SOAP clients for SanMar APIs
product_wsdl = "https://ws.sanmar.com:8080/SanMarWebService/SanMarProductInfoServicePort?wsdl"
inventory_wsdl = "https://ws.sanmar.com:8080/promostandards/InventoryServiceBindingV2final?WSDL"
pricing_wsdl = "https://ws.sanmar.com:8080/promostandards/PricingAndConfigurationServiceBinding?WSDL"

# Configure retry strategy
retry_strategy = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504]
)
transport = Transport(timeout=30)
transport.session.mount('https://', HTTPAdapter(max_retries=retry_strategy))

# Initialize SOAP clients
try:
    product_client = zeep.Client(wsdl=product_wsdl, transport=transport)
    inventory_client = zeep.Client(wsdl=inventory_wsdl, transport=transport)
    pricing_client = zeep.Client(wsdl=pricing_wsdl, transport=transport)
    logger.info("Successfully initialized SOAP clients")
except Exception as e:
    logger.error(f"Error initializing SOAP clients: {str(e)}")
    exit(1)

def get_product_categories():
    """Get all product categories from SanMar API."""
    logger.info("Fetching product categories from SanMar API...")
    
    request_data = {
        "arg0": {"style": "", "color": "", "size": ""},
        "arg1": {"sanMarCustomerNumber": SANMAR_CUSTOMER_NUMBER, 
                 "sanMarUserName": SANMAR_USERNAME,
                 "sanMarUserPassword": SANMAR_PASSWORD}
    }
    
    try:
        response = product_client.service.getProductInfoByCategory(**request_data)
        
        if hasattr(response, 'errorOccured') and response.errorOccured:
            logger.error(f"API error: {response.message}")
            return []
        
        categories = []
        if hasattr(response, 'listResponse'):
            for item in response.listResponse:
                if hasattr(item, 'category'):
                    categories.append(item.category)
        
        # Remove duplicates
        categories = list(set(categories))
        logger.info(f"Found {len(categories)} unique categories")
        return categories
    
    except Exception as e:
        logger.error(f"Error fetching product categories: {str(e)}")
        return []

def get_products_by_category(category):
    """Get all products for a specific category from SanMar API."""
    logger.info(f"Fetching products for category: {category}")
    
    request_data = {
        "arg0": {"category": category, "style": "", "color": "", "size": ""},
        "arg1": {"sanMarCustomerNumber": SANMAR_CUSTOMER_NUMBER, 
                 "sanMarUserName": SANMAR_USERNAME,
                 "sanMarUserPassword": SANMAR_PASSWORD}
    }
    
    try:
        response = product_client.service.getProductInfoByCategory(**request_data)
        
        if hasattr(response, 'errorOccured') and response.errorOccured:
            logger.error(f"API error: {response.message}")
            return []
        
        products = []
        if hasattr(response, 'listResponse'):
            for item in response.listResponse:
                if hasattr(item, 'productBasicInfo'):
                    products.append(item)
        
        logger.info(f"Found {len(products)} products in category {category}")
        return products
    
    except Exception as e:
        logger.error(f"Error fetching products for category {category}: {str(e)}")
        return []

def get_product_details(style):
    """Get detailed information for a specific product style."""
    logger.info(f"Fetching details for product style: {style}")
    
    request_data = {
        "arg0": {"style": style, "color": "", "size": ""},
        "arg1": {"sanMarCustomerNumber": SANMAR_CUSTOMER_NUMBER, 
                 "sanMarUserName": SANMAR_USERNAME,
                 "sanMarUserPassword": SANMAR_PASSWORD}
    }
    
    try:
        response = product_client.service.getProductInfoByStyleColorSize(**request_data)
        
        if hasattr(response, 'errorOccured') and response.errorOccured:
            logger.error(f"API error: {response.message}")
            return None
        
        if hasattr(response, 'listResponse') and len(response.listResponse) > 0:
            return response.listResponse
        
        logger.warning(f"No details found for product style: {style}")
        return None
    
    except Exception as e:
        logger.error(f"Error fetching details for product style {style}: {str(e)}")
        return None

def get_inventory_levels(style):
    """Get inventory levels for a specific product style."""
    logger.info(f"Fetching inventory levels for product style: {style}")
    
    request_data = {
        "wsVersion": "2.0.0",
        "id": SANMAR_USERNAME,
        "password": SANMAR_PASSWORD,
        "productId": style
    }
    
    try:
        response = inventory_client.service.getInventoryLevels(**request_data)
        
        # Process the response into a more usable format
        inventory_data = {}
        
        if hasattr(response, 'Inventory') and hasattr(response.Inventory, 'PartInventoryArray'):
            for part in response.Inventory.PartInventoryArray.PartInventory:
                color = part.partColor
                size = part.labelSize
                
                if color not in inventory_data:
                    inventory_data[color] = {}
                
                # Get total quantity across all warehouses
                total_qty = 0
                warehouse_data = {}
                
                if hasattr(part, 'InventoryLocationArray'):
                    for location in part.InventoryLocationArray.InventoryLocation:
                        warehouse_id = location.inventoryLocationId
                        qty = int(location.inventoryLocationQuantity.Quantity.value)
                        warehouse_data[warehouse_id] = qty
                        total_qty += qty
                
                inventory_data[color][size] = {
                    'total': total_qty,
                    'warehouses': warehouse_data
                }
        
        logger.info(f"Retrieved inventory data for {len(inventory_data)} colors")
        return inventory_data
    
    except Exception as e:
        logger.error(f"Error fetching inventory levels for product style {style}: {str(e)}")
        return {}

def get_pricing_data(style):
    """Get pricing data for a specific product style."""
    logger.info(f"Fetching pricing data for product style: {style}")
    
    request_data = {
        "wsVersion": "1.0.0",
        "id": SANMAR_USERNAME,
        "password": SANMAR_PASSWORD,
        "productId": style,
        "currency": "USD",
        "fobId": "1",
        "priceType": "List",
        "localizationCountry": "US",
        "localizationLanguage": "EN",
        "configurationType": "Blank"
    }
    
    try:
        response = pricing_client.service.getConfigurationAndPricing(**request_data)
        
        # Process the response into a more usable format
        pricing_data = {}
        
        if hasattr(response, 'Configuration') and hasattr(response.Configuration, 'PartArray'):
            for part in response.Configuration.PartArray:
                part_id = part.partId
                
                # Get color and size from part description
                part_desc = part.partDescription if hasattr(part, 'partDescription') else ""
                color_size = part_desc.split('.')[-1].strip() if '.' in part_desc else ""
                
                # Extract pricing information
                if hasattr(part, 'PartPriceArray') and part.PartPriceArray:
                    for price in part.PartPriceArray:
                        if price.minQuantity == 1:  # Use the price for a single unit
                            pricing_data[part_id] = {
                                'price': float(price.price),
                                'description': part_desc,
                                'color_size': color_size
                            }
                            break
        
        logger.info(f"Retrieved pricing data for {len(pricing_data)} parts")
        return pricing_data
    
    except Exception as e:
        logger.error(f"Error fetching pricing data for product style {style}: {str(e)}")
        return {}

def format_product_for_caspio(product_info, inventory_data, pricing_data):
    """Format product data for Caspio import."""
    formatted_products = []
    
    try:
        # Extract basic product information
        basic_info = product_info.productBasicInfo if hasattr(product_info, 'productBasicInfo') else None
        if not basic_info:
            return []
        
        style = basic_info.style if hasattr(basic_info, 'style') else ""
        product_title = basic_info.productTitle if hasattr(basic_info, 'productTitle') else ""
        product_description = basic_info.productDescription if hasattr(basic_info, 'productDescription') else ""
        
        # Extract image information
        image_info = product_info.productImageInfo if hasattr(product_info, 'productImageInfo') else None
        thumbnail_image = image_info.thumbnailImage if image_info and hasattr(image_info, 'thumbnailImage') else ""
        product_image = image_info.productImage if image_info and hasattr(image_info, 'productImage') else ""
        
        # Extract category information
        category_name = basic_info.category if hasattr(basic_info, 'category') else ""
        subcategory_name = basic_info.subCategory if hasattr(basic_info, 'subCategory') else ""
        
        # Extract color and size
        color_name = basic_info.color if hasattr(basic_info, 'color') else ""
        size = basic_info.size if hasattr(basic_info, 'size') else ""
        
        # Extract unique key and part ID
        unique_key = basic_info.uniqueKey if hasattr(basic_info, 'uniqueKey') else ""
        part_id = unique_key  # Use unique key as part ID
        
        # Get inventory quantity
        qty = 0
        if color_name in inventory_data and size in inventory_data[color_name]:
            qty = inventory_data[color_name][size]['total']
        
        # Get pricing information
        piece_price = 0
        case_price = 0
        case_size = 0
        
        if part_id in pricing_data:
            piece_price = pricing_data[part_id]['price']
            case_price = piece_price  # Default to piece price if case price not available
        
        # Create formatted product record
        formatted_product = {
            'UNIQUE_KEY': unique_key,
            'STYLE': style,
            'PRODUCT_TITLE': product_title,
            'PRODUCT_DESCRIPTION': product_description,
            'THUMBNAIL_IMAGE': thumbnail_image,
            'PRODUCT_IMAGE': product_image,
            'CATEGORY_NAME': category_name,
            'SUBCATEGORY_NAME': subcategory_name,
            'COLOR_NAME': color_name,
            'SIZE': size,
            'QTY': qty,
            'PIECE_PRICE': piece_price,
            'CASE_PRICE': case_price,
            'CASE_SIZE': case_size,
            'MILL': basic_info.mill if hasattr(basic_info, 'mill') else "",
            'BRAND_NAME': basic_info.mill if hasattr(basic_info, 'mill') else "",  # Use mill as brand name
            'PRODUCT_STATUS': basic_info.productStatus if hasattr(basic_info, 'productStatus') else ""
        }
        
        # Add additional fields if available
        if hasattr(basic_info, 'msrp'):
            formatted_product['MSRP'] = basic_info.msrp
        
        if hasattr(basic_info, 'mapPricing'):
            formatted_product['MAP_PRICING'] = basic_info.mapPricing
        
        if image_info and hasattr(image_info, 'colorSquareImage'):
            formatted_product['COLOR_SQUARE_IMAGE'] = image_info.colorSquareImage
        
        if image_info and hasattr(image_info, 'colorProductImage'):
            formatted_product['COLOR_PRODUCT_IMAGE'] = image_info.colorProductImage
        
        formatted_products.append(formatted_product)
        
    except Exception as e:
        logger.error(f"Error formatting product for Caspio: {str(e)}")
    
    return formatted_products

def export_to_csv(products, filename):
    """Export formatted products to a CSV file."""
    if not products:
        logger.warning("No products to export")
        return False
    
    try:
        # Get all possible field names from all products
        fieldnames = set()
        for product in products:
            fieldnames.update(product.keys())
        
        fieldnames = sorted(list(fieldnames))
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(products)
        
        logger.info(f"Successfully exported {len(products)} products to {filename}")
        return True
    
    except Exception as e:
        logger.error(f"Error exporting to CSV: {str(e)}")
        return False

def main():
    """Main function to run the export process."""
    logger.info("Starting SanMar to Caspio export process")
    
    # Create output directory if it doesn't exist
    output_dir = "caspio_export"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Get all product categories
    categories = get_product_categories()
    
    if not categories:
        logger.error("No categories found. Exiting.")
        return
    
    # Process each category
    all_products = []
    
    for category in categories:
        logger.info(f"Processing category: {category}")
        
        # Get products for this category
        category_products = get_products_by_category(category)
        
        if not category_products:
            logger.warning(f"No products found for category: {category}")
            continue
        
        # Process each product
        for product in category_products:
            if not hasattr(product, 'productBasicInfo'):
                continue
            
            style = product.productBasicInfo.style if hasattr(product.productBasicInfo, 'style') else ""
            
            if not style:
                continue
            
            # Get detailed product information
            product_details = get_product_details(style)
            
            if not product_details:
                continue
            
            # Get inventory levels
            inventory_data = get_inventory_levels(style)
            
            # Get pricing data
            pricing_data = get_pricing_data(style)
            
            # Format each product variant
            for detail in product_details:
                formatted_products = format_product_for_caspio(detail, inventory_data, pricing_data)
                all_products.extend(formatted_products)
            
            # Sleep briefly to avoid overwhelming the API
            time.sleep(0.5)
    
    # Export all products to CSV
    csv_filename = os.path.join(output_dir, f"sanmar_products_{timestamp}.csv")
    export_success = export_to_csv(all_products, csv_filename)
    
    if export_success:
        logger.info(f"Export completed successfully. File: {csv_filename}")
    else:
        logger.error("Export failed.")

if __name__ == "__main__":
    main()