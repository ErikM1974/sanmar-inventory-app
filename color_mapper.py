"""
Color and Size mapping utilities for the SanMar Inventory App.
This module handles normalizing color and size formats from various sources.
"""

import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ColorMapper:
    """Class to handle color and size mapping/normalization"""

    def __init__(self):
        # Standard size mapping - convert API sizes to display sizes
        self.size_mapping = {
            # Convert Roman numeral sizes to numeric
            "XXL": "2XL",
            "XXXL": "3XL",
            "XXXXL": "4XL",
            "XXXXXL": "5XL",
            "XXXXXXL": "6XL",
            
            # Abbreviated sizes
            "SM": "S",
            "MED": "M",
            "LG": "L",
            "XLG": "XL",
            
            # Other common variations
            "4X": "4XL",
            "3X": "3XL",
            "2X": "2XL",
            "1X": "XL"
        }

        # Initialize color mapping dictionary (can be expanded as needed)
        self.color_mapping = {}

    def normalize_size(self, size):
        """
        Convert various size formats to a standardized notation
        Args:
            size (str): Size string to normalize
        Returns:
            str: Normalized size string
        """
        if size in self.size_mapping:
            return self.size_mapping[size]
        return size

    def map_color(self, color_name):
        """
        Map color names between different systems
        Args:
            color_name (str): Color name to map
        Returns:
            str: Mapped color name, or original if no mapping
        """
        if color_name in self.color_mapping:
            return self.color_mapping[color_name]
        return color_name


# Create a singleton instance for importing
color_mapper = ColorMapper()