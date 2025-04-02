# SanMar to Caspio Integration

This project provides a complete solution for integrating SanMar product data with Caspio tables. It includes scripts for importing categories, products, pricing, and inventory data from SanMar APIs into Caspio tables.

## Table of Contents

- [Overview](#overview)
- [Table Structure](#table-structure)
- [Setup](#setup)
- [Usage](#usage)
- [Scheduled Tasks](#scheduled-tasks)
- [Authentication](#authentication)
- [Error Handling](#error-handling)
- [Troubleshooting](#troubleshooting)

## Overview

This integration solution consists of several components:

1. **Initial Import**: One-time script to populate Caspio tables with initial data from SanMar.
2. **Daily Inventory Update**: Script to update inventory data daily at 7 AM.
3. **Quarterly Product Update**: Script to update product and category data every 3 months.
4. **Authentication Utilities**: Scripts to manage Caspio API tokens.
5. **API Clients**: Modules for interacting with Caspio and SanMar APIs.

## Table Structure

### Categories Table
- **CATEGORY_ID** (AutoNumber) - Primary key
- **CATEGORY_NAME** (Text) - Name of the category
- **PARENT_CATEGORY_ID** (Number) - ID of the parent category (null for top-level categories)
- **DISPLAY_ORDER** (Number) - Order to display categories

### Products Table
- **PRODUCT_ID** (AutoNumber) - Primary key
- **STYLE** (Text) - SanMar style number
- **PRODUCT_TITLE** (Text) - Product title
- **CATEGORY_NAME** (Text) - Category name
- **COLOR_NAME** (Text) - Color name
- **SIZE** (Text) - Size name
- **SIZE_INDEX** (Number) - Order to display sizes
- **BRAND_NAME** (Text) - Brand name
- **BRAND_LOGO_IMAGE** (Text) - URL to brand logo image
- **PRODUCT_IMAGE_URL** (Text) - URL to product image
- **COLOR_SQUARE_IMAGE** (Text) - URL to color swatch image
- **PRICE** (Currency) - Regular price
- **PIECE_PRICE** (Currency) - Price per piece
- **CASE_PRICE** (Currency) - Price per case
- **CASE_SIZE** (Number) - Number of pieces in a case
- **KEYWORDS** (Text) - Keywords for search

### Inventory Table
- **INVENTORY_ID** (AutoNumber) - Primary key
- **STYLE** (Text) - SanMar style number
- **COLOR_NAME** (Text) - Color name
- **SIZE** (Text) - Size name
- **WAREHOUSE_ID** (Text) - Warehouse ID
- **QUANTITY** (Number) - Quantity available
- **LAST_UPDATED** (Date/Time) - Last update timestamp

## Setup

1. **Create Caspio Tables**:
   - Create the tables in Caspio with the structure described above.
   - Make sure to set the appropriate primary keys and indexes.

2. **Configure Environment Variables**:
   - Copy `.env.sample` to `.env`
   - Fill in your SanMar and Caspio API credentials:
     ```
     # SanMar API credentials
     SANMAR_USERNAME=your_sanmar_username
     SANMAR_PASSWORD=your_sanmar_password
     SANMAR_CUSTOMER_NUMBER=your_sanmar_customer_number

     # Caspio API credentials
     CASPIO_BASE_URL=https://c3eku948.caspio.com
     CASPIO_CLIENT_ID=your_caspio_client_id
     CASPIO_CLIENT_SECRET=your_caspio_client_secret

     # Caspio OAuth token (if using token-based authentication)
     CASPIO_ACCESS_TOKEN=your_caspio_access_token
     CASPIO_REFRESH_TOKEN=your_caspio_refresh_token
     ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Test Caspio Connection

Before running any import scripts, test your connection to the Caspio API:

```bash
python test_caspio_connection.py
```

### Initial Import

To perform the initial import of all data (categories, products, and inventory) from SanMar to Caspio:

```bash
python initial_import.py
```

This script will:
1. Import categories from SanMar to Caspio
2. Import products with pricing information from SanMar to Caspio
3. Import inventory data from SanMar to Caspio

### Daily Inventory Import

To manually run the daily inventory import:

```bash
python daily_inventory_import.py
```

This script will:
1. Get all product styles from the Caspio Products table
2. Get inventory data for those styles from SanMar
3. Update the Caspio Inventory table with the latest data

### Quarterly Product Update

To manually run the quarterly product update:

```bash
python quarterly_product_update.py
```

This script will:
1. Get categories from SanMar and update the Caspio Categories table
2. Get products for each category from SanMar, including pricing information
3. Update the Caspio Products table with the latest data

### Token Management

If you're using token-based authentication with Caspio, you can use these utilities:

#### Update Token

To update the access token in your .env file:

```bash
python update_caspio_token.py <access_token> [refresh_token]
```

#### Refresh Token

To refresh the access token using the refresh token:

```bash
python refresh_caspio_token.py
```

## Scheduled Tasks

### Windows

To set up scheduled tasks on Windows:

1. Run the setup script as an administrator:
   ```
   setup_scheduled_tasks_windows.bat
   ```

2. This will create two scheduled tasks:
   - **SanMar Daily Inventory Import**: Runs daily at 7 AM
   - **SanMar Quarterly Product Update**: Runs on the 1st day of January, April, July, and October at 1 AM

### Linux/Mac

To set up scheduled tasks on Linux or Mac:

1. Make the setup script executable:
   ```bash
   chmod +x setup_scheduled_tasks_linux.sh
   ```

2. Run the setup script:
   ```bash
   ./setup_scheduled_tasks_linux.sh
   ```

3. This will create two cron jobs:
   - Daily inventory import at 7 AM
   - Quarterly product update on the 1st day of January, April, July, and October at 1 AM

## Authentication

### SanMar API

The SanMar API uses basic authentication with a username, password, and customer number. These credentials should be set in the `.env` file.

### Caspio API

The Caspio API supports two authentication methods:

1. **OAuth 2.0 Client Credentials**: Set `CASPIO_CLIENT_ID` and `CASPIO_CLIENT_SECRET` in the `.env` file.
2. **OAuth 2.0 Access Token**: Set `CASPIO_ACCESS_TOKEN` and `CASPIO_REFRESH_TOKEN` in the `.env` file.

The scripts will automatically use the appropriate authentication method based on the credentials provided.

## Error Handling

The scripts include comprehensive error handling and logging. Logs are written to:
- `initial_import.log` for the initial import script
- `daily_inventory_import.log` for the daily inventory import script
- `quarterly_product_update.log` for the quarterly product update script
- `test_caspio_connection.log` for the connection test script
- `caspio_token_refresh.log` for the token refresh script
- `caspio_token_update.log` for the token update script

## Troubleshooting

If you encounter issues:

1. **Check the logs** for error messages
2. **Verify your API credentials** in the `.env` file
3. **Test your connection** to the Caspio API using `test_caspio_connection.py`
4. **Check your Caspio tables** to ensure they have the correct structure
5. **Refresh your Caspio token** if it has expired using `refresh_caspio_token.py`

For SanMar API issues, make sure your SanMar credentials are correct and that you have access to the required API endpoints.

For Caspio API issues, verify that your Caspio account has API access enabled and that you have the necessary permissions to access and modify the tables.