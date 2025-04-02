# Caspio Integration Plan for Northwest Custom Apparel

## Overview

This document outlines the plan for integrating Caspio with the Northwest Custom Apparel inventory application to simplify data management and reduce API calls to SanMar.

## Current Status

We've updated the `caspio_client.py` file with the appropriate field names and table structure based on the Caspio API. However, initial testing shows connectivity issues with the Caspio API. Authentication is working (token refresh successful), but API requests are failing.

## Required Caspio Components

### 1. Caspio DataPage Structure

#### Tables Required

1. **SanMar_Product_Catalog** - Main product data table
   - Fields:
     - `STYLE` (Text, Primary Key) - SanMar style number
     - `PRODUCT_TITLE` (Text) - Product name/description
     - `BRAND_NAME` (Text) - Brand name (Port & Company, Sport-Tek, etc.)
     - `BRAND_LOGO_IMAGE` (Text/URL) - URL to brand logo image
     - `CATEGORY_NAME` (Text) - Product category (T-Shirts, Polos, etc.)
     - `SUBCATEGORY_NAME` (Text) - Product subcategory
     - `COLOR_NAME` (Text) - Color name
     - `COLOR_SQUARE_IMAGE` (Text/URL) - URL to color swatch image
     - `SIZE` (Text) - Size name (S, M, L, etc.)
     - `SIZE_INDEX` (Number) - Numeric value for sorting sizes correctly
     - `QTY` (Number) - Available quantity
     - `PIECE_PRICE` (Currency) - Price per piece
     - `CASE_PRICE` (Currency) - Price per case
     - `CASE_SIZE` (Number) - Number of items in a case
     - `PRODUCT_IMAGE` (Text/URL) - URL to product image
     - `KEYWORDS` (Text) - Search keywords
     - `LAST_UPDATED` (DateTime) - Last update timestamp

2. **SanMar_Inventory_Log** - Inventory change tracking
   - Fields:
     - `LOG_ID` (AutoNumber, Primary Key)
     - `STYLE` (Text) - SanMar style number
     - `COLOR_NAME` (Text) - Color name
     - `SIZE` (Text) - Size name
     - `QTY_BEFORE` (Number) - Quantity before update
     - `QTY_AFTER` (Number) - Quantity after update
     - `CHANGE_DATE` (DateTime) - Date/time of change
     - `CHANGE_SOURCE` (Text) - Source of change (API, manual, etc.)

### 2. DataPages Required

1. **Product Catalog Browse** - For browsing all products
   - Filterable by category, subcategory, brand
   - Sortable by style, product title
   - Pagination support

2. **Product Detail** - For viewing detailed product information
   - Shows all product details, colors, sizes, inventory
   - Links to edit product information

3. **Product Search** - For searching products
   - Search by style, product title, keywords
   - Advanced filtering options

4. **Inventory Management** - For updating inventory levels
   - Batch update capabilities
   - Inventory history viewing

5. **Data Import** - For importing data from SanMar API
   - Scheduled import capabilities
   - Error logging and reporting

## Implementation Steps

1. **Create Caspio Database Tables**
   - Create the tables described above in Caspio
   - Set up appropriate indexes for performance
   - Configure data validation rules

2. **Create DataPages**
   - Design and create each of the required DataPages
   - Configure security and access controls
   - Set up appropriate styling to match Northwest Custom Apparel branding

3. **Fix API Connection Issues**
   - Troubleshoot current connection issues with Caspio API
   - Verify correct API endpoint URLs
   - Confirm authentication parameters
   - Test with Caspio's API testing tools

4. **Develop Data Synchronization Process**
   - Create scripts to sync data from SanMar to Caspio
   - Implement incremental updates to minimize data transfer
   - Set up error handling and retry logic

5. **Integrate with Existing Application**
   - Update application to use Caspio data instead of direct SanMar API calls
   - Implement fallback to SanMar API when Caspio data is unavailable
   - Add caching layer for improved performance

6. **Testing**
   - Test all DataPages for functionality
   - Verify data accuracy compared to SanMar API
   - Performance testing under load
   - Error handling testing

7. **Deployment**
   - Deploy Caspio DataPages to production
   - Update application configuration to use production Caspio endpoints
   - Monitor initial usage and performance

## API Connection Troubleshooting

Current issues with the Caspio API connection need to be resolved:

1. Verify Caspio account credentials and permissions
2. Confirm the correct table name (`Sanmar_Bulk_251816_Feb2024`)
3. Check network connectivity from application server to Caspio
4. Review Caspio API documentation for any required headers or parameters
5. Test API calls using Postman or similar tool to isolate issues
6. Check Caspio API logs for error messages

## Benefits of Caspio Integration

1. **Reduced API Calls to SanMar**
   - Caspio will serve as a cache for SanMar data
   - Only need to update data periodically from SanMar

2. **Improved Performance**
   - Faster response times for product data
   - Reduced load on application servers

3. **Enhanced Data Management**
   - Easy-to-use interface for data updates
   - Better tracking of inventory changes

4. **Simplified Application Logic**
   - Less complex error handling for API calls
   - More consistent data structure

## Timeline

1. **Week 1**: Set up Caspio tables and resolve API connection issues
2. **Week 2**: Create and configure DataPages
3. **Week 3**: Develop data synchronization process
4. **Week 4**: Integrate with existing application and testing
5. **Week 5**: Deployment and monitoring

## Conclusion

Integrating Caspio with the Northwest Custom Apparel inventory application will significantly improve performance and reliability while reducing dependency on the SanMar API. The plan outlined above provides a structured approach to implementing this integration.