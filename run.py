"""
Simple script to run the Flask app directly with Python
No need to use the 'flask' command which can sometimes cause issues
"""
from app import app
import os
import logging
from sanmar_inventory import get_inventory_by_style

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    print("Starting SanMar Inventory App...")
    print("Open http://localhost:5000 in your browser")
    
    # Test inventory access for J790
    logger.info("------ TESTING DIRECT INVENTORY ACCESS for J790 ------")
    try:
        inventory_result = get_inventory_by_style('J790')
        if isinstance(inventory_result, tuple) and len(inventory_result) == 2:
            inventory_data, timestamp = inventory_result
            logger.info(f"Successfully retrieved inventory data with timestamp {timestamp}")
        else:
            inventory_data = inventory_result
            logger.info("Successfully retrieved inventory data (not in tuple format)")
            
        # Log inventory structure
        logger.info(f"Inventory data type: {type(inventory_data)}")
        if isinstance(inventory_data, dict):
            logger.info(f"Inventory data contains {len(inventory_data)} colors")
            for color, color_data in inventory_data.items():
                logger.info(f"Color: {color}")
                logger.info(f"Sizes for {color}: {list(color_data.keys()) if isinstance(color_data, dict) else 'No sizes'}")
                
                if isinstance(color_data, dict):
                    for size, size_data in color_data.items():
                        logger.info(f"  Size: {size}")
                        if isinstance(size_data, dict) and 'warehouses' in size_data:
                            logger.info(f"    Warehouses: {size_data['warehouses']}")
                            logger.info(f"    Total: {size_data.get('total', 'N/A')}")
    except Exception as e:
        logger.error(f"Error testing inventory access: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
