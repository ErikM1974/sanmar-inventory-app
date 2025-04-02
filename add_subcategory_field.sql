-- SQL script to add SUBCATEGORY_NAME field to the Products table in Caspio

-- Add the SUBCATEGORY_NAME field after the CATEGORY_NAME field
ALTER TABLE Products
ADD SUBCATEGORY_NAME VARCHAR(255) NULL;

-- Add a comment to the field
COMMENT ON COLUMN Products.SUBCATEGORY_NAME IS 'Subcategory name';

-- Update existing records with subcategory data from Sanmar_Bulk_251816_Feb2024 table
-- Note: This assumes the Sanmar_Bulk_251816_Feb2024 table is accessible
-- You may need to adjust this query based on your specific database structure
UPDATE Products p
SET SUBCATEGORY_NAME = s.SUBCATEGORY_NAME
FROM Sanmar_Bulk_251816_Feb2024 s
WHERE p.STYLE = s.STYLE
  AND p.COLOR_NAME = s.COLOR_NAME
  AND p.SIZE = s.SIZE;

-- Create an index on SUBCATEGORY_NAME for better query performance
CREATE INDEX idx_products_subcategory_name ON Products(SUBCATEGORY_NAME);