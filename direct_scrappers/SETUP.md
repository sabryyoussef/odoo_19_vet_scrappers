# Setup Instructions

## 📦 Installation

```bash
# Navigate to direct_scrappers folder
cd direct_scrappers

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## 🚀 Usage

### Unified Scraper
```bash
cd scrapers/unified_scraper
python3 cli.py
```

### Vetution Scraper
```bash
cd scrapers/vetution_scraper
python3 run.py
```

### Helper Scripts
```bash
# Test Vetution variants
python3 scripts/test_vetution_variants.py

# Export variants to CSV
python3 scripts/export_variants_flat.py
```

## 📁 Data Locations

- **Unified Scraper:** `scrapers/unified_scraper/data/results_YYYYMMDD/`
- **Vetution Scraper:** `scrapers/vetution_scraper/data/results_YYYYMMDD/`
- **Legacy Data:** `data/vetution/`, `data/amin_petshop/`

## 🔧 Paths

All scripts are configured to work from the `direct_scrappers/` folder root.
No path adjustments needed when running from this folder.

