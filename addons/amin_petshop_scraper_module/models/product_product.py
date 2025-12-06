# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    """Extend product.product with Amin Petshop fields"""
    _inherit = 'product.product'

    # Basic Information Fields
    amin_petshop_link = fields.Char(
        string='Amin Petshop Link',
        help='Product URL from Amin Petshop website (REQUIRED for matching)'
    )

    amin_petshop_image_url = fields.Char(
        string='Image URL',
        help='External product image URL from Amin Petshop'
    )

    amin_petshop_sku = fields.Char(
        string='SKU',
        help='Product SKU from Amin Petshop (for matching)',
        index=True
    )

    amin_petshop_brand = fields.Char(
        string='Brand',
        help='Brand name from Amin Petshop'
    )

    # Pricing Fields
    amin_petshop_price = fields.Float(
        string='Amin Petshop Price',
        digits='Product Price',
        help='Current sale price from Amin Petshop'
    )

    amin_petshop_regular_price = fields.Float(
        string='Regular Price',
        digits='Product Price',
        help='Regular price before discount'
    )

    amin_petshop_currency = fields.Char(
        string='Currency',
        default='EGP',
        size=3,
        help='Currency code (EGP/LE)'
    )

    amin_petshop_discount_percentage = fields.Float(
        string='Discount %',
        compute='_compute_discount_info',
        store=True,
        digits=(5, 2),
        help='Discount percentage if on sale'
    )

    amin_petshop_discount_amount = fields.Float(
        string='Discount Amount',
        compute='_compute_discount_info',
        store=True,
        digits='Product Price',
        help='Discount amount (regular_price - price)'
    )

    amin_petshop_has_discount = fields.Boolean(
        string='Has Discount',
        compute='_compute_discount_info',
        store=True,
        help='True if product is on sale'
    )

    amin_petshop_price_history_ids = fields.One2many(
        'amin.petshop.price.history',
        'product_id',
        string='Price History',
        help='Price change history'
    )

    # Category Fields
    amin_petshop_main_category = fields.Char(
        string='Main Category',
        help='Main category: Dog, Cat, Amin Clinic, Collections'
    )

    amin_petshop_subcategory = fields.Char(
        string='Subcategory',
        help='Subcategory: Adult Dog, Puppy, Kitten, etc.'
    )

    amin_petshop_category_path = fields.Char(
        string='Category Path',
        help='Full category hierarchy (e.g., "Dog > Adult Dog > Dry Food")'
    )

    amin_petshop_collection = fields.Char(
        string='Collection',
        help='Collection name if part of a collection'
    )

    # Availability & Status Fields
    amin_petshop_available = fields.Boolean(
        string='Available on Amin Petshop',
        default=True,
        help='Product availability status'
    )

    amin_petshop_stock_status = fields.Selection([
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('low_stock', 'Low Stock'),
    ], string='Stock Status', help='Current stock status')

    amin_petshop_last_stock_check = fields.Datetime(
        string='Last Stock Check',
        readonly=True,
        help='Last time stock was checked'
    )

    # Product Details Fields
    amin_petshop_description = fields.Text(
        string='Description',
        help='Full product description from Amin Petshop'
    )

    amin_petshop_short_description = fields.Text(
        string='Short Description',
        help='Short description/excerpt'
    )

    amin_petshop_specifications = fields.Text(
        string='Specifications',
        help='Product specifications'
    )

    amin_petshop_variants = fields.Text(
        string='Variants',
        help='Product variants (sizes, colors, etc.) as JSON string'
    )

    # Tracking Fields
    amin_petshop_first_seen = fields.Datetime(
        string='First Seen',
        readonly=True,
        help='When product was first imported from Amin Petshop'
    )

    amin_petshop_last_updated = fields.Datetime(
        string='Last Updated',
        readonly=True,
        help='Last update timestamp from Amin Petshop'
    )

    amin_petshop_last_price_update = fields.Datetime(
        string='Last Price Update',
        readonly=True,
        help='Last price update timestamp'
    )

    amin_petshop_update_count = fields.Integer(
        string='Update Count',
        default=0,
        readonly=True,
        help='Number of times product was updated'
    )

    @api.depends('amin_petshop_price', 'amin_petshop_regular_price')
    def _compute_discount_info(self):
        """Compute discount information"""
        for record in self:
            if record.amin_petshop_regular_price and record.amin_petshop_regular_price > 0:
                if record.amin_petshop_price and record.amin_petshop_price < record.amin_petshop_regular_price:
                    record.amin_petshop_has_discount = True
                    record.amin_petshop_discount_amount = record.amin_petshop_regular_price - record.amin_petshop_price
                    record.amin_petshop_discount_percentage = (
                        (record.amin_petshop_discount_amount / record.amin_petshop_regular_price) * 100
                    )
                else:
                    record.amin_petshop_has_discount = False
                    record.amin_petshop_discount_amount = 0.0
                    record.amin_petshop_discount_percentage = 0.0
            else:
                record.amin_petshop_has_discount = False
                record.amin_petshop_discount_amount = 0.0
                record.amin_petshop_discount_percentage = 0.0

    def update_from_amin_petshop_data(self, scraped_data):
        """
        Update product from scraped Amin Petshop data

        Args:
            scraped_data (dict): Dictionary containing scraped product data

        Returns:
            bool: True if updated successfully
        """
        self.ensure_one()

        update_vals = {}
        now = fields.Datetime.now()

        # Basic Information
        if scraped_data.get('link'):
            update_vals['amin_petshop_link'] = scraped_data['link']
        if scraped_data.get('image_url'):
            update_vals['amin_petshop_image_url'] = scraped_data['image_url']
        if scraped_data.get('sku'):
            update_vals['amin_petshop_sku'] = scraped_data['sku']
        if scraped_data.get('brand'):
            update_vals['amin_petshop_brand'] = scraped_data['brand']

        # Pricing - Track price changes
        if scraped_data.get('price') is not None:
            old_price = self.amin_petshop_price
            new_price = scraped_data['price']

            # Create price history if price changed
            if old_price and old_price != new_price:
                self.env['amin.petshop.price.history'].create({
                    'product_id': self.id,
                    'price': old_price,
                    'regular_price': self.amin_petshop_regular_price,
                    'currency': self.amin_petshop_currency or 'EGP',
                    'date': now,
                    'available': self.amin_petshop_available,
                    'stock_status': self.amin_petshop_stock_status
                })

            update_vals['amin_petshop_price'] = new_price
            update_vals['amin_petshop_last_price_update'] = now

        if scraped_data.get('regular_price') is not None:
            update_vals['amin_petshop_regular_price'] = scraped_data['regular_price']
        if scraped_data.get('currency'):
            update_vals['amin_petshop_currency'] = scraped_data['currency']

        # Category
        if scraped_data.get('main_category'):
            update_vals['amin_petshop_main_category'] = scraped_data['main_category']
        if scraped_data.get('subcategory'):
            update_vals['amin_petshop_subcategory'] = scraped_data['subcategory']
        if scraped_data.get('category_path'):
            update_vals['amin_petshop_category_path'] = scraped_data['category_path']
        if scraped_data.get('collection'):
            update_vals['amin_petshop_collection'] = scraped_data['collection']

        # Availability
        if 'available' in scraped_data:
            update_vals['amin_petshop_available'] = scraped_data['available']
        if scraped_data.get('stock_status'):
            update_vals['amin_petshop_stock_status'] = scraped_data['stock_status']
            update_vals['amin_petshop_last_stock_check'] = now

        # Details
        if scraped_data.get('description'):
            update_vals['amin_petshop_description'] = scraped_data['description']
        if scraped_data.get('short_description'):
            update_vals['amin_petshop_short_description'] = scraped_data['short_description']
        if scraped_data.get('specifications'):
            update_vals['amin_petshop_specifications'] = scraped_data['specifications']
        if scraped_data.get('variants'):
            if isinstance(scraped_data['variants'], (list, dict)):
                update_vals['amin_petshop_variants'] = json.dumps(scraped_data['variants'])
            else:
                update_vals['amin_petshop_variants'] = str(scraped_data['variants'])

        # Tracking
        if not self.amin_petshop_first_seen:
            update_vals['amin_petshop_first_seen'] = now
        update_vals['amin_petshop_last_updated'] = now
        update_vals['amin_petshop_update_count'] = (self.amin_petshop_update_count or 0) + 1

        # Update product
        if update_vals:
            self.write(update_vals)

        return True

    def action_open_amin_petshop_link(self):
        """Open product link in Amin Petshop website"""
        self.ensure_one()
        if self.amin_petshop_link:
            return {
                'type': 'ir.actions.act_url',
                'url': self.amin_petshop_link,
                'target': 'new',
            }
        return False

    def action_update_from_amin_petshop(self):
        """Open update wizard"""
        self.ensure_one()
        return {
            'name': 'Update from Amin Petshop',
            'type': 'ir.actions.act_window',
            'res_model': 'amin.petshop.update.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_product_ids': [(6, 0, self.ids)],
            },
        }

    def action_view_price_history(self):
        """View price history for this product"""
        self.ensure_one()
        return {
            'name': 'Price History',
            'type': 'ir.actions.act_window',
            'res_model': 'amin.petshop.price.history',
            'view_mode': 'list,graph',
            'domain': [('product_id', '=', self.id)],
            'context': {'default_product_id': self.id},
        }

