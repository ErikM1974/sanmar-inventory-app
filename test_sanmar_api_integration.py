"""
Test script to verify SanMar API integration for product images and data
"""

import os
import sys
import json
import time
import logging
import requests
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from io import BytesIO

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('sanmar_api_test_results.log')
    ]
)
logger = logging.getLogger(__name__)

# Add app directory to path to import from app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import SanMar API modules - try/except to handle import errors gracefully
try:
    from sanmar_inventory import get_inventory_by_style
    from app_product_info import get_product_data
    from sanmar_pricing_api import get_pricing_for_color_swatch
    HAS_API_MODULES = True
except ImportError as e:
    logger.warning(f"Could not import SanMar API modules: {str(e)}")
    logger.warning("Will run in limited mode without direct API access")
    HAS_API_MODULES = False

# List of popular SanMar styles for testing
TEST_STYLES = [
    # T-Shirts
    "PC61", "PC55", "DT6000", "DT5000", "ST350", "2000", "2000B", 
    # Polos
    "K500", "K540", "L500", "L524", "TLK500", "M265",
    # Outerwear
    "J343", "J317", "J754", "L332", "JP77", "J302", 
    # Sweatshirts
    "PC78", "PC90", "PC90H", "18000", "18500", "ST850",
    # Bags & Accessories
    "BG100", "BG200", "BG303", "BG212", "C112", "CP81",
    # Ladies
    "L5001", "L3517", "L6008", "LST700", "L608", "LOG105"
]

