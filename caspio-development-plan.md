# Caspio-Development Branch - Implementation Plan

## Overview
This branch focuses on restructuring the SanMar Inventory application to maximize the use of Caspio datapages for easier maintenance and faster development. The goal is to create a beautiful, functional UI that primarily uses Caspio datapages for data display and interaction.

## Architecture

### Core Components
1. **Flask Application**
   - Serves as a container/wrapper for Caspio datapages
   - Provides consistent header, footer, navigation
   - Handles routing between pages
   - Offers API endpoints where needed

2. **Caspio Datapages**
   - Embedded in Flask templates
   - Handle all data display and interaction
   - Connect directly to SanMar data

3. **JavaScript Glue Code**
   - Enhances interaction between Caspio datapages
   - Manages the quote cart functionality
   - Provides UI improvements and animations

### Page Structure
- **Homepage** (`/`)
  - Modern header with navigation (Home, Products, New Arrivals, Top Sellers, Quote Cart, Resources)
  - Left sidebar with SanMar product categories:
    - NEW (highlighted section)
    - Brands
    - T-Shirts
    - Polos/Knits
    - Sweatshirts/Fleece
    - Caps
    - Activewear
    - Outerwear
    - Woven/Dress Shirts
    - Bottoms
    - Workwear
    - Bags
    - Accessories
    - Personal Protection
    - Women's
    - Youth
    - Outlet
  - Featured products area (Caspio gallery datapage)
  - Quick search (existing Caspio search datapage)
  - New arrivals section (Caspio datapage)
  - Top sellers section (Caspio datapage)

- **Category Pages** (`/categories`, `/subcategory/<id>`)
  - Product grid with filtering (Caspio datapage)
  - Left sidebar with subcategory navigation (Caspio datapage)

- **Product Detail** (`/product/<style>`)
  - Enhanced version of current product page
  - "Add to Quote" functionality

- **Quote System** (`/quote`)
  - Quote cart functionality (Caspio datapage)
  - Quote request submission (Caspio form)

## Caspio Datapages Requirements

1. **Category Navigation Datapage**
   - Vertical list showing main SanMar categories as displayed in the mockup
   - Links to filtered product pages
   - Uses `caspio_api.get_categories()` for data
   - Includes styling to highlight the "NEW" section

2. **Featured Products Datapage**
   - Grid layout of selected featured products
   - Each card shows:
     - Product image (from SanMar API)
     - Product title (e.g., "Port & Company PC61")
     - Product style description (e.g., "Essential T-Shirt")
     - Starting price ("From $X.XX")
     - "Add to Quote" button
   - Optional "New" or "Sale" badge for special items
   - Clickable to product detail page

3. **New Arrivals Datapage**
   - Similar layout to Featured Products
   - Filtered to show only recently added products
   - Same card design and functionality

4. **Top Sellers Datapage**
   - Similar layout to Featured Products
   - Filtered by popularity or sales data
   - Same card design and functionality

5. **Product Grid Datapage**
   - Main product browsing experience when a category is selected
   - Filterable by multiple attributes (size, color, brand)
   - "Add to Quote" button on each product
   - Pagination for large result sets

6. **Quote Cart Datapage**
   - Creates new table in Caspio to store quote requests
   - Allows adding products, specifying quantities, colors, and sizes
   - Calculates estimated pricing based on quantity
   - Form for customer information
   - Submit button to send quote request

## Implementation Phases

### Phase 1: Homepage Redesign
- Update templates to support new layout with sidebar
- Embed existing Caspio datapages
- Create template placeholders for new datapages
- Enhance CSS for better styling
- Implement mockup homepage (/mockup route) to validate design before full implementation

### Phase 2: Category/Product Browsing
- Implement left sidebar category navigation
- Enhance product grid display
- Add filtering capabilities

### Phase 3: Product Detail Enhancements
- Update product detail page
- Add "Add to Quote" functionality
- Improve image display and color selection

