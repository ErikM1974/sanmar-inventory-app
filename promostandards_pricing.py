import logging
import zeep
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from zeep.transports import Transport
import os
from decimal import Decimal

# Set up logging
logger = logging.getLogger(__name__)

class PromoStandardsPricing:
    """
    Client for the PromoStandards Pricing and Configuration Service
    This provides standardized pricing that aligns with what's displayed on SanMar.com
    """
    
    def __init__(self, username, password, customer_number):
        """
        Initialize the PromoStandards Pricing client
        
        Args:
            username (str): SanMar API username
            password (str): SanMar API password
            customer_number (str): SanMar customer number
        """
        self.username = username
        self.password = password
        self.customer_number = customer_number
        
        # Configure retry strategy for API calls
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
        
        # Set up transport with retry strategy and timeout
        self.transport = Transport(timeout=30)
        self.transport.session.mount('https://', HTTPAdapter(max_retries=retry_strategy))
        
        # PromoStandards Pricing WSDL URL - use EDEV for testing, WS for production
        self.wsdl_url = "https://ws.sanmar.com:8080/promostandards/PricingAndConfigurationServiceBinding?WSDL"
        
        try:
            # Initialize SOAP client
            self.client = zeep.Client(wsdl=self.wsdl_url, transport=self.transport)
            logger.info("Successfully initialized PromoStandards Pricing Service client")
            self._ready = True
        except Exception as e:
            logger.error(f"Error initializing PromoStandards Pricing client: {str(e)}")
            self._ready = False
    
    def is_ready(self):
        """Check if the client is initialized and ready to use."""
        return self._ready
    
    def get_pricing(self, style, color=None, fob_id="1", price_type="Net"):
        """
        Fetch pricing data from PromoStandards Pricing and Configuration Service
        
        Args:
            style (str): Product style number (e.g., "PC61")
            color (str, optional): Color name
            fob_id (str, optional): FOB/warehouse ID (default: "1" for Seattle)
            price_type (str, optional): Price type ("Net" for distributor, "List" for MSRP, "Customer" for special pricing)
        
        Returns:
            dict: Pricing data for the specified product or None if error
        """
        if not self._ready:
            logger.error("PromoStandards Pricing client not initialized")
            return None
        
        request_data = {
            "wsVersion": "1.0.0",
            "id": self.username,
            "password": self.password,
            "productId": style,
            "currency": "USD",
            "fobId": fob_id,
            "priceType": price_type,
            "localizationCountry": "US",
            "localizationLanguage": "EN",
            "configurationType": "Blank"
        }
        
        try:
            logger.info(f"Requesting PromoStandards pricing for style: {style}, type: {price_type}")
            response = self.client.service.getConfigurationAndPricing(**request_data)
            return self._process_pricing_response(response, style, color)
        except Exception as e:
            logger.error(f"Error fetching PromoStandards pricing: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def _process_pricing_response(self, response, style, color=None):
        """
        Process the pricing response from PromoStandards service
        
        Args:
            response: SOAP response object
            style (str): Product style number
            color (str, optional): Color name
            
        Returns:
            dict: Processed pricing data
        """
        pricing_data = {
            "original_price": {},
            "sale_price": {},
            "program_price": {},
            "case_size": {},
            "color_pricing": {}
        }
        
        if not response or not hasattr(response, 'Configuration') or not hasattr(response.Configuration, 'PartArray'):
            logger.warning(f"Invalid or empty response for style: {style}")
            return pricing_data
        
        logger.info(f"Processing PromoStandards pricing response for style: {style}")
        
        try:
            # Process each part (different SKUs - style/color/size combinations)
            for part in response.Configuration.PartArray:
                if not hasattr(part, 'partId') or not hasattr(part, 'PartPriceArray'):
                    continue
                
                part_id = part.partId  # SKU identifier (e.g., "PC61BK-M" for Black Medium)
                logger.debug(f"Processing part ID: {part_id}")
                
                # Extract color and size from part ID or description
                part_color, part_size = self._extract_color_size_from_part_id(part_id, part)
                
                # Create a nested structure for each color if not exists
                if part_color and part_color not in pricing_data["color_pricing"]:
                    pricing_data["color_pricing"][part_color] = {
                        "original_price": {},
                        "sale_price": {},
                        "program_price": {},
                        "case_size": {}
                    }
                
                # Process pricing information for this part
                if hasattr(part, 'PartPriceArray') and part.PartPriceArray:
                    for price in part.PartPriceArray:
                        if not hasattr(price, 'price') or not hasattr(price, 'minQuantity'):
                            continue
                        
                        # Get the price value as a float
                        price_value = float(price.price) if hasattr(price, 'price') else 0.0
                        
                        # Only process if we have a valid size and price
                        if part_size and price_value > 0:
                            # Add to general pricing
                            if price.minQuantity == 1:  # Single unit price
                                pricing_data["original_price"][part_size] = price_value
                                pricing_data["sale_price"][part_size] = price_value
                                pricing_data["program_price"][part_size] = price_value
                                
                                # Get case size if available or use defaults
                                case_size = self._get_case_size(style, part, part_size)
                                pricing_data["case_size"][part_size] = case_size
                                
                                # Add to color-specific pricing if color is available
                                if part_color:
                                    # Make sure this color exists in the pricing data
                                    if part_color not in pricing_data["color_pricing"]:
                                        pricing_data["color_pricing"][part_color] = {
                                            "original_price": {},
                                            "sale_price": {},
                                            "program_price": {},
                                            "case_size": {}
                                        }
                                        
                                    # Add pricing data for this specific color
                                    pricing_data["color_pricing"][part_color]["original_price"][part_size] = price_value
                                    pricing_data["color_pricing"][part_color]["sale_price"][part_size] = price_value
                                    pricing_data["color_pricing"][part_color]["program_price"][part_size] = price_value
                                    pricing_data["color_pricing"][part_color]["case_size"][part_size] = case_size
                                    
                                    logger.info(f"Using piecePrice: {price_value}")
                                    logger.info(f"Added pricing for size {part_size}: original={price_value}, sale={price_value}, program={price_value}, case={case_size}")
                                    
                                logger.info(f"Added pricing for {part_id}: {price_value} (size: {part_size}, color: {part_color})")
                                break  # Use first price for minQuantity=1
            
            return pricing_data
            
        except Exception as e:
            logger.error(f"Error processing PromoStandards pricing response: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return pricing_data
    
    def _extract_color_size_from_part_id(self, part_id, part):
        """
        Extract color and size information from part ID or part description
        
        Args:
            part_id (str): The part ID (SKU)
            part: The part object from the response
            
        Returns:
            tuple: (color, size) or (None, None) if not found
        """
        # Check if we have explicit color and size attributes
        if hasattr(part, 'color') and hasattr(part, 'size'):
            return part.color, part.size
        
        # For SanMar, try to parse from description or partId
        # Example formats: "PC61BK-M" for Black Medium, or "Port Authority PC61 Tee - Black - Medium"
        color = None
        size = None
        
        # Try to extract from description
        if hasattr(part, 'partDescription'):
            desc = part.partDescription
            # Look for common size patterns at the end of description
            for size_pattern in ['- XS', '- S', '- M', '- L', '- XL', '- 2XL', '- 3XL', '- 4XL', '- 5XL', '- OSFA']:
                if desc.endswith(size_pattern):
                    size = size_pattern.replace('- ', '')
                    # Then look for color before the size
                    color_section = desc.rsplit(' - ', 2)
                    if len(color_section) >= 2:
                        color = color_section[-2]
                    break
        
        # If not found in description, try parsing from part_id
        if not color or not size:
            # Common SanMar format: STYLE+COLOR_CODE+SIZE_CODE
            # Try some pattern matching based on common SanMar SKU formats
            if '-' in part_id:
                # Format like "PC61BK-M"
                style_color, size = part_id.rsplit('-', 1)
                if hasattr(part, 'productId') and style_color.upper().startswith(part.productId.upper()):
                    # Extract color code
                    color_code = style_color[len(part.productId):]
                    # Map color code to full color name if needed
                    # This is a simplified example and may need enhancement
                    color_map = {
                        'BK': 'Black',
                        'NV': 'Navy',
                        'RD': 'Red',
                        'WH': 'White',
                        'GR': 'Gray',
                        'KH': 'Khaki',
                        # Add more mappings as needed
                    }
                    color = color_map.get(color_code.upper(), color_code)
        
        logger.debug(f"Extracted color: '{color}', size: '{size}' from part ID: {part_id}")
        return color, size
    
    def _get_case_size(self, style, part, size):
        """
        Determine the case size based on style, part info, and size
        
        Args:
            style (str): Product style
            part: Part object
            size (str): Size code
            
        Returns:
            int: Case size
        """
        # Try to get case size from part info
        if hasattr(part, 'caseSize'):
            return int(part.caseSize)
        
        # Default case sizes based on style and size
        style = style.upper()
        default_case_size = 24  # Default fallback
        
        if style.startswith('PC61'):
            if size in ['XS', 'S', 'M', 'L', 'XL']:
                return 72
            else:  # 2XL and up
                return 36
        elif style.startswith('J790'):
            if size in ['XS', 'S', 'M', 'L', 'XL', '2XL']:
                return 24
            else:  # 3XL and up
                return 12
        elif style == 'C112':
            return 144  # Special case for caps
        
        return default_case_size
    
    def get_comprehensive_pricing(self, style, product_data):
        """
        Get comprehensive pricing for a style using multiple price types
        
        Args:
            style (str): Product style number
            product_data (dict): Product data containing part_id_map
            
        Returns:
            dict: Comprehensive pricing data with original, sale, and program prices
        """
        # Initialize the pricing data structure
        pricing_data = {
            "original_price": {},
            "sale_price": {},
            "program_price": {},
            "case_size": {},
            "color_pricing": {}
        }
        
        # Get the List pricing (MSRP/original price)
        list_pricing = self.get_pricing(style, price_type="List")
        if list_pricing:
            # Merge the original prices
            self._merge_prices(pricing_data, list_pricing, "original_price")
            # Initialize color pricing structure if needed
            for color in list_pricing.get("color_pricing", {}):
                if color not in pricing_data["color_pricing"]:
                    pricing_data["color_pricing"][color] = {
                        "original_price": {},
                        "sale_price": {},
                        "program_price": {},
                        "case_size": {}
                    }
                # Merge color-specific original prices
                if "original_price" in list_pricing["color_pricing"][color]:
                    pricing_data["color_pricing"][color]["original_price"] = list_pricing["color_pricing"][color]["original_price"]
                    # Also copy case sizes
                    if "case_size" in list_pricing["color_pricing"][color]:
                        pricing_data["color_pricing"][color]["case_size"] = list_pricing["color_pricing"][color]["case_size"]
            
            # Copy case sizes from list pricing
            if "case_size" in list_pricing:
                pricing_data["case_size"] = list_pricing["case_size"]
        
        # Get the Net pricing (distributor cost/sale price)
        net_pricing = self.get_pricing(style, price_type="Net")
        if net_pricing:
            # Merge the sale prices
            self._merge_prices(pricing_data, net_pricing, "sale_price")
            # Also use as program prices as a fallback
            self._merge_prices(pricing_data, net_pricing, "program_price")
            
            # Process color-specific pricing
            for color in net_pricing.get("color_pricing", {}):
                if color not in pricing_data["color_pricing"]:
                    pricing_data["color_pricing"][color] = {
                        "original_price": {},
                        "sale_price": {},
                        "program_price": {},
                        "case_size": {}
                    }
                # Merge color-specific sale prices
                if "sale_price" in net_pricing["color_pricing"][color]:
                    pricing_data["color_pricing"][color]["sale_price"] = net_pricing["color_pricing"][color]["sale_price"]
                # Use as program prices as fallback
                if "sale_price" in net_pricing["color_pricing"][color]:
                    pricing_data["color_pricing"][color]["program_price"] = net_pricing["color_pricing"][color]["sale_price"]
        
        # Get Customer pricing if available (specific contract pricing)
        customer_pricing = self.get_pricing(style, price_type="Customer")
        if customer_pricing:
            # Merge the program prices
            self._merge_prices(pricing_data, customer_pricing, "program_price")
            
            # Process color-specific pricing
            for color in customer_pricing.get("color_pricing", {}):
                if color not in pricing_data["color_pricing"]:
                    pricing_data["color_pricing"][color] = {
                        "original_price": {},
                        "sale_price": {},
                        "program_price": {},
                        "case_size": {}
                    }
                # Merge color-specific program prices
                if "program_price" in customer_pricing["color_pricing"][color]:
                    pricing_data["color_pricing"][color]["program_price"] = customer_pricing["color_pricing"][color]["program_price"]
        
        # Handle any missing data with fallbacks
        self._ensure_complete_pricing(pricing_data)
        
        # Create color mapping for variant names of same color
        self._map_color_variants(pricing_data, product_data)
        
        return pricing_data
    
    def _merge_prices(self, target, source, price_type):
        """
        Merge price data from source to target for the given price type
        
        Args:
            target (dict): Target pricing data structure
            source (dict): Source pricing data structure
            price_type (str): The price type to merge (original_price, sale_price, program_price)
        """
        if price_type in source and source[price_type]:
            # If target doesn't have this price type yet, or it's empty, use the source
            if price_type not in target or not target[price_type]:
                target[price_type] = source[price_type]
            else:
                # Otherwise merge individual sizes
                for size, price in source[price_type].items():
                    if price > 0:  # Only use valid prices
                        target[price_type][size] = price
    
    def _ensure_complete_pricing(self, pricing_data):
        """
        Ensure all price types have data, using fallbacks if needed
        
        Args:
            pricing_data (dict): Pricing data structure to validate and complete
        """
        # Handle fallbacks for main pricing
        if "original_price" in pricing_data and pricing_data["original_price"]:
            # If we have original price but no sale price, use original as sale
            if "sale_price" not in pricing_data or not pricing_data["sale_price"]:
                pricing_data["sale_price"] = pricing_data["original_price"].copy()
            # If we have original price but no program price, use sale as program
            if "program_price" not in pricing_data or not pricing_data["program_price"]:
                pricing_data["program_price"] = pricing_data["sale_price"].copy()
        
        # Do the same for color-specific pricing
        for color in pricing_data.get("color_pricing", {}):
            color_prices = pricing_data["color_pricing"][color]
            
            # If we have original price but no sale price, use original as sale
            if "original_price" in color_prices and color_prices["original_price"]:
                if "sale_price" not in color_prices or not color_prices["sale_price"]:
                    color_prices["sale_price"] = color_prices["original_price"].copy()
                # If we have original price but no program price, use sale as program
                if "program_price" not in color_prices or not color_prices["program_price"]:
                    color_prices["program_price"] = color_prices["sale_price"].copy()
    
    def _map_color_variants(self, pricing_data, product_data):
        """
        Create mappings for different variants of the same color name
        
        Args:
            pricing_data (dict): Pricing data structure
            product_data (dict): Product data containing part_id_map
        """
        # Get catalog colors from product data
        catalog_colors = []
        if product_data and 'part_id_map' in product_data:
            catalog_colors = list(product_data['part_id_map'].keys())
        
        logger.info(f"_map_color_variants processing {len(catalog_colors)} catalog colors")
        logger.info(f"Initial color_pricing keys: {list(pricing_data['color_pricing'].keys())}")
        
        # Create a mapping from variations to the catalog color
        color_mapping = {}
        for catalog_color in catalog_colors:
            # Direct mapping
            color_mapping[catalog_color] = catalog_color
            
            # Add case variations
            color_mapping[catalog_color.upper()] = catalog_color
            color_mapping[catalog_color.lower()] = catalog_color
            color_mapping[catalog_color.title()] = catalog_color
            
            # Add variations with spaces and slashes
            if '/' in catalog_color:
                base_color = catalog_color.split('/')[0].strip()
                accent = catalog_color.split('/')[1].strip()
                
                color_mapping[f"{base_color}/{accent}"] = catalog_color
                color_mapping[f"{base_color}/ {accent}"] = catalog_color
                color_mapping[f"{base_color} {accent}"] = catalog_color
                color_mapping[f"{base_color} / {accent}"] = catalog_color
                
                # Add common variations
                if base_color == "Smk Gry" or base_color == "Smk":
                    color_mapping[f"Smoke {accent}"] = catalog_color
                    color_mapping[f"Smoke/ {accent}"] = catalog_color
                    color_mapping[f"Smoke/{accent}"] = catalog_color
                    color_mapping[f"Smoke Grey/{accent}"] = catalog_color
                    color_mapping[f"Smoke Grey/ {accent}"] = catalog_color
                    color_mapping[f"Smoke Gray/{accent}"] = catalog_color
                    color_mapping[f"Smoke Gray/ {accent}"] = catalog_color
                elif base_color == "AtlBlue":
                    color_mapping[f"Atlantic Blue/{accent}"] = catalog_color
                    color_mapping[f"Atlantic Blue/ {accent}"] = catalog_color
                    color_mapping[f"AtlanticBlue/{accent}"] = catalog_color
        
        # Initialize color-specific pricing for catalog colors if missing
        for catalog_color in catalog_colors:
            if catalog_color not in pricing_data["color_pricing"]:
                pricing_data["color_pricing"][catalog_color] = {
                    "original_price": {},
                    "sale_price": {},
                    "program_price": {},
                    "case_size": {}
                }
        
        # Apply color mapping to ensure we have pricing for all catalog colors
        # even if the API returned it under a variant name
        logger.info(f"Before color mapping, color_pricing keys: {list(pricing_data['color_pricing'].keys())}")
        color_pricing_copy = pricing_data["color_pricing"].copy()
        for variant_color, pricing in color_pricing_copy.items():
            # Find catalog color for this variant
            for color_variant, catalog_color in color_mapping.items():
                if variant_color == color_variant and variant_color != catalog_color:
                    # This is a variant name, ensure the catalog color has this pricing
                    logger.info(f"Mapping variant '{variant_color}' to catalog color '{catalog_color}'")
                    if catalog_color not in pricing_data["color_pricing"]:
                        pricing_data["color_pricing"][catalog_color] = pricing
                        logger.info(f"Added pricing for catalog color '{catalog_color}' from variant '{variant_color}'")
                    else:
                        # Merge with existing pricing data for catalog color
                        for price_type in ["original_price", "sale_price", "program_price", "case_size"]:
                            if price_type in pricing and pricing[price_type]:
                                if price_type not in pricing_data["color_pricing"][catalog_color]:
                                    pricing_data["color_pricing"][catalog_color][price_type] = {}
                                for size, value in pricing[price_type].items():
                                    pricing_data["color_pricing"][catalog_color][price_type][size] = value
                                    logger.info(f"Updated {price_type} for '{catalog_color}' size '{size}' to {value} from variant '{variant_color}'")
        
        # If any catalog colors are still missing pricing, use the general pricing as fallback
        for catalog_color in catalog_colors:
            if catalog_color not in pricing_data["color_pricing"]:
                pricing_data["color_pricing"][catalog_color] = {
                    "original_price": {},
                    "sale_price": {},
                    "program_price": {},
                    "case_size": {}
                }
                
            # Ensure each color has all pricing and case size data
            if not pricing_data["color_pricing"][catalog_color].get("original_price"):
                pricing_data["color_pricing"][catalog_color]["original_price"] = pricing_data["original_price"].copy()
            if not pricing_data["color_pricing"][catalog_color].get("sale_price"):
                pricing_data["color_pricing"][catalog_color]["sale_price"] = pricing_data["sale_price"].copy()
            if not pricing_data["color_pricing"][catalog_color].get("program_price"):
                pricing_data["color_pricing"][catalog_color]["program_price"] = pricing_data["program_price"].copy()
            if not pricing_data["color_pricing"][catalog_color].get("case_size"):
                pricing_data["color_pricing"][catalog_color]["case_size"] = pricing_data["case_size"].copy()
                
        logger.info(f"Final color_pricing keys after fallback: {list(pricing_data['color_pricing'].keys())}")