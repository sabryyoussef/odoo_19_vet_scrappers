# Odoo 19 Veterinary Scraper Modules

A comprehensive Odoo 19 module suite for web scraping and product data integration from various e-commerce platforms, specifically designed for veterinary and pet shop businesses.

## 🚀 Features

### 1. **Unified Scraper Module** (`unified_scrapper`)

A powerful, flexible scraping framework that supports multiple data sources and authentication methods.

#### Key Features:
- **Multiple Authentication Methods:**
  - Basic Authentication
  - Token-based Authentication
  - API Key Authentication
  - Website Form Login
  - API/AJAX Login
  - Browser Automation Login
  - Manual Cookie Import

- **Category-Based Import:**
  - Import products by category
  - Hierarchical category mapping
  - Automatic Odoo category creation
  - Category-filtered product imports

- **Data Source Management:**
  - Multiple data source configurations
  - Connection testing
  - Login validation
  - Session management

- **Import Wizard:**
  - Multi-step import process
  - Data validation and preview
  - Category filtering
  - Duplicate detection
  - Error handling

- **Scrape & Import:**
  - Direct scraping from category URLs
  - Automatic scraper configuration
  - Integration with Universal Scraper module
  - Real-time progress tracking

### 2. **Universal Scraper Odoo** (`universal_scraper_odoo`)

A robust web scraping engine with Playwright integration for dynamic content extraction.

#### Key Features:
- **Browser Automation:**
  - Chromium-based scraping
  - Docker-compatible configuration
  - Headless mode support
  - Cookie management

- **Scraper Configurations:**
  - Platform-specific scrapers
  - Customizable selectors
  - Max pages limit
  - Fetch details option

- **Sample Configurations:**
  - Pre-configured scrapers for Amin Petshop
  - Example configurations for Vetution
  - Ready-to-use category scrapers

## 📦 Modules

### `unified_scrapper`
- **Version:** 19.0.4.3.2
- **Category:** Tools
- **Dependencies:** `base`, `product`, `stock`

### `universal_scraper_odoo`
- **Version:** 19.0.1.1.1
- **Category:** Tools
- **Dependencies:** `base`, `product`

## 🛠️ Installation

### Prerequisites
- Odoo 19
- Docker & Docker Compose
- Python 3.12+
- PostgreSQL 15

### Docker Setup

1. **Clone the repository:**
```bash
git clone https://github.com/sabryyoussef/odoo_19_vet_scrappers.git
cd odoo_19_vet_scrappers
```

2. **Start Docker containers:**
```bash
sudo docker-compose up -d
```

3. **Wait for Odoo to start (30-60 seconds):**
```bash
sudo docker logs -f odoo_19_vetutions-odoo-1
```

4. **Access Odoo:**
   - URL: http://localhost:8070
   - Create a new database or use existing one

5. **Install modules:**
   - Go to Apps menu
   - Update Apps List
   - Search for "Unified Scraper" or "Universal Scraper"
   - Click Install

## 🔧 Configuration

### 1. Data Source Setup

Navigate to: **Unified Scraper → Configuration → Data Sources**

#### Example: Amin Petshop Configuration
- **Name:** Amin Petshop
- **Source Type:** Web API
- **Source URL:** https://aminpetshop.com
- **Authentication:** Browser Automation
- **Login Method:** Browser
- **Login URL:** https://aminpetshop.com/account/login
- **Username:** your_email@example.com
- **Password:** your_password

### 2. Category Mapping

Navigate to: **Unified Scraper → Configuration → Category Mappings**

Pre-configured categories for Amin Petshop:
- Dogs (with subcategories: Food, Treats, Toys, etc.)
- Cats (with subcategories: Food, Treats, Toys, etc.)
- Offers & Sales
- Clinic

### 3. Scraper Configuration

Navigate to: **Universal Scraper → Configuration → Scraper Configs**

Sample configurations included for:
- Amin Petshop categories (Dogs Food, Cats Food, etc.)
- Vetution products

## 📖 Usage

### Method 1: Category-Based Scraping (Recommended)

1. **Navigate to Category Mappings:**
   ```
   Unified Scraper → Configuration → Category Mappings
   ```

2. **Select a category** (e.g., "Dogs - Food")

3. **Click "Scrape & Import"** button

4. **Wait for scraping to complete**

5. **Review imported products** in draft state

### Method 2: File Import

1. **Prepare JSON file** with product data

2. **Navigate to Data Sources:**
   ```
   Unified Scraper → Data Sources
   ```

3. **Select a data source**

4. **Click "Import Products"**

5. **Upload JSON file**

6. **Review and confirm import**

### Method 3: Direct Scraper Execution

1. **Navigate to Scraper Configs:**
   ```
   Universal Scraper → Configuration → Scraper Configs
   ```

2. **Select a scraper configuration**

3. **Click "Run Scraper Now"**

4. **Monitor progress in logs**

## 🐛 Troubleshooting

### Chromium Crashes in Docker

If you encounter `BrowserType.launch: Target page, context or browser has been closed` errors:

1. **Verify Docker configuration:**
   - Check `shm_size: '2gb'` in docker-compose.yml
   - Check `cap_add: - SYS_ADMIN` in docker-compose.yml

2. **Verify Chromium dependencies:**
   - All dependencies are included in the Dockerfile
   - Rebuild if necessary: `sudo docker-compose build`

3. **Check browser arguments:**
   - The `--single-process` flag is critical for Docker
   - See `CHROMIUM_DOCKER_FIX.md` for details

### Login Issues

1. **Test connection first:**
   - Click "Test Connection" button on data source
   - Verify URL is accessible

2. **Test login:**
   - Click "Test Login" button
   - Check login status and error messages

3. **For invisible CAPTCHA:**
   - Use "Browser Automation" login method
   - Manually import cookies after logging in via browser

### Import Errors

1. **Check JSON format:**
   - Validate JSON syntax
   - Ensure required fields are present

2. **Check category mapping:**
   - Verify external category IDs match
   - Enable import for categories

3. **Check logs:**
   ```bash
   sudo docker logs odoo_19_vetutions-odoo-1
   ```

## 📚 Documentation

- **Testing Guide:** `addons/unified_scrapper/document/TESTING_GUIDE.md`
- **Complete Workflow:** `addons/unified_scrapper/document/COMPLETE_WORKFLOW_TESTING.md`
- **Chromium Fix:** `CHROMIUM_DOCKER_FIX.md`

## 🔐 Security Notes

- **Never commit credentials** to the repository
- Use environment variables for sensitive data
- Sample data includes placeholder credentials only
- Update credentials in Odoo UI after installation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the LGPL-3 License.

## 🙏 Acknowledgments

- Built for veterinary and pet shop businesses
- Designed for Amin Petshop and Vetution integration
- Powered by Odoo 19 and Playwright

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check documentation files
- Review error logs

## 🎯 Roadmap

- [ ] Additional platform support
- [ ] Advanced scraping rules
- [ ] Scheduled imports
- [ ] Real-time sync
- [ ] Product matching algorithms
- [ ] Image optimization
- [ ] Multi-language support

---

**Built with ❤️ for the veterinary community**
