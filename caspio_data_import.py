#!/usr/bin/env python
"""
Caspio Data Import Script for SanMar Product Data

This script imports product data from SanMar API into Caspio database.
It handles incremental updates to minimize data transfer and API calls.
"""

import os
import json
import logging
import time
from datetime import datetime
from dotenv import load_dotenv

# Import our custom modules
from caspio_client import caspio_api
from middleware_client import create_session_with_retries
import sanmar_inventory
import sanmar_product
from sanmar_category_service import get_all_categories

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("caspio_import.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_sanmar_categories():
    """Get all categories from SanMar API"""
    logger.info("Fetching categories from SanMar API")
    try:
        categories = get_all_categories()
        logger.info(f"Successfully retrieved {len(categories)} categories")
        return categories
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        return []

def get_sanmar_products_by_category(category):
    """Get all products for a specific category from SanMar API"""
    logger.info(f"Fetching products for category: {category}")
    try:
        products = sanmar_product.get_products_by_category(category)
        logger.info(f"Successfully retrieved {len(products)} products for category {category}")
        return products
    except Exception as e:
        logger.error(f"Error fetching products for category {category}: {str(e)}")
        return []

def get_sanmar_product_details(style):
    """Get detailed product information for a specific style"""
    logger.info(f"Fetching product details for style: {style}")
    try:
        product_details = sanmar_product.get_product_details(style)
        return product_details
    except Exception as e:
        logger.error(f"Error fetching product details for style {style}: {str(e)}")
        return None

def get_sanmar_inventory(style):
    """Get inventory information for a specific style"""
    logger.info(f"Fetching inventory for style: {style}")
    try:
        inventory = sanmar_inventory.get_inventory(style)
        return inventory
    except Exception as e:
        logger.error(f"Error fetching inventory for style {style}: {str(e)}")
        return None

def transform_product_data(product, product_details, inventory):
    """Transform SanMar product data to Caspio format"""
    caspio_records = []
    
    # Basic product information
    base_record = {
        "STYLE": product.get("styleNumber", ""),
        "PRODUCT_TITLE": product.get("name", ""),
        "BRAND_NAME": product.get("brand", {}).get("name", ""),
        "BRAND_LOGO_IMAGE": product.get("brand", {}).get("logoUrl", ""),
        "CATEGORY_NAME": product.get("primaryCategory", {}).get("name", ""),
        "SUBCATEGORY_NAME": product.get("secondaryCategory", {}).get("name", ""),
        "KEYWORDS": ", ".join(product.get("keywords", [])),
        "LAST_UPDATED": datetime.now().isoformat()
    }
    
    # Add product details if available
    if product_details:
        base_record["PRODUCT_IMAGE"] = product_details.get("mainImage", "")
    
    # Add inventory and color/size information if available
    if inventory:
        for color, sizes in inventory.items():
            color_record = base_record.copy()
            color_record["COLOR_NAME"] = color
            
            # Try to find color swatch image from product details
            if product_details and "colors" in product_details:
                for color_info in product_details.get("colors", []):
                    if color_info.get("name") == color:
                        color_record["COLOR_SQUARE_IMAGE"] = color_info.get("swatchImage", "")
                        break
            
            for size, qty in sizes.items():
                size_record = color_record.copy()
                size_record["SIZE"] = size
                
                # Set size index for proper sorting
                size_index = get_size_index(size)
                size_record["SIZE_INDEX"] = size_index
                
                # Set quantity
                size_record["QTY"] = qty.get("total", 0) if isinstance(qty, dict) else qty
                
                # Add pricing information (placeholder - would need to be updated with actual pricing API)
                size_record["PIECE_PRICE"] = 0.0
                size_record["CASE_PRICE"] = 0.0
                size_record["CASE_SIZE"] = 0
                
                caspio_records.append(size_record)
    
    return caspio_records

def get_size_index(size):
    """Get numeric index for size to enable proper sorting"""
    size_map = {
        "XS": 10,
        "S": 20,
        "S/M": 25,
        "M": 30,
        "M/L": 35,
        "L": 40,
        "L/XL": 45,
        "XL": 50,
        "XXL": 60,
        "2XL": 60,  # Same as XXL
        "3XL": 70,
        "4XL": 80,
        "5XL": 90,
        "6XL": 100
    }
    
    # Try to match the size directly
    if size in size_map:
        return size_map[size]
    
    # For numeric sizes, try to extract the number
    if size.isdigit():
        return int(size) * 5
    
    # Default to a high number for unknown sizes
    return 999

def upload_to_caspio(records):
    """Upload records to Caspio database"""
    if not records:
        logger.warning("No records to upload")
        return 0
    
    logger.info(f"Uploading {len(records)} records to Caspio")
    
    # Split records into batches to avoid API limits
    batch_size = 100
    batches = [records[i:i + batch_size] for i in range(0, len(records), batch_size)]
    
    total_uploaded = 0
    for i, batch in enumerate(batches):
        logger.info(f"Uploading batch {i+1} of {len(batches)} ({len(batch)} records)")
        try:
            # First check if records exist and need updating
            for record in batch:
                style = record["STYLE"]
                color = record["COLOR_NAME"]
                size = record["SIZE"]
                
                # Check if record exists
                existing = caspio_api.get_product_by_style_color_size(style, color, size)
                
                if existing and existing.get("Result") and len(existing["Result"]) > 0:
                    # Record exists, update it
                    record_id = existing["Result"][0]["RecordID"]  # Assuming RecordID is the primary key
                    result = caspio_api._make_api_request(
                        f"rest/v2/tables/{caspio_api.products_table}/records/{record_id}",
                        method="PUT",
                        data=record
                    )
                    if result:
                        total_uploaded += 1
                else:
                    # Record doesn't exist, create it
                    result = caspio_api._make_api_request(
                        f"rest/v2/tables/{caspio_api.products_table}/records",
                        method="POST",
                        data=record
                    )
                    if result:
                        total_uploaded += 1
            
            # Sleep briefly between batches to avoid rate limits
            if i < len(batches) - 1:
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Error uploading batch {i+1}: {str(e)}")
    
    logger.info(f"Successfully uploaded {total_uploaded} records to Caspio")
    return total_uploaded

def main():
    """Main function to import SanMar data into Caspio"""
    logger.info("Starting SanMar to Caspio data import")
    
    # Get all categories from SanMar
    categories = get_sanmar_categories()
    
    total_products = 0
    total_records = 0
    
    # Process each category
    for category in categories:
        category_name = category.get("name")
        logger.info(f"Processing category: {category_name}")
        
        # Get products for this category
        products = get_sanmar_products_by_category(category_name)
        
        # Process each product
        for product in products:
            style = product.get("styleNumber")
            if not style:
                continue
                
            # Get detailed product information
            product_details = get_sanmar_product_details(style)
            
            # Get inventory information
            inventory = get_sanmar_inventory(style)
            
            # Transform data to Caspio format
            caspio_records = transform_product_data(product, product_details, inventory)
            
            # Upload to Caspio
            uploaded = upload_to_caspio(caspio_records)
            
            total_products += 1
            total_records += uploaded
            
            # Log progress
            if total_products % 10 == 0:
                logger.info(f"Processed {total_products} products, uploaded {total_records} records")
            
            # Sleep briefly to avoid overwhelming the APIs
            time.sleep(0.5)
    
    logger.info(f"Import complete. Processed {total_products} products, uploaded {total_records} records")

if __name__ == "__main__":
    main()