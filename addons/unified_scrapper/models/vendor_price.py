# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class UnifiedVendorPrice(models.Model):
    """
    Vendor Price Model
    
    Tracks product prices from different external sources/vendors.
    Allows price comparison and multi-source product management.
    """
    _name = 'unified.vendor.price'
    _description = 'Vendor Price from External Source'
    _order = 'price asc, last_update desc'
    _rec_name = 'display_name'

    # Product Reference
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string='Product Template',
        required=True,
        ondelete='cascade',
        index=True,
        help='Product template this price belongs to'
    )
    
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product Variant',
        ondelete='cascade',
        index=True,
        help='Specific product variant (optional)'
    )
    
    # Source Information
    data_source_id = fields.Many2one(
        comodel_name='unified.data.source',
        string='Data Source',
        ondelete='set null',
        help='Data source configuration that imported this price'
    )
    
    source = fields.Selection(
        selection=[
            ('vetution', 'Vetution'),
            ('amin_petshop', 'Amin Petshop'),
            ('amazon', 'Amazon'),
            ('other', 'Other/Custom'),
        ],
        string='Source System',
        required=True,
        index=True,
        help='External source system'
    )
    
    vendor_name = fields.Char(
        string='Vendor Name',
        help='Specific vendor/seller name within the source'
    )
    
    # Price Information
    price = fields.Float(
        string='Price',
        required=True,
        digits='Product Price',
        help='Current price from vendor'
    )
    
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True
    )
    
    price_company_currency = fields.Monetary(
        string='Price (Company Currency)',
        compute='_compute_price_company_currency',
        store=True,
        currency_field='company_currency_id',
        help='Price converted to company currency'
    )
    
    company_currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Company Currency',
        default=lambda self: self.env.company.currency_id,
        readonly=True
    )
    
    # External Reference
    external_product_id = fields.Char(
        string='External Product ID/SKU',
        index=True,
        help='Product ID or SKU in external system'
    )
    
    external_url = fields.Char(
        string='Product URL',
        help='Direct link to product on vendor website'
    )
    
    # Availability
    availability = fields.Selection(
        selection=[
            ('in_stock', 'In Stock'),
            ('out_of_stock', 'Out of Stock'),
            ('limited', 'Limited Stock'),
            ('preorder', 'Pre-order'),
            ('unknown', 'Unknown'),
        ],
        string='Availability',
        default='unknown',
        help='Stock availability status'
    )
    
    stock_quantity = fields.Integer(
        string='Stock Quantity',
        help='Available stock quantity (if provided by source)'
    )
    
    # Metadata
    last_update = fields.Datetime(
        string='Last Updated',
        default=fields.Datetime.now,
        required=True,
        help='When this price was last updated'
    )
    
    first_seen = fields.Datetime(
        string='First Seen',
        default=fields.Datetime.now,
        readonly=True,
        help='When this vendor price was first recorded'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Uncheck to archive this vendor price'
    )
    
    notes = fields.Text(
        string='Notes',
        help='Additional notes about this vendor price'
    )
    
    # Computed Fields
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )
    
    is_lowest = fields.Boolean(
        string='Is Lowest Price',
        compute='_compute_price_comparison',
        store=False,
        help='True if this is the lowest price for the product'
    )
    
    is_highest = fields.Boolean(
        string='Is Highest Price',
        compute='_compute_price_comparison',
        store=False,
        help='True if this is the highest price for the product'
    )
    
    price_difference = fields.Float(
        string='Difference from Lowest',
        compute='_compute_price_comparison',
        store=False,
        help='Price difference from lowest vendor price'
    )

    # Constraints
    _sql_constraints = [
        ('unique_product_source', 
         'UNIQUE(product_tmpl_id, source, vendor_name)',
         'A vendor price already exists for this product and source!'),
        ('positive_price', 
         'CHECK(price >= 0)',
         'Price must be positive!'),
    ]

    @api.depends('product_tmpl_id', 'source', 'vendor_name', 'price')
    def _compute_display_name(self):
        """Compute display name for vendor price"""
        for record in self:
            parts = []
            if record.product_tmpl_id:
                parts.append(record.product_tmpl_id.name)
            if record.source:
                parts.append(dict(record._fields['source'].selection).get(record.source, record.source))
            if record.vendor_name:
                parts.append(record.vendor_name)
            if record.price:
                parts.append(f"{record.price:.2f} {record.currency_id.symbol or ''}")
            
            record.display_name = ' - '.join(parts) if parts else 'New Vendor Price'

    @api.depends('price', 'currency_id', 'company_currency_id')
    def _compute_price_company_currency(self):
        """Convert price to company currency"""
        for record in self:
            if record.currency_id and record.company_currency_id:
                record.price_company_currency = record.currency_id._convert(
                    record.price,
                    record.company_currency_id,
                    record.env.company,
                    record.last_update or fields.Date.today()
                )
            else:
                record.price_company_currency = record.price

    @api.depends('product_tmpl_id', 'price')
    def _compute_price_comparison(self):
        """Compute price comparison metrics"""
        for record in self:
            if not record.product_tmpl_id:
                record.is_lowest = False
                record.is_highest = False
                record.price_difference = 0.0
                continue
            
            # Get all active vendor prices for this product
            vendor_prices = self.search([
                ('product_tmpl_id', '=', record.product_tmpl_id.id),
                ('active', '=', True),
                ('id', '!=', record.id)
            ])
            
            all_prices = [record.price] + vendor_prices.mapped('price')
            
            if all_prices:
                lowest = min(all_prices)
                highest = max(all_prices)
                
                record.is_lowest = (record.price == lowest)
                record.is_highest = (record.price == highest)
                record.price_difference = record.price - lowest
            else:
                record.is_lowest = True
                record.is_highest = True
                record.price_difference = 0.0

    @api.model
    def create(self, vals):
        """Set first_seen on creation"""
        if 'first_seen' not in vals:
            vals['first_seen'] = fields.Datetime.now()
        return super().create(vals)

    def write(self, vals):
        """Update last_update when price changes"""
        if 'price' in vals and 'last_update' not in vals:
            vals['last_update'] = fields.Datetime.now()
        return super().write(vals)

    def action_open_external_link(self):
        """Open external product URL in browser"""
        self.ensure_one()
        if not self.external_url:
            raise ValidationError(_('No external URL configured for this vendor price.'))
        
        return {
            'type': 'ir.actions.act_url',
            'url': self.external_url,
            'target': 'new',
        }

    def action_update_price(self):
        """Trigger price update from source (placeholder for future implementation)"""
        self.ensure_one()
        # TODO: Implement in Phase 3.2
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Price Update'),
                'message': _('Price update functionality will be implemented in Phase 3.2'),
                'type': 'info',
                'sticky': False,
            }
        }

    @api.model
    def find_or_create_vendor_price(self, product_tmpl_id, source, price_data):
        """
        Find existing vendor price or create new one
        
        Args:
            product_tmpl_id: Product template ID
            source: Source system (vetution, amin_petshop, etc.)
            price_data: Dictionary with price information
            
        Returns:
            vendor_price record (existing or new)
        """
        vendor_name = price_data.get('vendor_name', '')
        
        # Search for existing vendor price
        existing = self.search([
            ('product_tmpl_id', '=', product_tmpl_id),
            ('source', '=', source),
            ('vendor_name', '=', vendor_name),
        ], limit=1)
        
        if existing:
            # Update existing vendor price
            existing.write({
                'price': price_data.get('price', existing.price),
                'currency_id': price_data.get('currency_id', existing.currency_id.id),
                'external_product_id': price_data.get('external_product_id', existing.external_product_id),
                'external_url': price_data.get('external_url', existing.external_url),
                'availability': price_data.get('availability', existing.availability),
                'stock_quantity': price_data.get('stock_quantity', existing.stock_quantity),
                'last_update': fields.Datetime.now(),
            })
            _logger.info(f"Updated vendor price for product {product_tmpl_id} from {source}")
            return existing
        else:
            # Create new vendor price
            vals = {
                'product_tmpl_id': product_tmpl_id,
                'source': source,
                'vendor_name': vendor_name,
                'price': price_data.get('price', 0.0),
                'currency_id': price_data.get('currency_id', self.env.company.currency_id.id),
                'external_product_id': price_data.get('external_product_id'),
                'external_url': price_data.get('external_url'),
                'availability': price_data.get('availability', 'unknown'),
                'stock_quantity': price_data.get('stock_quantity', 0),
                'data_source_id': price_data.get('data_source_id'),
                'notes': price_data.get('notes'),
            }
            new_price = self.create(vals)
            _logger.info(f"Created new vendor price for product {product_tmpl_id} from {source}")
            return new_price

