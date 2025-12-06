# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Related fields from product.product (variant)
    amin_petshop_link = fields.Char(related='product_variant_ids.amin_petshop_link', readonly=False, string='Amin Petshop Link')
    amin_petshop_image_url = fields.Char(related='product_variant_ids.amin_petshop_image_url', readonly=False, string='Image URL')
    amin_petshop_sku = fields.Char(related='product_variant_ids.amin_petshop_sku', readonly=False, string='SKU')
    amin_petshop_brand = fields.Char(related='product_variant_ids.amin_petshop_brand', readonly=False, string='Brand')
    
    amin_petshop_price = fields.Float(related='product_variant_ids.amin_petshop_price', readonly=False, string='Amin Petshop Price')
    amin_petshop_regular_price = fields.Float(related='product_variant_ids.amin_petshop_regular_price', readonly=False, string='Regular Price')
    amin_petshop_currency = fields.Char(related='product_variant_ids.amin_petshop_currency', readonly=False, string='Currency')
    amin_petshop_discount_percentage = fields.Float(related='product_variant_ids.amin_petshop_discount_percentage', string='Discount %')
    amin_petshop_discount_amount = fields.Float(related='product_variant_ids.amin_petshop_discount_amount', string='Discount Amount')
    amin_petshop_has_discount = fields.Boolean(related='product_variant_ids.amin_petshop_has_discount', string='Has Discount')
    amin_petshop_last_price_update = fields.Datetime(related='product_variant_ids.amin_petshop_last_price_update', readonly=False, string='Last Price Update')
    amin_petshop_price_history_ids = fields.One2many(related='product_variant_ids.amin_petshop_price_history_ids', string='Price History')
    
    amin_petshop_main_category = fields.Char(related='product_variant_ids.amin_petshop_main_category', readonly=False, string='Main Category')
    amin_petshop_subcategory = fields.Char(related='product_variant_ids.amin_petshop_subcategory', readonly=False, string='Subcategory')
    amin_petshop_category_path = fields.Char(related='product_variant_ids.amin_petshop_category_path', readonly=False, string='Category Path')
    amin_petshop_collection = fields.Char(related='product_variant_ids.amin_petshop_collection', readonly=False, string='Collection')
    
    amin_petshop_available = fields.Boolean(related='product_variant_ids.amin_petshop_available', readonly=False, string='Available')
    amin_petshop_stock_status = fields.Selection(related='product_variant_ids.amin_petshop_stock_status', readonly=False, string='Stock Status')
    amin_petshop_last_stock_check = fields.Datetime(related='product_variant_ids.amin_petshop_last_stock_check', readonly=False, string='Last Stock Check')
    
    amin_petshop_short_description = fields.Text(related='product_variant_ids.amin_petshop_short_description', readonly=False, string='Short Description')
    amin_petshop_description = fields.Text(related='product_variant_ids.amin_petshop_description', readonly=False, string='Description')
    amin_petshop_specifications = fields.Text(related='product_variant_ids.amin_petshop_specifications', readonly=False, string='Specifications')
    amin_petshop_variants = fields.Text(related='product_variant_ids.amin_petshop_variants', readonly=False, string='Variants')
    
    amin_petshop_first_seen = fields.Datetime(related='product_variant_ids.amin_petshop_first_seen', readonly=False, string='First Seen')
    amin_petshop_last_updated = fields.Datetime(related='product_variant_ids.amin_petshop_last_updated', readonly=False, string='Last Updated')
    amin_petshop_update_count = fields.Integer(related='product_variant_ids.amin_petshop_update_count', readonly=False, string='Update Count')

    def action_open_amin_petshop_link(self):
        """Open Amin Petshop link in browser"""
        self.ensure_one()
        if self.product_variant_ids:
            return self.product_variant_ids[0].action_open_amin_petshop_link()
        return {'type': 'ir.actions.act_window_close'}

    def action_update_from_amin_petshop(self):
        """Update product from Amin Petshop data"""
        self.ensure_one()
        if self.product_variant_ids:
            return self.product_variant_ids[0].action_update_from_amin_petshop()
        return {'type': 'ir.actions.act_window_close'}

    def action_view_price_history(self):
        """View price history"""
        self.ensure_one()
        if self.product_variant_ids:
            return self.product_variant_ids[0].action_view_price_history()
        return {'type': 'ir.actions.act_window_close'}

