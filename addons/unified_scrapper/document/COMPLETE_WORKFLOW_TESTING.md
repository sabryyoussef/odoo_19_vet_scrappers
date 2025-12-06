# Complete Workflow Testing Guide

## Overview
This guide walks you through testing the complete end-to-end workflow from category selection to final product import, including the new "Scrape & Import" feature.

---

## Prerequisites

- Odoo 19 running at http://localhost:8070
- Both modules installed:
  - Universal Web Scraper
  - Unified Product Scrapper

---

## Testing Timeline

**Total Time: 30 minutes**

- Step 1: Upgrade Modules (5 min)
- Step 2: Verify Configurations (3 min)
- Step 3: Test "Scrape & Import" (10 min)
- Step 4: Review Scraped Products (5 min)
- Step 5: Import to Unified Scrapper (5 min)
- Step 6: Verify Final Products (5 min)

---

## STEP 1: Upgrade Both Modules (5 minutes)

### Actions

1. **Open Odoo**
   ```
   http://localhost:8070
   ```

2. **Upgrade Universal Scraper**
   - Navigate to: **Apps**
   - Search: "Universal Web Scraper"
   - Click: **"Upgrade"** button
   - Wait for completion

3. **Upgrade Unified Scrapper**
   - Search: "Unified Product Scrapper"
   - Click: **"Upgrade"** button
   - Wait for completion

### Expected Results

✅ Both modules upgraded successfully  
✅ No errors in upgrade process  
✅ Version updated to:
- Universal Scraper: 19.0.1.1.1
- Unified Scrapper: 19.0.4.3.0

---

## STEP 2: Verify Configurations (3 minutes)

### 2.1 Check Scraper Configurations

**Navigate to:** Universal Scraper → Configuration → Scraper Configs

**Expected: 6 configurations visible**

1. ✅ Amin Petshop - Offers & Sales
2. ✅ Amin Petshop - Adult Dog Dry Food
3. ✅ Amin Petshop - Puppy Dry Food
4. ✅ Amin Petshop - Dog Treats
5. ✅ Amin Petshop - Dog Toys
6. ✅ Vetution - All Products (inactive)

**Verify each config has:**
- Platform Type: shopify (or generic for Vetution)
- Max Pages: 5-10
- Data Source: Linked to Amin Petshop or Vetution
- Active: True (except Vetution)

### 2.2 Check Category Mappings

**Navigate to:** Unified Scrapper → Configuration → Category Mappings

**Expected: 27 categories visible**

Key categories to verify:
- ✅ Offers & Sales
- ✅ Adult Dog Dry Food
- ✅ Puppy Dry Food
- ✅ Dog Treats
- ✅ Dog Toys
- ✅ Dog Bones
- ✅ Dog Grooming
- ✅ ... and 20 more

### 2.3 Check Data Sources

**Navigate to:** Unified Scrapper → Configuration → Data Sources

**Expected: 4 data sources**

1. ✅ Vetution
2. ✅ Amin Petshop
3. ✅ Amazon
4. ✅ Generic E-commerce

---

## STEP 3: Test "Scrape & Import" (10 minutes)

### This is the MAIN test - automatic scraping from category!

### 3.1 Navigate to Category

**Path:** Unified Scrapper → Configuration → Category Mappings

**Action:** Open "Offers & Sales" category

### 3.2 Verify Button Layout

**You should see TWO buttons in the header:**

```
[Scrape & Import]  [Import from File]  [Create Odoo Category]
     (Blue)              (Gray)              (Gray)
```

- **Scrape & Import** = Primary button (blue) - NEW!
- **Import from File** = Secondary button (gray) - Existing
- **Create Odoo Category** = Secondary button (gray)

### 3.3 Click "Scrape & Import"

**Action:** Click the blue **"Scrape & Import"** button

### 3.4 Expected Behavior

**One of two things will happen:**

