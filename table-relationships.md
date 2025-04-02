# Table Relationships in Caspio

## Current Tables

Based on the screenshots provided, we have three tables in Caspio:

1. **Sanmar_Bulk_251816_Feb2024**: Contains product data
2. **Inventory**: Contains inventory data
3. **Pricing**: Contains pricing data

## Relationship Structure

These tables are related through common fields:

```
Sanmar_Bulk_251816_Feb2024 ──┐
  (STYLE, COLOR_NAME, SIZE)   │
                             │
                             ├── Common fields create
                             │    virtual relationships
                             │
Inventory ────────────────────┘
  (STYLE, COLOR_NAME, SIZE)   │
                             │
                             ├── Common fields create
                             │    virtual relationships
                             │
Pricing ─────────────────────┘
  (STYLE, COLOR_NAME, SIZE)
```

## Setting Up Virtual Relationships in Caspio

Caspio uses "virtual relationships" rather than traditional foreign key constraints. Here's how to set them up:

### 1. Create a Relationship in DataPages

When creating a DataPage that uses multiple tables:

1. Go to the DataPage wizard
2. In the "Data Source" step, click "Add Table"
3. Select the second table (e.g., Inventory or Pricing)
4. Define the relationship by matching fields:
   - STYLE in Sanmar_Bulk_251816_Feb2024 = STYLE in Inventory/Pricing
   - COLOR_NAME in Sanmar_Bulk_251816_Feb2024 = COLOR_NAME in Inventory/Pricing
   - SIZE in Sanmar_Bulk_251816_Feb2024 = SIZE in Inventory/Pricing

### 2. Create a View (Alternative Approach)

You can also create a View in Caspio that joins these tables:

1. Go to Tables > Views
2. Click "Create View"
3. Add all three tables
4. Define the JOIN conditions:
   - Sanmar_Bulk_251816_Feb2024.STYLE = Inventory.STYLE AND
   - Sanmar_Bulk_251816_Feb2024.COLOR_NAME = Inventory.COLOR_NAME AND
   - Sanmar_Bulk_251816_Feb2024.SIZE = Inventory.SIZE
   
   - Sanmar_Bulk_251816_Feb2024.STYLE = Pricing.STYLE AND
   - Sanmar_Bulk_251816_Feb2024.COLOR_NAME = Pricing.COLOR_NAME AND
   - Sanmar_Bulk_251816_Feb2024.SIZE = Pricing.SIZE

5. Select the fields you want to include in the view

## Benefits of This Approach

1. **Flexibility**: You can query each table independently when needed
2. **Performance**: Each table can be optimized for its specific purpose
3. **Data Integrity**: Updates to one table don't affect the others
4. **Simplified Updates**: Each table can be updated on its own schedule

## Recommended Indexes

To optimize query performance when joining these tables, create the following indexes:

### Sanmar_Bulk_251816_Feb2024
- Create a composite index on (STYLE, COLOR_NAME, SIZE)

### Inventory
- Create a composite index on (STYLE, COLOR_NAME, SIZE)
- Create an index on WAREHOUSE_ID

### Pricing
- Create a composite index on (STYLE, COLOR_NAME, SIZE)

## Example Query Using These Relationships

When you need to combine data from all three tables, you would use a query like this:

```sql
SELECT 
    b.PRODUCT_TITLE,
    b.CATEGORY_NAME,
    b.SUBCATEGORY_NAME,
    b.FRONT_MODEL,
    i.WAREHOUSE_ID,
    i.QUANTITY,
    p.PIECE_PRICE,
    p.CASE_PRICE,
    p.PROGRAM_PRICE
FROM 
    Sanmar_Bulk_251816_Feb2024 b
JOIN 
    Inventory i ON b.STYLE = i.STYLE AND b.COLOR_NAME = i.COLOR_NAME AND b.SIZE = i.SIZE
JOIN 
    Pricing p ON b.STYLE = p.STYLE AND b.COLOR_NAME = p.COLOR_NAME AND b.SIZE = p.SIZE
WHERE 
    b.STYLE = 'PC61'
```

In Caspio's DataPage builder, this type of join is handled automatically when you define the relationships between tables.