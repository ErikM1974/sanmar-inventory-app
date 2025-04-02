#!/usr/bin/env python
"""
Caspio API client for interacting with Caspio tables.
"""

import os
import json
import logging
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CaspioClient:
    """Client for interacting with the Caspio API."""
    
    def __init__(self, base_url, client_id=None, client_secret=None, access_token=None, refresh_token=None):
        """Initialize the Caspio API client."""
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expiry = None
    
    def get_access_token(self):
        """Get an access token from the Caspio API."""
        # If we already have an access token, use it
        if self.access_token:
            return self.access_token
        
        # If we don't have an access token but have client credentials, get a new token
        if self.client_id and self.client_secret:
            auth_url = f"{self.base_url}/oauth/token"
            payload = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            try:
                response = requests.post(auth_url, data=payload)
                response.raise_for_status()
                
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
                
                return self.access_token
            except requests.exceptions.RequestException as e:
                logger.error(f"Error getting authentication token: {str(e)}")
                if hasattr(e, 'response') and e.response is not None:
                    logger.error(f"Response content: {e.response.text}")
                return None
        
        logger.error("No valid authentication method available.")
        return None
    
    def refresh_access_token(self):
        """Refresh the access token using the refresh token."""
        if not self.refresh_token:
            logger.error("No refresh token available.")
            return False
        
        auth_url = f"{self.base_url}/oauth/token"
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        
        try:
            response = requests.post(auth_url, data=payload)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')
            expires_in = token_data.get('expires_in', 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            logger.info("Successfully refreshed access token.")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error refreshing access token: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return False
    
    def make_api_request(self, endpoint, method="GET", data=None, params=None):
        """Make a request to the Caspio API."""
        # Ensure we don't have double slashes in the URL
        if self.base_url.endswith('/') and endpoint.startswith('/'):
            endpoint = endpoint[1:]
        elif not self.base_url.endswith('/') and not endpoint.startswith('/'):
            endpoint = f"/{endpoint}"
        
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.get_access_token()}',
            'Content-Type': 'application/json'
        }
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, params=params)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None
            
            response.raise_for_status()
            
            if response.status_code == 204:  # No content
                return {}
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return None
    
    def get_tables(self):
        """Get a list of all tables in the Caspio account."""
        endpoint = "rest/v2/tables"
        response = self.make_api_request(endpoint)
        
        if response and 'Result' in response:
            return response['Result']
        
        return []
    
    def get_table_fields(self, table_name):
        """Get a list of all fields in a table."""
        endpoint = f"rest/v2/tables/{table_name}/fields"
        response = self.make_api_request(endpoint)
        
        if response and 'Result' in response:
            return response['Result']
        
        return []
    
    def query_records(self, table_name, fields=None, where=None, order_by=None, limit=None, offset=None):
        """Query records from a table."""
        endpoint = f"rest/v2/tables/{table_name}/records"
        params = {}
        
        if fields:
            params['select'] = ','.join(fields)
        
        if where:
            params['where'] = where
        
        if order_by:
            params['sort'] = order_by
        
        if limit:
            params['limit'] = limit
        
        if offset:
            params['offset'] = offset
        
        response = self.make_api_request(endpoint, params=params)
        
        if response and 'Result' in response:
            return response['Result']
        
        return []
    
    def get_record(self, table_name, record_id):
        """Get a record from a table by ID."""
        endpoint = f"rest/v2/tables/{table_name}/records/{record_id}"
        return self.make_api_request(endpoint)
    
    def insert_record(self, table_name, record_data):
        """Insert a record into a table."""
        endpoint = f"rest/v2/tables/{table_name}/records"
        return self.make_api_request(endpoint, method="POST", data=record_data)
    
    def update_record(self, table_name, record_id, record_data):
        """Update a record in a table."""
        endpoint = f"rest/v2/tables/{table_name}/records/{record_id}"
        return self.make_api_request(endpoint, method="PUT", data=record_data)
    
    def delete_record(self, table_name, record_id):
        """Delete a record from a table."""
        endpoint = f"rest/v2/tables/{table_name}/records/{record_id}"
        return self.make_api_request(endpoint, method="DELETE")
    
    def delete_all_records(self, table_name):
        """Delete all records from a table."""
        endpoint = f"rest/v2/tables/{table_name}/records"
        return self.make_api_request(endpoint, method="DELETE")