#!/usr/bin/env python
"""
Script to download SanMar inventory file from FTP, convert to CSV, and upload to Box.com.
This script is designed to run daily on Heroku to automate the inventory data import process.
"""

import os
import sys
import csv
import ftplib
import logging
import tempfile
import requests
from datetime import datetime
from dotenv import load_dotenv
from boxsdk import Client, OAuth2
import base64

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sanmar_ftp_to_box.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# SanMar FTP credentials
SANMAR_FTP_HOST = os.getenv('SANMAR_FTP_HOST', 'ftp.sanmar.com')
SANMAR_FTP_USER = os.getenv('SANMAR_FTP_USER', '6920')
SANMAR_FTP_PASSWORD = os.getenv('SANMAR_FTP_PASSWORD', 'Sanmar20')
SANMAR_FTP_DIR = os.getenv('SANMAR_FTP_DIR', '/SanMarPDD/')
SANMAR_FTP_FILENAME = os.getenv('SANMAR_FTP_FILENAME', 'sanmar_dip.txt')

# Box.com credentials
BOX_CLIENT_ID = os.getenv('BOX_CLIENT_ID', 'bapez65e9mnc3yg0yop17wy646pq57rs')
BOX_CLIENT_SECRET = os.getenv('BOX_CLIENT_SECRET', 'wAZDgCAmVKOJH7PRbw1h74mDEs30uUZN')
BOX_FOLDER_ID = os.getenv('BOX_FOLDER_ID', '0')  # Use '0' for the root folder
BOX_ENTERPRISE_ID = os.getenv('BOX_ENTERPRISE_ID', '73197563')

def download_from_ftp(local_path):
    """Download the inventory file from SanMar FTP server."""
    try:
        logger.info(f"Connecting to SanMar FTP server: {SANMAR_FTP_HOST}")
        ftp = ftplib.FTP(SANMAR_FTP_HOST)
        ftp.login(SANMAR_FTP_USER, SANMAR_FTP_PASSWORD)
        
        # Navigate to the directory
        if SANMAR_FTP_DIR != '/':
            ftp.cwd(SANMAR_FTP_DIR)
        
        logger.info(f"Downloading file: {SANMAR_FTP_FILENAME}")
        with open(local_path, 'wb') as f:
            ftp.retrbinary(f'RETR {SANMAR_FTP_FILENAME}', f.write)
        
        ftp.quit()
        logger.info(f"Download completed successfully to: {local_path}")
        return True
    except Exception as e:
        logger.error(f"Error downloading from FTP: {str(e)}")
        return False

def convert_to_csv(input_path, output_path):
    """Convert the pipe-delimited file to CSV format."""
    try:
        logger.info(f"Converting {input_path} to CSV format")
        
        # Read the pipe-delimited file
        with open(input_path, 'r', encoding='utf-8') as input_file:
            # Read the header line to get column names
            header_line = input_file.readline().strip()
            # Remove quotes and split by pipe
            headers = [h.strip('"') for h in header_line.split('|')]
            
            # Create CSV file
            with open(output_path, 'w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)
                # Write headers
                writer.writerow(headers)
                
                # Process each line
                for line in input_file:
                    # Remove quotes and split by pipe
                    values = [v.strip('"') for v in line.strip().split('|')]
                    writer.writerow(values)
        
        logger.info(f"Conversion completed successfully to: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error converting file: {str(e)}")
        return False

def upload_to_box(file_path, file_name):
    """Upload the CSV file to Box.com."""
    try:
        logger.info(f"Authenticating with Box.com using Client Credentials Grant")
        
        # Get access token using Client Credentials Grant
        auth_url = "https://api.box.com/oauth2/token"
        
        data = {
            'grant_type': 'client_credentials',
            'client_id': BOX_CLIENT_ID,
            'client_secret': BOX_CLIENT_SECRET,
            'box_subject_type': 'enterprise',
            'box_subject_id': BOX_ENTERPRISE_ID
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        logger.info("Requesting access token from Box.com")
        response = requests.post(auth_url, data=data, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get access token: {response.text}")
        
        access_token = response.json().get('access_token')
        logger.info("Successfully obtained access token")
        
        # Create Box client with the access token
        auth = OAuth2(
            client_id=BOX_CLIENT_ID,
            client_secret=BOX_CLIENT_SECRET,
            access_token=access_token
        )
        client = Client(auth)
        
        # Get the folder
        folder = client.folder(folder_id=BOX_FOLDER_ID).get()
        logger.info(f"Uploading to Box folder: {folder.name}")
        
        # Upload the file
        with open(file_path, 'rb') as file_content:
            uploaded_file = folder.upload_stream(file_content, file_name)
        
        logger.info(f"Upload completed successfully. File ID: {uploaded_file.id}")
        
        # Return the file ID and shared link
        shared_link = uploaded_file.get_shared_link()
        return {
            'file_id': uploaded_file.id,
            'shared_link': shared_link
        }
    except Exception as e:
        logger.error(f"Error uploading to Box: {str(e)}")
        return None

def main():
    """Main function to orchestrate the process."""
    logger.info("Starting SanMar FTP to Box.com process")
    
    # Create temporary directory for files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Generate file paths
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dip_file_path = os.path.join(temp_dir, f"sanmar_inventory_{timestamp}.dip")
        csv_file_path = os.path.join(temp_dir, f"sanmar_inventory_{timestamp}.csv")
        csv_file_name = f"sanmar_inventory_{timestamp}.csv"
        
        # Download from FTP
        if not download_from_ftp(dip_file_path):
            logger.error("Failed to download from FTP. Aborting.")
            sys.exit(1)
        
        # Convert to CSV
        if not convert_to_csv(dip_file_path, csv_file_path):
            logger.error("Failed to convert file. Aborting.")
            sys.exit(1)
        
        # Upload to Box
        upload_result = upload_to_box(csv_file_path, csv_file_name)
        if not upload_result:
            logger.error("Failed to upload to Box. Aborting.")
            sys.exit(1)
        
        logger.info("Process completed successfully")
        logger.info(f"CSV file uploaded to Box.com: {csv_file_name}")
        logger.info(f"Shared link: {upload_result['shared_link']}")

if __name__ == "__main__":
    main()