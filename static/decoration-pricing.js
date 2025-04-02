/**
 * Northwest Custom Apparel - Decoration Pricing Module
 * Handles pricing for various decoration methods:
 * - Embroidery
 * - Screen Printing
 * - Direct to Garment (DTG)
 * - Heat Transfer
 * - Cap Embroidery
 */

/**
 * Calculate decoration pricing based on method, quantity and options
 * @param {string} method - Decoration method (embroidery, screenPrint, dtg, heatTransfer, capEmbroidery)
 * @param {number} quantity - Total quantity of items
 * @param {number} locations - Number of decoration locations
 * @param {Array} options - Array of optional features/add-ons
 * @returns {Object} - Pricing details including total and breakdown
 */
function calculateDecorationPrice(method, quantity, locations = 1, options = []) {
    // Default result structure
    const result = {
        total: 0,
        breakdown: {
            basePrice: 0,
            volumeDiscount: 0,
            optionsCost: 0,
            multiLocationCost: 0
        }
    };
    
    // Validate inputs
    if (!method || quantity <= 0 || locations <= 0) {
        return result;
    }
    
    // Calculate base price based on method and quantity
    switch (method.toLowerCase()) {
        case 'embroidery':
            result.breakdown.basePrice = calculateEmbroideryPrice(quantity);
            break;
            
        case 'screenprint':
            result.breakdown.basePrice = calculateScreenPrintPrice(quantity);
            break;
            
        case 'dtg':
            result.breakdown.basePrice = calculateDTGPrice(quantity);
            break;
            
        case 'heattransfer':
            result.breakdown.basePrice = calculateHeatTransferPrice(quantity);
            break;
            
        case 'capembroidery':
            result.breakdown.basePrice = calculateCapEmbroideryPrice(quantity);
            break;
            
        default:
            // Unknown method, return zero pricing
            return result;
    }
    
    // Apply volume discount
    result.breakdown.volumeDiscount = calculateVolumeDiscount(result.breakdown.basePrice, quantity);
    
    // Calculate cost for additional options
    result.breakdown.optionsCost = calculateOptionsPrice(method, options, quantity);
    
    // Calculate cost for multiple locations
    result.breakdown.multiLocationCost = calculateMultiLocationCost(method, locations, quantity);
    
    // Calculate total
    result.total = result.breakdown.basePrice - 
                  result.breakdown.volumeDiscount + 
                  result.breakdown.optionsCost + 
                  result.breakdown.multiLocationCost;
    
    // Round to 2 decimal places
    result.total = Math.round(result.total * 100) / 100;
    
    return result;
}

/**
 * Calculate embroidery price based on quantity
 * @param {number} quantity - Number of items
 * @returns {number} - Base price
 */
function calculateEmbroideryPrice(quantity) {
    let price = 0;
    
    // Tiered pricing based on quantity
    if (quantity < 12) {
        price = 7.50 * quantity;
    } else if (quantity < 24) {
        price = 6.75 * quantity;
    } else if (quantity < 50) {
        price = 6.00 * quantity;
    } else if (quantity < 100) {
        price = 5.50 * quantity;
    } else if (quantity < 250) {
        price = 5.00 * quantity;
    } else {
        price = 4.50 * quantity;
    }
    
    return price;
}

/**
 * Calculate screen printing price based on quantity
 * @param {number} quantity - Number of items
 * @returns {number} - Base price
 */
function calculateScreenPrintPrice(quantity) {
    let price = 0;
    
    // Tiered pricing based on quantity
    if (quantity < 12) {
        price = 8.00 * quantity;
    } else if (quantity < 24) {
        price = 6.50 * quantity;
    } else if (quantity < 50) {
        price = 5.50 * quantity;
    } else if (quantity < 100) {
        price = 4.75 * quantity;
    } else if (quantity < 250) {
        price = 4.00 * quantity;
    } else {
        price = 3.50 * quantity;
    }
    
    return price;
}

/**
 * Calculate DTG (Direct to Garment) price based on quantity
 * @param {number} quantity - Number of items
 * @returns {number} - Base price
 */
function calculateDTGPrice(quantity) {
    let price = 0;
    
    // Tiered pricing based on quantity
    if (quantity < 12) {
        price = 9.50 * quantity;
    } else if (quantity < 24) {
        price = 9.00 * quantity;
    } else if (quantity < 50) {
        price = 8.50 * quantity;
    } else if (quantity < 100) {
        price = 8.00 * quantity;
    } else if (quantity < 250) {
        price = 7.50 * quantity;
    } else {
        price = 7.00 * quantity;
    }
    
    return price;
}

/**
 * Calculate heat transfer price based on quantity
 * @param {number} quantity - Number of items
 * @returns {number} - Base price
 */
function calculateHeatTransferPrice(quantity) {
    let price = 0;
    
    // Tiered pricing based on quantity
    if (quantity < 12) {
        price = 7.00 * quantity;
    } else if (quantity < 24) {
        price = 6.50 * quantity;
    } else if (quantity < 50) {
        price = 6.00 * quantity;
    } else if (quantity < 100) {
        price = 5.50 * quantity;
    } else if (quantity < 250) {
        price = 5.00 * quantity;
    } else {
        price = 4.50 * quantity;
    }
    
    return price;
}

