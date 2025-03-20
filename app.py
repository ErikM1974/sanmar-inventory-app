from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import json
from functools import lru_cache

# Import our simplified inventory module
import sanmar_inventory
import mock_data

# Color to hex code mapping for swatch display
COLOR_HEX_CODES = {
    "black": "#000000",
    "navy": "#000080",
    "navy blue": "#000080",
    "true navy": "#000080",
    "white": "#ffffff",
    "red": "#ff0000",
    "true red": "#ff0000",
    "royal": "#4169e1",
    "true royal": "#4169e1",
    "royal blue": "#4169e1",
    "athletic heather": "#d3d3d3",
    "sport grey": "#c0c0c0",
    "dark heather": "#606060",
    "grey": "#808080",
    "gray": "#808080",
    "light grey": "#d3d3d3",
    "steel grey": "#71797e",
    "ash": "#e6e6e6",
    "purple": "#800080",
    "green": "#008000",
    "forest green": "#228b22",
    "kelly green": "#4cbb17",
    "yellow": "#ffff00",
    "gold": "#ffd700",
    "orange": "#ffa500",
    "maroon": "#800000",
    "brown": "#8b4513",
    "pink": "#ffc0cb",
    "hot pink": "#ff69b4",
    "natural": "#f5f5dc",
    "charcoal": "#36454f",
}

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Startup environment check
if not all([os.getenv("SANMAR_USERNAME"), os.getenv("SANMAR_PASSWORD"), os.getenv("SANMAR_CUSTOMER_NUMBER")]):
    print("*" * 80)
    print("WARNING: Missing SanMar API credentials!")
    print("Please ensure environment variables are set")
    print("*" * 80)

# Warehouse mapping for display
WAREHOUSES = {
    "1": "Seattle, WA", "2": "Cincinnati, OH", "3": "Dallas, TX", "4": "Reno, NV",
    "5": "Robbinsville, NJ", "6": "Jacksonville, FL", "7": "Minneapolis, MN",
    "12": "Phoenix, AZ", "31": "Richmond, VA"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/product/<style>')
def product_page(style):
    """Product inventory page with direct API call"""
    style = style.upper()
    selected_color = request.args.get('color', '')
    
    inventory_data, timestamp = sanmar_inventory.get_inventory_by_style(style)
    
    if "error" in inventory_data:
        return render_template('error.html', 
                              error_message=f"Could not retrieve inventory data: {inventory_data['error']}",
                              style=style)
    
    colors = list(inventory_data.keys())
    if not selected_color or selected_color not in colors:
        selected_color = colors[0] if colors else ""
    
    all_sizes = set()
    for color_data in inventory_data.values():
        all_sizes.update(color_data.keys())
    sizes = sorted(list(all_sizes))
    
    # Get actual product images and color swatches from mock data or API
    images = {}
    swatch_images = {}
    
    # Try to get images from mock data first
    mock_product = mock_data.get_mock_data_for_style(style)
    if mock_product:
        if 'images' in mock_product:
            images = mock_product['images']
        
        if 'color_swatches' in mock_product:
            # Use the proper SanMar color swatch URLs
            swatch_images = mock_product['color_swatches']
        else:
            # Create color swatches directly if not in mock data
            swatch_images = {
                color: mock_data.get_color_swatch_url(style, color) 
                for color in colors
            }
    else:
        # Fallback to placeholder images
        images = {color: f"https://via.placeholder.com/300x300/f8f9fa/212529?text={style}+{color}" 
                 for color in colors}
        # Generate color swatch URLs directly
        swatch_images = {
            color: mock_data.get_color_swatch_url(style, color) 
            for color in colors
        }
    
    return render_template('product.html', 
                          style=style,
                          colors=colors,
                          sizes=sizes,
                          selected_color=selected_color,
                          inventory_data=inventory_data,
                          warehouses=WAREHOUSES,
                          images=images,
                          swatch_images=swatch_images,
                          timestamp=timestamp,
                          color_hex_codes=COLOR_HEX_CODES)

@app.route('/api/autocomplete')
def autocomplete():
    """API endpoint for style number autocomplete"""
    query = request.args.get('q', '').strip().upper()
    if not query or len(query) < 2:
        return jsonify([])
    
    # Hardcoded for now; future: integrate SanMar style catalog API
    common_styles = ["PC61", "5000", "DT6000", "ST850", "K420", "L110", 
                     "G200", "G800", "M1000", "K500", "L100", "8800", "PC55"]
    
    return jsonify([style for style in common_styles if style.startswith(query)])

@app.route('/clear-cache')
def clear_cache():
    """Clear the inventory cache"""
    sanmar_inventory.clear_inventory_cache()
    return jsonify({"status": "Cache cleared"})

if __name__ == "__main__":
    app.run(debug=True)
