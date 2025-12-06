# -*- coding: utf-8 -*-
{
    'name': 'Amin Petshop Scraper',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'Import and manage products from Amin Petshop',
    'description': """
        Amin Petshop Scraper Module
        ===========================
        
        This module allows you to:
        * Import products from Amin Petshop website
        * Track prices and availability
        * Monitor price history
        * Update products automatically
        
        Features:
        * JSON/CSV import functionality
        * Price history tracking
        * Category management
        * Stock status monitoring
    """,
    'author': 'Your Company',
    'website': 'https://aminpetshop.com',
    'depends': [
        'base',
        'product',
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/amin_petshop_price_history_views.xml',
        'views/product_product_views.xml',
        'wizard/amin_petshop_import_wizard_views.xml',
        'wizard/amin_petshop_update_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

