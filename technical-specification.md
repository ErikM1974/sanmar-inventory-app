# Technical Specification: Dynamic Product Pricing for Color Swatch Selection

## Overview
This document provides technical details for implementing dynamic product pricing when color swatches are selected in the SanMar Inventory Application. It includes code examples for backend and frontend components.

## 1. Backend Implementation

### 1.1 Enhanced SanMar Pricing Service

We'll extend the existing `SanmarPricingService` class to support both request formats and add caching capabilities:

```python
# sanmar_pricing_service.py
import logging
import zeep
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from zeep.transports import Transport
import os
from functools import lru_cache
import time
from threading import Lock

# Set up logging
logger = logging.getLogger(__name__)

class PricingCache:
    """Simple in-memory cache for pricing data with TTL"""
    def __init__(self, ttl=900):  # Default TTL: 15 minutes (900 seconds)
        self.cache = {}
        self.lock = Lock()
        self.ttl = ttl
    
    def get(self, key):
        """Get item from cache if it exists and hasn't expired"""
        with self.lock:
            if key in self.cache:
                timestamp, data = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    return data
                else:
                    # Expired item
                    del self.cache[key]
            return None
    
    def set(self, key, data):
        """Store item in cache with current timestamp"""
        with self.lock:
            self.cache[key] = (time.time(), data)
    
    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
    
    def cleanup(self):
        """Remove expired entries"""
        with self.lock:
            now = time.time()
            expired_keys = [k for k, (timestamp, _) in self.cache.items() 
                           if now - timestamp >= self.ttl]
            for k in expired_keys:
                del self.cache[k]

class SanmarPricingService:
    """
    Client for the SanMar Pricing Service
    This provides direct pricing information for specific style/color/size combinations
    """
    
    def __init__(self, username, password, customer_number, environment="production"):
        """
        Initialize the SanMar Pricing Service client
        
        Args:
            username (str): SanMar API username
            password (str): SanMar API password
            customer_number (str): SanMar customer number
            environment (str): "production" or "development"
        """
        self.username = username
        self.password = password
        self.customer_number = customer_number
        self.environment = environment
        
        # Initialize cache
        self.cache = PricingCache()
        
        # Configure retry strategy for API calls
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
        
        # Set up transport with retry strategy and timeout
        self.transport = Transport(timeout=30)
        self.transport.session.mount('https://', HTTPAdapter(max_retries=retry_strategy))
        
        # SanMar Pricing Service WSDL URL based on environment
        if environment.lower() == "development":
            self.wsdl_url = "https://edev-ws.sanmar.com:8080/SanMarWebService/SanMarPricingServicePort?wsdl"
            logger.info("Using development environment for SanMar Pricing Service")
        else:
            self.wsdl_url = "https://ws.sanmar.com:8080/SanMarWebService/SanMarPricingServicePort?wsdl"
            logger.info("Using production environment for SanMar Pricing Service")
        
        try:
            # Initialize SOAP client
            self.client = zeep.Client(wsdl=self.wsdl_url, transport=self.transport)
            logger.info("Successfully initialized SanMar Pricing Service client")
            self._ready = True
        except Exception as e:
            logger.error(f"Error initializing SanMar Pricing Service client: {str(e)}")
            self._ready = False
    
    def is_ready(self):
        """Check if the client is initialized and ready to use."""
        return self._ready
    
    def get_pricing(self, style, color=None, size=None, use_cache=True):
        """
        Fetch pricing data directly from SanMar Pricing Service using style/color/size
        
        Args:
            style (str): Product style number (e.g., "PC61")
            color (str, optional): Catalog color name
            size (str, optional): Size code
            use_cache (bool): Whether to use cached data (default: True)
        
        Returns:
            dict: Pricing data for the specified product or None if error
        """
        if not self._ready:
            logger.error("SanMar Pricing Service client not initialized")
            return None
        
        # Generate cache key
        cache_key = f"{style}:{color or ''}:{size or ''}"
        
        # Check cache if enabled
        if use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data:
                logger.info(f"Using cached pricing data for {cache_key}")
                return cached_data
        
        # Prepare the request data
        request_data = {
            "arg0": {
                "style": style,
                "color": color if color else "",
                "size": size if size else "",
                "casePrice": None,
                "dozenPrice": None,
                "piecePrice": None,
                "salePrice": None,
                "myPrice": None,
                "inventoryKey": None,
                "sizeIndex": None
            },
            "arg1": {
                "sanMarCustomerNumber": self.customer_number,
                "sanMarUserName": self.username,
                "sanMarUserPassword": self.password
            }
        }
        
        # Log the request for debugging (without credentials)
        debug_request = {
            "arg0": {
                "style": style,
                "color": color if color else "",
                "size": size if size else "",
            }
        }
        logger.info(f"Requesting SanMar pricing for style: {style}, color: {color if color else 'None'}, size: {size if size else 'None'}")
        
        try:
            # Call the API
            response = self.client.service.getPricing(**request_data)
            
            # Check for errors
            if response.errorOccurred:
                logger.error(f"API error: {response.message}")
                return None
            
            # Create our pricing data structure
            pricing_data = {
                "original_price": {},
                "sale_price": {},
                "program_price": {},
                "case_size": {},
                "color_pricing": {}
            }
            
            # Process the response
            if hasattr(response, 'listResponse') and response.listResponse:
                # Normalize colors and sizes for consistent storage
                colors_seen = set()
                
                # Process each response item
                for item in response.listResponse:
                    # Get the size and color
                    current_size = getattr(item, 'size', 'Unknown')
                    current_color = getattr(item, 'color', None)
                    
                    logger.info(f"Processing pricing for {style}, color: {current_color}, size: {current_size}")
                    
                    # Extract all price values
                    piece_price = getattr(item, 'piecePrice', None)
                    dozen_price = getattr(item, 'dozenPrice', None)
                    case_price = getattr(item, 'casePrice', None)
                    sale_price = getattr(item, 'salePrice', None)
                    my_price = getattr(item, 'myPrice', None)  # Customer-specific pricing
                    
                    # Extract sale dates if available
                    sale_start_date = getattr(item, 'saleStartDate', None)
                    sale_end_date = getattr(item, 'saleEndDate', None)
                    
                    # Extract inventory key and size index
                    inventory_key = getattr(item, 'inventoryKey', None)
                    size_index = getattr(item, 'sizeIndex', None)
                    
                    # Use piece price as primary, fall back to case price
                    price_value = piece_price if piece_price is not None else case_price
                    
                    # If we don't have either, skip this item
                    if price_value is None:
                        logger.warning(f"No price found for {style}, color: {current_color}, size: {current_size}")
                        continue
                    
                    # Get case size for this style/size
                    # Use default case sizes based on style and size
                    style_upper = style.upper()
                    if style_upper.startswith('PC61'):
                        if current_size in ['XS', 'S', 'M', 'L', 'XL']:
                            case_size = 72
                        else:  # 2XL and up
                            case_size = 36
                    elif style_upper.startswith('J790'):
                        if current_size in ['XS', 'S', 'M', 'L', 'XL', '2XL']:
                            case_size = 24
                        else:  # 3XL and up
                            case_size = 12
                    elif style_upper == 'C112':
                        case_size = 144  # Special case for caps
                    else:
                        case_size = 24  # Default
                    
                    # Add to general pricing
                    pricing_data["original_price"][current_size] = float(price_value)
                    pricing_data["sale_price"][current_size] = float(sale_price) if sale_price is not None else float(price_value)
                    pricing_data["program_price"][current_size] = float(my_price) if my_price is not None else float(price_value)
                    pricing_data["case_size"][current_size] = case_size
                    
                    # Add color-specific pricing
                    if current_color:
                        # Normalize the color for our data structure
                        colors_seen.add(current_color)
                        
                        # Make sure this color exists in our data structure
                        if current_color not in pricing_data["color_pricing"]:
                            pricing_data["color_pricing"][current_color] = {
                                "original_price": {},
                                "sale_price": {},
                                "program_price": {},
                                "case_size": {},
                                "dozen_price": {},
                                "piece_price": {},
                                "sale_dates": {}
                            }
                        
                        # Add the pricing data for this color and size
                        pricing_data["color_pricing"][current_color]["original_price"][current_size] = float(price_value)
                        pricing_data["color_pricing"][current_color]["sale_price"][current_size] = float(sale_price) if sale_price is not None else float(price_value)
                        pricing_data["color_pricing"][current_color]["program_price"][current_size] = float(my_price) if my_price is not None else float(price_value)
                        pricing_data["color_pricing"][current_color]["case_size"][current_size] = case_size
                        
                        # Add dozen price if available
                        if dozen_price is not None:
                            pricing_data["color_pricing"][current_color]["dozen_price"][current_size] = float(dozen_price)
                        
                        # Add piece price if available
                        if piece_price is not None:
                            pricing_data["color_pricing"][current_color]["piece_price"][current_size] = float(piece_price)
                        
                        # Add sale dates if available
                        if sale_start_date and sale_end_date:
                            pricing_data["color_pricing"][current_color]["sale_dates"][current_size] = {
                                "start": str(sale_start_date),
                                "end": str(sale_end_date)
                            }
                        
                        # Store inventory key and size index for future reference
                        if inventory_key and size_index:
                            if "inventory_mapping" not in pricing_data["color_pricing"][current_color]:
                                pricing_data["color_pricing"][current_color]["inventory_mapping"] = {}
                            
                            pricing_data["color_pricing"][current_color]["inventory_mapping"][current_size] = {
                                "inventoryKey": inventory_key,
                                "sizeIndex": size_index
                            }
                        
                        logger.info(f"Added pricing for {current_color}, size {current_size}: price={price_value}, sale={sale_price}, case_size={case_size}")
                
                # Create color pricing for default if a specific color was requested
                if color and color not in pricing_data["color_pricing"] and len(colors_seen) > 0:
                    # Use the first color we saw in the response as a fallback
                    fallback_color = next(iter(colors_seen))
                    logger.info(f"Requested color {color} not found in response, using {fallback_color} as fallback")
                    
                    pricing_data["color_pricing"][color] = pricing_data["color_pricing"][fallback_color]
                
                # Store in cache if enabled
                if use_cache:
                    self.cache.set(cache_key, pricing_data)
                    logger.info(f"Cached pricing data for {cache_key}")
                
                return pricing_data
            else:
                logger.warning(f"No listResponse found in pricing data for style: {style}")
                return None
        
        except Exception as e:
            logger.error(f"Error fetching SanMar pricing: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def get_pricing_by_inventory_key(self, inventory_key, size_index, use_cache=True):
        """
        Fetch pricing data directly from SanMar Pricing Service using inventoryKey/sizeIndex
        
        Args:
            inventory_key (str): SanMar inventory key
            size_index (str): SanMar size index
            use_cache (bool): Whether to use cached data (default: True)
        
        Returns:
            dict: Pricing data for the specified product or None if error
        """
        if not self._ready:
            logger.error("SanMar Pricing Service client not initialized")
            return None
        
        # Generate cache key
        cache_key = f"key:{inventory_key}:{size_index}"
        
        # Check cache if enabled
        if use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data:
                logger.info(f"Using cached pricing data for inventory key {inventory_key}")
                return cached_data
        
        # Prepare the request data
        request_data = {
            "arg0": {
                "style": "",
                "color": "",
                "size": "",
                "casePrice": None,
                "dozenPrice": None,
                "piecePrice": None,
                "salePrice": None,
                "myPrice": None,
                "inventoryKey": inventory_key,
                "sizeIndex": size_index
            },
            "arg1": {
                "sanMarCustomerNumber": self.customer_number,
                "sanMarUserName": self.username,
                "sanMarUserPassword": self.password
            }
        }
        
        logger.info(f"Requesting SanMar pricing for inventoryKey: {inventory_key}, sizeIndex: {size_index}")
        
        try:
            # Call the API
            response = self.client.service.getPricing(**request_data)
            
            # Check for errors
            if response.errorOccurred:
                logger.error(f"API error: {response.message}")
                return None
            
            # Process response as in get_pricing method
            # ...
            
            # Create our pricing data structure (similar to get_pricing)
            pricing_data = {
                "original_price": {},
                "sale_price": {},
                "program_price": {},
                "case_size": {},
                "color_pricing": {}
            }
            
            # Process the response (similar to get_pricing)
            # ...
            
            # Store in cache if enabled
            if use_cache:
                self.cache.set(cache_key, pricing_data)
                logger.info(f"Cached pricing data for {cache_key}")
            
            return pricing_data
        except Exception as e:
            logger.error(f"Error fetching SanMar pricing by inventory key: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
```

