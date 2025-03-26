// Function to set up the decoration tabs
function setupDecorationTabs() {
    // Get all tab navigation items
    const tabItems = document.querySelectorAll('.tab-item');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Add click event listeners to tab items
    tabItems.forEach(item => {
        item.addEventListener('click', function() {
            // Remove active class from all tabs
            tabItems.forEach(tab => tab.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to current tab
            this.classList.add('active');
            
            // Show corresponding content
            const tabId = this.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
            
            // If this is a decoration tab (not base-product), fetch pricing data
            if (tabId !== 'base-product') {
                updateDecorationPricing(tabId);
            }
        });
    });
    
    // Set up location selection change events
    setupDecorationOptions();
}

// Function to handle changes to decoration options (location, colors, etc.)
function setupDecorationOptions() {
    // Get all decoration select dropdowns
    const decorationSelects = document.querySelectorAll('.decoration-select');
    
    // Add change event listeners
    decorationSelects.forEach(select => {
        select.addEventListener('change', function() {
            // Get the decoration type (tab id) from the closest tab content
            const decorationType = this.closest('.tab-content').id;
            
            // Get all options for this decoration type
            const options = {};
            const selects = document.querySelectorAll(`#${decorationType} .decoration-select`);
            selects.forEach(s => {
                options[s.id] = s.value;
            });
            
            // Update pricing with new options
            updateDecorationPricing(decorationType, options);
        });
    });
}

// Function to fetch decoration pricing data from the server
function updateDecorationPricing(decorationType, options = {}) {
    // Get the currently selected color
    const selectedColor = document.getElementById('selected-color').textContent;
    
    // Get the style from the URL path
    const path = window.location.pathname;
    const style = path.includes('/') ? path.split('/').pop() : path;
    
    if (!style || !selectedColor) {
        console.error('Missing style or color');
        return;
    }
    
    console.log(`Fetching ${decorationType} pricing for style: ${style}, color: ${selectedColor}, options:`, options);
    
    // Get default location if not specified
    const location = options.location || 
                    (options[`${decorationType}-location`]) || 
                    document.querySelector(`#${decorationType}-location`)?.value || 
                    'left-chest';
    
    // For screen print, get colors if not specified
    const colors = options.colors || 
                  (options['screenprint-colors']) || 
                  document.querySelector('#screenprint-colors')?.value || 
                  '1';
    
    // For demo purposes, we'll just update the tables with mock data
    // In a production environment, you would make an API call here
    
    // Show loading indicator
    const loadingElement = document.querySelector(`#loading-${decorationType}`);
    if (loadingElement) {
        loadingElement.style.display = 'block';
    }
    
    // Hide any previous error message
    const errorElement = document.querySelector(`#error-${decorationType}`);
    if (errorElement) {
        errorElement.style.display = 'none';
    }
    
    // Simulate API call with timeout
    setTimeout(() => {
        // Hide loading indicator
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
        
        // Get mock pricing data based on decoration type and options
        const mockData = getMockDecorationPricing(decorationType, location, colors, style, selectedColor);
        
        // Update the pricing table
        updateDecorationTable(decorationType, mockData);
    }, 500);
    
    /* 
    // Uncomment this code when you have a real API endpoint
    
    // Build the API URL for decoration pricing
    const url = new URL(`${window.location.origin}/api/decoration-pricing`);
    url.searchParams.append('style', style);
    url.searchParams.append('color', selectedColor);
    url.searchParams.append('decoration', decorationType);
    url.searchParams.append('location', location);
    
    if (decorationType === 'screen-print') {
        url.searchParams.append('colors', colors);
    }
    
    // Make the request
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Hide loading indicator
            if (loadingElement) {
                loadingElement.style.display = 'none';
            }
            
            // Update the pricing table with the received data
            updateDecorationTable(decorationType, data);
        })
        .catch(error => {
            console.error(`Error fetching decoration pricing: ${error.message}`);
            
            // Hide loading indicator
            if (loadingElement) {
                loadingElement.style.display = 'none';
            }
            
            // Show error message
            if (errorElement) {
                errorElement.style.display = 'block';
            }
            
            // Use mock data as fallback
            const mockData = getMockDecorationPricing(decorationType, location, colors, style, selectedColor);
            updateDecorationTable(decorationType, mockData);
        });
    */
}

// Function to generate mock decoration pricing data
function getMockDecorationPricing(decorationType, location, colors, style, color) {
    // Base pricing for products (just mock data)
    const baseProductPrices = {
        '12': 14.15,
        '24': 13.95,
        '48': 13.75,
        '72': 13.55,
        '144': 13.45
    };
    
    // Location multipliers
    const locationMultipliers = {
        'left-chest': 1.0,
        'right-chest': 1.0,
        'full-front': 1.5,
        'full-back': 1.7,
        'sleeve': 1.2
    };
    
    // Base decoration prices by decoration type
    const decorationBasePrices = {
        'embroidery': {
            '12': 5.75,
            '24': 4.95,
            '48': 4.35,
            '72': 4.15,
            '144': 3.95
        },
        'screen-print': {
            '12': 4.25,
            '24': 3.85,
            '48': 3.35,
            '72': 3.15,
            '144': 2.95
        },
        'dtg': {
            '12': 7.25,
            '24': 6.85,
            '48': 6.35,
            '72': 6.15,
            '144': 5.95
        },
        'dtf': {
            '12': 6.75,
            '24': 6.35,
            '48': 5.85,
            '72': 5.65,
            '144': 5.45
        }
    };
    
    // Colors multiplier for screen printing
    const colorsMultiplier = {
        '1': 1.0,
        '2': 1.3,
        '3': 1.6,
        '4': 1.9
    };
    
    // Calculate decoration prices based on type, location, and colors
    const decorationPrices = {};
    const totalPrices = {};
    
    // Get the location multiplier
    const locMultiplier = locationMultipliers[location] || 1.0;
    
    // Get the colors multiplier if applicable
    const colMultiplier = decorationType === 'screen-print' ? (colorsMultiplier[colors] || 1.0) : 1.0;
    
    // Calculate prices for each quantity
    for (const qty in baseProductPrices) {
        const basePrice = baseProductPrices[qty];
        
        // Calculate decoration price with multipliers
        const baseDecPrice = decorationBasePrices[decorationType][qty] || 3.99;
        const decPrice = baseDecPrice * locMultiplier * colMultiplier;
        
        // Store calculated prices
        decorationPrices[qty] = parseFloat(decPrice.toFixed(2));
        totalPrices[qty] = parseFloat((basePrice + decPrice).toFixed(2));
    }
    
    return {
        base_prices: baseProductPrices,
        decoration_prices: decorationPrices,
        total_prices: totalPrices
    };
}

// Function to update the decoration pricing table
function updateDecorationTable(decorationType, data) {
    const table = document.querySelector(`#${decorationType} .pricing-table`);
    if (!table) {
        console.error(`Pricing table not found for ${decorationType}`);
        return;
    }
    
    // Get the rows
    const baseProductRow = table.querySelector('tbody tr:nth-child(1)');
    const decorationRow = table.querySelector('tbody tr:nth-child(2)');
    const totalRow = table.querySelector('tbody tr:nth-child(3)');
    
    // Get the quantity breaks from table headers
    const quantities = Array.from(
        table.querySelectorAll('thead th:not(:first-child)')
    ).map(th => th.textContent.trim());
    
    // Update base product prices
    if (baseProductRow && data.base_prices) {
        const cells = baseProductRow.querySelectorAll('td.price-value');
        cells.forEach((cell, index) => {
            const qty = quantities[index];
            if (qty && data.base_prices[qty] !== undefined) {
                cell.textContent = `$${data.base_prices[qty].toFixed(2)}`;
            }
        });
    }
    
    // Update decoration prices
    if (decorationRow && data.decoration_prices) {
        const cells = decorationRow.querySelectorAll('td.price-value');
        cells.forEach((cell, index) => {
            const qty = quantities[index];
            if (qty && data.decoration_prices[qty] !== undefined) {
                cell.textContent = `$${data.decoration_prices[qty].toFixed(2)}`;
            }
        });
    }
    
    // Update total prices
    if (totalRow && data.total_prices) {
        const cells = totalRow.querySelectorAll('td.price-value');
        cells.forEach((cell, index) => {
            const qty = quantities[index];
            if (qty && data.total_prices[qty] !== undefined) {
                cell.textContent = `$${data.total_prices[qty].toFixed(2)}`;
            }
        });
    }
    
    console.log(`Updated ${decorationType} pricing table with data`, data);
}