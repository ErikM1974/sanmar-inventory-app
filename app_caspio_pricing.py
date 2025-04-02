#!/usr/bin/env python
"""
Flask routes for integrating Sanmar_Bulk, Inventory, and Pricing data from Caspio.
This module provides routes that query the three tables and combine the data for display.
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
caspio_pricing_bp = Blueprint('caspio_pricing', __name__)

@caspio_pricing_bp.route('/product/<style>')
def product_detail(style):
    """Display detailed information for a specific product, including inventory and pricing."""
    try:
        # Step 1: Get product information from Sanmar_Bulk table
        product_params = {
            'q.where': f"STYLE='{style}'",
            'q.distinct': 'true',
            'q.limit': 1
        }
        product_response = caspio_client.make_api_request(
            f"rest/v2/tables/Sanmar_Bulk_251816_Feb2024/records", 
            params=product_params
        )
        
        if not product_response or 'Result' not in product_response or not product_response['Result']:
            logger.error(f"Product '{style}' not found.")
            return abort(404)
        
        product_info = product_response['Result'][0]
        
        # Step 2: Get color and size variations from Sanmar_Bulk table
        variations_params = {
            'q.where': f"STYLE='{style}'",
            'q.select': 'COLOR_NAME,SIZE,FRONT_MODEL,COLOR_SQUARE_IMAGE',
            'q.sort': 'COLOR_NAME,SIZE'
        }
        variations_response = caspio_client.make_api_request(
            f"rest/v2/tables/Sanmar_Bulk_251816_Feb2024/records", 
            params=variations_params
        )
        
        if not variations_response or 'Result' not in variations_response:
            logger.error(f"Failed to get variations for product '{style}'.")
            variations = []
        else:
            variations = variations_response['Result']
        
        # Step 3: Get inventory data from Inventory table
        inventory_params = {
            'q.where': f"STYLE='{style}'",
            'q.select': 'COLOR_NAME,SIZE,WAREHOUSE_ID,QUANTITY,LAST_UPDATED'
        }
        inventory_response = caspio_client.make_api_request(
            f"rest/v2/tables/Inventory/records", 
            params=inventory_params
        )
        
        if not inventory_response or 'Result' not in inventory_response:
            logger.error(f"Failed to get inventory for product '{style}'.")
            inventory = []
        else:
            inventory = inventory_response['Result']
        
        # Step 4: Get pricing data from Pricing table
        pricing_params = {
            'q.where': f"STYLE='{style}'",
            'q.select': 'COLOR_NAME,SIZE,PIECE_PRICE,CASE_PRICE,CASE_SIZE,PROGRAM_PRICE,LAST_UPDATED'
        }
        pricing_response = caspio_client.make_api_request(
            f"rest/v2/tables/Pricing/records", 
            params=pricing_params
        )
        
        if not pricing_response or 'Result' not in pricing_response:
            logger.error(f"Failed to get pricing for product '{style}'.")
            pricing = []
        else:
            pricing = pricing_response['Result']
        
        # Step 5: Organize the data for display
        # Group variations by color
        colors = {}
        for variation in variations:
            color_name = variation['COLOR_NAME']
            if color_name not in colors:
                colors[color_name] = {
                    'name': color_name,
                    'image': variation.get('COLOR_SQUARE_IMAGE', ''),
                    'sizes': [],
                    'front_model': variation.get('FRONT_MODEL', '')
                }
            
            # Add size to this color
            colors[color_name]['sizes'].append(variation['SIZE'])
        
        # Create inventory lookup dictionary
        inventory_lookup = {}
        for inv in inventory:
            key = f"{inv['COLOR_NAME']}_{inv['SIZE']}"
            if key not in inventory_lookup:
                inventory_lookup[key] = {}
            
            # Add warehouse inventory
            inventory_lookup[key][inv['WAREHOUSE_ID']] = inv['QUANTITY']
        
        # Create pricing lookup dictionary
        pricing_lookup = {}
        for price in pricing:
            key = f"{price['COLOR_NAME']}_{price['SIZE']}"
            pricing_lookup[key] = {
                'piece_price': price['PIECE_PRICE'],
                'case_price': price['CASE_PRICE'],
                'case_size': price['CASE_SIZE'],
                'program_price': price['PROGRAM_PRICE']
            }
        
        # Combine all data
        for color_name, color_data in colors.items():
            for i, size in enumerate(color_data['sizes']):
                key = f"{color_name}_{size}"
                
                # Add inventory data
                if key in inventory_lookup:
                    colors[color_name]['sizes'][i] = {
                        'name': size,
                        'inventory': inventory_lookup[key]
                    }
                else:
                    colors[color_name]['sizes'][i] = {
                        'name': size,
                        'inventory': {}
                    }
                
                # Add pricing data
                if key in pricing_lookup:
                    colors[color_name]['sizes'][i]['pricing'] = pricing_lookup[key]
                else:
                    colors[color_name]['sizes'][i]['pricing'] = {
                        'piece_price': 0,
                        'case_price': 0,
                        'case_size': 0,
                        'program_price': 0
                    }
        
        # Render the template with all the data
        return render_template(
            'product_detail_with_pricing.html',
            product=product_info,
            colors=colors
        )
    except Exception as e:
        logger.error(f"Error getting product '{style}': {str(e)}")
        return render_template('error.html', error=str(e))

@caspio_pricing_bp.route('/api/inventory/<style>/<color>/<size>')
def api_inventory(style, color, size):
    """API endpoint to get inventory and pricing information for a specific product variation."""
    try:
        # Get inventory data
        inventory_params = {
            'q.where': f"STYLE='{style}' AND COLOR_NAME='{color}' AND SIZE='{size}'",
            'q.select': 'WAREHOUSE_ID,QUANTITY'
        }
        inventory_response = caspio_client.make_api_request(
            f"rest/v2/tables/Inventory/records", 
            params=inventory_params
        )
        
        # Get pricing data
        pricing_params = {
            'q.where': f"STYLE='{style}' AND COLOR_NAME='{color}' AND SIZE='{size}'",
            'q.select': 'PIECE_PRICE,CASE_PRICE,CASE_SIZE,PROGRAM_PRICE'
        }
        pricing_response = caspio_client.make_api_request(
            f"rest/v2/tables/Pricing/records", 
            params=pricing_params
        )
        
        # Prepare the response
        result = {
            'style': style,
            'color': color,
            'size': size,
            'inventory': {},
            'pricing': {}
        }
        
        # Add inventory data
        if inventory_response and 'Result' in inventory_response and inventory_response['Result']:
            for inv in inventory_response['Result']:
                result['inventory'][inv['WAREHOUSE_ID']] = inv['QUANTITY']
            
            # Calculate total inventory
            result['total_inventory'] = sum(result['inventory'].values())
        else:
            result['total_inventory'] = 0
        
        # Add pricing data
        if pricing_response and 'Result' in pricing_response and pricing_response['Result']:
            pricing = pricing_response['Result'][0]
            result['pricing'] = {
                'piece_price': pricing['PIECE_PRICE'],
                'case_price': pricing['CASE_PRICE'],
                'case_size': pricing['CASE_SIZE'],
                'program_price': pricing['PROGRAM_PRICE']
            }
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting inventory and pricing for '{style}' in color '{color}' and size '{size}': {str(e)}")
        return jsonify({'error': str(e)}), 500

def register_caspio_pricing_routes(app):
    """Register the blueprint with the Flask app."""
    app.register_blueprint(caspio_pricing_bp)
    logger.info("Registered Caspio Pricing routes.")

if __name__ == "__main__":
    # This is for testing the routes directly
    from flask import Flask
    app = Flask(__name__)
    register_caspio_pricing_routes(app)
    app.run(debug=True)