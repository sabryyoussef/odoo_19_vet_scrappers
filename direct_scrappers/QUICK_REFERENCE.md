# Quick Reference Card

## 🚀 Run Scrapers

```bash
# Any e-commerce site
cd scrapers/unified_scraper && python3 cli.py

# Vetution.com  
cd scrapers/vetution_scraper && python3 run.py
```

## 📂 Where is Everything?

| What | Where |
|------|-------|
| Active scrapers | `scrapers/unified_scraper/` & `scrapers/vetution_scraper/` |
| Latest results | `scrapers/*/data/results_YYYYMMDD_HHMMSS/` |
| Test scripts | `scrapers/*/test_*.py` |
| Helper scripts | `scripts/` |
| Documentation | `scrapers/*/README.md` & root `*.md` files |
| Legacy data | `data/` (reference only) |
| Archived code | `archive/` (reference only) |

## 🎯 Common Tasks

| Task | Command |
|------|---------|
| **Test unified** | `cd scrapers/unified_scraper && python3 test_scraper.py` |
| **Test Vetution** | `python3 scripts/test_vetution_variants.py` |
| **Export variants** | `python3 scripts/export_variants_flat.py` |
| **View latest** | `ls -lt scrapers/*/data/results_*/` |
| **Cleanup old** | `rm -rf scrapers/*/data/results_202411*/` |

## 📊 Data Locations

### Unified Scraper Results
```
scrapers/unified_scraper/data/
└── results_20241205_143022/
    ├── products.json
    └── products.csv
```

### Vetution Scraper Results
```
scrapers/vetution_scraper/data/
└── results_20241205_143022/
    ├── products.json
    ├── products.csv
    └── variants_flat.csv (after export)
```

## 🔧 Configuration

```python
# Unified: Batch size
scraper.max_workers = 10

# Vetution: Credentials in code
email="vetdrughouse@gmail.com"
phone="01000059085"
```

## 📚 Key Documentation

- `README.md` - Project overview
- `WORKSPACE_GUIDE.md` - Navigation guide
- `scrapers/unified_scraper/README.md` - Unified docs
- `scrapers/vetution_scraper/USAGE_GUIDE.md` - Vetution guide

## ✅ Checklist

Before production:
- [ ] Test both scrapers
- [ ] Verify logins work
- [ ] Check data quality
- [ ] Read documentation

---

**Keep this handy!** 📌




