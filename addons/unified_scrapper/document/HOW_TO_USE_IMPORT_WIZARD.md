# How to Use the Import Wizard 📋

## 🎯 **Where to Find It**

The import wizard is now accessible from the Odoo menu:

```
📂 Unified Scrapper
└── 📂 Operations
    └── 📄 Import Products ← Click here!
```

**Path:** `Unified Scrapper > Operations > Import Products`

---

## 🚀 **How to Use It (5 Steps)**

### **Step 1: Upload File**

1. Click **"Import Products"** from the menu
2. (Optional) Select a configured **Data Source**
3. Click **"Upload a file"** and select your CSV or JSON file
4. The wizard will automatically detect the file type
5. Click **"Next"**

**Supported Files:**
- ✅ CSV files (`.csv`) with header row
- ✅ JSON files (`.json`) with product array

---

### **Step 2: Configure Import**

Configure how the import should work:

#### **Source Configuration:**
- **Source System:** Select where the data comes from
  - Vetution
  - Amin Petshop
  - Amazon
  - Other/Custom

- **Match Strategy:** How to find existing products
  - **By External URL** (Recommended) - Most reliable
  - **By SKU/External ID** - Good for products with unique SKUs
  - **By Product Name** - Least reliable (may create duplicates)
  - **By URL or SKU** - Try URL first, then SKU
  - **By URL or Name** - Try URL first, then name

- **If Product Exists:**
  - **Skip** - Keep existing product, don't import
  - **Update** - Update existing product with new data
  - **Create New** - Create a new product (may cause duplicates)
  - **Add as Vendor Price** ✅ (Recommended) - Add as vendor price to existing product

#### **Import Options:**
- ☑️ **Create Vendor Prices** - Create vendor price records
- ☑️ **Update Cost Price** - Update product cost from vendor prices
- **Cost Price Strategy:**
  - **Use Lowest** ✅ (Recommended) - Most competitive
  - **Use Average** - Balanced approach
  - **Use First Source** - Stable pricing
  - **Keep Manual** - Don't change cost price

Click **"Preview"** when ready.

---

### **Step 3: Preview Data**

- Review the first 10 records from your file
- Check that the data looks correct
- See total number of records to import
- Click **"Import Now"** to start, or **"Back"** to change settings

---

### **Step 4: Importing**

- The wizard shows a progress indicator
- Please wait while products are imported
- This may take a few moments for large files

---

### **Step 5: View Results**

After import completes, you'll see:

#### **Statistics:**
- ✅ Products Created
- ✅ Products Updated
- ⏭️ Products Skipped
- ❌ Products Failed
- 🏷️ Vendor Prices Created

#### **Actions:**
- **View Products** - See all imported products
- **View History** - See detailed import history record
- **Close** - Close the wizard

#### **Logs:**
- **Import Log** - Detailed log of what happened
- **Error Log** - Any errors that occurred (if any)

---

## 📄 **Sample CSV Format**

```csv
name,default_code,list_price,external_product_id,external_url,availability
Royal Canin Dog Food 15kg,RC-DOG-15,850,VET-12345,https://vetution.com/product/rc-dog-15,in_stock
Pedigree Adult 10kg,PED-ADULT-10,420,VET-12346,https://vetution.com/product/ped-adult-10,in_stock
```

**Required Columns:**
- `name` - Product name
- `list_price` or `price` - Product price

**Optional Columns:**
- `default_code` - Product SKU
- `external_product_id` - External system ID
- `external_url` - Product URL on external site
- `availability` - Stock status (in_stock, out_of_stock, etc.)
- `vendor_name` - Specific vendor name
- Any other product fields

---

## 📄 **Sample JSON Format**

```json
[
  {
    "name": "Royal Canin Dog Food 15kg",
    "default_code": "RC-DOG-15",
    "list_price": 850,
    "external_product_id": "VET-12345",
    "external_url": "https://vetution.com/product/rc-dog-15",
    "availability": "in_stock"
  },
  {
    "name": "Pedigree Adult 10kg",
    "default_code": "PED-ADULT-10",
    "list_price": 420,
    "external_product_id": "VET-12346",
    "external_url": "https://vetution.com/product/ped-adult-10",
    "availability": "in_stock"
  }
]
```

**Alternative JSON Format** (with wrapper):
```json
{
  "products": [
    { "name": "Product 1", "price": 100 },
    { "name": "Product 2", "price": 200 }
  ]
}
```

---

## ⚠️ **Current Limitations**

**Note:** The wizard UI is ready, but the actual import logic is **not yet implemented**. 

When you try to import, you'll see an error:
```
NotImplementedError: Product import logic will be implemented in next step
```

**What's Missing:**
- ❌ Product creation logic
- ❌ Duplicate detection
- ❌ Vendor price creation
- ❌ Field mapping application

**Next Steps:**
We need to implement the `_import_product()` method in the wizard to actually create/update products and vendor prices.

---

## 🎯 **Recommended Settings**

For best results, use these settings:

```
✅ Source System: [Your actual source]
✅ Match Strategy: By URL or SKU
✅ If Product Exists: Add as Vendor Price
✅ Create Vendor Prices: Yes
✅ Update Cost Price: Yes
✅ Cost Price Strategy: Use Lowest
```

This will:
1. Avoid creating duplicate products
2. Create vendor prices for price comparison
3. Update cost price to the lowest vendor price
4. Allow easy ordering from multiple sources

---

## 🔍 **After Import**

### **View Imported Products:**
```
Unified Scrapper > Products > [Your Source] Products
```

### **View Vendor Prices:**
```
Unified Scrapper > Products > Vendor Prices
```

### **View Import History:**
```
Unified Scrapper > Operations > Import History
```

### **Check Individual Product:**
1. Open any product
2. Go to **"Vendor Prices"** tab
3. See all vendor prices with clickable links
4. Click **"Open Link"** to order from vendor

---

## 💡 **Tips**

1. **Start Small:** Test with a small file (10-20 products) first
2. **Check Preview:** Always review the preview before importing
3. **Use URLs:** External URLs are the most reliable for matching
4. **Vendor Prices:** Enable "Add as Vendor Price" to avoid duplicates
5. **Review Logs:** Check import log for details on what happened
6. **Fix Errors:** If products fail, check error log for reasons

---

## 🚧 **Coming Soon**

The following features will be implemented next:

- ✅ Wizard UI (DONE!)
- ⏳ Product import logic
- ⏳ Smart duplicate detection
- ⏳ Vendor price creation
- ⏳ Field mapping support
- ⏳ Automatic image download
- ⏳ Category mapping
- ⏳ Scheduled imports

---

**Last Updated:** December 5, 2025  
**Status:** Wizard UI Ready, Import Logic Pending

