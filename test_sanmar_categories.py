import os
import json
import logging
from zeep import Client
from zeep.exceptions import Fault, TransportError
from zeep.helpers import serialize_object
import xml.etree.ElementTree as ET

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# SanMar Category service WSDL URL
CATEGORY_WSDL_URL = "https://ws.sanmar.com:8080/SanMarWebService/SanMarCategoryServicePort?wsdl"

# Credentials (from environment variables)
USERNAME = os.environ.get('SANMAR_USERNAME', 'your_username')
PASSWORD = os.environ.get('SANMAR_PASSWORD', 'your_password')
CUSTOMER_ID = os.environ.get('SANMAR_CUSTOMER_ID', 'your_customer_id')
CUSTOMER_USERNAME = os.environ.get('SANMAR_CUSTOMER_USERNAME', 'your_customer_username')
CUSTOMER_PASSWORD = os.environ.get('SANMAR_CUSTOMER_PASSWORD', 'your_customer_password')

def get_categories():
    """
    Fetch all categories from SanMar API
    """
    try:
        # Create the SOAP client
        client = Client(CATEGORY_WSDL_URL)
        
        # Prepare authentication header
        credentials = {
            'username': USERNAME,
            'password': PASSWORD,
            'customerID': CUSTOMER_ID,
            'customerUsername': CUSTOMER_USERNAME,
            'customerPassword': CUSTOMER_PASSWORD
        }
        
        # Create request header
        header = client.get_element('ns0:serviceCredentials')(
            username=credentials['username'],
            password=credentials['password'],
            customerID=credentials['customerID'],
            customerUsername=credentials['customerUsername'],
            customerPassword=credentials['customerPassword']
        )
        
        # Set the header for all requests
        client.set_default_soapheaders([header])
        
        # Call the getCategory method
        logger.info("Calling SanMar Category API...")
        response = client.service.getCategory()
        
        # Convert response to Python dict
        result = serialize_object(response)
        
        # Pretty print the results
        logger.info("Category API call successful")
        
        # Parse category tree structure
        categories = []
        if result and not result.get('errorOccured', True):
            category_tree = result.get('categoryTree', [])
            for category in category_tree:
                process_category(category, categories)
        
        return categories
        
    except Fault as e:
        logger.error(f"SOAP fault: {str(e)}")
        return []
    except TransportError as e:
        logger.error(f"Transport error: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return []

def process_category(category, categories, parent=None):
    """
    Process a category object and extract its information
    """
    if not category:
        return
    
    # Extract basic category info
    cat_info = {
        'id': category.get('categoryNumber', ''),
        'name': category.get('categoryName', ''),
        'parentId': parent['id'] if parent else None,
        'parentName': parent['name'] if parent else None,
        'subcategories': []
    }
    
    # Only add top-level categories to the main list
    if not parent:
        categories.append(cat_info)
    elif parent and 'subcategories' in parent:
        parent['subcategories'].append(cat_info)
    
    # Process child categories recursively
    child_categories = category.get('childCategories', [])
    if child_categories:
        for child in child_categories:
            process_category(child, categories, cat_info)

def main():
    """Main function to run the test"""
    logger.info("Starting SanMar Category API test")
    
    # Get all categories
    categories = get_categories()
    
    if categories:
        # Save the categories to a file
        output_file = 'data/sanmar_api_categories.json'
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(categories, f, indent=2)
        
        # Print summary
        logger.info(f"Retrieved {len(categories)} top-level categories")
        
        # Print category names
        print("\nMain Categories from SanMar API:")
        for cat in categories:
            print(f"- {cat['name']} (ID: {cat['id']})")
            subcats = cat.get('subcategories', [])
            if subcats:
                print(f"  Subcategories ({len(subcats)}):")
                for subcat in subcats[:5]:  # Show first 5 subcategories
                    print(f"  - {subcat['name']} (ID: {subcat['id']})")
                if len(subcats) > 5:
                    print(f"  - ...and {len(subcats) - 5} more")
                    
        print("\nCategory data saved to:", output_file)
    else:
        logger.error("Failed to retrieve categories from SanMar API")

if __name__ == "__main__":
    main()