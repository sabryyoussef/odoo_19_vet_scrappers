# Category-Filtered Import Testing Guide

## Overview
This guide will walk you through testing the category-filtered import feature step by step.

## Prerequisites

### 1. Upgrade the Module
```
1. Go to: http://localhost:8070
2. Navigate to: Apps
3. Search: "Unified Product Scrapper"
4. Click: "Upgrade" button
5. Wait for upgrade to complete
```

### 2. Test Data File
A sample test file is provided at:
```
/home/sabry3/odoo_19_vetutions/addons/unified_scrapper/tests/sample_test_data.json
```

This file contains **10 products** across **7 different categories**:
- 3 × Adult Dog Dry Food
- 2 × Puppy Dry Food
- 1 × Dog Bones
- 1 × Dog Treats
- 1 × Dog Grooming
- 1 × Flea & Tick Treatments
- 1 × Dog Toys

---

## Test Scenario 1: View Category Mappings

### Objective
Verify that all 27 Amin Petshop categories are loaded.

### Steps
1. Navigate to: **Unified Scrapper → Configuration → Category Mappings**
2. You should see a list of categories

### Expected Results
✅ **27 categories** displayed
✅ Categories organized by sequence
✅ "Import Enabled" toggle visible
✅ Categories include:
   - Dog
   - Cat
   - Adult Dog Dry Food
   - Puppy Dry Food
   - Dog Bones
   - Dog Treats
   - Dog Grooming
   - Flea & Tick Treatments
   - Dog Toys
   - And 18 more...

### Verification
- [ ] All 27 categories visible
- [ ] Can filter by "Import Enabled"
- [ ] Can search by name
- [ ] Can group by "Data Source"

---

## Test Scenario 2: Import WITHOUT Category Filter

### Objective
Test standard import (all categories) to establish baseline.

### Steps
1. Navigate to: **Unified Scrapper → Operations → Import Products**
2. Click: **"New"** or **"Import Products"** button
3. **Upload File**:
   - Click "Choose File"
   - Select: `addons/unified_scrapper/tests/sample_test_data.json`
   - Click: **"Next"**
4. **Configure Import**:
   - Source System: **Amin Petshop**
   - Match Strategy: **By URL or SKU**
   - If Product Exists: **Add as Vendor Price**
   - Create Vendor Prices: ✓ **Checked**
   - Update Cost Price: ✓ **Checked**
   - Cost Price Strategy: **Use Lowest Vendor Price**
   - Click: **"Preview"**
5. **Review Preview**:
   - Should show "Found **10** records in file"
   - Preview shows first few products
   - Click: **"Import Now"**
6. **Review Results**:
   - Wait for import to complete
   - Check import statistics

### Expected Results
✅ **10 products** imported (all products)
✅ **0 skipped** (no category filter)
✅ **10 vendor prices** created
✅ Import log shows all products processed
✅ No category filter mentioned in log

### Verification
- [ ] Products Created: 10
- [ ] Products Skipped: 0
- [ ] Vendor Prices Created: 10
- [ ] Import log shows success
- [ ] No errors in error log

### View Imported Products
1. Click: **"View Products"** button
2. Should see all 10 products
3. Check product details:
   - External Source: **amin_petshop**
   - External Category ID: (varies)
   - External Category Name: (varies)
   - Vendor Prices tab: 1 vendor price

---

## Test Scenario 3: Import WITH Category Filter (Adult Dog Dry Food)

### Objective
Test category-filtered import - only import adult dog dry food products.

### Steps
1. Navigate to: **Unified Scrapper → Configuration → Category Mappings**
2. Find and open: **"Adult Dog Dry Food"**
3. Click: **"Import Products"** button (in header)
4. **Verify Filter Set**:
   - Category Name field should show: **"Adult Dog Dry Food"** (read-only)
   - This confirms filter is active
5. **Upload File**:
   - Click "Choose File"
   - Select: `addons/unified_scrapper/tests/sample_test_data.json`
   - Click: **"Next"**
6. **Configure Import**:
   - Source System: **Amin Petshop** (auto-selected)
   - Match Strategy: **By URL or SKU**
   - If Product Exists: **Update (Merge Data)** (to test updates)
   - Create Vendor Prices: ✓ **Checked**
   - Update Cost Price: ✓ **Checked**
   - Click: **"Preview"**
7. **Review Preview**:
   - Should show "Found **10** records in file" (total)
   - But only 3 will be imported (filtered)
   - Click: **"Import Now"**
8. **Review Results**:
   - Check import statistics
   - Review import log

### Expected Results
✅ **0 products created** (already exist from Test 2)
✅ **3 products updated** (Royal Canin, Pedigree, Farmina)
✅ **7 products skipped** (category filter)
✅ Import log shows:
   - "Category Filter: Adult Dog Dry Food"
   - "Skipped (category filter: puppy-dry-food != adult-dog-dry-food)"
   - "Skipped (category filter: bones != adult-dog-dry-food)"
   - etc.

