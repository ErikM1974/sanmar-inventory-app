/**
 * Caspio Integration JavaScript
 * This script enhances the Caspio DataPages with additional functionality
 * and improves the user experience when interacting with Caspio-embedded content.
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Caspio integration
    initCaspioIntegration();
});

/**
 * Initialize Caspio integration features
 */
function initCaspioIntegration() {
    // Add event listeners to Caspio elements once they're loaded
    waitForCaspioElements(function() {
        enhanceCaspioTables();
        setupCaspioFilters();
        addInventoryHighlighting();
        setupCaspioPagination();
    });

    // Set up loading spinners for Caspio DataPages
    setupLoadingSpinners();
}

/**
 * Wait for Caspio elements to be loaded in the DOM
 * @param {Function} callback - Function to call when elements are loaded
 */
function waitForCaspioElements(callback) {
    // Check if Caspio elements exist
    if (document.querySelector('.cbResultSetTable') || 
        document.querySelector('.cbSearchForm') || 
        document.querySelector('.cbDetailView')) {
        // Elements exist, call the callback
        callback();
    } else {
        // Elements don't exist yet, wait and try again
        setTimeout(function() {
            waitForCaspioElements(callback);
        }, 500);
    }
}

/**
 * Enhance Caspio tables with additional functionality
 */
function enhanceCaspioTables() {
    // Get all Caspio tables
    const tables = document.querySelectorAll('.cbResultSetTable');
    
    tables.forEach(function(table) {
        // Add Bootstrap table classes
        table.classList.add('table', 'table-striped', 'table-hover');
        
        // Add click event to rows for selection
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(function(row) {
            row.addEventListener('click', function() {
                // Toggle selected class
                this.classList.toggle('table-primary');
                
                // If this is a product row with a style, update the URL hash
                const styleCell = this.querySelector('td[data-field="STYLE"]');
                if (styleCell) {
                    const style = styleCell.textContent.trim();
                    window.location.hash = 'style=' + style;
                }
            });
        });
        
        // Make table responsive
        const wrapper = document.createElement('div');
        wrapper.classList.add('table-responsive');
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    });
}

/**
 * Set up Caspio filters for enhanced filtering
 */
function setupCaspioFilters() {
    // Get all Caspio search forms
    const searchForms = document.querySelectorAll('.cbSearchForm');
    
    searchForms.forEach(function(form) {
        // Add Bootstrap form classes
        const inputs = form.querySelectorAll('input[type="text"], select');
        inputs.forEach(function(input) {
            input.classList.add('form-control');
        });
        
        // Add Bootstrap button classes
        const buttons = form.querySelectorAll('button, input[type="submit"], input[type="button"]');
        buttons.forEach(function(button) {
            button.classList.add('btn', 'btn-primary');
        });
        
        // Add a clear button if it doesn't exist
        if (!form.querySelector('.clear-button')) {
            const submitButton = form.querySelector('input[type="submit"]');
            if (submitButton) {
                const clearButton = document.createElement('button');
                clearButton.type = 'button';
                clearButton.classList.add('btn', 'btn-secondary', 'clear-button');
                clearButton.textContent = 'Clear';
                clearButton.addEventListener('click', function() {
                    // Clear all inputs
                    inputs.forEach(function(input) {
                        input.value = '';
                    });
                    
                    // Submit the form to reset the search
                    if (typeof form.submit === 'function') {
                        form.submit();
                    } else {
                        const submitEvent = new Event('submit', {
                            bubbles: true,
                            cancelable: true
                        });
                        form.dispatchEvent(submitEvent);
                    }
                });
                
                submitButton.parentNode.insertBefore(clearButton, submitButton.nextSibling);
            }
        }
    });
}

/**
 * Add highlighting to inventory levels
 */
