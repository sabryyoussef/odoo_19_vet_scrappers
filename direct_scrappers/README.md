# Direct Scrappers - Complete Scraping Suite

This folder contains all scrapers, scripts, tests, documentation, and data for the veterinary product scraping project.

## 📁 Structure

```
direct_scrappers/
├── scrapers/              # All active scrapers
│   ├── unified_scraper/   # General e-commerce scraper
│   └── vetution_scraper/  # Vetution.com specialist
├── scripts/               # Helper scripts
├── tests/                 # Test files
├── docs/                  # Documentation
├── archive/               # Archived scrapers
├── data/                  # Scraped data
├── README.md              # This file
├── QUICK_REFERENCE.md     # Quick guide
└── requirements.txt       # Dependencies
```

## 🚀 Quick Start

### Unified Scraper (Any E-commerce Site)
```bash
cd scrapers/unified_scraper
python3 cli.py
```

### Vetution Scraper (Vetution.com)
```bash
cd scrapers/vetution_scraper
python3 run.py
```

## 📚 Documentation

- **Quick Start:** `QUICK_REFERENCE.md`
- **Full Guide:** `docs/README.md`
- **Workspace Guide:** `docs/guides/WORKSPACE_GUIDE.md`

## 🔧 Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## 📊 Features

### Unified Scraper
- Multi-platform support (Shopify, WooCommerce, Magento, etc.)
- Availability tracking
- Stock quantity extraction
- Multi-language (EN/AR)
- Batch processing

### Vetution Scraper
- Login support
- Variant extraction
- Multi-vendor pricing
- Price ranges
- Flat CSV export for Odoo

---

**Complete scraping infrastructure for veterinary products**

