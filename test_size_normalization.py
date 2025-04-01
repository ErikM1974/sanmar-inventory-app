"""
Test script for size normalization functionality in the ColorMapper class
"""

import logging
import json
from color_mapper import color_mapper

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_size_normalization():
    """Test the size normalization functionality"""
    # Create test data with different size formats
    test_inventory = {
        "Black": {
            "XXL": "123456",
            "XXXL": "123457",
            "4X": "123458",
            "SM": "123459",
            "XLG": "123460",
            "LG": "123461",
            "MED": "123462"
        },
        "Navy": {
            "XS": "234567",
            "S": "234568", 
            "M": "234569",
            "L": "234570",
            "XL": "234571",
            "2XL": "234572",
            "3XL": "234573"
        }
    }
    
    logger.info("Original inventory data:")
    logger.info(json.dumps(test_inventory, indent=2))
    
    # Create normalized inventory data
    normalized_inventory = {}
    for color, sizes in test_inventory.items():
        normalized_sizes = {}
        
        # Process each size
        for size, part_id in sizes.items():
            # Normalize the size notation
            normalized_size = color_mapper.normalize_size(size)
            
            # Add to normalized dictionary
            normalized_sizes[normalized_size] = part_id
            
            # If size changed, log it
            if normalized_size != size:
                logger.info(f"Normalized size '{size}' to '{normalized_size}' for color {color}")
        
        # Replace sizes with normalized version
        normalized_inventory[color] = normalized_sizes
    
    logger.info("Normalized inventory data:")
    logger.info(json.dumps(normalized_inventory, indent=2))
    
    # Verify specific normalizations
    assert "2XL" in normalized_inventory["Black"], "XXL should be normalized to 2XL"
    assert "3XL" in normalized_inventory["Black"], "XXXL should be normalized to 3XL"
    assert "4XL" in normalized_inventory["Black"], "4X should be normalized to 4XL"
    assert "S" in normalized_inventory["Black"], "SM should be normalized to S"
    assert "XL" in normalized_inventory["Black"], "XLG should be normalized to XL"
    assert "L" in normalized_inventory["Black"], "LG should be normalized to L"
    assert "M" in normalized_inventory["Black"], "MED should be normalized to M"
    
    # Check that standardized sizes remain the same
    assert normalized_inventory["Navy"] == test_inventory["Navy"], "Already standardized sizes should not change"
    
    logger.info("All tests passed!")

if __name__ == "__main__":
    test_size_normalization()