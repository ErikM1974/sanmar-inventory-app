# SanMar Inventory App Home Page Redesign

## Overview
This document outlines the plan for redesigning the SanMar Inventory App home page to create a more intuitive, category-based search experience while maintaining compatibility with the existing product detail pages.

## Current State Analysis
The current app has a minimal home page focused on style number search with:
- Basic search bar with autocomplete
- Test styles section for quick access
- Simple layout optimized for direct style lookup

## Design Goals
1. Create a visually engaging home page with product categorization
2. Enable search by product type, styles, brands, and colors
3. Maintain compatibility with existing product detail pages
4. Improve overall user experience and product discoverability

## Data Sources
The redesigned home page will utilize two primary data sources:

### 1. SanMar Data Library (SDL) Files
**Source File:** `SanMar_SDL_N.csv`
**Usage:** Extract structural information for categories, brands, and product types
**Update Frequency:** Download periodically to refresh product category data

**Key Fields:**
- `CATEGORY`: For main product categories (T-Shirts, Polos, Jackets, etc.)
- `BRAND_NAME`: For brand listings (Port Authority, Port & Company, Sport-Tek, etc.)
- `SUB_CATEGORY`: For subcategory listings within each category

### 2. SanMar API Endpoints
**For Product Details:**
- `getProductInfoByStyleColorSize`: Fetch specific product information
- `getInventoryByStyleColorSize`: Retrieve inventory levels

**For Search Functionality:**
- Current autocomplete endpoint (enhanced with category/type filters)

## Home Page Structure

### 1. Header & Navigation
```
┌──────────────────────────────────────────────────────────────────────┐
│                     SanMar Inventory Lookup                          │
└──────────────────────────────────────────────────────────────────────┘
```

### 2. Enhanced Search Bar with Filters
```
┌──────────────────────────────────────────────────────────────────────┐
│ ┌──────────┐ ┌────────────────────────────────────────────────┐ ┌───┐│
│ │Product▾  │ │Search by style, product, or keyword...         │ │ 🔍 ││
│ └──────────┘ └────────────────────────────────────────────────┘ └───┘│
└──────────────────────────────────────────────────────────────────────┘
```

### 3. Two-Column Layout

```
┌──────────────────────┬───────────────────────────────────────────────┐
│                      │                                               │
│   CATEGORIES         │  FEATURED PRODUCTS                            │
│   ═════════════      │  ═══════════════════                          │
│                      │                                               │
│   ☑ NEW              │  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│   ☐ BRANDS           │  │         │  │         │  │         │        │
│   ☐ T-SHIRTS         │  │  IMG    │  │  IMG    │  │  IMG    │        │
│   ☐ POLOS/KNITS      │  │         │  │         │  │         │        │
│   ☐ OUTERWEAR        │  │ K500    │  │ PC61    │  │ J790    │        │
│   ☐ FLEECE           │  │ Polo    │  │ T-Shirt │  │ Jacket  │        │
│   ☐ WOVEN SHIRTS     │  └─────────┘  └─────────┘  └─────────┘        │
│   ☐ ACTIVEWEAR       │                                               │
│   ☐ LADIES           │  POPULAR CATEGORIES                           │
│   ☐ HEADWEAR         │  ═════════════════                            │
│   ☐ BAGS             │                                               │
│   ☐ ACCESSORIES      │  T-SHIRTS         POLOS/KNITS     OUTERWEAR   │
│                      │  ════════         ══════════      ═════════   │
│                      │  100% Cotton      Pique            Soft Shell │
│                      │  Tri-Blend        Jersey           Rain       │
│                      │  Performance      Performance      Fleece     │
│                      │  Long Sleeve      Long Sleeve      Vests      │
│                      │                                               │
│   BRANDS             │  BRANDS                                       │
│   ══════             │  ══════                                       │
│                      │                                               │
│   ☐ Port Authority   │  PORT AUTHORITY   SPORT-TEK       DISTRICT    │
│   ☐ Port & Company   │  ══════════════   ═════════       ════════    │
│   ☐ Sport-Tek        │                                               │
│   ☐ District         │  PORT & COMPANY   EDDIE BAUER     NEW ERA     │
│   ☐ Eddie Bauer      │  ══════════════   ═══════════     ════════    │
│   ☐ New Era          │                                               │
│                      │                                               │
└──────────────────────┴───────────────────────────────────────────────┘
```

