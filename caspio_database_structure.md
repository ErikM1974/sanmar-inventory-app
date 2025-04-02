# Caspio Database Structure for SanMar Inventory App

This document outlines the database structure and DataPages needed for the SanMar Inventory App in Caspio.

## Database Tables

### 1. Categories Table

This table stores the product categories from SanMar.

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| CATEGORY_ID | AutoNumber | Primary key |
| CATEGORY_NAME | Text(100) | Category name |
| PARENT_CATEGORY_ID | Number | Foreign key to parent category (for hierarchical categories) |
| DISPLAY_ORDER | Number | Order to display categories |

### 2. Products Table

This table stores the product information from SanMar.

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| PRODUCT_ID | AutoNumber | Primary key |
| STYLE | Text(50) | Product style number |
| PRODUCT_TITLE | Text(255) | Product title |
| CATEGORY_NAME | Text(100) | Category name (foreign key to Categories table) |
| COLOR_NAME | Text(100) | Color name |
| SIZE | Text(20) | Size name |
| SIZE_INDEX | Number | Index for sorting sizes in correct order |
| BRAND_NAME | Text(100) | Brand name |
| BRAND_LOGO_IMAGE | Text(255) | URL to brand logo image |
| PRODUCT_IMAGE_URL | Text(255) | URL to product image |
| COLOR_SQUARE_IMAGE | Text(255) | URL to color square image |
| PRICE | Currency | Regular price |
| PIECE_PRICE | Currency | Price per piece |
| CASE_PRICE | Currency | Price per case |
| CASE_SIZE | Number | Number of pieces in a case |
| KEYWORDS | Text(1000) | Keywords for search |

### 3. Inventory Table

This table stores the inventory information from SanMar.

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| INVENTORY_ID | AutoNumber | Primary key |
| STYLE | Text(50) | Product style number (foreign key to Products table) |
| COLOR_NAME | Text(100) | Color name |
| SIZE | Text(20) | Size name |
| WAREHOUSE_ID | Text(20) | Warehouse ID |
| QUANTITY | Number | Quantity available |
| LAST_UPDATED | DateTime | Last updated timestamp |

## DataPages

### 1. Category List DataPage

This DataPage displays a list of all categories.

**Type:** Tabular Report
**Data Source:** Categories Table
**Fields to Display:**
- CATEGORY_NAME
- DISPLAY_ORDER

**Sorting:** DISPLAY_ORDER (Ascending)
**Filtering:** None
**Actions:** Link to Category Detail DataPage

### 2. Category Detail DataPage

This DataPage displays products in a specific category.

**Type:** Tabular Report
**Data Source:** Products Table
**Fields to Display:**
- STYLE
- PRODUCT_TITLE
- BRAND_NAME
- PRODUCT_IMAGE_URL
- COLOR_NAME
- COLOR_SQUARE_IMAGE

**Sorting:** PRODUCT_TITLE (Ascending)
**Filtering:** CATEGORY_NAME = [Parameter]
**Actions:** Link to Product Detail DataPage

### 3. Product Detail DataPage

This DataPage displays detailed information about a specific product.

**Type:** Tabular Report with Tabs
**Data Source:** Products Table
**Fields to Display:**
- STYLE
- PRODUCT_TITLE
- BRAND_NAME
- BRAND_LOGO_IMAGE
- PRODUCT_IMAGE_URL
- COLOR_NAME
- COLOR_SQUARE_IMAGE
- SIZE
- PRICE
- PIECE_PRICE
- CASE_PRICE
- CASE_SIZE

**Sorting:** SIZE_INDEX (Ascending)
**Filtering:** STYLE = [Parameter]
**Actions:** Link to Inventory DataPage

### 4. Inventory DataPage

This DataPage displays inventory information for a specific product.

**Type:** Tabular Report
**Data Source:** Inventory Table
**Fields to Display:**
- STYLE
- COLOR_NAME
- SIZE
- WAREHOUSE_ID
- QUANTITY
- LAST_UPDATED

**Sorting:** WAREHOUSE_ID (Ascending)
**Filtering:** STYLE = [Parameter], COLOR_NAME = [Parameter], SIZE = [Parameter]
**Actions:** None

### 5. Search DataPage

This DataPage allows users to search for products.

**Type:** Search Form with Results
**Data Source:** Products Table
**Search Fields:**
- STYLE
- PRODUCT_TITLE
- CATEGORY_NAME
- BRAND_NAME
- KEYWORDS

**Results Fields to Display:**
- STYLE
- PRODUCT_TITLE
- BRAND_NAME
- PRODUCT_IMAGE_URL
- COLOR_NAME
- COLOR_SQUARE_IMAGE

**Sorting:** PRODUCT_TITLE (Ascending)
**Actions:** Link to Product Detail DataPage

## Integration with Flask Application

The Flask application will interact with Caspio through the following methods:

1. **Data Import**: Use the `import_sanmar_to_caspio.py` script to import data from SanMar APIs to Caspio.
2. **Data Retrieval**: Use the `caspio_client.py` module to retrieve data from Caspio for display in the Flask application.
3. **API Endpoints**: Use the `app_caspio_routes.py` module to create API endpoints that fetch data from Caspio and return it in the format expected by the frontend.

## Deployment Steps

1. Create the Caspio database tables as described above.
2. Create the DataPages as described above.
3. Configure the Caspio API credentials in the Flask application's `.env` file.
4. Run the `import_sanmar_to_caspio.py` script to import data from SanMar APIs to Caspio.
5. Update the Flask application to use the Caspio routes by adding the following to `app.py`:

```python
from app_caspio_routes import register_caspio_routes

# Register Caspio routes
register_caspio_routes(app)
```

6. Test the application to ensure it's correctly retrieving data from Caspio.

## Benefits of Using Caspio

1. **Reduced API Calls**: By storing data in Caspio, we reduce the number of API calls to SanMar, which can help with rate limiting and performance.
2. **Improved Performance**: Caspio's database is optimized for fast queries, which can improve the performance of the application.
3. **Data Caching**: Caspio acts as a cache for SanMar data, which can be updated periodically rather than on every request.
4. **Simplified Development**: Caspio's DataPages provide a quick way to create user interfaces without writing custom code.
5. **Reduced Server Load**: By offloading data storage and retrieval to Caspio, we reduce the load on our application server.