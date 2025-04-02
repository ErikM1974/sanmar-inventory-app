"""
Customer-facing routes for Northwest Custom Apparel
"""

import os
import json
import logging
from datetime import datetime
from flask import (
    Blueprint, render_template, request, jsonify, 
    current_app, redirect, url_for, session
)

# Import mock data for testing without API connectivity
from mock_product_data import (
    get_mock_product_data,
    get_mock_pricing,
    get_mock_inventory,
    get_mock_image_url,
    get_mock_swatch_url
)

# Set up logging
logger = logging.getLogger(__name__)

# Create Blueprint for customer routes
customer_bp = Blueprint('customer', __name__)

# ===== Page Routes =====

@customer_bp.route('/')
def home():
    """Homepage route"""
    return render_template('index.html', page_title="Welcome to Northwest Custom Apparel")

@customer_bp.route('/product/<style>')
def product_detail(style):
    """Product detail page"""
    # Get product data from mock or API
    product_data = get_mock_product_data(style)
    
    if not product_data:
        return render_template('error.html', 
                              error_message=f"Product {style} not found",
                              page_title="Product Not Found")
    
    # Get pricing data
    pricing_data = get_mock_pricing(style)
    
    # Get inventory data
    inventory_data = get_mock_inventory(style)
    
    # Prepare data for template
    context = {
        'style': style,
        'product': product_data,
        'pricing': pricing_data,
        'inventory': inventory_data,
        'page_title': f"{product_data.get('product_name', style)} - Product Details"
    }
    
    return render_template('product.html', **context)
@customer_bp.route('/category/<category_name>')
def category_view(category_name):
    """Category page view with Caspio gallery integration"""
    from caspio_embed_helper import generate_category_gallery_embed
    
    # Get the Caspio embed code for the category gallery
    caspio_embed = generate_category_gallery_embed(category=category_name)
    
    # Prepare context for template
    context = {
        'category_name': category_name,
        'caspio_embed': caspio_embed,
        'page_title': f"{category_name} - Product Category"
    }
    
    return render_template('category.html', **context)

@customer_bp.route('/category/<category_name>/<subcategory_name>')
def subcategory_view(category_name, subcategory_name):
    """Subcategory page view with Caspio gallery integration"""
    from caspio_embed_helper import generate_category_gallery_embed
    
    # Get the Caspio embed code for the subcategory gallery
    caspio_embed = generate_category_gallery_embed(category=category_name, subcategory=subcategory_name)
    
    # Prepare context for template
    context = {
        'category_name': category_name,
        'subcategory_name': subcategory_name,
        'caspio_embed': caspio_embed,
        'page_title': f"{subcategory_name} - {category_name} Products"
    }
    
    return render_template('category.html', **context)

@customer_bp.route('/search')
def search_results():
    """Search results page"""
    query = request.args.get('q', '')
    
    if not query:
        return redirect(url_for('customer.home'))
    
    # In a real implementation, you'd search the product database
    # Here we'll just filter our mock data based on the query
    test_styles = ["PC61", "J790", "K500", "L500"]
    results = []
    
    for style in test_styles:
        product_data = get_mock_product_data(style)
        if product_data:
            # Check if query matches style or product name
            if (query.lower() in style.lower() or 
                query.lower() in product_data.get('product_name', '').lower()):
                
                # Add style to the product data
                product_data['style'] = style
                
                # Add a default image URL
                if 'images' in product_data and len(product_data['images']) > 0:
                    first_color = next(iter(product_data['images']))
                    product_data['image_url'] = product_data['images'][first_color]
                else:
                    product_data['image_url'] = get_mock_image_url(style)
                    
                # Add pricing
                pricing = get_mock_pricing(style)
                if pricing and 'original_price' in pricing and 'M' in pricing['original_price']:
                    # Use medium size price as default
                    product_data['price'] = pricing['original_price']['M']
                else:
                    product_data['price'] = 0.00
                    
                results.append(product_data)
    
    # Prepare context for template
    context = {
        'query': query,
        'results': results,
        'result_count': len(results),
        'page_title': f"Search Results for '{query}'"
    }
    
    return render_template('search_results.html', **context)