### 4. Color Filter Section

```
┌──────────────────────────────────────────────────────────────────────┐
│ POPULAR COLORS                                                       │
│ ═════════════                                                        │
│                                                                      │
│ ⬤ Black   ⬤ Navy   ⬤ White   ⬤ Red   ⬤ Royal   ⬤ Grey  + More Colors │
└──────────────────────────────────────────────────────────────────────┘
```

## Technical Implementation

### 1. Backend Enhancements

#### 1.1 Data Import and Processing
- Create a scheduled task to download and process the SanMar_SDL_N.csv file
- Extract and organize categories, subcategories, and brands
- Store processed data in a structured format (JSON or database)

```python
# Pseudo-code for SDL file processing
def process_sdl_file(file_path):
    categories = {}
    brands = set()
    
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            category = row['CATEGORY']
            subcategory = row['SUB_CATEGORY']
            brand = row['BRAND_NAME']
            
            if category not in categories:
                categories[category] = set()
            
            categories[category].add(subcategory)
            brands.add(brand)
    
    return {
        'categories': categories,
        'brands': list(brands)
    }
```

#### 1.2 New API Endpoints
Add these endpoints to support the enhanced home page:

1. **Categories Endpoint**
```python
@app.route('/api/categories')
def get_categories():
    # Return processed category data
    return jsonify(categories_data)
```

2. **Brands Endpoint**
```python
@app.route('/api/brands')
def get_brands():
    # Return processed brands data
    return jsonify(brands_data)
```

3. **Enhanced Search Endpoint**
```python
@app.route('/api/search')
def enhanced_search():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    brand = request.args.get('brand', '')
    color = request.args.get('color', '')
    
    # Filter results based on parameters
    results = filter_products(query, category, brand, color)
    return jsonify(results)
```

### 2. Frontend Implementation

#### 2.1 HTML Structure (index.html)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SanMar Inventory Lookup</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='home-page.css') }}">
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="py-3 mb-3 text-center">
            <h1>SanMar Inventory Lookup</h1>
        </header>
        
        <!-- Enhanced Search Bar -->
        <div class="search-container mb-4">
            <form action="/search" method="GET" id="searchForm">
                <div class="search-bar-container">
                    <div class="filter-dropdown">
                        <select class="form-select" id="categoryFilter" name="category">
                            <option value="">All Products</option>
                            <!-- Categories populated by JavaScript -->
                        </select>
                    </div>
                    <div class="search-input-container">
                        <input type="text" 
                               class="form-control form-control-lg" 
                               id="styleInput" 
                               name="query" 
                               placeholder="Search by style, product, or keyword..." 
                               autocomplete="off">
                        <div id="autocompleteResults" class="autocomplete-results"></div>
                    </div>
                    <button type="submit" class="btn btn-primary search-btn">
                        <i class="fas fa-search"></i>
                    </button>
                </div>
            </form>
        </div>
        
        <!-- Main Content -->
        <div class="row">
            <!-- Left Sidebar -->
            <div class="col-md-3">
                <div class="sidebar">
                    <h3>Categories</h3>
                    <div class="category-list" id="categoryList">
                        <!-- Categories populated by JavaScript -->
                    </div>
                    
                    <h3 class="mt-4">Brands</h3>
                    <div class="brand-list" id="brandList">
                        <!-- Brands populated by JavaScript -->
                    </div>
                </div>
            </div>
            
            <!-- Main Content Area -->
            <div class="col-md-9">
                <!-- Featured Products -->
                <div class="featured-products">
                    <h2>Featured Products</h2>
                    <div class="product-grid" id="featuredProducts">
                        <!-- Featured products populated by JavaScript -->
                    </div>
                </div>
                
                <!-- Popular Categories -->
                <div class="popular-categories mt-5">
                    <h2>Popular Categories</h2>
                    <div class="category-grid" id="popularCategories">
                        <!-- Category columns populated by JavaScript -->
                    </div>
                </div>
                
                <!-- Popular Brands -->
                <div class="popular-brands mt-5">
                    <h2>Brands</h2>
                    <div class="brand-grid" id="popularBrands">
                        <!-- Brand logos populated by JavaScript -->
                    </div>
                </div>
                
                <!-- Color Filters -->
                <div class="color-filters mt-5">
                    <h2>Popular Colors</h2>
                    <div class="color-swatches" id="colorSwatches">
                        <!-- Color swatches populated by JavaScript -->
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://kit.fontawesome.com/your-fontawesome-kit.js"></script>
    <script src="{{ url_for('static', filename='home-page.js') }}"></script>