class SanMarAPITester:
    def __init__(self):
        """Initialize the SanMar API tester"""
        self.results = {
            "images_tested": 0,
            "images_accessible": 0,
            "images_failed": 0,
            "product_data_tested": 0,
            "product_data_success": 0,
            "product_data_failed": 0,
            "inventory_tested": 0,
            "inventory_success": 0,
            "inventory_failed": 0,
            "pricing_tested": 0,
            "pricing_success": 0, 
            "pricing_failed": 0,
            "failed_styles": [],
            "style_results": {}
        }

    def test_image_url(self, style, image_type="p110"):
        """Test if a SanMar image URL is accessible
        
        Args:
            style (str): Product style code
            image_type (str): Image type (p110, m110, etc.)
            
        Returns:
            tuple: (success, url, status_code, image_size)
        """
        # Construct the URL
        url = f"https://cdni.sanmar.com/catalog/images/{style}{image_type}.jpg"
        
        try:
            # Make a HEAD request first to check if the image exists
            head_response = requests.head(url, timeout=5)
            if head_response.status_code != 200:
                # Try alternative image formats
                alt_urls = [
                    f"https://cdni.sanmar.com/catalog/images/{style.lower()}{image_type}.jpg",
                    f"https://cdni.sanmar.com/catalog/images/{style}{image_type}.png",
                    f"https://cdni.sanmar.com/catalog/images/{style}.jpg"
                ]
                
                for alt_url in alt_urls:
                    alt_head_response = requests.head(alt_url, timeout=5)
                    if alt_head_response.status_code == 200:
                        url = alt_url
                        break
                else:
                    return (False, url, head_response.status_code, None)
            
            # If HEAD request is successful, make a GET request to get the image
            response = requests.get(url, timeout=10)
            
            # Check if the response is successful
            if response.status_code == 200:
                # Try to open the image to verify it's valid
                try:
                    img = Image.open(BytesIO(response.content))
                    width, height = img.size
                    return (True, url, response.status_code, (width, height))
                except Exception as e:
                    logger.warning(f"Invalid image data for {style}: {str(e)}")
                    return (False, url, response.status_code, None)
            else:
                return (False, url, response.status_code, None)
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error accessing {url}: {str(e)}")
            return (False, url, None, None)

    def test_product_data(self, style):
        """Test retrieving product data from SanMar API
        
        Args:
            style (str): Product style code
            
        Returns:
            tuple: (success, data)
        """
        if not HAS_API_MODULES:
            return (False, "API modules not available")
            
        try:
            # Call the product data API
            product_data = get_product_data(style)
            
            if product_data:
                # Check if the product data has expected fields
                required_fields = ['product_name', 'sizes', 'catalog_colors']
                missing_fields = [field for field in required_fields if field not in product_data]
                
                if missing_fields:
                    logger.warning(f"Product data for {style} is missing fields: {missing_fields}")
                    return (False, f"Missing fields: {missing_fields}")
                    
                return (True, product_data)
            else:
                return (False, "No product data returned")
                
        except Exception as e:
            logger.error(f"Error getting product data for {style}: {str(e)}")
            return (False, str(e))

    def test_inventory(self, style):
        """Test retrieving inventory data from SanMar API
        
        Args:
            style (str): Product style code
            
        Returns:
            tuple: (success, data)
        """
        if not HAS_API_MODULES:
            return (False, "API modules not available")
            
        try:
            # Call the inventory API
            inventory_data = get_inventory_by_style(style)
            
            if inventory_data and isinstance(inventory_data, dict) and len(inventory_data) > 0:
                # Check if inventory data has expected structure
                first_color = next(iter(inventory_data))
                if first_color in inventory_data:
                    first_size = next(iter(inventory_data[first_color]))
                    # Check if it has the total and warehouses fields
                    if "total" in inventory_data[first_color][first_size]:
                        return (True, inventory_data)
                
                return (False, "Invalid inventory data structure")
            else:
                return (False, "No inventory data returned")
                
        except Exception as e:
            logger.error(f"Error getting inventory for {style}: {str(e)}")
            return (False, str(e))

    def test_pricing(self, style, color=None):
        """Test retrieving pricing data from SanMar API
        
        Args:
            style (str): Product style code
            color (str, optional): Color name
            
        Returns:
            tuple: (success, data)
        """
        if not HAS_API_MODULES:
            return (False, "API modules not available")
            
        try:
            # Call the pricing API
            pricing_data = get_pricing_for_color_swatch(style=style, color=color)
            
            if pricing_data and not pricing_data.get("error", False):
                return (True, pricing_data)
            else:
                return (False, pricing_data.get("message", "No pricing data returned"))
                
        except Exception as e:
            logger.error(f"Error getting pricing for {style}: {str(e)}")
            return (False, str(e))

    def test_style(self, style):
        """Run all tests for a specific style
        
        Args:
            style (str): Product style code
            
        Returns:
            dict: Test results for this style
        """
        logger.info(f"Testing style: {style}")
        style_result = {
            "style": style,
            "image_results": {},
            "product_data": {"success": False, "data": None},
            "inventory": {"success": False, "data": None},
            "pricing": {"success": False, "data": None}
        }
        
        # Test main product image
        main_image_success, main_image_url, status_code, image_size = self.test_image_url(style)
        style_result["image_results"]["main"] = {
            "success": main_image_success,
            "url": main_image_url,
            "status_code": status_code,
            "size": image_size
        }
        
        self.results["images_tested"] += 1
        if main_image_success:
            self.results["images_accessible"] += 1
        else:
            self.results["images_failed"] += 1
        
        # Test product data
        self.results["product_data_tested"] += 1
        data_success, product_data = self.test_product_data(style)
        style_result["product_data"]["success"] = data_success
        style_result["product_data"]["data"] = "Data available" if data_success else product_data
        
        if data_success:
            self.results["product_data_success"] += 1
            
            # If product data is available, test color swatches
            if isinstance(product_data, dict) and "catalog_colors" in product_data:
                for color in product_data["catalog_colors"][:3]:  # Test first 3 colors only
                    swatch_success, swatch_url, status_code, image_size = self.test_image_url(
                        f"{style}_{color}",
                        image_type="s"
                    )
                    style_result["image_results"][f"swatch_{color}"] = {
                        "success": swatch_success,
                        "url": swatch_url,
                        "status_code": status_code,
                        "size": image_size
                    }
                    
                    self.results["images_tested"] += 1
                    if swatch_success:
                        self.results["images_accessible"] += 1
                    else:
                        self.results["images_failed"] += 1
                        
                # Test model image if available
                model_success, model_url, status_code, image_size = self.test_image_url(style, image_type="m110")
                style_result["image_results"]["model"] = {
                    "success": model_success,
                    "url": model_url,
                    "status_code": status_code,
                    "size": image_size
                }
                
                self.results["images_tested"] += 1
                if model_success:
                    self.results["images_accessible"] += 1
                else:
                    self.results["images_failed"] += 1
                
                # Test first color for inventory
                if len(product_data["catalog_colors"]) > 0:
                    first_color = product_data["catalog_colors"][0]
                    
                    # Test inventory
                    self.results["inventory_tested"] += 1
                    inventory_success, inventory_data = self.test_inventory(style)
                    style_result["inventory"]["success"] = inventory_success
                    style_result["inventory"]["data"] = "Data available" if inventory_success else inventory_data
                    
                    if inventory_success:
                        self.results["inventory_success"] += 1
                    else:
                        self.results["inventory_failed"] += 1
                    
                    # Test pricing
                    self.results["pricing_tested"] += 1
                    pricing_success, pricing_data = self.test_pricing(style, first_color)
                    style_result["pricing"]["success"] = pricing_success
                    style_result["pricing"]["data"] = "Data available" if pricing_success else pricing_data
                    
                    if pricing_success:
                        self.results["pricing_success"] += 1
                    else:
                        self.results["pricing_failed"] += 1
        else:
            self.results["product_data_failed"] += 1
            
        # Check if all tests passed
        all_tests_passed = (
            main_image_success and
            style_result["product_data"]["success"] and
            style_result["inventory"]["success"] and
            style_result["pricing"]["success"]
        )
        
        # Add to failed styles if any test failed
        if not all_tests_passed:
            self.results["failed_styles"].append(style)
            
        # Add results for this style
        self.results["style_results"][style] = style_result
        
        return style_result

    def run_tests(self, styles=None, max_workers=5):
        """Run tests for all styles
        
        Args:
            styles (list, optional): List of styles to test. Defaults to TEST_STYLES.
            max_workers (int, optional): Maximum number of worker threads. Defaults to 5.
            
        Returns:
            dict: Test results
        """
        start_time = time.time()
        logger.info(f"Starting SanMar API integration tests with {max_workers} workers")
        
        if styles is None:
            styles = TEST_STYLES
            
        # Use ThreadPoolExecutor to run tests in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(self.test_style, styles)
            
        end_time = time.time()
        duration = end_time - start_time
        
        # Calculate success rates
        self.results["image_success_rate"] = (
            self.results["images_accessible"] / self.results["images_tested"] * 100
            if self.results["images_tested"] > 0 else 0
        )
        self.results["product_data_success_rate"] = (
            self.results["product_data_success"] / self.results["product_data_tested"] * 100
            if self.results["product_data_tested"] > 0 else 0
        )
        self.results["inventory_success_rate"] = (
            self.results["inventory_success"] / self.results["inventory_tested"] * 100
            if self.results["inventory_tested"] > 0 else 0
        )
        self.results["pricing_success_rate"] = (
            self.results["pricing_success"] / self.results["pricing_tested"] * 100
            if self.results["pricing_tested"] > 0 else 0
        )
        
        # Add test summary
        self.results["total_styles_tested"] = len(styles)
        self.results["total_styles_failed"] = len(self.results["failed_styles"])
        self.results["total_styles_passed"] = self.results["total_styles_tested"] - self.results["total_styles_failed"]
        self.results["overall_success_rate"] = (
            self.results["total_styles_passed"] / self.results["total_styles_tested"] * 100
            if self.results["total_styles_tested"] > 0 else 0
        )
        self.results["duration_seconds"] = duration
        
        return self.results
        
    def print_summary(self):
        """Print a summary of the test results"""
        print("\n" + "="*80)
        print(f"SanMar API Integration Test Summary")
        print("="*80)
        print(f"Total styles tested: {self.results['total_styles_tested']}")
        print(f"Styles passed: {self.results['total_styles_passed']} ({self.results['overall_success_rate']:.2f}%)")
        print(f"Styles failed: {self.results['total_styles_failed']}")
        print("-"*80)
        print(f"Images tested: {self.results['images_tested']}")
        print(f"Images accessible: {self.results['images_accessible']} ({self.results['image_success_rate']:.2f}%)")
        print(f"Images failed: {self.results['images_failed']}")
        print("-"*80)
        print(f"Product data tested: {self.results['product_data_tested']}")
        print(f"Product data success: {self.results['product_data_success']} ({self.results['product_data_success_rate']:.2f}%)")
        print(f"Product data failed: {self.results['product_data_failed']}")
        print("-"*80)
        print(f"Inventory tested: {self.results['inventory_tested']}")
        print(f"Inventory success: {self.results['inventory_success']} ({self.results['inventory_success_rate']:.2f}%)")
        print(f"Inventory failed: {self.results['inventory_failed']}")
        print("-"*80)
        print(f"Pricing tested: {self.results['pricing_tested']}")
        print(f"Pricing success: {self.results['pricing_success']} ({self.results['pricing_success_rate']:.2f}%)")
        print(f"Pricing failed: {self.results['pricing_failed']}")
        print("-"*80)
        print(f"Test duration: {self.results['duration_seconds']:.2f} seconds")
        print("="*80)
        
        if self.results["failed_styles"]:
            print("\nFailed styles:")
            for style in self.results["failed_styles"]:
                print(f"  - {style}")
            print()

def main():
    """Main function"""
    # Create the tester
    tester = SanMarAPITester()
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Test SanMar API integration for images and product data')
    parser.add_argument('--styles', type=str, help='Comma-separated list of styles to test')
    parser.add_argument('--workers', type=int, default=5, help='Maximum number of worker threads')
    parser.add_argument('--output', type=str, help='Output file for detailed results (JSON)')
    args = parser.parse_args()
    
    # Set styles to test
    styles = TEST_STYLES
    if args.styles:
        styles = [s.strip() for s in args.styles.split(',')]
    
    # Run the tests
    results = tester.run_tests(styles=styles, max_workers=args.workers)
    
    # Print the summary
    tester.print_summary()
    
    # Save detailed results to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Detailed results saved to {args.output}")
        
    # Return success or failure
    return 0 if results["total_styles_failed"] == 0 else 1

if __name__ == '__main__':
    sys.exit(main())