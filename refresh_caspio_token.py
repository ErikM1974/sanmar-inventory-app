#!/usr/bin/env python
"""
Script to refresh the Caspio API access token using the refresh token.
"""

import os
import json
import logging
import requests
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("caspio_token_refresh.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Caspio API credentials
CASPIO_BASE_URL = os.getenv('CASPIO_BASE_URL', 'https://c3eku948.caspio.com')
CASPIO_REFRESH_TOKEN = os.getenv('CASPIO_REFRESH_TOKEN')

def refresh_access_token(refresh_token):
    """Refresh the access token using the refresh token."""
    if not refresh_token:
        logger.error("No refresh token available. Please set CASPIO_REFRESH_TOKEN in your .env file.")
        return None
    
    auth_url = f"{CASPIO_BASE_URL}/oauth/token"
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    
    try:
        response = requests.post(auth_url, data=payload)
        response.raise_for_status()
        
        token_data = response.json()
        access_token = token_data.get('access_token')
        new_refresh_token = token_data.get('refresh_token')
        expires_in = token_data.get('expires_in', 3600)
        
        logger.info(f"Successfully refreshed access token. Expires in {expires_in} seconds.")
        
        return {
            'access_token': access_token,
            'refresh_token': new_refresh_token,
            'expires_in': expires_in
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Error refreshing access token: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return None

def update_env_file(token_data):
    """Update the .env file with the new token data."""
    if not token_data:
        return False
    
    try:
        # Read the current .env file
        env_lines = []
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                env_lines = f.readlines()
        
        # Update or add the token variables
        access_token_line = f"CASPIO_ACCESS_TOKEN={token_data['access_token']}\n"
        refresh_token_line = f"CASPIO_REFRESH_TOKEN={token_data['refresh_token']}\n"
        
        access_token_found = False
        refresh_token_found = False
        
        for i, line in enumerate(env_lines):
            if line.startswith('CASPIO_ACCESS_TOKEN='):
                env_lines[i] = access_token_line
                access_token_found = True
            elif line.startswith('CASPIO_REFRESH_TOKEN='):
                env_lines[i] = refresh_token_line
                refresh_token_found = True
        
        if not access_token_found:
            env_lines.append(access_token_line)
        if not refresh_token_found:
            env_lines.append(refresh_token_line)
        
        # Write the updated .env file
        with open('.env', 'w') as f:
            f.writelines(env_lines)
        
        logger.info("Updated .env file with new token data.")
        return True
    except Exception as e:
        logger.error(f"Error updating .env file: {str(e)}")
        return False

def main():
    """Main function to refresh the Caspio API access token."""
    logger.info("Starting Caspio token refresh...")
    
    # Check if refresh token is available
    if not CASPIO_REFRESH_TOKEN:
        logger.error("Refresh token is not set. Please set CASPIO_REFRESH_TOKEN in your .env file.")
        return
    
    # Refresh the access token
    token_data = refresh_access_token(CASPIO_REFRESH_TOKEN)
    if not token_data:
        logger.error("Failed to refresh access token.")
        return
    
    # Update the .env file
    if update_env_file(token_data):
        logger.info("Token refresh completed successfully.")
    else:
        logger.error("Failed to update .env file with new token data.")
    
    # Print the new token data
    print("\nNew token data:")
    print(f"Access Token: {token_data['access_token']}")
    print(f"Refresh Token: {token_data['refresh_token']}")
    print(f"Expires In: {token_data['expires_in']} seconds")

if __name__ == "__main__":
    main()