#### Option A: Scraping Starts (Success)
```
✅ Notification: "Scraping Started"
✅ Message: "Scraping products from Offers & Sales. 
            Check scraped products in Universal Scraper module."
✅ Opens: Scraped products view
```

#### Option B: Warning Message
```
⚠️  "Scraper Not Available"
⚠️  "Universal Scraper module is not installed. 
     Please install it or use manual file import."
```

If you get Option B:
- Universal Scraper module not working
- Check module is installed and upgraded
- Check logs: `docker-compose logs odoo | tail -100`

### 3.5 Monitor Scraping Progress

If scraping started successfully:

1. **Check Scraper Jobs**
   - Navigate to: Universal Scraper → Operations → Scraper Jobs
   - Should see: New job with status "Running" or "Completed"
   - Job details:
     - Config: Amin Petshop - Offers & Sales
     - Status: Running → Completed
     - Products Scraped: [count]

2. **Wait for Completion**
   - Time: 1-5 minutes (depends on number of products)
   - Don't close the browser
   - Check job status periodically

### Expected Results

✅ Scraper config created or found  
✅ Scraping job started  
✅ Job completes successfully  
✅ Products appear in drafts  
✅ No errors in job log

---

## STEP 4: Review Scraped Products (5 minutes)

### 4.1 Navigate to Scraped Products

**Path:** Universal Scraper → Scraped Products

### 4.2 Filter by Scraper Config

**Action:** Use search/filter to select "Amin Petshop - Offers & Sales"

### 4.3 Review Product List

**Expected: 10-50 products in draft state**

Example products you might see:
- Royal Canin Adult Dog Dry Food 15kg - 1250 EGP
- Pedigree Adult Dry Food 10kg - 850 EGP
- Farmina N&D Adult Dog Dry Food 12kg - 1450 EGP
- ... more products

### 4.4 Check Product Details

**Open a product and verify:**

- ✅ Product Name: Captured correctly
- ✅ Price: Present and correct
- ✅ Description: Captured (if available)
- ✅ Image URL: Present (if available)
- ✅ External URL: Link to original product
- ✅ Availability: In Stock / Out of Stock
- ✅ State: Draft
- ✅ Scraper Config: Amin Petshop - Offers & Sales

### 4.5 Edit Products (Optional)

**You can edit products before import:**

1. Open a product
2. Modify: name, price, description, etc.
3. Save changes
4. Changes will be imported

### Expected Results

✅ Products visible in draft state  
✅ Product details captured correctly  
✅ Can view and edit products  
✅ External URLs are valid

---

## STEP 5: Import to Unified Scrapper (5 minutes)

### 5.1 Select Products to Import

**Navigate to:** Universal Scraper → Scraped Products

**Actions:**
1. Filter by "Amin Petshop - Offers & Sales"
2. Select products:
   - Select all (checkbox in header)
   - OR select specific products
3. Click: **Action** dropdown
4. Select: **"Import to Unified Scrapper"**

### 5.2 Import Wizard Opens

**Expected: Import wizard form**

**Configure import settings:**

1. **Data Source** (Required)
   - Select: **"Amin Petshop"**
   - This links products to the data source

2. **Match Strategy**
   - Select: **"By URL or SKU"**
   - Prevents duplicates

3. **Duplicate Action**
   - Select: **"Add as Vendor Price"**
   - Adds price to existing products instead of creating duplicates

4. **Additional Options:**
   - ✅ Create Vendor Prices: Checked
   - ✅ Update Cost Price: Checked
   - Cost Price Strategy: "Use Lowest Vendor Price"

### 5.3 Execute Import

**Action:** Click **"Import"** button

**Expected:**
- Progress notification
- Import processing
- Completion message

### 5.4 Review Import Results

**Import wizard shows:**
- Products Created: [count]
- Products Updated: [count]
- Products Skipped: [count]
- Vendor Prices Created: [count]
- Status: Success

### Expected Results

✅ Import wizard opens correctly  
✅ Can configure import options  
✅ Import executes successfully  
✅ Products created or updated  
✅ Vendor prices created  
✅ No errors

