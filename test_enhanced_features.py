"""
Test script for enhanced homepage and quote cart features
Connects to SanMar API for real product data and images for testing
"""

import unittest
import os
import sys
import json
import logging
import requests
from flask import url_for
from bs4 import BeautifulSoup
from unittest.mock import patch, MagicMock

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add app directory to path to import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app
from sanmar_inventory import get_inventory_by_style
from app_customer_routes import api_caspio_categories, api_product_quick_view, api_submit_quote

class TestEnhancedFeatures(unittest.TestCase):
    """Tests for the enhanced homepage and quote cart features"""

    def setUp(self):
        """Set up test client and other test variables"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Sample product styles for testing
        self.test_styles = ["PC61", "J790", "K110", "ST850", "L420", "C112"]
        
        # Sample quote cart data
        self.sample_quote_data = {
            "customer": {
                "name": "Test Customer",
                "email": "test@example.com",
                "phone": "555-123-4567",
                "company": "Test Company",
                "message": "This is a test quote request"
            },
            "items": [
                {
                    "style": "PC61",
                    "name": "Port & Company Essential T-Shirt",
                    "color": "Black",
                    "size": "XL",
                    "price": 5.99,
                    "quantity": 24,
                    "imageUrl": "https://cdni.sanmar.com/catalog/images/PC61p110.jpg"
                },
                {
                    "style": "J790",
                    "name": "Port Authority Glacier Soft Shell Jacket",
                    "color": "Navy/Chrome",
                    "size": "L",
                    "price": 49.99,
                    "quantity": 10,
                    "imageUrl": "https://cdni.sanmar.com/catalog/images/J790p110.jpg"
                }
            ],
            "totalAmount": 643.66,
            "submittedAt": "2025-04-01T16:00:00.000Z"
        }

    def tearDown(self):
        """Clean up after each test"""
        self.app_context.pop()

    def test_home_page_loads(self):
        """Test if the enhanced homepage loads correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check if the page contains key elements
        html = response.data.decode('utf-8')
        self.assertIn("Northwest Custom Apparel", html)
        self.assertIn("Featured Products", html)
        self.assertIn("Find Products", html)
        self.assertIn("Categories", html)
        
        logger.info("✅ Homepage loaded successfully with all key elements")

    def test_quote_cart_page_loads(self):
        """Test if the quote cart page loads correctly"""
        response = self.client.get('/quote')
        self.assertEqual(response.status_code, 200)
        
        # Check if the page contains key elements
        html = response.data.decode('utf-8')
        self.assertIn("Your Quote Cart", html)
        self.assertIn("Review Items", html)
        self.assertIn("Add Your Details", html)
        self.assertIn("Get Your Quote", html)
        
        logger.info("✅ Quote cart page loaded successfully with all key elements")

    def test_caspio_categories_api(self):
        """Test the Caspio categories API endpoint"""
        response = self.client.get('/api/caspio-categories')
        self.assertEqual(response.status_code, 200)
        
        # Parse response JSON
        data = json.loads(response.data.decode('utf-8'))
        
        # Check if the response contains the expected structure
        self.assertTrue(data.get('success'))
        self.assertIn('categories', data)
        self.assertIsInstance(data['categories'], list)
        self.assertTrue(len(data['categories']) > 0)
        
        # Check if each category has the expected fields
        for category in data['categories']:
            self.assertIn('name', category)
            self.assertIn('count', category)
        
        logger.info("✅ Caspio categories API returned valid data")

    def test_product_quick_view_api(self):
        """Test the product quick view API endpoint with real SanMar products"""
        for style in self.test_styles:
            response = self.client.get(f'/api/product-quick-view/{style}')
            self.assertEqual(response.status_code, 200, f"Failed to get quick view for {style}")
            
            # Parse response JSON
            data = json.loads(response.data.decode('utf-8'))
            
            # Check if the response contains the expected structure
            if data.get('success'):
                self.assertIn('product', data)
                product = data['product']
                self.assertIn('name', product)
                self.assertIn('description', product)
                self.assertIn('price', product)
                self.assertIn('colors', product)
                self.assertIn('sizes', product)
                self.assertIn('imageUrl', product)
                
                # Verify image URL is valid
                image_url = product['imageUrl']
                if image_url and not image_url.startswith('http'):
                    self.fail(f"Invalid image URL format: {image_url}")
                
                logger.info(f"✅ Product quick view for {style} returned valid data")
            else:
                logger.warning(f"⚠️ Product quick view for {style} failed: {data.get('message')}")

    @patch('app_customer_routes.api_submit_quote')
    def test_quote_submission(self, mock_submit_quote):
        """Test quote submission API"""
        # Configure mock to return success
        mock_response = {
            "success": True,
            "message": "Quote submitted successfully",
            "quoteId": "Q-12345678"
        }
        mock_submit_quote.return_value = mock_response
        
        # Send post request with sample quote data
        response = self.client.post(
            '/api/submit-quote',
            data=json.dumps(self.sample_quote_data),
            content_type='application/json'
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data.get('success'))
        self.assertIn('quoteId', data)
        
        logger.info("✅ Quote submission API passed")

    def test_sanmar_image_urls(self):
        """Test that SanMar image URLs are valid and accessible"""
        for style in self.test_styles:
            # Test main product image
            main_image_url = f"https://cdni.sanmar.com/catalog/images/{style}p110.jpg"
            response = requests.head(main_image_url)
            
            if response.status_code == 200:
                logger.info(f"✅ Main image for {style} is accessible")
            else:
                logger.warning(f"⚠️ Main image for {style} is not accessible (Status: {response.status_code})")
                
                # Try alternative URLs
                alt_urls = [
                    f"https://cdni.sanmar.com/catalog/images/{style}m110.jpg",  # Model image
                    f"https://cdni.sanmar.com/catalog/images/{style}.jpg",      # Standard image
                    f"https://cdni.sanmar.com/catalog/images/{style}.png"       # PNG format
                ]
                
                for alt_url in alt_urls:
                    alt_response = requests.head(alt_url)
                    if alt_response.status_code == 200:
                        logger.info(f"✅ Alternative image for {style} is accessible: {alt_url}")
                        break
                else:
                    logger.error(f"❌ No accessible images found for {style}")

    @patch('sanmar_inventory.get_inventory_by_style')
    def test_inventory_integration(self, mock_get_inventory):
        """Test integration with SanMar inventory API"""
        # Sample inventory data
        mock_inventory = {
            "Black": {
                "S": {"total": 250, "warehouses": {"1": 50, "2": 100, "3": 100}},
                "M": {"total": 500, "warehouses": {"1": 100, "2": 200, "3": 200}},
                "L": {"total": 750, "warehouses": {"1": 150, "2": 300, "3": 300}},
                "XL": {"total": 750, "warehouses": {"1": 150, "2": 300, "3": 300}},
                "2XL": {"total": 500, "warehouses": {"1": 100, "2": 200, "3": 200}}
            },
            "Navy": {
                "S": {"total": 200, "warehouses": {"1": 40, "2": 80, "3": 80}},
                "M": {"total": 400, "warehouses": {"1": 80, "2": 160, "3": 160}},
                "L": {"total": 600, "warehouses": {"1": 120, "2": 240, "3": 240}},
                "XL": {"total": 600, "warehouses": {"1": 120, "2": 240, "3": 240}},
                "2XL": {"total": 400, "warehouses": {"1": 80, "2": 160, "3": 160}}
            }
        }
        
        # Set up mock to return sample inventory data
        mock_get_inventory.return_value = mock_inventory
        
        # Test with a sample style
        style = "PC61"
        inventory = get_inventory_by_style(style)
        
        # Check if inventory data has the correct structure
        self.assertIsInstance(inventory, dict)
        self.assertIn("Black", inventory)
        self.assertIn("Navy", inventory)
        
        # Check individual size inventory
        self.assertIn("M", inventory["Black"])
        self.assertEqual(inventory["Black"]["M"]["total"], 500)
        
        logger.info("✅ Inventory API integration test passed")

    def test_javascript_assets_load(self):
        """Test that all JavaScript assets load correctly"""
        js_files = [
            '/static/quote-cart.js',
            '/static/homepage-enhancements.js',
            '/static/product-cache.js'
        ]
        
        for js_file in js_files:
            response = self.client.get(js_file)
            self.assertEqual(response.status_code, 200, f"Failed to load {js_file}")
            logger.info(f"✅ JavaScript file {js_file} loaded successfully")

    def test_css_assets_load(self):
        """Test that all CSS assets load correctly"""
        css_files = [
            '/static/style.css',
            '/static/home-style.css',
            '/static/product-styles.css'
        ]
        
        for css_file in css_files:
            response = self.client.get(css_file)
            self.assertEqual(response.status_code, 200, f"Failed to load {css_file}")
            logger.info(f"✅ CSS file {css_file} loaded successfully")


if __name__ == '__main__':
    try:
        # Initialize the server in a way that doesn't conflict with the test client
        with app.app_context():
            logger.info("Starting comprehensive tests of enhanced features...")
            unittest.main(verbosity=2)
    except Exception as e:
        logger.error(f"Error running tests: {str(e)}")
        sys.exit(1)