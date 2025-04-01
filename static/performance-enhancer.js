/**
 * Performance enhancement for SanMar Inventory App
 * This script provides client-side optimizations to improve application performance
 */

// Create a self-executing function to avoid polluting global scope
(function() {
    'use strict';

    // Configuration
    const config = {
        cacheEnabled: true,
        cacheTTL: 30 * 60 * 1000, // 30 minutes in milliseconds
        batchSize: 10, // Number of items to load in a batch
        lazyLoadImages: true,
        prefetchRelatedProducts: true,
        apiThrottleMs: 100, // Minimum time between API calls
        debugMode: false // Set to true to enable debug logs
    };

    // Cache storage
    const cache = {
        pricing: {},
        products: {},
        colors: {},
        inventory: {}
    };

    // Debug logger
    const logger = {
        debug: function(message) {
            if (config.debugMode) {
                console.log(`[SanMar Debug] ${message}`);
            }
        },
        info: function(message) {
            console.log(`[SanMar Info] ${message}`);
        },
        warn: function(message) {
            console.warn(`[SanMar Warning] ${message}`);
        },
        error: function(message) {
            console.error(`[SanMar Error] ${message}`);
        },
        performance: function(label, startTime) {
            const duration = performance.now() - startTime;
            this.debug(`${label}: ${duration.toFixed(2)}ms`);
        }
    };

    // Initialize performance monitoring
    logger.info('Performance enhancements loaded');
    const initTime = performance.now();

    /**
     * Cache API responses in localStorage for faster access
     * @param {string} key - Cache key
     * @param {Object} data - Data to cache
     * @param {number} ttl - Time to live in milliseconds
     */
    function cacheData(key, data, ttl = config.cacheTTL) {
        if (!config.cacheEnabled) return;
        
        try {
            const cacheItem = {
                data: data,
                timestamp: Date.now(),
                expires: Date.now() + ttl
            };
            
            // Try to use localStorage for persistence
            try {
                localStorage.setItem(`sanmar_${key}`, JSON.stringify(cacheItem));
            } catch (e) {
                // If localStorage fails (quota exceeded, etc), use in-memory cache
                logger.warn(`LocalStorage error: ${e.message}. Using in-memory cache.`);
                cache[key] = cacheItem;
            }
            
            logger.debug(`Cached data for key: ${key}`);
        } catch (e) {
            logger.error(`Error caching data: ${e.message}`);
        }
    }

    /**
     * Retrieve cached data if available and not expired
     * @param {string} key - Cache key
     * @returns {Object|null} - Cached data or null if not found/expired
     */
    function getCachedData(key) {
        if (!config.cacheEnabled) return null;
        
        try {
            let cacheItem;
            
            // Try localStorage first
            const storedItem = localStorage.getItem(`sanmar_${key}`);
            if (storedItem) {
                cacheItem = JSON.parse(storedItem);
            } else if (cache[key]) {
                // Fall back to in-memory cache
                cacheItem = cache[key];
            }
            
            if (cacheItem && cacheItem.expires > Date.now()) {
                logger.debug(`Cache hit for key: ${key}`);
                return cacheItem.data;
            }
            
            // Cache miss or expired
            logger.debug(`Cache miss or expired for key: ${key}`);
            return null;
        } catch (e) {
            logger.error(`Error retrieving cached data: ${e.message}`);
            return null;
        }
    }

    /**
     * Optimized AJAX function with caching and request throttling
     * @param {Object} options - Request options
     * @returns {Promise} - Promise resolving to response data
     */
    function optimizedAjax(options) {
        const startTime = performance.now();
        const cacheKey = `ajax_${options.url}_${JSON.stringify(options.data || {})}`;
        
        // Check cache first
        const cachedData = getCachedData(cacheKey);
        if (cachedData) {
            logger.performance('AJAX cache hit', startTime);
            return Promise.resolve(cachedData);
        }
        
        // Implement request throttling
        return new Promise((resolve, reject) => {
            // Create a throttled fetch function
            const throttledFetch = () => {
                fetch(options.url, {
                    method: options.method || 'GET',
                    headers: options.headers || {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: options.data ? JSON.stringify(options.data) : undefined
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    // Cache the successful response
                    cacheData(cacheKey, data, options.cacheTTL || config.cacheTTL);
                    logger.performance('AJAX request completed', startTime);
                    resolve(data);
                })
                .catch(error => {
                    logger.error(`AJAX error: ${error.message}`);
                    reject(error);
                });
            };
            
            // Execute the throttled function
            setTimeout(throttledFetch, config.apiThrottleMs);
        });
    }

    /**
     * Batch load pricing data for multiple colors
     * @param {string} style - Product style
     * @param {Array} colors - Array of color codes
     * @returns {Promise} - Promise resolving when all batches are loaded
     */
    function batchLoadPricing(style, colors) {
        if (!colors || !colors.length) return Promise.resolve({});
        
        logger.debug(`Batch loading pricing for style ${style}, ${colors.length} colors`);
        const startTime = performance.now();
        
        // Split colors into batches
        const batches = [];
        for (let i = 0; i < colors.length; i += config.batchSize) {
            batches.push(colors.slice(i, i + config.batchSize));
        }
        
        // Track progress
        let completed = 0;
        const totalBatches = batches.length;
        
        // Process batches sequentially to avoid overwhelming the server
        return batches.reduce((promise, batch) => {
            return promise.then(results => {
                return Promise.all(batch.map(color => {
                    return fetchPricing(style, color)
                        .then(priceData => {
                            results[color] = priceData;
                            return priceData;
                        });
                }))
                .then(() => {
                    completed++;
                    logger.debug(`Completed batch ${completed}/${totalBatches}`);
                    return results;
                });
            });
        }, Promise.resolve({}))
        .then(results => {
            logger.performance(`Batch load pricing for ${colors.length} colors`, startTime);
            return results;
        });
    }

    /**
     * Fetch pricing data for a specific style and color
     * @param {string} style - Product style
     * @param {string} color - Color code
     * @returns {Promise} - Promise resolving to pricing data
     */
    function fetchPricing(style, color) {
        const cacheKey = `pricing_${style}_${color}`;
        const cachedData = getCachedData(cacheKey);
        
        if (cachedData) {
            return Promise.resolve(cachedData);
        }
        
        return optimizedAjax({
            url: `/api/pricing?style=${encodeURIComponent(style)}&color=${encodeURIComponent(color)}`,
            method: 'GET',
            cacheTTL: 30 * 60 * 1000 // 30 minutes
        })
        .then(data => {
            cacheData(cacheKey, data);
            return data;
        });
    }

    /**
     * Lazy load images only when they are about to enter the viewport
     */
    function setupLazyLoading() {
        if (!config.lazyLoadImages) return;
        
        const lazyImages = [].slice.call(document.querySelectorAll('img.lazy'));
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const lazyImage = entry.target;
                        lazyImage.src = lazyImage.dataset.src;
                        if (lazyImage.dataset.srcset) {
                            lazyImage.srcset = lazyImage.dataset.srcset;
                        }
                        lazyImage.classList.remove('lazy');
                        imageObserver.unobserve(lazyImage);
                        logger.debug('Lazy loaded image: ' + lazyImage.dataset.src);
                    }
                });
            });
            
            lazyImages.forEach(lazyImage => {
                imageObserver.observe(lazyImage);
            });
        } else {
            // Fallback for browsers without IntersectionObserver
            let active = false;
            
            const lazyLoad = () => {
                if (active === false) {
                    active = true;
                    
                    setTimeout(() => {
                        lazyImages.forEach(lazyImage => {
                            if ((lazyImage.getBoundingClientRect().top <= window.innerHeight && 
                                lazyImage.getBoundingClientRect().bottom >= 0) && 
                                getComputedStyle(lazyImage).display !== 'none') {
                                
                                lazyImage.src = lazyImage.dataset.src;
                                if (lazyImage.dataset.srcset) {
                                    lazyImage.srcset = lazyImage.dataset.srcset;
                                }
                                lazyImage.classList.remove('lazy');
                                
                                lazyImages = lazyImages.filter(image => image !== lazyImage);
                                
                                if (lazyImages.length === 0) {
                                    document.removeEventListener('scroll', lazyLoad);
                                    window.removeEventListener('resize', lazyLoad);
                                    window.removeEventListener('orientationchange', lazyLoad);
                                }
                            }
                        });
                        
                        active = false;
                    }, 200);
                }
            };
            
            document.addEventListener('scroll', lazyLoad);
            window.addEventListener('resize', lazyLoad);
            window.addEventListener('orientationchange', lazyLoad);
            lazyLoad();
        }
        
        logger.info('Lazy loading initialized');
    }

    /**
     * Optimize color swatch loading
     * Only loads a subset of colors initially, then loads the rest on demand
     */
    function optimizeColorSwatches() {
        const colorContainer = document.querySelector('.color-selector');
        if (!colorContainer) return;
        
        const colors = colorContainer.querySelectorAll('.color-swatch');
        if (colors.length <= config.batchSize) return;
        
        // Show only the first batch of colors initially
        for (let i = config.batchSize; i < colors.length; i++) {
            colors[i].style.display = 'none';
        }
        
        // Add a "Show More" button
        const showMoreBtn = document.createElement('button');
        showMoreBtn.innerText = 'Show More Colors';
        showMoreBtn.className = 'show-more-colors btn btn-sm btn-secondary mt-2';
        showMoreBtn.addEventListener('click', function() {
            // Show all colors
            for (let i = 0; i < colors.length; i++) {
                colors[i].style.display = '';
            }
            // Remove the button
            this.remove();
        });
        
        colorContainer.appendChild(showMoreBtn);
        logger.debug('Color swatches optimized');
    }

    /**
     * Set up background prefetching of related products
     * @param {string} currentStyle - Current product style
     */
    function prefetchRelatedProducts(currentStyle) {
        if (!config.prefetchRelatedProducts) return;
        
        // Wait until the page is fully loaded and idle
        if ('requestIdleCallback' in window) {
            requestIdleCallback(() => {
                fetchRelatedProducts(currentStyle);
            });
        } else {
            // Fallback for browsers without requestIdleCallback
            setTimeout(() => {
                fetchRelatedProducts(currentStyle);
            }, 2000);
        }
    }

    /**
     * Fetch related products data
     * @param {string} currentStyle - Current product style
     */
    function fetchRelatedProducts(currentStyle) {
        // This would typically call an API endpoint that returns related products
        // For demonstration, we're just logging it
        logger.debug(`Would prefetch related products for style: ${currentStyle}`);
        
        // In a real implementation, you would:
        // 1. Call an API to get related products
        // 2. Cache the results
        // 3. Maybe even preload images for these products
    }

    /**
     * Performance optimizations for product page
     */
    function optimizeProductPage() {
        // Extract current product style from URL
        const pathParts = window.location.pathname.split('/');
        const currentStyle = pathParts[pathParts.length - 1];
        
        if (!currentStyle) return;
        
        logger.debug(`Optimizing product page for style: ${currentStyle}`);
        
        // Set up lazy loading for images
        setupLazyLoading();
        
        // Optimize color swatches
        optimizeColorSwatches();
        
        // Prefetch related products
        prefetchRelatedProducts(currentStyle);
        
        // Convert standard images to lazy-loaded images
        document.querySelectorAll('.product-image:not(.lazy)').forEach(img => {
            if (!img.classList.contains('lazy') && img.src) {
                img.dataset.src = img.src;
                img.src = 'data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='; // Transparent placeholder
                img.classList.add('lazy');
            }
        });
    }

    /**
     * Apply performance optimizations based on current page
     */
    function applyOptimizations() {
        // Detect current page type
        if (window.location.pathname.includes('/product/')) {
            optimizeProductPage();
        }
        
        // These optimizations apply to all pages
        setupLazyLoading();
        
        // Update performance metrics
        logger.performance('Performance enhancements initialization', initTime);
    }

    // Expose some functions to global scope for use in other scripts
    window.SanMarPerformance = {
        fetchPricing: fetchPricing,
        batchLoadPricing: batchLoadPricing,
        optimizedAjax: optimizedAjax,
        getCachedData: getCachedData,
        cacheData: cacheData
    };

    // Initialize when the DOM is fully loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', applyOptimizations);
    } else {
        applyOptimizations();
    }
})();