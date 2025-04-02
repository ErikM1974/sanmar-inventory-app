# Caspio Implementation Guide for SanMar Inventory App

This guide outlines the steps to implement the SanMar Inventory App using Caspio as the backend database and datapage provider. By following this guide, you'll be able to set up a complete system that stores SanMar product data, inventory levels, and pricing information in Caspio, allowing you to build datapages that display this information to users without needing to make direct API calls to SanMar.

## Table Structure

The implementation uses the following tables in Caspio:

1. **ColorMapping** - Maps SanMar color codes to display-friendly color names
2. **Inventory** - Stores inventory levels for each product style, color, and size
3. **Pricing** - Stores pricing information for each product style, color, and size
4. **Products** - Stores product information (optional, can be added later)
5. **Categories** - Stores category information (optional, can be added later)

### Table Relationships

- Products and Inventory are related by STYLE
- Products and Pricing are related by STYLE
- Inventory and Pricing are related by STYLE, COLOR_NAME, and SIZE
- ColorMapping is related to Inventory and Pricing by COLOR_NAME

## Step 1: Create Tables in Caspio

### Create the ColorMapping Table

1. Log in to your Caspio account
2. Go to Tables > New Table
3. Create a table named "ColorMapping" with the following fields:
   - MAPPING_ID (Autonumber, Primary Key)
   - API_COLOR_NAME (Text, 100 characters)
   - DISPLAY_COLOR_NAME (Text, 100 characters)
   - LAST_UPDATED (Date/Time)
4. Add a unique index on API_COLOR_NAME to prevent duplicates

### Create the Inventory Table

1. Go to Tables > New Table
2. Create a table named "Inventory" with the following fields:
   - INVENTORY_ID (Autonumber, Primary Key)
   - STYLE (Text, 50 characters)
   - COLOR_NAME (Text, 100 characters)
   - DISPLAY_COLOR (Text, 100 characters)
   - SIZE (Text, 20 characters)
   - WAREHOUSE_ID (Text, 20 characters)
   - QUANTITY (Number)
   - LAST_UPDATED (Date/Time)
3. Add indexes for faster lookups:
   - Create an index on (STYLE, COLOR_NAME, SIZE)
   - Create an index on WAREHOUSE_ID
   - Create an index on DISPLAY_COLOR

### Create the Pricing Table

1. Go to Tables > New Table
2. Create a table named "Pricing" with the following fields:
   - PRICING_ID (Autonumber, Primary Key)
   - STYLE (Text, 50 characters)
   - COLOR_NAME (Text, 100 characters)
   - DISPLAY_COLOR (Text, 100 characters)
   - SIZE (Text, 20 characters)
   - PIECE_PRICE (Decimal, 10.2)
   - CASE_PRICE (Decimal, 10.2)
   - PROGRAM_PRICE (Decimal, 10.2)
   - LAST_UPDATED (Date/Time)
3. Add indexes for faster lookups:
   - Create an index on (STYLE, COLOR_NAME, SIZE)
   - Create an index on DISPLAY_COLOR

## Step 2: Set Up Data Import

The data import process is handled by the `daily_inventory_pricing_import.py` script, which:

1. Extracts color mappings from the SanMar API and stores them in the ColorMapping table
2. Gets inventory data from the SanMar API and stores it in the Inventory table
3. Gets pricing data from the SanMar API and stores it in the Pricing table

To set up the data import:

1. Ensure you have the necessary Python dependencies installed:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your SanMar and Caspio API credentials:
   ```
   SANMAR_USERNAME=your_sanmar_username
   SANMAR_PASSWORD=your_sanmar_password
   SANMAR_CUSTOMER_NUMBER=your_sanmar_customer_number
   
   CASPIO_BASE_URL=your_caspio_base_url
   CASPIO_CLIENT_ID=your_caspio_client_id
   CASPIO_CLIENT_SECRET=your_caspio_client_secret
   ```

3. Run the import script:
   ```
   python daily_inventory_pricing_import.py
   ```

4. Set up a scheduled task to run the script daily:
   - On Windows, use Task Scheduler and the provided `setup_scheduled_tasks_windows.bat` script
   - On Linux, use cron and the provided `setup_scheduled_tasks_linux.sh` script

## Step 3: Create Caspio DataPages

Now that you have the data in Caspio, you can create datapages to display the information to users.

### Product Listing DataPage

1. Go to DataPages > New DataPage
2. Choose "Search and Report" datapage type
3. Select the Inventory table as the data source
4. Configure the search form with the following fields:
   - STYLE
   - DISPLAY_COLOR
   - SIZE
5. Configure the results page to display:
   - STYLE
   - DISPLAY_COLOR
   - SIZE
   - QUANTITY (sum of all warehouses)
6. Add a link to the Product Detail DataPage, passing STYLE, COLOR_NAME, and SIZE as parameters

### Product Detail DataPage

1. Go to DataPages > New DataPage
2. Choose "Tabular Report" datapage type
3. Create a SQL query that joins the Inventory and Pricing tables:
   ```sql
   SELECT 
       i.STYLE, 
       i.DISPLAY_COLOR, 
       i.SIZE, 
       SUM(i.QUANTITY) AS TOTAL_QUANTITY, 
       p.PIECE_PRICE, 
       p.PROGRAM_PRICE
   FROM 
       Inventory i
   JOIN 
       Pricing p ON i.STYLE = p.STYLE AND i.COLOR_NAME = p.COLOR_NAME AND i.SIZE = p.SIZE
   WHERE 
       i.STYLE = '[STYLE]' AND 
       i.COLOR_NAME = '[COLOR_NAME]' AND 
       i.SIZE = '[SIZE]'
   GROUP BY 
       i.STYLE, i.DISPLAY_COLOR, i.SIZE, p.PIECE_PRICE, p.PROGRAM_PRICE
   ```
4. Configure the results page to display:
   - STYLE
   - DISPLAY_COLOR
   - SIZE
   - TOTAL_QUANTITY
   - PIECE_PRICE
   - PROGRAM_PRICE

### Inventory by Warehouse DataPage

1. Go to DataPages > New DataPage
2. Choose "Tabular Report" datapage type
3. Select the Inventory table as the data source
4. Configure parameters for STYLE, COLOR_NAME, and SIZE
5. Configure the results page to display:
   - WAREHOUSE_ID
   - QUANTITY
   - LAST_UPDATED

## Step 4: Embed DataPages in Your Application

1. Go to Deploy > DataPage Links
2. Get the embed code for each datapage
3. Add the embed code to your application's HTML templates

For example, to embed the Product Listing DataPage:

```html
<div id="product-listing">
    <!-- Caspio DataPage embed code goes here -->
    <script type="text/javascript" src="https://your-caspio-account.caspio.com/dp/12345/emb"></script>
</div>
```

## Step 5: Customize DataPage Appearance

1. Go to Styles > New Style
2. Create a custom style that matches your application's design
3. Apply the style to your datapages

## Conclusion

By following this guide, you've set up a complete system that stores SanMar product data in Caspio and displays it to users through datapages. This approach offers several benefits:

1. **Reduced API Calls**: Instead of making API calls to SanMar for every user request, you only need to update the data once per day.
2. **Improved Performance**: Caspio datapages load quickly and can be cached for even better performance.
3. **Simplified Development**: You don't need to write complex code to handle API responses and error conditions.
4. **Better User Experience**: Users see consistent data and don't have to wait for API calls to complete.

The system is designed to be maintainable and extensible. You can add more tables and datapages as needed to support additional features.