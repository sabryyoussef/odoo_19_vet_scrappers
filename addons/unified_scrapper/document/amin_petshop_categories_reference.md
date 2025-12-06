# Amin Petshop Categories Reference

## Overview
This document lists all 27 category mappings created for Amin Petshop integration.

## Category Hierarchy

### Main Categories (2)
- **Dog** (`dog`)
- **Cat** (`cat`)

### Dog Food Categories (7)

#### Adult Dog Food (`adult-dog`)
- Adult Dog Dry Food (`adult-dog-dry-food`)
- Adult Dog Wet Food (`adult-dog-wet-food`)
- Fresh Dog Food (`woof-fetch/fresh-food`)

#### Puppy Food (`puppy`)
- Puppy Dry Food (`puppy-dry-food`)
- Puppy Wet Food (`wet-puppy-food`)
- Dog Milk (`dog-milk`)

### Dog Treats & Snacks (4)

#### Bones, Snacks & Treats (`bones-snacks`)
- Dog Bones (`bones`)
- Dog Snacks (`dog-snacks`)
- Dog Treats (`dog-treats`)

### Dog Grooming & Healthcare (4)

#### Grooming & Healthcare (`grooming-healthcare`)
- Dog Grooming (`grooming`)
- Flea & Tick Treatments (`dog-flea-tick-treatments`)
- Dog Supplements (`dog-supplements`)

### Dog Accessories (4)

#### Dog Accessories (`dog-accessories`)
- Dog Toys (`dog-toys`)
- Dog Beds (`dog-beds`)
- Dog Bowls (`dog-bowls`)

### Special Categories (2)
- **Offers & Sales** (`end-of-year-sale`) - ENABLED
- **Amin Clinic** (`amin-clinic`) - DISABLED (services only)

## Category URLs

All categories follow the pattern:
```
https://aminpetshop.com/collections/{category-id}
```

Examples:
- `https://aminpetshop.com/collections/adult-dog-dry-food`
- `https://aminpetshop.com/collections/dog-toys`
- `https://aminpetshop.com/collections/end-of-year-sale`

## Import Settings

### Enabled for Import (26 categories)
All categories except "Amin Clinic" are enabled for import by default.

### Disabled for Import (1 category)
- **Amin Clinic** - Contains service listings, not physical products

### Auto-Create Categories
All categories have `auto_create_category` enabled, meaning Odoo will automatically create corresponding product categories if they don't exist.

## Parent-Child Relationships

| Parent Category | Child Categories |
|----------------|------------------|
| dog | adult-dog, puppy, bones-snacks, grooming-healthcare, dog-accessories |
| adult-dog | adult-dog-dry-food, adult-dog-wet-food, woof-fetch/fresh-food |
| puppy | puppy-dry-food, wet-puppy-food, dog-milk |
| bones-snacks | bones, dog-snacks, dog-treats |
| grooming-healthcare | grooming, dog-flea-tick-treatments, dog-supplements |
| dog-accessories | dog-toys, dog-beds, dog-bowls |

## Sequence Numbers

Categories are ordered by sequence numbers:
- Special categories: 5
- Main categories: 10-20
- Dog food: 100-113
- Treats & snacks: 120-123
- Grooming & healthcare: 130-133
- Accessories: 140-143
- Clinic: 200

## Usage Notes

### Importing by Category
1. Navigate to: **Unified Scrapper → Configuration → Category Mappings**
2. Select a category (e.g., "Adult Dog Dry Food")
3. Click **"Import Products"** button
4. Products from that category will be imported with proper categorization

### Mapping to Odoo Categories
1. Open a category mapping record
2. Set the **"Odoo Product Category"** field
3. Or click **"Create Odoo Category"** to auto-create

### Disabling Categories
To skip importing certain categories:
1. Open the category mapping
2. Uncheck **"Enable Import"**
3. Save

### Tracking Statistics
Each category shows:
- **Product Count**: Total products in external source
- **Products Imported**: Number of products imported to Odoo
- **Last Sync Date**: When category was last synced

## Future Expansion

### Cat Categories
The "Cat" main category is ready for expansion. Add cat-specific subcategories as needed:
- Cat Food (Dry, Wet, Kitten)
- Cat Treats
- Cat Grooming
- Cat Accessories
- Cat Toys
- Cat Litter

### Other Categories
Additional categories can be added as Amin Petshop expands their catalog:
- Birds
- Fish & Aquariums
- Small Animals (Rabbits, Hamsters, etc.)
- Reptiles

## Technical Details

### Model
- **Model Name**: `unified.category.mapping`
- **Data File**: `data/amin_petshop_categories.xml`

### Fields
- `data_source_id`: Reference to Amin Petshop data source
- `external_category_id`: Category ID from Amin Petshop
- `external_category_name`: Display name
- `external_category_url`: Full URL to category page
- `external_parent_id`: Parent category ID (if applicable)
- `odoo_category_id`: Mapped Odoo product category
- `import_enabled`: Whether to include in imports
- `auto_create_category`: Auto-create Odoo category
- `sequence`: Display order
- `product_count`: Number of products (from external source)
- `products_imported`: Number imported to Odoo
- `last_sync_date`: Last sync timestamp

## Troubleshooting

### Categories Not Showing
1. Ensure module is upgraded
2. Check: **Unified Scrapper → Configuration → Category Mappings**
3. Verify data source is "Amin Petshop"

### Import Not Working
1. Verify category has `import_enabled = True`
2. Check category URL is accessible
3. Ensure data source has valid credentials/cookies

### Duplicate Products
The import wizard handles duplicates by:
- Matching by external product ID
- Adding vendor prices for existing products
- Updating product information if needed

## Contact & Support

For issues or questions about category mappings, refer to:
- Main documentation: `unified_scrapper/document/unified_scrapper_plan.md`
- Import wizard documentation: Check wizard help text in Odoo