### Verification
- [ ] Products Updated: 3
- [ ] Products Skipped: 7
- [ ] Import log mentions "Category Filter: Adult Dog Dry Food"
- [ ] Skipped products show category mismatch reason
- [ ] Only adult dog dry food products updated

### View Updated Products
1. Click: **"View Products"** button
2. Should see only **3 products** (adult dog dry food)
3. Check update count:
   - External Update Count: **2** (1 from initial import + 1 from this import)

---

## Test Scenario 4: Import Multiple Categories Sequentially

### Objective
Test importing different categories one by one.

### Steps

#### 4A: Import Puppy Dry Food
1. Navigate to: **Category Mappings**
2. Open: **"Puppy Dry Food"**
3. Click: **"Import Products"**
4. Upload: `sample_test_data.json`
5. Configure and import

**Expected:**
- ✅ 2 products updated (Royal Canin Puppy, Pedigree Puppy)
- ✅ 8 products skipped (other categories)

#### 4B: Import Dog Treats
1. Navigate to: **Category Mappings**
2. Open: **"Dog Treats"**
3. Click: **"Import Products"**
4. Upload: `sample_test_data.json`
5. Configure and import

**Expected:**
- ✅ 1 product updated (Dog Treats Chicken Flavor)
- ✅ 9 products skipped (other categories)

#### 4C: Import Dog Toys
1. Navigate to: **Category Mappings**
2. Open: **"Dog Toys"**
3. Click: **"Import Products"**
4. Upload: `sample_test_data.json`
5. Configure and import

**Expected:**
- ✅ 1 product updated (Dog Toy Rubber Ball)
- ✅ 9 products skipped (other categories)

### Verification
- [ ] Each import only updates products from selected category
- [ ] Other categories are skipped
- [ ] Import logs clearly show category filter
- [ ] No errors

---

## Test Scenario 5: View Import History

### Objective
Verify import history tracking.

### Steps
1. Navigate to: **Unified Scrapper → Operations → Import History**
2. You should see all import records from previous tests

### Expected Results
✅ Multiple import history records
✅ Each record shows:
   - Import Date
   - User
   - Data Source: Amin Petshop
   - Status: Success
   - Products Created/Updated/Skipped/Failed
   - Duration

### Verification
- [ ] All imports logged
- [ ] Statistics match actual results
- [ ] Can view detailed import log
- [ ] Can view error log (if any)

---

## Test Scenario 6: View Vendor Prices

### Objective
Verify vendor prices were created correctly.

### Steps
1. Navigate to: **Unified Scrapper → Products → Vendor Prices**
2. You should see all vendor price records

### Expected Results
✅ **10 vendor price records** (one per product)
✅ Each record shows:
   - Product name
   - Data Source: Amin Petshop
   - Price
   - Availability: In Stock
   - Stock Quantity
   - External URL (clickable)

### Verification
- [ ] All 10 products have vendor prices
- [ ] Prices match test data
- [ ] External URLs are clickable
- [ ] Can filter by data source
- [ ] Can search by product name

---

## Test Scenario 7: View Products by Category

### Objective
Verify products are properly categorized.

### Steps
1. Navigate to: **Unified Scrapper → Products → Amin Petshop Products**
2. You should see all 10 imported products

### Verification
- [ ] All 10 products visible
- [ ] External Source: amin_petshop
- [ ] External Category ID populated
- [ ] External Category Name populated
- [ ] Can filter by category

### Check Individual Product
1. Open: **"Royal Canin Adult Dog Dry Food 15kg"**
2. Go to: **"External Source"** tab
3. Verify:
   - External Source: amin_petshop
   - External Product ID: RC-ADULT-15KG
   - External Product URL: (clickable link)
   - External Category ID: adult-dog-dry-food
   - External Category Name: Adult Dog Dry Food
   - External Sync Status: synced
   - External Update Count: 2 (or more)
4. Go to: **"Vendor Prices"** tab
5. Verify:
   - 1 vendor price record
   - Data Source: Amin Petshop
   - Price: 1250.00
   - External URL: (clickable)

---

## Test Scenario 8: Test Category Statistics

### Objective
Verify category statistics are tracked.

### Steps
1. Navigate to: **Category Mappings**
2. Open: **"Adult Dog Dry Food"**
3. Check statistics:
   - Products Imported: Should show count
   - Last Sync Date: Should show recent date

### Note
Statistics are updated when products are imported through the category's "Import Products" button. Manual imports may not update these statistics.

---

## Test Scenario 9: Create Odoo Category Mapping

### Objective
Test mapping external categories to Odoo product categories.

### Steps
1. Navigate to: **Category Mappings**
2. Open: **"Adult Dog Dry Food"**
3. Click: **"Create Odoo Category"** button (if not already mapped)
4. A new Odoo product category should be created

### Expected Results
✅ Odoo Product Category created: "Adult Dog Dry Food"
✅ Category mapping updated with Odoo category
✅ Success notification displayed

