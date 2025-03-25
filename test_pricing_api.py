"""
Test script to verify the SanMar pricing API functionality
Specifically checking PC61 Cardinal color pricing
"""
import os
import sys
import logging
import json
from dotenv import load_dotenv
from sanmar_pricing_api import get_pricing_for_color_swatch

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_pc61_cardinal_pricing():
    """Test PC61 Cardinal pricing to verify it matches SanMar.com values"""
    logger.info("Testing PC61 Cardinal pricing...")
    
    # Get pricing data for PC61 in Cardinal color
    pricing_data = get_pricing_for_color_swatch("PC61", "Cardinal")
    
    # Print the full pricing data for inspection
    logger.info(f"Pricing data: {json.dumps(pricing_data, indent=2)}")
    
    # Verify key pricing values
    # For S-XL sizes
    for size in ["S", "M", "L", "XL"]:
        if (
            pricing_data["original_price"].get(size) == 3.41 and
            pricing_data["sale_price"].get(size) == 2.72 and
            pricing_data["program_price"].get(size) == 2.18 and
            pricing_data["case_size"].get(size) == 72
        ):
            logger.info(f"✓ Size {size} pricing is correct")
        else:
            logger.error(f"✗ Size {size} pricing is incorrect")
            logger.error(f"  Expected: original=3.41, sale=2.72, program=2.18, case=72")
            logger.error(f"  Got: original={pricing_data['original_price'].get(size)}, sale={pricing_data['sale_price'].get(size)}, program={pricing_data['program_price'].get(size)}, case={pricing_data['case_size'].get(size)}")
    
    # For 2XL size
    if (
        pricing_data["original_price"].get("2XL") == 4.53 and
        pricing_data["sale_price"].get("2XL") == 3.63 and
        pricing_data["program_price"].get("2XL") == 3.63 and
        pricing_data["case_size"].get("2XL") == 36
    ):
        logger.info("✓ Size 2XL pricing is correct")
    else:
        logger.error("✗ Size 2XL pricing is incorrect")
        logger.error(f"  Expected: original=4.53, sale=3.63, program=3.63, case=36")
        logger.error(f"  Got: original={pricing_data['original_price'].get('2XL')}, sale={pricing_data['sale_price'].get('2XL')}, program={pricing_data['program_price'].get('2XL')}, case={pricing_data['case_size'].get('2XL')}")
    
    # For 3XL-6XL sizes
    for size in ["3XL", "4XL", "5XL", "6XL"]:
        if (
            pricing_data["original_price"].get(size) == 4.96 and
            pricing_data["sale_price"].get(size) == 3.97 and
            pricing_data["program_price"].get(size) == 3.97 and
            pricing_data["case_size"].get(size) == 36
        ):
            logger.info(f"✓ Size {size} pricing is correct")
        else:
            logger.error(f"✗ Size {size} pricing is incorrect")
            logger.error(f"  Expected: original=4.96, sale=3.97, program=3.97, case=36")
            logger.error(f"  Got: original={pricing_data['original_price'].get(size)}, sale={pricing_data['sale_price'].get(size)}, program={pricing_data['program_price'].get(size)}, case={pricing_data['case_size'].get(size)}")

if __name__ == "__main__":
    test_pc61_cardinal_pricing()