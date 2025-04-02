# Caspio Implementation Plan for Northwest Custom Apparel

This document outlines the plan for implementing Caspio DataPages to simplify the Northwest Custom Apparel product catalog application.

## Overview

The current application uses SanMar APIs to fetch product data, which can be complex and sometimes unreliable. By moving this data to Caspio, we can:

1. Reduce API calls to SanMar
2. Improve application performance
3. Simplify the codebase
4. Provide a more reliable user experience

## Caspio Database Structure

### Tables

#### 1. Product_Catalog

This will be the main table storing all product information from SanMar.

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| PK_ID | AutoNumber | Primary key |
| UNIQUE_KEY | Number | SanMar's unique identifier for the product |
| STYLE | Text | Product style number (e.g., PC61) |
| PRODUCT_TITLE | Text | Full product name |
| PRODUCT_DESCRIPTION | Text | Detailed product description |
| AVAILABLE_SIZES | Text | List of available sizes |
| BRAND_LOGO_IMAGE | Text | URL to brand logo image |
| THUMBNAIL_IMAGE | Text | URL to product thumbnail |
| COLOR_SWATCH_IMAGE | Text | URL to color swatch image |
| PRODUCT_IMAGE | Text | URL to main product image |
| SPEC_SHEET | Text | URL to specification sheet PDF |
| PRICE_TEXT | Text | Text describing pricing details |
| SUGGESTED_PRICE | Number | MSRP price |
| CATEGORY_NAME | Text | Primary product category |
| SUBCATEGORY_NAME | Text | Product subcategory |
| COLOR_NAME | Text | Color name |
| COLOR_SQUARE_IMAGE | Text | URL to color square image |
| COLOR_PRODUCT_IMAGE | Text | URL to product in specific color |
| COLOR_PRODUCT_IMAGE_THUMBNAIL | Text | URL to thumbnail of product in specific color |
| SIZE | Text | Size (S, M, L, XL, etc.) |
| QTY | Number | Inventory quantity |
| PIECE_WEIGHT | Number | Weight per piece |
| PIECE_PRICE | Number | Price per piece |
| DOZENS_PRICE | Number | Price per dozen |
| CASE_PRICE | Number | Price per case |
| PRICE_GROUP | Text | Price group code |
| CASE_SIZE | Number | Number of items per case |
| INVENTORY_KEY | Number | Inventory reference key |
| SIZE_INDEX | Number | Index for sorting sizes |
| MILL | Text | Manufacturer name |
| PRODUCT_STATUS | Text | Active, Discontinued, etc. |
| COMPANION_STYLES | Text | Related style numbers |
| MSRP | Number | Manufacturer's suggested retail price |
| MAP_PRICING | Text | Minimum advertised price |
| FRONT_MODEL_IMAGE_URL | Text | URL to front model image |
| BACK_MODEL_IMAGE | Text | URL to back model image |
| FRONT_FLAT_IMAGE | Text | URL to front flat image |
| BACK_FLAT_IMAGE | Text | URL to back flat image |
| PMS_COLOR | Text | Pantone color code |
| BRAND_NAME | Text | Brand name |
| KEYWORDS | Text | Search keywords |

#### 2. Inventory_Levels (Optional)

If we need real-time inventory, we can keep this in a separate table that's updated more frequently.

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| PK_ID | AutoNumber | Primary key |
| STYLE | Text | Product style number |
| COLOR | Text | Color name |
| SIZE | Text | Size |
| WAREHOUSE_ID | Text | Warehouse identifier |
| QUANTITY | Number | Available quantity |
| LAST_UPDATED | DateTime | Timestamp of last update |

## Caspio DataPages

### 1. Category Gallery DataPage (dp1)

This DataPage will display products filtered by category and subcategory.

**Features:**
- Grid layout with product images
- Filtering by category and subcategory
- Sorting options (price, name, etc.)
- Pagination
- Quick view functionality

**Parameters:**
- category: Filter by category name
- subcategory: Filter by subcategory name (optional)

### 2. Product Detail DataPage (dp2)

This DataPage will display detailed information about a specific product.

**Features:**
- Product images (multiple views)
- Color swatches
- Size selection
- Pricing information
- Inventory availability
- Add to quote functionality

**Parameters:**
- style: Product style number
- color: Selected color (optional)

### 3. Search Results DataPage (dp3)

This DataPage will display search results based on user queries.

**Features:**
- List of matching products
- Filtering options
- Sorting options
- Pagination

**Parameters:**
- q: Search query

## Data Import Process

1. **Initial Import:**
   - Export data from SanMar API using a script
   - Format the data for Caspio import
   - Import into Caspio Product_Catalog table

2. **Regular Updates:**
   - Create a scheduled task to update product data daily
   - Update inventory data more frequently (hourly or as needed)
   - Log update history for troubleshooting

## Integration with Existing Application

1. **Update Routes:**
   - Modify category and product detail routes to use Caspio embed codes
   - Keep existing API routes as fallbacks

2. **Update Templates:**
   - Modify templates to accommodate Caspio DataPage embeds
   - Ensure consistent styling between application and DataPages

3. **JavaScript Integration:**
   - Add JavaScript to handle interactions between application and DataPages
   - Implement event listeners for DataPage actions

## Deployment Steps

1. **Caspio Setup:**
   - Create the necessary tables in Caspio
   - Design and publish the DataPages
   - Set up authentication and permissions

2. **Data Migration:**
   - Run the initial data import script
   - Verify data integrity
   - Set up scheduled updates

3. **Application Updates:**
   - Update the application code to use Caspio DataPages
   - Test thoroughly
   - Deploy to production

4. **Monitoring and Maintenance:**
   - Monitor application performance
   - Set up alerts for data update failures
   - Regularly review and optimize DataPage designs

## Benefits

1. **Reduced API Dependency:**
   - Less reliance on SanMar API availability
   - Fewer API calls means better performance

2. **Simplified Codebase:**
   - Less custom code to maintain
   - Easier to update and extend

3. **Improved User Experience:**
   - Faster page loads
   - More consistent data presentation
   - Better search and filtering capabilities

4. **Easier Administration:**
   - Non-technical staff can update product data through Caspio
   - Simplified reporting and analytics

## Timeline

1. **Phase 1 (Week 1):**
   - Set up Caspio tables
   - Create initial data import script
   - Import test data

2. **Phase 2 (Week 2):**
   - Design and publish DataPages
   - Integrate with test application
   - Initial testing

3. **Phase 3 (Week 3):**
   - Full data import
   - Complete application integration
   - Comprehensive testing

4. **Phase 4 (Week 4):**
   - Production deployment
   - Monitoring and optimization
   - Documentation and training