</body>
</html>
```

#### 2.2 CSS Styling (home-page.css)

```css
/* Modern CSS Variables */
:root {
    --primary: #0d6efd;
    --primary-dark: #0b5ed7;
    --primary-light: #cfe2ff;
    --gray-100: #f8f9fa;
    --gray-200: #e9ecef;
    --gray-300: #dee2e6;
    --gray-600: #6c757d;
    --gray-800: #343a40;
    --border-radius: 0.375rem;
    --box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
    --transition: all 0.2s ease-in-out;
}

/* Layout Styles */
body {
    background-color: var(--gray-100);
}

.container {
    max-width: 1400px;
    padding: 2rem 1rem;
}

/* Enhanced Search Bar */
.search-bar-container {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
}

.filter-dropdown {
    min-width: 150px;
}

.search-input-container {
    flex-grow: 1;
    position: relative;
}

.search-btn {
    padding: 0.75rem 1.25rem;
    font-size: 1.25rem;
}

/* Sidebar Styles */
.sidebar {
    background-color: white;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    padding: 1.5rem;
}

.sidebar h3 {
    border-bottom: 2px solid var(--primary);
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
    font-size: 1.25rem;
    font-weight: 600;
}

.category-list, .brand-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.category-item, .brand-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    border-radius: var(--border-radius);
    transition: var(--transition);
    cursor: pointer;
}

.category-item:hover, .brand-item:hover {
    background-color: var(--gray-200);
}

.category-item.active, .brand-item.active {
    background-color: var(--primary-light);
    font-weight: 600;
}

/* Main Content Styles */
.col-md-9 > div {
    background-color: white;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

.col-md-9 h2 {
    border-bottom: 2px solid var(--primary);
    padding-bottom: 0.5rem;
    margin-bottom: 1.5rem;
    font-size: 1.5rem;
    font-weight: 600;
}

/* Product Grid */
.product-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1.5rem;
}

.product-card {
    border: 1px solid var(--gray-300);
    border-radius: var(--border-radius);
    overflow: hidden;
    transition: var(--transition);
    background-color: white;
}

.product-card:hover {
    transform: translateY(-5px);
    box-shadow: var(--box-shadow);
}

.product-image {
    width: 100%;
    height: 200px;
    object-fit: cover;
}

.product-info {
    padding: 1rem;
}

.product-style {
    font-weight: 700;
    margin-bottom: 0.25rem;
}

.product-name {
    color: var(--gray-600);
    font-size: 0.9rem;
}

/* Category Grid */
.category-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 2rem;
}

.category-column h3 {
    border-bottom: 2px solid var(--primary);
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
    font-size: 1.2rem;
    font-weight: 600;
}

