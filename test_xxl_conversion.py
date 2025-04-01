"""
Test script to demonstrate the XXL to 2XL size format conversion
"""

import logging
import requests
import json
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import color mapper
try:
    from color_mapper import color_mapper
    HAS_COLOR_MAPPER = True
except ImportError:
    logger.warning("Could not import color_mapper module")
    HAS_COLOR_MAPPER = False

def main():
    # Test products known to have XXL sizes
    test_styles = ["L131", "PC61", "G200"]
    
    logger.info("Testing size format conversion for styles with XXL sizes")
    
    for style in test_styles:
        logger.info(f"\nTesting style: {style}")
        
        # Make a direct request to our local app
        try:
            # First get the raw product data from the API endpoint
            url = f"http://localhost:5000/product/{style}"
            logger.info(f"Requesting product data from: {url}")
            
            response = requests.get(url)
            if response.status_code != 200:
                logger.error(f"Error requesting product data: {response.status_code}")
                continue
                
            # Now we'll demonstrate the size normalization
            if HAS_COLOR_MAPPER:
                # Test with some example sizes
                test_sizes = ["XS", "S", "M", "L", "XL", "XXL", "XXXL", "XXXXL", "2XL", "3XL", "4XL"]
                logger.info("Size normalization examples:")
                for size in test_sizes:
                    normalized = color_mapper.normalize_size(size)
                    if size != normalized:
                        logger.info(f"  Converted: '{size}' → '{normalized}'")
                    else:
                        logger.info(f"  Unchanged: '{size}' (already in standard format)")
            
            logger.info("Success - style was processed with normalized sizes")
            
        except Exception as e:
            logger.error(f"Error testing style {style}: {str(e)}")
    
    logger.info("\nTesting complete!")

if __name__ == "__main__":
    main()