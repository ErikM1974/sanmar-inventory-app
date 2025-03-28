// Home Page JavaScript with Performance Optimizations

// Debounce function to prevent excessive API calls
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

// Common style number prefixes for instant results
const COMMON_PREFIXES = {
    'K': ['K500', 'K540', 'K420', 'K110', 'K800'],
    'PC': ['PC61', 'PC54', 'PC55', 'PC61LS', 'PC90H'],
    'ST': ['ST350', 'ST850', 'ST320', 'ST271', 'ST650'],
    'J': ['J790', 'J317', 'J293', 'J706', 'J754'],
    'DT': ['DT6000', 'DT104', 'DT1350', 'DT1170', 'DT501'],
    'L': ['L500', 'L223', 'L110', 'L540', 'L800']
};

// Cache for autocomplete results
const styleCache = {};

document.addEventListener('DOMContentLoaded', function() {
    // Initialize autocomplete for search inputs
    const searchInputs = document.querySelectorAll('input[name="query"]');
    searchInputs.forEach(input => {
        if (input) {
            setupAutocomplete(input);
        }
    });
    
    // Add animation to category cards with optimized styles
    const categoryCards = document.querySelectorAll('.category-card');
    categoryCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });
    
    // Product card hover effects
    const productCards = document.querySelectorAll('.product-card');
    productCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });
});

