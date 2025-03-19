from flask import Flask, render_template, jsonify
import zeep
import os
import requests
from dotenv import load_dotenv
import json
from flask import jsonify, request
from flask import Flask, render_template, jsonify

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Sanmar API credentials from environment variables
USERNAME = os.getenv("SANMAR_USERNAME")
PASSWORD = os.getenv("SANMAR_PASSWORD")
CUSTOMER_NUMBER = os.getenv("SANMAR_CUSTOMER_NUMBER")

# Startup environment check
if not all([USERNAME, PASSWORD, CUSTOMER_NUMBER]):
    print("*" * 80)
    print("WARNING: Missing SanMar API credentials!")
    print("Please ensure the following environment variables are set:")
    print("- SANMAR_USERNAME")
    print("- SANMAR_PASSWORD")
    print("- SANMAR_CUSTOMER_NUMBER")
    print("*" * 80)

# SOAP clients for Sanmar APIs with improved timeout and retry settings
product_wsdl = "https://ws.sanmar.com:8080/SanMarWebService/SanMarProductInfoServicePort?wsdl"
inventory_wsdl = "https://ws.sanmar.com:8080/promostandards/InventoryServiceBindingV2final?WSDL"
pricing_wsdl = "https://ws.sanmar.com:8080/promostandards/PricingAndConfigurationServiceBinding?WSDL"

# Create a transport with timeout settings
from zeep.transports import Transport
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configure retry strategy
retry_strategy = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET", "POST"]
)

# Create a transport with the retry strategy
transport = Transport(timeout=15)
transport.session.mount('https://', HTTPAdapter(max_retries=retry_strategy))
transport.session.mount('http://', HTTPAdapter(max_retries=retry_strategy))

# Initialize SOAP clients with the custom transport
product_client = zeep.Client(wsdl=product_wsdl, transport=transport)
inventory_client = zeep.Client(wsdl=inventory_wsdl, transport=transport)
pricing_client = zeep.Client(wsdl=pricing_wsdl, transport=transport)