### Phase 4: Quote and Decoration System
- Create quote cart functionality with product selection
- Implement decoration method selection and pricing
- Add decoration options and quantity-based pricing tiers
- Implement order total calculation with product and decoration costs
- Create quote request submission form with customer information
- Add quote history for logged-in users
- Develop admin interface for quote management

### Phase 5: User Accounts
- Add user account functionality
- Implement saved quotes and favorites
- Add order history and status tracking
- Create account preferences

### Required Caspio Tables

1. **SanMar_Products** (Existing - using `SanMar_Bulk_251816_Feb2024`)
   - Contains all product information
   
7. **Decoration_Methods**
   - Fields: ID, MethodName, Description, SetupFee, MinimumCharge
   - Stores the basic decoration methods (Embroidery, Cap Embroidery, Screen Print, DTG, Transfers)

8. **Decoration_Price_Tiers**
   - Fields: ID, MethodID (FK to Decoration_Methods), MinQuantity, MaxQuantity, FirstLocationPrice, AdditionalLocationPrice, IsFirstLocation
   - Stores pricing tiers based on quantity ranges for each decoration method

9. **Decoration_Options**
   - Fields: ID, MethodID (FK to Decoration_Methods), OptionName, PriceType (per-piece, flat), Price, Description
   - Stores additional options for each decoration method (nameAdd, oversize, metallic, etc.)

10. **Decoration_Color_Pricing** (For Screen Print only)
    - Fields: ID, ColorCount, SetupFee, PriceModifier
    - Stores how pricing changes based on number of colors for screen printing

2. **Featured_Products**
   - Fields: ID, ProductID, DisplayOrder, BadgeType, Featured_Until
   - For manually curating the featured products section

3. **New_Arrivals**
   - Auto-populated based on product release date
   - Fields: ID, ProductID, ReleaseDate

4. **Top_Sellers**
   - Auto-populated based on sales data
   - Fields: ID, ProductID, SalesCount, LastUpdated

5. **Quote_Requests**
   - Fields: ID, CustomerName, Email, Phone, CompanyName, Notes, DateSubmitted, Status
   
6. **Quote_Items**
   - Fields: ID, QuoteID, ProductID, Style, Color, Size, Quantity, UnitPrice, Subtotal

## Decoration Pricing Structure

The decoration pricing system we've implemented follows these principles:

1. **Method-Based Pricing**: Each decoration method (Embroidery, Screen Print, etc.) has its own pricing structure

2. **Quantity Tiers**: Prices decrease as quantity increases, with defined breakpoints (1-11, 12-23, etc.)

3. **Location-Based**: First location has a higher price than additional locations

4. **Options**: Each method has specific options that can affect pricing:
   - **Embroidery**: Metallic thread, oversize designs, personalization
   - **Cap Embroidery**: 3D embroidery, metallic thread
   - **Screen Print**: Number of colors affects both setup fees and per-piece costs
   - **DTG**: Oversize designs
   - **Transfers**: Oversize designs

5. **Components of Pricing**:
   - **Setup Fee**: One-time charge for preparing artwork/screens
   - **Minimum Charge**: Ensures small orders remain profitable
   - **Per-Piece Price**: Based on quantity tier and decoration method
   - **Additional Locations**: Discounted pricing for decorating multiple locations
   - **Options**: Add-ons that can be selected by the customer

This structure is implemented in the frontend JavaScript with the decoration-pricing.js module, with data that would ultimately be sourced from the Caspio tables described above.

In the production implementation, we'll create Caspio DataPages that allow:
1. Administrators to update pricing tiers and options
2. Customers to see real-time pricing calculations
3. The quote system to store decoration choices with the order

The current implementation uses static data in the JavaScript file, but is structured to easily transition to API-based pricing data from Caspio when ready.

## Expected Outcomes

- Redesigned homepage with improved navigation
- Category-based product browsing
- Enhanced product detail pages
- Interactive decoration pricing calculator
- Complete quote system with decoration options