/**
 * SanMar Image Helper - Utilities for loading and handling product images
 */

// Create a namespace for the helper functions
window.SanmarImageHelper = {
    // Set an image with fallback support
    setImageWithFallback: function(imgElement, primaryUrl, fallbackUrl) {
        if (!imgElement) return;
        
        // If the primary URL is '#', use a colored block as fallback
        if (primaryUrl === '#') {
            this.setColorBlock(imgElement);
            return;
        }
        
        // Add loading class and set up events
        imgElement.classList.add('fallback-ready');
        
        // Create a loading indicator
        const container = imgElement.closest('.category-image-container');
        let loadingIndicator;
        
        if (container) {
            loadingIndicator = document.createElement('div');
            loadingIndicator.className = 'image-loading';
            loadingIndicator.innerHTML = '<div class="loading-spinner"></div>';
            container.appendChild(loadingIndicator);
        }
        
        // Try loading the primary image
        imgElement.onerror = function() {
            console.log('Primary image failed to load:', primaryUrl);
            
            // If fallback URL is provided and different from primary, try it
            if (fallbackUrl && fallbackUrl !== primaryUrl && fallbackUrl !== '#') {
                console.log('Trying fallback image:', fallbackUrl);
                imgElement.onerror = function() {
                    console.log('Fallback image also failed:', fallbackUrl);
                    // If fallback also fails, show a colored block
                    SanmarImageHelper.setColorBlock(imgElement);
                    
                    // Remove loading indicator
                    if (loadingIndicator) {
                        loadingIndicator.classList.add('hidden');
                    }
                };
                imgElement.src = fallbackUrl;
            } else {
                // No valid fallback, show colored block
                SanmarImageHelper.setColorBlock(imgElement);
                
                // Remove loading indicator
                if (loadingIndicator) {
                    loadingIndicator.classList.add('hidden');
                }
            }
        };
        
        imgElement.onload = function() {
            console.log('Image loaded successfully:', this.src);
            imgElement.classList.add('loaded');
            
            // Remove loading indicator
            if (loadingIndicator) {
                loadingIndicator.classList.add('hidden');
            }
            
            // Hide placeholder if exists
            const container = imgElement.closest('.category-image-container');
            if (container) {
                const placeholder = container.querySelector('.category-image-placeholder');
                if (placeholder) {
                    placeholder.style.display = 'none';
                }
            }
        };
        
        // Start loading the primary image
        imgElement.src = primaryUrl;
    },
    
    // Set a colored block in place of a failed image
    setColorBlock: function(imgElement) {
        if (!imgElement) return;
        
        const container = imgElement.closest('.category-image-container');
        if (container) {
            // Show the placeholder
            const placeholder = container.querySelector('.category-image-placeholder');
            if (placeholder) {
                placeholder.style.display = 'flex';
            }
            
            // Hide the image
            imgElement.style.display = 'none';
        } else {
            // If no container, style the image element itself
            imgElement.style.background = 'linear-gradient(135deg, #f0f0f0, #e0e0e0)';
            imgElement.style.display = 'block';
            imgElement.style.width = '100%';
            imgElement.style.height = '100%';
            imgElement.removeAttribute('src');
        }
    },
    
    // Preload common category images
    preloadCategoryImages: function() {
        const commonCategories = [
            'TSHIRTS', 'POLOS', 'OUTERWEAR', 'WOVEN_SHIRTS',
            'SWEATSHIRTS', 'HEADWEAR', 'WORKWEAR', 'BAGS'
        ];
        
        commonCategories.forEach(category => {
            fetch(`/api/category-image?category=${encodeURIComponent(category)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data && data.image_url) {
                        // Preload the image
                        const img = new Image();
                        img.src = data.image_url;
                        console.log(`Preloaded image for ${category}`);
                    }
                })
                .catch(error => {
                    console.warn(`Failed to preload image for ${category}:`, error);
                });
        });
    }
};

// When the DOM is loaded, preload common category images
document.addEventListener('DOMContentLoaded', function() {
    // Preload category images in the background
    setTimeout(() => {
        SanmarImageHelper.preloadCategoryImages();
    }, 1000); // Delay to prioritize visible content first
});