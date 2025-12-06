# Universal Web Scraper for Odoo 19

A professional web scraping module that integrates the powerful `unified_scraper` Python library with Odoo 19, enabling automated product data extraction from various e-commerce platforms.

## 🌟 Features

### **Core Capabilities**
- 🎯 **Multi-Platform Support**: Shopify, WooCommerce, Magento, Odoo, Amazon, eBay, and generic sites
- ⚡ **Batch Processing**: Efficient multi-threaded scraping (configurable workers)
- ✅ **Availability Detection**: Automatic stock status tracking
- 🔐 **Authentication**: Manual and automated login support
- 📅 **Scheduled Scraping**: Cron-based automatic scraping
- 🔄 **Draft Review System**: Review scraped products before importing
- 🔗 **Unified Scrapper Integration**: Seamless integration with vendor price tracking

### **Data Extraction**
- Product names, prices, currencies
- SKUs, brands, categories
- Product images and descriptions
- Stock availability and quantities
- Complete raw data preservation

### **Smart Features**
- Automatic platform detection
- Duplicate product detection
- Multiple matching strategies (URL, SKU, Name)
- Flexible duplicate handling (skip, update, add vendor price)
- Cost price calculation strategies (lowest, average, first)

## 📋 Requirements

### **Python Dependencies**
```bash
pip install playwright beautifulsoup4 lxml
playwright install chromium
```

### **Odoo Dependencies**
- `base`
- `product`
- `mail`
- `unified_scrapper` (must be installed first)

## 🚀 Installation

1. **Install Python dependencies** (in your Odoo environment):
   ```bash
   pip install playwright beautifulsoup4 lxml
   playwright install chromium
   ```

2. **Install Unified Scrapper module** (if not already installed):
   - Install the `unified_scrapper` module first
   - This module depends on it for final product import

3. **Copy the module** to your Odoo addons directory:
   ```bash
   cp -r universal_scraper_odoo /path/to/odoo/addons/
   ```

4. **Restart Odoo** and update the app list

5. **Install the module** from Odoo Apps

## 📖 Usage

### **1. Quick Scrape (One-Time)**

Perfect for testing or one-time scraping:

1. Go to **Web Scraper > Operations > Quick Scrape**
2. Enter the target URL (e.g., `https://example.com/collections/all`)
3. Select platform type (or use "Generic" for auto-detect)
4. Set max pages and options
5. Select the data source for Unified Scrapper
6. Click **Run Scraper**

### **2. Scraper Configuration (Reusable)**

For recurring scraping or scheduled jobs:

1. Go to **Web Scraper > Configuration > Scraper Configurations**
2. Click **Create**
3. Configure:
   - **Name**: e.g., "Vetution Product Scraper"
   - **URL**: Target website URL
   - **Platform**: Select or use auto-detect
   - **Options**: Max pages, fetch details, batch size
   - **Data Source**: Link to Unified Scrapper data source
4. **Optional**: Enable scheduling (hourly, daily, weekly, monthly)
5. **Save** and click **Run Scraper Now**

### **3. Review Scraped Products**

1. Go to **Web Scraper > Operations > Scraped Products**
2. Review draft products:
   - Check for duplicates (marked with ⚠️)
   - Verify pricing and availability
   - View raw data if needed
3. **Approve** products you want to import
4. **Reject** products you don't want

### **4. Import to Unified Scrapper**

1. Select approved products
2. Click **Action > Import to Unified Scrapper**
3. Configure import settings:
   - **Matching Strategy**: How to find existing products
   - **Duplicate Handling**: What to do with duplicates
   - **Cost Price Strategy**: How to calculate main price
4. Click **Import Now**
5. Products will be created in Unified Scrapper with vendor prices

### **5. Scheduled Scraping**

1. Create or edit a scraper configuration
2. Go to **Scheduling** tab
3. Enable **Enable Scheduled Scraping**
4. Select frequency (hourly, daily, weekly, monthly)
5. Save

The scraper will run automatically and create draft products for review.

## 🔧 Configuration

### **Scraper Settings**

| Setting | Description | Recommendation |
|---------|-------------|----------------|
| **Max Pages** | Number of pages to scrape | 1-3 for testing, 5-10 for production |
| **Fetch Details** | Visit each product page | Enable for accurate data (slower) |
| **Headless Mode** | Run browser in background | Enable for production, disable for debugging |
| **Batch Size** | Parallel processing workers | 5-8 for most sites, 2-3 for slow sites |

### **Authentication**

For sites requiring login:

1. Enable **Requires Login**
2. Choose:
   - **Manual Login**: Browser opens for you to login
   - **Automated Login**: Provide email/password

### **Platform Support**

| Platform | Detection | Support Level |
|----------|-----------|---------------|
| Shopify | Excellent | ✅ Full |
| WooCommerce | Good | ✅ Full |
| Magento | Good | ✅ Full |
| Odoo E-commerce | Good | ✅ Full |
| Amazon | Limited | ⚠️ Basic |
| eBay | Limited | ⚠️ Basic |
| Generic | Varies | ⚠️ Depends |

## 📊 Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  1. Configure Scraper                                       │
│     • Set URL, platform, options                            │
│     • Link to Unified Data Source                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Run Scraper (Manual or Scheduled)                       │
│     • Your unified_scraper extracts data                    │
│     • Products saved as drafts                              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Review Draft Products                                   │
│     • Check for duplicates                                  │
│     • Approve/Reject products                               │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Import to Unified Scrapper                              │
│     • Creates final products                                │
│     • Creates vendor prices                                 │
│     • Calculates cost prices                                │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Troubleshooting

### **No Products Found**
- Try with visible browser (disable headless mode)
- Check if site requires login
- Verify URL is correct
- Try with platform type instead of "Generic"

### **Slow Performance**
- Disable "Fetch Details" for faster scraping
- Reduce batch size for unstable sites
- Scrape fewer pages initially

### **Import Errors**
- Ensure Unified Scrapper module is installed
- Check that data source exists
- Verify products are approved before importing

### **Python Dependencies Missing**
```bash
# Install in Odoo environment
pip install playwright beautifulsoup4 lxml
playwright install chromium
```

## 📚 Documentation

- **Unified Scraper**: See `/lib/unified_scraper/README_COMPLETE.md`
- **Unified Scrapper Integration**: See `unified_scrapper` module docs
- **Odoo 19**: Official Odoo documentation

## ⚖️ Legal & Ethics

⚠️ **Important:**
- For educational/personal use
- Respect website terms of service
- Follow robots.txt
- Don't scrape personal data
- Comply with GDPR/CCPA
- Get permission for commercial use

## 🤝 Support

For issues or questions:
1. Check this README
2. Review the unified_scraper documentation
3. Check Odoo logs for errors
4. Try with visible browser for debugging

## 📄 License

LGPL-3

---

**Made with ❤️ for ethical web scraping and Odoo integration**