function addInventoryHighlighting() {
    // Get all quantity cells
    const quantityCells = document.querySelectorAll('td[data-field="QUANTITY"], td[data-field="TOTAL_QUANTITY"]');
    
    quantityCells.forEach(function(cell) {
        const quantity = parseInt(cell.textContent.trim(), 10);
        
        // Add appropriate class based on quantity
        if (quantity > 100) {
            cell.classList.add('inventory-high');
        } else if (quantity > 20) {
            cell.classList.add('inventory-medium');
        } else if (quantity >= 0) {
            cell.classList.add('inventory-low');
        }
    });
}

/**
 * Set up Caspio pagination for better navigation
 */
function setupCaspioPagination() {
    // Get all Caspio pagination elements
    const paginationElements = document.querySelectorAll('.cbPagination');
    
    paginationElements.forEach(function(pagination) {
        // Add Bootstrap pagination classes
        pagination.classList.add('pagination-container');
        
        const paginationLinks = pagination.querySelectorAll('a');
        
        // Create a new pagination element with Bootstrap classes
        const nav = document.createElement('nav');
        nav.setAttribute('aria-label', 'Page navigation');
        
        const ul = document.createElement('ul');
        ul.classList.add('pagination');
        
        paginationLinks.forEach(function(link) {
            const li = document.createElement('li');
            li.classList.add('page-item');
            
            if (link.classList.contains('cbCurrentPage')) {
                li.classList.add('active');
            }
            
            const a = document.createElement('a');
            a.classList.add('page-link');
            a.href = link.href;
            a.textContent = link.textContent;
            
            li.appendChild(a);
            ul.appendChild(li);
        });
        
        nav.appendChild(ul);
        
        // Replace the original pagination with the new one
        pagination.parentNode.replaceChild(nav, pagination);
    });
}

/**
 * Set up loading spinners for Caspio DataPages
 */
function setupLoadingSpinners() {
    // Get all Caspio DataPage containers
    const dataPageContainers = document.querySelectorAll('[id^="caspioform"]');
    
    dataPageContainers.forEach(function(container) {
        // Create a loading spinner
        const spinner = document.createElement('div');
        spinner.classList.add('caspio-spinner-block');
        spinner.innerHTML = '<div class="caspio-spinner"></div><p>Loading data...</p>';
        
        // Insert the spinner before the container
        container.parentNode.insertBefore(spinner, container);
        
        // Hide the spinner when the DataPage is loaded
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    // Check if the DataPage content has loaded
                    if (container.querySelector('.cbResultSetTable') || 
                        container.querySelector('.cbSearchForm') || 
                        container.querySelector('.cbDetailView')) {
                        // Content has loaded, hide the spinner
                        spinner.style.display = 'none';
                        
                        // Disconnect the observer
                        observer.disconnect();
                    }
                }
            });
        });
        
        // Start observing the container
        observer.observe(container, { childList: true, subtree: true });
    });
}

/**
 * Get URL parameters as an object
 * @returns {Object} URL parameters
 */
function getUrlParams() {
    const params = {};
    const queryString = window.location.search.substring(1);
    const pairs = queryString.split('&');
    
    for (let i = 0; i < pairs.length; i++) {
        const pair = pairs[i].split('=');
        params[decodeURIComponent(pair[0])] = decodeURIComponent(pair[1] || '');
    }
    
    return params;
}

/**
 * Apply URL parameters to Caspio search form
 */
function applyUrlParamsToSearch() {
    const params = getUrlParams();
    const searchForm = document.querySelector('.cbSearchForm');
    
    if (searchForm) {
        // Loop through all form inputs
        const inputs = searchForm.querySelectorAll('input[type="text"], select');
        inputs.forEach(function(input) {
            const name = input.name;
            if (params[name]) {
                input.value = params[name];
            }
        });
    }
}

/**
 * Export functions for use in other scripts
 */
window.caspioIntegration = {
    waitForCaspioElements: waitForCaspioElements,
    enhanceCaspioTables: enhanceCaspioTables,
    setupCaspioFilters: setupCaspioFilters,
    addInventoryHighlighting: addInventoryHighlighting,
    setupCaspioPagination: setupCaspioPagination,
    getUrlParams: getUrlParams,
    applyUrlParamsToSearch: applyUrlParamsToSearch
};