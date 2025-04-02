-- Products Table
CREATE TABLE Products (
    PRODUCT_ID INT IDENTITY(1,1) PRIMARY KEY,
    STYLE NVARCHAR(50) NOT NULL,
    PRODUCT_TITLE NVARCHAR(255) NOT NULL,
    CATEGORY_NAME NVARCHAR(100) NOT NULL,
    COLOR_NAME NVARCHAR(100) NOT NULL,
    SIZE NVARCHAR(20) NOT NULL,
    SIZE_INDEX INT NOT NULL DEFAULT 0,
    BRAND_NAME NVARCHAR(100) NOT NULL,
    BRAND_LOGO_IMAGE NVARCHAR(255) NULL,
    PRODUCT_IMAGE_URL NVARCHAR(255) NULL,
    COLOR_SQUARE_IMAGE NVARCHAR(255) NULL,
    PRICE MONEY NOT NULL DEFAULT 0,
    PIECE_PRICE MONEY NOT NULL DEFAULT 0,
    CASE_PRICE MONEY NOT NULL DEFAULT 0,
    CASE_SIZE INT NOT NULL DEFAULT 1,
    KEYWORDS NVARCHAR(1000) NULL
);

-- Add indexes for faster lookups
CREATE INDEX IDX_STYLE ON Products (STYLE);
CREATE INDEX IDX_CATEGORY_NAME ON Products (CATEGORY_NAME);
CREATE INDEX IDX_COLOR_NAME ON Products (COLOR_NAME);
CREATE INDEX IDX_SIZE ON Products (SIZE);
CREATE INDEX IDX_BRAND_NAME ON Products (BRAND_NAME);

-- Sample data for Products table
INSERT INTO Products (
    STYLE, PRODUCT_TITLE, CATEGORY_NAME, COLOR_NAME, SIZE, SIZE_INDEX,
    BRAND_NAME, BRAND_LOGO_IMAGE, PRODUCT_IMAGE_URL, COLOR_SQUARE_IMAGE,
    PRICE, PIECE_PRICE, CASE_PRICE, CASE_SIZE, KEYWORDS
)
VALUES (
    'PC61', 'Port & Company Essential T-Shirt', 'T-Shirts', 'White', 'S', 1,
    'Port & Company', 'https://www.sanmar.com/brands/port-company/logo.png',
    'https://www.sanmar.com/products/PC61/white_flat_front.jpg',
    'https://www.sanmar.com/colors/PC61/white_square.jpg',
    5.99, 5.49, 59.90, 12, 'tshirt, t-shirt, essential, basic, cotton'
);

INSERT INTO Products (
    STYLE, PRODUCT_TITLE, CATEGORY_NAME, COLOR_NAME, SIZE, SIZE_INDEX,
    BRAND_NAME, BRAND_LOGO_IMAGE, PRODUCT_IMAGE_URL, COLOR_SQUARE_IMAGE,
    PRICE, PIECE_PRICE, CASE_PRICE, CASE_SIZE, KEYWORDS
)
VALUES (
    'PC61', 'Port & Company Essential T-Shirt', 'T-Shirts', 'White', 'M', 2,
    'Port & Company', 'https://www.sanmar.com/brands/port-company/logo.png',
    'https://www.sanmar.com/products/PC61/white_flat_front.jpg',
    'https://www.sanmar.com/colors/PC61/white_square.jpg',
    5.99, 5.49, 59.90, 12, 'tshirt, t-shirt, essential, basic, cotton'
);

INSERT INTO Products (
    STYLE, PRODUCT_TITLE, CATEGORY_NAME, COLOR_NAME, SIZE, SIZE_INDEX,
    BRAND_NAME, BRAND_LOGO_IMAGE, PRODUCT_IMAGE_URL, COLOR_SQUARE_IMAGE,
    PRICE, PIECE_PRICE, CASE_PRICE, CASE_SIZE, KEYWORDS
)
VALUES (
    'PC61', 'Port & Company Essential T-Shirt', 'T-Shirts', 'White', 'L', 3,
    'Port & Company', 'https://www.sanmar.com/brands/port-company/logo.png',
    'https://www.sanmar.com/products/PC61/white_flat_front.jpg',
    'https://www.sanmar.com/colors/PC61/white_square.jpg',
    5.99, 5.49, 59.90, 12, 'tshirt, t-shirt, essential, basic, cotton'
);