### 1.2 New API Endpoint

We'll add a new endpoint to app.py for AJAX pricing requests:

```python
@app.route('/api/pricing/<style>/<color>')
def api_pricing(style, color):
    """API endpoint for fetching pricing data for a specific style and color."""
    try:
        logger.info(f"API pricing request for style: {style}, color: {color}")
        
        # Check if we have valid credentials
        if not HAS_CREDENTIALS:
            logger.error("No SanMar API credentials available")
            return jsonify({
                "error": "API credentials not configured",
                "pricing": create_default_pricing(style, color)
            }), 500
        
        # Fetch pricing data
        pricing_data = None
        error_message = None
        
        # Try the direct SanMar Pricing Service first
        if sanmar_pricing_service and sanmar_pricing_service.is_ready():
            pricing_data = sanmar_pricing_service.get_pricing(style, color)
            
            if pricing_data:
                logger.info(f"Successfully retrieved pricing data for {style}, color: {color}")
                
                # Add cache headers to response
                response = jsonify(pricing_data)
                response.headers['Cache-Control'] = 'public, max-age=900'  # 15 minutes
                return response
        
        # Fallback to default pricing if API call fails
        logger.warning(f"Failed to retrieve pricing data for {style}, color: {color}")
        return jsonify({
            "error": "Failed to retrieve pricing data",
            "pricing": create_default_pricing(style, color)
        }), 500
        
    except Exception as e:
        logger.error(f"Error in API pricing endpoint: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return jsonify({
            "error": str(e),
            "pricing": create_default_pricing(style, color)
        }), 500
```