### Verification
- [ ] Odoo category created
- [ ] Category mapping shows Odoo category
- [ ] "Create Odoo Category" button hidden (already mapped)

### View Odoo Category
1. Navigate to: **Inventory → Configuration → Product Categories**
2. Find: **"Adult Dog Dry Food"**
3. Verify it exists

---

## Test Scenario 10: Test with CSV File

### Objective
Test category filtering with CSV format.

### Steps
1. Create a CSV file: `test_products.csv`

```csv
name,sku,price,external_category_id,external_category_name,url
Test Product 1,TEST-001,100.00,adult-dog-dry-food,Adult Dog Dry Food,https://aminpetshop.com/products/test-001
Test Product 2,TEST-002,200.00,puppy-dry-food,Puppy Dry Food,https://aminpetshop.com/products/test-002
```

2. Navigate to: **Category Mappings → Adult Dog Dry Food**
3. Click: **"Import Products"**
4. Upload: `test_products.csv`
5. Configure and import

### Expected Results
✅ 1 product imported (Test Product 1)
✅ 1 product skipped (Test Product 2 - different category)

### Verification
- [ ] CSV import works
- [ ] Category filtering works with CSV
- [ ] Only matching category imported

---

## Common Issues & Troubleshooting

### Issue 1: All Products Skipped
**Symptom:** Import log shows all products skipped by category filter

**Cause:** Category IDs in file don't match filter

**Solution:**
1. Check import log for actual category IDs
2. Verify category mapping has correct `external_category_id`
3. Ensure file uses same category ID format

---

### Issue 2: Category Filter Not Working
**Symptom:** All products imported regardless of category

**Cause:** Category filter not set or file missing category fields

**Solution:**
1. Verify "Category Name" field shows in wizard
2. Check file includes `external_category_id` or `category_id` fields
3. Try opening wizard from category mapping (not direct import)

---

### Issue 3: Products Not Categorized
**Symptom:** Products imported but no category information

**Cause:** File missing category fields

**Solution:**
1. Add `external_category_id` and `external_category_name` to file
2. Re-import products with "Update" action

---

### Issue 4: Duplicate Products
**Symptom:** Same product imported multiple times

**Cause:** Match strategy not finding existing products

**Solution:**
1. Use "By URL or SKU" match strategy
2. Ensure products have unique URLs or SKUs
3. Use "Add as Vendor Price" for duplicates

---

## Success Criteria

Your testing is successful if:

- [ ] ✅ All 27 categories loaded
- [ ] ✅ Import without filter: 10 products imported
- [ ] ✅ Import with filter: Only matching category imported
- [ ] ✅ Import log shows category filter
- [ ] ✅ Skipped products show category mismatch
- [ ] ✅ Vendor prices created correctly
- [ ] ✅ Products properly categorized
- [ ] ✅ Import history tracked
- [ ] ✅ CSV and JSON formats work
- [ ] ✅ Odoo category mapping works

---

## Next Steps After Testing

Once testing is successful:

1. **Create Real Data Files**
   - Export products from Amin Petshop
   - Include all required fields
   - Ensure category IDs match mappings

2. **Import Production Data**
   - Start with small categories
   - Verify results before proceeding
   - Import larger categories

3. **Create Categories for Other Sources**
   - Vetution categories
   - Amazon categories
   - Custom sources

4. **Integrate with Scraper**
   - Connect `universal_scraper_odoo` module
   - Automate category sync
   - Schedule regular imports

---

## Support

For issues or questions:
- Check: `category_filtered_import_guide.md`
- Check: `amin_petshop_categories_reference.md`
- Review import logs for detailed error messages
- Check Odoo logs: `docker-compose logs odoo`

---

## Test Data Summary

The `sample_test_data.json` file contains:

| Product | SKU | Category | Price |
|---------|-----|----------|-------|
| Royal Canin Adult Dog Dry Food 15kg | RC-ADULT-15KG | adult-dog-dry-food | 1250.00 |
| Pedigree Adult Dry Food 10kg | PED-ADULT-10KG | adult-dog-dry-food | 850.00 |
| Farmina N&D Adult Dog Dry Food 12kg | FAR-ADULT-12KG | adult-dog-dry-food | 1450.00 |
| Royal Canin Puppy Dry Food 8kg | RC-PUPPY-8KG | puppy-dry-food | 950.00 |
| Pedigree Puppy Dry Food 6kg | PED-PUPPY-6KG | puppy-dry-food | 650.00 |
| Dog Chew Bones Pack of 5 | BONE-PACK-5 | bones | 120.00 |
| Dog Treats Chicken Flavor 500g | TREAT-CHICKEN-500G | dog-treats | 95.00 |
| Dog Shampoo Sensitive Skin 500ml | SHAMP-SENS-500ML | grooming | 180.00 |
| Flea & Tick Treatment 3 Doses | FLEA-TREAT-3D | dog-flea-tick-treatments | 350.00 |
| Dog Toy Rubber Ball Large | TOY-BALL-L | dog-toys | 75.00 |

**Total:** 10 products across 7 categories