.subcategory-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.subcategory-item {
    padding: 0.5rem;
    border-radius: var(--border-radius);
    transition: var(--transition);
    cursor: pointer;
}

.subcategory-item:hover {
    background-color: var(--gray-200);
}

/* Brand Grid */
.brand-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1.5rem;
}

.brand-card {
    border: 1px solid var(--gray-300);
    border-radius: var(--border-radius);
    padding: 1rem;
    text-align: center;
    transition: var(--transition);
    background-color: white;
    cursor: pointer;
    height: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.brand-card:hover {
    transform: translateY(-5px);
    box-shadow: var(--box-shadow);
}

.brand-logo {
    max-width: 100%;
    max-height: 80px;
    object-fit: contain;
}

/* Color Swatches */
.color-swatches {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
}

.color-swatch {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    cursor: pointer;
    border: 2px solid var(--gray-300);
    transition: var(--transition);
    position: relative;
}

.color-swatch:hover {
    transform: scale(1.2);
}

.color-swatch.active {
    border-color: var(--primary);
    transform: scale(1.2);
}

/* Color tooltips */
.color-swatch::after {
    content: attr(data-color);
    position: absolute;
    bottom: -30px;
    left: 50%;
    transform: translateX(-50%);
    background-color: var(--gray-800);
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: var(--border-radius);
    font-size: 0.75rem;
    white-space: nowrap;
    opacity: 0;
    transition: var(--transition);
    pointer-events: none;
}

.color-swatch:hover::after {
    opacity: 1;
}

/* Responsive Adjustments */
@media (max-width: 768px) {
    .search-bar-container {
        flex-direction: column;
        align-items: stretch;
    }
    
    .category-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
}
```

#### 2.3 JavaScript (home-page.js)

```javascript
document.addEventListener('DOMContentLoaded', function() {
    // Load Categories and Brands
    fetchCategories();
    fetchBrands();
    
    // Load Featured Products
    loadFeaturedProducts();
    
    // Load Popular Categories
    loadPopularCategories();
    
    // Load Popular Brands
    loadPopularBrands();
    
    // Load Color Swatches
    loadColorSwatches();
    
    // Set up Search Autocomplete
    setupAutocomplete();
    
    // Set up Event Listeners
    setupEventListeners();
});

// Fetch Categories from API
async function fetchCategories() {
    try {
        const response = await fetch('/api/categories');
        const data = await response.json();
        
        // Populate category dropdown in search
        const categoryFilter = document.getElementById('categoryFilter');
        populateCategoryDropdown(categoryFilter, data);
        
        // Populate sidebar category list
        const categoryList = document.getElementById('categoryList');
        populateCategoryList(categoryList, data);
        
    } catch (error) {
        console.error('Error fetching categories:', error);
    }
}

// Fetch Brands from API
async function fetchBrands() {
    try {
        const response = await fetch('/api/brands');
        const data = await response.json();
        
        // Populate sidebar brand list
        const brandList = document.getElementById('brandList');
        populateBrandList(brandList, data);
        
    } catch (error) {
        console.error('Error fetching brands:', error);
    }
}

// Load Featured Products
function loadFeaturedProducts() {
    const featuredProducts = document.getElementById('featuredProducts');
    
    // Featured product data (could come from API in production)
    const products = [
        { style: 'K500', name: 'Port Authority Silk Touch Polo', image: 'https://www.sanmar.com/products/catalog/2022/f1/port_authority/fullsize/K500_Black_Model_Front_2022.jpg' },
        { style: 'PC61', name: 'Port & Company Essential T-Shirt', image: 'https://www.sanmar.com/products/catalog/2021/f2/port__company/fullsize/PC61_Black_Model_Front_2021.jpg' },
        { style: 'J790', name: 'Port Authority Glacier Soft Shell Jacket', image: 'https://www.sanmar.com/products/catalog/2022/f2/port_authority/fullsize/J790_Black_Model_Front_2022.jpg' },
        { style: 'ST850', name: 'Sport-Tek PosiCharge Competitor Tee', image: 'https://www.sanmar.com/products/catalog/2022/f1/sport-tek/fullsize/ST850_Black_Model_Front_2022.jpg' }
    ];
    
    // Create product cards
    products.forEach(product => {
        featuredProducts.innerHTML += `
            <div class="product-card">
                <img src="${product.image}" alt="${product.name}" class="product-image">
                <div class="product-info">
                    <div class="product-style">${product.style}</div>
                    <div class="product-name">${product.name}</div>
                </div>
            </div>
        `;
    });
}

// Load Popular Categories
function loadPopularCategories() {
    const popularCategories = document.getElementById('popularCategories');
    
    // Category data (could come from API in production)
    const categories = [
        {
            name: 'T-SHIRTS',
            subcategories: ['100% Cotton', 'Tri-Blend', 'Performance', 'Long Sleeve']
        },
        {
            name: 'POLOS/KNITS',
            subcategories: ['Pique', 'Jersey', 'Performance', 'Long Sleeve']
        },
        {
            name: 'OUTERWEAR',
            subcategories: ['Soft Shell', 'Rain', 'Fleece', 'Vests']
        }
    ];
    
    // Create category columns
    categories.forEach(category => {
        let subcategoryHTML = '';
        
        category.subcategories.forEach(subcategory => {
            subcategoryHTML += `<div class="subcategory-item">${subcategory}</div>`;
        });
        
        popularCategories.innerHTML += `
            <div class="category-column">
                <h3>${category.name}</h3>
                <div class="subcategory-list">
                    ${subcategoryHTML}
                </div>
            </div>
        `;
    });
}

// Load Popular Brands
function loadPopularBrands() {
    const popularBrands = document.getElementById('popularBrands');
    
    // Brand data (could come from API in production)
    const brands = [
        { name: 'PORT AUTHORITY', logo: '/static/images/brands/port-authority.png' },
        { name: 'SPORT-TEK', logo: '/static/images/brands/sport-tek.png' },
        { name: 'DISTRICT', logo: '/static/images/brands/district.png' },
        { name: 'PORT & COMPANY', logo: '/static/images/brands/port-and-company.png' },
        { name: 'EDDIE BAUER', logo: '/static/images/brands/eddie-bauer.png' },
        { name: 'NEW ERA', logo: '/static/images/brands/new-era.png' }
    ];
    
    // Create brand cards
    brands.forEach(brand => {
        popularBrands.innerHTML += `
            <div class="brand-card" data-brand="${brand.name}">
                <img src="${brand.logo}" alt="${brand.name}" class="brand-logo">
            </div>
        `;
    });
}

// Load Color Swatches
function loadColorSwatches() {
    const colorSwatches = document.getElementById('colorSwatches');
    
    // Color data (could come from API in production)
    const colors = [
        { name: 'Black', hex: '#000000' },
        { name: 'Navy', hex: '#000080' },
        { name: 'White', hex: '#FFFFFF' },
        { name: 'Red', hex: '#FF0000' },
        { name: 'Royal', hex: '#4169E1' },
        { name: 'Grey', hex: '#808080' }
    ];
    
    // Create color swatches
    colors.forEach(color => {
        colorSwatches.innerHTML += `
            <div class="color-swatch" style="background-color: ${color.hex};" data-color="${color.name}"></div>
        `;
    });
    
    // Add "More Colors" link
    colorSwatches.innerHTML += `
        <a href="/colors" class="more-colors">+ More Colors</a>
    `;
}

// Set up Autocomplete for Search
function setupAutocomplete() {
    const styleInput = document.getElementById('styleInput');
    const autocompleteResults = document.getElementById('autocompleteResults');
    
    styleInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        if (query.length < 2) {
            autocompleteResults.innerHTML = '';
            autocompleteResults.style.display = 'none';
            return;
        }
        
        // Get selected category from dropdown
        const categoryFilter = document.getElementById('categoryFilter');
        const category = categoryFilter.value;
        
        // Fetch autocomplete results
        fetch(`/autocomplete?q=${encodeURIComponent(query)}&category=${encodeURIComponent(category)}`)
            .then(response => response.json())
            .then(data => {
                if (data.length === 0) {
                    autocompleteResults.innerHTML = '';
                    autocompleteResults.style.display = 'none';
                    return;
                }
                
                // Display results
                autocompleteResults.innerHTML = '';
                data.forEach(item => {
                    const resultItem = document.createElement('div');
                    resultItem.classList.add('autocomplete-item');
                    
                    // Highlight the matching text
                    const regex = new RegExp(`(${query})`, 'gi');
                    const highlightedText = item.replace(regex, '<strong>$1</strong>');
                    
                    resultItem.innerHTML = highlightedText;
                    
                    // Add click event
                    resultItem.addEventListener('click', function() {
                        styleInput.value = item;
                        autocompleteResults.style.display = 'none';
                        document.getElementById('searchForm').submit();
                    });
                    
                    autocompleteResults.appendChild(resultItem);
                });
                
                autocompleteResults.style.display = 'block';
            })
            .catch(error => {
                console.error('Error fetching autocomplete results:', error);
            });
    });
    
    // Close autocomplete when clicking outside
    document.addEventListener('click', function(event) {
        if (!styleInput.contains(event.target) && !autocompleteResults.contains(event.target)) {
            autocompleteResults.style.display = 'none';
        }
    });
}

