# Workspace Guide - Quick Reference

## 📂 Directory Structure (Final)

```
vetutions/                                  # Project root
│
├── 🎯 scrapers/                           # ALL ACTIVE SCRAPERS
│   │
│   ├── unified_scraper/                   # General purpose
│   │   ├── unified_scraper.py            # Main scraper (692 lines)
│   │   ├── cli.py                        # Interactive CLI (189 lines)
│   │   ├── run.py                        # Quick launcher
│   │   ├── README.md                     # Documentation (291 lines)
│   │   ├── test_scraper.py               # Basic test
│   │   ├── test_availability.py          # Availability test
│   │   ├── test_multithreading.py        # Performance test
│   │   ├── requirements.txt              # Dependencies
│   │   └── data/
│   │       ├── results_20241205/         # 📅 Timestamped results
│   │       ├── results_20241206/
│   │       └── README.md
│   │
│   ├── vetution_scraper/                  # Vetution specialist
│   │   ├── scraper_playwright.py         # Main scraper (1230 lines)
│   │   ├── run.py                        # Quick launcher
│   │   ├── USAGE_GUIDE.md                # Complete guide (451 lines)
│   │   ├── VARIANT_EXTRACTION.md         # Technical docs (394 lines)
│   │   └── data/
│   │       ├── results_20241205/         # 📅 Timestamped results
│   │       ├── results_20241206/
│   │       ├── products.json             # Latest data
│   │       └── products.csv
│   │
│   └── README.md                          # Scrapers overview
│
├── 🛠️ scripts/                            # Utilities
│   ├── test_vetution_variants.py         # Test variants
│   ├── export_variants_flat.py           # Flatten for Odoo
│   └── _common.py                        # Shared utilities
│
├── 📦 data/                               # Legacy (reference)
│   ├── vetution/                         # Old Vetution data
│   ├── amin_petshop/                     # Old Amin data
│   └── README.md
│
├── 🗄️ archive/                            # Reference only
│   ├── scrapers/
│   │   ├── amin_petshop/                 # Replaced
│   │   └── amazon_pets/                  # Never completed
│   ├── external_scrapers/                # GitHub clones
│   └── README.md
│
├── 📖 README.md                           # Main project README
├── docs/
│   ├── guides/WORKSPACE_GUIDE.md         # This file
│   ├── reference/PROJECT_STRUCTURE.md     # Detailed structure
│   └── summaries/FINAL_SUMMARY.md        # Complete summary
├── QUICK_REFERENCE.md                     # Quick cheat sheet
├── 📦 requirements.txt                    # Dependencies
└── 🚫 .gitignore                          # Ignore patterns
```

---

## ⚡ Quick Commands

### Unified Scraper (Any Site)
```bash
cd scrapers/unified_scraper

# Interactive mode
python3 cli.py

# Quick test
python3 test_scraper.py

# Availability test
python3 test_availability.py
```

### Vetution Scraper (Vetution.com)
```bash
cd scrapers/vetution_scraper

# Full scrape with login
python3 scraper_playwright.py --manual-login

# Quick test (3 products)
python3 ../../scripts/test_vetution_variants.py

# Export for Odoo
python3 ../../scripts/export_variants_flat.py
```

---

## 📅 Timestamped Results

### How It Works
Each time you scrape, results go into a timestamped folder:

```
data/
├── results_20241205_143022/  # Dec 5, 2024 at 14:30:22
├── results_20241205_180945/  # Dec 5, 2024 at 18:09:45
└── results_20241206_091530/  # Dec 6, 2024 at 09:15:30
```

### Benefits
- ✅ Never overwrite previous results
- ✅ Easy to compare different runs
- ✅ Track changes over time
- ✅ Safe experimentation

### Cleanup Old Results
```bash
# Keep last 30 days, delete older
find scrapers/*/data/results_* -type d -mtime +30 -exec rm -rf {} +

# Or manually delete specific dates
rm -rf scrapers/unified_scraper/data/results_20241201/
```

---

## 🎯 Workflow Examples

### Daily Vetution Scraping
```bash
# 1. Morning quick check (5-10 min)
cd scrapers/vetution_scraper
python3 scraper_playwright.py --manual-login
# Get: Basic prices, no details

# 2. Results saved to: data/results_20241205_090000/
#    - products.json
#    - products.csv

# 3. Compare with yesterday
diff data/results_20241204_090000/products.json \
     data/results_20241205_090000/products.json
```

### Weekly Full Scrape with Variants
```bash
# 1. Full scrape (2-3 hours)
cd scrapers/vetution_scraper
python3 scraper_playwright.py --manual-login
# Enable fetch_details=True in script

# 2. Export for Odoo
cd ../..
python3 scripts/export_variants_flat.py

# 3. Results:
#    - scrapers/vetution_scraper/data/results_20241205_140000/
#      • products.json (full data)
#      • products.csv (standard format)
#      • variants_flat.csv (one row per variant)
```

