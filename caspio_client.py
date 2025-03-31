"""
Caspio API Client for accessing product data from Caspio Database
"""
import json
import logging
import requests
import time
from urllib.parse import urljoin

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CaspioClient:
    """Client for accessing the Caspio REST API"""
    
    def __init__(self):
        # Caspio API configuration
        self.base_url = "https://c3eku948.caspio.com/"
        self.token_endpoint = "oauth/token"
        self.swagger_url = "rest/swagger"
        self.client_id = "25bea36404d34215e23255861c370d0fc417444f0af8e8477c"
        self.client_secret = "5316be27cadd4b56a235a544c9018aa54feb64d90805430011"
        
        # Caspio table name
        self.products_table = "Sanmar_Bulk_251816_Feb2024"
        
        # Pre-configured access token
        self._access_token = "OGi_Ibkp7GlHv-upuNAIJlWpLm3v8aNZDU2iaUcq_buZaGGfBKMfEx4Vd3DRBjGNK1Izse50dACFVZXanB0002LU8hZCU6mP-lVHLAZRovCKFRy3z3W-mWEa-LqBQve2UwNfZJTWO1epgm_XYd8TfQ5gu7XeGzBATzK7ktH_4GOm0QJYWpM3ncJNaDNE0fUn3bFGypzFVTozbtesT1gj1I7cwywZCbqXOIEHvxtvcEaldDx-MvDYCC4BdZPxtxzMEo5aWpfccuQFApWqKZ8hcagzB424Mbw5GFflr6AAD2SpH6Qrl88DOgHMn9xW_j_TekNBCwYQGD51vszE-AeOPXxdq0fnXJ1naNFIU-8JusnSBCY76M7fBe-4EgcEyHF-pgn0OeAHHK-Kb9XmtHaFFF262Q4wHamXtga0O0-hLa0"
        self._token_type = "bearer"
        self._refresh_token = "620fca784a99481b990e1a65663872f61c03c2c3821041d6a0a1688615ff7da4"
        self._token_expiry = time.time() + 86399  # Set expiry to ~24 hours from now
        
        # Cache for API responses
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache TTL
    
    def _get_access_token(self):
        """Get a new access token or return cached one if still valid"""
        current_time = time.time()
        
        # If token exists and is not expired, return it
        if self._access_token and current_time < self._token_expiry:
            return self._access_token
        
        # Otherwise, get a new token
        token_url = urljoin(self.base_url, self.token_endpoint)
        
        try:
            response = requests.post(
                token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
            )
            
            response.raise_for_status()
            token_data = response.json()
            
            self._access_token = token_data.get("access_token")
            # Set expiry time with a small buffer to avoid edge cases
            expires_in = token_data.get("expires_in", 3600)
            self._token_expiry = current_time + expires_in - 60
            
            logger.info("Successfully obtained new Caspio API access token")
            return self._access_token
            
        except Exception as e:
            logger.error(f"Error obtaining Caspio API access token: {str(e)}")
            return None
    
    def _make_api_request(self, endpoint, method="GET", params=None, data=None):
        """Make a request to the Caspio API with authentication"""
        # Get a valid access token
        access_token = self._get_access_token()
        if not access_token:
            logger.error("Unable to obtain access token for Caspio API")
            return None
        
        # Create cache key if this is a GET request
        cache_key = None
        if method == "GET":
            cache_key = f"{endpoint}:{json.dumps(params or {})}"
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if time.time() < cache_entry['expiry']:
                    logger.info(f"Using cached response for {endpoint}")
                    return cache_entry['data']
        
        # Make the API request
        url = urljoin(self.base_url, endpoint)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = None
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            
            if not response:
                logger.error(f"Invalid method {method} for Caspio API request")
                return None
                
            response.raise_for_status()
            result = response.json()
            
            # Cache the result for GET requests
            if method == "GET" and cache_key:
                self.cache[cache_key] = {
                    'data': result,
                    'expiry': time.time() + self.cache_ttl
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error making Caspio API request to {endpoint}: {str(e)}")
            return None
    
    def get_categories(self):
        """Get distinct categories from SanMar Bulk Data"""
        endpoint = f"rest/v2/tables/{self.products_table}/records"
        params = {
            "q.select": "DISTINCT category",
            "q.where": "category IS NOT NULL",
            "q.orderBy": "category ASC"
        }
        return self._make_api_request(endpoint, "GET", params=params)
        
    def get_subcategories(self, category):
        """Get distinct subcategories for a specific category"""
        endpoint = f"rest/v2/tables/{self.products_table}/records"
        params = {
            "q.select": "DISTINCT subcategory",
            "q.where": f"category = '{category}' AND subcategory IS NOT NULL",
            "q.orderBy": "subcategory ASC"
        }
        return self._make_api_request(endpoint, "GET", params=params)
    
    def get_products_by_category(self, category, page=1, page_size=50):
        """Get products filtered by category"""
        endpoint = f"rest/v2/tables/{self.products_table}/records"
        params = {
            "q.pageSize": page_size,
            "q.pageNumber": page,
            "q.where": f"category = '{category}'",
            "q.orderBy": "style ASC"
        }
        return self._make_api_request(endpoint, "GET", params=params)
    
    def get_products_by_style_search(self, style_term, page=1, page_size=50):
        """Get products matching a style search term"""
        endpoint = f"rest/v2/tables/{self.products_table}/records"
        params = {
            "q.pageSize": page_size,
            "q.pageNumber": page,
            "q.where": f"style LIKE '{style_term}%'",
            "q.orderBy": "style ASC"
        }
        return self._make_api_request(endpoint, "GET", params=params)
    
    def get_product_by_style(self, style):
        """Get product information by exact style number"""
        endpoint = f"rest/v2/tables/{self.products_table}/records"
        params = {
            "q.where": f"style = '{style}'",
            "q.orderBy": "color ASC, size ASC"
        }
        return self._make_api_request(endpoint, "GET", params=params)
    
    def get_brands(self):
        """Get distinct brands from SanMar Bulk Data"""
        endpoint = f"rest/v2/tables/{self.products_table}/records"
        params = {
            "q.select": "DISTINCT brandName",
            "q.where": "brandName IS NOT NULL",
            "q.orderBy": "brandName ASC"
        }
        return self._make_api_request(endpoint, "GET", params=params)

# Create a singleton instance
caspio_api = CaspioClient()