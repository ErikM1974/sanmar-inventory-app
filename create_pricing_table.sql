-- SQL script to create the Pricing table in Caspio

-- Create the Pricing table
CREATE TABLE Pricing (
    PRICING_ID INT IDENTITY(1,1) PRIMARY KEY,
    STYLE VARCHAR(255) NOT NULL,
    COLOR_NAME VARCHAR(255) NOT NULL,
    SIZE VARCHAR(255) NOT NULL,
    PIECE_PRICE MONEY NOT NULL,
    CASE_PRICE MONEY NOT NULL,
    CASE_SIZE INT NOT NULL,
    PROGRAM_PRICE MONEY NOT NULL,
    LAST_UPDATED DATETIME NOT NULL
);

-- Add comments to the fields
COMMENT ON COLUMN Pricing.PRICING_ID IS 'Primary key';
COMMENT ON COLUMN Pricing.STYLE IS 'SanMar style number';
COMMENT ON COLUMN Pricing.COLOR_NAME IS 'Color name';
COMMENT ON COLUMN Pricing.SIZE IS 'Size name';
COMMENT ON COLUMN Pricing.PIECE_PRICE IS 'Regular price per piece';
COMMENT ON COLUMN Pricing.CASE_PRICE IS 'Price per case';
COMMENT ON COLUMN Pricing.CASE_SIZE IS 'Number of pieces in a case';
COMMENT ON COLUMN Pricing.PROGRAM_PRICE IS 'Special program pricing';
COMMENT ON COLUMN Pricing.LAST_UPDATED IS 'Last update timestamp';

-- Create indexes for better query performance
CREATE INDEX idx_pricing_style ON Pricing(STYLE);
CREATE INDEX idx_pricing_style_color_size ON Pricing(STYLE, COLOR_NAME, SIZE);
CREATE INDEX idx_pricing_last_updated ON Pricing(LAST_UPDATED);

-- Create a unique constraint to ensure no duplicate entries
ALTER TABLE Pricing
ADD CONSTRAINT uq_pricing_style_color_size UNIQUE (STYLE, COLOR_NAME, SIZE);