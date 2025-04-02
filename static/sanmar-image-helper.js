/**
 * SanMar Image Helper
 * Utility functions for working with SanMar product images
 */

const SanMarImageHelper = {
    /**
     * Base URL for SanMar product images
     */
    baseUrl: 'https://cdni.sanmar.com/catalog/images/',
    
    /**
     * Default image to use when product image is not available
     */
    defaultImage: '/static/images/no-image-available.png',
    
    /**
     * Get product image URL for a specific style
     * @param {string} style - Product style number
     * @param {string} [type='p110'] - Image type (p110 for product, m110 for model, etc.)
     * @param {string} [format='jpg'] - Image format (jpg, png)
     * @returns {string} Full image URL
     */
    getProductImageUrl(style, type = 'p110', format = 'jpg') {
        if (!style) return this.defaultImage;
        return `${this.baseUrl}${style}${type}.${format}`;
    },
    
    /**
     * Get color swatch image URL
     * @param {string} style - Product style number
     * @param {string} color - Color code
     * @param {string} [format='jpg'] - Image format (jpg, png)
     * @returns {string} Full swatch image URL
     */
    getSwatchImageUrl(style, color, format = 'jpg') {
        if (!style || !color) return this.defaultImage;
        return `${this.baseUrl}${style}_${color}s.${format}`;
    },
    
    /**
     * Get alternative image URL if the main one is not available
     * @param {string} style - Product style number
     * @returns {string[]} Array of alternative image URLs to try
     */
    getAlternativeImageUrls(style) {
        if (!style) return [this.defaultImage];
        
        return [
            this.getProductImageUrl(style, 'p110', 'jpg'),
            this.getProductImageUrl(style, 'm110', 'jpg'),
            this.getProductImageUrl(style, '', 'jpg'),
            this.getProductImageUrl(style, 'p110', 'png'),
            this.getProductImageUrl(style.toLowerCase(), 'p110', 'jpg')
        ];
    },
    
    /**
     * Check if an image URL exists
     * @param {string} url - Image URL to check
     * @param {Function} successCallback - Called if image exists
     * @param {Function} errorCallback - Called if image doesn't exist
     */
    checkImageExists(url, successCallback, errorCallback) {
        const img = new Image();
        img.onload = () => successCallback(url);
        img.onerror = () => errorCallback(url);
        img.src = url;
    },
    
    /**
     * Find the first valid image URL from a list of alternatives
     * @param {string} style - Product style number
     * @param {Function} callback - Called with the valid URL or default image
     */
    findValidProductImage(style, callback) {
        if (!style) {
            callback(this.defaultImage);
            return;
        }
        
        const urls = this.getAlternativeImageUrls(style);
        let index = 0;
        
        const tryNextUrl = () => {
            if (index >= urls.length) {
                callback(this.defaultImage);
                return;
            }
            
            this.checkImageExists(
                urls[index],
                (validUrl) => callback(validUrl),
                () => {
                    index++;
                    tryNextUrl();
                }
            );
        };
        
        tryNextUrl();
    },
    
    /**
     * Create an image element with a valid SanMar product image
     * @param {string} style - Product style number
     * @param {Object} [options] - Additional options
     * @param {string} [options.alt] - Alt text for the image
     * @param {string} [options.className] - CSS class for the image
     * @param {Function} [options.onLoad] - Callback when image is loaded
     * @returns {HTMLImageElement} Image element
     */
    createProductImageElement(style, options = {}) {
        const img = document.createElement('img');
        if (options.alt) img.alt = options.alt;
        if (options.className) img.className = options.className;
        
        // Set default image initially
        img.src = this.defaultImage;
        
        // Find a valid image
        this.findValidProductImage(style, (validUrl) => {
            img.src = validUrl;
            if (options.onLoad) {
                img.onload = () => options.onLoad(img);
            }
        });
        
        return img;
    },
    
    /**
     * Initialize color swatches for a product
     * @param {string} style - Product style number
     * @param {string[]} colors - Array of color codes
     * @param {string} containerId - ID of the container element for swatches
     * @param {Function} onSwatchClick - Callback when a swatch is clicked
     */
    initColorSwatches(style, colors, containerId, onSwatchClick) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = '';
        
        colors.forEach(color => {
            const swatch = document.createElement('div');
            swatch.className = 'color-swatch';
            swatch.dataset.color = color;
            
            const swatchImg = document.createElement('img');
            swatchImg.alt = color;
            swatchImg.src = this.getSwatchImageUrl(style, color);
            swatchImg.onerror = () => {
                // If swatch image fails, create a colored div instead
                swatchImg.style.display = 'none';
                swatch.style.backgroundColor = this.getColorHex(color) || '#cccccc';
            };
            
            swatch.appendChild(swatchImg);
            swatch.addEventListener('click', () => onSwatchClick(color));
            container.appendChild(swatch);
        });
    },
    
    /**
     * Get approximate hex color from color name
     * @param {string} colorName - Color name
     * @returns {string|null} Hex color code or null if not found
     */
    getColorHex(colorName) {
        const colorMap = {
            'black': '#000000',
            'white': '#ffffff',
            'navy': '#000080',
            'blue': '#0000ff',
            'royal': '#4169e1',
            'red': '#ff0000',
            'green': '#008000',
            'forest': '#228b22',
            'purple': '#800080',
            'grey': '#808080',
            'gray': '#808080',
            'charcoal': '#36454f',
            'orange': '#ffa500',
            'yellow': '#ffff00',
            'brown': '#a52a2a',
            'tan': '#d2b48c',
            'maroon': '#800000',
            'pink': '#ffc0cb',
            'heather': '#b8c0c0'
        };
        
        // Try to find a close match in the color map
        const lowerName = colorName.toLowerCase();
        for (const [key, value] of Object.entries(colorMap)) {
            if (lowerName.includes(key)) {
                return value;
            }
        }
        
        return null;
    }
};

// Export for CommonJS environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SanMarImageHelper;
}