### Test New E-commerce Site
```bash
# 1. Run unified scraper
cd scrapers/unified_scraper
python3 cli.py

# 2. Enter URL: https://newsite.com/products
# 3. Configure options
# 4. Scrape!

# 5. Results in: data/results_20241205_HHMMSS/
```

---

## 📊 Data Flow

```
Source Website
    ↓
[Scraper] (unified or vetution)
    ↓
scrapers/[scraper_name]/data/results_YYYYMMDD_HHMMSS/
    ├── products.json          # Full structured data
    ├── products.csv           # Spreadsheet format
    └── variants_flat.csv      # Odoo-ready (Vetution only)
    ↓
[Export Scripts] (optional)
    ↓
Odoo / Excel / Database
```

---

## 🔍 Finding Your Data

### Latest Unified Scraper Results
```bash
ls -lt scrapers/unified_scraper/data/results_*/
# Shows newest first
```

### Latest Vetution Results
```bash
ls -lt scrapers/vetution_scraper/data/results_*/
# Shows newest first
```

### Specific Date
```bash
# Find results from December 5
ls scrapers/*/data/results_20241205*/
```

---

## 🧹 Maintenance

### Weekly
```bash
# Remove old test data (>30 days)
find scrapers/*/data/results_* -mtime +30 -type d -exec rm -rf {} +

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +

# Remove log files
rm -f *.log
```

### Monthly
```bash
# Backup important data
tar -czf backup_$(date +%Y%m).tar.gz \
    scrapers/unified_scraper/data/ \
    scrapers/vetution_scraper/data/

# Or use git
git add -A
git commit -m "data: Monthly backup"
```

---

## 💡 Pro Tips

### 1. Always Test First
```bash
# Test with 1 product/page before full scrape
python3 test_scraper.py
```

### 2. Use Timestamped Folders
Results are automatically timestamped - never worry about overwrites!

### 3. Keep Data Organized
```bash
# Each scraper has its own data/ folder
# Legacy data in /data/ (for reference)
# Archive in /archive/ (for backup)
```

### 4. Quick Navigation
```bash
# Add aliases to your .bashrc
alias scrape-unified='cd ~/vetutions/scrapers/unified_scraper && python3 cli.py'
alias scrape-vetution='cd ~/vetutions/scrapers/vetution_scraper && python3 run.py'
```

### 5. Monitor Disk Space
```bash
# Check data folder sizes
du -sh scrapers/*/data/
```

---

## 📋 Cheat Sheet

| Task | Command |
|------|---------|
| Scrape any site | `cd scrapers/unified_scraper && python3 cli.py` |
| Scrape Vetution | `cd scrapers/vetution_scraper && python3 run.py` |
| Test unified | `cd scrapers/unified_scraper && python3 test_scraper.py` |
| Test Vetution | `python3 scripts/test_vetution_variants.py` |
| Export variants | `python3 scripts/export_variants_flat.py` |
| View latest data | `ls -lt scrapers/*/data/results_*/` |
| Cleanup old data | `find scrapers/*/data/results_* -mtime +30 -exec rm -rf {} +` |

---

## 🎓 Learning Path

### Day 1: Unified Scraper
1. Read: `scrapers/unified_scraper/QUICK_START.md`
2. Test: `python3 test_scraper.py`
3. Try: `python3 cli.py` with a real site

### Day 2: Vetution Scraper  
1. Read: `scrapers/vetution_scraper/USAGE_GUIDE.md`
2. Test: `python3 scripts/test_vetution_variants.py`
3. Login and verify variants are extracted

### Day 3: Production
1. Run full scrapes
2. Export data
3. Import to Odoo
4. Set up automation (optional)

---

## ✅ Quality Checklist

Before using in production:
- [ ] Test scrapers with sample data
- [ ] Verify login works (Vetution)
- [ ] Check variant extraction (Vetution)
- [ ] Validate availability tracking
- [ ] Test data exports (JSON/CSV)
- [ ] Review data quality
- [ ] Backup existing data
- [ ] Document any customizations

---

## 🎉 Summary

✨ **Clean Structure**: Both scrapers in `scrapers/`
📅 **Timestamped Results**: Never overwrite data
🗑️ **Cleaned Up**: Removed logs, cache, legacy files
📚 **Well Documented**: 13+ documentation files
💾 **Git Tracked**: 4 commits, clean history

**Your workspace is now production-ready!** 🚀

---

*Quick reference guide for navigating the Vetutions project*
*Last updated: December 5, 2024*




