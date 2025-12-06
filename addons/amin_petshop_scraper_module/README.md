# Amin Petshop Scraper Module

## Overview

Complete Odoo 19 module for importing and managing products from Amin Petshop website (https://aminpetshop.com/).

## Features

- **Extended Product Fields**: 30+ custom fields for Amin Petshop product data
- **Price History Tracking**: Automatic tracking of price changes over time
- **Import Wizard**: Import products from JSON or CSV files
- **Update Wizard**: Update existing products from Amin Petshop
- **Discount Calculation**: Automatic calculation of discount percentage and amount
- **Category Management**: Track main category, subcategory, and category path
- **Stock Monitoring**: Track availability and stock status
- **Product Matching**: Smart matching by link, SKU, or product name

## Module Structure

```
amin_petshop_scraper_module/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── product_product.py          # Extended product.product model
│   └── amin_petshop_price_history.py  # Price history model
├── views/
│   ├── product_product_views.xml    # Product form/tree views
│   └── amin_petshop_price_history_views.xml
├── wizard/
│   ├── __init__.py
│   ├── amin_petshop_import_wizard.py
│   ├── amin_petshop_update_wizard.py
│   ├── amin_petshop_import_wizard_views.xml
│   └── amin_petshop_update_wizard_views.xml
├── security/
│   └── ir.model.access.csv
└── README.md
```

## Installation

1. Copy the module to your Odoo addons directory
2. Update the apps list in Odoo
3. Install the module from Apps menu

## Usage

### Import Products

1. Navigate to **Sales > Import Products from Amin Petshop**
2. Select import type (JSON or CSV)
3. Upload your data file
4. Configure matching options
5. Click **Import**

### Update Products

1. Select products in the product list
2. Click **Update from Amin Petshop** button
3. Or use **Sales > Update Products from Amin Petshop**
4. Select products and update mode
5. Click **Update**

### View Price History

1. Open a product with Amin Petshop data
2. Go to **Amin Petshop** tab
3. Click **View Price History** button
4. Or use **Sales > Price History** menu

## Sample Data Format

```json
{
    "name": "PURINA DOG CHOW ADULT With Chicken 14KG",
    "link": "https://aminpetshop.com/products/purina-dog-chow-adult-chicken-14kg",
    "image_url": "https://cdn.shopify.com/s/files/1/0123/4567/products/dog-chow-14kg.jpg",
    "price": 1507.00,
    "regular_price": 3015.00,
    "currency": "EGP",
    "brand": "Dog chow",
    "sku": "PURINA-DC-ADULT-14KG",
    "main_category": "Dog",
    "subcategory": "Adult Dog",
    "category_path": "Dog > Adult Dog > Dry Food",
    "collection": "Dog Chow",
    "available": true,
    "stock_status": "in_stock",
    "description": "Full product description...",
    "short_description": "Short description...",
    "specifications": "Weight: 14KG, Age: Adult...",
    "variants": [...]
}
```

## Key Features

- **Automatic Price History**: Price changes are automatically tracked
- **Discount Calculation**: Computed fields for discount percentage and amount
- **Smart Matching**: Prevents duplicates by matching on link, SKU, or name
- **Bulk Operations**: Import/update multiple products at once
- **Error Handling**: Graceful handling of missing or invalid data
- **Comprehensive Logging**: Detailed logs for import/update operations

## Fields Overview

### Basic Information
- Amin Petshop Link (required for matching)
- Image URL
- SKU
- Brand

### Pricing
- Current Price
- Regular Price
- Currency
- Discount Percentage (computed)
- Discount Amount (computed)
- Has Discount (computed)

### Category
- Main Category
- Subcategory
- Category Path
- Collection

### Availability
- Available Status
- Stock Status
- Last Stock Check

### Tracking
- First Seen
- Last Updated
- Last Price Update
- Update Count

## License

LGPL-3

