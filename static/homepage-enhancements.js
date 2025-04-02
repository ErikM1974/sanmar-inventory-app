/**
 * Homepage Enhancements
 * JavaScript functionality for the Northwest Custom Apparel homepage
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initFeaturedProducts();
    initCategorySlider();
    initCaspioCategories();
    initTestimonialSlider();
    initAnimations();
    initStyleSearch();
});

/**
 * Initialize featured products section
 * Loads products from API and displays them in the featured products section
 */
function initFeaturedProducts() {
    const featuredProductsContainer = document.getElementById('featured-products');
    if (!featuredProductsContainer) return;
    
    // Featured product styles to display
    const featuredStyles = ['PC61', 'K500', 'J790', 'L500'];
    
    // Create a container for the products
    const productsRow = document.createElement('div');
    productsRow.className = 'row';
    
    // Load each product
    featuredStyles.forEach(style => {
        // First add a placeholder
        const productCol = document.createElement('div');
        productCol.className = 'col-md-3 mb-4';
        productCol.innerHTML = `
            <div class="product-card h-100">
                <div class="product-image-container">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
                <div class="product-info">
                    <h5 class="product-title">Loading...</h5>
                </div>
            </div>
        `;
        productsRow.appendChild(productCol);
        
        // Fetch product data
        fetch(`/api/product-quick-view/${style}`)
            .then(response => response.json())
            .then(data => {
                // Replace placeholder with actual product
                productCol.innerHTML = `
                    <div class="product-card h-100">
                        <div class="product-image-container">
                            <img src="${data.imageUrl || `/static/images/product-${style.toLowerCase()}.jpg`}" 
                                alt="${data.name || style}" class="product-image">
                            ${Math.random() > 0.5 ? '<span class="product-badge">Popular</span>' : ''}
                        </div>
                        <div class="product-info">
                            <h5 class="product-title">${data.name || `Product ${style}`}</h5>
                            <p class="product-style">${style}</p>
                            <div class="product-colors">
                                ${generateColorDots(data.colors || ['Black', 'Navy', 'White', 'Red', 'Royal'])}
                            </div>
                            <p class="product-price">$${(data.price || 19.99).toFixed(2)}</p>
                            <div class="product-actions">
                                <a href="/product/${style}" class="btn btn-primary btn-sm">View Details</a>
                                <button class="btn btn-outline-primary btn-sm add-to-quote" 
                                        data-style="${style}"
                                        data-name="${data.name || `Product ${style}`}"
                                        data-price="${data.price || 19.99}">
                                    Add to Quote
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                
                // Reinitialize the add to quote buttons
                if (typeof QuoteCart !== 'undefined' && QuoteCart.init) {
                    productCol.querySelectorAll('.add-to-quote').forEach(button => {
                        button.addEventListener('click', event => {
                            if (typeof QuoteCart.addItem === 'function') {
                                const { style, name, price } = button.dataset;
                                QuoteCart.addItem({
                                    style, 
                                    name,
                                    price,
                                    size: 'L',
                                    color: 'Black',
                                    quantity: 1
                                });
                            }
                        });
                    });
                }
            })
            .catch(error => {
                console.error(`Error loading product ${style}:`, error);
                // Show error state
                productCol.innerHTML = `
                    <div class="product-card h-100">
                        <div class="product-info text-center py-4">
                            <div class="text-danger mb-2">
                                <i class="fas fa-exclamation-circle fa-2x"></i>
                            </div>
                            <h5 class="product-title">Couldn't load product</h5>
                            <p class="text-muted">Please try again later</p>
                            <a href="/product/${style}" class="btn btn-outline-primary btn-sm">Try View Product</a>
                        </div>
                    </div>
                `;
            });
    });
    
    // Add products to container
    featuredProductsContainer.appendChild(productsRow);
}

/**
 * Generate HTML for color dots
 */
function generateColorDots(colors) {
    if (!colors || !colors.length) return '';
    
    // Limit to 5 colors with a "+X more" indicator if needed
    const displayColors = colors.slice(0, 5);
    const remainingCount = colors.length - displayColors.length;
    
    let dotsHtml = displayColors.map(color => {
        // Convert color names to hex codes (simplified mapping)
        const colorMap = {
            'Black': '#000000',
            'White': '#ffffff',
            'Navy': '#000080',
            'Royal': '#4169e1',
            'Red': '#ff0000',
            'Gray': '#808080',
            'Green': '#008000',
            'Pink': '#ffc0cb',
            'Purple': '#800080',
            'Orange': '#ffa500',
            'Yellow': '#ffff00',
            'Brown': '#a52a2a',
            'Maroon': '#800000',
            'Gold': '#ffd700',
            'Silver': '#c0c0c0',
            'Athletic Heather': '#d3d3d3'
        };
        
        const hex = colorMap[color] || '#000000';
        const border = (color === 'White') ? 'border: 1px solid #dee2e6;' : '';
        
        return `<div class="color-dot" style="background-color: ${hex}; ${border}" title="${color}"></div>`;
    }).join('');
    
    // Add the "+X more" indicator if needed
    if (remainingCount > 0) {
        dotsHtml += `<div class="color-dot-more">+${remainingCount}</div>`;
    }
    
    return dotsHtml;
}

/**
 * Initialize category slider
 */
function initCategorySlider() {
    const categorySection = document.getElementById('category-slider');
    if (!categorySection) return;
    
    // Dummy implementation - in a real app, this would be a carousel or similar
    // Here we just add some basic mouse hover effects
    const categoryCards = categorySection.querySelectorAll('.category-card');
    categoryCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            categoryCards.forEach(c => c.style.opacity = '0.7');
            card.style.opacity = '1';
            card.style.transform = 'translateY(-10px)';
        });
        
        card.addEventListener('mouseleave', () => {
            categoryCards.forEach(c => c.style.opacity = '1');
            card.style.transform = 'translateY(-5px)';
        });
    });
}

/**
 * Initialize Caspio categories in the sidebar
 * Loads categories from API and displays them in the sidebar
 */
function initCaspioCategories() {
    const categoryList = document.getElementById('category-sidebar');
    if (!categoryList) return;
    
    // Show loading state
    categoryList.innerHTML = `
        <div class="text-center py-3">
            <div class="spinner-border spinner-border-sm text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mb-0 mt-2">Loading categories...</p>
        </div>
    `;
    
    // Fetch categories from API
    fetch('/api/caspio-categories')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.categories && data.categories.length) {
                // Create category list
                const ul = document.createElement('ul');
                ul.className = 'list-unstyled';
                
                data.categories.forEach(category => {
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <a href="${category.url}" class="d-flex align-items-center">
                            <span>${category.name}</span>
                            <span class="category-count ms-auto">${category.count}</span>
                        </a>
                    `;
                    ul.appendChild(li);
                });
                
                // Clear loading state and add categories
                categoryList.innerHTML = '';
                categoryList.appendChild(ul);
            } else {
                throw new Error('No categories found');
            }
        })
        .catch(error => {
            console.error('Error loading categories:', error);
            
            // Show error state
            categoryList.innerHTML = `
                <div class="text-center py-3">
                    <div class="text-danger">
                        <i class="fas fa-exclamation-circle"></i>
                    </div>
                    <p class="mb-0 mt-2">Couldn't load categories</p>
                    <button class="btn btn-sm btn-outline-primary mt-2" onclick="initCaspioCategories()">
                        Try Again
                    </button>
                </div>
            `;
        });
}

