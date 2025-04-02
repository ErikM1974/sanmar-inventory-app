# Inventory and Pricing Data Management Analysis

## Current Situation

Based on our discussion, we have:

1. **Sanmar_Bulk_251816_Feb2024 table**: Contains product data including:
   - Product information (style, color, size, etc.)
   - Basic pricing (piece price, case price)
   - BUT does not have up-to-date pricing or program pricing

2. **Inventory table**: Contains:
   - INVENTORY_ID (Primary Key)
   - STYLE
   - COLOR_NAME
   - SIZE
   - WAREHOUSE_ID
   - QUANTITY
   - LAST_UPDATED
   - Case_Price
   - Program_Price

3. **Requirements**:
   - Update inventory numbers every 24 hours
   - Need to include case price and program price
   - Need up-to-date pricing information

## Analysis: Is the Inventory Table the Best Place for Pricing?

### Pros of Keeping Pricing in the Inventory Table

1. **Simplicity**: One table to query for both inventory and pricing data
2. **Update Frequency Alignment**: If both inventory and pricing need to be updated at the same frequency (daily), it's convenient to update them together
3. **Warehouse-Specific Pricing**: If pricing varies by warehouse, it makes sense to have pricing tied to inventory records

### Cons of Keeping Pricing in the Inventory Table

1. **Data Duplication**: If the same product (style/color/size) is stocked in multiple warehouses, pricing information would be duplicated across multiple records
2. **Update Complexity**: If pricing changes but inventory doesn't (or vice versa), you'd need to update only some fields in many records
3. **Data Integrity Risks**: More chances for inconsistencies if the same product has different prices in different warehouse records
4. **Query Performance**: Joining inventory and pricing data at query time might be more efficient than storing them together

## Recommendation: Separate Pricing Table

Based on the analysis, I recommend creating a separate **Pricing** table with the following structure:

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| PRICING_ID | AutoNumber | Primary key |
| STYLE | Text (255) | SanMar style number |
| COLOR_NAME | Text (255) | Color name |
| SIZE | Text (255) | Size name |
| PIECE_PRICE | Currency | Regular price per piece |
| CASE_PRICE | Currency | Price per case |
| CASE_SIZE | Number | Number of pieces in a case |
| PROGRAM_PRICE | Currency | Special program pricing |
| LAST_UPDATED | DateTime | Last update timestamp |

### Benefits of This Approach

1. **No Data Duplication**: Pricing is stored once per product variation (style/color/size)
2. **Simplified Updates**: Pricing updates are separate from inventory updates
3. **Data Integrity**: Consistent pricing across all warehouses
4. **Flexible Update Schedules**: Can update pricing on a different schedule than inventory if needed
5. **Clear Separation of Concerns**: Each table has a single responsibility

## Implementation Plan

### 1. Create the Pricing Table

Create a new table in Caspio with the structure outlined above.

### 2. Modify the Daily Inventory Import Script

Update the daily import script to:

1. Fetch inventory data from SanMar API
2. Update the Inventory table with quantities and warehouse information
3. Fetch pricing data from SanMar API
4. Update the Pricing table with the latest pricing information

### 3. Update Application Code

Modify the application code to:

1. Query the Sanmar_Bulk table for product information
2. Query the Inventory table for inventory levels
3. Query the Pricing table for up-to-date pricing

### 4. Example Code for Daily Import

Here's a simplified example of how the daily import script could be structured:

```python
def main():
    # Fetch inventory data from SanMar API
    inventory_data = get_sanmar_inventory()
    
    # Update Inventory table (without pricing information)
    update_inventory_table(inventory_data)
    
    # Fetch pricing data from SanMar API
    pricing_data = get_sanmar_pricing()
    
    # Update Pricing table
    update_pricing_table(pricing_data)
    
    logger.info("Daily import completed successfully.")
```

### 5. Example Code for Querying Data

```python
def get_product_details(style, color, size):
    # Get product information from Sanmar_Bulk table
    product_info = query_sanmar_bulk(style, color, size)
    
    # Get inventory levels from Inventory table
    inventory_levels = query_inventory(style, color, size)
    
    # Get pricing from Pricing table
    pricing = query_pricing(style, color, size)
    
    # Combine the data
    product_details = {
        **product_info,
        "inventory": inventory_levels,
        "pricing": pricing
    }
    
    return product_details
```

## Conclusion

While it's possible to keep pricing information in the Inventory table, a separate Pricing table offers better data organization, reduces duplication, and simplifies updates. This approach aligns with database normalization principles and will make your application more maintainable in the long run.

If you decide to keep pricing in the Inventory table, I recommend removing the pricing fields from individual warehouse records and instead creating a separate record with a special "ALL" warehouse ID that contains the pricing information for each product variation.