// Helper Functions
function populateCategoryDropdown(selectElement, categories) {
    Object.keys(categories).forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        selectElement.appendChild(option);
    });
}

function populateCategoryList(containerElement, categories) {
    Object.keys(categories).forEach(category => {
        const categoryItem = document.createElement('div');
        categoryItem.classList.add('category-item');
        categoryItem.innerHTML = `
            <input type="checkbox" id="category-${category.toLowerCase().replace(/\s+/g, '-')}">
            <label for="category-${category.toLowerCase().replace(/\s+/g, '-')}">${category}</label>
        `;
        containerElement.appendChild(categoryItem);
        
        // Add click event (toggle checkbox and filter results)
        categoryItem.addEventListener('click', function(event) {
            if (event.target.tagName !== 'INPUT') {
                const checkbox = this.querySelector('input[type="checkbox"]');
                checkbox.checked = !checkbox.checked;
                filterResults();
            }
        });
    });
}

function populateBrandList(containerElement, brands) {
    brands.forEach(brand => {
        const brandItem = document.createElement('div');
        brandItem.classList.add('brand-item');
        brandItem.innerHTML = `
            <input type="checkbox" id="brand-${brand.toLowerCase().replace(/\s+/g, '-')}">
            <label for="brand-${brand.toLowerCase().replace(/\s+/g, '-')}">${brand}</label>
        `;
        containerElement.appendChild(brandItem);
        
        // Add click event (toggle checkbox and filter results)
        brandItem.addEventListener('click', function(event) {
            if (event.target.tagName !== 'INPUT') {
                const checkbox = this.querySelector('input[type="checkbox"]');
                checkbox.checked = !checkbox.checked;
                filterResults();
            }
        });
    });
}

