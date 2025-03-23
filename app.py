from flask import Flask, render_template, jsonify, request, redirect, url_for
import zeep
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import logging
from mock_data import get_mock_inventory, WAREHOUSES, COMMON_STYLES
from middleware_client import fetch_autocomplete

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Sanmar API credentials from environment variables
USERNAME = os.getenv("SANMAR_USERNAME")
PASSWORD = os.getenv("SANMAR_PASSWORD")
CUSTOMER_NUMBER = os.getenv("SANMAR_CUSTOMER_NUMBER")

# Check if credentials are set (but don't raise error - use mock data instead)
HAS_CREDENTIALS = all([USERNAME, PASSWORD, CUSTOMER_NUMBER])
if not HAS_CREDENTIALS:
    logger.warning("SanMar API credentials not set in .env file. Using mock data.")

# SOAP clients for Sanmar APIs
product_wsdl = "https://ws.sanmar.com:8080/SanMarWebService/SanMarProductInfoServicePort?wsdl"
inventory_wsdl = "https://ws.sanmar.com:8080/promostandards/InventoryServiceBindingV2final?WSDL"
pricing_wsdl = "https://ws.sanmar.com:8080/promostandards/PricingAndConfigurationServiceBinding?WSDL"

# Create SOAP clients only if credentials are set
if HAS_CREDENTIALS:
    try:
        product_client = zeep.Client(wsdl=product_wsdl)
        inventory_client = zeep.Client(wsdl=inventory_wsdl)
        pricing_client = zeep.Client(wsdl=pricing_wsdl)
        logger.info("Successfully initialized SOAP clients")
    except Exception as e:
        logger.error(f"Error initializing SOAP clients: {str(e)}")
        HAS_CREDENTIALS = False  # Fallback to mock data if client initialization fails

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/autocomplete')
def autocomplete():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    # Try to get autocomplete data from middleware
    results = fetch_autocomplete(query)
    
    # If middleware fails, use mock data
    if not results:
        # Filter common styles that match the query
        results = [style for style in COMMON_STYLES if query.lower() in style.lower()]
        
    return jsonify(results)

@app.route('/product')
def product_redirect():
    style = request.args.get('style', '')
    if not style:
        return redirect(url_for('index'))
    return redirect(url_for('product_page', style=style))

