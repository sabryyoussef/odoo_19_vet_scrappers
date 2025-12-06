# -*- coding: utf-8 -*-

from odoo import models, fields, api


class VetutionVendorPrice(models.Model):
    """Model to store multiple vendor prices for each product"""
    _name = 'vetution.vendor.price'
    _description = 'Vetution Vendor Price'
    _order = 'price asc'

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        ondelete='cascade',
        index=True
    )
    price = fields.Float(
        string='Price',
        required=True,
        digits='Product Price'
    )
    currency = fields.Char(
        string='Currency',
        default='EGP',
        size=3,
        help='Currency code (e.g., EGP, USD)'
    )
    expiration_date = fields.Date(
        string='Expiration Date',
        help='Product expiration date for this vendor price'
    )
    available = fields.Boolean(
        string='Available',
        default=True,
        help='Whether this vendor price is currently available'
    )
    vendor_name = fields.Char(
        string='Vendor Name',
        help='Name of the vendor/supplier'
    )

    @api.constrains('price')
    def _check_price(self):
        """Ensure price is positive"""
        for record in self:
            if record.price < 0:
                raise models.ValidationError('Price must be positive or zero.')