@customer_bp.route('/quote')
def quote_cart():
    """Quote cart page"""
    # Get quote items from session, or initialize empty
    quote_items = session.get('quote_items', [])
    
    # Calculate totals
    subtotal = sum(item.get('total', 0) for item in quote_items)
    
    # Prepare context
    context = {
        'quote_items': quote_items,
        'subtotal': subtotal,
        'page_title': "Your Quote Cart"
    }
    
    return render_template('quote_cart.html', **context)

@customer_bp.route('/mockup')
def mockup_page():
    """Mockup page for creating custom designs"""
    return render_template('mockup.html', page_title="Create Your Design")

# ===== API Routes =====

@customer_bp.route('/api/product-quick-view/<style>')
def api_product_quick_view(style):
    """API endpoint to get quick view data for a product"""
    try:
        # Get product data from mock or API
        product_data = get_mock_product_data(style)
        
        if not product_data:
            return jsonify({
                'success': False,
                'message': f"Product {style} not found"
            })
        
        # Get pricing data
        pricing_data = get_mock_pricing(style)
        
        # Prepare simplified product data for quick view
        quick_view_data = {
            'name': product_data.get('product_name', ''),
            'description': product_data.get('product_description', '')[:100] + '...',
            'colors': product_data.get('catalog_colors', []),
            'sizes': product_data.get('sizes', []),
        }
        
        # Add image URL
        if 'images' in product_data and len(product_data['images']) > 0:
            first_color = next(iter(product_data['images']))
            quick_view_data['imageUrl'] = product_data['images'][first_color]
        else:
            quick_view_data['imageUrl'] = get_mock_image_url(style)
            
        # Add pricing - use medium size price as default
        if pricing_data and 'original_price' in pricing_data and 'M' in pricing_data['original_price']:
            quick_view_data['price'] = pricing_data['original_price']['M']
        else:
            quick_view_data['price'] = 0.00
        
        return jsonify({
            'success': True,
            'product': quick_view_data
        })
        
    except Exception as e:
        logger.error(f"Error in product quick view API for {style}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error retrieving product data: {str(e)}"
        })

@customer_bp.route('/api/caspio-categories')
def api_caspio_categories():
    """API endpoint to get product categories from Caspio"""
    try:
        # Import the Caspio client
        from caspio_client import caspio_api
        
        # Get categories from Caspio
        categories_response = caspio_api.get_categories()
        
        if not categories_response:
            logger.error("Failed to get categories from Caspio API")
            # Fall back to mock data
            categories = [
                { "name": "T-Shirts", "count": 354, "url": "/customer/category/T-Shirts" },
                { "name": "Polos", "count": 187, "url": "/customer/category/Polos" },
                { "name": "Sweatshirts & Fleece", "count": 213, "url": "/customer/category/Sweatshirts" },
                { "name": "Jackets & Outerwear", "count": 178, "url": "/customer/category/Jackets" },
                { "name": "Activewear", "count": 145, "url": "/customer/category/Activewear" },
                { "name": "Workwear", "count": 92, "url": "/customer/category/Workwear" },
                { "name": "Bags", "count": 76, "url": "/customer/category/Bags" },
                { "name": "Hats & Caps", "count": 81, "url": "/customer/category/Hats" },
                { "name": "Ladies", "count": 198, "url": "/customer/category/Ladies" }
            ]
        else:
            # Process the Caspio API response
            categories = []
            for item in categories_response.get('Result', []):
                category_name = item.get('category', '')
                if category_name:
                    # Get subcategories for this category
                    subcategories_response = caspio_api.get_subcategories(category_name)
                    subcategory_count = len(subcategories_response.get('Result', [])) if subcategories_response else 0
                    
                    categories.append({
                        "name": category_name,
                        "count": subcategory_count,
                        "url": f"/customer/category/{category_name}"
                    })
        
        return jsonify({
            'success': True,
            'categories': categories
        })
        
    except Exception as e:
        logger.error(f"Error in Caspio categories API: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error retrieving categories: {str(e)}"
        })

