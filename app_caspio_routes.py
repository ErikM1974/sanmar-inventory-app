"""
Flask routes for the Caspio-integrated version of the SanMar Inventory App.
This module provides routes that use Caspio datapages instead of direct SanMar API calls.
"""

import os
import logging
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from caspio_client import CaspioClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Blueprint
caspio_bp = Blueprint('caspio', __name__, url_prefix='/caspio')

# Initialize Caspio client
CASPIO_BASE_URL = os.getenv('CASPIO_BASE_URL')
CASPIO_CLIENT_ID = os.getenv('CASPIO_CLIENT_ID')
CASPIO_CLIENT_SECRET = os.getenv('CASPIO_CLIENT_SECRET')
CASPIO_ACCESS_TOKEN = os.getenv('CASPIO_ACCESS_TOKEN')
CASPIO_REFRESH_TOKEN = os.getenv('CASPIO_REFRESH_TOKEN')

caspio_client = None
if CASPIO_CLIENT_ID and CASPIO_CLIENT_SECRET:
    caspio_client = CaspioClient(
        base_url=CASPIO_BASE_URL,
        client_id=CASPIO_CLIENT_ID,
        client_secret=CASPIO_CLIENT_SECRET
    )
elif CASPIO_ACCESS_TOKEN:
    caspio_client = CaspioClient(
        base_url=CASPIO_BASE_URL,
        access_token=CASPIO_ACCESS_TOKEN,
        refresh_token=CASPIO_REFRESH_TOKEN
    )
else:
    logger.warning("Caspio API credentials are not properly configured. Some features may not work.")

# Caspio DataPage IDs (replace with your actual DataPage IDs)
DATAPAGE_IDS = {
    'product_listing': '12345',
    'product_detail': '67890',
    'inventory_by_warehouse': '54321'
}

@caspio_bp.route('/')
def index():
    """Render the Caspio-integrated home page."""
    return render_template('caspio_index.html', datapage_id=DATAPAGE_IDS['product_listing'])

@caspio_bp.route('/product/<style>')
def product_detail(style):
    """Render the Caspio-integrated product detail page."""
    color = request.args.get('color', '')
    size = request.args.get('size', '')
    
    return render_template(
        'caspio_product.html',
        style=style,
        color=color,
        size=size,
        datapage_id=DATAPAGE_IDS['product_detail']
    )

@caspio_bp.route('/category/<category>')
def category(category):
    """Render the Caspio-integrated category page."""
    return render_template(
        'caspio_category.html',
        category=category,
        datapage_id=DATAPAGE_IDS['product_listing']
    )

@caspio_bp.route('/api/inventory/<style>')
def api_inventory(style):
    """API endpoint to get inventory data from Caspio."""
    if not caspio_client:
        return jsonify({'error': 'Caspio client not configured'}), 500
    
    color = request.args.get('color', '')
    size = request.args.get('size', '')
    
    try:
        # Build the query
        query = f"STYLE='{style}'"
        if color:
            query += f" AND COLOR_NAME='{color}'"
        if size:
            query += f" AND SIZE='{size}'"
        
        # Query the Inventory table
        inventory_data = caspio_client.query_records(
            'Inventory',
            where=query
        )
        
        # Process the data
        result = []
        for item in inventory_data:
            result.append({
                'style': item.get('STYLE', ''),
                'color': item.get('DISPLAY_COLOR', ''),
                'size': item.get('SIZE', ''),
                'warehouse_id': item.get('WAREHOUSE_ID', ''),
                'quantity': item.get('QUANTITY', 0)
            })
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error querying Caspio inventory: {str(e)}")
        return jsonify({'error': str(e)}), 500

@caspio_bp.route('/api/pricing/<style>')
def api_pricing(style):
    """API endpoint to get pricing data from Caspio."""
    if not caspio_client:
        return jsonify({'error': 'Caspio client not configured'}), 500
    
    color = request.args.get('color', '')
    size = request.args.get('size', '')
    
    try:
        # Build the query
        query = f"STYLE='{style}'"
        if color:
            query += f" AND COLOR_NAME='{color}'"
        if size:
            query += f" AND SIZE='{size}'"
        
        # Query the Pricing table
        pricing_data = caspio_client.query_records(
            'Pricing',
            where=query
        )
        
        # Process the data
        result = []
        for item in pricing_data:
            result.append({
                'style': item.get('STYLE', ''),
                'color': item.get('DISPLAY_COLOR', ''),
                'size': item.get('SIZE', ''),
                'piece_price': float(item.get('PIECE_PRICE', 0)),
                'case_price': float(item.get('CASE_PRICE', 0)),
                'program_price': float(item.get('PROGRAM_PRICE', 0))
            })
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error querying Caspio pricing: {str(e)}")
        return jsonify({'error': str(e)}), 500

@caspio_bp.route('/api/product/<style>')
def api_product(style):
    """API endpoint to get combined product data from Caspio."""
    if not caspio_client:
        return jsonify({'error': 'Caspio client not configured'}), 500
    
    color = request.args.get('color', '')
    size = request.args.get('size', '')
    
    try:
        # Get inventory data
        inventory_query = f"STYLE='{style}'"
        if color:
            inventory_query += f" AND COLOR_NAME='{color}'"
        if size:
            inventory_query += f" AND SIZE='{size}'"
        
        inventory_data = caspio_client.query_records(
            'Inventory',
            where=inventory_query
        )
        
        # Get pricing data
        pricing_query = f"STYLE='{style}'"
        if color:
            pricing_query += f" AND COLOR_NAME='{color}'"
        if size:
            pricing_query += f" AND SIZE='{size}'"
        
        pricing_data = caspio_client.query_records(
            'Pricing',
            where=pricing_query
        )
        
        # Create a lookup dictionary for pricing
        pricing_lookup = {}
        for item in pricing_data:
            key = f"{item.get('STYLE')}_{item.get('COLOR_NAME')}_{item.get('SIZE')}"
            pricing_lookup[key] = {
                'piece_price': float(item.get('PIECE_PRICE', 0)),
                'case_price': float(item.get('CASE_PRICE', 0)),
                'program_price': float(item.get('PROGRAM_PRICE', 0))
            }
        
        # Combine inventory and pricing data
        result = []
        for item in inventory_data:
            style = item.get('STYLE', '')
            color_name = item.get('COLOR_NAME', '')
            size = item.get('SIZE', '')
            key = f"{style}_{color_name}_{size}"
            
            pricing = pricing_lookup.get(key, {
                'piece_price': 0,
                'case_price': 0,
                'program_price': 0
            })
            
            result.append({
                'style': style,
                'color': item.get('DISPLAY_COLOR', ''),
                'size': size,
                'warehouse_id': item.get('WAREHOUSE_ID', ''),
                'quantity': item.get('QUANTITY', 0),
                'piece_price': pricing['piece_price'],
                'case_price': pricing['case_price'],
                'program_price': pricing['program_price']
            })
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error querying Caspio product data: {str(e)}")
        return jsonify({'error': str(e)}), 500

def register_caspio_routes(app):
    """Register the Caspio blueprint with the Flask app."""
    app.register_blueprint(caspio_bp)
    
    # Add a redirect from the root to the Caspio index
    @app.route('/caspio-demo')
    def caspio_demo():
        return redirect(url_for('caspio.index'))