#!/usr/bin/env python3
"""
Enhanced run script for SanMar Inventory App with performance optimizations
"""

import sys
import os
import logging
import time
from datetime import datetime
import signal
import threading

# Add current directory to path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("optimized_run")

# Import our performance optimizations
try:
    import performance_config
    from performance_optimizations import (
        timed_execution, cache_result, parallel_map,
        batch_process, retry, compressed_response
    )
    logger.info("Performance optimizations imported successfully")
except ImportError as e:
    logger.warning(f"Could not import performance optimizations: {e}")
    logger.warning("Continuing without performance optimizations")
except Exception as e:
    logger.error(f"Error importing performance optimizations: {e}")
    import traceback
    logger.error(traceback.format_exc())
    logger.warning("Continuing without performance optimizations")

def print_ascii_banner():
    """Print an ASCII art banner for the optimized server"""
    banner = """
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃                                                        ┃
    ┃    SANMAR INVENTORY APP - OPTIMIZED PERFORMANCE        ┃
    ┃                                                        ┃
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
    """
    print(banner)
    print(f"Server started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Performance optimizations: {'ENABLED' if 'timed_execution' in globals() else 'DISABLED'}")
    try:
        print(f"Cache timeout: {performance_config.CACHE_TIMEOUT} seconds")
        print(f"Max threads: {performance_config.MAX_THREADS}")
        print(f"Compression: {'ENABLED' if performance_config.ENABLE_COMPRESSION else 'DISABLED'}")
    except:
        pass
    print("\nPress Ctrl+C to stop the server\n")

def apply_performance_patches():
    """
    Dynamically apply performance optimizations to the main app
    This approach avoids modifying the original app.py file
    """
    if 'timed_execution' not in globals():
        logger.warning("Performance optimizations not available, skipping patches")
        return False

    try:
        import app
        
        # Apply caching to product_page function
        if hasattr(app, 'product_page') and callable(app.product_page):
            original_product_page = app.product_page
            app.product_page = timed_execution(app.product_page)
            logger.info("Applied performance optimization to product_page")
        
        # Apply caching to get_product_data function
        if hasattr(app, 'get_product_data') and callable(app.get_product_data):
            original_get_product_data = app.get_product_data
            app.get_product_data = cache_result(timeout=3600)(app.get_product_data)
            logger.info("Applied caching to get_product_data")
        
        # Apply caching to get_inventory function
        if hasattr(app, 'get_inventory') and callable(app.get_inventory):
            original_get_inventory = app.get_inventory
            app.get_inventory = cache_result(timeout=1800)(app.get_inventory)
            logger.info("Applied caching to get_inventory")
        
        # Apply retry logic to API calls
        if hasattr(app, 'fetch_pricing_by_type') and callable(app.fetch_pricing_by_type):
            original_fetch_pricing = app.fetch_pricing_by_type
            app.fetch_pricing_by_type = retry(max_attempts=3)(app.fetch_pricing_by_type)
            logger.info("Applied retry logic to fetch_pricing_by_type")
        
        # Apply response compression
        if hasattr(app, 'app') and hasattr(app.app, 'route'):
            # Find the product_page route
            for endpoint, view_func in app.app.view_functions.items():
                if endpoint == 'product_page':
                    app.app.view_functions['product_page'] = compressed_response(view_func)
                    logger.info("Applied response compression to product_page endpoint")
                    break
        
        logger.info("Performance patches applied successfully")
        return True
    except Exception as e:
        logger.error(f"Error applying performance patches: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def monitor_performance():
    """
    Background thread to monitor and log performance metrics
    This is a simplified version that doesn't require psutil
    """
    logger.info("Starting performance monitoring thread")
    
    while True:
        try:
            # Simple monitor that logs memory usage
            import gc
            gc.collect()  # Collect garbage to get more accurate readings
            
            # Log basic memory info
            logger.info(f"Memory objects: {len(gc.get_objects())}")
            
            # Sleep for monitoring interval
            time.sleep(30)  # Check every 30 seconds
        except Exception as e:
            logger.error(f"Error in performance monitoring: {e}")
            time.sleep(60)  # Wait longer after an error

def handle_signals():
    """Set up signal handlers for graceful shutdown"""
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal, cleaning up...")
        # Perform any cleanup needed
        logger.info("Server shutting down")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def main():
    """Main entry point for the optimized server"""
    print_ascii_banner()
    
    # Apply performance patches
    patched = apply_performance_patches()
    if not patched:
        logger.warning("Running without performance optimizations")
    
    # Set up signal handlers
    handle_signals()
    
    # Start performance monitoring in background thread
    monitor_thread = threading.Thread(target=monitor_performance)
    monitor_thread.daemon = True
    monitor_thread.start()
    logger.info("Performance monitoring started")
    
    # Import and run the app
    try:
        from app import app
        
        # Run the app with optimized settings
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True,
            use_reloader=False  # Disable reloader for better performance
        )
    except ImportError as e:
        logger.error(f"Could not import app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()