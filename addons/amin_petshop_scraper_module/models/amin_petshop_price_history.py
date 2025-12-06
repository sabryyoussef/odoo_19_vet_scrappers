# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AminPetshopPriceHistory(models.Model):
    _name = 'amin.petshop.price.history'
    _description = 'Amin Petshop Price History'
    _order = 'date desc'

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        ondelete='cascade',
        index=True
    )

    price = fields.Float(
        string='Price',
        digits='Product Price',
        required=True
    )

    regular_price = fields.Float(
        string='Regular Price',
        digits='Product Price'
    )

    currency = fields.Char(
        string='Currency',
        default='EGP',
        size=3
    )

    date = fields.Datetime(
        string='Date',
        required=True,
        default=fields.Datetime.now
    )

    available = fields.Boolean(
        string='Available',
        default=True,
        help='Availability at this time'
    )

    stock_status = fields.Selection([
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('low_stock', 'Low Stock'),
    ], string='Stock Status')

