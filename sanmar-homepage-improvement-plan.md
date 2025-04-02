# SanMar Inventory Homepage Improvement Plan

## Overview
This document outlines the improvements made to the Northwest Custom Apparel SanMar Inventory app homepage and the customer-facing features. The enhancements focus on creating a beautiful, functional UI with integrated Caspio datapages, an online quote cart system, and a more organized page structure.

## New Components & Features

### 1. Customer-Facing Routes Module
- Created `app_customer_routes.py` to separate customer-facing routes from the internal inventory management routes
- Organized routes by function: product views, category browsing, quote system, etc.
- Added retail pricing support with a 40% margin on case prices

### 2. Quote Cart System
- Implemented complete quote cart functionality in `quote-cart.js`
- Features:
  - Add products to quote with size, color and quantity
  - View and edit quote items
  - Select decoration methods and options
  - Calculate accurate pricing based on quantity and decoration
  - Submit quote requests with customer information
  - localStorage persistence for cart contents

### 3. Pricing Modules
- **Retail Pricing Module** (`retail-pricing.js`):
  - Calculates retail prices with a 40% margin on case prices
  - Handles size upcharges for larger sizes (2XL+)
  - Supports quantity discounts
  
- **Decoration Pricing Module** (`decoration-pricing.js`):
  - Supports multiple decoration methods:
    - Embroidery
    - Screen Printing
    - Direct to Garment (DTG)
    - Heat Transfer
    - Cap Embroidery
  - Volume-based pricing tiers
  - Special options pricing (metallic thread, oversize designs, etc.)
  - Multiple location pricing

### 4. Enhanced Homepage UI
- **Redesigned Homepage** (`enhanced-index.html`):
  - Modern, responsive Bootstrap 5 layout
  - Clear navigation with categories in the sidebar
  - Quick search options with style number and keyword search
  - Advanced search with filters for color, size, brand, price range, and inventory
  - Featured products carousel showcase
  - Top sellers and new arrivals sections
  - Integrated quote cart indicator

- **Improved Styling** (`home-style.css`):
  - Consistent color scheme matching Northwest Custom Apparel branding
  - Responsive product cards with hover effects
  - Mobile-friendly layout adjustments
  - Enhanced visual hierarchy for better user experience

### 5. Quote Cart Page
- **Quote Cart UI** (`quote-cart.html`):
  - Product list with images, details, and quantities
  - Decoration options selection
  - Price summary with subtotals
  - Customer information form
  - Quote submission system
  - Confirmation display

## Integration with Caspio

The new design provides placeholder sections for embedding Caspio datapages:

1. **Category Listing** (`#categories-datapage`)
   - Left sidebar with category listings and product counts
   - Links to category-specific product pages

2. **Style Search** (`#style-search-datapage`)
   - Quick search by style number

3. **Keyword Search** (`#keyword-search-datapage`)
   - Search across product names and descriptions

4. **Top Sellers Gallery** (`#top-sellers-datapage`)
   - Visual display of most popular products

5. **New Arrivals Gallery** (`#new-arrivals-datapage`)
   - Latest products added to the inventory

## How to Use

### Embedding Caspio Datapages
1. Create the corresponding datapages in Caspio:
   - Categories listing datapage
   - Style search datapage
   - Keyword search datapage
   - Top sellers gallery datapage
   - New arrivals gallery datapage
   
2. Replace the placeholder content in each section with the Caspio embed code:
   ```html
   <!-- Example for categories datapage -->
   <div id="categories-datapage">
     <!-- Replace this comment with Caspio embed code -->
   </div>
   ```

### Page Navigation
The new structure supports the following page organization:

- `/` - Homepage with search and featured products
- `/customer/products` - All products listing
- `/customer/product/{style}` - Individual product page
- `/customer/category/{category}` - Category-specific product listings
- `/customer/new-arrivals` - New products showcase
- `/customer/top-sellers` - Popular products gallery
- `/customer/resources` - Resources and documentation
- `/quote` - Quote cart and checkout process

### Adding New Pages
To add new pages to the system:

1. Create a new HTML template in the `templates/` directory
2. Add a new route in `app_customer_routes.py`:
   ```python
   @app.route('/customer/new-page')
   def customer_new_page():
       return render_template('new-page.html')
   ```
3. Add a link to the new page in the navigation menu in `enhanced-index.html`

## Next Steps

### Short-term Improvements
1. Create remaining customer-facing templates:
   - All products listing page
   - Category-specific product page
   - New arrivals page
   - Top sellers page
   - Resources page

2. Improve product detail page with:
   - More detailed inventory information
   - Size chart integration
   - Related products section

3. Implement additional search and filter options:
   - Filter by brand
   - Filter by product type
   - Price range filtering

### Long-term Enhancements
1. User account system:
   - Save quotes for later
   - View quote history
   - Favorite products

2. Inventory alerts:
   - Stock level notifications
   - Automatic email for low inventory

3. Order management:
   - Track order status
   - Manage pending orders
   - Process payment integrations

4. Advanced product visualization:
   - 360° product views
   - Virtual try-on for apparel
   - Custom decoration preview

## Technical Details

### JavaScript Modules
- **quote-cart.js**: Manages the quote cart functionality
- **retail-pricing.js**: Calculates retail pricing with margin
- **decoration-pricing.js**: Handles decoration pricing logic

### CSS Files
- **home-style.css**: Homepage-specific styling
- **style.css**: Global styling for the application

### Templates
- **enhanced-index.html**: Main homepage template
- **customer-product.html**: Product detail page template
- **quote-cart.html**: Quote cart page template

### Python Modules
- **app_customer_routes.py**: Customer-facing route handlers
- **app.py**: Core application with API routes and admin functions