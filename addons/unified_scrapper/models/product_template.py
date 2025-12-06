# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    """
    Product Template Extension for External Source Tracking
    
    Extends product.template with related fields from product.product
    for easier access in template views.
    """
    _inherit = 'product.template'

    # Related fields from product.product (variant)
    external_source = fields.Selection(
        related='product_variant_ids.external_source',
        readonly=False,
        string='External Source',
        store=True
    )
    
    external_product_id = fields.Char(
        related='product_variant_ids.external_product_id',
        readonly=False,
        string='External Product ID',
        store=True
    )
    
    external_product_url = fields.Char(
        related='product_variant_ids.external_product_url',
        readonly=False,
        string='External Product URL',
        store=True
    )
    
    external_last_sync = fields.Datetime(
        related='product_variant_ids.external_last_sync',
        string='Last Sync',
        store=True
    )
    
    external_sync_status = fields.Selection(
        related='product_variant_ids.external_sync_status',
        readonly=False,
        string='Sync Status',
        store=True
    )
    
    external_sync_error = fields.Text(
        related='product_variant_ids.external_sync_error',
        string='Sync Error Message',
        store=True
    )
    
    external_import_date = fields.Datetime(
        related='product_variant_ids.external_import_date',
        string='First Import Date',
        store=True
    )
    
    external_update_count = fields.Integer(
        related='product_variant_ids.external_update_count',
        string='Update Count',
        store=True
    )
    
    # Vendor Prices
    vendor_price_ids = fields.One2many(
        comodel_name='unified.vendor.price',
        inverse_name='product_tmpl_id',
        string='Vendor Prices',
        help='Prices from different external sources/vendors'
    )
    
    vendor_price_count = fields.Integer(
        string='Vendor Price Count',
        compute='_compute_vendor_price_stats',
        help='Number of vendor prices for this product'
    )
    
    lowest_vendor_price = fields.Float(
        string='Lowest Vendor Price',
        compute='_compute_vendor_price_stats',
        digits='Product Price',
        help='Lowest price among all vendors'
    )
    
    highest_vendor_price = fields.Float(
        string='Highest Vendor Price',
        compute='_compute_vendor_price_stats',
        digits='Product Price',
        help='Highest price among all vendors'
    )
    
    average_vendor_price = fields.Float(
        string='Average Vendor Price',
        compute='_compute_vendor_price_stats',
        digits='Product Price',
        help='Average price across all vendors'
    )
    
    @api.depends('vendor_price_ids', 'vendor_price_ids.price', 'vendor_price_ids.active')
    def _compute_vendor_price_stats(self):
        """Compute vendor price statistics"""
        for product in self:
            active_prices = product.vendor_price_ids.filtered(lambda p: p.active)
            prices = active_prices.mapped('price')
            
            product.vendor_price_count = len(active_prices)
            
            if prices:
                product.lowest_vendor_price = min(prices)
                product.highest_vendor_price = max(prices)
                product.average_vendor_price = sum(prices) / len(prices)
            else:
                product.lowest_vendor_price = 0.0
                product.highest_vendor_price = 0.0
                product.average_vendor_price = 0.0

    # Action Methods (delegate to variant)
    def action_open_external_link(self):
        """Open external product URL in browser"""
        self.ensure_one()
        if self.product_variant_ids:
            return self.product_variant_ids[0].action_open_external_link()
        return {'type': 'ir.actions.act_window_close'}

    def action_sync_from_source(self):
        """Trigger re-import/sync of this product from external source"""
        self.ensure_one()
        if self.product_variant_ids:
            return self.product_variant_ids[0].action_sync_from_source()
        return {'type': 'ir.actions.act_window_close'}

    def action_view_sync_history(self):
        """View import/sync history for this product"""
        self.ensure_one()
        if self.product_variant_ids:
            return self.product_variant_ids[0].action_view_sync_history()
        return {'type': 'ir.actions.act_window_close'}

    def action_clear_sync_error(self):
        """Clear sync error status"""
        self.ensure_one()
        if self.product_variant_ids:
            return self.product_variant_ids[0].action_clear_sync_error()
        return {'type': 'ir.actions.act_window_close'}
    
    def action_view_vendor_prices(self):
        """View all vendor prices for this product"""
        self.ensure_one()
        return {
            'name': _('Vendor Prices'),
            'type': 'ir.actions.act_window',
            'res_model': 'unified.vendor.price',
            'view_mode': 'list,form',
            'domain': [('product_tmpl_id', '=', self.id)],
            'context': {
                'default_product_tmpl_id': self.id,
                'default_source': self.external_source or 'other',
            },
        }

