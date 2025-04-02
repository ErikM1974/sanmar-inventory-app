#!/usr/bin/env python
"""
Script to update the Caspio API access token in the .env file.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("caspio_token_update.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def update_env_file(access_token, refresh_token=None):
    """Update the .env file with the new token data."""
    if not access_token:
        logger.error("No access token provided.")
        return False
    
    try:
        # Read the current .env file
        env_lines = []
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                env_lines = f.readlines()
        
        # Update or add the token variables
        access_token_line = f"CASPIO_ACCESS_TOKEN={access_token}\n"
        
        access_token_found = False
        refresh_token_found = False
        
        for i, line in enumerate(env_lines):
            if line.startswith('CASPIO_ACCESS_TOKEN='):
                env_lines[i] = access_token_line
                access_token_found = True
            elif refresh_token and line.startswith('CASPIO_REFRESH_TOKEN='):
                env_lines[i] = f"CASPIO_REFRESH_TOKEN={refresh_token}\n"
                refresh_token_found = True
        
        if not access_token_found:
            env_lines.append(access_token_line)
        if refresh_token and not refresh_token_found:
            env_lines.append(f"CASPIO_REFRESH_TOKEN={refresh_token}\n")
        
        # Write the updated .env file
        with open('.env', 'w') as f:
            f.writelines(env_lines)
        
        logger.info("Updated .env file with new token data.")
        return True
    except Exception as e:
        logger.error(f"Error updating .env file: {str(e)}")
        return False

def main():
    """Main function to update the Caspio API access token."""
    logger.info("Starting Caspio token update...")
    
    # Check if access token is provided as command line argument
    if len(sys.argv) < 2:
        logger.error("No access token provided. Usage: python update_caspio_token.py <access_token> [refresh_token]")
        return
    
    access_token = sys.argv[1]
    refresh_token = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Update the .env file
    if update_env_file(access_token, refresh_token):
        logger.info("Token update completed successfully.")
        print("\nToken update completed successfully.")
        print(f"Access Token: {access_token}")
        if refresh_token:
            print(f"Refresh Token: {refresh_token}")
    else:
        logger.error("Failed to update .env file with new token data.")
        print("\nFailed to update .env file with new token data.")

if __name__ == "__main__":
    main()