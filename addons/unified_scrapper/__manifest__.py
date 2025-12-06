# -*- coding: utf-8 -*-
{
    'name': 'Unified Product Scrapper',
    'version': '19.0.4.3.2',
    'category': 'Sales',
    'summary': 'Central integration layer for products from multiple external data sources',
    'description': """
        Unified Product Scrapper
        ========================
        
        This module provides a centralized framework for importing and managing 
        products from multiple external sources (Vetution, Amin Petshop, Amazon, etc.).
        
        Key Features:
        * Configure external data sources (CSV/JSON/API)
        * Define field mappings from external data to Odoo product fields
        * Tag and identify products by their source system
        * Generic, extensible design for any future data source
        
        Note: All web scraping is done externally. This module only consumes 
        structured data (CSV/JSON) provided by external scraping systems.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'product',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sample_data_sources.xml',
        'data/amin_petshop_categories.xml',
        'views/data_source_views.xml',
        'views/field_mapping_views.xml',
        'views/import_history_views.xml',
        'views/vendor_price_views.xml',
        'views/category_mapping_views.xml',
        'views/product_views.xml',
        'wizards/import_wizard_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

