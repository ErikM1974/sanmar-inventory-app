# SanMar Inventory App Home Page Mockup

This document provides a visual representation of the redesigned home page for the SanMar Inventory App.

## Visual Mockup

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│                    SANMAR INVENTORY LOOKUP                           │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ ┌──────────┐ ┌────────────────────────────────────────────────┐ ┌───┐│
│ │Product▾  │ │Search by style, product, or keyword...         │ │ 🔍 ││
│ └──────────┘ └────────────────────────────────────────────────┘ └───┘│
│                                                                      │
├──────────────────────┬───────────────────────────────────────────────┤
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
│   BRANDS             │  POPULAR COLORS                               │
│   ══════             │  ══════════════                               │
│                      │                                               │
│   ☐ Port Authority   │  ⬤ Black   ⬤ Navy   ⬤ White   ⬤ Red   ⬤ Royal │
│   ☐ Port & Company   │                                               │
│   ☐ Sport-Tek        │                                               │
│   ☐ District         │                                               │
│   ☐ Eddie Bauer      │                                               │
│   ☐ New Era          │                                               │
│                      │                                               │
└──────────────────────┴───────────────────────────────────────────────┘
```

## High-Fidelity Design Concepts

### 1. Modern Header with Enhanced Search

![Header With Search](https://placeholder-for-mockup-image-1.png)

The header features:
- Clean, minimalist design with SanMar branding
- Dropdown product type filter
- Advanced search bar with autocomplete
- Responsive design for all devices

### 2. Category Navigation with Visual Cards

![Category Navigation](https://placeholder-for-mockup-image-2.png)

The category section includes:
- Visual cards for each product category
- Icons representing different product types
- Hover effects for better user interaction
- Clear, consistent labeling

### 3. Product Grid Display

![Product Grid](https://placeholder-for-mockup-image-3.png)

The product grid features:
- Clean product cards with images
- Style numbers prominently displayed
- Brief product descriptions
- Consistent sizing and spacing
- Hover effects for interactive feedback

### 4. Filter Sidebar

![Filter Sidebar](https://placeholder-for-mockup-image-4.png)

The filter sidebar includes:
- Collapsible category sections
- Checkbox selection for multi-filtering
- Brand filters with logos
- Clear filter option
- Mobile-friendly accordion design

### 5. Color Selection Interface

![Color Selection](https://placeholder-for-mockup-image-5.png)

The color selection features:
- Visual color swatches
- Tooltips showing color names
- Selected state indication
- Grouping of similar colors

## Mobile Design Considerations

### Responsive Layout Changes

```
┌────────────────────────────┐
│                            │
│  SANMAR INVENTORY LOOKUP   │
│                            │
├────────────────────────────┤
│                            │
│ ┌──────────┐ ┌──────────┐  │
│ │Product▾  │ │Search... │  │
│ └──────────┘ └──────────┘  │
│                            │
├────────────────────────────┤
│ ☰ FILTERS                  │
├────────────────────────────┤
│                            │
│ FEATURED PRODUCTS          │
│ ═══════════════            │
│                            │
│ ┌─────────┐  ┌─────────┐   │
│ │         │  │         │   │
│ │  IMG    │  │  IMG    │   │
│ │         │  │         │   │
│ │ K500    │  │ PC61    │   │
│ │ Polo    │  │ T-Shirt │   │
│ └─────────┘  └─────────┘   │
│                            │
│ CATEGORIES                 │
│ ═════════                  │
│                            │
│ » T-SHIRTS                 │
│ » POLOS/KNITS              │
│ » OUTERWEAR                │
│ » FLEECE                   │
│                            │
│ POPULAR COLORS             │
│ ═════════════              │
│                            │
│ ⬤ ⬤ ⬤ ⬤ ⬤ ⬤ + More        │
│                            │
└────────────────────────────┘
```

On mobile devices:
1. The sidebar becomes a collapsible menu
2. Product grid adjusts to one or two columns
3. Search bar simplifies for touch interaction
4. Category browsing becomes more linear

## User Interaction Flow

### Scenario 1: Direct Style Number Search
1. User enters style number in search bar
2. Autocomplete shows matching options
3. User selects or submits the style number
4. System redirects to existing product detail page

### Scenario 2: Category-Based Browsing
1. User clicks on a product category (e.g., "T-SHIRTS")
2. System displays filtered results for that category
3. User can further refine by brand, color, etc.
4. User selects a product to view details

### Scenario 3: Combined Filtering
1. User selects a product category from sidebar
2. User then selects a brand filter
3. User further narrows by clicking a color swatch
4. User selects from filtered product grid
5. System navigates to product detail page

## Design Language & Style Guide

### Color Palette
- Primary Blue: #0d6efd (Used for buttons, links, selection indicators)
- Secondary Gray: #6c757d (Used for text, borders, subtle elements)
- Light Background: #f8f9fa (Used for page background and cards)
- White: #ffffff (Used for content areas and cards)
- Success Green: #198754 (Used for availability indicators)
- Warning Yellow: #ffc107 (Used for limited stock indicators)

### Typography
- Primary Font: System UI stack (consistent with your existing styling)
- Headings: 600 weight, slightly reduced letter spacing
- Body Text: 400 weight, 1.6 line height
- Navigation: 500 weight, uppercase for categories
- Product Names: 500 weight, title case

### Spacing System
- Base Unit: 0.25rem (4px)
- Standard Margins: 1.5rem (24px)
- Card Padding: 1rem (16px)
- Grid Gap: 1.5rem (24px)

### Interactive Elements
- Buttons: Rounded corners, subtle hover effect with shadow
- Cards: Slight elevation on hover, subtle shadow
- Swatches: Scale effect on hover, border highlight on active
- Checkboxes: Custom styling to match design language

## Implementation Considerations

1. The design maintains compatibility with your existing product detail pages
2. All interactive elements have appropriate hover/focus states for accessibility
3. Color contrast meets WCAG AA standards for readability
4. The layout accommodates various product image formats and text lengths
5. The design supports internationalization with text expansion/contraction

Would you like me to create a sample HTML implementation of this mockup that you could adapt in Code mode?