// Set up Event Listeners
function setupEventListeners() {
    // Brand card click
    document.querySelectorAll('.brand-card').forEach(card => {
        card.addEventListener('click', function() {
            const brand = this.dataset.brand;
            window.location.href = `/search?brand=${encodeURIComponent(brand)}`;
        });
    });
    
    // Subcategory item click
    document.querySelectorAll('.subcategory-item').forEach(item => {
        item.addEventListener('click', function() {
            const category = this.closest('.category-column').querySelector('h3').textContent;
            const subcategory = this.textContent;
            window.location.href = `/search?category=${encodeURIComponent(category)}&subcategory=${encodeURIComponent(subcategory)}`;
        });
    });
    
    // Color swatch click
    document.querySelectorAll('.color-swatch').forEach(swatch => {
        swatch.addEventListener('click', function() {
            const color = this.dataset.color;
            window.location.href = `/search?color=${encodeURIComponent(color)}`;
        });
    });
}

// Filter results based on selected categories, brands, etc.
function filterResults() {
    // This would be implemented to dynamically filter the product grid
    // based on selected checkboxes in the sidebar
    console.log('Filtering results based on selected options');
}
```

### 3. Server-Side Route Updates

```python
# Update app.py to add new routes

# Main home page route - enhanced version
@app.route('/')
def index():
    return render_template('index.html')

