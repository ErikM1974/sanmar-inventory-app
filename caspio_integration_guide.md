# Caspio Integration Guide for SanMar Inventory App

This guide provides instructions for integrating the SanMar Inventory App with Caspio, a cloud-based database platform. By using Caspio, we can simplify the application architecture, improve performance, and reduce API calls to SanMar's services.

## Overview

The integration involves the following components:

1. **Caspio Database**: Stores product information, inventory levels, and pricing data
2. **Data Import Process**: Imports data from SanMar APIs to Caspio
3. **Flask Application**: Uses Caspio API instead of SanMar APIs for data retrieval

## Caspio Database Structure

The Caspio database consists of the following tables:

### 1. Products Table

This table stores product information such as style, title, category, color, size, etc.

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| STYLE | String | Product style number (e.g., PC61) |
| PRODUCT_TITLE | String | Product title/name |
| CATEGORY_NAME | String | Product category |
| COLOR_NAME | String | Product color |
| SIZE | String | Product size |
| SIZE_INDEX | Integer | Index for sorting sizes correctly |
| PRICE | Decimal | Product price |
| BRAND_NAME | String | Product brand |
| BRAND_LOGO_IMAGE | String | URL to brand logo image |
| PRODUCT_IMAGE_URL | String | URL to product image |
| COLOR_SQUARE_IMAGE | String | URL to color swatch image |
| KEYWORDS | String | Keywords for search |
| PIECE_PRICE | Decimal | Price per piece |
| CASE_PRICE | Decimal | Price per case |
| CASE_SIZE | Integer | Number of pieces in a case |

### 2. Inventory Table

This table stores inventory levels for each product by warehouse.

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| INVENTORY_ID | AutoNumber | Unique identifier for inventory record |
| STYLE | String | Product style number |
| COLOR_NAME | String | Product color |
| SIZE | String | Product size |
| WAREHOUSE_ID | String | Warehouse identifier |
| QUANTITY | Integer | Quantity available |
| LAST_UPDATED | DateTime | Timestamp of last update |

### 3. Categories Table

This table stores the category hierarchy.

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| CATEGORY_ID | AutoNumber | Unique identifier for category |
| CATEGORY_NAME | String | Category name |
| PARENT_CATEGORY_ID | Integer | Parent category ID (for subcategories) |
| DISPLAY_ORDER | Integer | Order for display |

## Setup Instructions

### 1. Set Up Caspio Account

1. Sign up for a Caspio account at [https://www.caspio.com/](https://www.caspio.com/)
2. Create a new application in Caspio
3. Obtain API credentials (Client ID and Client Secret)

### 2. Configure Environment Variables

Add the following environment variables to your `.env` file:

```
CASPIO_BASE_URL=https://your-caspio-instance.caspio.com/
CASPIO_CLIENT_ID=your_client_id
CASPIO_CLIENT_SECRET=your_client_secret
CASPIO_TABLE_NAME=Products
```

### 3. Create Caspio Tables

Run the `setup_caspio_tables.py` script to create the necessary tables in Caspio:

```bash
python setup_caspio_tables.py
```

This script will:
- Check if the tables already exist
- Create the tables if they don't exist
- Add the necessary fields to each table

### 4. Import Data from SanMar to Caspio

Run the `import_sanmar_to_caspio.py` script to import data from SanMar APIs to Caspio:

```bash
python import_sanmar_to_caspio.py
```

This script will:
- Get categories from SanMar API
- Get products for each category
- Get inventory levels for each product
- Transform the data to Caspio format
- Insert or update records in Caspio tables

### 5. Update Flask Application to Use Caspio

Run the `app_caspio_integration.py` script to update the Flask application to use Caspio:

```bash
python app_caspio_integration.py
```

This script will:
- Register Caspio routes with the Flask app
- Start the Flask app with Caspio integration

## Caspio DataPages

To create DataPages in Caspio for the SanMar Inventory App, follow these steps:

### 1. Product Catalog DataPage

1. Log in to your Caspio account
2. Go to DataPages > Create New DataPage
3. Select "Table Report" as the DataPage type
4. Select the "Products" table as the data source
5. Configure the following fields to display:
   - STYLE
   - PRODUCT_TITLE
   - CATEGORY_NAME
   - BRAND_NAME
   - PRODUCT_IMAGE_URL
6. Add a search form with the following search fields:
   - STYLE
   - PRODUCT_TITLE
   - CATEGORY_NAME
   - BRAND_NAME
   - KEYWORDS
7. Configure sorting by STYLE, CATEGORY_NAME, and BRAND_NAME
8. Configure pagination with 20 records per page
9. Deploy the DataPage

### 2. Product Detail DataPage

1. Go to DataPages > Create New DataPage
2. Select "Details Page" as the DataPage type
3. Select the "Products" table as the data source
4. Configure the following fields to display:
   - STYLE
   - PRODUCT_TITLE
   - CATEGORY_NAME
   - BRAND_NAME
   - PRODUCT_IMAGE_URL
   - COLOR_NAME
   - SIZE
   - PRICE
   - PIECE_PRICE
   - CASE_PRICE
   - CASE_SIZE
5. Configure the parameter to be STYLE
6. Deploy the DataPage

### 3. Inventory DataPage

1. Go to DataPages > Create New DataPage
2. Select "Table Report" as the DataPage type
3. Select the "Inventory" table as the data source
4. Configure the following fields to display:
   - STYLE
   - COLOR_NAME
   - SIZE
   - WAREHOUSE_ID
   - QUANTITY
   - LAST_UPDATED
5. Add a search form with the following search fields:
   - STYLE
   - COLOR_NAME
   - SIZE
   - WAREHOUSE_ID
6. Configure sorting by STYLE, COLOR_NAME, SIZE, and WAREHOUSE_ID
7. Configure pagination with 20 records per page
8. Deploy the DataPage

## Deployment

To deploy the SanMar Inventory App with Caspio integration, follow these steps:

1. Ensure all environment variables are properly set
2. Run the Flask application with Caspio integration:

```bash
python app_caspio_integration.py
```

3. Access the application at http://localhost:5000

## Maintenance

### Updating Data

To update the data in Caspio, run the `import_sanmar_to_caspio.py` script periodically. You can set up a cron job or scheduled task to run this script at regular intervals (e.g., daily or hourly).

### Monitoring

Monitor the application logs for any errors or issues with the Caspio integration. The logs are stored in the following files:
- `caspio_setup.log`: Logs from the table setup process
- `caspio_import.log`: Logs from the data import process
- `caspio_integration.log`: Logs from the Flask application with Caspio integration

## Troubleshooting

### Authentication Issues

If you encounter authentication issues with the Caspio API, check the following:
- Ensure the CASPIO_CLIENT_ID and CASPIO_CLIENT_SECRET environment variables are correctly set
- Verify that the API credentials are valid and have the necessary permissions
- Check if the access token has expired and needs to be refreshed

### Data Import Issues

If you encounter issues with the data import process, check the following:
- Ensure the SanMar API credentials are correctly set
- Verify that the SanMar APIs are accessible
- Check the `caspio_import.log` file for specific error messages

### Application Issues

If you encounter issues with the Flask application, check the following:
- Ensure all required environment variables are correctly set
- Verify that the Caspio tables exist and have the correct structure
- Check the `caspio_integration.log` file for specific error messages

## Conclusion

By integrating the SanMar Inventory App with Caspio, we have simplified the application architecture, improved performance, and reduced API calls to SanMar's services. The Caspio database provides a reliable and scalable solution for storing and retrieving product information, inventory levels, and pricing data.