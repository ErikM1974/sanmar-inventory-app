# Caspio Table Creation Steps

## Inventory Table

1. Log in to Caspio Bridge
2. Go to the "Data" section
3. Click on "Tables"
4. Click on "New Table"
5. Enter "Inventory" as the table name
6. Add the following fields:

### Fields

1. **INVENTORY_ID**
   - Data Type: AutoNumber
   - Label: Inventory ID
   - Make this field unique

2. **STYLE**
   - Data Type: Text (255)
   - Label: Style
   - Length: 50
   - Required: Yes

3. **COLOR_NAME**
   - Data Type: Text (255)
   - Label: Color Name
   - Length: 100
   - Required: Yes

4. **SIZE**
   - Data Type: Text (255)
   - Label: Size
   - Length: 20
   - Required: Yes

5. **WAREHOUSE_ID**
   - Data Type: Text (255)
   - Label: Warehouse ID
   - Length: 20
   - Required: Yes

6. **QUANTITY**
   - Data Type: Number
   - Label: Quantity
   - Required: Yes

7. **LAST_UPDATED**
   - Data Type: Date/Time
   - Label: Last Updated
   - Required: Yes

7. Click "Save" to create the table

## Create Index on Inventory Table

1. Go to the "Data" section
2. Click on "Tables"
3. Click on the "Inventory" table
4. Go to the "Indexes" tab
5. Click "New Index"
6. Enter "IDX_INVENTORY_STYLE_COLOR_SIZE_WAREHOUSE" as the index name
7. Select the following fields: STYLE, COLOR_NAME, SIZE, WAREHOUSE_ID
8. Check the "Unique" checkbox
9. Click "Save" to create the index

## Create DataPage for Inventory Management

1. Go to the "DataPages" section
2. Click "New DataPage"
3. Select "Submission Form"
4. Select the "Inventory" table
5. Configure the form fields
6. Click "Deploy" to deploy the DataPage