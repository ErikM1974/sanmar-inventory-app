# Caspio Deployment Guide for SanMar Inventory App

This guide outlines the steps to deploy the Caspio solution for the SanMar Inventory App.

## Prerequisites

1. Caspio account with API access
2. SanMar API credentials
3. Python 3.7+ installed
4. Flask application codebase

## Step 1: Set Up Caspio Database

1. Log in to your Caspio account.
2. Create a new application called "SanMar Inventory App".
3. Create the following tables as defined in the `caspio_database_structure.md` document:
   - Categories
   - Products
   - Inventory

### Categories Table

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| CATEGORY_ID | AutoNumber | Primary key |
| CATEGORY_NAME | Text(100) | Category name |
| PARENT_CATEGORY_ID | Number | Foreign key to parent category |
| DISPLAY_ORDER | Number | Order to display categories |

### Products Table

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| PRODUCT_ID | AutoNumber | Primary key |
| STYLE | Text(50) | Product style number |
| PRODUCT_TITLE | Text(255) | Product title |
| CATEGORY_NAME | Text(100) | Category name |
| COLOR_NAME | Text(100) | Color name |
| SIZE | Text(20) | Size name |
| SIZE_INDEX | Number | Index for sorting sizes |
| BRAND_NAME | Text(100) | Brand name |
| BRAND_LOGO_IMAGE | Text(255) | URL to brand logo image |
| PRODUCT_IMAGE_URL | Text(255) | URL to product image |
| COLOR_SQUARE_IMAGE | Text(255) | URL to color square image |
| PRICE | Currency | Regular price |
| PIECE_PRICE | Currency | Price per piece |
| CASE_PRICE | Currency | Price per case |
| CASE_SIZE | Number | Number of pieces in a case |
| KEYWORDS | Text(1000) | Keywords for search |

### Inventory Table

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| INVENTORY_ID | AutoNumber | Primary key |
| STYLE | Text(50) | Product style number |
| COLOR_NAME | Text(100) | Color name |
| SIZE | Text(20) | Size name |
| WAREHOUSE_ID | Text(20) | Warehouse ID |
| QUANTITY | Number | Quantity available |
| LAST_UPDATED | DateTime | Last updated timestamp |

## Step 2: Create DataPages

Create the following DataPages as defined in the `caspio_database_structure.md` document:

1. Category List DataPage
2. Category Detail DataPage
3. Product Detail DataPage
4. Inventory DataPage
5. Search DataPage

### Category List DataPage

1. Go to "DataPages" in your Caspio application.
2. Click "New DataPage".
3. Select "Tabular Report" as the DataPage type.
4. Select "Categories" as the data source.
5. Select the following fields to display:
   - CATEGORY_NAME
   - DISPLAY_ORDER
6. Set sorting to DISPLAY_ORDER (Ascending).
7. Add a link to the Category Detail DataPage, passing CATEGORY_NAME as a parameter.
8. Save and deploy the DataPage.

### Category Detail DataPage

1. Go to "DataPages" in your Caspio application.
2. Click "New DataPage".
3. Select "Tabular Report" as the DataPage type.
4. Select "Products" as the data source.
5. Select the following fields to display:
   - STYLE
   - PRODUCT_TITLE
   - BRAND_NAME
   - PRODUCT_IMAGE_URL
   - COLOR_NAME
   - COLOR_SQUARE_IMAGE
6. Set sorting to PRODUCT_TITLE (Ascending).
7. Add a filter: CATEGORY_NAME = [Parameter].
8. Add a link to the Product Detail DataPage, passing STYLE as a parameter.
9. Save and deploy the DataPage.

### Product Detail DataPage

1. Go to "DataPages" in your Caspio application.
2. Click "New DataPage".
3. Select "Tabular Report with Tabs" as the DataPage type.
4. Select "Products" as the data source.
5. Select the following fields to display:
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
6. Set sorting to SIZE_INDEX (Ascending).
7. Add a filter: STYLE = [Parameter].
8. Add a link to the Inventory DataPage, passing STYLE, COLOR_NAME, and SIZE as parameters.
9. Save and deploy the DataPage.

### Inventory DataPage

1. Go to "DataPages" in your Caspio application.
2. Click "New DataPage".
3. Select "Tabular Report" as the DataPage type.
4. Select "Inventory" as the data source.
5. Select the following fields to display:
   - STYLE
   - COLOR_NAME
   - SIZE
   - WAREHOUSE_ID
   - QUANTITY
   - LAST_UPDATED
6. Set sorting to WAREHOUSE_ID (Ascending).
7. Add filters:
   - STYLE = [Parameter]
   - COLOR_NAME = [Parameter]
   - SIZE = [Parameter]
