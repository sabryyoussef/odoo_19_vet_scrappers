# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ScraperWizard(models.TransientModel):
    _name = 'scraper.wizard'
    _description = 'Quick Scraper Wizard'

    # Quick scrape fields
    url = fields.Char(
        string='Target URL',
        required=True,
        help='The URL to scrape (e.g., https://example.com/collections/all)'
    )
    platform_type = fields.Selection([
        ('shopify', 'Shopify'),
        ('woocommerce', 'WooCommerce'),
        ('magento', 'Magento'),
        ('odoo', 'Odoo E-commerce'),
        ('amazon', 'Amazon'),
        ('ebay', 'eBay'),
        ('generic', 'Generic/Auto-detect'),
    ], string='Platform Type', default='generic', required=True,
       help='E-commerce platform type (auto-detected if Generic)')
    
    max_pages = fields.Integer(
        string='Max Pages',
        default=1,
        required=True,
        help='Maximum number of pages to scrape'
    )
    fetch_details = fields.Boolean(
        string='Fetch Product Details',
        default=False,
        help='Visit each product page to get full details (slower but more accurate)'
    )
    
    data_source_id = fields.Many2one(
        comodel_name='unified.data.source',
        string='Data Source',
        required=True,
        help='The data source in Unified Scrapper to associate scraped products with'
    )
    
    save_config = fields.Boolean(
        string='Save as Configuration',
        default=False,
        help='Save these settings as a reusable scraper configuration'
    )
    config_name = fields.Char(
        string='Configuration Name',
        help='Name for the saved configuration'
    )
    
    def action_run_scraper(self):
        """Run the scraper with current settings"""
        self.ensure_one()
        
        # Create or use existing config
        if self.save_config:
            if not self.config_name:
                raise UserError(_("Please provide a name for the configuration"))
            
            config = self.env['scraper.config'].create({
                'name': self.config_name,
                'url': self.url,
                'platform_type': self.platform_type,
                'max_pages': self.max_pages,
                'fetch_details': self.fetch_details,
                'data_source_id': self.data_source_id.id,
            })
            
            # Run the scraper
            return config.action_run_scraper()
        else:
            # Create temporary config
            config = self.env['scraper.config'].create({
                'name': f"Quick Scrape - {self.url}",
                'url': self.url,
                'platform_type': self.platform_type,
                'max_pages': self.max_pages,
                'fetch_details': self.fetch_details,
                'data_source_id': self.data_source_id.id,
                'active': False,  # Mark as temporary
            })
            
            # Run the scraper
            result = config.action_run_scraper()
            
            # Delete temporary config after successful run
            # (keep it if failed for debugging)
            if config.last_run_status == 'success':
                config.unlink()
            
            return result

