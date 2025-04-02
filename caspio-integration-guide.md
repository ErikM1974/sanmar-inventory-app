# Caspio Integration Guide for SanMar Inventory App

This guide provides instructions for integrating the SanMar Inventory App with Caspio, a cloud-based database platform. The integration will simplify the management of product data by storing it in Caspio tables and using Caspio DataPages for displaying and interacting with the data.

## Overview

The integration involves:

1. Setting up Caspio tables to store product data
2. Creating a data import process to fetch data from SanMar APIs
3. Developing DataPages to display and interact with the data
4. Integrating the DataPages into the Flask application

## Caspio Database Structure

### Tables

Create the following tables in your Caspio database:

#### 1. Categories

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| CATEGORY_ID | AutoNumber | Primary key |
| CATEGORY_NAME | Text (100) | Name of the category |
| PARENT_CATEGORY_ID | Number | Foreign key to parent category (null for top-level categories) |
| DISPLAY_ORDER | Number | Order to display categories |

#### 2. Products

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| PRODUCT_ID | AutoNumber | Primary key |
| STYLE | Text (50) | SanMar style number |
| PRODUCT_TITLE | Text (255) | Product title |
| CATEGORY_NAME | Text (100) | Category name |
| COLOR_NAME | Text (100) | Color name |
| SIZE | Text (20) | Size name |
| SIZE_INDEX | Number | Order to display sizes |
| BRAND_NAME | Text (100) | Brand name |
| BRAND_LOGO_IMAGE | Text (255) | URL to brand logo image |
| PRODUCT_IMAGE_URL | Text (255) | URL to product image |
| COLOR_SQUARE_IMAGE | Text (255) | URL to color swatch image |
| PRICE | Currency | Regular price |
| PIECE_PRICE | Currency | Price per piece |
| CASE_PRICE | Currency | Price per case |
| CASE_SIZE | Number | Number of pieces in a case |
| KEYWORDS | Text (255) | Keywords for search |

#### 3. Inventory

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| INVENTORY_ID | AutoNumber | Primary key |
| STYLE | Text (50) | SanMar style number |
| COLOR_NAME | Text (100) | Color name |
| SIZE | Text (20) | Size name |
| WAREHOUSE_ID | Text (20) | Warehouse ID |
| QUANTITY | Number | Quantity available |
| LAST_UPDATED | DateTime | Last update timestamp |

## Data Import Process

Use the provided `import_sanmar_to_caspio.py` script to import data from SanMar APIs to Caspio. This script:

1. Fetches categories, products, and inventory data from SanMar APIs
2. Formats the data for Caspio tables
3. Imports the data into Caspio using the Caspio API

### Running the Import

1. Set up environment variables for Caspio API credentials:
   ```
   CASPIO_BASE_URL=your_caspio_base_url
   CASPIO_CLIENT_ID=your_caspio_client_id
   CASPIO_CLIENT_SECRET=your_caspio_client_secret
   ```

2. Run the import script:
   ```
   python import_sanmar_to_caspio.py
   ```

3. Schedule the script to run periodically to keep the data up to date.

## Caspio DataPages

Create the following DataPages in Caspio:

### 1. Category List DataPage

- **Type**: Report
- **Data Source**: Categories table
- **Filter**: WHERE PARENT_CATEGORY_ID IS NULL
- **Sort**: DISPLAY_ORDER ASC
- **Fields to Display**: CATEGORY_NAME
- **Style**: Grid or List view
- **Actions**: Link to Category Detail DataPage

### 2. Category Detail DataPage

- **Type**: Report
- **Data Source**: Products table
- **Filter**: WHERE CATEGORY_NAME = [Parameter]
- **Group By**: STYLE
- **Fields to Display**: STYLE, PRODUCT_TITLE, BRAND_NAME, PRODUCT_IMAGE_URL
- **Style**: Grid view with images
- **Actions**: Link to Product Detail DataPage

### 3. Product Detail DataPage

- **Type**: Report
- **Data Source**: Products table
- **Filter**: WHERE STYLE = [Parameter]
- **Fields to Display**: STYLE, PRODUCT_TITLE, BRAND_NAME, BRAND_LOGO_IMAGE, COLOR_NAME, SIZE, PRICE, PIECE_PRICE, CASE_PRICE, CASE_SIZE, PRODUCT_IMAGE_URL
- **Style**: Tabbed view with colors and sizes
- **Additional Features**: 
  - Color selection
  - Size selection
  - Price display
  - Inventory lookup (using a separate DataPage)

### 4. Inventory Lookup DataPage

- **Type**: Report
- **Data Source**: Inventory table
- **Filter**: WHERE STYLE = [Parameter] AND COLOR_NAME = [Parameter] AND SIZE = [Parameter]
- **Fields to Display**: WAREHOUSE_ID, QUANTITY, LAST_UPDATED
- **Style**: Table view
- **Additional Features**: Total quantity calculation

### 5. Search DataPage

- **Type**: Search
- **Data Source**: Products table
- **Search Fields**: STYLE, PRODUCT_TITLE, CATEGORY_NAME, BRAND_NAME, KEYWORDS
- **Results Fields**: STYLE, PRODUCT_TITLE, BRAND_NAME, PRODUCT_IMAGE_URL
- **Style**: Grid view with images
- **Actions**: Link to Product Detail DataPage

## Integration with Flask Application

The Flask application integrates with Caspio in two ways:

1. **API Integration**: Using the Caspio API to fetch data programmatically
2. **DataPage Embedding**: Embedding Caspio DataPages in the application

### API Integration

The `caspio_client.py` module provides a client for interacting with the Caspio API. This client is used by the `app_caspio_routes.py` module to fetch data from Caspio and render it in the application's templates.

### DataPage Embedding

Caspio DataPages can be embedded in the application's templates using iframes or JavaScript. The `templates/caspio_index.html`, `templates/caspio_category.html`, and `templates/caspio_product.html` templates are set up to display Caspio DataPages.

## Deployment Steps

1. Create the Caspio tables as described above.
2. Run the import script to populate the tables with data.
3. Create the Caspio DataPages as described above.
4. Deploy the DataPages and note their deployment IDs.
5. Update the Flask application to use the deployed DataPages.
6. Test the integration to ensure everything is working correctly.

## Benefits of Caspio Integration

- **Simplified Data Management**: Caspio provides a user-friendly interface for managing data.
- **Reduced API Calls**: Data is stored in Caspio, reducing the need for frequent API calls to SanMar.
- **Improved Performance**: Caspio's cloud infrastructure provides fast data access.
- **Customizable UI**: Caspio DataPages can be customized to match the application's design.
- **Scalability**: Caspio can handle large amounts of data and traffic.

## Maintenance

- Regularly run the import script to keep the data up to date.
- Monitor the Caspio usage to ensure you stay within your plan limits.
- Update the DataPages as needed to accommodate changes in the application's requirements.