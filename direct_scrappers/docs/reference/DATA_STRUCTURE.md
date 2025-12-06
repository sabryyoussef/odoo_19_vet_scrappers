# Data Structure Organization

## Overview

All scraped data is now organized by scraper in separate folders under `data/`.

## Current Structure

```
vetutions/
├── data/
│   ├── vetution/              # Vetution.com products
│   │   ├── products.json      # 1.3MB, 706 products
│   │   └── products.csv       # 704KB, 708 lines
│   │
│   ├── amin_petshop/          # Amin Petshop products
│   │   ├── products.json      # (to be created)
│   │   ├── products.csv       # (to be created)
│   │   └── categories.json    # Category exploration
│   │
│   └── external_scrapers/      # External scraper tests
│       └── (test outputs)
│
├── scrapers/
│   ├── vetution/              # Saves to data/vetution/
│   └── amin_petshop/          # Saves to data/amin_petshop/
│
└── scripts/                    # Default to data/vetution/
    └── (all scripts use _common.py)
```

## What Changed

### Before
- All data in `data/products.json` and `data/products.csv`
- Mixed data from different scrapers

### After
- Each scraper has its own folder: `data/{scraper_name}/`
- Consistent naming: `products.json` and `products.csv` in each folder
- Clear separation of data sources

## Updated Files

### Scrapers
- ✅ `scrapers/vetution/scraper_playwright.py` → saves to `data/vetution/`
- ✅ `scrapers/amin_petshop/scraper.py` → saves to `data/amin_petshop/`
- ✅ `scrapers/amin_petshop/category_explorer.py` → saves to `data/amin_petshop/categories.json`

### Scripts
- ✅ `scripts/_common.py` → Updated with scraper-specific paths
- ✅ `scripts/update_image_urls.py` → Uses vetution data folder
- ✅ `scripts/add_product_details.py` → Uses vetution data folder
- ✅ `scripts/daily_update.py` → Uses vetution data folder
- ✅ `scripts/daily_update_auto.py` → Uses vetution data folder
- ✅ `scripts/monitor_progress.py` → Uses vetution data folder
- ✅ `scripts/compare_updates.py` → Uses vetution data folder
- ✅ `scripts/scrape_amin_petshop.py` → Uses amin_petshop data folder

### External Scrapers
- ✅ `external_scrapers/product-web-scraper/example_amin_petshop.py` → saves to `data/amin_petshop/`
- ✅ `external_scrapers/product-web-scraper/custom_store_template.py` → saves to `data/external_scrapers/`
- ✅ `external_scrapers/product-web-scraper/test_working.py` → saves to `data/external_scrapers/`

## Usage

### Vetution Scraper
```python
from scrapers.vetution import VetutionScraper

scraper = VetutionScraper()
scraper.scrape_all_pages()
scraper.save_to_json()  # Saves to data/vetution/products.json
scraper.save_to_csv()   # Saves to data/vetution/products.csv
```

### Amin Petshop Scraper
```python
from scrapers.amin_petshop import AminPetshopScraper

scraper = AminPetshopScraper()
scraper.scrape_all_pages()
scraper.save_to_json()  # Saves to data/amin_petshop/products.json
scraper.save_to_csv()   # Saves to data/amin_petshop/products.csv
```

### From Scripts
```python
from scripts._common import get_products_json, get_products_csv

# Vetution (default)
vetution_json = get_products_json('vetution')
vetution_csv = get_products_csv('vetution')

# Amin Petshop
amin_json = get_products_json('amin_petshop')
amin_csv = get_products_csv('amin_petshop')
```

## Benefits

1. **Clear Organization** - Easy to find data for each scraper
2. **No Conflicts** - Each scraper has its own space
3. **Easy Backup** - Can backup individual scraper data
4. **Scalable** - Easy to add new scrapers
5. **Consistent** - Same file names in each folder

## Adding New Scrapers

When adding a new scraper:

1. Create folder: `data/new_scraper/`
2. Update scraper's `save_to_json()` and `save_to_csv()` methods to use `data/new_scraper/`
3. Add functions to `scripts/_common.py` if needed
4. Update documentation

