# Caspio DataPages Design for SanMar Integration

This document outlines the design of Caspio DataPages for the SanMar inventory application integration.

## Tables

### 1. Categories Table

This table stores category information from SanMar.

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| CATEGORY_ID | AutoNumber | Primary key |
| CATEGORY_NAME | Text (255) | Name of the category |
| PARENT_CATEGORY_ID | Number | Foreign key to parent category (null for top-level categories) |
| DISPLAY_ORDER | Number | Order to display categories |

### 2. Products Table

This table stores product information from SanMar.

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| PRODUCT_ID | AutoNumber | Primary key |
| STYLE | Text (255) | SanMar style number |
| PRODUCT_TITLE | Text (255) | Product title |
| CATEGORY_NAME | Text (255) | Category name |
| SUBCATEGORY_NAME | Text (255) | Subcategory name |
| COLOR_NAME | Text (255) | Color name |
| SIZE | Text (255) | Size name |
| SIZE_INDEX | Number | Index for sorting sizes |
| BRAND_NAME | Text (255) | Brand name |
| BRAND_LOGO_IMAGE | Text (255) | URL to brand logo image |
| PRODUCT_IMAGE_URL | Text (255) | URL to product image |
| COLOR_SQUARE_IMAGE | Text (255) | URL to color square image |
| PRICE | Currency | List price |
| PIECE_PRICE | Currency | Price per piece |
| CASE_PRICE | Currency | Price per case |
| CASE_SIZE | Number | Number of pieces in a case |
| PROGRAM_PRICE | Currency | Program-specific pricing |
| KEYWORDS | Text (255) | Keywords for search |

### 3. Inventory Table

This table stores inventory information from SanMar.

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| INVENTORY_ID | AutoNumber | Primary key |
| STYLE | Text (255) | SanMar style number |
| COLOR_NAME | Text (255) | Color name |
| SIZE | Text (255) | Size name |
| WAREHOUSE_ID | Text (50) | Warehouse ID |
| QUANTITY | Number | Quantity available |
| LAST_UPDATED | DateTime | Last updated timestamp |

## DataPages

### 1. Category Browser DataPage

This DataPage allows users to browse categories and subcategories.

**Type:** Search and Report
**Data Source:** Categories Table
**Features:**
- Display categories in a hierarchical structure
- Link to Product Browser DataPage filtered by category

### 2. Product Browser DataPage

This DataPage allows users to browse and search products.

**Type:** Search and Report
**Data Source:** Products Table
**Features:**
- Search by style, title, brand, etc.
- Filter by category, brand, etc.
- Sort by various fields
- Display product images
- Link to Product Detail DataPage

### 3. Product Detail DataPage

This DataPage displays detailed information about a product.

**Type:** Details
**Data Source:** Products Table
**Features:**
- Display all product information
- Show product images
- Display pricing information
- Link to Inventory DataPage filtered by product

### 4. Inventory DataPage

This DataPage displays inventory information for products.

**Type:** Search and Report
**Data Source:** Inventory Table
**Features:**
- Filter by style, color, size, etc.
- Display inventory levels by warehouse
- Show last updated timestamp

### 5. Product Search DataPage

This DataPage allows users to search for products.

**Type:** Search and Report
**Data Source:** Products Table
**Features:**
- Advanced search options
- Filter by multiple criteria
- Sort by various fields
- Display results in a grid or list view

## Deployment Steps

1. Create the Categories, Products, and Inventory tables in Caspio.
2. Set up the DataPages as described above.
3. Configure the DataPage parameters and styles to match the application's design.
4. Deploy the DataPages to the application.
5. Set up the scheduled tasks to run the quarterly_product_update.py and daily_inventory_import.py scripts.

## Integration with Python Application

The Python application will:

1. Fetch data from SanMar APIs (or use the existing Sanmar_Bulk_251816_Feb2024 table).
2. Process and transform the data as needed.
3. Import the data into the Caspio tables using the Caspio API.
4. The DataPages will then display the data from the Caspio tables.

This approach simplifies the application by offloading the data storage and presentation to Caspio, while still allowing for custom data processing and integration with SanMar APIs.