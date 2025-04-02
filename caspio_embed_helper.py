"""
Helper module for generating Caspio DataPage embed codes for the Northwest Custom Apparel application.
This module provides functions to generate embed codes for Caspio DataPages based on category and subcategory filters.
"""

import os
import logging
import requests
from urllib.parse import quote

# Set up logging
logger = logging.getLogger(__name__)

# Caspio API configuration
CASPIO_API_BASE_URL = "https://c3eku948.caspio.com/rest/v2"
CASPIO_AUTH_TOKEN = os.getenv("CASPIO_AUTH_TOKEN", "sTK_RbMKwhm37ztbV5cGXjdTak4QYoS-mbL_cIPdB1Ojn-X2hELp6uyfo1pZ0CZGuwCx9gnvQiM3GLQ37CTTCnKKJVCU8MNUKYUpyvu5yOW_c5nrQzIN46gJUsHwuZAlNNfQcuAdmIpHUklwHOiutExgD2kWXhMiD1okuGyxbYD4kFUo4vY-Gt9J09dMGlDivUyKRfput_nES7kmQGj4IzvEovQo3KKlkpeCEBFQHbLDA07LkuwJD9Sky_2OX1Iu5VNGe4t0sRqA4EMnQw2lDlWqCyNTAXDYH_9Owy-1pGksM3mPWAnel6PYkp_pQICgMYGjoZVkkCX_glOdCnCsh6OGc419b7zmMGt7bIPcWM1XxvLQMNfuobEnFW-_kzM_P7n7dnxwrEjkHMEgfGKiCATTkzK_9IiRCJSFeEuIVCM")
CASPIO_TABLE_NAME = "Sanmar_Bulk_251816_Feb2024"

# Caspio DataPage IDs
CATEGORY_DATAPAGE_ID = "dp1"  # Replace with your actual DataPage ID
PRODUCT_DETAIL_DATAPAGE_ID = "dp2"  # Replace with your actual DataPage ID

def test_caspio_api_connection():
    """Test the connection to the Caspio API by fetching a small amount of data."""
    try:
        url = f"{CASPIO_API_BASE_URL}/tables/{CASPIO_TABLE_NAME}/records?q.limit=2"
        headers = {
            "accept": "application/json",
            "Authorization": f"bearer {CASPIO_AUTH_TOKEN}"
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            logger.info("Successfully connected to Caspio API")
            return True, response.json()
        else:
            logger.error(f"Failed to connect to Caspio API: {response.status_code} - {response.text}")
            return False, None
    except Exception as e:
        logger.error(f"Error connecting to Caspio API: {str(e)}")
        return False, None

def get_categories_from_caspio():
    """Fetch unique categories from the Caspio database."""
    try:
        url = f"{CASPIO_API_BASE_URL}/tables/{CASPIO_TABLE_NAME}/records?q.select=CATEGORY_NAME&q.distinct=true&q.limit=100"
        headers = {
            "accept": "application/json",
            "Authorization": f"bearer {CASPIO_AUTH_TOKEN}"
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            categories = [item["CATEGORY_NAME"] for item in response.json().get("Result", [])]
            return categories
        else:
            logger.error(f"Failed to fetch categories: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        return []

def get_subcategories_for_category(category):
    """Fetch unique subcategories for a specific category from the Caspio database."""
    try:
        encoded_category = quote(category)
        url = f"{CASPIO_API_BASE_URL}/tables/{CASPIO_TABLE_NAME}/records?q.where=CATEGORY_NAME='{encoded_category}'&q.select=SUBCATEGORY_NAME&q.distinct=true&q.limit=100"
        headers = {
            "accept": "application/json",
            "Authorization": f"bearer {CASPIO_AUTH_TOKEN}"
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            subcategories = [item["SUBCATEGORY_NAME"] for item in response.json().get("Result", [])]
            return subcategories
        else:
            logger.error(f"Failed to fetch subcategories: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        logger.error(f"Error fetching subcategories: {str(e)}")
        return []

def generate_category_gallery_embed(category=None, subcategory=None):
    """
    Generate the Caspio DataPage embed code for a category or subcategory gallery.
    
    Args:
        category (str, optional): The category name to filter by. Defaults to None.
        subcategory (str, optional): The subcategory name to filter by. Defaults to None.
        
    Returns:
        str: HTML embed code for the Caspio DataPage
    """
    # Test the API connection first
    connection_success, _ = test_caspio_api_connection()
    if not connection_success:
        logger.error("Cannot generate embed code due to Caspio API connection failure")
        return "<div class='alert alert-danger'>Unable to connect to product database. Please try again later.</div>"
    
    # Base embed code template
    embed_template = """
    <div class="caspio-container">
        <script type="text/javascript" src="https://c3eku948.caspio.com/dp/{datapage_id}?{params}"></script>
    </div>
    """
    
    # Determine which DataPage to use and what parameters to pass
    datapage_id = CATEGORY_DATAPAGE_ID
    params = []
    
    if category:
        params.append(f"category={quote(category)}")
    
    if subcategory:
        params.append(f"subcategory={quote(subcategory)}")
        
    # Join parameters with &
    param_string = "&".join(params)
    
    # Generate the final embed code
    embed_code = embed_template.format(
        datapage_id=datapage_id,
        params=param_string
    )
    
    return embed_code

def generate_product_detail_embed(style=None, color=None):
    """
    Generate the Caspio DataPage embed code for a product detail page.
    
    Args:
        style (str, optional): The product style to display. Defaults to None.
        color (str, optional): The product color to filter by. Defaults to None.
        
    Returns:
        str: HTML embed code for the Caspio DataPage
    """
    # Test the API connection first
    connection_success, _ = test_caspio_api_connection()
    if not connection_success:
        logger.error("Cannot generate embed code due to Caspio API connection failure")
        return "<div class='alert alert-danger'>Unable to connect to product database. Please try again later.</div>"
    
    # Base embed code template
    embed_template = """
    <div class="caspio-container">
        <script type="text/javascript" src="https://c3eku948.caspio.com/dp/{datapage_id}?{params}"></script>
    </div>
    """
    
    # Determine which DataPage to use and what parameters to pass
    datapage_id = PRODUCT_DETAIL_DATAPAGE_ID
    params = []
    
    if style:
        params.append(f"style={quote(style)}")
    
    if color:
        params.append(f"color={quote(color)}")
        
    # Join parameters with &
    param_string = "&".join(params)
    
    # Generate the final embed code
    embed_code = embed_template.format(
        datapage_id=datapage_id,
        params=param_string
    )
    
    return embed_code

# Test the connection when the module is imported
if __name__ == "__main__":
    success, data = test_caspio_api_connection()
    if success:
        print("Successfully connected to Caspio API")
        print(f"Sample data: {data}")
    else:
        print("Failed to connect to Caspio API")