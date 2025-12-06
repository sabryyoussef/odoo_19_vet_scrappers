{
    'name': 'Vetution Product Scraper',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'Scrape and import veterinary products from Vetution.com',
    'description': """
        Vetution Product Scraper Module
        ================================
        
        This module allows you to:
        * Scrape products from Vetution.com website
        * Import scraped data into Odoo products
        * Schedule daily updates for prices and availability
        * Manage vendor prices and product details
        * Track product changes and updates
        
        Features:
        * Automated scraping with Playwright
        * JSON/CSV import functionality
        * Daily price and availability updates
        * Multi-vendor price tracking
        * Product detail management
    """,
    'author': 'Vetution',
    'website': 'https://www.vetution.com',
    'depends': [
        'base',
        'product',
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/vetution_security.xml',
        'data/ir_cron_data.xml',
        'views/product_product_views.xml',
        'views/vetution_vendor_price_views.xml',
        'views/vetution_scraper_menus.xml',
        'wizard/vetution_scrape_wizard_views.xml',
        'wizard/vetution_import_wizard_views.xml',
        'wizard/vetution_update_wizard_views.xml',
    ],
    'external_dependencies': {
        'python': ['playwright', 'beautifulsoup4', 'requests'],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