---

## STEP 6: Verify Final Products (5 minutes)

### 6.1 Navigate to Products

**Path:** Unified Scrapper → Products → Amin Petshop Products

**Expected: Imported products visible**

### 6.2 Check Product List

**Verify:**
- ✅ All imported products visible
- ✅ Product names correct
- ✅ Prices displayed
- ✅ External Source: amin_petshop

### 6.3 Open a Product

**Select:** Any imported product (e.g., "Royal Canin Adult Dog Dry Food 15kg")

### 6.4 Verify "External Source" Tab

**Navigate to:** External Source tab

**Check fields:**
- ✅ External Source: amin_petshop
- ✅ External Product ID: [SKU or ID]
- ✅ External Product URL: [clickable link to Amin Petshop]
- ✅ External Category ID: end-of-year-sale
- ✅ External Category Name: Offers & Sales
- ✅ External Sync Status: synced
- ✅ External Last Sync: [recent timestamp]
- ✅ External Update Count: 1 (or more)

### 6.5 Verify "Vendor Prices" Tab

**Navigate to:** Vendor Prices tab

**Expected: 1 vendor price record**

**Check fields:**
- ✅ Data Source: Amin Petshop
- ✅ Price: [from scraped data, e.g., 1250.00]
- ✅ Currency: EGP
- ✅ Availability: In Stock
- ✅ Stock Quantity: [if available]
- ✅ External URL: [clickable link]
- ✅ Last Updated: [recent timestamp]
- ✅ Active: True

### 6.6 Test External URL

**Action:** Click the external URL in vendor price

**Expected:**
- ✅ Opens in new browser tab
- ✅ Goes to Amin Petshop product page
- ✅ Correct product displayed

### 6.7 Check Import History

**Navigate to:** Unified Scrapper → Operations → Import History

**Expected: Import record visible**

**Verify:**
- ✅ Import Date: Recent
- ✅ User: Your username
- ✅ Data Source: Amin Petshop
- ✅ Status: Success
- ✅ Products Created: [count]
- ✅ Products Updated: [count]
- ✅ Products Skipped: [count]
- ✅ Duration: [seconds]

**Open import record:**
- ✅ Import Log: Detailed log of import process
- ✅ Error Log: Empty (no errors)

### Expected Results

✅ Products created with all data  
✅ Vendor prices created correctly  
✅ Categories assigned properly  
✅ External URLs work  
✅ Import history tracked  
✅ No errors or missing data

---

## STEP 7: Test Alternative Workflow (Optional - 5 minutes)

### Test manual scraper run without category button

### 7.1 Navigate to Scraper Configs

**Path:** Universal Scraper → Configuration → Scraper Configs

### 7.2 Select a Different Config

**Action:** Open "Amin Petshop - Dog Treats"

### 7.3 Run Scraper Manually

**Action:** Click **"Scrape Now"** button in header

**Expected:**
- ✅ Notification: "Scraping job started"
- ✅ Job created

### 7.4 Check Job Status

**Navigate to:** Universal Scraper → Operations → Scraper Jobs

**Verify:**
- ✅ New job visible
- ✅ Config: Amin Petshop - Dog Treats
- ✅ Status: Running → Completed
- ✅ Products Scraped: [count]

### 7.5 Import Products

**Follow steps 4-6 above:**
1. Review scraped products
2. Import to Unified Scrapper
3. Verify final products

### Expected Results

✅ Manual scraping works  
✅ Job tracked correctly  
✅ Products scraped  
✅ Can import successfully

---

## Testing Checklist

### Basic Tests
- [ ] Both modules upgraded successfully
- [ ] 6 scraper configs visible
- [ ] 27 category mappings visible
- [ ] 4 data sources visible
- [ ] "Scrape & Import" button visible on category form
- [ ] "Import from File" button visible on category form

