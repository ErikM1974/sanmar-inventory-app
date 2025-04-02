#!/bin/bash
# Script to create the Inventory table in Caspio using the REST API

# Replace with your actual access token
ACCESS_TOKEN="YOUR_ACCESS_TOKEN"

# API endpoint
API_ENDPOINT="https://c3eku948.caspio.com/rest/v2/tables"

# Table definition JSON
TABLE_DEFINITION='{
  "Name": "Inventory",
  "Columns": [
    {
      "Name": "INVENTORY_ID",
      "Type": "AutoNumber",
      "Unique": true,
      "Label": "Inventory ID",
      "Description": "Primary key for inventory record"
    },
    {
      "Name": "STYLE",
      "Type": "Text",
      "Length": 50,
      "Label": "Style",
      "Description": "SanMar style number",
      "Required": true
    },
    {
      "Name": "COLOR_NAME",
      "Type": "Text",
      "Length": 100,
      "Label": "Color Name",
      "Description": "Color name",
      "Required": true
    },
    {
      "Name": "SIZE",
      "Type": "Text",
      "Length": 20,
      "Label": "Size",
      "Description": "Size name",
      "Required": true
    },
    {
      "Name": "WAREHOUSE_ID",
      "Type": "Text",
      "Length": 20,
      "Label": "Warehouse ID",
      "Description": "Warehouse ID",
      "Required": true
    },
    {
      "Name": "QUANTITY",
      "Type": "Number",
      "Label": "Quantity",
      "Description": "Quantity available",
      "Required": true
    },
    {
      "Name": "LAST_UPDATED",
      "Type": "DateTime",
      "Label": "Last Updated",
      "Description": "Last update timestamp",
      "Required": true
    }
  ]
}'

# Make the API request
curl -X POST "$API_ENDPOINT" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$TABLE_DEFINITION" \
  -v