# Search results page
@app.route('/search')
def search_results():
    query = request.args.get('query', '')
    category = request.args.get('category', '')
    brand = request.args.get('brand', '')
    color = request.args.get('color', '')
    subcategory = request.args.get('subcategory', '')
    
    # If searching by style number directly, redirect to product page
    if query and len(query) >= 3 and not any([category, brand, color, subcategory]):
        # Check if this is a valid style number format
        if re.match(r'^[A-Za-z0-9]{3,10}$', query):
            return redirect(url_for('product_page', style=query))
    
    # Otherwise, perform a search
    results = perform_search(query, category, brand, color, subcategory)
    
    return render_template('search_results.html', 
                          results=results,
                          query=query,
                          category=category,
                          brand=brand,
                          color=color,
                          subcategory=subcategory)

# Enhanced autocomplete endpoint
@app.route('/autocomplete')
def autocomplete():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    
    if not query or len(query) < 2:
        return jsonify([])
    
    # Get filtered autocomplete results
    results = get_filtered_autocomplete(query, category)
    
    return jsonify(results)

# Helper function for filtered autocomplete
def get_filtered_autocomplete(query, category=None):
    # If using the original autocomplete function
    results = fetch_autocomplete(query)
    
    # Filter by category if specified
    if category and results:
        # This would require a mapping from style numbers to categories
        # which could come from the SDL data
        results = [style for style in results if get_style_category(style) == category]
    
    return results

# New API endpoints
@app.route('/api/categories')
def api_categories():
    # Return processed category data from SDL file
    return jsonify(get_categories_data())

@app.route('/api/brands')
def api_brands():
    # Return processed brand data from SDL file
    return jsonify(get_brands_data())
```

## Integration with Existing Product Detail Page

The redesigned home page integrates seamlessly with the existing product detail page by:

1. **Maintaining URL Structure**: All product links use the same `/product/<style>` URL pattern
2. **Passing query parameters**: When filtering by color, passes a `color` parameter to the product page
3. **Maintaining Context**: The search form is included in the product page header for easy return to search

## Deployment Plan

### Phase 1: Initial Setup
1. Create new HTML, CSS, and JS files for the redesigned homepage
2. Add placeholder content for testing
3. Implement basic search bar functionality
4. Test compatibility with existing product detail page

### Phase 2: Backend Integration
1. Set up CSV data import and processing
2. Create new API endpoints for categories and brands
3. Enhance the search and autocomplete functionality
4. Connect frontend components to backend data

### Phase 3: Testing and Refinement
1. Test all filtering options and product grid display
2. Ensure mobile responsiveness
3. Optimize performance and loading times
4. Gather user feedback and make adjustments

### Phase 4: Launch
1. Deploy to staging environment for final testing
2. Verify analytics tracking
3. Deploy to production
4. Monitor for any issues

## Conclusion

This redesigned home page will significantly improve the user experience by:

1. Providing multiple ways to discover products (category, brand, color)
2. Offering visual navigation options for quick access to popular items
3. Maintaining compatibility with the existing product detail page
4. Creating a more engaging and intuitive interface for both new and returning users