# Warehouse mapping
WAREHOUSES = {
    "1": "Seattle, WA", "2": "Cincinnati, OH", "3": "Dallas, TX", "4": "Reno, NV",
    "5": "Robbinsville, NJ", "6": "Jacksonville, FL", "7": "Minneapolis, MN",
    "12": "Phoenix, AZ", "31": "Richmond, VA"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    # Check API credentials
    credential_status = {
        "SANMAR_USERNAME": bool(USERNAME),
        "SANMAR_PASSWORD": bool(PASSWORD),
        "SANMAR_CUSTOMER_NUMBER": bool(CUSTOMER_NUMBER),
    }
    
    # Check API connectivity
    api_status = {}
    
    try:
        # Ping product API
        product_client.transport.session.get(product_wsdl, timeout=5)
        api_status["product_api"] = "Connected"
    except Exception as e:
        api_status["product_api"] = f"Error: {str(e)}"
    
    try:
        # Ping inventory API
        inventory_client.transport.session.get(inventory_wsdl, timeout=5)
        api_status["inventory_api"] = "Connected"
    except Exception as e:
        api_status["inventory_api"] = f"Error: {str(e)}"
        
    try:
        # Ping pricing API
        pricing_client.transport.session.get(pricing_wsdl, timeout=5)
        api_status["pricing_api"] = "Connected"
    except Exception as e:
        api_status["pricing_api"] = f"Error: {str(e)}"
    
    return render_template('health.html', 
                          credential_status=credential_status, 
                          api_status=api_status)

# SanMar API endpoints configuration
# Primary SOAP endpoints are already defined above with the WSDLs
# Direct access to SanMar API is preferred for reliability
SANMAR_API_BASE_URL = "https://ws.sanmar.com:8080"

# Fallback middleware server URL (may be used for specific operations)
MIDDLEWARE_API_BASE_URL = "https://api-mini-server-919227e25714.herokuapp.com"

# Default timeout for API requests (seconds)
API_TIMEOUT = 15

# Max retry attempts for API requests
MAX_RETRIES = 2

@app.route('/api/autocomplete')
def autocomplete():
    """API endpoint to provide style number autocomplete suggestions"""
    query = request.args.get('q', '').strip().upper()
    if not query or len(query) < 2:
        return jsonify([])
    
    try:
        # Try to get style numbers that match the query using the product client
        results = []
        request_data = {
            "arg0": {"style": query + "%", "color": "", "size": ""},
            "arg1": {"sanMarCustomerNumber": CUSTOMER_NUMBER, "sanMarUserName": USERNAME,
                     "sanMarUserPassword": PASSWORD}
        }
        
        try:
            print(f"Searching for styles matching: {query}")
            response = product_client.service.getProductInfoByStyleColorSize(**request_data)
            
            if not response.errorOccured and hasattr(response, 'listResponse') and hasattr(response.listResponse, 'productBasicInfo'):
                # Extract unique style numbers
                styles = set()
                for item in response.listResponse.productBasicInfo:
                    style = item.style
                    if style.startswith(query):
                        styles.add(style)
                
                results = list(styles)[:10]  # Limit to 10 results
            
        except Exception as e:
            print(f"Error in autocomplete search: {e}")
            
        # Fallback: Add common style numbers if we don't have enough results
        if len(results) < 3:
            common_styles = ["PC61", "5000", "DT6000", "ST850", "K420", "G200", "BC3001", "PC850", "L223"]
            for style in common_styles:
                if style.startswith(query) and style not in results:
                    results.append(style)
        
        return jsonify(results[:10])  # Return maximum 10 results
        
    except Exception as e:
        print(f"Autocomplete error: {e}")
        return jsonify([])

# Mock product data for demonstration purposes
MOCK_PRODUCTS = {
    "C112": {
        "name": "Port Authority Core Blend Pique Polo",
        "description": "This budget-friendly essential combines the soft comfort of cotton with the durability of polyester. Features an extended tail for tucking, flat knit collar, three-button placket, dyed-to-match buttons, and side vents.",
        "colors": ["Black", "Navy", "White", "Red", "Royal", "Dark Green", "Steel Grey"],
        "sizes": ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL", "5XL", "6XL"],
        "images": {
            "Black": "https://www.sanmar.com/products/catalog/2022/f1/port_authority/fullsize/C112_Black_Flat_2022.jpg",
            "Navy": "https://www.sanmar.com/products/catalog/2022/f1/port_authority/fullsize/C112_Navy_Flat_2022.jpg",
            "White": "https://www.sanmar.com/products/catalog/2022/f1/port_authority/fullsize/C112_White_Flat_2022.jpg",
            "Red": "https://www.sanmar.com/products/catalog/2022/f1/port_authority/fullsize/C112_Red_Flat_2022.jpg",
            "Royal": "https://www.sanmar.com/products/catalog/2022/f1/port_authority/fullsize/C112_Royal_Flat_2022.jpg",
            "Dark Green": "https://www.sanmar.com/products/catalog/2022/f1/port_authority/fullsize/C112_DarkGreen_Flat_2022.jpg",
            "Steel Grey": "https://www.sanmar.com/products/catalog/2022/f1/port_authority/fullsize/C112_SteelGrey_Flat_2022.jpg"
        },
        "price": {
            "base": 19.99,
            "sale": 15.99,
            "case_size": 36
        }
    },
    "J790": {
        "name": "Port Authority Glacier Soft Shell Jacket",
        "description": "A versatile soft shell jacket with a clean, simple design. Perfect for corporate and outdoor activities.",
        "colors": ["Black", "Dress Blue Navy", "True Red", "Dark Smoke Grey", "Rich Green"],
        "sizes": ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"],
        "images": {
            "Black": "https://www.sanmar.com/products/catalog/2022/f2/port_authority/fullsize/J790_Black_Flat_2022.jpg",
            "Dress Blue Navy": "https://www.sanmar.com/products/catalog/2022/f2/port_authority/fullsize/J790_DressBlueNavy_Flat_2022.jpg",
            "True Red": "https://www.sanmar.com/products/catalog/2022/f2/port_authority/fullsize/J790_TrueRed_Flat_2022.jpg",
            "Dark Smoke Grey": "https://www.sanmar.com/products/catalog/2022/f2/port_authority/fullsize/J790_DarkSmokeGrey_Flat_2022.jpg",
            "Rich Green": "https://www.sanmar.com/products/catalog/2022/f2/port_authority/fullsize/J790_RichGreen_Flat_2022.jpg"
        },
        "price": {
            "base": 49.99,
            "sale": 39.99,
            "case_size": 12
        }
    },
    "PC61": {
        "name": "Port & Company Essential T-Shirt",
        "description": "A comfortable, everyday t-shirt that's perfect for screen printing and embroidery.",
        "colors": ["Black", "White", "Navy", "Red", "Royal", "Athletic Heather", "Dark Green"],
        "sizes": ["S", "M", "L", "XL", "2XL", "3XL", "4XL"],
        "images": {
            "Black": "https://www.sanmar.com/products/catalog/2021/f2/port__company/fullsize/PC61_Black_Flat_2021.jpg",
            "White": "https://www.sanmar.com/products/catalog/2021/f2/port__company/fullsize/PC61_White_Flat_2021.jpg",
            "Navy": "https://www.sanmar.com/products/catalog/2021/f2/port__company/fullsize/PC61_Navy_Flat_2021.jpg",
            "Red": "https://www.sanmar.com/products/catalog/2021/f2/port__company/fullsize/PC61_Red_Flat_2021.jpg",
            "Royal": "https://www.sanmar.com/products/catalog/2021/f2/port__company/fullsize/PC61_Royal_Flat_2021.jpg",
            "Athletic Heather": "https://www.sanmar.com/products/catalog/2021/f2/port__company/fullsize/PC61_AthleticHeather_Flat_2021.jpg",
            "Dark Green": "https://www.sanmar.com/products/catalog/2021/f2/port__company/fullsize/PC61_DarkGreen_Flat_2021.jpg"
        },
        "price": {
            "base": 4.49,
            "sale": 3.59,
            "case_size": 72
        }
    },
    "5000": {
        "name": "Gildan Heavy Cotton T-Shirt",
        "description": "A classic, heavyweight t-shirt perfect for everyday wear.",
        "colors": ["Black", "White", "Navy", "Red", "Royal", "Sport Grey", "Dark Heather"],
        "sizes": ["S", "M", "L", "XL", "2XL", "3XL"],
        "images": {
            "Black": "https://www.sanmar.com/products/catalog/2021/f1/gildan/fullsize/5000_Black_Flat_2021.jpg",
            "White": "https://www.sanmar.com/products/catalog/2021/f1/gildan/fullsize/5000_White_Flat_2021.jpg",
            "Navy": "https://www.sanmar.com/products/catalog/2021/f1/gildan/fullsize/5000_Navy_Flat_2021.jpg",
            "Red": "https://www.sanmar.com/products/catalog/2021/f1/gildan/fullsize/5000_Red_Flat_2021.jpg",
            "Royal": "https://www.sanmar.com/products/catalog/2021/f1/gildan/fullsize/5000_Royal_Flat_2021.jpg",
            "Sport Grey": "https://www.sanmar.com/products/catalog/2021/f1/gildan/fullsize/5000_SportGrey_Flat_2021.jpg",
            "Dark Heather": "https://www.sanmar.com/products/catalog/2021/f1/gildan/fullsize/5000_DarkHeather_Flat_2021.jpg"
        },
        "price": {
            "base": 3.99,
            "sale": 3.19,
            "case_size": 72
        }
    },
    "DT6000": {
        "name": "District Very Important Tee",
        "description": "A soft, comfortable tee with modern styling.",
        "colors": ["Black", "White", "Navy", "Red", "Blue", "Grey"],
        "sizes": ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"],
        "images": {
            "Black": "https://www.sanmar.com/products/catalog/2022/f1/district/fullsize/DT6000_Black_Flat_2022.jpg",
            "White": "https://www.sanmar.com/products/catalog/2022/f1/district/fullsize/DT6000_White_Flat_2022.jpg",
            "Navy": "https://www.sanmar.com/products/catalog/2022/f1/district/fullsize/DT6000_Navy_Flat_2022.jpg",
            "Red": "https://www.sanmar.com/products/catalog/2022/f1/district/fullsize/DT6000_Red_Flat_2022.jpg",
            "Blue": "https://www.sanmar.com/products/catalog/2022/f1/district/fullsize/DT6000_Blue_Flat_2022.jpg",
            "Grey": "https://www.sanmar.com/products/catalog/2022/f1/district/fullsize/DT6000_Grey_Flat_2022.jpg"
        },
        "price": {
            "base": 5.99,
            "sale": 4.79,
            "case_size": 48
        }
    },
    "ST850": {
        "name": "Sport-Tek PosiCharge Competitor Tee",
        "description": "A moisture-wicking, performance tee ideal for athletics and active wear.",
        "colors": ["Black", "White", "True Navy", "True Red", "True Royal", "Silver"],
        "sizes": ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"],
        "images": {
            "Black": "https://www.sanmar.com/products/catalog/2022/f1/sport-tek/fullsize/ST850_Black_Flat_2022.jpg",
            "White": "https://www.sanmar.com/products/catalog/2022/f1/sport-tek/fullsize/ST850_White_Flat_2022.jpg",
            "True Navy": "https://www.sanmar.com/products/catalog/2022/f1/sport-tek/fullsize/ST850_TrueNavy_Flat_2022.jpg",
            "True Red": "https://www.sanmar.com/products/catalog/2022/f1/sport-tek/fullsize/ST850_TrueRed_Flat_2022.jpg",
            "True Royal": "https://www.sanmar.com/products/catalog/2022/f1/sport-tek/fullsize/ST850_TrueRoyal_Flat_2022.jpg",
            "Silver": "https://www.sanmar.com/products/catalog/2022/f1/sport-tek/fullsize/ST850_Silver_Flat_2022.jpg"
        },
        "price": {
            "base": 7.99,
            "sale": 6.39,
            "case_size": 36
        }
    }
}

@app.route('/product/<style>')
def product_page(style):
    """
    Product detail page with improved error handling and fallback to mock data
    """
    # Standardize style number format
    style = style.upper()
    
    # Check if we have mock data for this style first for faster response
    if style in MOCK_PRODUCTS:
        print(f"Using mock data for {style}")
        mock_data = MOCK_PRODUCTS[style]
        
        # Create part_id_map from mock data
        part_id_map = {}
        for color in mock_data["colors"]:
            part_id_map[color] = {}
            for size in mock_data["sizes"]:
                part_id_map[color][size] = f"{style}_{color}_{size}"
        
        # Create inventory data - show random stock in each warehouse
        inventory = {}
        for color in mock_data["colors"]:
            for size in mock_data["sizes"]:
                part_id = f"{style}_{color}_{size}"
                inventory[part_id] = {
                    "total": sum(range(1, 10)) * 100,  # Random total
                    "warehouses": {
                        wh_id: (idx + 1) * 100  # Different stock by warehouse
                        for idx, wh_id in enumerate(WAREHOUSES.keys())
                    }
                }
        
        # Create pricing data
        pricing = {}
        for color in mock_data["colors"]:
            for size in mock_data["sizes"]:
                part_id = f"{style}_{color}_{size}"
                pricing[part_id] = {
                    "original": mock_data["price"]["base"],
                    "sale": mock_data["price"]["sale"],
                    "program": mock_data["price"]["sale"] * 0.9,  # 10% discount for program
                    "case_size": mock_data["price"]["case_size"]
                }
        
        return render_template('product.html', 
                              style=style, 
                              colors=mock_data["colors"], 
                              sizes=mock_data["sizes"],
                              inventory_json=json.dumps(inventory), 
                              pricing_json=json.dumps(pricing),
                              part_id_map_json=json.dumps(part_id_map), 
                              warehouses=WAREHOUSES,
                              images=mock_data["images"])
    
    # If not in mock data, try using our primary SOAP API method
    print(f"Attempting to fetch live data for {style} from SanMar API")
    product_data = get_product_data(style)
    
    # If we got product data from the primary method, use it
    if product_data:
        colors = product_data["colors"]
        sizes = product_data["sizes"]
        part_id_map = product_data["part_id_map"]
        images = product_data["images"]

        inventory = get_inventory(style)
        pricing = get_pricing(style)

        return render_template('product.html', 
                              style=style, 
                              colors=colors, 
                              sizes=sizes,
                              inventory_json=json.dumps(inventory), 
                              pricing_json=json.dumps(pricing),
                              part_id_map_json=json.dumps(part_id_map), 
                              warehouses=WAREHOUSES,
                              images=images)
    
    # If primary method fails, try using the SanMar combined endpoint as fallback
    print(f"Primary product API failed for {style}, trying combined endpoint fallback")
    try:
        # Try the middleware server as a fallback since the direct API might have connectivity issues
        # Format is /sanmar/combined/:styleNo/:colorCode?
        combined_url = f"{MIDDLEWARE_API_BASE_URL}/sanmar/combined/{style}"
        print(f"Attempting to fetch from middleware combined endpoint: {combined_url}")
        
        try:
            combined_response = requests.get(combined_url, timeout=API_TIMEOUT)
            print(f"Combined endpoint response status: {combined_response.status_code}")
            
            if combined_response.status_code == 200:
                try:
                    data = combined_response.json()
                    print(f"Combined endpoint JSON data received: {json.dumps(data)[:500]}...")
                    
                    if data.get('success') and data.get('data'):
                        # Extract data from combined endpoint
                        combined_data = data['data']
                        
                        # Build product data structure from combined endpoint response
                        product_info = combined_data.get('product', {})
                        inventory_info = combined_data.get('inventory', {})
                        pricing_info = combined_data.get('pricing', {})
                        if product_info.get('colorName'):
                            main_color = product_info.get('colorName')
                            colors.append(main_color)
                            
                            # Add images
                            if product_info.get('colorImage'):
                                images[main_color] = product_info.get('colorImage')
                            elif product_info.get('mainImage'):
                                images[main_color] = product_info.get('mainImage')
                            else:
                                images[main_color] = f"https://via.placeholder.com/300?text={style}_{main_color}"
                                
                        # If no colors, but we have a main image
                        elif product_info.get('mainImage'):
                            colors = ["Default"]
                            images["Default"] = product_info.get('mainImage')
                            
                        # Last resort - create a default color
                        else:
                            colors = ["Default"]
                            images["Default"] = f"https://via.placeholder.com/300?text={style}"
                        
                        # Build part_id_map
                        part_id_map = {}
                        for color in colors:
                            part_id_map[color] = {}
                            for size in sizes:
                                # Generate a placeholder part_id
                                part_id_map[color][size] = f"{style}_{color}_{size}"
                        
                        # Process inventory data
                        inventory = {}
                        for color in colors:
                            for size in sizes:
                                part_id = part_id_map[color][size]
                                total_quantity = 0
                                warehouse_quantities = {}
                                
                                if 'warehouses' in inventory_info:
                                    for warehouse in inventory_info['warehouses']:
                                        wh_id = warehouse.get('code', '1')
                                        qty = 0
                                        
                                        # Find matching size in warehouse quantities
                                        for item in warehouse.get('quantities', []):
                                            if item.get('size') == size:
                                                qty = item.get('quantity', 0)
                                                total_quantity += qty
                                                break
                                                
                                        warehouse_quantities[wh_id] = qty
                                
                                # If no inventory found, generate mock data
                                if not warehouse_quantities:
                                    total_quantity = 500  # Default mock quantity
                                    for wh_id in WAREHOUSES.keys():
                                        warehouse_quantities[wh_id] = (int(wh_id) * 30) % 200 + 50  # Random-ish values
                                
                                inventory[part_id] = {
                                    "total": total_quantity,
                                    "warehouses": warehouse_quantities
                                }
                        
                        # Process pricing data
                        pricing = {}
                        for color in colors:
                            for size in sizes:
                                part_id = part_id_map[color][size]
                                
                                if pricing_info:
                                    base_price = pricing_info.get('originalPrice', 4.99)
                                    sale_price = pricing_info.get('salePrice')
                                    program_price = pricing_info.get('programPrice')
                                    case_size = 72
                                else:
                                    # Mock pricing data
                                    base_price = 4.99
                                    sale_price = 3.99
                                    program_price = 3.49
                                    case_size = 72
                                
                                pricing[part_id] = {
                                    "original": base_price,
                                    "sale": sale_price or base_price * 0.8,
                                    "program": program_price or base_price * 0.7,
                                    "case_size": case_size
                                }
                        
                        # Use combined data for display
                        return render_template('product.html', 
                                            style=style, 
                                            colors=colors, 
                                            sizes=sizes,
                                            inventory_json=json.dumps(inventory), 
                                            pricing_json=json.dumps(pricing),
                                            part_id_map_json=json.dumps(part_id_map), 
                                            warehouses=WAREHOUSES,
                                            images=images)
                    else:
                        print(f"Combined endpoint success is false or no data in response: {data}")
                except json.JSONDecodeError as jde:
                    print(f"Error decoding JSON from combined endpoint: {jde}")
            else:
                print(f"Combined endpoint returned non-200 status: {combined_response.status_code}")
                print(f"Response content: {combined_response.text[:500]}")
        except requests.RequestException as re:
            print(f"Request exception for combined endpoint: {re}")
    except Exception as e:
        print(f"Error using combined endpoint: {e}")
    
    # ===== All API methods failed =====
    
    # Check if credentials are configured
    if not all([USERNAME, PASSWORD, CUSTOMER_NUMBER]):
        print("ERROR: API credentials missing or not configured properly")
        return render_template('error.html', 
                            error_title="API Configuration Error",
                            error_message="Missing SanMar API credentials. Please check your environment variables."), 500
    
    # If credentials exist but product wasn't found
    print(f"ERROR: All methods failed to find product data for style '{style}'")
    return render_template('error.html',
                        error_title="Product Not Found",
                        error_message=f"Style number '{style}' could not be found or retrieved from SanMar."), 404

def get_product_data(style):
    """
    Fetch product data from SanMar API using the SOAP service.
    Enhanced with better error handling and debugging.
    """
    # Validate API credentials
    if not all([USERNAME, PASSWORD, CUSTOMER_NUMBER]):
        print("ERROR: Missing SanMar API credentials in environment variables")
        return None
        
    # Attempt with exact style match first
    request_data = {
        "arg0": {"style": style, "color": "", "size": ""},
        "arg1": {"sanMarCustomerNumber": CUSTOMER_NUMBER, "sanMarUserName": USERNAME,
                 "sanMarUserPassword": PASSWORD}
    }
    
    try:
        print(f"Requesting product info for style: {style}")
        # Dump request for debugging
        print(f"Request data: {json.dumps(request_data, default=str)[:200]}...")
        
        # Make API call
        response = product_client.service.getProductInfoByStyleColorSize(**request_data)
        
        # Check for errors
        if hasattr(response, 'errorOccured') and response.errorOccured:
            error_msg = getattr(response, 'errorMessage', 'Unknown API error')
            print(f"SanMar API returned error: {error_msg}")
            
            # Try a wildcard search if exact match fails
            wildcard_request = {
                "arg0": {"style": f"{style}%", "color": "", "size": ""},
                "arg1": {"sanMarCustomerNumber": CUSTOMER_NUMBER, "sanMarUserName": USERNAME,
                        "sanMarUserPassword": PASSWORD}
            }
            print(f"Trying wildcard search: {style}%")
            response = product_client.service.getProductInfoByStyleColorSize(**wildcard_request)
            
            if hasattr(response, 'errorOccured') and response.errorOccured:
                print(f"Wildcard search also failed: {getattr(response, 'errorMessage', 'Unknown error')}")
                return None
            
        # Debug response structure
        has_list_response = hasattr(response, 'listResponse')
        has_product_info = has_list_response and hasattr(response.listResponse, 'productBasicInfo')
        
        print(f"Response has listResponse: {has_list_response}")
        print(f"Response has productBasicInfo: {has_product_info}")
        
        if not has_list_response or not has_product_info:
            print(f"Invalid or empty response structure for style: {style}")
            print(f"Response structure: {dir(response)}")
            return None
            
        # Check if any products were returned
        product_count = len(response.listResponse.productBasicInfo)
        print(f"Found {product_count} product variants for style {style}")
        
        if product_count == 0:
            print(f"No product information returned for style: {style}")
            return None
        
        # Extract colors, sizes, and other data
        try:
            # Get unique colors from all products
            colors = list(set(item.catalogColor for item in response.listResponse.productBasicInfo))
            print(f"Colors found: {colors}")
            
            # Get sizes from the first product - assuming consistent across colors
            first_product = response.listResponse.productBasicInfo[0]
            if hasattr(first_product, 'availableSizes') and first_product.availableSizes:
                sizes = first_product.availableSizes.split(", ")
            else:
                # If no availableSizes field, extract from individual products
                all_sizes = set()
                for item in response.listResponse.productBasicInfo:
                    if hasattr(item, 'size') and item.size:
                        all_sizes.add(item.size)
                sizes = list(all_sizes)
            
            print(f"Sizes found: {sizes}")
            
            # Build part_id_map and images collections
            part_id_map = {}
            images = {}
            
            for item in response.listResponse.productBasicInfo:
                color = item.catalogColor
                size = item.size if hasattr(item, 'size') else "ONE SIZE"
                part_id = item.uniqueKey if hasattr(item, 'uniqueKey') else f"{style}_{color}_{size}"
                
                # Initialize color in maps if needed
                if color not in part_id_map:
                    part_id_map[color] = {}
                    
                # Add part_id for this color/size
                part_id_map[color][size] = part_id
                
                # Add image for this color if not already added
                if color not in images and hasattr(item, 'colorProductImage') and item.colorProductImage:
                    images[color] = item.colorProductImage
            
            # Make sure we have images for all colors
            for color in colors:
                if color not in images:
                    # Use a placeholder if we don't have an image
                    images[color] = f"https://via.placeholder.com/300?text={style}_{color}"
            
            return {
                "colors": colors, 
                "sizes": sizes, 
                "part_id_map": part_id_map, 
                "images": images
            }
        except Exception as e:
            print(f"Error processing product data: {e}")
            import traceback
            traceback.print_exc()
            return None
    except zeep.exceptions.Fault as zf:
        print(f"SOAP Fault fetching product data: {zf}")
        return None
    except zeep.exceptions.TransportError as te:
        print(f"Transport error connecting to SanMar API: {te}")
        return None
    except Exception as e:
        print(f"Unexpected error fetching product data: {e}")
        return None

def get_inventory(product_id):
    # Skip if credentials aren't configured
    if not all([USERNAME, PASSWORD]):
        print("ERROR: Missing SanMar API credentials for inventory API")
        return {}
        
    request_data = {
        "wsVersion": "2.0.0", "id": USERNAME, "password": PASSWORD, "productId": product_id
    }
    
    try:
        print(f"Requesting inventory data for product: {product_id}")
        response = inventory_client.service.GetInventoryLevelsRequest(**request_data)
        
        inventory = {}
        # Check if response contains the expected data structure
        if ("Inventory" not in response or 
            "PartInventoryArray" not in response["Inventory"] or 
            "PartInventory" not in response["Inventory"]["PartInventoryArray"]):
            print(f"Invalid or empty inventory response structure for product: {product_id}")
            return {}
            
        for part in response["Inventory"]["PartInventoryArray"]["PartInventory"]:
            part_id = part["partId"]
            total = part["quantityAvailable"]["Quantity"]["value"]
            warehouses = {
                loc["inventoryLocationId"]: loc["inventoryLocationQuantity"]["Quantity"]["value"]
                for loc in part["InventoryLocationArray"]["InventoryLocation"]
            }
            inventory[part_id] = {"total": total, "warehouses": warehouses}
        return inventory
    except zeep.exceptions.Fault as zf:
        print(f"SOAP Fault fetching inventory data: {zf}")
        return {}
    except zeep.exceptions.TransportError as te:
        print(f"Transport error connecting to SanMar inventory API: {te}")
        return {}
    except KeyError as ke:
        print(f"KeyError parsing inventory response: {ke}")
        return {}
    except Exception as e:
        print(f"Unexpected error fetching inventory: {e}")
        return {}

def get_pricing(product_id):
    # Skip if credentials aren't configured
    if not all([USERNAME, PASSWORD]):
        print("ERROR: Missing SanMar API credentials for pricing API")
        return {}
        
    request_data = {
        "wsVersion": "1.0.0", "id": USERNAME, "password": PASSWORD, "productId": product_id,
        "currency": "USD", "fobId": "1", "priceType": "Net", "localizationCountry": "US",
        "localizationLanguage": "EN", "configurationType": "Blank"
    }
    
    try:
        print(f"Requesting pricing data for product: {product_id}")
        response = pricing_client.service.GetConfigurationAndPricingRequest(**request_data)
        
        pricing = {}
        # Check if response contains the expected data structure
        if ("Configuration" not in response or 
            "PartArray" not in response["Configuration"] or 
            "Part" not in response["Configuration"]["PartArray"]):
            print(f"Invalid or empty pricing response structure for product: {product_id}")
            return {}
            
        for part in response["Configuration"]["PartArray"]["Part"]:
            if "partId" not in part or "PartPriceArray" not in part:
                continue
                
            part_id = part["partId"]
            if "PartPrice" not in part["PartPriceArray"] or not part["PartPriceArray"]["PartPrice"]:
                continue
                
            price_info = part["PartPriceArray"]["PartPrice"][0]
            pricing[part_id] = {
                "original": price_info.get("price", 0),
                "sale": price_info.get("salePrice", None),
                "program": price_info.get("incentivePrice", None),
                "case_size": 72
            }
        return pricing
    except zeep.exceptions.Fault as zf:
        print(f"SOAP Fault fetching pricing data: {zf}")
        return {}
    except zeep.exceptions.TransportError as te:
        print(f"Transport error connecting to SanMar pricing API: {te}")
        return {}
    except KeyError as ke:
        print(f"KeyError parsing pricing response: {ke}")
        return {}
    except Exception as e:
        print(f"Unexpected error fetching pricing: {e}")
        return {}

if __name__ == "__main__":
    app.run(debug=True)