@customer_bp.route('/api/caspio-subcategories/<category>')
def api_caspio_subcategories(category):
    """API endpoint to get subcategories for a specific category from Caspio"""
    try:
        # Import the Caspio client
        from caspio_client import caspio_api
        
        # Get subcategories from Caspio
        subcategories_response = caspio_api.get_subcategories(category)
        
        if not subcategories_response:
            logger.error(f"Failed to get subcategories for {category} from Caspio API")
            # Return empty list
            subcategories = []
        else:
            # Process the Caspio API response
            subcategories = []
            for item in subcategories_response.get('Result', []):
                subcategory_name = item.get('subcategory', '')
                if subcategory_name:
                    subcategories.append({
                        "name": subcategory_name,
                        "url": f"/customer/category/{category}/{subcategory_name}"
                    })
        
        return jsonify({
            'success': True,
            'category': category,
            'subcategories': subcategories
        })
        
    except Exception as e:
        logger.error(f"Error in Caspio subcategories API: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error retrieving subcategories: {str(e)}"
        })

@customer_bp.route('/api/product-inventory/<style>')
def api_product_inventory(style):
    """API endpoint to get inventory for a product"""
    try:
        # Get inventory data from mock or API
        inventory_data = get_mock_inventory(style)
        
        if not inventory_data:
            return jsonify({
                'success': False,
                'message': f"Inventory for {style} not found"
            })
        
        return jsonify({
            'success': True,
            'inventory': inventory_data
        })
        
    except Exception as e:
        logger.error(f"Error in product inventory API for {style}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error retrieving inventory data: {str(e)}"
        })

@customer_bp.route('/api/product-pricing/<style>')
def api_product_pricing(style):
    """API endpoint to get pricing for a product"""
    try:
        # Get pricing data from mock or API
        pricing_data = get_mock_pricing(style)
        
        if not pricing_data:
            return jsonify({
                'success': False,
                'message': f"Pricing for {style} not found"
            })
        
        return jsonify({
            'success': True,
            'pricing': pricing_data
        })
        
    except Exception as e:
        logger.error(f"Error in product pricing API for {style}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error retrieving pricing data: {str(e)}"
        })

@customer_bp.route('/api/add-to-quote', methods=['POST'])
def api_add_to_quote():
    """API endpoint to add an item to the quote cart"""
    try:
        # Get item data from request
        item_data = request.json
        
        if not item_data or not item_data.get('style'):
            return jsonify({
                'success': False,
                'message': "Invalid item data"
            })
        
        # Get quote items from session, or initialize empty
        quote_items = session.get('quote_items', [])
        
        # Add quantity if not provided
        if 'quantity' not in item_data:
            item_data['quantity'] = 1
            
        # Calculate total for this item
        if 'price' in item_data and 'quantity' in item_data:
            item_data['total'] = float(item_data['price']) * int(item_data['quantity'])
        else:
            item_data['total'] = 0
            
        # Add timestamp
        item_data['added_at'] = datetime.now().isoformat()
        
        # Generate a unique ID for this item
        item_data['id'] = f"{item_data['style']}-{len(quote_items) + 1}-{int(datetime.now().timestamp())}"
        
        # Add to quote items
        quote_items.append(item_data)
        
        # Store in session
        session['quote_items'] = quote_items
        
        return jsonify({
            'success': True,
            'message': "Item added to quote",
            'quote_items': quote_items,
            'item_count': len(quote_items)
        })
        
    except Exception as e:
        logger.error(f"Error adding to quote: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error adding to quote: {str(e)}"
        })

@customer_bp.route('/api/update-quote-item', methods=['POST'])
def api_update_quote_item():
    """API endpoint to update an item in the quote cart"""
    try:
        # Get item data from request
        update_data = request.json
        
        if not update_data or not update_data.get('id'):
            return jsonify({
                'success': False,
                'message': "Invalid update data"
            })
        
        # Get quote items from session, or initialize empty
        quote_items = session.get('quote_items', [])
        
        # Find the item to update
        for i, item in enumerate(quote_items):
            if item.get('id') == update_data.get('id'):
                # Update fields
                for key, value in update_data.items():
                    if key != 'id':  # Don't update the ID
                        quote_items[i][key] = value
                
                # Recalculate total
                if 'price' in quote_items[i] and 'quantity' in quote_items[i]:
                    quote_items[i]['total'] = float(quote_items[i]['price']) * int(quote_items[i]['quantity'])
                
                # Store in session
                session['quote_items'] = quote_items
                
                return jsonify({
                    'success': True,
                    'message': "Item updated",
                    'quote_items': quote_items,
                    'item_count': len(quote_items)
                })
        
        # Item not found
        return jsonify({
            'success': False,
            'message': "Item not found in quote"
        })
        
    except Exception as e:
        logger.error(f"Error updating quote item: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error updating quote item: {str(e)}"
        })