## 2. Frontend Implementation

### 2.1 Updated JavaScript for Color Swatch Selection

We'll modify the `selectColor` function in product.html to fetch pricing data via AJAX:

```javascript
// Function to handle color swatch clicks
function selectColor(catalogColor) {
    // Find the selected swatch
    console.log(`Selecting color: ${catalogColor}`);
    const selectedSwatch = document.querySelector(`.color-swatch[data-catalog-color="${catalogColor}"]`);
    if (!selectedSwatch) {
        console.error(`No swatch found for catalog color: ${catalogColor}`);
        return;
    }
    
    // Get the display color from the data attribute
    const displayColor = selectedSwatch.getAttribute('data-display-color');
    console.log(`Display color for ${catalogColor}: ${displayColor}`);
    
    // Update active color display
    document.getElementById('selected-color').textContent = displayColor;
    
    // Remove active class from all swatches
    const swatches = document.querySelectorAll('.color-swatch');
    swatches.forEach(swatch => {
        swatch.classList.remove('active');
    });
    
    // Add active class to selected swatch
    selectedSwatch.classList.add('active');
    
    // Update product image (if available)
    updateProductImage(selectedSwatch);
    
    // Check if we have cached pricing data
    const cacheKey = `pricing_${window.location.pathname}_${catalogColor}`;
    const cachedData = localStorage.getItem(cacheKey);
    
    if (cachedData) {
        // Parse the cached data
        try {
            const parsedData = JSON.parse(cachedData);
            const timestamp = parsedData.timestamp || 0;
            const pricingData = parsedData.data;
            
            // Check if the cache is still valid (less than 30 minutes old)
            if (timestamp && (Date.now() - timestamp < 30 * 60 * 1000)) {
                console.log('Using cached pricing data');
                updatePricingDisplay(pricingData, catalogColor);
                return;
            } else {
                console.log('Cached pricing data expired');
                localStorage.removeItem(cacheKey);
            }
        } catch (e) {
            console.error('Error parsing cached pricing data', e);
            localStorage.removeItem(cacheKey);
        }
    }
    
    // Show loading indicator
    showPricingLoadingState(catalogColor);
    
    // Fetch updated pricing data from API
    const style = window.location.pathname.split('/').pop();
    
    fetch(`/api/pricing/${style}/${catalogColor}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Cache the data
            localStorage.setItem(cacheKey, JSON.stringify({
                timestamp: Date.now(),
                data: data
            }));
            
            // Update the pricing display
            updatePricingDisplay(data, catalogColor);
        })
        .catch(error => {
            console.error('Error fetching pricing data:', error);
            showPricingError(catalogColor);
            
            // Show the existing static table as fallback
            showStaticPricingTable(catalogColor);
        });
}