INSERT INTO Products (
    STYLE, PRODUCT_TITLE, CATEGORY_NAME, COLOR_NAME, SIZE, SIZE_INDEX,
    BRAND_NAME, BRAND_LOGO_IMAGE, PRODUCT_IMAGE_URL, COLOR_SQUARE_IMAGE,
    PRICE, PIECE_PRICE, CASE_PRICE, CASE_SIZE, KEYWORDS
)
VALUES (
    'PC61', 'Port & Company Essential T-Shirt', 'T-Shirts', 'White', 'XL', 4,
    'Port & Company', 'https://www.sanmar.com/brands/port-company/logo.png',
    'https://www.sanmar.com/products/PC61/white_flat_front.jpg',
    'https://www.sanmar.com/colors/PC61/white_square.jpg',
    5.99, 5.49, 59.90, 12, 'tshirt, t-shirt, essential, basic, cotton'
);

INSERT INTO Products (
    STYLE, PRODUCT_TITLE, CATEGORY_NAME, COLOR_NAME, SIZE, SIZE_INDEX,
    BRAND_NAME, BRAND_LOGO_IMAGE, PRODUCT_IMAGE_URL, COLOR_SQUARE_IMAGE,
    PRICE, PIECE_PRICE, CASE_PRICE, CASE_SIZE, KEYWORDS
)
VALUES (
    'PC61', 'Port & Company Essential T-Shirt', 'T-Shirts', 'White', '2XL', 5,
    'Port & Company', 'https://www.sanmar.com/brands/port-company/logo.png',
    'https://www.sanmar.com/products/PC61/white_flat_front.jpg',
    'https://www.sanmar.com/colors/PC61/white_square.jpg',
    7.99, 7.49, 79.90, 12, 'tshirt, t-shirt, essential, basic, cotton'
);

INSERT INTO Products (
    STYLE, PRODUCT_TITLE, CATEGORY_NAME, COLOR_NAME, SIZE, SIZE_INDEX,
    BRAND_NAME, BRAND_LOGO_IMAGE, PRODUCT_IMAGE_URL, COLOR_SQUARE_IMAGE,
    PRICE, PIECE_PRICE, CASE_PRICE, CASE_SIZE, KEYWORDS
)
VALUES (
    'PC61', 'Port & Company Essential T-Shirt', 'T-Shirts', 'Black', 'S', 1,
    'Port & Company', 'https://www.sanmar.com/brands/port-company/logo.png',
    'https://www.sanmar.com/products/PC61/black_flat_front.jpg',
    'https://www.sanmar.com/colors/PC61/black_square.jpg',
    5.99, 5.49, 59.90, 12, 'tshirt, t-shirt, essential, basic, cotton'
);

INSERT INTO Products (
    STYLE, PRODUCT_TITLE, CATEGORY_NAME, COLOR_NAME, SIZE, SIZE_INDEX,
    BRAND_NAME, BRAND_LOGO_IMAGE, PRODUCT_IMAGE_URL, COLOR_SQUARE_IMAGE,
    PRICE, PIECE_PRICE, CASE_PRICE, CASE_SIZE, KEYWORDS
)
VALUES (
    'PC61', 'Port & Company Essential T-Shirt', 'T-Shirts', 'Black', 'M', 2,
    'Port & Company', 'https://www.sanmar.com/brands/port-company/logo.png',
    'https://www.sanmar.com/products/PC61/black_flat_front.jpg',
    'https://www.sanmar.com/colors/PC61/black_square.jpg',
    5.99, 5.49, 59.90, 12, 'tshirt, t-shirt, essential, basic, cotton'
);

