# Workspace Structure

This document describes the organized workspace structure for multiple scrapers.

## Directory Structure

```
vetutions/
│
├── vetution_scraper_module/     # Odoo 19 Module (DO NOT MODIFY)
│   ├── models/                  # Odoo models
│   ├── views/                   # Odoo views
│   ├── wizard/                  # Odoo wizards
│   ├── security/                # Access rights
│   └── __manifest__.py
│
├── scrapers/                    # Scraper Implementations
│   ├── vetution/               # Vetution.com scraper
│   │   ├── scraper_playwright.py
│   │   ├── scraper.py          # (legacy, can be removed)
│   │   └── __init__.py
│   │
│   └── amazon_pets/             # Amazon Pets scraper (future)
│       └── __init__.py
│
├── scripts/                     # Utility Scripts
│   ├── _common.py              # Common utilities (paths, imports)
│   ├── scrape_with_login.py    # Main scraper script
│   ├── update_image_urls.py    # Update product images
│   ├── add_product_details.py  # Add detailed product info
│   ├── daily_update.py         # Interactive daily updates
│   ├── daily_update_auto.py    # Automated daily updates (cron)
│   ├── compare_updates.py      # Compare product files
│   ├── monitor_progress.py     # Monitor scraping progress
│   └── schedule_daily_update.sh # Cron setup script
│
├── data/                        # Scraped Data
│   ├── products.json           # All products (JSON)
│   └── products.csv            # All products (CSV)
│
├── venv/                        # Python virtual environment
├── requirements.txt            # Python dependencies
├── README.md                   # Main documentation
└── STRUCTURE.md                # This file
```

## Key Points

1. **Odoo Module**: The `vetution_scraper_module/` directory is kept separate and should not be modified when organizing scrapers.

2. **Scrapers**: Each website scraper has its own directory under `scrapers/`:
   - `scrapers/vetution/` - Vetution.com scraper
   - `scrapers/amazon_pets/` - Amazon Pets scraper (ready for implementation)

3. **Scripts**: All utility scripts are in `scripts/` and use `_common.py` for shared functionality.

4. **Data**: All scraped data is stored in `data/` directory for easy access and backup.

## Adding a New Scraper

To add a new scraper (e.g., Amazon Pets):

1. Create scraper directory:
   ```bash
   mkdir -p scrapers/amazon_pets
   ```

2. Create your scraper class in `scrapers/amazon_pets/scraper.py`:
   ```python
   from playwright.sync_api import sync_playwright
   # ... your scraper implementation
   ```

3. Export in `scrapers/amazon_pets/__init__.py`:
   ```python
   from .scraper import AmazonPetsScraper
   __all__ = ['AmazonPetsScraper']
   ```

4. Create scripts in `scripts/` that use your scraper:
   ```python
   from scrapers.amazon_pets import AmazonPetsScraper
   # ... your script
   ```

## Import Paths

All scripts use relative imports from the project root:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scrapers.vetution import VetutionScraper
from _common import get_products_json, get_products_csv
```

## Data Files

- Products are saved to `data/products.json` and `data/products.csv`
- Scripts use `_common.py` to get correct file paths
- Backups can be stored in `data/backups/` (created automatically)

