#!/usr/bin/env python
"""
Script to integrate Caspio API with the Flask application.
This script modifies app.py to use Caspio routes instead of SanMar routes.
"""

import logging
import os
import sys
from caspio_client import caspio_api
from app_caspio_routes import register_caspio_routes

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("caspio_integration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to integrate Caspio API with the Flask application"""
    logger.info("Starting Caspio integration...")
    
    # Check if Caspio API is properly configured
    if not caspio_api.client_id or not caspio_api.client_secret:
        logger.error("Caspio API is not properly configured. Please check your .env file.")
        sys.exit(1)
    
    # Test Caspio API connection
    logger.info("Testing Caspio API connection...")
    test_response = caspio_api._get_access_token()
    if not test_response:
        logger.error("Failed to connect to Caspio API. Please check your credentials.")
        sys.exit(1)
    
    logger.info("Successfully connected to Caspio API.")
    
    # Import Flask app
    try:
        from app import app
    except ImportError:
        logger.error("Failed to import Flask app. Please make sure app.py exists.")
        sys.exit(1)
    
    # Register Caspio routes with the Flask app
    logger.info("Registering Caspio routes with the Flask app...")
    register_caspio_routes(app)
    
    logger.info("Successfully registered Caspio routes with the Flask app.")
    logger.info("Caspio integration completed successfully.")
    
    # Run the Flask app
    logger.info("Running the Flask app...")
    app.run(host='0.0.0.0', debug=True)

if __name__ == "__main__":
    main()