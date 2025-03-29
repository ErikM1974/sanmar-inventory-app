import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# SanMar API credentials
SANMAR_USERNAME = os.getenv('SANMAR_USERNAME')
SANMAR_PASSWORD = os.getenv('SANMAR_PASSWORD')

# Categories with their IDs and display names
CATEGORIES = [
    {"id": "T-SHIRTS", "name": "T-Shirts", "description": "Essential tees for every occasion"},
    {"id": "POLOS", "name": "Polos", "description": "Classic and performance polos"},
    {"id": "SWEATSHIRTS", "name": "Sweatshirts", "description": "Comfortable sweatshirts and hoodies"},
    {"id": "FLEECE", "name": "Fleece", "description": "Warm and cozy fleece options"},
    {"id": "OUTERWEAR", "name": "Outerwear", "description": "Jackets, vests and outdoor apparel"},
    {"id": "WOVEN", "name": "Woven Shirts", "description": "Button-ups and dress shirts"},
    {"id": "CAPS", "name": "Caps & Hats", "description": "Headwear for all seasons"},
    {"id": "BAGS", "name": "Bags", "description": "Totes, backpacks and travel bags"},
    {"id": "ACCESSORIES", "name": "Accessories", "description": "Essential add-ons and accessories"},
    {"id": "WORKWEAR", "name": "Workwear", "description": "Durable clothing for the job site"},
    {"id": "LADIES", "name": "Ladies", "description": "Women's styles and fits"},
    {"id": "YOUTH", "name": "Youth", "description": "Styles for kids and teens"},
    {"id": "BOTTOMS", "name": "Bottoms", "description": "Pants, shorts and skirts"},
    {"id": "ACTIVEWEAR", "name": "Activewear", "description": "Performance apparel for sports and fitness"}
]

# Brand mapping
BRAND_MAPPING = {
    "PC61": "Port & Company",
    "K500": "Port Authority",
    "PC90H": "Port & Company",
    "J790": "Port Authority",
    "ST850": "Sport-Tek",
    "C112": "Port & Company",
    "DT6000": "District",
    "L500": "Port Authority",
    "NKDC1001": "Nike",
    "NKBQ5231": "Nike",
    "DM108": "District Made",
    "PC78": "Port & Company",
    "F280": "Fruit of the Loom",
    "G500": "Gildan",
    "G200": "Gildan",
    "G180": "Gildan",
    "G800": "Gildan",
    "OE320": "OGIO",
    "OE100": "OGIO",
    "NF0A47FG": "The North Face",
    "EB200": "Eddie Bauer",
    "CS410": "CornerStone",
    "RH54": "Red House",
    "TLK110": "Carhartt",
    "NEA510": "New Era"
}

def get_categories():
    """
    Get a list of all product categories.
    
    Returns:
        list: List of category dictionaries with id, name, and description
    """
    return CATEGORIES

def get_product_brand(style):
    """
    Get the brand name for a product style.
    
    Args:
        style (str): Product style number
        
    Returns:
        str: Brand name or "SanMar" if not found
    """
    # Normalize style to uppercase
    style_upper = style.upper()
    
    # Return the brand name if found, otherwise return "SanMar"
    return BRAND_MAPPING.get(style_upper, "SanMar")