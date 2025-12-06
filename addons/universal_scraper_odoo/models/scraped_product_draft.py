# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import json

_logger = logging.getLogger(__name__)


class ScrapedProductDraft(models.Model):
    _name = 'scraped.product.draft'
    _description = 'Scraped Product Draft'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'last_scraped desc, name'
    _rec_name = 'name'

    # Basic Product Information
    name = fields.Char(
        string='Product Name',
        required=True,
        tracking=True,
        help='Product name as scraped from the website'
    )
    url = fields.Char(
        string='Product URL',
        required=True,
        tracking=True,
        help='Direct link to the product on the source website'
    )
    sku = fields.Char(
        string='SKU',
        help='Product SKU/Code from the source'
    )
    brand = fields.Char(
        string='Brand',
        help='Product brand'
    )
    
    # Pricing
    price = fields.Float(
        string='Price',
        digits='Product Price',
        tracking=True,
        help='Product price as scraped'
    )
    currency = fields.Char(
        string='Currency',
        default='EGP',
        help='Currency code (EGP, USD, EUR, etc.)'
    )
    regular_price = fields.Float(
        string='Regular Price',
        digits='Product Price',
        help='Original price before discount (if available)'
    )
    
    # Availability & Stock
    availability = fields.Selection([
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('pre_order', 'Pre-Order'),
        ('low_stock', 'Low Stock'),
        ('unknown', 'Unknown'),
    ], string='Availability', default='unknown', tracking=True,
       help='Stock status as detected from the website')
    
    stock_quantity = fields.Integer(
        string='Stock Quantity',
        help='Available quantity (if shown on website)'
    )
    
    # Product Details
    description = fields.Text(
        string='Description',
        help='Full product description'
    )
    category = fields.Char(
        string='Category',
        help='Main category from the website'
    )
    subcategory = fields.Char(
        string='Subcategory',
        help='Subcategory from the website'
    )
    image_url = fields.Char(
        string='Image URL',
        help='URL of the product image'
    )
    
    # Scraping Metadata
    scraper_config_id = fields.Many2one(
        comodel_name='scraper.config',
        string='Scraper Configuration',
        required=True,
        ondelete='cascade',
        help='The scraper configuration that created this draft'
    )
    scraper_job_id = fields.Many2one(
        comodel_name='scraper.job',
        string='Scraping Job',
        ondelete='set null',
        help='The specific job that scraped this product'
    )
    data_source_id = fields.Many2one(
        comodel_name='unified.data.source',
        string='Data Source',
        related='scraper_config_id.data_source_id',
        store=True,
        help='The unified data source for import'
    )
    
    last_scraped = fields.Datetime(
        string='Last Scraped',
        default=fields.Datetime.now,
        help='When this product was last scraped'
    )
    raw_data = fields.Text(
        string='Raw Data',
        help='Complete raw data from scraper (JSON format)'
    )
    
    # State Management
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('imported', 'Imported'),
        ('rejected', 'Rejected'),
    ], string='State', default='draft', required=True, tracking=True,
       help='Current state of the scraped product')
    
    imported_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Imported Product',
        readonly=True,
        help='The final product created in Odoo (if imported)'
    )
    import_date = fields.Datetime(
        string='Import Date',
        readonly=True,
        help='When this draft was imported to final product'
    )
    rejection_reason = fields.Text(
        string='Rejection Reason',
        help='Why this product was rejected'
    )
    
    # Computed Fields
    is_duplicate = fields.Boolean(
        string='Potential Duplicate',
        compute='_compute_is_duplicate',
        store=True,
        help='Indicates if a similar product already exists in Odoo'
    )
    existing_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Existing Product',
        compute='_compute_is_duplicate',
        store=True,
        help='The existing product that matches this draft'
    )
    
    @api.depends('url', 'sku', 'name')
    def _compute_is_duplicate(self):
        """Check if product already exists in Odoo"""
        Product = self.env['product.product']
        
        for draft in self:
            existing = False
            
            # Try to find by URL
            if draft.url:
                existing = Product.search([
                    ('external_product_url', '=', draft.url)
                ], limit=1)
            
            # Try to find by SKU
            if not existing and draft.sku:
                existing = Product.search([
                    ('default_code', '=', draft.sku)
                ], limit=1)
            
            # Try to find by name (fuzzy match)
            if not existing and draft.name:
                existing = Product.search([
                    ('name', '=ilike', draft.name)
                ], limit=1)
            
            draft.is_duplicate = bool(existing)
            draft.existing_product_id = existing.id if existing else False
    
    def action_approve(self):
        """Approve draft product for import"""
        for draft in self:
            if draft.state != 'draft':
                raise UserError(_("Only draft products can be approved"))
            draft.state = 'approved'
    
    def action_reject(self):
        """Reject draft product"""
        for draft in self:
            if draft.state not in ('draft', 'approved'):
                raise UserError(_("Only draft or approved products can be rejected"))
            draft.state = 'rejected'
    
    def action_reset_to_draft(self):
        """Reset to draft state"""
        for draft in self:
            if draft.state == 'imported':
                raise UserError(_("Imported products cannot be reset to draft"))
            draft.state = 'draft'
    
    def action_open_url(self):
        """Open the product URL in a new browser tab"""
        self.ensure_one()
        if self.url:
            return {
                'type': 'ir.actions.act_url',
                'url': self.url,
                'target': 'new',
            }
        return {'type': 'ir.actions.act_window_close'}
    
    def action_view_existing_product(self):
        """View the existing product that matches this draft"""
        self.ensure_one()
        if self.existing_product_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'product.product',
                'view_mode': 'form',
                'res_id': self.existing_product_id.id,
                'target': 'new',
            }
        return {'type': 'ir.actions.act_window_close'}
    
    def action_import_to_unified(self):
        """Import approved drafts to Unified Scrapper"""
        approved_drafts = self.filtered(lambda d: d.state == 'approved')
        
        if not approved_drafts:
            raise UserError(_("Please approve at least one product before importing"))
        
        # Open the import wizard
        return {
            'name': _('Import to Unified Scrapper'),
            'type': 'ir.actions.act_window',
            'res_model': 'import.to.unified.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_draft_ids': [(6, 0, approved_drafts.ids)],
            },
        }
    
    def action_bulk_approve(self):
        """Bulk approve selected drafts"""
        self.filtered(lambda d: d.state == 'draft').action_approve()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('%s products approved') % len(self),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_bulk_reject(self):
        """Bulk reject selected drafts"""
        self.filtered(lambda d: d.state in ('draft', 'approved')).action_reject()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('%s products rejected') % len(self),
                'type': 'warning',
                'sticky': False,
            }
        }