// Enhanced autocomplete setup with performance optimizations
function setupAutocomplete(input) {
    // Create and style autocomplete container
    const autocompleteContainer = document.createElement('div');
    autocompleteContainer.classList.add('autocomplete-items');
    autocompleteContainer.style.display = 'none';
    autocompleteContainer.style.position = 'absolute';
    autocompleteContainer.style.zIndex = '99';
    autocompleteContainer.style.width = input.offsetWidth + 'px';
    autocompleteContainer.style.maxHeight = '300px';
    autocompleteContainer.style.overflowY = 'auto';
    autocompleteContainer.style.border = '1px solid #ddd';
    autocompleteContainer.style.borderTop = 'none';
    autocompleteContainer.style.borderRadius = '0 0 5px 5px';
    autocompleteContainer.style.backgroundColor = '#fff';
    input.parentNode.appendChild(autocompleteContainer);
    
    // Function to display results - extracted for reuse
    function displayResults(query, results) {
        // Clear and hide if no results
        if (!results || results.length === 0) {
            autocompleteContainer.innerHTML = '';
            autocompleteContainer.style.display = 'none';
            return;
        }
        
        // Show container and populate with results
        autocompleteContainer.innerHTML = '';
        autocompleteContainer.style.display = 'block';
        
        // Create items with optimized event handlers
        results.forEach(style => {
            const item = document.createElement('div');
            
            // Highlight the matching part of the style
            const upperStyle = style.toUpperCase();
            const upperQuery = query.toUpperCase();
            const index = upperStyle.indexOf(upperQuery);
            
            if (index >= 0) {
                const before = style.substring(0, index);
                const match = style.substring(index, index + query.length);
                const after = style.substring(index + query.length);
                item.innerHTML = `${before}<strong style="color: #0066cc;">${match}</strong>${after}`;
            } else {
                item.innerHTML = `<strong>${style}</strong>`;
            }
            
            item.style.padding = '10px';
            item.style.cursor = 'pointer';
            item.style.borderBottom = '1px solid #ddd';
            
            // Single event handler with direct navigation
            item.addEventListener('mousedown', function() {
                input.value = style;
                autocompleteContainer.style.display = 'none';
                
                // If it looks like a style number, go directly to product page
                if (/^[A-Za-z0-9]{3,10}$/.test(style)) {
                    window.location.href = `/product/${style}`;
                }
            });
            
            // Simple hover effects
            item.addEventListener('mouseover', function() {
                this.style.backgroundColor = '#f0f7ff';
            });
            
            item.addEventListener('mouseout', function() {
                this.style.backgroundColor = '#fff';
            });
            
            autocompleteContainer.appendChild(item);
        });
    }
    
    // Check for instant results based on common prefixes
    function getInstantResults(query) {
        if (query.length === 1) {
            // Handle single letter input with common prefixes
            return COMMON_PREFIXES[query.toUpperCase()] || [];
        } else if (query.length === 2) {
            // Handle two-letter prefixes by searching all common styles
            const prefix = query.toUpperCase();
            let results = [];
            Object.values(COMMON_PREFIXES).forEach(styles => {
                styles.forEach(style => {
                    if (style.toUpperCase().startsWith(prefix)) {
                        results.push(style);
                    }
                });
            });
            return results;
        }
        return null;
    }
    
    // Debounced input handler to prevent excessive API calls
    const debouncedInputHandler = debounce(function() {
        const query = this.value.trim();
        
        // Clear and hide for short queries
        if (query.length < 2) {
            autocompleteContainer.innerHTML = '';
            autocompleteContainer.style.display = 'none';
            return;
        }
        
        // Check cache first for exact match
        if (styleCache[query]) {
            displayResults(query, styleCache[query]);
            return;
        }
        
        // Try getting instant results for common prefixes
        const instantResults = getInstantResults(query);
        if (instantResults && instantResults.length > 0) {
            displayResults(query, instantResults);
            styleCache[query] = instantResults;
            return;
        }
        
        // Nothing in cache or instant results, fetch from server
        fetch(`/autocomplete?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                // Cache the results
                styleCache[query] = data;
                displayResults(query, data);
            })
            .catch(error => {
                console.error('Error fetching autocomplete results:', error);
                autocompleteContainer.style.display = 'none';
            });
    }, 150); // 150ms debounce delay - fast enough for responsive UI but reduces API load
    
    // Add the debounced input handler
    input.addEventListener('input', debouncedInputHandler);
    
    // Handle clicks outside to hide the autocomplete
    document.addEventListener('click', function() {
        autocompleteContainer.style.display = 'none';
    });
    
    // Prevent hiding on input click and show results if needed
    input.addEventListener('click', function(e) {
        e.stopPropagation();
        if (this.value.trim().length >= 2) {
            // Check cache first
            const query = this.value.trim();
            if (styleCache[query]) {
                displayResults(query, styleCache[query]);
            } else {
                // Trigger input event to show results
                this.dispatchEvent(new Event('input'));
            }
        }
    });
    
    // Add keyboard navigation for accessibility
    input.addEventListener('keydown', function(e) {
        if (autocompleteContainer.style.display === 'none') return;
        
        const items = autocompleteContainer.querySelectorAll('div');
        if (!items.length) return;
        
        let activeItem = autocompleteContainer.querySelector('div.autocomplete-active');
        let activeIndex = -1;
        
        if (activeItem) {
            activeIndex = Array.from(items).indexOf(activeItem);
        }
        
        // Arrow down
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            
            if (activeItem) activeItem.classList.remove('autocomplete-active');
            activeIndex = (activeIndex + 1) % items.length;
            items[activeIndex].classList.add('autocomplete-active');
            items[activeIndex].scrollIntoView({ block: 'nearest' });
        }
        // Arrow up
        else if (e.key === 'ArrowUp') {
            e.preventDefault();
            
            if (activeItem) activeItem.classList.remove('autocomplete-active');
            activeIndex = (activeIndex - 1 + items.length) % items.length;
            items[activeIndex].classList.add('autocomplete-active');
            items[activeIndex].scrollIntoView({ block: 'nearest' });
        }
        // Enter key
        else if (e.key === 'Enter' && activeItem) {
            e.preventDefault();
            input.value = activeItem.textContent.trim();
            autocompleteContainer.style.display = 'none';
            
            // Navigate to product if it's a style number
            if (/^[A-Za-z0-9]{3,10}$/.test(input.value)) {
                window.location.href = `/product/${input.value}`;
            }
        }
    });
}