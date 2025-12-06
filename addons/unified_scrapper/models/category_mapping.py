# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class CategoryMapping(models.Model):
    """
    Category Mapping Model
    
    Maps external source categories to Odoo product categories.
    Allows filtering imports by category.
    """
    _name = 'unified.category.mapping'
    _description = 'External Category to Odoo Category Mapping'
    _order = 'data_source_id, sequence, external_category_name'
    _rec_name = 'external_category_name'

    # Basic Information
    data_source_id = fields.Many2one(
        comodel_name='unified.data.source',
        string='Data Source',
        required=True,
        ondelete='cascade',
        help='The external data source this category belongs to'
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of display'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Enable/disable this category mapping'
    )
    
    # External Category Information
    external_category_id = fields.Char(
        string='External Category ID',
        help='Category ID from external source (e.g., "12345")'
    )
    
    external_category_name = fields.Char(
        string='External Category Name',
        required=True,
        help='Category name from external source (e.g., "Dog Food")'
    )
    
    external_category_url = fields.Char(
        string='External Category URL',
        help='URL to scrape products from this category'
    )
    
    external_parent_id = fields.Char(
        string='External Parent Category ID',
        help='Parent category ID from external source'
    )
    
    # Odoo Category Mapping
    odoo_category_id = fields.Many2one(
        comodel_name='product.category',
        string='Odoo Product Category',
        help='Map to this Odoo category'
    )
    
    auto_create_category = fields.Boolean(
        string='Auto-Create Category',
        default=True,
        help='Automatically create Odoo category if not mapped'
    )
    
    # Import Settings
    import_enabled = fields.Boolean(
        string='Enable Import',
        default=True,
        help='Include this category in imports'
    )
    
    product_count = fields.Integer(
        string='Product Count',
        help='Number of products in this category (from external source)'
    )
    
    last_sync_date = fields.Datetime(
        string='Last Sync Date',
        readonly=True,
        help='Last time this category was synced'
    )
    
    # Statistics
    products_imported = fields.Integer(
        string='Products Imported',
        readonly=True,
        default=0,
        help='Number of products imported from this category'
    )
    
    notes = fields.Text(
        string='Notes',
        help='Additional notes about this category'
    )

    # SQL Constraints
    _sql_constraints = [
        ('unique_external_category', 
         'UNIQUE(data_source_id, external_category_id)',
         'External category ID must be unique per data source!'),
    ]

    # Methods
    @api.model
    def sync_categories_from_source(self, data_source_id):
        """
        Sync categories from external data source
        This will be called by the scraper to update category list
        """
        data_source = self.env['unified.data.source'].browse(data_source_id)
        
        # TODO: Implement category scraping logic
        # This will be integrated with the universal_scraper_odoo module
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Category Sync'),
                'message': _('Category sync will be implemented with scraper integration'),
                'type': 'info',
            }
        }

    def action_import_products(self):
        """
        Import products from this category
        Opens import wizard with category filter (manual file upload)
        """
        self.ensure_one()
        
        return {
            'name': _('Import Products: %s') % self.external_category_name,
            'type': 'ir.actions.act_window',
            'res_model': 'unified.import.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_data_source_id': self.data_source_id.id,
                'default_category_filter': self.external_category_id,
                'default_category_name': self.external_category_name,
            }
        }

    def action_scrape_and_import(self):
        """
        Triggers the Universal Scraper to scrape products from this category's URL
        and saves them as draft products.
        """
        self.ensure_one()
        
        if not self.external_category_url:
            raise UserError(_("No External Category URL configured for this category."))
        
        # Check if universal_scraper_odoo is installed
        if 'scraper.config' not in self.env:
            raise UserError(_(
                "The 'Universal Web Scraper' module is not installed. "
                "Please install it to use the 'Scrape & Import' functionality."
            ))
        
        # Find or create a scraper.config for this category
        ScraperConfig = self.env['scraper.config']
        
        # Use a unique name for the scraper config based on data source and category
        config_name = f"{self.data_source_id.name} - {self.external_category_name}"
        
        scraper_config = ScraperConfig.search([
            ('name', '=', config_name),
            ('data_source_id', '=', self.data_source_id.id),
            ('url', '=', self.external_category_url),
        ], limit=1)
        
        if not scraper_config:
            scraper_config = ScraperConfig.create({
                'name': config_name,
                'url': self.external_category_url,
                'platform_type': self.data_source_id.source_system if self.data_source_id.source_system in ['shopify', 'woocommerce', 'magento', 'odoo', 'amazon', 'ebay'] else 'generic',
                'data_source_id': self.data_source_id.id,
                'max_pages': 5, # Default to 5 pages for category scrape
                'fetch_details': True,
                'headless': True,
                'max_workers': 5,
                'active': True,
                'requires_login': self.data_source_id.login_method != 'none',
                'login_email': self.data_source_id.website_username,
                'login_password': self.data_source_id.website_password,
            })
            _logger.info(f"Created new scraper config for category {self.external_category_name}: {scraper_config.name}")
        else:
            _logger.info(f"Found existing scraper config for category {self.external_category_name}: {scraper_config.name}")
        
        # Trigger the scraping job
        scraper_config.action_run_scraper()
        
        # Update last sync date for the category
        self.last_sync_date = fields.Datetime.now()
        
        # Return an action to view the scraped products (drafts)
        return {
            'name': _('Scraped Products for %s') % self.external_category_name,
            'type': 'ir.actions.act_window',
            'res_model': 'scraped.product.draft',
            'view_mode': 'list,form',
            'domain': [('scraper_config_id', '=', scraper_config.id)],
            'context': {'search_default_scraper_config_id': scraper_config.id},
            'target': 'current',
        }

    def action_create_odoo_category(self):
        """
        Create corresponding Odoo category
        """
        self.ensure_one()
        
        if self.odoo_category_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Already Mapped'),
                    'message': _('This category is already mapped to: %s') % self.odoo_category_id.name,
                    'type': 'warning',
                }
            }
        
        # Create new Odoo category
        category = self.env['product.category'].create({
            'name': self.external_category_name,
        })
        
        self.odoo_category_id = category.id
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Category Created'),
                'message': _('Created Odoo category: %s') % category.name,
                'type': 'success',
            }
        }

    def action_view_products(self):
        """
        View products imported from this category
        """
        self.ensure_one()
        
        # Find products with this external category
        # This assumes products have external_category field
        return {
            'name': _('Products: %s') % self.external_category_name,
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'view_mode': 'list,form',
            'domain': [
                ('external_source', '=', self.data_source_id.source_system),
                # Add category filter when field is added to product
            ],
        }

