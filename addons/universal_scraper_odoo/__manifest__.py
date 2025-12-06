# -*- coding: utf-8 -*-
{
    'name': 'Universal Web Scraper',
    'version': '19.0.1.2.0',
    'category': 'Sales/Productivity',
    'summary': 'Web scraping engine for e-commerce sites with Odoo integration',
    'description': """
        Universal Web Scraper for Odoo
        ===============================
        
        This module integrates a professional web scraping engine into Odoo,
        allowing you to scrape product data from various e-commerce platforms
        and store them as draft records for review before importing.
        
        Features:
        ---------
        - Multi-platform support (Shopify, WooCommerce, Magento, Odoo, Amazon, eBay)
        - Automatic platform detection
        - Batch processing with multi-threading
        - Availability and stock tracking
        - Manual and scheduled scraping
        - Draft product review before import
        - Direct integration with Unified Scrapper module
        - Comprehensive scraping history and logs
        
        Supported Platforms:
        -------------------
        - Shopify stores
        - WooCommerce sites
        - Magento stores
        - Odoo e-commerce
        - Amazon (basic)
        - eBay (basic)
        - Generic e-commerce sites
        
        Workflow:
        ---------
        1. Configure scraper (URL, platform, options)
        2. Run scraper (manual or scheduled)
        3. Review scraped products in draft state
        4. Approve and import to Unified Scrapper
        5. Unified Scrapper creates final products with vendor prices
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'product',
        'mail',
        'unified_scrapper',  # Integration with unified scrapper
    ],
    'external_dependencies': {
        'python': [
            'playwright',
            'beautifulsoup4',
            'lxml',
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'data/cron_data.xml',
        'data/sample_scraper_configs.xml',
        'views/scraper_config_views.xml',
        'views/scraped_product_draft_views.xml',
        'views/scraper_job_views.xml',
        'wizards/scraper_wizard_views.xml',
        'wizards/import_to_unified_wizard_views.xml',
        'views/menu_views.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'post_init_hook': 'post_init_hook',
}

