"""
Mock data for SanMar products, inventory, and pricing.
This is used as a fallback when the middleware API is unavailable.
"""

# Warehouse mapping for SanMar distribution centers
WAREHOUSES = {
    "1": "Seattle, WA", 
    "2": "Cincinnati, OH", 
    "3": "Dallas, TX", 
    "4": "Reno, NV",
    "5": "Robbinsville, NJ", 
    "6": "Jacksonville, FL", 
    "7": "Minneapolis, MN",
    "12": "Phoenix, AZ", 
    "31": "Richmond, VA"
}

# Mock product data with inventory and pricing
MOCK_PRODUCTS = {
    "C112": {
        "product": {
            "name": "Port Authority Core Blend Pique Polo",
            "description": "This budget-friendly essential combines the soft comfort of cotton with the durability of polyester. Features an extended tail for tucking, flat knit collar, three-button placket, dyed-to-match buttons, and side vents.",
            "colorName": "Black",
            "mainImage": "https://www.sanmar.com/products/catalog/2022/f1/port_authority/fullsize/C112_Black_Flat_2022.jpg",
            "colorImage": "https://www.sanmar.com/products/catalog/2022/f1/port_authority/fullsize/C112_Black_Flat_2022.jpg",
        },
        "colors": ["Black", "Navy", "White", "Red", "Royal", "Dark Green", "Steel Grey"],
        "sizes": ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL", "5XL", "6XL"],
        "inventory": {
            "warehouses": [
                {
                    "code": "1",
                    "quantities": [
                        {"size": "S", "quantity": 120},
                        {"size": "M", "quantity": 150},
                        {"size": "L", "quantity": 180},
                        {"size": "XL", "quantity": 200}
                    ]
                },
                {
                    "code": "2",
                    "quantities": [
                        {"size": "S", "quantity": 100},
                        {"size": "M", "quantity": 130},
                        {"size": "L", "quantity": 160},
                        {"size": "XL", "quantity": 180}
                    ]
                }
            ]
        },
        "pricing": {
            "originalPrice": 19.99,
            "salePrice": 15.99,
            "programPrice": 14.99,
            "caseSize": 36
        },
        "images": {
            "Black": "https://www.sanmar.com/products/catalog/2022/f1/port_authority/fullsize/C112_Black_Flat_2022.jpg",
            "Navy": "https://www.sanmar.com/products/catalog/2022/f1/port_authority/fullsize/C112_Navy_Flat_2022.jpg",
            "White": "https://www.sanmar.com/products/catalog/2022/f1/port_authority/fullsize/C112_White_Flat_2022.jpg",
            "Red": "https://www.sanmar.com/products/catalog/2022/f1/port_authority/fullsize/C112_Red_Flat_2022.jpg",
            "Royal": "https://www.sanmar.com/products/catalog/2022/f1/port_authority/fullsize/C112_Royal_Flat_2022.jpg",
            "Dark Green": "https://www.sanmar.com/products/catalog/2022/f1/port_authority/fullsize/C112_DarkGreen_Flat_2022.jpg",
            "Steel Grey": "https://www.sanmar.com/products/catalog/2022/f1/port_authority/fullsize/C112_SteelGrey_Flat_2022.jpg"
        }
    },
    
    "J790": {
        "product": {
            "name": "Port Authority Glacier Soft Shell Jacket",
            "description": "A versatile soft shell jacket with a clean, simple design. Perfect for corporate and outdoor activities.",
            "colorName": "Black",
            "mainImage": "https://www.sanmar.com/products/catalog/2022/f2/port_authority/fullsize/J790_Black_Flat_2022.jpg",
            "colorImage": "https://www.sanmar.com/products/catalog/2022/f2/port_authority/fullsize/J790_Black_Flat_2022.jpg",
        },
        "colors": ["Black", "Dress Blue Navy", "True Red", "Dark Smoke Grey", "Rich Green"],
        "sizes": ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"],
        "inventory": {
            "warehouses": [
                {
                    "code": "1",
                    "quantities": [
                        {"size": "S", "quantity": 45},
                        {"size": "M", "quantity": 60},
                        {"size": "L", "quantity": 75},
                        {"size": "XL", "quantity": 65}
                    ]
                },
                {
                    "code": "3",
                    "quantities": [
                        {"size": "S", "quantity": 50},
                        {"size": "M", "quantity": 65},
                        {"size": "L", "quantity": 80},
                        {"size": "XL", "quantity": 70}
                    ]
                }
            ]
        },
        "pricing": {
            "originalPrice": 49.99,
            "salePrice": 39.99,
            "programPrice": 36.99,
            "caseSize": 12
        },
        "images": {
            "Black": "https://www.sanmar.com/products/catalog/2022/f2/port_authority/fullsize/J790_Black_Flat_2022.jpg",
            "Dress Blue Navy": "https://www.sanmar.com/products/catalog/2022/f2/port_authority/fullsize/J790_DressBlueNavy_Flat_2022.jpg",
            "True Red": "https://www.sanmar.com/products/catalog/2022/f2/port_authority/fullsize/J790_TrueRed_Flat_2022.jpg",
            "Dark Smoke Grey": "https://www.sanmar.com/products/catalog/2022/f2/port_authority/fullsize/J790_DarkSmokeGrey_Flat_2022.jpg",
            "Rich Green": "https://www.sanmar.com/products/catalog/2022/f2/port_authority/fullsize/J790_RichGreen_Flat_2022.jpg"
        }
    },
    
    "PC61": {
        "product": {
            "name": "Port & Company Essential T-Shirt",
            "description": "A comfortable, everyday t-shirt that's perfect for screen printing and embroidery.",
            "colorName": "Black",
            "mainImage": "https://www.sanmar.com/products/catalog/2021/f2/port__company/fullsize/PC61_Black_Flat_2021.jpg",
            "colorImage": "https://www.sanmar.com/products/catalog/2021/f2/port__company/fullsize/PC61_Black_Flat_2021.jpg",
        },
        "colors": ["Black", "White", "Navy", "Red", "Royal", "Athletic Heather", "Dark Green"],
        "sizes": ["S", "M", "L", "XL", "2XL", "3XL", "4XL"],
        "inventory": {
            "warehouses": [
                {
                    "code": "1",
                    "quantities": [
                        {"size": "S", "quantity": 250},
                        {"size": "M", "quantity": 350},
                        {"size": "L", "quantity": 450},
                        {"size": "XL", "quantity": 400}
                    ]
                },
                {
                    "code": "4",
                    "quantities": [
                        {"size": "S", "quantity": 200},
                        {"size": "M", "quantity": 300},
                        {"size": "L", "quantity": 400},
                        {"size": "XL", "quantity": 350}
                    ]
                }
            ]
        },
        "pricing": {
            "originalPrice": 4.49,
            "salePrice": 3.59,
            "programPrice": 3.29,
            "caseSize": 72
        },
        "images": {
            "Black": "https://www.sanmar.com/products/catalog/2021/f2/port__company/fullsize/PC61_Black_Flat_2021.jpg",
            "White": "https://www.sanmar.com/products/catalog/2021/f2/port__company/fullsize/PC61_White_Flat_2021.jpg",
            "Navy": "https://www.sanmar.com/products/catalog/2021/f2/port__company/fullsize/PC61_Navy_Flat_2021.jpg",
            "Red": "https://www.sanmar.com/products/catalog/2021/f2/port__company/fullsize/PC61_Red_Flat_2021.jpg",
            "Royal": "https://www.sanmar.com/products/catalog/2021/f2/port__company/fullsize/PC61_Royal_Flat_2021.jpg",
            "Athletic Heather": "https://www.sanmar.com/products/catalog/2021/f2/port__company/fullsize/PC61_AthleticHeather_Flat_2021.jpg",
            "Dark Green": "https://www.sanmar.com/products/catalog/2021/f2/port__company/fullsize/PC61_DarkGreen_Flat_2021.jpg"
        }
    },
    
    "5000": {
        "product": {
            "name": "Gildan Heavy Cotton T-Shirt",
            "description": "A classic, heavyweight t-shirt perfect for everyday wear.",
            "colorName": "Black",
            "mainImage": "https://www.sanmar.com/products/catalog/2021/f1/gildan/fullsize/5000_Black_Flat_2021.jpg",
            "colorImage": "https://www.sanmar.com/products/catalog/2021/f1/gildan/fullsize/5000_Black_Flat_2021.jpg",
        },
        "colors": ["Black", "White", "Navy", "Red", "Royal", "Sport Grey", "Dark Heather"],
        "sizes": ["S", "M", "L", "XL", "2XL", "3XL"],
        "inventory": {
            "warehouses": [
                {
                    "code": "2",
                    "quantities": [
                        {"size": "S", "quantity": 280},
                        {"size": "M", "quantity": 380},
                        {"size": "L", "quantity": 480},
                        {"size": "XL", "quantity": 430}
                    ]
                },
                {
                    "code": "5",
                    "quantities": [
                        {"size": "S", "quantity": 230},
                        {"size": "M", "quantity": 330},
                        {"size": "L", "quantity": 430},
                        {"size": "XL", "quantity": 380}
                    ]
                }
            ]
        },
        "pricing": {
            "originalPrice": 3.99,
            "salePrice": 3.19,
            "programPrice": 2.99,
            "caseSize": 72
        },
        "images": {
            "Black": "https://www.sanmar.com/products/catalog/2021/f1/gildan/fullsize/5000_Black_Flat_2021.jpg",
            "White": "https://www.sanmar.com/products/catalog/2021/f1/gildan/fullsize/5000_White_Flat_2021.jpg",
            "Navy": "https://www.sanmar.com/products/catalog/2021/f1/gildan/fullsize/5000_Navy_Flat_2021.jpg",
            "Red": "https://www.sanmar.com/products/catalog/2021/f1/gildan/fullsize/5000_Red_Flat_2021.jpg",
            "Royal": "https://www.sanmar.com/products/catalog/2021/f1/gildan/fullsize/5000_Royal_Flat_2021.jpg",
            "Sport Grey": "https://www.sanmar.com/products/catalog/2021/f1/gildan/fullsize/5000_SportGrey_Flat_2021.jpg",
            "Dark Heather": "https://www.sanmar.com/products/catalog/2021/f1/gildan/fullsize/5000_DarkHeather_Flat_2021.jpg"
        }
    },
    
    "DT6000": {
        "product": {
            "name": "District Very Important Tee",
            "description": "A soft, comfortable tee with modern styling.",
            "colorName": "Black",
            "mainImage": "https://www.sanmar.com/products/catalog/2022/f1/district/fullsize/DT6000_Black_Flat_2022.jpg",
            "colorImage": "https://www.sanmar.com/products/catalog/2022/f1/district/fullsize/DT6000_Black_Flat_2022.jpg",
        },
        "colors": ["Black", "White", "Navy", "Red", "Blue", "Grey"],
        "sizes": ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"],
        "inventory": {
            "warehouses": [
                {
                    "code": "3",
                    "quantities": [
                        {"size": "S", "quantity": 120},
                        {"size": "M", "quantity": 160},
                        {"size": "L", "quantity": 200},
                        {"size": "XL", "quantity": 180}
                    ]
                },
                {
                    "code": "6",
                    "quantities": [
                        {"size": "S", "quantity": 110},
                        {"size": "M", "quantity": 150},
                        {"size": "L", "quantity": 190},
                        {"size": "XL", "quantity": 170}
                    ]
                }
            ]
        },
        "pricing": {
            "originalPrice": 5.99,
            "salePrice": 4.79,
            "programPrice": 4.49,
            "caseSize": 48
        },
        "images": {
            "Black": "https://www.sanmar.com/products/catalog/2022/f1/district/fullsize/DT6000_Black_Flat_2022.jpg",
            "White": "https://www.sanmar.com/products/catalog/2022/f1/district/fullsize/DT6000_White_Flat_2022.jpg",
            "Navy": "https://www.sanmar.com/products/catalog/2022/f1/district/fullsize/DT6000_Navy_Flat_2022.jpg",
            "Red": "https://www.sanmar.com/products/catalog/2022/f1/district/fullsize/DT6000_Red_Flat_2022.jpg",
            "Blue": "https://www.sanmar.com/products/catalog/2022/f1/district/fullsize/DT6000_Blue_Flat_2022.jpg",
            "Grey": "https://www.sanmar.com/products/catalog/2022/f1/district/fullsize/DT6000_Grey_Flat_2022.jpg"
        }
    },
    
    "ST850": {
        "product": {
            "name": "Sport-Tek PosiCharge Competitor Tee",
            "description": "A moisture-wicking, performance tee ideal for athletics and active wear.",
            "colorName": "Black",
            "mainImage": "https://www.sanmar.com/products/catalog/2022/f1/sport-tek/fullsize/ST850_Black_Flat_2022.jpg",
            "colorImage": "https://www.sanmar.com/products/catalog/2022/f1/sport-tek/fullsize/ST850_Black_Flat_2022.jpg",
        },
        "colors": ["Black", "White", "True Navy", "True Red", "True Royal", "Silver"],
        "sizes": ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"],
        "inventory": {
            "warehouses": [
                {
                    "code": "4",
                    "quantities": [
                        {"size": "S", "quantity": 90},
                        {"size": "M", "quantity": 120},
                        {"size": "L", "quantity": 150},
                        {"size": "XL", "quantity": 130}
                    ]
                },
                {
                    "code": "7",
                    "quantities": [
                        {"size": "S", "quantity": 80},
                        {"size": "M", "quantity": 110},
                        {"size": "L", "quantity": 140},
                        {"size": "XL", "quantity": 120}
                    ]
                }
            ]
        },
        "pricing": {
            "originalPrice": 7.99,
            "salePrice": 6.39,
            "programPrice": 5.99,
            "caseSize": 36
        },
        "images": {
            "Black": "https://www.sanmar.com/products/catalog/2022/f1/sport-tek/fullsize/ST850_Black_Flat_2022.jpg",
            "White": "https://www.sanmar.com/products/catalog/2022/f1/sport-tek/fullsize/ST850_White_Flat_2022.jpg",
            "True Navy": "https://www.sanmar.com/products/catalog/2022/f1/sport-tek/fullsize/ST850_TrueNavy_Flat_2022.jpg",
            "True Red": "https://www.sanmar.com/products/catalog/2022/f1/sport-tek/fullsize/ST850_TrueRed_Flat_2022.jpg",
            "True Royal": "https://www.sanmar.com/products/catalog/2022/f1/sport-tek/fullsize/ST850_TrueRoyal_Flat_2022.jpg",
            "Silver": "https://www.sanmar.com/products/catalog/2022/f1/sport-tek/fullsize/ST850_Silver_Flat_2022.jpg"
        }
    }
}

