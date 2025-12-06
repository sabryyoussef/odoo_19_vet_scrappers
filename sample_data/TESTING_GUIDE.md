# Import Wizard Testing Guide 🧪

## 🎯 **What's Ready to Test**

✅ **Complete Import Wizard** with:
- Multi-step UI (Upload → Configure → Preview → Import → Results)
- CSV/JSON parsing with encoding detection
- Smart duplicate detection (by URL, SKU, or name)
- Product creation with all fields
- Vendor price creation
- Cost price calculation (lowest/average/first)
- Detailed import logging

---

## 📁 **Sample Files Location**

Sample files are located in: `/home/sabry3/odoo_19_vetutions/sample_data/`

1. **`products_sample.csv`** - 5 Vetution products (CSV format)
2. **`products_sample.json`** - 5 Vetution products (JSON format)
3. **`amin_petshop_sample.csv`** - 3 Amin Petshop products (same products, different prices)

---

## 🧪 **Test Scenario 1: Basic Import (CSV)**

**Goal:** Import products from Vetution

### Steps:

1. **Open Odoo:** http://localhost:8070
2. **Navigate:** `Unified Scrapper > Operations > Import Products`
3. **Upload File:**
   - Click "Upload a file"
   - Select `/home/sabry3/odoo_19_vetutions/sample_data/products_sample.csv`
   - File type should auto-detect as "CSV File"
   - Click **"Next"**

4. **Configure Import:**
   - Source System: **Vetution**
   - Match Strategy: **By URL or SKU**
   - If Product Exists: **Add as Vendor Price**
   - ☑️ Create Vendor Prices: **Yes**
   - ☑️ Update Cost Price: **Yes**
   - Cost Price Strategy: **Use Lowest**
   - Click **"Preview"**

5. **Preview Data:**
   - Review the 5 products shown
   - Click **"Import Now"**

6. **View Results:**
   - Should show: **5 Products Created, 5 Vendor Prices Created**
   - Click **"View Products"** to see imported products

### Expected Results:
- ✅ 5 new products created
- ✅ 5 vendor prices created (one per product)
- ✅ Products have external_source = "vetution"
- ✅ Products have clickable external URLs
- ✅ Cost prices set to list prices

---

## 🧪 **Test Scenario 2: Multi-Source Import (Vendor Prices)**

**Goal:** Import same products from Amin Petshop to create vendor prices

### Steps:

1. **Navigate:** `Unified Scrapper > Operations > Import Products`
2. **Upload File:**
   - Select `/home/sabry3/odoo_19_vetutions/sample_data/amin_petshop_sample.csv`
   - Click **"Next"**

3. **Configure Import:**
   - Source System: **Amin Petshop**
   - Match Strategy: **By SKU** (products have same SKUs)
   - If Product Exists: **Add as Vendor Price** ← Important!
   - ☑️ Create Vendor Prices: **Yes**
   - ☑️ Update Cost Price: **Yes**
   - Cost Price Strategy: **Use Lowest**
   - Click **"Preview"**

4. **Preview & Import:**
   - Should show 3 products
   - Click **"Import Now"**

5. **View Results:**
   - Should show: **0 Created, 3 Updated, 3 Vendor Prices Created**
   - This means it found existing products and added vendor prices!

### Expected Results:
- ✅ No new products created (matched existing)
- ✅ 3 vendor prices added to existing products
- ✅ Products now have 2 vendor prices each (Vetution + Amin Petshop)
- ✅ Cost prices updated to lowest (Amin Petshop is cheaper)

---

## 🧪 **Test Scenario 3: View Vendor Prices**

**Goal:** See price comparison for multi-source products

### Steps:

1. **Navigate:** `Unified Scrapper > Products > All External Products`
2. **Open Product:** "Royal Canin Dog Food 15kg"
3. **Go to Tab:** "Vendor Prices"

### Expected Results:
You should see:
```
Price Statistics:
- Lowest: 820 EGP (Amin Petshop) ✅
- Highest: 850 EGP (Vetution)
- Average: 835 EGP

Vendor Price List:
┌──────────────┬───────┬──────────┬──────────────────┐
│ Source       │ Price │ Stock    │ Link             │
├──────────────┼───────┼──────────┼──────────────────┤
│ Amin Petshop │ 820 ✅│ In Stock │ 🔗 Open Link     │
│ Vetution     │ 850   │ In Stock │ 🔗 Open Link     │
└──────────────┴───────┴──────────┴──────────────────┘
```

- ✅ Lowest price highlighted in green
- ✅ Both vendor links are clickable
- ✅ Product cost price = 820 EGP (lowest)

---

## 🧪 **Test Scenario 4: JSON Import**

**Goal:** Test JSON file import

### Steps:

1. **Navigate:** `Unified Scrapper > Operations > Import Products`
2. **Upload File:**
   - Select `/home/sabry3/odoo_19_vetutions/sample_data/products_sample.json`
   - File type should detect as "JSON File"
   - Click **"Next"**

