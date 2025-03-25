"""
Test script for the SanMar Pricing API implementation.
This script demonstrates how to use the get_pricing_for_color_swatch function
and verifies that it's working as expected.
"""

import os
import logging
import json
from datetime import datetime
from sanmar_pricing_api import get_pricing_for_color_swatch

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pricing_api():
    """Test the pricing API functionality."""
    print("=== SanMar Pricing API Test ===")
    
    # Test with style and color
    style = "PC61"
    color = "Black"
    print(f"\nTesting pricing for style={style}, color={color}")
    
    # Get pricing data
    result = get_pricing_for_color_swatch(style, color)
    
    # Check if there was an error
    if result.get("error", False):
        print(f"Error: {result.get('message', 'Unknown error')}")
    else:
        # Print the pricing data
        print("Pricing data retrieved successfully")
        print(f"Has sale: {result.get('meta', {}).get('has_sale', False)}")
        print(f"Sale period: {result.get('meta', {}).get('sale_start_date')} to {result.get('meta', {}).get('sale_end_date')}")
        
        # Print pricing for a specific size
        size = "L"
        print(f"\nPricing for size {size}:")
        print(f"Original price: ${result.get('original_price', {}).get(size, 'N/A')}")
        print(f"Sale price: ${result.get('sale_price', {}).get(size, 'N/A')}")
        print(f"Program price: ${result.get('program_price', {}).get(size, 'N/A')}")
        print(f"Case size: {result.get('case_size', {}).get(size, 'N/A')}")
        
        # Print all sizes
        print("\nAll sizes pricing:")
        for size in sorted(result.get("original_price", {})):
            original = result.get("original_price", {}).get(size, "N/A")
            sale = result.get("sale_price", {}).get(size, "N/A")
            program = result.get("program_price", {}).get(size, "N/A")
            case = result.get("case_size", {}).get(size, "N/A")
            print(f"Size {size}: Original=${original}, Sale=${sale}, Program=${program}, Case={case}")
    
    # Test with inventory key and size index
    print("\n\nTesting with inventoryKey and sizeIndex")
    inventory_key = "11803"  # Example inventory key for PC61 White S
    size_index = "2"         # Example size index for S
    
    print(f"Testing pricing for inventoryKey={inventory_key}, sizeIndex={size_index}")
    
    # Get pricing data
    result = get_pricing_for_color_swatch(None, None, None, inventory_key, size_index)
    
    # Check if there was an error
    if result.get("error", False):
        print(f"Error: {result.get('message', 'Unknown error')}")
    else:
        # Print a summary of the pricing data
        print("Pricing data retrieved successfully")
        print(f"Retrieved {len(result.get('original_price', {}))} size(s)")
        
        # Print all retrieved prices
        print("\nRetrieved pricing:")
        for size in sorted(result.get("original_price", {})):
            original = result.get("original_price", {}).get(size, "N/A")
            sale = result.get("sale_price", {}).get(size, "N/A")
            program = result.get("program_price", {}).get(size, "N/A")
            case = result.get("case_size", {}).get(size, "N/A")
            print(f"Size {size}: Original=${original}, Sale=${sale}, Program=${program}, Case={case}")

if __name__ == "__main__":
    test_pricing_api()