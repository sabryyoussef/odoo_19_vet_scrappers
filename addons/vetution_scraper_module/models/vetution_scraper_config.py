# -*- coding: utf-8 -*-

from odoo import models, fields, api


class VetutionScraperConfig(models.Model):
    _name = 'vetution.scraper.config'
    _description = 'Vetution Scraper Configuration'
    _rec_name = 'name'

    name = fields.Char(string='Configuration Name', required=True, default='Default')
    active = fields.Boolean(string='Active', default=True)
    
    # Website settings
    base_url = fields.Char(string='Base URL', default='https://www.vetution.com', required=True)
    categories = fields.Char(string='Categories', default='pharmacy-vaccines', help='Comma-separated category filters')
    
    # Login credentials
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    password = fields.Char(string='Password')
    
    # Scraping settings
    start_page = fields.Integer(string='Start Page', default=1)
    end_page = fields.Integer(string='End Page', default=23)
    fetch_details = fields.Boolean(string='Fetch Detailed Information', default=True, 
                                   help='Fetch detailed product information (slower but complete)')
    delay_between_pages = fields.Float(string='Delay Between Pages (seconds)', default=1.0)
    delay_between_products = fields.Float(string='Delay Between Products (seconds)', default=0.3)
    
    # Update settings
    update_existing = fields.Boolean(string='Update Existing Products', default=True)
    create_new = fields.Boolean(string='Create New Products', default=True)
    match_by = fields.Selection([
        ('name', 'Product Name'),
        ('link', 'Vetution Link'),
        ('barcode', 'Barcode'),
    ], string='Match Products By', default='link', required=True)
    
    # Auto-update settings
    auto_update_enabled = fields.Boolean(string='Enable Auto Updates', default=False)
    update_frequency = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('custom', 'Custom'),
    ], string='Update Frequency', default='daily')
    update_time = fields.Float(string='Update Time', default=2.0, 
                               help='Hour of day to run update (0-23)')
    
    # Product creation defaults
    default_categ_id = fields.Many2one('product.category', string='Default Product Category')
    default_sale_ok = fields.Boolean(string='Can be Sold', default=True)
    default_purchase_ok = fields.Boolean(string='Can be Purchased', default=False)
    
    @api.model
    def get_default_config(self):
        """Get the active configuration"""
        config = self.search([('active', '=', True)], limit=1)
        if not config:
            config = self.create({'name': 'Default'})
        return config