INSERT INTO Products (
    STYLE, PRODUCT_TITLE, CATEGORY_NAME, COLOR_NAME, SIZE, SIZE_INDEX,
    BRAND_NAME, BRAND_LOGO_IMAGE, PRODUCT_IMAGE_URL, COLOR_SQUARE_IMAGE,
    PRICE, PIECE_PRICE, CASE_PRICE, CASE_SIZE, KEYWORDS
)
VALUES (
    'K500', 'Port Authority Silk Touch Polo', 'Polos', 'Red', 'M', 2,
    'Port Authority', 'https://www.sanmar.com/brands/port-authority/logo.png',
    'https://www.sanmar.com/products/K500/red_flat_front.jpg',
    'https://www.sanmar.com/colors/K500/red_square.jpg',
    19.99, 18.99, 215.88, 12, 'polo, golf, business, professional'
);

INSERT INTO Products (
    STYLE, PRODUCT_TITLE, CATEGORY_NAME, COLOR_NAME, SIZE, SIZE_INDEX,
    BRAND_NAME, BRAND_LOGO_IMAGE, PRODUCT_IMAGE_URL, COLOR_SQUARE_IMAGE,
    PRICE, PIECE_PRICE, CASE_PRICE, CASE_SIZE, KEYWORDS
)
VALUES (
    'K500', 'Port Authority Silk Touch Polo', 'Polos', 'Red', 'L', 3,
    'Port Authority', 'https://www.sanmar.com/brands/port-authority/logo.png',
    'https://www.sanmar.com/products/K500/red_flat_front.jpg',
    'https://www.sanmar.com/colors/K500/red_square.jpg',
    19.99, 18.99, 215.88, 12, 'polo, golf, business, professional'
);

INSERT INTO Products (
    STYLE, PRODUCT_TITLE, CATEGORY_NAME, COLOR_NAME, SIZE, SIZE_INDEX,
    BRAND_NAME, BRAND_LOGO_IMAGE, PRODUCT_IMAGE_URL, COLOR_SQUARE_IMAGE,
    PRICE, PIECE_PRICE, CASE_PRICE, CASE_SIZE, KEYWORDS
)
VALUES (
    'J317', 'Port Authority Core Soft Shell Jacket', 'Outerwear', 'Black', 'M', 2,
    'Port Authority', 'https://www.sanmar.com/brands/port-authority/logo.png',
    'https://www.sanmar.com/products/J317/black_flat_front.jpg',
    'https://www.sanmar.com/colors/J317/black_square.jpg',
    49.99, 47.99, 287.94, 6, 'jacket, outerwear, soft shell, waterproof'
);

INSERT INTO Products (
    STYLE, PRODUCT_TITLE, CATEGORY_NAME, COLOR_NAME, SIZE, SIZE_INDEX,
    BRAND_NAME, BRAND_LOGO_IMAGE, PRODUCT_IMAGE_URL, COLOR_SQUARE_IMAGE,
    PRICE, PIECE_PRICE, CASE_PRICE, CASE_SIZE, KEYWORDS
)
VALUES (
    'J317', 'Port Authority Core Soft Shell Jacket', 'Outerwear', 'Black', 'L', 3,
    'Port Authority', 'https://www.sanmar.com/brands/port-authority/logo.png',
    'https://www.sanmar.com/products/J317/black_flat_front.jpg',
    'https://www.sanmar.com/colors/J317/black_square.jpg',
    49.99, 47.99, 287.94, 6, 'jacket, outerwear, soft shell, waterproof'
);

INSERT INTO Products (
    STYLE, PRODUCT_TITLE, CATEGORY_NAME, COLOR_NAME, SIZE, SIZE_INDEX,
    BRAND_NAME, BRAND_LOGO_IMAGE, PRODUCT_IMAGE_URL, COLOR_SQUARE_IMAGE,
    PRICE, PIECE_PRICE, CASE_PRICE, CASE_SIZE, KEYWORDS
)
VALUES (
    'J317', 'Port Authority Core Soft Shell Jacket', 'Outerwear', 'Black', 'XL', 4,
    'Port Authority', 'https://www.sanmar.com/brands/port-authority/logo.png',
    'https://www.sanmar.com/products/J317/black_flat_front.jpg',
    'https://www.sanmar.com/colors/J317/black_square.jpg',
    49.99, 47.99, 287.94, 6, 'jacket, outerwear, soft shell, waterproof'
);