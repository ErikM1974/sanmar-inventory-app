"""
Mock inventory data for testing when SanMar API is unavailable.
This allows the app to function and demonstrate the UI without valid credentials.
"""

import random
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Common warehouse IDs based on SanMar's distribution centers
WAREHOUSES = ["1", "2", "3", "4", "5", "6", "7", "12", "31"]

def generate_mock_inventory(style):
    """
    Generate mock inventory data for a style number
    
    Args:
        style (str): The product style number
        
    Returns:
        dict: Mock inventory data with a realistic structure
        str: Current timestamp
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Generating mock inventory data for style: {style}")
    
    # Mock product data dictionary with common colors and sizes
    product_data = {
        "PC61": {
            "colors": ["Black", "White", "Navy", "Red", "Royal", "Athletic Heather"],
            "sizes": ["S", "M", "L", "XL", "2XL", "3XL", "4XL"]
        },
        "5000": {
            "colors": ["Black", "White", "Navy", "Red", "Sport Grey", "Dark Heather"],
            "sizes": ["S", "M", "L", "XL", "2XL", "3XL"]
        },
        "K420": {
            "colors": ["Black", "Navy", "White", "Red", "Royal", "Steel Grey"],
            "sizes": ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"]
        },
        "ST850": {
            "colors": ["Black", "White", "True Navy", "True Red", "True Royal"],
            "sizes": ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"]
        },
        "PC90H": {
            "colors": ["Black", "Navy", "White", "Red", "Royal", "Orange", "Athletic Heather", "Dark Green"],
            "sizes": ["S", "M", "L", "XL", "2XL", "3XL", "4XL"]
        },
        "C112": {
            "colors": ["True Red", "Black/White", "Rich Navy/White", "Maroon/White", "Heather Grey/Rich Navy", "White/Black/Gusty Grey", "Grey Steel/ White"],
            "sizes": ["OSFA"]
        }
    }
    
    # Default colors and sizes if style not in our mock data
    default_colors = ["Black", "Navy", "White", "Red", "Grey"]
    default_sizes = ["S", "M", "L", "XL", "2XL"]
    
    # Get colors and sizes for this style or use defaults
    colors = product_data.get(style, {}).get("colors", default_colors)
    sizes = product_data.get(style, {}).get("sizes", default_sizes)
    
    # Build mock inventory data
    inventory_data = {}
    
    # Special case for C112 - always have good inventory
    if style.upper() == "C112":
        for color in colors:
            inventory_data[color] = {}
            for size in sizes:
                # Create warehouse inventory levels with higher quantities
                warehouses = {}
                total_qty = 0
                
                for wh in WAREHOUSES:
                    # Generate a higher quantity for C112
                    qty = random.randint(20, 100)
                    warehouses[wh] = qty
                    total_qty += qty
                
                inventory_data[color][size] = {
                    "warehouses": warehouses,
                    "total": total_qty
                }
        
        return inventory_data, timestamp
    
    # Regular case for other styles
    for color in colors:
        inventory_data[color] = {}
        for size in sizes:
            # Create warehouse inventory levels with some randomization
            warehouses = {}
            total_qty = 0
            
            for wh in WAREHOUSES:
                # Generate a somewhat realistic quantity
                # Popular sizes have more stock than unpopular ones
                popularity_factor = 1.0
                if size in ["M", "L", "XL"]:
                    popularity_factor = 2.0  # More stock for popular sizes
                elif size in ["4XL", "5XL"]:
                    popularity_factor = 0.3  # Less stock for uncommon sizes
                
                # Generate a random quantity with some warehouses having more stock
                base_qty = int(random.gauss(30, 15) * popularity_factor)
                qty = max(0, base_qty)  # Ensure no negative quantities
                
                # Some warehouses might be out of stock
                if random.random() < 0.2:  # 20% chance of being out of stock
                    qty = 0
                
                warehouses[wh] = qty
                total_qty += qty
            
            inventory_data[color][size] = {
                "warehouses": warehouses,
                "total": total_qty
            }
    
    return inventory_data, timestamp
