"""
Mock product data for Northwest Custom Apparel
This module provides mock data for the customer-facing routes when API connections aren't available
"""

import logging
import json
import os
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

# Product data for top selling styles
MOCK_PRODUCTS = {
    "PC61": {
        "product_name": "Port & Company Essential Tee",
        "product_description": "An enduring favorite, our comfortable classic tee is an everyday essential. With superior wrinkle and shrink resistance, a silky soft hand and an incredible range of styles, sizes and colors.",
        "catalog_colors": ["Black", "White", "Navy", "Athletic Heather", "Red", "Royal"],
        "sizes": ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"],
        "price": 3.49,
        "case_size": 72
    },
    "J790": {
        "product_name": "Port Authority Glacier Soft Shell Jacket",
        "product_description": "Our Glacier Soft Shell Jacket keeps the elements at bay with a windproof and water-resistant membrane. Great for everyday wear, this gentle stretch jacket has comfortable features ideal for layering.",
        "catalog_colors": ["Black/Chrome", "AtlBlue/Chrome", "Smk Gry/Chrome", "Olive/Chrome"],
        "sizes": ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"],
        "price": 30.59,
        "case_size": 24
    },
    "K500": {
        "product_name": "Port Authority Silk Touch Polo",
        "product_description": "A silky smooth, baby piqué knit polo that resists wrinkles, wicking and shrinking. Easy care blend for wash-and-wear convenience. The K500 delivers superior performance and color retention.",
        "catalog_colors": ["Black", "White", "Navy", "Royal", "Red"],
        "sizes": ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"],
        "price": 13.99,
        "case_size": 36
    },
    "L500": {
        "product_name": "Port Authority Ladies Silk Touch Polo",
        "product_description": "The Ladies Silk Touch Polo offers superior wrinkle and shrink resistance, a silky soft hand and incredible range of styles, sizes and colors. Features a flat knit collar and cuffs, metal buttons with dyed-to-match plastic rims, and side vents.",
        "catalog_colors": ["Black", "White", "Navy", "Royal", "Red", "Pink"],
        "sizes": ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"],
        "price": 13.99,
        "case_size": 36
    }
}

# Additional product data for fallback
MOCK_PRODUCTS_FALLBACK = {
    "DT292": {
        "product_name": "District Very Important Tee",
        "product_description": "This is it. The perfect tee for any occasion. Our District Very Important Tee is made from super soft 100% ring spun cotton for incredible comfort and style.",
        "catalog_colors": ["Black", "White", "Navy", "Athletic Heather", "Red"],
        "sizes": ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"],
        "price": 4.99,
        "case_size": 72
    },
    "LK5602": {
        "product_name": "Sport-Tek Ladies PosiCharge Electric Heather Colorblock 1/4-Zip Pullover",
        "product_description": "This colorblock pullover combines active-friendly technology with electric heather styling. It wicks moisture, fights odor and static, and is snag resistant.",
        "catalog_colors": ["Black Electric/Black", "True Navy Electric/True Navy", "True Red Electric/True Red"],
        "sizes": ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"],
        "price": 24.99,
        "case_size": 24
    }
}