# Common style numbers for autocomplete fallback
COMMON_STYLES = ["PC61", "5000", "DT6000", "ST850", "K420", "G200", "BC3001", "PC850", "L223", "C112", "J790"]

# Map brands to their prefixes for color swatch URLs
BRAND_PREFIXES = {
    "PC": "port",  # Port & Company
    "K": "port",   # Port Authority
    "ST": "sport", # Sport-Tek
    "DT": "dist",  # District
    "G": "gildan", # Gildan
    "L": "port",   # Port Authority Ladies
    "J": "port",   # Port Authority Outerwear
    "TW": "port",  # Port Authority Tall
    "LW": "port",  # Port Authority Ladies Outerwear
    "BG": "port",  # Port Authority Bags
    "CP": "cp",    # CornerStone
    "CS": "cs",    # CornerStone
    "RH": "red",   # Red House
    "NKDC": "nike", # Nike
    "OGIO": "ogio", # OGIO
    "EB": "eb",    # Eddie Bauer
    "NF": "nf",    # North Face
    "": "port"     # Default to Port Authority
}

def get_color_swatch_url(style, color):
    """
    Get the URL for a color swatch from SanMar
    
    Args:
        style (str): The product style number
        color (str): The color name
        
    Returns:
        str: URL to the color swatch image
    """
    # Default to Port & Company if we can't determine the brand
    brand_prefix = "port"
    
    # Try to determine the brand prefix from the style number
    style = style.upper()
    for prefix, brand in BRAND_PREFIXES.items():
        if style.startswith(prefix):
            brand_prefix = brand
            break
    
    # Format the color for the URL
    color_formatted = color.lower().replace(" ", "_")
    
    # Return the full swatch URL
    # Example: https://cdnm.sanmar.com/swatch/gifs/port_black.gif
    return f"https://cdnm.sanmar.com/swatch/gifs/{brand_prefix}_{color_formatted}.gif"

def get_mock_data_for_style(style):
    """
    Get mock data for a given style number
    
    Args:
        style (str): The product style number
        
    Returns:
        dict: Mock data for the style or None if not found
    """
    style = style.upper()
    product_data = MOCK_PRODUCTS.get(style)
    
    # If product exists, add color swatch URLs
    if product_data:
        # Add swatch URLs for all colors
        product_data['color_swatches'] = {
            color: get_color_swatch_url(style, color) 
            for color in product_data.get('colors', [])
        }
    
    return product_data

def get_mock_autocomplete(query):
    """
    Get mock autocomplete suggestions for a style number prefix
    
    Args:
        query (str): The search query (style number prefix)
        
    Returns:
        list: List of matching style numbers
    """
    query = query.upper()
    if len(query) < 2:
        return []
        
    return [style for style in COMMON_STYLES if style.startswith(query)][:10]