@customer_bp.route('/api/remove-quote-item', methods=['POST'])
def api_remove_quote_item():
    """API endpoint to remove an item from the quote cart"""
    try:
        # Get item ID from request
        item_data = request.json
        
        if not item_data or not item_data.get('id'):
            return jsonify({
                'success': False,
                'message': "Invalid item data"
            })
        
        # Get quote items from session, or initialize empty
        quote_items = session.get('quote_items', [])
        
        # Remove the item
        quote_items = [item for item in quote_items if item.get('id') != item_data.get('id')]
        
        # Store in session
        session['quote_items'] = quote_items
        
        return jsonify({
            'success': True,
            'message': "Item removed from quote",
            'quote_items': quote_items,
            'item_count': len(quote_items)
        })
        
    except Exception as e:
        logger.error(f"Error removing from quote: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error removing from quote: {str(e)}"
        })

@customer_bp.route('/api/clear-quote', methods=['POST'])
def api_clear_quote():
    """API endpoint to clear the quote cart"""
    try:
        # Clear quote items from session
        session['quote_items'] = []
        
        return jsonify({
            'success': True,
            'message': "Quote cleared",
            'quote_items': [],
            'item_count': 0
        })
        
    except Exception as e:
        logger.error(f"Error clearing quote: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error clearing quote: {str(e)}"
        })

@customer_bp.route('/api/submit-quote', methods=['POST'])
def api_submit_quote():
    """API endpoint to submit a quote"""
    try:
        # Get quote data from request
        quote_data = request.json
        
        if not quote_data:
            return jsonify({
                'success': False,
                'message': "Invalid quote data"
            })
        
        # In a real implementation, you'd save this to Caspio or database
        # Here we'll just log it and return success
        logger.info(f"Quote submitted: {json.dumps(quote_data)}")
        
        # Generate a quote ID
        quote_id = f"Q-{int(datetime.now().timestamp())}"
        
        # Clear the quote cart
        session['quote_items'] = []
        
        return jsonify({
            'success': True,
            'message': "Quote submitted successfully",
            'quoteId': quote_id
        })
        
    except Exception as e:
        logger.error(f"Error submitting quote: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error submitting quote: {str(e)}"
        })