// Helper function to update the product image
function updateProductImage(selectedSwatch) {
    const productImage = document.getElementById('product-image');
    if (productImage) {
        // Get the image URL from the data attribute
        const imageUrl = selectedSwatch.getAttribute('data-image');
        if (imageUrl) {
            productImage.src = imageUrl;
            const displayColor = selectedSwatch.getAttribute('data-display-color');
            productImage.alt = `${displayColor} ${productImage.alt.split(' ').slice(1).join(' ')}`;
        }
    }
}

// Function to show loading state for pricing
function showPricingLoadingState(catalogColor) {
    // Hide all inventory tables
    const tables = document.querySelectorAll('.inventory-tables');
    tables.forEach(table => {
        table.style.display = 'none';
    });
    
    // Show loading indicator
    const loadingIndicator = document.getElementById('pricing-loading') || createLoadingIndicator();
    loadingIndicator.style.display = 'block';
}

// Function to create loading indicator if it doesn't exist
function createLoadingIndicator() {
    const loadingIndicator = document.createElement('div');
    loadingIndicator.id = 'pricing-loading';
    loadingIndicator.className = 'text-center my-4';
    loadingIndicator.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading pricing data...</span>
        </div>
        <p class="mt-2">Loading pricing data...</p>
    `;
    
    // Insert after the color section
    const colorSection = document.querySelector('.color-section');
    if (colorSection) {
        colorSection.parentNode.insertBefore(loadingIndicator, colorSection.nextSibling);
    } else {
        document.querySelector('.container').appendChild(loadingIndicator);
    }
    
    return loadingIndicator;
}

// Function to show pricing error
function showPricingError(catalogColor) {
    // Hide loading indicator
    const loadingIndicator = document.getElementById('pricing-loading');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
    }
    
    // Show error message
    const errorMessage = document.getElementById('pricing-error') || createErrorMessage();
    errorMessage.style.display = 'block';
    
    // Hide after 5 seconds
    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 5000);
}

// Function to create error message if it doesn't exist
function createErrorMessage() {
    const errorMessage = document.createElement('div');
    errorMessage.id = 'pricing-error';
    errorMessage.className = 'alert alert-danger my-3';
    errorMessage.innerText = 'Error loading pricing data. Using cached pricing information.';
    
    // Insert after the color section
    const colorSection = document.querySelector('.color-section');
    if (colorSection) {
        colorSection.parentNode.insertBefore(errorMessage, colorSection.nextSibling);
    } else {
        document.querySelector('.container').appendChild(errorMessage);
    }
    
    return errorMessage;
}

// Function to show the static pricing table as fallback
function showStaticPricingTable(catalogColor) {
    // Show selected inventory table
    const selectedTableId = `inventory-${catalogColor}`;
    const selectedTable = document.getElementById(selectedTableId);
    if (selectedTable) {
        selectedTable.style.display = 'block';
    } else {
        console.error(`No inventory table found for catalog color: ${catalogColor}`);
    }
}

// Function to update the pricing display with dynamic data
function updatePricingDisplay(pricingData, catalogColor) {
    // Hide loading indicator
    const loadingIndicator = document.getElementById('pricing-loading');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
    }
    
    // Check if we have a static table for this color
    const staticTable = document.getElementById(`inventory-${catalogColor}`);
    
    if (staticTable) {
        // Update the existing table with new pricing data
        updatePricingTable(staticTable, pricingData, catalogColor);
        staticTable.style.display = 'block';
    } else {
        // Create a new table dynamically
        createDynamicPricingTable(pricingData, catalogColor);
    }
}

// Function to update an existing pricing table with new data
function updatePricingTable(table, pricingData, catalogColor) {
    const pricingTable = table.querySelector('.pricing-table');
    if (!pricingTable) return;
    
    // Get pricing rows
    const rows = pricingTable.querySelectorAll('tbody tr');
    
    // Update original price row
    updatePricingRow(rows[0], pricingData.original_price, catalogColor, pricingData);
    
    // Update sale price row
    updatePricingRow(rows[1], pricingData.sale_price, catalogColor, pricingData);
    
    // Update program price row
    updatePricingRow(rows[2], pricingData.program_price, catalogColor, pricingData);
    
    // Update case size row
    updatePricingRow(rows[3], pricingData.case_size, catalogColor, pricingData);
}

// Function to update a single pricing row
function updatePricingRow(row, priceData, catalogColor, fullPricingData) {
    if (!row) return;
    
    const cells = row.querySelectorAll('td');
    if (cells.length <= 1) return;
    
    // Skip the first cell (label)
    for (let i = 1; i < cells.length; i++) {
        const cell = cells[i];
        const sizeIndex = i - 1;
        const size = getSizeFromIndex(sizeIndex);
        
        if (size && priceData) {
            // Try color-specific pricing first
            if (fullPricingData.color_pricing && 
                fullPricingData.color_pricing[catalogColor] &&
                fullPricingData.color_pricing[catalogColor][row.dataset.priceType] &&
                fullPricingData.color_pricing[catalogColor][row.dataset.priceType][size] !== undefined) {
                
                cell.textContent = fullPricingData.color_pricing[catalogColor][row.dataset.priceType][size];
            }
            // Fall back to general pricing
            else if (priceData[size] !== undefined) {
                cell.textContent = priceData[size];
            }
        }
    }
}

// Function to get size from index
function getSizeFromIndex(index) {
    // This function should return the size at the given index
    // You'll need to adapt this to your actual size array
    const sizes = Array.from(document.querySelectorAll('.pricing-table th')).slice(1).map(th => th.textContent.trim());
    return sizes[index];
}

// Function to create a new dynamic pricing table
function createDynamicPricingTable(pricingData, catalogColor) {
    // Create table container
    const tableContainer = document.createElement('div');
    tableContainer.id = `dynamic-inventory-${catalogColor}`;
    tableContainer.className = 'inventory-tables';
    
    // Get display color
    const selectedSwatch = document.querySelector(`.color-swatch[data-catalog-color="${catalogColor}"]`);
    const displayColor = selectedSwatch ? selectedSwatch.getAttribute('data-display-color') : catalogColor;
    
    // Add header
    tableContainer.innerHTML = `
        <h4 class="mb-3">Inventory for ${displayColor}</h4>
        
        <div class="table-responsive mb-4">
            <table class="table table-bordered pricing-table">
                <thead class="table-secondary">
                    <tr>
                        <th>Pricing</th>
                        ${getSizesHeaderHTML()}
                    </tr>
                </thead>
                <tbody>
                    <tr data-price-type="original_price">
                        <td>Original Price: $</td>
                        ${getSizesPricingHTML(pricingData, 'original_price', catalogColor)}
                    </tr>
                    <tr class="sale-price" data-price-type="sale_price">
                        <td>Sale Price: $</td>
                        ${getSizesPricingHTML(pricingData, 'sale_price', catalogColor)}
                    </tr>
                    <tr class="program-price" data-price-type="program_price">
                        <td>Program Price: $</td>
                        ${getSizesPricingHTML(pricingData, 'program_price', catalogColor)}
                    </tr>
                    <tr data-price-type="case_size">
                        <td>Case Size</td>
                        ${getSizesPricingHTML(pricingData, 'case_size', catalogColor)}
                    </tr>
                </tbody>
            </table>
        </div>
    `;
    
    // Append to the page
    const inventoryTablesContainer = document.querySelector('.col-md-12');
    if (inventoryTablesContainer) {
        inventoryTablesContainer.appendChild(tableContainer);
    }
}

// Function to get sizes header HTML
function getSizesHeaderHTML() {
    const sizes = Array.from(document.querySelectorAll('.pricing-table th')).slice(1).map(th => th.textContent.trim());
    return sizes.map(size => `<th>${size}</th>`).join('');
}

// Function to get sizes pricing HTML
function getSizesPricingHTML(pricingData, priceType, catalogColor) {
    const sizes = Array.from(document.querySelectorAll('.pricing-table th')).slice(1).map(th => th.textContent.trim());
    
    return sizes.map(size => {
        let value = 0;
        
        // Try color-specific pricing first
        if (pricingData.color_pricing && 
            pricingData.color_pricing[catalogColor] && 
            pricingData.color_pricing[catalogColor][priceType] &&
            pricingData.color_pricing[catalogColor][priceType][size] !== undefined) {
            
            value = pricingData.color_pricing[catalogColor][priceType][size];
        }
        // Fall back to general pricing
        else if (pricingData[priceType] && pricingData[priceType][size] !== undefined) {
            value = pricingData[priceType][size];
        }
        
        return `<td>${value}</td>`;
    }).join('');
}

// Initialize with the first color
document.addEventListener('DOMContentLoaded', function() {
    const firstSwatch = document.querySelector('.color-swatch');
    if (firstSwatch) {
        const firstCatalogColor = firstSwatch.getAttribute('data-catalog-color');
        selectColor(firstCatalogColor);
    }
    
    // Add touch event listeners for mobile
    document.querySelectorAll('.color-swatch').forEach(swatch => {
        swatch.addEventListener('touchstart', function(e) {
            e.preventDefault();
            const catalogColor = this.getAttribute('data-catalog-color');
            selectColor(catalogColor);
        });
    });
});
```

### 2.2 CSS Additions for Loading States

Add these CSS rules to the existing styles:

```css
/* Loading and Error States */
#pricing-loading {
    display: none;
    margin: 20px 0;
}

#pricing-error {
    display: none;
    margin: 20px 0;
}

/* Transition for pricing tables */
.pricing-table td {
    transition: background-color 0.3s ease;
}

.pricing-table td.updating {
    background-color: #f8f9fa;
}

/* Responsive adjustments for mobile */
@media (max-width: 768px) {
    .color-swatch {
        width: 40px;
        height: 40px;
        margin: 3px;
    }
    
    .pricing-table th, .pricing-table td {
        font-size: 0.9rem;
        padding: 6px 4px;
    }
}
```

## 3. Implementation Considerations

### 3.1 Caching Strategy

1. **Server-side caching**:
   - In-memory cache with 15-minute TTL
   - Style+color combination as cache key
   - Automatic cleanup of expired entries

2. **Client-side caching**:
   - localStorage with 30-minute expiration
   - Style+color as cache key
   - Timestamp-based validation

### 3.2 Error Handling

1. **Network errors**: Fallback to cached data or static tables
2. **API errors**: Log detailed error information, return user-friendly messages
3. **Parsing errors**: Handle gracefully with fallback to default pricing

### 3.3 Mobile Considerations

1. **Touch events**: Support for both click and touch interactions
2. **Responsive design**: Adjustments for smaller screens
3. **Bandwidth conservation**: Use caching to reduce data usage

## 4. Testing

### 4.1 Test Scenarios

1. Test color selection with cached pricing data
2. Test color selection without cached data (first load)
3. Test with network errors (offline mode)
4. Test on mobile devices (touch events)
5. Test with different product styles and colors

### 4.2 Performance Tests

1. Measure page load times before and after implementation
2. Measure time to display pricing data with and without caching
3. Measure memory usage with large product catalogs