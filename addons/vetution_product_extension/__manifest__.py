# -*- coding: utf-8 -*-
{
    'name': 'Vetution Product Extension',
    'version': '19.0.1.0.1',
    'category': 'Sales',
    'summary': 'Extend Product Model with Veterinary Product Data Fields',
    'description': """
        Veterinary Product Data Import Module
        =====================================
        
        This module extends the product.product model to support veterinary product data
        imported from e-commerce websites. It includes:
        
        * Extended product fields for veterinary data
        * Multi-vendor pricing support
        * JSON and CSV import wizard
        * Comprehensive product information fields
    """,
    'author': 'Vetution',
    'website': 'https://www.vetution.com',
    'depends': ['product', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/vendor_price_views.xml',
        'views/product_views.xml',
        'wizard/import_product_data_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
    'post_init_hook': 'post_init_hook',
    'post_load': None,
}

