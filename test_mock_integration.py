"""
Test script to verify integration with our mock SanMar product data
"""

import os
import sys
import json
import logging
import unittest
from flask import url_for

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import our mock data module
from mock_product_data import (
    get_mock_product_data, 
    get_mock_pricing, 
    get_mock_inventory,
    get_mock_image_url,
    get_mock_swatch_url,
    MOCK_PRODUCTS,
    MOCK_PRICING,
    MOCK_INVENTORY
)

class TestMockIntegration(unittest.TestCase):
    """Test the integration with our mock SanMar product data"""
    
    def setUp(self):
        """Set up test variables"""
        self.test_styles = ["PC61", "J790", "K500", "L500"]
        self.test_colors = {
            "PC61": ["Black", "White", "Navy"],
            "J790": ["Black/Chrome", "AtlBlue/Chrome"],
            "K500": ["Black", "Navy", "Red"],
            "L500": ["Black", "White", "Navy"]
        }
        self.test_sizes = {
            "PC61": ["S", "M", "L", "XL", "2XL"],
            "J790": ["S", "M", "L", "XL", "2XL"],
            "K500": ["S", "M", "L", "XL", "2XL"],
            "L500": ["S", "M", "L", "XL", "2XL"]
        }
        
    def test_mock_product_data(self):
        """Test that we can get mock product data"""
        for style in self.test_styles:
            # Test getting product data for a style
            logger.info(f"Testing mock product data for style: {style}")
            product_data = get_mock_product_data(style)
            
            # Assertions
            self.assertIsNotNone(product_data, f"Product data for {style} should not be None")
            self.assertIn("product_name", product_data, f"Product data for {style} should have product_name")
            self.assertIn("catalog_colors", product_data, f"Product data for {style} should have catalog_colors")
            self.assertIn("sizes", product_data, f"Product data for {style} should have sizes")
            
            # Test colors
            self.assertTrue(len(product_data["catalog_colors"]) > 0, f"Product data for {style} should have at least one color")
            
            # Test sizes
            self.assertTrue(len(product_data["sizes"]) > 0, f"Product data for {style} should have at least one size")
            
            # Test images
            self.assertIn("images", product_data, f"Product data for {style} should have images")
            self.assertIn("swatch_images", product_data, f"Product data for {style} should have swatch_images")
            
            # Test with color parameter
            if style in self.test_colors and len(self.test_colors[style]) > 0:
                color = self.test_colors[style][0]
                logger.info(f"Testing mock product data for style: {style}, color: {color}")
                product_data_with_color = get_mock_product_data(style, color)
                self.assertIsNotNone(product_data_with_color, f"Product data for {style}, color {color} should not be None")
                
                # If a color was provided, the catalog_colors should only contain that color
                if product_data_with_color:
                    self.assertEqual(len(product_data_with_color["catalog_colors"]), 1, 
                                     f"Product data for {style}, color {color} should have exactly one color")
                    self.assertEqual(product_data_with_color["catalog_colors"][0].lower(), color.lower(), 
                                     f"Product data for {style}, color {color} should have the correct color")
                
                # Test with size parameter
                if style in self.test_sizes and len(self.test_sizes[style]) > 0:
                    size = self.test_sizes[style][0]
                    logger.info(f"Testing mock product data for style: {style}, color: {color}, size: {size}")
                    product_data_with_color_size = get_mock_product_data(style, color, size)
                    self.assertIsNotNone(product_data_with_color_size, 
                                         f"Product data for {style}, color {color}, size {size} should not be None")
                    
                    # If a size was provided, the sizes should only contain that size
                    if product_data_with_color_size and "sizes" in product_data_with_color_size:
                        self.assertEqual(len(product_data_with_color_size["sizes"]), 1, 
                                         f"Product data for {style}, color {color}, size {size} should have exactly one size")
                        self.assertEqual(product_data_with_color_size["sizes"][0], size, 
                                         f"Product data for {style}, color {color}, size {size} should have the correct size")
            
            print(f"✓ Mock product data for {style} is valid")

    def test_mock_pricing(self):
        """Test that we can get mock pricing data"""
        for style in self.test_styles:
            # Test getting pricing data for a style
            logger.info(f"Testing mock pricing data for style: {style}")
            pricing_data = get_mock_pricing(style)
            
            # Assertions
            self.assertIsNotNone(pricing_data, f"Pricing data for {style} should not be None")
            self.assertIn("original_price", pricing_data, f"Pricing data for {style} should have original_price")
            self.assertIn("sale_price", pricing_data, f"Pricing data for {style} should have sale_price")
            self.assertIn("program_price", pricing_data, f"Pricing data for {style} should have program_price")
            self.assertIn("case_size", pricing_data, f"Pricing data for {style} should have case_size")
            
            # Check that each price dictionary has at least one size
            self.assertTrue(len(pricing_data["original_price"]) > 0, 
                           f"Pricing data for {style} should have at least one size in original_price")
            self.assertTrue(len(pricing_data["sale_price"]) > 0, 
                           f"Pricing data for {style} should have at least one size in sale_price")
            self.assertTrue(len(pricing_data["program_price"]) > 0, 
                           f"Pricing data for {style} should have at least one size in program_price")
            self.assertTrue(len(pricing_data["case_size"]) > 0, 
                           f"Pricing data for {style} should have at least one size in case_size")
            
            # Check that common sizes have pricing data
            common_sizes = ["M", "L", "XL"]
            for size in common_sizes:
                if size in pricing_data["original_price"]:
                    self.assertGreater(pricing_data["original_price"][size], 0, 
                                      f"Pricing data for {style}, size {size} should have a positive original price")
                    self.assertGreater(pricing_data["sale_price"][size], 0, 
                                      f"Pricing data for {style}, size {size} should have a positive sale price")
                    self.assertGreater(pricing_data["program_price"][size], 0, 
                                      f"Pricing data for {style}, size {size} should have a positive program price")
                    self.assertGreater(pricing_data["case_size"][size], 0, 
                                      f"Pricing data for {style}, size {size} should have a positive case size")
            
            print(f"✓ Mock pricing data for {style} is valid")

    def test_mock_inventory(self):
        """Test that we can get mock inventory data"""
        for style in self.test_styles:
            # Test getting inventory data for a style
            logger.info(f"Testing mock inventory data for style: {style}")
            inventory_data = get_mock_inventory(style)
            
            # Some styles might not have inventory data in our mock
            if inventory_data is None:
                logger.warning(f"No mock inventory data for style: {style}")
                continue
                
            # Assertions
            self.assertIsNotNone(inventory_data, f"Inventory data for {style} should not be None")
            self.assertTrue(len(inventory_data) > 0, f"Inventory data for {style} should have at least one color")
            
            # Test a specific color if available
            if style in self.test_colors and len(self.test_colors[style]) > 0:
                # Find a color that exists in the inventory data
                test_color = None
                for color in self.test_colors[style]:
                    if color in inventory_data:
                        test_color = color
                        break
                        
                if test_color:
                    logger.info(f"Testing mock inventory data for style: {style}, color: {test_color}")
                    inventory_data_with_color = get_mock_inventory(style, test_color)
                    self.assertIsNotNone(inventory_data_with_color, 
                                        f"Inventory data for {style}, color {test_color} should not be None")
                    self.assertIn(test_color, inventory_data_with_color, 
                                 f"Inventory data for {style}, color {test_color} should have the color key")
                    
                    # Test a specific size if available
                    color_inventory = inventory_data[test_color]
                    if len(color_inventory) > 0:
                        test_size = next(iter(color_inventory))
                        logger.info(f"Testing mock inventory data for style: {style}, color: {test_color}, size: {test_size}")
                        inventory_data_with_color_size = get_mock_inventory(style, test_color, test_size)
                        self.assertIsNotNone(inventory_data_with_color_size, 
                                            f"Inventory data for {style}, color {test_color}, size {test_size} should not be None")
                        self.assertIn(test_color, inventory_data_with_color_size, 
                                     f"Inventory data for {style}, color {test_color}, size {test_size} should have the color key")
                        self.assertIn(test_size, inventory_data_with_color_size[test_color], 
                                     f"Inventory data for {style}, color {test_color}, size {test_size} should have the size key")
            
            print(f"✓ Mock inventory data for {style} is valid")

    def test_mock_image_urls(self):
        """Test that we can generate mock image URLs"""
        for style in self.test_styles:
            # Test getting a main product image URL
            logger.info(f"Testing mock image URL for style: {style}")
            image_url = get_mock_image_url(style)
            self.assertIsNotNone(image_url, f"Image URL for {style} should not be None")
            self.assertTrue(image_url.startswith("https://cdni.sanmar.com/catalog/images/"), 
                           f"Image URL for {style} should start with the correct base URL")
            self.assertTrue(image_url.endswith(".jpg"), f"Image URL for {style} should end with .jpg")
            
            # Test with different image types
            for image_type in ["p110", "m110", ""]:
                logger.info(f"Testing mock image URL for style: {style}, image_type: {image_type}")
                image_url = get_mock_image_url(style, None, image_type)
                self.assertIsNotNone(image_url, f"Image URL for {style}, image_type {image_type} should not be None")
                self.assertTrue(image_url.startswith("https://cdni.sanmar.com/catalog/images/"), 
                               f"Image URL for {style}, image_type {image_type} should start with the correct base URL")
                # Check that the image type is included in the URL if provided
                if image_type:
                    self.assertTrue(image_type in image_url, 
                                   f"Image URL for {style}, image_type {image_type} should include the image type")
            
            # Test with color parameter
            if style in self.test_colors and len(self.test_colors[style]) > 0:
                color = self.test_colors[style][0]
                logger.info(f"Testing mock image URL for style: {style}, color: {color}")
                image_url = get_mock_image_url(style, color)
                self.assertIsNotNone(image_url, f"Image URL for {style}, color {color} should not be None")
                self.assertTrue(image_url.startswith("https://cdni.sanmar.com/catalog/images/"), 
                               f"Image URL for {style}, color {color} should start with the correct base URL")
                
                # Test swatch image URL
                logger.info(f"Testing mock swatch URL for style: {style}, color: {color}")
                swatch_url = get_mock_swatch_url(style, color)
                self.assertIsNotNone(swatch_url, f"Swatch URL for {style}, color {color} should not be None")
                self.assertTrue(swatch_url.startswith("https://cdni.sanmar.com/catalog/images/"), 
                               f"Swatch URL for {style}, color {color} should start with the correct base URL")
                self.assertTrue(f"{style}_" in swatch_url, 
                               f"Swatch URL for {style}, color {color} should include the style number")
            
            print(f"✓ Mock image URLs for {style} are valid")

    def test_mock_data_consistency(self):
        """Test that mock data is consistent across different modules"""
        for style in self.test_styles:
            # Skip styles that don't have both product data and inventory data
            if style not in MOCK_PRODUCTS or style not in MOCK_INVENTORY:
                continue
                
            product_data = MOCK_PRODUCTS[style]
            pricing_data = MOCK_PRICING.get(style, None)
            inventory_data = MOCK_INVENTORY.get(style, None)
            
            self.assertIsNotNone(product_data, f"Product data for {style} should not be None")
            self.assertIsNotNone(pricing_data, f"Pricing data for {style} should not be None")
            self.assertIsNotNone(inventory_data, f"Inventory data for {style} should not be None")
            
            # Check that catalog colors exist in inventory data
            for color in product_data["catalog_colors"]:
                # We may not have inventory data for all colors
                if color in inventory_data:
                    self.assertIsNotNone(inventory_data[color], 
                                        f"Inventory data for {style}, color {color} should not be None")
                    
                    # Check that sizes in inventory data match sizes in product data
                    inventory_sizes = set(inventory_data[color].keys())
                    product_sizes = set(product_data["sizes"])
                    
                    # There might be sizes in inventory that aren't in product data
                    # and vice versa, but there should be some overlap
                    intersection = inventory_sizes.intersection(product_sizes)
                    self.assertTrue(len(intersection) > 0, 
                                   f"Inventory data for {style}, color {color} should have some sizes that match product data")
            
            # Check that sizes in pricing data match sizes in product data
            pricing_sizes = set(pricing_data["original_price"].keys())
            product_sizes = set(product_data["sizes"])
            
            # There might be sizes in pricing that aren't in product data
            # and vice versa, but there should be some overlap
            intersection = pricing_sizes.intersection(product_sizes)
            self.assertTrue(len(intersection) > 0, 
                           f"Pricing data for {style} should have some sizes that match product data")
            
            print(f"✓ Mock data for {style} is consistent across modules")

def main():
    """Run the tests"""
    unittest.main()

if __name__ == "__main__":
    main()