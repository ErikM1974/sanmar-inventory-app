/**
 * Quote Cart Management
 * Handles adding, updating, removing items to the quote cart
 */

// QuoteCart namespace to avoid global pollution
const QuoteCart = (() => {
    // Private variables
    let cartItems = [];
    let cartCount = 0;
    
    // DOM elements
    const cartBadge = document.getElementById('quote-cart-badge');
    const cartItemsContainer = document.getElementById('quote-cart-items');
    const cartSummaryContainer = document.getElementById('quote-cart-summary');
    
    // Initialize
    const init = () => {
        // Get cart data from local storage if available
        loadCartFromLocalStorage();
        
        // Update cart badge count
        updateCartBadge();
        
        // Set up event listeners for add to quote buttons
        document.querySelectorAll('.add-to-quote').forEach(button => {
            button.addEventListener('click', handleAddToQuote);
        });
        
        // If we're on the quote page, load the cart items
        if (cartItemsContainer) {
            renderCartItems();
        }
        
        // If we're on the quote page, load the cart summary
        if (cartSummaryContainer) {
            renderCartSummary();
        }
    };
    
    // Load cart from local storage
    const loadCartFromLocalStorage = () => {
        const savedCart = localStorage.getItem('quoteCart');
        if (savedCart) {
            try {
                cartItems = JSON.parse(savedCart);
                cartCount = cartItems.length;
            } catch (e) {
                console.error('Error loading cart from local storage:', e);
                cartItems = [];
                cartCount = 0;
            }
        }
    };
    
    // Save cart to local storage
    const saveCartToLocalStorage = () => {
        localStorage.setItem('quoteCart', JSON.stringify(cartItems));
    };
    
    // Update cart badge count
    const updateCartBadge = () => {
        if (cartBadge) {
            cartBadge.textContent = cartCount;
        }
    };
    
    // Handle add to quote button click
    const handleAddToQuote = (event) => {
        const button = event.target.closest('.add-to-quote');
        if (!button) return;
        
        const { style, name, price } = button.dataset;
        
        // Default to first size and color if not specified
        const size = button.dataset.size || 'L';
        const color = button.dataset.color || 'Black';
        
        addItem({
            style, 
            name,
            price,
            size,
            color,
            quantity: 1
        });
    };
    
    // Add an item to the cart
    const addItem = (item) => {
        // Call API to add item
        fetch('/api/add-to-quote', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(item)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Add item to local cart
                cartItems.push(item);
                cartCount++;
                
                // Update UI
                updateCartBadge();
                saveCartToLocalStorage();
                
                // Show notification
                showNotification('Success', `Added ${item.name} to your quote`);
            } else {
                showNotification('Error', data.message || 'Could not add item to quote');
            }
        })
        .catch(error => {
            console.error('Error adding item to quote:', error);
            showNotification('Error', 'Could not add item to quote');
        });
    };
    
    // Update an item in the cart
    const updateItem = (id, updates) => {
        // Call API to update item
        fetch('/api/update-quote-item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id, ...updates })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update item in local cart
                const index = cartItems.findIndex(item => item.id === id);
                if (index !== -1) {
                    cartItems[index] = { ...cartItems[index], ...updates };
                }
                
                // Update UI
                if (cartItemsContainer) {
                    renderCartItems();
                }
                if (cartSummaryContainer) {
                    renderCartSummary();
                }
                
                saveCartToLocalStorage();
                
                // Show notification
                showNotification('Success', 'Quote item updated');
            } else {
                showNotification('Error', data.message || 'Could not update item');
            }
        })
        .catch(error => {
            console.error('Error updating item:', error);
            showNotification('Error', 'Could not update item');
        });
    };
    
    // Remove an item from the cart
    const removeItem = (id) => {
        // Call API to remove item
        fetch('/api/remove-quote-item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove item from local cart
                cartItems = cartItems.filter(item => item.id !== id);
                cartCount--;
                
                // Update UI
                updateCartBadge();
                if (cartItemsContainer) {
                    renderCartItems();
                }
                if (cartSummaryContainer) {
                    renderCartSummary();
                }
                
                saveCartToLocalStorage();
                
                // Show notification
                showNotification('Success', 'Item removed from quote');
            } else {
                showNotification('Error', data.message || 'Could not remove item');
            }
        })
        .catch(error => {
            console.error('Error removing item:', error);
            showNotification('Error', 'Could not remove item');
        });
    };
    
    // Clear the cart
    const clearCart = () => {
        // Call API to clear cart
        fetch('/api/clear-quote', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Clear local cart
                cartItems = [];
                cartCount = 0;
                
                // Update UI
                updateCartBadge();
                if (cartItemsContainer) {
                    renderCartItems();
                }
                if (cartSummaryContainer) {
                    renderCartSummary();
                }
                
                saveCartToLocalStorage();
                
                // Show notification
                showNotification('Success', 'Quote cart cleared');
            } else {
                showNotification('Error', data.message || 'Could not clear quote');
            }
        })
        .catch(error => {
            console.error('Error clearing quote:', error);
            showNotification('Error', 'Could not clear quote');
        });
    };
    
    // Submit the quote
    const submitQuote = (customerInfo) => {
        // Prepare quote data
        const quoteData = {
            customer: customerInfo,
            items: cartItems,
            submittedAt: new Date().toISOString()
        };
        
        // Call API to submit quote
        fetch('/api/submit-quote', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(quoteData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Clear local cart on successful submission
                cartItems = [];
                cartCount = 0;
                
                // Update UI
                updateCartBadge();
                saveCartToLocalStorage();
                
                // Show success message
                showNotification('Success', `Quote submitted successfully! Your quote number is ${data.quoteId}.`);
                
                // Redirect to success page or show thank you message
                // For now, just reload the page after a brief delay
                setTimeout(() => {
                    window.location.href = '/';
                }, 3000);
                
            } else {
                showNotification('Error', data.message || 'Could not submit quote');
            }
        })
        .catch(error => {
            console.error('Error submitting quote:', error);
            showNotification('Error', 'Could not submit quote');
        });
    };
    
    // Render cart items in the quote cart page
    const renderCartItems = () => {
        if (!cartItemsContainer) return;
        
        if (cartItems.length === 0) {
            // Show empty cart message
            cartItemsContainer.innerHTML = `
                <div class="empty-cart-message">
                    <div class="text-center">
                        <i class="fas fa-shopping-cart fa-4x text-muted mb-3"></i>
                        <h4>Your quote cart is empty</h4>
                        <p>Add products to your quote to get started.</p>
                        <a href="/" class="btn btn-primary mt-3">Browse Products</a>
                    </div>
                </div>
            `;
            return;
        }
        
        // Create table with cart items
        const table = document.createElement('table');
        table.className = 'table quote-items-table';
        
        // Table header
        const thead = document.createElement('thead');
        thead.innerHTML = `
            <tr>
                <th class="item-image">Image</th>
                <th>Product</th>
                <th>Details</th>
                <th>Price</th>
                <th>Quantity</th>
                <th>Total</th>
                <th>Actions</th>
            </tr>
        `;
        table.appendChild(thead);
        
        // Table body
        const tbody = document.createElement('tbody');
        
        cartItems.forEach(item => {
            const row = document.createElement('tr');
            row.dataset.id = item.id;
            
            // Calculate item total
            const quantity = parseInt(item.quantity) || 1;
            const price = parseFloat(item.price) || 0;
            const total = quantity * price;
            
            row.innerHTML = `
                <td class="item-image">
                    <img src="/static/images/product-${item.style.toLowerCase()}.jpg" class="quote-item-image" alt="${item.name}">
                </td>
                <td>
                    <h5 class="mb-1">${item.name}</h5>
                    <p class="mb-0 text-muted">Style: ${item.style}</p>
                </td>
                <td>
                    <p class="mb-1">Color: ${item.color}</p>
                    <p class="mb-0">Size: ${item.size}</p>
                </td>
                <td>$${price.toFixed(2)}</td>
                <td>
                    <div class="quantity-control">
                        <button class="btn btn-sm btn-outline-secondary quantity-minus">
                            <i class="fas fa-minus"></i>
                        </button>
                        <input type="number" class="form-control quantity-input" value="${quantity}" min="1" max="100">
                        <button class="btn btn-sm btn-outline-secondary quantity-plus">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                </td>
                <td class="item-total">$${total.toFixed(2)}</td>
                <td>
                    <button class="btn btn-sm btn-danger remove-item">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            
            tbody.appendChild(row);
        });
        
        table.appendChild(tbody);
        
        // Clear container and add table
        cartItemsContainer.innerHTML = '';
        cartItemsContainer.appendChild(table);
        
        // Add event listeners for quantity controls and remove buttons
        cartItemsContainer.querySelectorAll('.quantity-minus').forEach(button => {
            button.addEventListener('click', handleQuantityDecrease);
        });
        
        cartItemsContainer.querySelectorAll('.quantity-plus').forEach(button => {
            button.addEventListener('click', handleQuantityIncrease);
        });
        
        cartItemsContainer.querySelectorAll('.quantity-input').forEach(input => {
            input.addEventListener('change', handleQuantityChange);
        });
        
        cartItemsContainer.querySelectorAll('.remove-item').forEach(button => {
            button.addEventListener('click', handleRemoveItem);
        });
    };
    
    // Render cart summary in the quote cart page
    const renderCartSummary = () => {
        if (!cartSummaryContainer) return;
        
        // Calculate subtotal
        const subtotal = cartItems.reduce((acc, item) => {
            const quantity = parseInt(item.quantity) || 1;
            const price = parseFloat(item.price) || 0;
            return acc + (quantity * price);
        }, 0);
        
        // Create summary content
        cartSummaryContainer.innerHTML = `
            <div class="cart-summary-content">
                <h4 class="mb-3">Quote Summary</h4>
                <div class="summary-line">
                    <span>Items:</span>
                    <span>${cartCount}</span>
                </div>
                <div class="summary-line subtotal">
                    <span>Subtotal:</span>
                    <span>$${subtotal.toFixed(2)}</span>
                </div>
                <p class="summary-note">
                    <i class="fas fa-info-circle"></i> 
                    This is a quote only. Prices may vary based on quantity, decoration method, and other factors.
                </p>
                <div class="quote-actions">
                    <button class="btn btn-primary w-100 mb-2" id="request-quote-btn">
                        <i class="fas fa-paper-plane"></i> Request Quote
                    </button>
                    <button class="btn btn-outline-secondary w-100" id="clear-quote-btn">
                        <i class="fas fa-trash"></i> Clear Quote
                    </button>
                </div>
            </div>
        `;
        
        // Add event listeners for quote actions
        if (cartSummaryContainer.querySelector('#request-quote-btn')) {
            cartSummaryContainer.querySelector('#request-quote-btn').addEventListener('click', handleRequestQuote);
        }
        
        if (cartSummaryContainer.querySelector('#clear-quote-btn')) {
            cartSummaryContainer.querySelector('#clear-quote-btn').addEventListener('click', handleClearQuote);
        }
    };
    
    // Event handler for quantity decrease
    const handleQuantityDecrease = (event) => {
        const row = event.target.closest('tr');
        const input = row.querySelector('.quantity-input');
        const currentValue = parseInt(input.value);
        
        if (currentValue > 1) {
            input.value = currentValue - 1;
            updateItemQuantity(row, currentValue - 1);
        }
    };
    
    // Event handler for quantity increase
    const handleQuantityIncrease = (event) => {
        const row = event.target.closest('tr');
        const input = row.querySelector('.quantity-input');
        const currentValue = parseInt(input.value);
        
        if (currentValue < 100) {
            input.value = currentValue + 1;
            updateItemQuantity(row, currentValue + 1);
        }
    };
    
    // Event handler for quantity input change
    const handleQuantityChange = (event) => {
        const input = event.target;
        const row = input.closest('tr');
        let value = parseInt(input.value);
        
        // Validate input
        if (isNaN(value) || value < 1) {
            value = 1;
            input.value = 1;
        } else if (value > 100) {
            value = 100;
            input.value = 100;
        }
        
        updateItemQuantity(row, value);
    };
    
    // Update item quantity in UI and data
    const updateItemQuantity = (row, quantity) => {
        const id = row.dataset.id;
        const item = cartItems.find(item => item.id === id);
        
        if (item) {
            // Update price display
            const price = parseFloat(item.price) || 0;
            const total = price * quantity;
            row.querySelector('.item-total').textContent = `$${total.toFixed(2)}`;
            
            // Highlight the row to indicate change
            row.classList.add('highlight');
            setTimeout(() => {
                row.classList.remove('highlight');
            }, 2000);
            
            // Update the item data
            updateItem(id, { quantity });
        }
    };
    
    // Event handler for remove item button
    const handleRemoveItem = (event) => {
        const row = event.target.closest('tr');
        const id = row.dataset.id;
        
        // Add animation before removing
        row.style.transition = 'opacity 0.3s, transform 0.3s';
        row.style.opacity = '0';
        row.style.transform = 'translateX(20px)';
        
        setTimeout(() => {
            removeItem(id);
        }, 300);
    };
    
    // Event handler for request quote button
    const handleRequestQuote = (event) => {
        // Show quote request form
        const quoteForm = document.getElementById('quote-request-form');
        if (quoteForm) {
            quoteForm.scrollIntoView({ behavior: 'smooth' });
        }
    };
    
    // Event handler for clear quote button
    const handleClearQuote = (event) => {
        if (confirm('Are you sure you want to clear your quote cart?')) {
            clearCart();
        }
    };
    
    // Show notification
    const showNotification = (title, message) => {
        // Check if notification container exists
        let notificationContainer = document.getElementById('notification-container');
        if (!notificationContainer) {
            // Create container if it doesn't exist
            notificationContainer = document.createElement('div');
            notificationContainer.id = 'notification-container';
            document.body.appendChild(notificationContainer);
        }
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.innerHTML = `
            <div class="notification-header">
                <h4>${title}</h4>
                <button class="notification-close">&times;</button>
            </div>
            <div class="notification-body">${message}</div>
        `;
        
        // Add to container
        notificationContainer.appendChild(notification);
        
        // Add event listener for close button
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.classList.add('notification-hiding');
            setTimeout(() => {
                notification.remove();
            }, 300);
        });
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            notification.classList.add('notification-hiding');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 5000);
        
        // Show notification with animation
        setTimeout(() => {
            notification.classList.add('notification-visible');
        }, 10);
    };
    
    // Public API
    return {
        init,
        addItem,
        updateItem,
        removeItem,
        clearCart,
        submitQuote,
        updateCartBadge
    };
})();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', QuoteCart.init);