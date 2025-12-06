# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class VetutionVendorPrice(models.Model):
    _name = 'vetution.vendor.price'
    _description = 'Vetution Vendor Price'
    _order = 'price asc'

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        ondelete='cascade'
    )
    price = fields.Float(string='Price', digits=(16, 2), required=True)
    currency = fields.Char(string='Currency', default='EGP', required=True)
    expiration_date = fields.Date(string='Expiration Date')
    available = fields.Boolean(string='Available', default=True)
    vendor_name = fields.Char(string='Vendor Name')
    last_updated = fields.Datetime(string='Last Updated', default=fields.Datetime.now)

    @api.model
    def create(self, vals):
        """Set last_updated on create"""
        if 'last_updated' not in vals:
            vals['last_updated'] = fields.Datetime.now()
        return super().create(vals)

    def write(self, vals):
        """Update last_updated on write"""
        vals['last_updated'] = fields.Datetime.now()
        return super().write(vals)

    def name_get(self):
        """Display name for vendor price"""
        result = []
        for record in self:
            name = f"{record.price} {record.currency}"
            if record.vendor_name:
                name = f"{record.vendor_name}: {name}"
            if record.expiration_date:
                name = f"{name} (Exp: {record.expiration_date})"
            if not record.available:
                name = f"{name} [Unavailable]"
            result.append((record.id, name))
        return result