/**
 * Calculate cap embroidery price based on quantity
 * @param {number} quantity - Number of items
 * @returns {number} - Base price
 */
function calculateCapEmbroideryPrice(quantity) {
    let price = 0;
    
    // Tiered pricing based on quantity
    if (quantity < 12) {
        price = 8.50 * quantity;
    } else if (quantity < 24) {
        price = 8.00 * quantity;
    } else if (quantity < 50) {
        price = 7.50 * quantity;
    } else if (quantity < 100) {
        price = 7.00 * quantity;
    } else if (quantity < 250) {
        price = 6.50 * quantity;
    } else {
        price = 6.00 * quantity;
    }
    
    return price;
}

/**
 * Calculate volume discount based on quantity
 * @param {number} basePrice - Base price before discount
 * @param {number} quantity - Number of items
 * @returns {number} - Discount amount
 */
function calculateVolumeDiscount(basePrice, quantity) {
    let discountPercentage = 0;
    
    // Determine discount percentage based on quantity
    if (quantity >= 500) {
        discountPercentage = 0.10; // 10% discount for 500+ pieces
    } else if (quantity >= 250) {
        discountPercentage = 0.08; // 8% discount for 250-499 pieces
    } else if (quantity >= 100) {
        discountPercentage = 0.05; // 5% discount for 100-249 pieces
    } else if (quantity >= 50) {
        discountPercentage = 0.03; // 3% discount for 50-99 pieces
    }
    
    return basePrice * discountPercentage;
}

/**
 * Calculate additional cost for options/add-ons
 * @param {string} method - Decoration method
 * @param {Array} options - Array of options
 * @param {number} quantity - Number of items
 * @returns {number} - Additional cost
 */
function calculateOptionsPrice(method, options, quantity) {
    if (!options || !Array.isArray(options) || options.length === 0) {
        return 0;
    }
    
    let optionsCost = 0;
    
    // Process each option based on decoration method
    for (let option of options) {
        switch (method.toLowerCase()) {
            case 'embroidery':
                if (option === 'Metallic Thread') {
                    optionsCost += 1.50 * quantity;
                } else if (option === 'Oversized Design (8,000-15,000 stitches)') {
                    optionsCost += 3.00 * quantity;
                }
                break;
                
            case 'capembroidery':
                if (option === 'Metallic Thread') {
                    optionsCost += 1.50 * quantity;
                }
                break;
                
            case 'screenprint':
                if (option === 'Flash Cure') {
                    optionsCost += 0.75 * quantity;
                } else if (option === 'Oversize Print') {
                    optionsCost += 1.00 * quantity;
                }
                break;
                
            case 'dtg':
                if (option === 'Oversize Print') {
                    optionsCost += 2.00 * quantity;
                } else if (option === 'Pre-treatment') {
                    optionsCost += 1.00 * quantity;
                }
                break;
                
            case 'heattransfer':
                if (option === 'Metallic Vinyl') {
                    optionsCost += 1.00 * quantity;
                } else if (option === 'Glitter Vinyl') {
                    optionsCost += 1.50 * quantity;
                }
                break;
        }
    }
    
    return optionsCost;
}

/**
 * Calculate cost for multiple decoration locations
 * @param {string} method - Decoration method
 * @param {number} locations - Number of locations
 * @param {number} quantity - Number of items
 * @returns {number} - Additional cost for multiple locations
 */
function calculateMultiLocationCost(method, locations, quantity) {
    if (locations <= 1) {
        return 0;
    }
    
    // Additional locations cost (locations - 1) * discount * base price for one location
    const additionalLocations = locations - 1;
    let locationMultiplier = 0;
    
    switch (method.toLowerCase()) {
        case 'embroidery':
        case 'capembroidery':
            locationMultiplier = 0.75; // 75% of first location price for each additional location
            break;
            
        case 'screenprint':
            locationMultiplier = 0.65; // 65% of first location price for each additional location
            break;
            
        case 'dtg':
            locationMultiplier = 0.85; // 85% of first location price for each additional location
            break;
            
        case 'heattransfer':
            locationMultiplier = 0.70; // 70% of first location price for each additional location
            break;
    }
    
    // Get base price for one location
    let basePrice = 0;
    switch (method.toLowerCase()) {
        case 'embroidery':
            basePrice = calculateEmbroideryPrice(quantity) / quantity;
            break;
            
        case 'screenprint':
            basePrice = calculateScreenPrintPrice(quantity) / quantity;
            break;
            
        case 'dtg':
            basePrice = calculateDTGPrice(quantity) / quantity;
            break;
            
        case 'heattransfer':
            basePrice = calculateHeatTransferPrice(quantity) / quantity;
            break;
            
        case 'capembroidery':
            basePrice = calculateCapEmbroideryPrice(quantity) / quantity;
            break;
    }
    
    return additionalLocations * locationMultiplier * basePrice * quantity;
}

// If running in Node.js environment, export the module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        calculateDecorationPrice,
        calculateEmbroideryPrice,
        calculateScreenPrintPrice,
        calculateDTGPrice,
        calculateHeatTransferPrice,
        calculateCapEmbroideryPrice
    };
}