def get_mock_product_data(style):
    """
    Get mock product data for a specific style
    
    Args:
        style (str): Product style number
    
    Returns:
        dict: Product data or None if style not found
    """
    logger.info(f"Getting mock product data for style: {style}")
    
    # First check our primary mock products
    if style in MOCK_PRODUCTS:
        product = MOCK_PRODUCTS[style]
        
        # Generate image URLs for all colors
        images = {}
        swatch_images = {}
        for color in product["catalog_colors"]:
            images[color] = get_mock_image_url(style, image_type="p110", color=color)
            swatch_images[color] = get_mock_swatch_url(style, color=color)
            
        # Create a more comprehensive product data structure
        product_data = {
            "product_name": product["product_name"],
            "product_description": product["product_description"],
            "catalog_colors": product["catalog_colors"],
            "display_colors": {color: color for color in product["catalog_colors"]},
            "sizes": product["sizes"],
            "images": images,
            "swatch_images": swatch_images,
            "price": product["price"],
            "case_size": product["case_size"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return product_data
    
    # Check fallback products
    elif style in MOCK_PRODUCTS_FALLBACK:
        product = MOCK_PRODUCTS_FALLBACK[style]
        
        # Generate image URLs for all colors
        images = {}
        swatch_images = {}
        for color in product["catalog_colors"]:
            images[color] = get_mock_image_url(style, image_type="p110", color=color)
            swatch_images[color] = get_mock_swatch_url(style, color=color)
            
        # Create a more comprehensive product data structure
        product_data = {
            "product_name": product["product_name"],
            "product_description": product["product_description"],
            "catalog_colors": product["catalog_colors"],
            "display_colors": {color: color for color in product["catalog_colors"]},
            "sizes": product["sizes"],
            "images": images,
            "swatch_images": swatch_images,
            "price": product["price"],
            "case_size": product["case_size"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return product_data
    
    # If we don't have data for this style, return a generic mock
    else:
        logger.warning(f"No specific mock data for style {style}, creating generic mock")
        # Create a generic product with the style number
        generic_product = {
            "product_name": f"Product {style}",
            "product_description": f"Generic product description for style {style}.",
            "catalog_colors": ["Black", "Navy", "White"],
            "display_colors": {"Black": "Black", "Navy": "Navy", "White": "White"},
            "sizes": ["S", "M", "L", "XL", "2XL"],
            "images": {
                "Black": get_mock_image_url(style, image_type="p110", color="Black"),
                "Navy": get_mock_image_url(style, image_type="p110", color="Navy"),
                "White": get_mock_image_url(style, image_type="p110", color="White")
            },
            "swatch_images": {
                "Black": get_mock_swatch_url(style, color="Black"),
                "Navy": get_mock_swatch_url(style, color="Navy"),
                "White": get_mock_swatch_url(style, color="White")
            },
            "price": 15.99,
            "case_size": 24,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return generic_product

def get_mock_pricing(style):
    """
    Get mock pricing data for a specific style
    
    Args:
        style (str): Product style number
    
    Returns:
        dict: Pricing data structure
    """
    logger.info(f"Getting mock pricing data for style: {style}")
    
    # Create a default pricing structure
    pricing_data = {
        "case_price": {},
        "original_price": {},
        "sale_price": {},
        "program_price": {},
        "case_size": {}
    }
    
    # Default logic from the original app.py
    style = style.upper()
    
    # PC61 - Port & Company Essential Tee
    if style == "PC61":
        sizes = ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"]
        for size in sizes:
            if size in ["XS", "S", "M", "L", "XL"]:
                pricing_data["case_price"][size] = 3.41
                pricing_data["original_price"][size] = 3.41
                pricing_data["sale_price"][size] = 2.72
                pricing_data["program_price"][size] = 2.18
                pricing_data["case_size"][size] = 72
            else:  # 2XL and up
                pricing_data["case_price"][size] = 4.53 if size == "2XL" else 4.96
                pricing_data["original_price"][size] = 4.53 if size == "2XL" else 4.96
                pricing_data["sale_price"][size] = 3.63 if size == "2XL" else 3.97
                pricing_data["program_price"][size] = 3.17 if size == "2XL" else 3.47
                pricing_data["case_size"][size] = 36
    
    # J790 - Port Authority Glacier Soft Shell Jacket
    elif style == "J790":
        sizes = ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"]
        
        for size in sizes:
            pricing_data["case_price"][size] = 30.59
            pricing_data["original_price"][size] = 30.59
            pricing_data["sale_price"][size] = 30.59
            pricing_data["program_price"][size] = 30.59
            
            if size in ["XS", "S", "M", "L", "XL", "2XL"]:
                pricing_data["case_size"][size] = 24
            else:  # 3XL and up
                pricing_data["case_size"][size] = 12
    
    # K500 - Port Authority Silk Touch Polo
    elif style == "K500":
        sizes = ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"]
        
        for size in sizes:
            if size in ["XS", "S", "M", "L", "XL"]:
                pricing_data["case_price"][size] = 13.99
                pricing_data["original_price"][size] = 13.99
                pricing_data["sale_price"][size] = 11.19
                pricing_data["program_price"][size] = 10.07
                pricing_data["case_size"][size] = 36
            else:  # 2XL and up
                pricing_data["case_price"][size] = 15.99 if size == "2XL" else 17.99
                pricing_data["original_price"][size] = 15.99 if size == "2XL" else 17.99
                pricing_data["sale_price"][size] = 12.79 if size == "2XL" else 14.39
                pricing_data["program_price"][size] = 11.51 if size == "2XL" else 12.95
                pricing_data["case_size"][size] = 24
    
    # L500 - Port Authority Ladies Silk Touch Polo
    elif style == "L500":
        sizes = ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"]
        
        for size in sizes:
            if size in ["XS", "S", "M", "L", "XL"]:
                pricing_data["case_price"][size] = 13.99
                pricing_data["original_price"][size] = 13.99
                pricing_data["sale_price"][size] = 11.19
                pricing_data["program_price"][size] = 10.07
                pricing_data["case_size"][size] = 36
            else:  # 2XL and up
                pricing_data["case_price"][size] = 15.99 if size == "2XL" else 17.99
                pricing_data["original_price"][size] = 15.99 if size == "2XL" else 17.99
                pricing_data["sale_price"][size] = 12.79 if size == "2XL" else 14.39
                pricing_data["program_price"][size] = 11.51 if size == "2XL" else 12.95
                pricing_data["case_size"][size] = 24
    
    # Default for any other style
    else:
        # Use a few standard sizes for defaults
        sizes = ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"]
        
        for size in sizes:
            if size in ["XS", "S", "M", "L", "XL"]:
                pricing_data["case_price"][size] = 15.99
                pricing_data["original_price"][size] = 15.99
                pricing_data["sale_price"][size] = 13.99
                pricing_data["program_price"][size] = 12.99
                pricing_data["case_size"][size] = 36
            else:  # 2XL and up
                pricing_data["case_price"][size] = 17.99
                pricing_data["original_price"][size] = 17.99
                pricing_data["sale_price"][size] = 15.99
                pricing_data["program_price"][size] = 14.99
                pricing_data["case_size"][size] = 24
    
    return pricing_data

def get_mock_inventory(style):
    """
    Get mock inventory data for a specific style
    
    Args:
        style (str): Product style number
    
    Returns:
        dict: Inventory data by color and size
    """
    logger.info(f"Getting mock inventory data for style: {style}")
    
    # Get product info to get colors and sizes
    product = get_mock_product_data(style)
    
    if not product:
        logger.warning(f"No product data for style {style}, returning empty inventory")
        return {}
    
    colors = product.get("catalog_colors", [])
    sizes = product.get("sizes", [])
    
    # Create inventory data
    inventory = {}
    
    # Warehouse IDs from the original app.py
    warehouse_ids = ["1", "2", "3", "4", "5", "6", "7", "12", "31"]
    
    # Create inventory for each color and size
    for color in colors:
        inventory[color] = {}
        
        for size in sizes:
            # Generate random inventory levels for each warehouse
            import random
            
            # For main colors and common sizes, ensure good inventory
            is_main_color = color in ["Black", "Navy", "White", "Black/Chrome"]
            is_common_size = size in ["S", "M", "L", "XL"]
            
            if is_main_color and is_common_size:
                # Main colors and common sizes have good inventory
                min_qty = 50
                max_qty = 500
            elif is_main_color or is_common_size:
                # Either main color or common size has decent inventory
                min_qty = 20
                max_qty = 200
            else:
                # Other combinations might have less inventory
                min_qty = 0
                max_qty = 100
            
            # Create warehouse inventory
            warehouses = {}
            for wh_id in warehouse_ids:
                # XL sizes have more inventory in warehouse 31
                if size == "XL" and wh_id == "31":
                    warehouses[wh_id] = random.randint(min_qty*2, max_qty*2)
                else:
                    warehouses[wh_id] = random.randint(min_qty, max_qty)
            
            # Calculate total across all warehouses
            total = sum(warehouses.values())
            
            # Store inventory data
            inventory[color][size] = {
                "warehouses": warehouses,
                "total": total
            }
    
    return inventory

def get_mock_image_url(style, image_type="p110", color=None):
    """
    Generate a mock image URL for a product
    
    Args:
        style (str): Product style number
        image_type (str): Image type (p110, m110, etc.)
        color (str): Product color
    
    Returns:
        str: Image URL
    """
    logger.info(f"Getting mock image URL for style: {style}, image_type: {image_type}, color: {color}")
    
    # Base SanMar image URL
    base_url = "https://cdni.sanmar.com/catalog/images"
    
    # If style is one of our known styles, use SanMar's actual image pattern
    if style.upper() in ["PC61", "J790", "K500", "L500", "DT292", "LK5602"]:
        if color:
            # Try to use a color-specific image if available
            # In reality, SanMar's image naming is more complex, but this is a simplified version
            # Convert color to a simple format for the URL (lowercase, no spaces)
            color_slug = color.lower().replace(' ', '').replace('/', '')
            return f"{base_url}/{style.upper()}{image_type}_{color_slug}.jpg"
        else:
            # Use the default image without color
            return f"{base_url}/{style.upper()}{image_type}.jpg"
    
    # For unknown styles, use a placeholder image
    return f"{base_url}/placeholder_{style.upper()}.jpg"

def get_mock_swatch_url(style, color):
    """
    Generate a mock swatch image URL for a product color
    
    Args:
        style (str): Product style number
        color (str): Product color
    
    Returns:
        str: Swatch image URL
    """
    logger.info(f"Getting mock swatch URL for style: {style}, color: {color}")
    
    # Base SanMar swatch image URL
    base_url = "https://cdni.sanmar.com/catalog/swatches"
    
    if color:
        # Convert color to a simple format for the URL (lowercase, no spaces)
        color_slug = color.lower().replace(' ', '').replace('/', '')
        return f"{base_url}/{color_slug}.jpg"
    
    # Default swatch for unknown colors
    return f"{base_url}/black.jpg"