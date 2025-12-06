# Category-Filtered Import Guide

## Overview
The category-filtered import feature allows you to import products selectively by category, making imports faster and more organized.

## How It Works

### 1. From Category Mapping
The easiest way to use category-filtered import:

1. Navigate to: **Unified Scrapper → Configuration → Category Mappings**
2. Open any category (e.g., "Adult Dog Dry Food")
3. Click the **"Import Products"** button
4. The import wizard opens with the category filter already set
5. Upload your file and proceed with import

### 2. Category Filter Behavior
When a category filter is active:
- Only products with matching `external_category_id` are imported
- Products from other categories are **skipped** (not failed)
- Skipped products are logged for reference
- Import statistics show how many were filtered

### 3. Data File Requirements

Your JSON or CSV files **must include** category information:

#### JSON Format
```json
{
  "products": [
    {
      "name": "Royal Canin Adult Dog Food",
      "sku": "RC-ADULT-001",
      "price": 450.00,
      "external_category_id": "adult-dog-dry-food",
      "external_category_name": "Adult Dog Dry Food",
      "url": "https://aminpetshop.com/products/royal-canin-adult"
    }
  ]
}
```

#### CSV Format
```csv
name,sku,price,external_category_id,external_category_name,url
Royal Canin Adult Dog Food,RC-ADULT-001,450.00,adult-dog-dry-food,Adult Dog Dry Food,https://aminpetshop.com/products/royal-canin-adult
```

#### Supported Field Names
The import wizard recognizes these field names for categories:
- `external_category_id`, `category_id`, `category`
- `external_category_name`, `category_name`, `category_title`

## Import Log Example

```
Starting import of 150 records...
Source: amin_petshop
Match Strategy: url_or_sku
Duplicate Action: add_vendor
Category Filter: Adult Dog Dry Food
════════════════════════════════════════════════════════════

Processing record 1/150...
  ✓ Created: Royal Canin Adult Dog Food

Record 2: Skipped (category filter: puppy-dry-food != adult-dog-dry-food)

Processing record 3/150...
  ✓ Added vendor price: Pedigree Adult Dry Food

Record 4: Skipped (category filter: dog-toys != adult-dog-dry-food)

...

════════════════════════════════════════════════════════════
IMPORT COMPLETE
Duration: 45.23 seconds
Created: 35
Updated: 20
Skipped: 95 (70 by category filter, 25 duplicates)
Failed: 0
Vendor Prices Created: 20
```

## Use Cases

### Use Case 1: Import Single Category
**Scenario:** You only want to import dog food products from a large file containing all products.

**Steps:**
1. Go to Category Mappings
2. Open "Adult Dog Dry Food"
3. Click "Import Products"
4. Upload file with all products
5. Only dog food products are imported

**Result:** Faster import, only relevant products added.

---

### Use Case 2: Incremental Category Import
**Scenario:** Import products category by category to organize your catalog.

**Steps:**
1. Day 1: Import "Adult Dog Dry Food"
2. Day 2: Import "Puppy Food"
3. Day 3: Import "Dog Treats"
4. Continue for each category

**Result:** Organized import process, easier to review and verify.

---

### Use Case 3: Testing with Small Dataset
**Scenario:** Test import with a small category before importing everything.

**Steps:**
1. Select a small category (e.g., "Dog Milk" - few products)
2. Import and verify
3. If successful, proceed with larger categories

**Result:** Reduced risk, easier troubleshooting.

---

### Use Case 4: Selective Product Range
**Scenario:** You only sell certain product categories.

**Steps:**
1. Disable unwanted categories in Category Mappings
2. Import only enabled categories
3. Skip toys, accessories, etc. if you don't sell them

**Result:** Clean catalog, no irrelevant products.

## Benefits

### Performance
- **Faster imports**: Skip irrelevant products early
- **Less processing**: Don't create/check products you don't need
- **Reduced memory**: Process smaller datasets

### Organization
- **Better categorization**: Products are categorized during import
- **Easier review**: Review one category at a time
- **Clear logs**: See exactly what was filtered

### Flexibility
- **Selective importing**: Choose what to import
- **Incremental updates**: Update one category at a time
- **Testing**: Test with small categories first

## Technical Details

### Category Matching
The filter compares:
```python
record_category == category_filter
```

Both are converted to strings for comparison, so these are equivalent:
- `"adult-dog-dry-food"` == `"adult-dog-dry-food"` ✓
- `123` == `"123"` ✓

### Field Extraction Priority
The wizard checks these fields in order:
1. `external_category_id`
2. `category_id`
3. `category`

First match wins.

### Storage in Odoo
Imported products store category information in:
- `external_category_id` (Char field)
- `external_category_name` (Char field)

These fields are on `product.product` model.

## Troubleshooting

### Problem: All products skipped
**Cause:** Category IDs in file don't match filter

**Solution:**
1. Check import log for actual category IDs
2. Verify category mapping has correct `external_category_id`
3. Ensure file uses same category ID format

---

### Problem: Some products imported, some skipped
**Cause:** File contains multiple categories

**Solution:** This is normal! The filter is working correctly.
- Check import log to see which categories were skipped
- If you want all products, don't use category filter

---

### Problem: Category fields not stored in products
**Cause:** File doesn't include category fields

**Solution:**
1. Add `external_category_id` and `external_category_name` to your data file
2. Re-import

---

### Problem: Can't find "Import Products" button
**Cause:** Category mapping form view not showing button

**Solution:**
1. Ensure module is upgraded to v19.0.4.2.0 or later
2. Refresh browser
3. Check you're on the category mapping form view (not list view)

## Best Practices

### 1. Always Include Category Fields
Even if not using filters, include category fields in your data files for:
- Better organization
- Future filtering
- Reporting and analytics

### 2. Use Consistent Category IDs
Use the same category ID format across all your data sources:
- `adult-dog-dry-food` ✓
- `adult_dog_dry_food` ✗ (different format)

### 3. Test with Small Categories First
Before importing large categories:
1. Test with a small category (5-10 products)
2. Verify results
3. Then proceed with larger imports

### 4. Review Import Logs
Always check import logs to:
- Verify correct products were imported
- See what was skipped
- Identify any issues

### 5. Map Categories to Odoo
After importing:
1. Go to Category Mappings
2. Map external categories to Odoo product categories
3. Or click "Create Odoo Category" to auto-create

## API Reference

### Wizard Fields
```python
category_filter = fields.Char(
    string='Category Filter',
    help='Filter products by category ID'
)

category_name = fields.Char(
    string='Category Name',
    help='Display name of filtered category'
)
```

### Context for Opening Wizard
```python
{
    'default_data_source_id': data_source.id,
    'default_category_filter': 'adult-dog-dry-food',
    'default_category_name': 'Adult Dog Dry Food',
}
```

### Product Fields
```python
external_category_id = fields.Char(
    string='External Category ID'
)

external_category_name = fields.Char(
    string='External Category Name'
)
```

## See Also
- [Amin Petshop Categories Reference](amin_petshop_categories_reference.md)
- [Unified Scrapper Plan](unified_scrapper_plan.md)
- Import Wizard documentation (in Odoo help text)

