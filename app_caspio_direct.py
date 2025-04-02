#!/usr/bin/env python
"""
Flask routes for direct integration with Caspio Sanmar_Bulk_251816_Feb2024 table.
This module provides routes that query the Sanmar_Bulk table directly,
eliminating the need for a separate Products table.
"""

import os
import logging
from flask import Blueprint, render_template, request, jsonify, abort
from caspio_client import CaspioClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Caspio client
CASPIO_BASE_URL = os.getenv('CASPIO_BASE_URL')
CASPIO_ACCESS_TOKEN = os.getenv('CASPIO_ACCESS_TOKEN')

caspio_client = CaspioClient(
    base_url=CASPIO_BASE_URL,
    access_token=CASPIO_ACCESS_TOKEN
)

# Create Blueprint
caspio_direct_bp = Blueprint('caspio_direct', __name__)

@caspio_direct_bp.route('/categories')
def categories():
    """Display all product categories."""
    try:
        # Query distinct categories from Sanmar_Bulk table
        params = {
            'q.select': 'CATEGORY_NAME',
            'q.distinct': 'true',
            'q.sort': 'CATEGORY_NAME'
        }
        response = caspio_client.make_api_request(
            f"rest/v2/tables/Sanmar_Bulk_251816_Feb2024/records", 
            params=params
        )
        
        if not response or 'Result' not in response:
            logger.error("Failed to get categories from Caspio.")
            categories = []
        else:
            categories = [item['CATEGORY_NAME'] for item in response['Result']]
        
        return render_template('categories.html', categories=categories)
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        return render_template('error.html', error=str(e))

@caspio_direct_bp.route('/subcategories/<category_name>')
def subcategories(category_name):
    """Display subcategories for a specific category."""
    try:
        # Query distinct subcategories for the specified category
        params = {
            'q.select': 'SUBCATEGORY_NAME',
            'q.where': f"CATEGORY_NAME='{category_name}'",
            'q.distinct': 'true',
            'q.sort': 'SUBCATEGORY_NAME'
        }
        response = caspio_client.make_api_request(
            f"rest/v2/tables/Sanmar_Bulk_251816_Feb2024/records",
            params=params
        )
        
        if not response or 'Result' not in response:
            logger.error(f"Failed to get subcategories for category '{category_name}' from Caspio.")
            subcategories = []
        else:
            subcategories = [item['SUBCATEGORY_NAME'] for item in response['Result']]
        
        return render_template('subcategories.html', category=category_name, subcategories=subcategories)
    except Exception as e:
        logger.error(f"Error getting subcategories for category '{category_name}': {str(e)}")
        return render_template('error.html', error=str(e))

@caspio_direct_bp.route('/category/<category_name>')
@caspio_direct_bp.route('/category/<category_name>/subcategory/<subcategory_name>')
def category_detail(category_name, subcategory_name=None):
    """Display products in a specific category and optional subcategory."""
    try:
        # Build the where clause based on whether subcategory is provided
        if subcategory_name:
            where_clause = f"CATEGORY_NAME='{category_name}' AND SUBCATEGORY_NAME='{subcategory_name}'"
        else:
            where_clause = f"CATEGORY_NAME='{category_name}'"
        
        # Query products for the specified category and subcategory
        params = {
            'q.where': where_clause,
            'q.select': 'STYLE,PRODUCT_TITLE,BRAND_NAME,FRONT_MODEL,SUBCATEGORY_NAME',
            'q.distinct': 'true',
            'q.sort': 'PRODUCT_TITLE'
        }
        response = caspio_client.make_api_request(
            f"rest/v2/tables/Sanmar_Bulk_251816_Feb2024/records",
            params=params
        )
        
        if not response or 'Result' not in response:
            logger.error(f"Failed to get products for category '{category_name}'{' and subcategory ' + subcategory_name if subcategory_name else ''} from Caspio.")
            products = []
        else:
            products = response['Result']
            
            # Rename fields to match expected template variables
            for product in products:
                product['PRODUCT_IMAGE_URL'] = product.get('FRONT_MODEL', '')
        
        return render_template(
            'category_detail.html',
            category=category_name,
            subcategory=subcategory_name,
            products=products
        )
    except Exception as e:
        logger.error(f"Error getting products for category '{category_name}': {str(e)}")
        return render_template('error.html', error=str(e))