def register_customer_routes(app):
    """Register the customer blueprint with the Flask app"""
    # Register the blueprint with the app
    app.register_blueprint(customer_bp, url_prefix='/customer')
    
    # Use app-level routes for convenience - no customer prefix
    @app.route('/')
    def home():
        return render_template('index.html', page_title="Welcome to Northwest Custom Apparel")
    
    @app.route('/product/<style>')
    def product_detail(style):
        return customer_bp.view_functions['product_detail'](style)
    
    @app.route('/search')
    def search_results():
        return customer_bp.view_functions['search_results']()
    
    @app.route('/quote')
    def quote_cart():
        return customer_bp.view_functions['quote_cart']()
    
    @app.route('/mockup')
    def mockup_page():
        return customer_bp.view_functions['mockup_page']()
    
    # Register API routes at the app level
    # API routes with direct implementation
    @app.route('/api/product-quick-view/<style>')
    def api_product_quick_view(style):
        # Mock product quick view implementation
        from flask import jsonify
        import random
        
        # Create a mock product response
        mock_data = {
            "style": style,
            "product_name": f"Sample Product {style}",
            "description": "This is a sample product description.",
            "price": round(random.uniform(10.0, 50.0), 2),
            "colors": ["Black", "Navy", "White", "Red", "Royal"],
            "image_url": f"/static/images/product-{style.lower()}.jpg"
        }
        return jsonify(mock_data)
        
    @app.route('/api/caspio-categories')
    def api_caspio_categories():
        # Mock caspio categories implementation
        from flask import jsonify
        
        # Create mock categories
        mock_categories = [
            {"id": 1, "name": "T-Shirts", "count": 42},
            {"id": 2, "name": "Polos", "count": 28},
            {"id": 3, "name": "Sweatshirts", "count": 17},
            {"id": 4, "name": "Jackets", "count": 31},
            {"id": 5, "name": "Workwear", "count": 22},
            {"id": 6, "name": "Ladies", "count": 36},
            {"id": 7, "name": "Youth", "count": 19},
            {"id": 8, "name": "Bags", "count": 15},
            {"id": 9, "name": "Hats", "count": 24}
        ]
        return jsonify({"categories": mock_categories})
        
    @app.route('/api/product-inventory/<style>')
    def api_product_inventory(style):
        # Mock inventory implementation
        from flask import jsonify
        import random
        
        # Create mock inventory data
        colors = ["Black", "Navy", "White", "Red", "Royal"]
        sizes = ["S", "M", "L", "XL", "2XL", "3XL"]
        
        inventory = {}
        for color in colors:
            inventory[color] = {}
            for size in sizes:
                inventory[color][size] = random.randint(10, 100)
        
        return jsonify({"style": style, "inventory": inventory})
        
    @app.route('/api/product-pricing/<style>')
    def api_product_pricing(style):
        # Mock pricing implementation
        from flask import jsonify
        import random
        
        # Create mock pricing data
        base_price = round(random.uniform(10.0, 30.0), 2)
        pricing = {
            "base_price": base_price,
            "quantity_breaks": [
                {"quantity": 12, "price": round(base_price * 0.95, 2)},
                {"quantity": 24, "price": round(base_price * 0.90, 2)},
                {"quantity": 48, "price": round(base_price * 0.85, 2)},
                {"quantity": 96, "price": round(base_price * 0.80, 2)},
                {"quantity": 144, "price": round(base_price * 0.75, 2)}
            ]
        }
        
        return jsonify({"style": style, "pricing": pricing})
        
    @app.route('/api/add-to-quote', methods=['POST'])
    def api_add_to_quote():
        # Mock implementation to add an item to quote
        from flask import request, jsonify
        import random
        
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
                
            # In a real implementation, we would store this in a database
            # Here we're just acknowledging receipt
            return jsonify({
                "success": True,
                "message": "Item added to quote",
                "item": data,
                "item_count": random.randint(1, 10)
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    @app.route('/api/update-quote-item', methods=['POST'])
    def api_update_quote_item():
        # Mock implementation to update a quote item
        from flask import request, jsonify
        
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
                
            # In a real implementation, we would update the item in a database
            return jsonify({
                "success": True,
                "message": "Quote item updated",
                "item": data
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    @app.route('/api/remove-quote-item', methods=['POST'])
    def api_remove_quote_item():
        # Mock implementation to remove from quote
        from flask import request, jsonify
        
        try:
            data = request.get_json()
            if not data or 'id' not in data:
                return jsonify({"error": "No item ID provided"}), 400
                
            # In a real implementation, we would remove the item from a database
            return jsonify({
                "success": True,
                "message": f"Item {data['id']} removed from quote"
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    @app.route('/api/clear-quote', methods=['POST'])
    def api_clear_quote():
        # Mock implementation to clear quote
        from flask import jsonify
        
        try:
            # In a real implementation, we would clear items from a database
            return jsonify({
                "success": True,
                "message": "Quote cleared successfully"
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    @app.route('/api/submit-quote', methods=['POST'])
    def api_submit_quote():
        # Mock implementation to submit quote
        from flask import request, jsonify
        import random
        
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
                
            # In a real implementation, we would process the quote submission
            # and potentially send emails, create records, etc.
            quote_number = "Q-" + ''.join([str(random.randint(0, 9)) for _ in range(6)])
            
            return jsonify({
                "success": True,
                "message": "Quote submitted successfully",
                "quote_number": quote_number,
                "data": data
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # Log successful registration
    logger.info("Registered customer routes")