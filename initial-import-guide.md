# Initial Data Import Guide

This guide provides step-by-step instructions for performing the initial import of inventory and pricing data from the SanMar API into your Caspio tables.

## Prerequisites

1. Caspio tables are created:
   - Inventory table
   - Pricing table
   - Sanmar_Bulk_251816_Feb2024 table (already exists)

2. Environment is set up:
   - Python 3.7+ installed
   - Required Python packages installed
   - `.env` file with credentials

## Step 1: Install Required Packages

```bash
pip install requests zeep python-dotenv
```

## Step 2: Set Up Environment Variables

Create a `.env` file in the project directory with the following variables:

```
# SanMar API credentials
SANMAR_USERNAME=your_sanmar_username
SANMAR_PASSWORD=your_sanmar_password
SANMAR_CUSTOMER_NUMBER=your_sanmar_customer_number

# Caspio API credentials
CASPIO_BASE_URL=your_caspio_base_url
CASPIO_CLIENT_ID=your_caspio_client_id
CASPIO_CLIENT_SECRET=your_caspio_client_secret
# OR
CASPIO_ACCESS_TOKEN=your_caspio_access_token
CASPIO_REFRESH_TOKEN=your_caspio_refresh_token
```

## Step 3: Run the Initial Import

The `daily_inventory_pricing_import.py` script can be used for both the initial import and subsequent daily updates. To run the initial import:

```bash
python daily_inventory_pricing_import.py
```

This will:
1. Get product styles from the Sanmar_Bulk table
2. Fetch inventory data from SanMar API
3. Fetch pricing data from SanMar API
4. Import the data into the Inventory and Pricing tables

## Step 4: Verify the Import

After the import completes, verify that data was successfully imported:

1. Log in to your Caspio account
2. Go to the Inventory table and check that records were created
3. Go to the Pricing table and check that records were created

## Step 5: Set Up Scheduled Task

To keep the data up-to-date, set up a scheduled task to run the import script daily:

### On Windows:

1. Open Task Scheduler
2. Create a new task
3. Set the trigger to run daily at your preferred time (e.g., 7 AM)
4. Set the action to run the script:
   - Program/script: `python`
   - Arguments: `C:\path\to\daily_inventory_pricing_import.py`
   - Start in: `C:\path\to\project\directory`

### On Linux/Mac:

1. Open crontab:
   ```bash
   crontab -e
   ```

2. Add a line to run the script daily at 7 AM:
   ```
   0 7 * * * cd /path/to/project/directory && python daily_inventory_pricing_import.py >> /path/to/logfile.log 2>&1
   ```

## Troubleshooting

### Common Issues:

1. **API Authentication Errors**:
   - Verify your SanMar API credentials in the `.env` file
   - Check that your account has access to the required APIs

2. **Caspio Authentication Errors**:
   - Verify your Caspio API credentials in the `.env` file
   - If using token-based authentication, ensure the token is valid

3. **Import Failures**:
   - Check the log file for specific error messages
   - Verify that the Caspio tables have the correct structure

### Logging:

The script logs detailed information to `daily_inventory_pricing_import.log`. If you encounter issues, check this file for error messages and stack traces.

## Next Steps

After successfully importing the data:

1. Create indexes on the tables for better performance
2. Set up virtual relationships in Caspio DataPages
3. Integrate the Flask application code

## Monitoring

It's important to monitor the daily imports to ensure they're running successfully. Consider setting up email notifications for import failures or creating a simple dashboard to track import status.