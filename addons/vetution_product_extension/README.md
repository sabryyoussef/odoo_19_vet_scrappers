# Vetution Product Extension Module

## Overview

This Odoo 19 module extends the `product.product` model to support veterinary product data imported from e-commerce websites. It provides comprehensive fields for veterinary product information and supports importing data from JSON and CSV files.

## Features

- **Extended Product Fields**: Adds 30+ custom fields to product.product for veterinary data
- **Multi-Vendor Pricing**: Separate model to store multiple vendor prices per product
- **JSON/CSV Import**: Wizard to import product data from JSON or CSV files
- **Flexible Matching**: Match products by name, barcode, or Vetution link
- **Data Mapping**: Automatic mapping of nested structures (lists, dictionaries)
- **Comprehensive Views**: Organized views with logical grouping of fields

## Module Structure

```
vetution_product_extension/
├── __init__.py
├── manifest.py
├── models/
│   ├── __init__.py
│   ├── product_product.py      # Extended product.product model
│   └── vendor_price.py         # Vendor price model
├── views/
│   ├── product_views.xml       # Product form/tree views
│   └── vendor_price_views.xml  # Vendor price views
├── wizard/
│   ├── __init__.py
│   ├── import_product_data.py   # Import wizard logic
│   └── import_product_data_views.xml
├── security/
│   └── ir.model.access.csv     # Access rights
└── README.md
```

## Installation

1. Copy the module to your Odoo addons directory
2. Update the apps list in Odoo
3. Install the module from Apps menu

## Usage

### Importing Product Data

1. Navigate to **Sales > Import Product Data**
2. Select file type (JSON or CSV)
3. Upload your file
4. Configure import options:
   - **Import Mode**: Create, Update, or Both
   - **Match By**: Name, Barcode, or Vetution Link
   - **Skip Duplicates**: Skip existing products
5. Click **Import**

### JSON Format

The module expects JSON files with the following structure:

```json
{
  "name": "NOBIVAC RABIES",
  "link": "https://www.vetution.com/products/nobivac-rabies",
  "brand": "MSD Animal Health",
  "brand_link": "https://www.vetution.com/brands/msd-animal-health",
  "review_count": 0,
  "ingredients": ["Inactivated virus"],
  "sizes": ["1 dose"],
  "express_delivery": true,
  "cold_chain": true,
  "price": 200.0,
  "currency": "EGP",
  "vendor_prices": [
    {
      "price": 200.0,
      "currency": "EGP",
      "expiration_date": "2028-02-28",
      "available": true
    }
  ],
  "min_price": 192.0,
  "max_price": 210.0,
  "image_url": "https://...",
  "tags": ["Cat", "Vaccines", "Dog"],
  "species": ["Canine", "Feline"],
  "detailed_sections": {
    "composition": "...",
    "indications": "...",
    "dose_and_administration": "..."
  }
}
```

### CSV Format

CSV files should have column headers matching the JSON field names. List fields can be:
- Comma-separated values: `"Cat, Dog, Bird"`
- JSON arrays: `["Cat", "Dog", "Bird"]`

## Field Mappings

### Direct Mappings
- `name` → Product Name
- `link` → `vetution_link`
- `brand` → `vetution_brand`
- `price` → `vetution_price`
- `currency` → `vetution_currency`
- And more...

### List to Text
- `ingredients` → `vetution_ingredients` (comma-separated)
- `sizes` → `vetution_sizes` (comma-separated)
- `tags` → `vetution_tags` (comma-separated)
- `species` → `vetution_species` (comma-separated)

### Dictionary Mappings
- `detailed_sections.composition` → `vetution_composition`
- `detailed_sections.indications` → `vetution_indications`
- And 13 more detailed section fields...

## Models

### product.product (Extended)

Adds veterinary-specific fields organized in categories:
- Basic Information (link, brand, reviews, rating)
- Product Attributes (ingredients, sizes, tags, species)
- Pricing & Vendors (price, currency, vendor prices)
- Detailed Information (composition, indications, etc.)
- Delivery & Storage (express delivery, cold chain)

### vetution.vendor.price

Stores multiple vendor prices for each product:
- `product_id`: Link to product
- `price`: Vendor price
- `currency`: Currency code
- `expiration_date`: Product expiration
- `available`: Availability status
- `vendor_name`: Vendor name

## Views

### Product Form View
- New "Vetution Data" tab with all custom fields
- Organized into logical groups
- Vendor prices shown as One2many

### Product Tree View
- Additional columns: Brand, Price, Express Delivery, Cold Chain

### Search Filters
- Filter by Express Delivery
- Filter by Cold Chain
- Search by Brand and Species

## Technical Details

- **Odoo Version**: 19.0
- **Module Version**: 19.0.1.0.0
- **Dependencies**: product, base
- **License**: LGPL-3

## Support

For issues or questions, please contact the development team.

