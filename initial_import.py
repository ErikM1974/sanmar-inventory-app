#!/usr/bin/env python
"""
Script to perform the initial import of all SanMar data into Caspio.
This is a one-time script to populate the Caspio tables with the initial data.
"""

import os
import sys
import logging
import time
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("initial_import.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to perform the initial import of all SanMar data into Caspio."""
    logger.info("Starting initial import of all SanMar data into Caspio...")
    
    # Import quarterly product and category data
    logger.info("Importing product and category data...")
    try:
        from quarterly_product_update import main as quarterly_update
        quarterly_update()
        logger.info("Product and category import completed successfully.")
    except Exception as e:
        logger.error(f"Error importing product and category data: {str(e)}")
        sys.exit(1)
    
    # Sleep briefly to allow the API to process the previous requests
    logger.info("Waiting for 5 seconds before proceeding to inventory import...")
    time.sleep(5)
    
    # Import daily inventory data
    logger.info("Importing inventory data...")
    try:
        from daily_inventory_import import main as daily_import
        daily_import()
        logger.info("Inventory import completed successfully.")
    except Exception as e:
        logger.error(f"Error importing inventory data: {str(e)}")
        sys.exit(1)
    
    logger.info("Initial import of all SanMar data into Caspio completed successfully.")
    logger.info("You can now set up scheduled tasks to run the following scripts:")
    logger.info("- daily_inventory_import.py: Run daily at 7 AM")
    logger.info("- quarterly_product_update.py: Run every 3 months")

if __name__ == "__main__":
    main()