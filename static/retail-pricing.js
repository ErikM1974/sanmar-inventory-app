/**
 * Northwest Custom Apparel - Retail Pricing Module
 * Handles retail pricing calculations with a standard 40% margin on case prices
 * Also handles size upcharges for larger sizes
 */

const retailPricing = {
    /**
     * Calculate retail price with a 40% margin on case price
     * @param {number} casePrice - The case price from SanMar
     * @param {string} size - The garment size
     * @returns {number} - The calculated retail price
     */
    calculateRetailPrice: function(casePrice, size) {
        if (!casePrice || isNaN(casePrice)) {
            return 0;
        }
        
        // Base retail price with 40% margin
        // Formula: Retail = Case / (1 - margin)
        let retailPrice = casePrice / 0.6;
        
        // Add size upcharges for larger sizes
        const sizeUpcharges = {
            '2XL': 2.00,
            'XXL': 2.00,
            '3XL': 3.00,
            'XXXL': 3.00,
            '4XL': 4.00,
            'XXXXL': 4.00,
            '5XL': 5.00,
            'XXXXXL': 5.00,
            '6XL': 6.00,
            'XXXXXXL': 6.00
        };
        
        // Apply size upcharge if applicable
        if (size && sizeUpcharges[size]) {
            retailPrice += sizeUpcharges[size];
        }
        
        // Round to 2 decimal places
        return Math.round(retailPrice * 100) / 100;
    },
    
    /**
     * Calculate discount percentage from case to retail
     * @param {number} casePrice - The case price
     * @param {number} retailPrice - The retail price
     * @returns {number} - The discount percentage
     */
    calculateDiscount: function(casePrice, retailPrice) {
        if (!casePrice || !retailPrice || isNaN(casePrice) || isNaN(retailPrice)) {
            return 0;
        }
        
        return Math.round(((retailPrice - casePrice) / retailPrice) * 100);
    },
    
    /**
     * Format price as currency string
     * @param {number} price - The price to format
     * @returns {string} - Formatted price string
     */
    formatPrice: function(price) {
        if (price === null || price === undefined || isNaN(price)) {
            return '$0.00';
        }
        
        return '$' + price.toFixed(2);
    },
    
    /**
     * Calculate quantity discount price
     * @param {number} basePrice - The base retail price
     * @param {number} quantity - Quantity ordered
     * @returns {number} - Discounted price
     */
    calculateQuantityDiscount: function(basePrice, quantity) {
        if (!basePrice || isNaN(basePrice)) {
            return 0;
        }
        
        let discountPercentage = 0;
        
        // Apply discount based on quantity
        if (quantity >= 500) {
            discountPercentage = 0.15; // 15% discount for 500+ pieces
        } else if (quantity >= 250) {
            discountPercentage = 0.10; // 10% discount for 250-499 pieces
        } else if (quantity >= 100) {
            discountPercentage = 0.07; // 7% discount for 100-249 pieces
        } else if (quantity >= 50) {
            discountPercentage = 0.05; // 5% discount for 50-99 pieces
        } else if (quantity >= 24) {
            discountPercentage = 0.03; // 3% discount for 24-49 pieces
        }
        
        // Apply discount and round to 2 decimal places
        const discountedPrice = basePrice * (1 - discountPercentage);
        return Math.round(discountedPrice * 100) / 100;
    }
};

// If running in Node.js environment, export the module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = retailPricing;
}