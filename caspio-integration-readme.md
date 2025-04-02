# SanMar to Caspio Integration

This project provides scripts to import data from SanMar APIs into Caspio tables. It includes functionality to import categories, products, pricing, and inventory data.

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

1. Create the tables in Caspio with the structure described above.
2. Copy `.env.sample` to `.env` and fill in your SanMar and Caspio API credentials.
3. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Import All Data

To import all data (categories, products, and inventory) from SanMar to Caspio:

```bash
python import_sanmar_to_caspio.py
```

This script will:
1. Get categories from SanMar and import them to Caspio
2. Get products for each category from SanMar, including pricing information, and import them to Caspio
3. Get inventory information from SanMar and import it to Caspio

### Import Only Inventory Data

If you only want to import inventory data:

```bash
python import_sanmar_inventory_to_caspio.py
```

This script will:
1. Get inventory data from SanMar
2. Import it to the Caspio Inventory table

## Authentication

### SanMar API

The SanMar API uses basic authentication with a username, password, and customer number. These credentials should be set in the `.env` file.

### Caspio API

The Caspio API supports two authentication methods:

1. **OAuth 2.0 Client Credentials**: Set `CASPIO_CLIENT_ID` and `CASPIO_CLIENT_SECRET` in the `.env` file.
2. **OAuth 2.0 Access Token**: Set `CASPIO_ACCESS_TOKEN` and `CASPIO_REFRESH_TOKEN` in the `.env` file.

## Error Handling

The scripts include error handling and logging. Logs are written to:
- `sanmar_to_caspio_import.log` for the main import script
- `sanmar_inventory_import.log` for the inventory-only import script

## Scheduling

You can schedule these scripts to run periodically using cron (Linux/Mac) or Task Scheduler (Windows) to keep your Caspio data up to date with SanMar.

Example cron job to run the import every day at 2 AM:

```
0 2 * * * cd /path/to/project && python import_sanmar_to_caspio.py >> /path/to/logs/cron.log 2>&1
```

## Troubleshooting

If you encounter issues:

1. Check the log files for error messages
2. Verify your API credentials in the `.env` file
3. Ensure your Caspio tables have the correct structure
4. Check your network connection and firewall settings