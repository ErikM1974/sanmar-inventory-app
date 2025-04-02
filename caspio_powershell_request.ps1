# PowerShell script to create the Inventory table in Caspio using the REST API

# Replace with your actual access token
$ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"

# API endpoint
$API_ENDPOINT = "https://c3eku948.caspio.com/rest/v2/tables"

# Table definition JSON
$TABLE_DEFINITION = @"
{
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
}
"@

# Headers
$headers = @{
    "Authorization" = "Bearer $ACCESS_TOKEN"
    "Content-Type" = "application/json"
}

# Make the API request
try {
    $response = Invoke-RestMethod -Uri $API_ENDPOINT -Method Post -Headers $headers -Body $TABLE_DEFINITION -Verbose
    Write-Output "Response:"
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Error "Error making API request: $_"
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        $statusDescription = $_.Exception.Response.StatusDescription
        Write-Error "Status Code: $statusCode - $statusDescription"
        
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Error "Response Body: $responseBody"
    }
}