3. **Configure Import:**
   - Source System: **Vetution**
   - Match Strategy: **By URL or SKU**
   - If Product Exists: **Skip** (products already exist from CSV test)
   - Click **"Preview"** → **"Import Now"**

### Expected Results:
- ✅ 5 Products Skipped (already exist)
- ✅ 0 Created, 0 Updated
- ✅ Import log shows "Skipped: Already exists"

---

## 🧪 **Test Scenario 5: Update Existing Products**

**Goal:** Update product data

### Steps:

1. **Edit CSV file:** Change prices in `products_sample.csv`
   ```csv
   Royal Canin Dog Food 15kg,RC-DOG-15,900,...  (was 850)
   ```

2. **Import with:**
   - Source System: **Vetution**
   - Match Strategy: **By URL or SKU**
   - If Product Exists: **Update** ← Changed!
   - Click **"Import Now"**

### Expected Results:
- ✅ 5 Products Updated
- ✅ Prices updated to new values
- ✅ `external_update_count` incremented
- ✅ `external_last_sync` updated

---

## 🔍 **Verification Checklist**

After importing, verify:

### **Products:**
- [ ] Products appear in `Unified Scrapper > Products > Vetution Products`
- [ ] Product names, SKUs, and prices are correct
- [ ] External source field = "vetution" or "amin_petshop"
- [ ] External URLs are clickable

### **Vendor Prices:**
- [ ] Vendor prices appear in `Unified Scrapper > Products > Vendor Prices`
- [ ] Each product has correct number of vendor prices
- [ ] Prices are sorted (lowest first)
- [ ] Lowest price is highlighted in green
- [ ] "Open Link" buttons work

### **Product Form:**
- [ ] "External Source" tab shows source info
- [ ] "Vendor Prices" tab shows all vendor prices
- [ ] Price statistics are correct (lowest, highest, average)
- [ ] Smart button shows vendor price count

### **Import History:**
- [ ] Import history record created in `Operations > Import History`
- [ ] Statistics are correct (created, updated, skipped, failed)
- [ ] Import log shows detailed information
- [ ] No errors in error log

---

## 🐛 **Common Issues & Solutions**

### **Issue 1: "Product name is required" error**
**Solution:** Ensure CSV/JSON has a `name` field for each product

### **Issue 2: All products skipped**
**Solution:** Change "If Product Exists" to "Update" or "Add as Vendor Price"

### **Issue 3: Duplicate products created**
**Solution:** Use better match strategy (URL or SKU instead of name)

### **Issue 4: Vendor prices not created**
**Solution:** Ensure "Create Vendor Prices" is checked

### **Issue 5: Cost price not updated**
**Solution:** Ensure "Update Cost Price" is checked

---

## 📊 **Expected Performance**

- **Small files (< 100 products):** < 10 seconds
- **Medium files (100-1000 products):** < 2 minutes
- **Large files (1000+ products):** 2-10 minutes

---

## 🎯 **Advanced Testing**

### **Test Different Match Strategies:**
1. **By URL:** Most reliable, prevents duplicates
2. **By SKU:** Good if SKUs are unique
3. **By Name:** May create duplicates if names vary slightly
4. **By URL or SKU:** Best balance

### **Test Different Duplicate Actions:**
1. **Skip:** Fast, but doesn't update
2. **Update:** Updates all product data
3. **Add as Vendor Price:** Best for multi-source products
4. **Create New:** May cause duplicates

### **Test Cost Price Strategies:**
1. **Lowest:** Most competitive pricing
2. **Average:** Balanced approach
3. **First:** Stable, doesn't change
4. **Manual:** No automatic updates

---

## ✅ **Success Criteria**

The import wizard is working correctly if:

1. ✅ Can upload and parse CSV files
2. ✅ Can upload and parse JSON files
3. ✅ Creates new products with all fields
4. ✅ Detects duplicate products correctly
5. ✅ Creates vendor price records
6. ✅ Updates cost prices based on strategy
7. ✅ Shows detailed import results
8. ✅ Logs all actions and errors
9. ✅ Vendor price links are clickable
10. ✅ Multi-source products show price comparison

---

## 📝 **Test Report Template**

```
Test Date: ___________
Tester: ___________

Scenario 1 (Basic Import): ☐ Pass ☐ Fail
Scenario 2 (Multi-Source): ☐ Pass ☐ Fail
Scenario 3 (Vendor Prices): ☐ Pass ☐ Fail
Scenario 4 (JSON Import): ☐ Pass ☐ Fail
Scenario 5 (Update): ☐ Pass ☐ Fail

Issues Found:
1. ___________
2. ___________

Notes:
___________
```

---

**Happy Testing!** 🚀

If you encounter any issues, check the import log and error log in the wizard results screen.

