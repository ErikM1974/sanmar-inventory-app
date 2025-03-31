/**
 * Product Repository - Handles storage and retrieval of product data
 */

// Create a namespace for the product repository
window.ProductRepository = (function() {
    // Private cache storage
    const cache = {
        products: {},
        categories: {},
        images: {},
        searchResults: {},
        categoryImages: {}
    };
    
    // TTL for cache items in milliseconds
    const CACHE_TTL = {
        products: 60 * 60 * 1000, // 1 hour
        categories: 60 * 60 * 1000, // 1 hour
        images: 24 * 60 * 60 * 1000, // 24 hours
        searchResults: 15 * 60 * 1000, // 15 minutes
        categoryImages: 24 * 60 * 60 * 1000 // 24 hours
    };
    
    // Private methods
    const _isCacheValid = function(cacheItem) {
        if (!cacheItem || !cacheItem.timestamp) return false;
        const now = Date.now();
        const expirationTime = cacheItem.timestamp + cacheItem.ttl;
        return now < expirationTime;
    };
    
    const _setCacheItem = function(cacheKey, category, value, ttl) {
        if (!cache[category]) cache[category] = {};
        
        cache[category][cacheKey] = {
            data: value,
            timestamp: Date.now(),
            ttl: ttl || CACHE_TTL[category]
        };
    };
    
    const _getCacheItem = function(cacheKey, category) {
        if (!cache[category] || !cache[category][cacheKey]) return null;
        
        if (!_isCacheValid(cache[category][cacheKey])) {
            delete cache[category][cacheKey];
            return null;
        }
        
        return cache[category][cacheKey].data;
    };
    
    // Public API
    return {
        /**
         * Get a product by style
         * @param {string} style - The product style number
         * @param {function} onSuccess - Callback when product is retrieved
         * @param {function} onError - Callback when error occurs
         */
        getProduct: function(style, onSuccess, onError) {
            // Check cache first
            const cachedProduct = _getCacheItem(style, 'products');
            if (cachedProduct) {
                console.log(`Product ${style} retrieved from cache`);
                onSuccess(cachedProduct);
                return;
            }
            
            // Fetch from API
            fetch(`/api/product/${style}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Failed to fetch product: ${response.statusText}`);
                    }
                    return response.json();
                })
                .then(data => {
                    // Transform and cache the product data
                    const transformedProduct = window.DataTransformService.transformProductData(data);
                    _setCacheItem(style, 'products', transformedProduct);
                    onSuccess(transformedProduct);
                })
                .catch(error => {
                    console.error(`Error fetching product ${style}:`, error);
                    if (onError) onError(error);
                });
        },
        
        /**
         * Get all available images for a product
         * @param {string} style - The product style number
         * @param {string} color - Optional color to filter by
         * @returns {Array} - Array of cached image URLs or empty array if not found
         */
        getProductImages: function(style, color) {
            const cacheKey = color ? `${style}_${color}` : style;
            return _getCacheItem(cacheKey, 'images') || [];
        },
        
        /**
         * Cache product images
         * @param {string} style - The product style number
         * @param {Array} images - Array of image URLs
         * @param {string} color - Optional color to filter by
         */
        cacheProductImages: function(style, images, color) {
            const cacheKey = color ? `${style}_${color}` : style;
            _setCacheItem(cacheKey, 'images', images);
        },
        
        /**
         * Get image for a product category
         * @param {string} categoryId - The category identifier
         * @param {function} onSuccess - Callback when image is retrieved
         * @param {function} onError - Callback when error occurs
         */
        getCategoryImage: function(categoryId, onSuccess, onError) {
            // Check cache first
            const cachedImage = _getCacheItem(categoryId, 'categoryImages');
            if (cachedImage) {
                console.log(`Category image for ${categoryId} retrieved from cache`);
                onSuccess(cachedImage);
                return;
            }
            
            // Fetch from API
            fetch(`/api/category-image?category=${encodeURIComponent(categoryId)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Failed to fetch category image: ${response.statusText}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data && data.imageUrl) {
                        _setCacheItem(categoryId, 'categoryImages', data.imageUrl);
                        console.log(`Found image for ${categoryId}: ${data.imageUrl}`);
                        onSuccess(data.imageUrl);
                    } else if (data && data.image_url) {
                        // Backward compatibility with older API format
                        _setCacheItem(categoryId, 'categoryImages', data.image_url);
                        console.log(`Found image (old format) for ${categoryId}: ${data.image_url}`);
                        onSuccess(data.image_url);
                    } else {
                        // If no image, try to get a model image for a representative product
                        const categoryName = categoryId.toUpperCase();
                        const modelProductMap = {
                            'POLOS': 'K500',
                            'TSHIRTS': 'PC61',
                            'OUTERWEAR': 'J790',
                            'HEADWEAR': 'C112',
                            'BAGS': 'BG100',
                            'WORKWEAR': 'CS410'
                        };
                        
                        if (modelProductMap[categoryName] && window.SanmarApiService) {
                            // Try to get model image from our new service
                            window.SanmarApiService.getModelImage(modelProductMap[categoryName])
                                .then(modelUrl => {
                                    if (modelUrl) {
                                        _setCacheItem(categoryId, 'categoryImages', modelUrl);
                                        console.log(`Found model image for ${categoryId}: ${modelUrl}`);
                                        onSuccess(modelUrl);
                                    } else {
                                        throw new Error('No model image found');
                                    }
                                })
                                .catch(err => {
                                    throw new Error('Error fetching model image: ' + err.message);
                                });
                        } else {
                            throw new Error('No image found for category');
                        }
                    }
                })
                .catch(error => {
                    console.error(`Error fetching category image for ${categoryId}:`, error);
                    if (onError) onError(error);
                });
        },
        /**
         * Get subcategories for a category
         * @param {string} categoryId - The category identifier
         * @param {function} onSuccess - Callback when subcategories are retrieved
         * @param {function} onError - Callback when error occurs
         */
        getSubcategories: function(categoryId, onSuccess, onError) {
            // Check cache first
            const cacheKey = `subcategories_${categoryId}`;
            const cachedSubcategories = _getCacheItem(cacheKey, 'categories');
            if (cachedSubcategories) {
                console.log(`Subcategories for ${categoryId} retrieved from cache`);
                onSuccess(cachedSubcategories);
                return;
            }
            
            // Fetch from API
            fetch(`/api/subcategories?category=${encodeURIComponent(categoryId)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Failed to fetch subcategories: ${response.statusText}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data && data.subcategories) {
                        _setCacheItem(cacheKey, 'categories', data.subcategories);
                        console.log(`Found ${data.subcategories.length} subcategories for ${categoryId}`);
                        onSuccess(data.subcategories);
                    } else {
                        onSuccess([]);
                    }
                })
                .catch(error => {
                    console.error(`Error fetching subcategories for ${categoryId}:`, error);
                    if (onError) onError(error);
                });
        },
        
        /**
         * Clear all cached data
         */
        clearCache: function() {
            for (const category in cache) {
                cache[category] = {};
            }
            console.log('Cache cleared');
        }
    };
})();