/**
 * Initialize testimonial slider
 */
function initTestimonialSlider() {
    const testimonialSection = document.getElementById('testimonials');
    if (!testimonialSection) return;
    
    // Simple automatic rotation of testimonials
    const testimonials = testimonialSection.querySelectorAll('.testimonial-card');
    if (testimonials.length <= 1) return;
    
    let currentIndex = 0;
    
    // Highlight the first testimonial
    testimonials[currentIndex].classList.add('active');
    
    // Set up rotation
    setInterval(() => {
        // Remove active class from current testimonial
        testimonials[currentIndex].classList.remove('active');
        
        // Move to next testimonial
        currentIndex = (currentIndex + 1) % testimonials.length;
        
        // Add active class to new testimonial
        testimonials[currentIndex].classList.add('active');
    }, 5000);
}

/**
 * Initialize animations
 * Adds scroll-based animations to page elements
 */
function initAnimations() {
    // Simple fade-in animation for sections as they scroll into view
    const animateSections = document.querySelectorAll('.section-animate');
    
    // Simple implementation - in a real app, you might use IntersectionObserver
    function checkScroll() {
        animateSections.forEach(section => {
            const sectionTop = section.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (sectionTop < windowHeight * 0.8) {
                section.classList.add('section-visible');
            }
        });
    }
    
    // Add initial classes
    animateSections.forEach(section => {
        section.classList.add('section-hidden');
    });
    
    // Check on scroll
    window.addEventListener('scroll', checkScroll);
    
    // Check once on load
    setTimeout(checkScroll, 100);
}

/**
 * Initialize style search form
 */
function initStyleSearch() {
    const styleSearchForm = document.getElementById('style-search-form');
    if (!styleSearchForm) return;
    
    styleSearchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const styleInput = document.getElementById('style-search-input');
        if (styleInput && styleInput.value.trim()) {
            window.location.href = `/product/${styleInput.value.trim()}`;
        }
    });
}