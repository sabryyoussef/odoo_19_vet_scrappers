# Universal Scraper Odoo - Installation Guide

## ✅ Module Created Successfully!

Your `universal_scraper_odoo` module has been created and is ready to install.

## 📦 What's Included

### **Your Scraper (Unchanged)**
```
lib/unified_scraper/
├── unified_scraper.py      ← Your tested scraper (exact copy)
├── __init__.py
├── requirements.txt
└── ... (all your files)
```

### **Odoo Integration (New)**
```
models/
├── scraper_config.py       ← Scraper configurations
├── scraped_product_draft.py ← Draft products for review
└── scraper_job.py          ← Scraping history

wizards/
├── scraper_wizard.py       ← Quick scrape wizard
└── import_to_unified_wizard.py ← Import to Unified Scrapper

views/
├── scraper_config_views.xml
├── scraped_product_draft_views.xml
├── scraper_job_views.xml
├── scraper_wizard_views.xml
├── import_to_unified_wizard_views.xml
└── menu_views.xml

data/
└── cron_data.xml           ← Scheduled scraping

security/
└── ir.model.access.csv     ← Access rights
```

## 🚀 Installation Steps

### **Step 1: Install Python Dependencies**

```bash
# Activate your Odoo environment (if using venv/conda)
# Then install dependencies:

pip install playwright beautifulsoup4 lxml

# Install Chromium browser for Playwright
playwright install chromium
```

### **Step 2: Verify Unified Scrapper is Installed**

The `universal_scraper_odoo` module depends on `unified_scrapper`. Make sure it's installed first:

1. Go to **Apps** in Odoo
2. Search for "Unified Scrapper"
3. If not installed, install it first

### **Step 3: Restart Odoo**

```bash
# If using Docker:
docker-compose restart

# If running Odoo directly:
# Stop and start your Odoo service
```

### **Step 4: Update Apps List**

1. Go to **Apps** in Odoo
2. Click **Update Apps List** (top-right menu)
3. Confirm the update

### **Step 5: Install Universal Scraper**

1. Go to **Apps**
2. Remove the "Apps" filter to show all modules
3. Search for "Universal Web Scraper"
4. Click **Install**

### **Step 6: Verify Installation**

After installation, you should see a new menu:

```
📡 Web Scraper
├── Configuration
│   └── Scraper Configurations
├── Operations
│   ├── Quick Scrape
│   ├── Scraped Products
│   └── Scraping Jobs
└── Unified Scrapper
    ├── Data Sources
    ├── Import Products
    └── Vendor Prices
```

## 🎯 Quick Test

### **Test 1: Quick Scrape**

1. Go to **Web Scraper > Operations > Quick Scrape**
2. Enter a test URL (e.g., `https://aminpetshop.com/collections/all`)
3. Set **Max Pages** to `1`
4. Disable **Fetch Details** (for speed)
5. Select a **Data Source** from Unified Scrapper
6. Click **Run Scraper**

### **Test 2: Review Drafts**

1. Go to **Web Scraper > Operations > Scraped Products**
2. You should see the scraped products in draft state
3. Click on a product to view details
4. Click **Approve** to approve it

### **Test 3: Import to Unified**

1. Select approved products
2. Click **Action > Import to Unified Scrapper**
3. Configure import settings
4. Click **Import Now**
5. Check **Unified Scrapper > Vendor Prices** to see the results

## 🔧 Troubleshooting

### **Error: "Module not found: playwright"**

```bash
# Make sure you're in the correct Python environment
pip install playwright beautifulsoup4 lxml
playwright install chromium
```

### **Error: "unified_scrapper module not found"**

Install the `unified_scrapper` module first. This module depends on it.

### **Error: "No module named 'unified_scraper'"**

The scraper files should be in:
```
/path/to/odoo/addons/universal_scraper_odoo/lib/unified_scraper/
```

Verify they were copied correctly.

### **Scraper Returns No Products**

1. Try with **Headless Mode** disabled to see the browser
2. Check if the site requires login
3. Verify the URL is correct
4. Try with a different platform type

### **Import Fails**

1. Ensure products are **approved** before importing
2. Check that the **Data Source** exists in Unified Scrapper
3. Verify **Unified Scrapper** module is installed and working

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  YOUR SCRAPER (lib/unified_scraper/)                        │
│  ─────────────────────────────────────                      │
│  • unified_scraper.py (unchanged)                           │
│  • All your tested code                                     │
│  • Works exactly as before                                  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ (Odoo wrapper calls your scraper)
                 │
┌────────────────▼────────────────────────────────────────────┐
│  ODOO MODELS (models/)                                      │
│  ────────────────────                                       │
│  • scraper.config - Configurations                          │
│  • scraped.product.draft - Draft products                   │
│  • scraper.job - Job history                                │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ (Saves to drafts, then imports)
                 │
┌────────────────▼────────────────────────────────────────────┐
│  UNIFIED SCRAPPER (existing module)                         │
│  ──────────────────────────────                             │
│  • Creates final products                                   │
│  • Creates vendor prices                                    │
│  • Manages multi-source products                            │
└─────────────────────────────────────────────────────────────┘
```

## ✅ Next Steps

1. **Create Data Sources** in Unified Scrapper for each website you want to scrape
2. **Create Scraper Configurations** for each data source
3. **Run scrapers** manually or enable scheduling
4. **Review drafts** and approve products
5. **Import to Unified Scrapper** to create final products

## 📚 Documentation

- **README.md** - Full module documentation
- **Unified Scraper** - See `lib/unified_scraper/README_COMPLETE.md`
- **Unified Scrapper** - See `unified_scrapper` module docs

---

**🎉 Your module is ready! Start scraping!**