@caspio_direct_bp.route('/product/<style>')
def product_detail(style):
    """Display detailed information for a specific product."""
    try:
        # Query product details
        params = {
            'q.where': f"STYLE='{style}'",
            'q.sort': 'COLOR_NAME,SIZE_INDEX'
        }
        response = caspio_client.make_api_request(
            f"rest/v2/tables/Sanmar_Bulk_251816_Feb2024/records", 
            params=params
        )
        
        if not response or 'Result' not in response or not response['Result']:
            logger.error(f"Product '{style}' not found.")
            return abort(404)
        
        products = response['Result']
        
        # Group products by color
        colors = {}
        for product in products:
            color = product.get('COLOR_NAME', 'Unknown')
            if color not in colors:
                colors[color] = []
            colors[color].append(product)
        
        # Get basic product info from the first item
        first_product = products[0]
        product_info = {
            'STYLE': first_product.get('STYLE', ''),
            'PRODUCT_TITLE': first_product.get('PRODUCT_TITLE', ''),
            'BRAND_NAME': first_product.get('BRAND_NAME', ''),
            'BRAND_LOGO_IMAGE': first_product.get('BRAND_LOGO_IMAGE', ''),
            'CATEGORY_NAME': first_product.get('CATEGORY_NAME', ''),
            'SUBCATEGORY_NAME': first_product.get('SUBCATEGORY_NAME', ''),
            'PRODUCT_DESCRIPTION': first_product.get('PRODUCT_DESCRIPTION', '')
        }
        
        return render_template(
            'product_detail.html', 
            product=product_info, 
            colors=colors
        )
    except Exception as e:
        logger.error(f"Error getting product '{style}': {str(e)}")
        return render_template('error.html', error=str(e))

@caspio_direct_bp.route('/api/inventory/<style>/<color>/<size>')
def api_inventory(style, color, size):
    """API endpoint to get inventory information for a specific product variation."""
    try:
        # Query inventory data
        params = {
            'q.where': f"STYLE='{style}' AND COLOR_NAME='{color}' AND SIZE='{size}'",
            'q.select': 'QTY'
        }
        response = caspio_client.make_api_request(
            f"rest/v2/tables/Sanmar_Bulk_251816_Feb2024/records", 
            params=params
        )
        
        if not response or 'Result' not in response or not response['Result']:
            return jsonify({'inventory': 0})
        
        # Sum up inventory across all records
        total_inventory = sum(int(item.get('QTY', 0)) for item in response['Result'])
        
        return jsonify({'inventory': total_inventory})
    except Exception as e:
        logger.error(f"Error getting inventory for '{style}' in color '{color}' and size '{size}': {str(e)}")
        return jsonify({'error': str(e)}), 500

@caspio_direct_bp.route('/search')
def search():
    """Search for products."""
    query = request.args.get('q', '')
    if not query:
        return render_template('search.html', products=[], query='')
    
    try:
        # Search for products matching the query
        where_clause = f"STYLE LIKE '%{query}%' OR PRODUCT_TITLE LIKE '%{query}%' OR BRAND_NAME LIKE '%{query}%' OR KEYWORDS LIKE '%{query}%'"
        params = {
            'q.where': where_clause,
            'q.select': 'STYLE,PRODUCT_TITLE,BRAND_NAME,FRONT_MODEL,COLOR_NAME',
            'q.distinct': 'true',
            'q.sort': 'PRODUCT_TITLE',
            'q.limit': 100
        }
        response = caspio_client.make_api_request(
            f"rest/v2/tables/Sanmar_Bulk_251816_Feb2024/records", 
            params=params
        )
        
        if not response or 'Result' not in response:
            logger.error(f"Failed to search for products with query '{query}'.")
            products = []
        else:
            products = response['Result']
            
            # Rename fields to match expected template variables
            for product in products:
                product['PRODUCT_IMAGE_URL'] = product.get('FRONT_MODEL', '')
        
        return render_template('search.html', products=products, query=query)
    except Exception as e:
        logger.error(f"Error searching for products with query '{query}': {str(e)}")
        return render_template('error.html', error=str(e))

def register_caspio_direct_routes(app):
    """Register the blueprint with the Flask app."""
    app.register_blueprint(caspio_direct_bp)
    logger.info("Registered Caspio Direct routes.")

if __name__ == "__main__":
    # This is for testing the routes directly
    from flask import Flask
    app = Flask(__name__)
    register_caspio_direct_routes(app)
    app.run(debug=True)