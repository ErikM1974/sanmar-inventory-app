#!/bin/bash
# Setup scheduled task for daily SanMar inventory and pricing import
# This script creates a cron job to run the import script at 7 AM every day

echo "Setting up cron job for daily SanMar inventory and pricing import..."

# Get the current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SCRIPT_PATH="$SCRIPT_DIR/daily_inventory_pricing_import.py"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Create a temporary file for the crontab
TEMP_CRON=$(mktemp)

# Export the current crontab
crontab -l > "$TEMP_CRON" 2>/dev/null

# Check if the cron job already exists
if grep -q "daily_inventory_pricing_import.py" "$TEMP_CRON"; then
    echo "Cron job already exists. Updating..."
    sed -i '/daily_inventory_pricing_import.py/d' "$TEMP_CRON"
fi

# Add the new cron job
echo "0 7 * * * cd $SCRIPT_DIR && python3 $SCRIPT_PATH >> $SCRIPT_DIR/daily_import.log 2>&1" >> "$TEMP_CRON"

# Import the updated crontab
crontab "$TEMP_CRON"

# Clean up
rm "$TEMP_CRON"

if [ $? -eq 0 ]; then
    echo "Cron job created successfully."
    echo "The import script will run at 7 AM every day."
    echo "Logs will be written to $SCRIPT_DIR/daily_import.log"
else
    echo "Failed to create cron job."
fi

echo ""
echo "You can view your crontab with 'crontab -l'."
echo ""