@app.route('/product/<style>')
def product_page(style):
    try:
        # Setup warehouse dictionary for template
        warehouse_dict = {}
        for wh_id, wh_name in WAREHOUSES.items():
            warehouse_dict[wh_id] = {"id": wh_id, "name": wh_name}
        
        # Default pricing data
        pricing_data = {
            "original_price": {
                "XS": 15.06, "S": 15.06, "M": 15.06, "L": 15.06,
                "XL": 15.06, "2XL": 17.36, "3XL": 19.46, "4XL": 19.46
            },
            "sale_price": {
                "XS": 14.29, "S": 14.29, "M": 14.29, "L": 14.29,
                "XL": 14.29, "2XL": 13.92, "3XL": 14.87, "4XL": 14.87
            },
            "program_price": {
                "XS": 11.03, "S": 11.03, "M": 11.03, "L": 11.03,
                "XL": 11.03, "2XL": 13.92, "3XL": 14.87, "4XL": 14.87
            },
            "case_size": {
                "XS": 24, "S": 24, "M": 24, "L": 24,
                "XL": 24, "2XL": 12, "3XL": 12, "4XL": 12
            }
        }
        
        # Try to get data from SanMar API if credentials are set
        if HAS_CREDENTIALS:
            logger.info(f"Attempting to fetch data from SanMar API for style: {style}")
            try:
                # Get product data
                product_data = get_product_data(style)
                if product_data:
                    logger.info(f"Successfully retrieved product data for {style}")
                    
                    # Create a mapping from catalog color codes to display names
                    color_mapping = {}
                    if 'listResponse' in product_data:
                        for item in product_data['listResponse']:
                            if isinstance(item, dict) and 'productBasicInfo' in item:
                                basic_info = item['productBasicInfo']
                                if 'catalogColor' in basic_info and 'color' in basic_info:
                                    catalog_color = basic_info['catalogColor']
                                    display_color = basic_info['color']
                                    color_mapping[catalog_color] = display_color
                    
                    # Get inventory data
                    inventory_data = get_inventory(style)
                    if inventory_data:
                        logger.info(f"Successfully retrieved inventory data for {style}")
                        
                        # Get pricing data
                        pricing_result = get_pricing(style)
                        if pricing_result:
                            logger.info(f"Successfully retrieved pricing data for {style}")
                            
                            # Ensure all colors in inventory_data are using display names
                            # This is a safety check in case any catalog color codes slipped through
                            safe_inventory_data = {}
                            for color_key in inventory_data:
                                # If this is a catalog color code, try to map it to a display name
                                display_color = color_mapping.get(color_key, color_key)
                                safe_inventory_data[display_color] = inventory_data[color_key]
                            
                            # Replace the inventory_data with the safe version
                            inventory_data = safe_inventory_data
                            
                            # Convert pricing data to the format expected by the template
                            api_pricing_data = {}
                            
                            # Process pricing data from API
                            if pricing_result:
                                # Initialize pricing data structure
                                api_pricing_data = {
                                    "original_price": {},
                                    "sale_price": {},
                                    "program_price": {},
                                    "case_size": {}
                                }
                                
                                # Map part IDs to sizes
                                part_id_to_size = {}
                                if product_data and 'part_id_map' in product_data:
                                    for color, sizes in product_data['part_id_map'].items():
                                        for size, part_id in sizes.items():
                                            part_id_to_size[part_id] = size
                                
                                # Process each part's pricing
                                for part_id, price_info in pricing_result.items():
                                    # Skip if price_info is not a dictionary
                                    if not isinstance(price_info, dict):
                                        continue
                                        
                                    size = part_id_to_size.get(part_id, "Unknown")
                                    
                                    api_pricing_data["original_price"][size] = price_info.get("original", 0)
                                    api_pricing_data["sale_price"][size] = price_info.get("sale", 0)
                                    api_pricing_data["program_price"][size] = price_info.get("program", 0)
                                    api_pricing_data["case_size"][size] = price_info.get("case_size", 72)
                                
                                # Use API pricing data if available
                                if any(api_pricing_data["original_price"]):
                                    pricing_data = api_pricing_data
                                    logger.info(f"Using API pricing data for {style}")
                                else:
                                    logger.warning(f"API pricing data is empty, using default pricing data")
                        # Setup data for template
                        return render_template('product.html',
                                            style=style,
                                            product_name=product_data.get('product_name', style),
                                            product_description=product_data.get('product_description', ''),
                                            colors=product_data.get('colors', []),
                                            sizes=product_data.get('sizes', []),
                                            inventory=inventory_data,
                                            warehouses=warehouse_dict,
                                            pricing=pricing_data,
                                            images=product_data.get('images', {}),
                                            swatch_images=product_data.get('swatch_images', {}),
                                            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            except Exception as e:
                logger.error(f"Error fetching data from SanMar API: {str(e)}")
                logger.warning(f"Falling back to mock data for {style}")
        
        # Fallback to mock data if API call fails or credentials not set
        logger.info(f"Using mock data for style: {style}")
        
        try:
            # Import the function here to avoid circular imports
            from mock_data import get_mock_inventory
            mock_data = get_mock_inventory(style)
            
            # Setup data for template with mock data
            return render_template('product.html',
                                style=style,
                                product_name=f"Port Authority {style}",
                                product_description="An enduring favorite, our comfortable classic polo is anything but ordinary. With superior wrinkle and shrink resistance, a silky soft hand and an incredible range of styles, sizes and colors.",
                                colors=mock_data.get('colors', []),
                                sizes=mock_data.get('sizes', []),
                                inventory=mock_data.get('inventory', {}),
                                warehouses=warehouse_dict,
                                pricing=pricing_data,
                                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        except Exception as e:
            logger.error(f"Error using mock data: {str(e)}")
            # If mock data fails, return a minimal template with default data
            return render_template('product.html',
                                style=style,
                                product_name=f"Port Authority {style}",
                                product_description="Product information not available.",
                                colors=["Black", "Navy", "White"],
                                sizes=["S", "M", "L", "XL", "2XL"],
                                inventory={},
                                warehouses=warehouse_dict,
                                pricing=pricing_data,
                                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    except Exception as e:
        logger.error(f"Error processing product page: {str(e)}")
        return render_template('error.html', 
                            style=style,
                            message=f"Error retrieving product data: {str(e)}"), 500

def get_product_data(style):
    """Get product data from SanMar API for a given style."""
    logger.info(f"Fetching product data for style: {style}")
    
    request_data = {
        "arg0": {"style": style, "color": "", "size": ""},
        "arg1": {"sanMarCustomerNumber": CUSTOMER_NUMBER, 
                 "sanMarUserName": USERNAME,
                 "sanMarUserPassword": PASSWORD}
    }
    
    try:
        response = product_client.service.getProductInfoByStyleColorSize(**request_data)
        
        # Log the response for debugging
        logger.info(f"API response received for style: {style}")
        logger.info(f"Response has errorOccured: {response.errorOccured}")
        if hasattr(response, 'message'):
            logger.info(f"Response message: {response.message}")
            
        # Log the entire response structure
        logger.info(f"Response type: {type(response)}")
        logger.info(f"Response dir: {dir(response)}")
        
        # Try to log the entire response as a string
        try:
            import json
            from zeep.helpers import serialize_object
            response_dict = serialize_object(response)
            logger.info(f"Response dict: {json.dumps(response_dict, indent=2)}")
        except Exception as e:
            logger.error(f"Error serializing response: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Check for error
        if response.errorOccured:
            logger.error(f"API error: {response.message}")
            return None
        
        # Check if listResponse exists
        if not hasattr(response, 'listResponse'):
            logger.error("No listResponse in API response")
            logger.info(f"Response attributes: {dir(response)}")
            return None
            
        # Process the response
        if isinstance(response.listResponse, list) and len(response.listResponse) > 0:
            logger.info(f"listResponse is a list with {len(response.listResponse)} items")
            # Extract product info from the response
            colors = set()
            sizes = set()
            part_id_map = {}
            images = {}
            swatch_images = {}
            product_name = ""
            product_description = ""
            product_description = ""
            
            # Process each item in the listResponse
            for item in response.listResponse:
                if hasattr(item, 'productBasicInfo'):
                    basic_info = item.productBasicInfo
                    
                    # Get product name and description from the first item
                    if not product_name and hasattr(basic_info, 'productTitle'):
                        product_name = basic_info.productTitle
                    
                    if not product_description and hasattr(basic_info, 'productDescription'):
                        product_description = basic_info.productDescription
                    
                    # Extract color and size
                    if hasattr(basic_info, 'catalogColor') and hasattr(basic_info, 'size'):
                        color = basic_info.catalogColor
                        size = basic_info.size
                        colors.add(color)
                        sizes.add(size)
                        
                        # Extract part ID
                        if hasattr(basic_info, 'uniqueKey'):
                            part_id = basic_info.uniqueKey
                            
                            if color not in part_id_map:
                                part_id_map[color] = {}
                            
                            part_id_map[color][size] = part_id
                        # Extract images
                        if hasattr(item, 'productImageInfo') and color not in images:
                            image_info = item.productImageInfo
                            if hasattr(image_info, 'colorProductImage'):
                                images[color] = image_info.colorProductImage
                            # Extract color swatch image
                            if hasattr(image_info, 'colorSquareImage'):
                                swatch_images[color] = image_info.colorSquareImage
                                logger.info(f"Added swatch image for {color}: {image_info.colorSquareImage}")
                                images[color] = image_info.colorProductImage
            
            # Convert sets to lists
            colors = list(colors)
            sizes = sorted(list(sizes))
            
            logger.info(f"Extracted {len(colors)} colors and {len(sizes)} sizes")
            
            # Create the product data structure
            product_data = {
                'colors': colors,
                'sizes': sizes,
                'part_id_map': part_id_map,
                'images': images,
                'swatch_images': swatch_images,
                'product_name': product_name,
                'product_description': product_description,
                '_raw_items': response.listResponse  # Store the raw response for later use
            }
            
            return product_data
        else:
            logger.error("listResponse is empty or not a list")
            return None
    except Exception as e:
        logger.error(f"Error fetching product data: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None

def get_inventory(style, color=None, size=None):
    """Get inventory data from SanMar API for a given style, color, and size."""
    logger.info(f"Fetching inventory data for style: {style}, color: {color}, size: {size}")
    
    try:
        # Create a new SOAP client for the SanMar Product Inventory Service
        product_inventory_wsdl = "https://ws.sanmar.com:8080/SanMarWebService/SanMarWebServicePort?wsdl"
        
        # Configure retry strategy and transport
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
        transport = Transport(timeout=10)
        transport.session.mount('https://', HTTPAdapter(max_retries=retry_strategy))
        
        # Create the client with the transport
        product_inventory_client = zeep.Client(wsdl=product_inventory_wsdl, transport=transport)
        
        # Call the SanMar API to get inventory data
        logger.info(f"Calling SanMar inventory API for style: {style}")
        
        # Prepare the arguments for the API call
        args = [CUSTOMER_NUMBER, USERNAME, PASSWORD, style]
        if color:
            args.append(color)
        if size:
            args.append(size)
        
        # Log the request for debugging (without credentials)
        debug_args = ["REDACTED", "REDACTED", "REDACTED", style]
        if color:
            debug_args.append(color)
        if size:
            debug_args.append(size)
        logger.info(f"Inventory API request args: {debug_args}")
        
        # Call the getInventoryQtyForStyleColorSize method
        inventory_response = product_inventory_client.service.getInventoryQtyForStyleColorSize(*args)
        
        # Log the response for debugging
        logger.info(f"Inventory API response received for style: {style}")
        
        # Try to log the entire response as a string
        try:
            import json
            from zeep.helpers import serialize_object
            response_dict = serialize_object(inventory_response)
            logger.info(f"Inventory response dict: {json.dumps(response_dict, indent=2)}")
        except Exception as e:
            logger.error(f"Error serializing inventory response: {str(e)}")
        # Process the response into a more usable format
        inventory_data = {}
        
        # Get product data to extract color mapping
        product_data = get_product_data(style)
        color_mapping = {}
        
        # Create a mapping from catalog color codes to display names
        if product_data and 'listResponse' in product_data:
            for item in product_data['listResponse']:
                if isinstance(item, dict) and 'productBasicInfo' in item:
                    basic_info = item['productBasicInfo']
                    if 'catalogColor' in basic_info and 'color' in basic_info:
                        catalog_color = basic_info['catalogColor']
                        display_color = basic_info['color']
                        color_mapping[catalog_color] = display_color
        
        # Check if the response has the expected structure
        if hasattr(inventory_response, 'errorOccurred') and not inventory_response.errorOccurred:
            # If we have a specific color and size, the response will be a list of quantities by warehouse
            if color and size:
                # Create the inventory data structure
                display_color = color_mapping.get(color, color)  # Use display name if available
                
                if display_color not in inventory_data:
                    inventory_data[display_color] = {}
                if size not in inventory_data[display_color]:
                    inventory_data[display_color][size] = {"warehouses": {}, "total": 0}
                
                # Add warehouse data
                warehouse_ids = ["1", "2", "3", "4", "5", "6", "7", "12", "31"]
                for i, qty in enumerate(inventory_response.listResponse):
                    if i < len(warehouse_ids):
                        warehouse_id = warehouse_ids[i]
                        inventory_data[display_color][size]["warehouses"][warehouse_id] = qty
                        inventory_data[display_color][size]["total"] += qty
            
            # If we have a style but no color or size, the response will be a more complex structure
            elif hasattr(inventory_response, 'response') and hasattr(inventory_response.response, 'skus'):
                for sku in inventory_response.response.skus:
                    sku_catalog_color = sku.color
                    sku_size = sku.size
                    
                    # Use display name if available
                    sku_display_color = color_mapping.get(sku_catalog_color, sku_catalog_color)
                    
                    # Create nested structure if not exists
                    if sku_display_color not in inventory_data:
                        inventory_data[sku_display_color] = {}
                    if sku_size not in inventory_data[sku_display_color]:
                        inventory_data[sku_display_color][sku_size] = {"warehouses": {}, "total": 0}
                    
                    # Add warehouse data
                    for whse in sku.whse:
                        warehouse_id = str(whse.whseID)
                        quantity = whse.qty
                        
                        inventory_data[sku_display_color][sku_size]["warehouses"][warehouse_id] = quantity
                        inventory_data[sku_display_color][sku_size]["total"] += quantity
                        inventory_data[sku_color][sku_size]["total"] += quantity
        
        # If data was processed successfully
        if inventory_data:
            logger.info(f"Successfully retrieved inventory data for {style} with {len(inventory_data)} colors")
            return inventory_data
        else:
            # No inventory data found, use mock data
            logger.warning(f"Empty inventory data returned for {style}, using mock data")
            logger.info(f"Using mock data for style: {style}")
            from mock_data import get_mock_inventory
            mock_data = get_mock_inventory(style)
            return mock_data.get('inventory', {})
    except Exception as e:
        logger.error(f"Error fetching inventory data: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Return mock data on error
        logger.info(f"Using mock data for style: {style} due to error")
        from mock_data import get_mock_inventory
        mock_data = get_mock_inventory(style)
        return mock_data.get('inventory', {})

def get_pricing(style):
    """Get pricing data from SanMar API for a given style."""
    logger.info(f"Fetching pricing data for style: {style}")
    
    try:
        # Get product data to extract pricing information
        product_data = get_product_data(style)
        if not product_data:
            logger.error(f"No product data available for style: {style}")
            return None
            
        # Create pricing data structure
        pricing_data = {}
        
        # Check if listResponse is in product_data
        if 'listResponse' not in product_data:
            # Try to extract pricing information directly from the API response
            response = product_client.service.getProductInfoByStyleColorSize(
                arg0={"style": style, "color": "", "size": ""},
                arg1={"sanMarCustomerNumber": CUSTOMER_NUMBER,
                     "sanMarUserName": USERNAME,
                     "sanMarUserPassword": PASSWORD}
            )
            
            if hasattr(response, 'listResponse') and response.listResponse:
                # Process each item in the listResponse
                for item in response.listResponse:
                    if hasattr(item, 'productBasicInfo') and hasattr(item.productBasicInfo, 'uniqueKey') and hasattr(item, 'productPriceInfo'):
                        part_id = item.productBasicInfo.uniqueKey
                        price_info = item.productPriceInfo
                        
                        # Extract pricing information
                        original_price = getattr(price_info, 'piecePrice', 0)
                        sale_price = getattr(price_info, 'pieceSalePrice', original_price) if hasattr(price_info, 'pieceSalePrice') and getattr(price_info, 'pieceSalePrice') else original_price
                        case_size = getattr(item.productBasicInfo, 'caseSize', 24)
                        
                        # Add to pricing data
                        pricing_data[part_id] = {
                            "original": float(original_price),
                            "sale": float(sale_price),
                            "program": float(sale_price),  # Use sale price as program price
                            "case_size": int(case_size)
                        }
            else:
                logger.error(f"No listResponse in API response for pricing data")
                return None
        else:
            # Extract pricing information from product_data
            for item in product_data['listResponse']:
                if isinstance(item, dict) and 'productBasicInfo' in item and 'uniqueKey' in item['productBasicInfo'] and 'productPriceInfo' in item:
                    part_id = item['productBasicInfo']['uniqueKey']
                    price_info = item['productPriceInfo']
                    
                    # Extract pricing information
                    original_price = price_info.get('piecePrice', 0)
                    sale_price = price_info.get('pieceSalePrice', original_price) if price_info.get('pieceSalePrice') else original_price
                    case_size = item['productBasicInfo'].get('caseSize', 24)
                    
                    # Add to pricing data
                    pricing_data[part_id] = {
                        "original": float(original_price),
                        "sale": float(sale_price),
                        "program": float(sale_price),  # Use sale price as program price
                        "case_size": int(case_size)
                    }
        
        logger.info(f"Successfully retrieved pricing data for {len(pricing_data)} parts")
        return pricing_data
    except Exception as e:
        logger.error(f"Error fetching pricing data: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Return default pricing data on error
        return {
            "part1": {"original": 15.06, "sale": 14.29, "program": 11.03, "case_size": 24},
            "part2": {"original": 15.06, "sale": 14.29, "program": 11.03, "case_size": 24},
            "part3": {"original": 17.36, "sale": 13.92, "program": 13.92, "case_size": 12},
            "part4": {"original": 19.46, "sale": 14.87, "program": 14.87, "case_size": 12}
        }

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    status = {
        "status": "ok",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "api_credentials": HAS_CREDENTIALS
    }
    
    # Check if we're using the template
    template = request.args.get('template', 'false').lower() == 'true'
    
    if template:
        return render_template('health.html', status=status)
    else:
        return jsonify(status)

if __name__ == '__main__':
    print("Starting SanMar Inventory App...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True)
