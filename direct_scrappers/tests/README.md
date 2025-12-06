# Tests Directory

This directory contains all test files, test data, and test utilities for the Vetutions project.

## 📁 Structure

```
tests/
├── README.md              # This file
├── test_page.html         # Test HTML page (Vetution products listing)
├── test_page2.html        # Additional test HTML page
└── [future test files]    # Python test scripts, fixtures, etc.
```

## 📄 Test Files

### HTML Test Pages

- **test_page.html** - Sample HTML from Vetution.com products page
  - Used for testing scraper selectors
  - Contains product cards with variants, prices, ingredients
  - Real-world HTML structure for development

- **test_page2.html** - Additional test HTML page
  - Backup or alternative test page
  - May contain different product structures

## 🧪 Usage

### For Scraper Development

These HTML files can be used to:
- Test CSS selectors without making HTTP requests
- Develop and debug scraping logic offline
- Validate data extraction patterns
- Test variant extraction methods

### Example Usage

```python
from bs4 import BeautifulSoup

# Load test page
with open('tests/test_page.html', 'r', encoding='utf-8') as f:
    html = f.read()
    soup = BeautifulSoup(html, 'lxml')

# Test selectors
products = soup.select('.drug-row-card')
print(f"Found {len(products)} products")
```

## 🔄 Adding New Tests

When adding new test files:

1. **Test HTML/Data**: Place in `tests/` root
2. **Python Test Scripts**: Place in `tests/` root or subdirectories
3. **Test Fixtures**: Create `tests/fixtures/` if needed
4. **Test Utilities**: Create `tests/utils/` if needed

## 📝 Naming Convention

- Test HTML files: `test_*.html` or `*_test.html`
- Test Python scripts: `test_*.py` or `*_test.py`
- Test data: `test_*.json`, `test_*.csv`

## 🎯 Future Test Organization

As the project grows, consider organizing tests by:

```
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
├── fixtures/         # Test data fixtures
├── utils/            # Test utilities
└── html/             # HTML test pages
```

---

**Note:** These test files are for development and testing purposes only.

