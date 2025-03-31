/**
 * Data Transform Service - Handles transforming API data to consistent formats
 */

// Create a namespace for data transformation utilities
window.DataTransformService = (function() {
    // Private utility functions
    
    /**
     * Extract image URLs from a product
     * @param {Object} product - The product data from API
     * @return {Object} - Object with categorized image URLs
     */
    const _extractImages = function(product) {
        const images = {
            main: null,
            thumbnails: [],
            color: [],
            model: {
                front: null,
                back: null,
                side: null,
                threeQ: null
            },
            flat: {
                front: null,
                back: null
            },
            swatch: null,
            colorSquare: null,
            brandLogo: null
        };
        
        // Early return if no product or image info
        if (!product || !product.productImageInfo) return images;
        
        const imageInfo = product.productImageInfo;
        
        // Extract main product image
        images.main = imageInfo.productImage || null;
        
        // Extract thumbnail
        if (imageInfo.thumbnailImage) {
            images.thumbnails.push(imageInfo.thumbnailImage);
        }
        
        // Extract color specific images
        if (imageInfo.colorProductImage) {
            images.color.push(imageInfo.colorProductImage);
        }
        
        // Extract model images
        images.model.front = imageInfo.frontModel || null;
        images.model.back = imageInfo.backModel || null;
        images.model.side = imageInfo.sideModel || null;
        images.model.threeQ = imageInfo.threeQModel || null;
        
        // Extract flat images
        images.flat.front = imageInfo.frontFlat || null;
        images.flat.back = imageInfo.backFlat || null;
        
        // Extract swatches and brand logo
        images.swatch = imageInfo.colorSwatchImage || null;
        images.colorSquare = imageInfo.colorSquareImage || null;
        images.brandLogo = imageInfo.brandLogoImage || null;
        
        return images;
    };
    
    /**
     * Extract pricing information from a product
     * @param {Object} product - The product data from API
     * @return {Object} - Object with normalized pricing data
     */
    const _extractPricing = function(product) {
        const pricing = {
            piece: {
                regular: null,
                sale: null
            },
            dozen: {
                regular: null,
                sale: null
            },
            case: {
                regular: null,
                sale: null,
                size: null
            },
            priceCode: null,
            priceText: null,
            onSale: false,
            saleStartDate: null,
            saleEndDate: null
        };
        
        // Early return if no product or price info
        if (!product || !product.productPriceInfo) return pricing;
        
        const priceInfo = product.productPriceInfo;
        
        // Extract piece prices
        pricing.piece.regular = priceInfo.piecePrice || null;
        pricing.piece.sale = priceInfo.pieceSalePrice || null;
        
        // Extract dozen prices
        pricing.dozen.regular = priceInfo.dozenPrice || null;
        pricing.dozen.sale = priceInfo.dozenSalePrice || null;
        
        // Extract case prices
        pricing.case.regular = priceInfo.casePrice || null;
        pricing.case.sale = priceInfo.caseSalePrice || null;
        
        // Extract other pricing information
        pricing.priceCode = priceInfo.priceCode || null;
        pricing.priceText = priceInfo.priceText || null;
        pricing.onSale = !!priceInfo.pieceSalePrice || !!priceInfo.dozenSalePrice || !!priceInfo.caseSalePrice;
        pricing.saleStartDate = priceInfo.saleStartDate || null;
        pricing.saleEndDate = priceInfo.saleEndDate || null;
        
        // Extract case size if available
        if (product.productBasicInfo && product.productBasicInfo.caseSize) {
            pricing.case.size = product.productBasicInfo.caseSize;
        }
        
        return pricing;
    };
    
    /**
     * Extract basic product information
     * @param {Object} product - The product data from API
     * @return {Object} - Object with basic product data
     */
    const _extractBasicInfo = function(product) {
        const info = {
            style: null,
            title: null,
            description: null,
            brand: null,
            color: null,
            size: null,
            category: null,
            keywords: null,
            availableSizes: null,
            inventoryKey: null,
            uniqueKey: null,
            status: null
        };
        
        // Early return if no product or basic info
        if (!product || !product.productBasicInfo) return info;
        
        const basicInfo = product.productBasicInfo;
        
        // Extract basic product information
        info.style = basicInfo.style || null;
        info.title = basicInfo.productTitle || null;
        info.description = basicInfo.productDescription || null;
        info.brand = basicInfo.brandName || null;
        info.color = basicInfo.color || null;
        info.size = basicInfo.size || null;
        info.category = basicInfo.category || null;
        info.keywords = basicInfo.keywords || null;
        info.availableSizes = basicInfo.availableSizes || null;
        info.inventoryKey = basicInfo.inventoryKey || null;
        info.uniqueKey = basicInfo.uniqueKey || null;
        info.status = basicInfo.productStatus || null;
        
        return info;
    };
    
    // Public API
    return {
        /**
         * Transform raw product data from API to a consistent format
         * @param {Object} data - The raw API response
         * @return {Object} - Normalized product data
         */
        transformProductData: function(data) {
            if (!data || !data.listResponse || !Array.isArray(data.listResponse)) {
                return {
                    success: false,
                    error: "Invalid product data",
                    raw: data
                };
            }
            
            const products = [];
            
            // Process each product in the response
            data.listResponse.forEach(product => {
                products.push({
                    info: _extractBasicInfo(product),
                    images: _extractImages(product),
                    pricing: _extractPricing(product)
                });
            });
            
            return {
                success: true,
                products: products,
                message: data.message || "",
                errorOccurred: !!data.errorOccured,
                raw: data
            };
        },
        
        /**
         * Get the best available image for a product
         * @param {Object} product - Transformed product data
         * @return {string|null} - URL of the best available image
         */
        getBestProductImage: function(product) {
            if (!product || !product.images) return null;
            
            // Priority order for images
            return product.images.model.front || 
                   product.images.flat.front || 
                   product.images.model.threeQ ||
                   product.images.model.side || 
                   product.images.model.back || 
                   product.images.flat.back || 
                   product.images.main || 
                   (product.images.thumbnails.length > 0 ? product.images.thumbnails[0] : null) ||
                   null;
        },
        
        /**
         * Format a price for display
         * @param {number} price - The price to format
         * @param {Object} options - Formatting options
         * @return {string} - Formatted price string
         */
        formatPrice: function(price, options = {}) {
            if (price === null || price === undefined) return 'N/A';
            
            const defaults = {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            };
            
            const formatOptions = { ...defaults, ...options };
            
            return new Intl.NumberFormat('en-US', formatOptions).format(price);
        }
    };
})();