"""
Simple test to demonstrate the XXL to 2XL size format conversion
"""

import logging
import sys
from color_mapper import color_mapper

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Test the size normalization functionality"""
    test_sizes = [
        "XS", "S", "M", "L", "XL", "XXL", "XXXL", "XXXXL",
        "2XL", "3XL", "4XL", "5XL", "6XL", 
        "SM", "MED", "LG", "XLG"
    ]
    
    logger.info("Size normalization test:")
    
    # Print a table of the normalizations
    logger.info(f"{'Original Size':<15} | {'Normalized Size':<15}")
    logger.info("-" * 35)
    
    for size in test_sizes:
        normalized = color_mapper.normalize_size(size)
        logger.info(f"{size:<15} | {normalized:<15}")
        
    # Check common problematic sizes specifically
    xxl = "XXL"
    normalized_xxl = color_mapper.normalize_size(xxl)
    logger.info(f"\nKey conversion: '{xxl}' -> '{normalized_xxl}'")
    
    xxxl = "XXXL"
    normalized_xxxl = color_mapper.normalize_size(xxxl)
    logger.info(f"Key conversion: '{xxxl}' -> '{normalized_xxxl}'")
    
    # Verify that already normalized sizes don't change
    already_normalized = "2XL"
    normalized_again = color_mapper.normalize_size(already_normalized)
    logger.info(f"Already normalized: '{already_normalized}' -> '{normalized_again}'")
    
    logger.info("\nTest complete!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())