8. Save and deploy the DataPage.

### Search DataPage

1. Go to "DataPages" in your Caspio application.
2. Click "New DataPage".
3. Select "Search Form with Results" as the DataPage type.
4. Select "Products" as the data source.
5. Add the following search fields:
   - STYLE
   - PRODUCT_TITLE
   - CATEGORY_NAME
   - BRAND_NAME
   - KEYWORDS
6. Select the following fields to display in the results:
   - STYLE
   - PRODUCT_TITLE
   - BRAND_NAME
   - PRODUCT_IMAGE_URL
   - COLOR_NAME
   - COLOR_SQUARE_IMAGE
7. Set sorting to PRODUCT_TITLE (Ascending).
8. Add a link to the Product Detail DataPage, passing STYLE as a parameter.
9. Save and deploy the DataPage.

## Step 3: Configure API Access

1. Go to "API" in your Caspio application.
2. Click "New API Key".
3. Enter a name for the API key (e.g., "SanMar Inventory App").
4. Select the tables and DataPages you want to access via the API.
5. Click "Generate Key".
6. Copy the Client ID and Client Secret.

## Step 4: Configure Flask Application

1. Create a `.env` file in the root directory of your Flask application.
2. Add the following environment variables:

```
CASPIO_BASE_URL=https://your-caspio-account.caspio.com
CASPIO_CLIENT_ID=your-client-id
CASPIO_CLIENT_SECRET=your-client-secret
SANMAR_USERNAME=your-sanmar-username
SANMAR_PASSWORD=your-sanmar-password
```

3. Update the `app.py` file to register the Caspio routes:

```python
from app_caspio_routes import register_caspio_routes

# Register Caspio routes
register_caspio_routes(app)
```

## Step 5: Import Data from SanMar to Caspio

1. Run the `import_sanmar_to_caspio.py` script to import data from SanMar APIs to Caspio:

```bash
python import_sanmar_to_caspio.py
```

This script will:
- Fetch categories from SanMar API and import them to Caspio
- Fetch products by category from SanMar API and import them to Caspio
- Fetch inventory data for each product from SanMar API and import it to Caspio
- Fetch pricing data for each product from SanMar API and import it to Caspio

## Step 6: Test the Application

1. Start the Flask application:

```bash
python run.py
```

2. Open a web browser and navigate to `http://localhost:5000/caspio/`.
3. Test the following routes:
   - `/caspio/` - Home page with categories
   - `/caspio/category/<category_name>` - Category page with products
   - `/caspio/product/<style>` - Product page with details
   - `/caspio/api/inventory/<style>` - API endpoint for inventory data
   - `/caspio/api/pricing/<style>` - API endpoint for pricing data
   - `/caspio/api/search?q=<query>` - API endpoint for search

## Step 7: Set Up Scheduled Data Updates

To keep the Caspio database up to date with the latest data from SanMar, set up a scheduled task to run the `import_sanmar_to_caspio.py` script periodically.

### On Windows:

1. Open Task Scheduler.
2. Click "Create Basic Task".
3. Enter a name and description for the task.
4. Select "Daily" as the trigger.
5. Set the start time and recurrence.
6. Select "Start a program" as the action.
7. Browse to the Python executable and add the script path as an argument.
8. Click "Finish".

### On Linux:

1. Open a terminal.
2. Run `crontab -e` to edit the crontab file.
3. Add a line to run the script daily at a specific time (e.g., 2 AM):

```
0 2 * * * /usr/bin/python /path/to/import_sanmar_to_caspio.py
```

4. Save and exit the editor.

## Step 8: Monitor and Maintain

1. Regularly check the Caspio database for data integrity.
2. Monitor the logs of the `import_sanmar_to_caspio.py` script for any errors.
3. Update the script as needed to handle changes in the SanMar API.
4. Optimize the Caspio database and DataPages for performance.

## Troubleshooting

### Common Issues

1. **API Authentication Errors**:
   - Check that the Caspio API credentials are correct.
   - Ensure that the API key has access to the necessary tables and DataPages.

2. **Data Import Errors**:
   - Check the SanMar API credentials.
   - Verify that the SanMar API endpoints are accessible.
   - Check the logs for specific error messages.

3. **Flask Application Errors**:
   - Ensure that the Caspio routes are properly registered.
   - Check that the environment variables are correctly set.
   - Verify that the Caspio API is accessible from the Flask application.

### Getting Help

If you encounter issues that you cannot resolve, contact:
- Caspio Support: https://support.caspio.com
- SanMar API Support: [Contact information]
- Flask Application Support: [Contact information]