### Scraping Tests
- [ ] Click "Scrape & Import" works
- [ ] Scraper config created or found
- [ ] Scraping job starts
- [ ] Job completes successfully
- [ ] Products appear in drafts
- [ ] Product details captured correctly

### Import Tests
- [ ] Can select draft products
- [ ] Import wizard opens
- [ ] Can configure import options
- [ ] Import executes successfully
- [ ] Products created or updated
- [ ] Vendor prices created
- [ ] Categories assigned

### Verification Tests
- [ ] Products visible in Amin Petshop Products
- [ ] External Source data correct
- [ ] External URLs clickable and working
- [ ] Vendor prices correct
- [ ] Import history tracked
- [ ] No errors in logs

---

## Success Criteria

Your testing is **SUCCESSFUL** if:

✅ Can click "Scrape & Import" from category  
✅ Scraping starts automatically  
✅ Products appear in drafts  
✅ Can review before import  
✅ Import creates products with vendor prices  
✅ Categories properly assigned  
✅ External URLs work  
✅ No errors in process

---

## Troubleshooting

### Problem: "Scraper Not Available" warning

**Cause:** Universal Scraper module not installed or not working

**Solution:**
1. Check module is installed: Apps → "Universal Web Scraper"
2. Check module is upgraded to latest version
3. Check logs: `docker-compose logs odoo | tail -100`
4. Restart Odoo if needed: `docker-compose restart odoo`

---

### Problem: No products scraped

**Cause:** Website may be blocking scraper or authentication required

**Solution:**
1. Check scraper job logs for errors
2. Check if website requires login
3. Add cookies for authentication:
   - Go to Data Source
   - Paste browser cookies in "Session Cookies" field
4. Reduce max_pages to 1 for testing

---

### Problem: Scraping takes too long

**Cause:** Too many pages or products to scrape

**Solution:**
1. Edit scraper config
2. Reduce max_pages to 1 or 2
3. Save and try again

---

### Problem: Import fails

**Cause:** Data validation errors or configuration issues

**Solution:**
1. Check import history for error details
2. Review error log
3. Check data source configuration
4. Verify products have required fields (name, price)

---

### Problem: Duplicate products created

**Cause:** Match strategy not finding existing products

**Solution:**
1. Use "By URL or SKU" match strategy
2. Use "Add as Vendor Price" duplicate action
3. Ensure products have unique URLs or SKUs

---

### Problem: External URLs not working

**Cause:** Invalid URLs in scraped data

**Solution:**
1. Check scraped product URLs
2. Edit products before import
3. Verify website URLs are accessible

---

## Expected Results Summary

After completing all tests, you should have:

| Item | Expected Count |
|------|----------------|
| Scraper Configs | 6 |
| Category Mappings | 27 |
| Data Sources | 4 |
| Scraped Products (Drafts) | 10-50 |
| Final Products | 10-50 |
| Vendor Prices | 10-50 |
| Import History Records | 1+ |
| Scraper Jobs | 1+ |

---

## Next Steps

After successful testing:

1. **Test other categories:**
   - Adult Dog Dry Food
   - Puppy Dry Food
   - Dog Treats
   - Dog Toys

2. **Set up authentication:**
   - Add cookies to Data Sources
   - Test authenticated scraping

3. **Schedule scraping:**
   - Enable cron in scraper configs
   - Set scraping frequency

4. **Create categories for other sources:**
   - Vetution categories
   - Amazon categories
   - Custom sources

5. **Production deployment:**
   - Increase max_pages
   - Enable all categories
   - Set up monitoring

---

## Support & Documentation

- **Main Documentation:** `unified_scrapper_plan.md`
- **Category Reference:** `amin_petshop_categories_reference.md`
- **Import Guide:** `category_filtered_import_guide.md`
- **Basic Testing:** `TESTING_GUIDE.md`

---

## Conclusion

This complete workflow testing guide covers the entire process from category selection to final product import. Follow each step carefully and verify all expected results.

**Happy Testing!** 🚀

