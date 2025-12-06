# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Basic Information
    vetution_link = fields.Char(string='Vetution Link', help='Product URL from Vetution.com')
    vetution_brand = fields.Char(string='Brand')
    vetution_brand_link = fields.Char(string='Brand Link')
    vetution_image_url = fields.Char(string='External Image URL')
    vetution_review_count = fields.Integer(string='Review Count')
    vetution_total_reviews = fields.Integer(string='Total Reviews')
    vetution_rating = fields.Float(string='Rating', digits=(2, 1))

    # Product Attributes
    vetution_ingredients = fields.Text(string='Ingredients', help='Active ingredients (comma-separated)')
    vetution_sizes = fields.Text(string='Sizes', help='Available product sizes/variants')
    vetution_tags = fields.Text(string='Tags', help='Product tags')
    vetution_species = fields.Text(string='Species', help='Target species (Canine, Feline, etc.)')

    # Delivery & Storage
    vetution_express_delivery = fields.Boolean(string='Express Delivery Available')
    vetution_cold_chain = fields.Boolean(string='Requires Cold Chain')

    # Pricing
    vetution_price = fields.Float(string='Vetution Price', digits=(16, 2))
    vetution_currency = fields.Char(string='Currency', default='EGP')
    vetution_min_price = fields.Float(string='Min Price', digits=(16, 2))
    vetution_max_price = fields.Float(string='Max Price', digits=(16, 2))
    vetution_vendor_price_ids = fields.One2many(
        'vetution.vendor.price',
        'product_id',
        string='Vendor Prices'
    )

    # Detailed Information Sections
    vetution_composition = fields.Text(string='Composition')
    vetution_indications = fields.Text(string='Indications')
    vetution_dose_administration = fields.Text(string='Dose & Administration')
    vetution_precautions = fields.Text(string='Precautions')
    vetution_pregnancy = fields.Text(string='Pregnancy Information')
    vetution_side_effects = fields.Text(string='Side Effects')
    vetution_presentation = fields.Text(string='Presentation')
    vetution_storage = fields.Text(string='Storage Requirements')
    vetution_contraindications = fields.Text(string='Contraindications')
    vetution_warnings = fields.Text(string='Warnings')
    vetution_interactions = fields.Text(string='Interactions')
    vetution_overdose = fields.Text(string='Overdose Information')
    vetution_policy_ordering_shipping = fields.Text(string='Ordering & Shipping Policy')
    vetution_delivery = fields.Text(string='Delivery Information')
    vetution_return = fields.Text(string='Return Policy')

    # Contact
    vetution_whatsapp_contact = fields.Char(string='WhatsApp Contact')

    # Tracking
    vetution_first_seen = fields.Datetime(string='First Seen')
    vetution_last_updated = fields.Datetime(string='Last Updated')
    vetution_last_price_update = fields.Datetime(string='Last Price Update')
    vetution_last_vendor_price_update = fields.Datetime(string='Last Vendor Price Update')

    # Computed fields
    vetution_has_vendor_prices = fields.Boolean(
        string='Has Vendor Prices',
        compute='_compute_has_vendor_prices',
        store=True
    )
    vetution_available_vendors = fields.Integer(
        string='Available Vendors',
        compute='_compute_available_vendors',
        store=True
    )

    @api.depends('vetution_vendor_price_ids')
    def _compute_has_vendor_prices(self):
        for record in self:
            record.vetution_has_vendor_prices = bool(record.vetution_vendor_price_ids)

    @api.depends('vetution_vendor_price_ids', 'vetution_vendor_price_ids.available')
    def _compute_available_vendors(self):
        for record in self:
            record.vetution_available_vendors = len(
                record.vetution_vendor_price_ids.filtered(lambda vp: vp.available)
            )

    def action_open_vetution_link(self):
        """Open product link in browser"""
        self.ensure_one()
        if self.vetution_link:
            return {
                'type': 'ir.actions.act_url',
                'url': self.vetution_link,
                'target': 'new',
            }
        return False

    def update_from_scraped_data(self, scraped_data):
        """Update product from scraped data dictionary"""
        self.ensure_one()
        
        # Basic fields
        if 'link' in scraped_data:
            self.vetution_link = scraped_data['link']
        if 'brand' in scraped_data:
            self.vetution_brand = scraped_data['brand']
        if 'brand_link' in scraped_data:
            self.vetution_brand_link = scraped_data['brand_link']
        if 'image_url' in scraped_data:
            self.vetution_image_url = scraped_data['image_url']
        if 'review_count' in scraped_data:
            self.vetution_review_count = scraped_data['review_count']
        if 'total_reviews' in scraped_data:
            self.vetution_total_reviews = scraped_data['total_reviews']
        if 'rating' in scraped_data:
            self.vetution_rating = scraped_data['rating']
        
        # List fields (convert to comma-separated)
        if 'ingredients' in scraped_data and isinstance(scraped_data['ingredients'], list):
            self.vetution_ingredients = ', '.join(scraped_data['ingredients'])
        if 'sizes' in scraped_data and isinstance(scraped_data['sizes'], list):
            self.vetution_sizes = ', '.join(scraped_data['sizes'])
        if 'tags' in scraped_data and isinstance(scraped_data['tags'], list):
            self.vetution_tags = ', '.join(scraped_data['tags'])
        if 'species' in scraped_data and isinstance(scraped_data['species'], list):
            self.vetution_species = ', '.join(scraped_data['species'])
        
        # Boolean fields
        if 'express_delivery' in scraped_data:
            self.vetution_express_delivery = scraped_data['express_delivery']
        if 'cold_chain' in scraped_data:
            self.vetution_cold_chain = scraped_data['cold_chain']
        
        # Price fields
        if 'price' in scraped_data:
            self.vetution_price = scraped_data['price']
        if 'currency' in scraped_data:
            self.vetution_currency = scraped_data['currency']
        if 'min_price' in scraped_data:
            self.vetution_min_price = scraped_data['min_price']
        if 'max_price' in scraped_data:
            self.vetution_max_price = scraped_data['max_price']
        
        # Vendor prices
        if 'vendor_prices' in scraped_data and scraped_data['vendor_prices']:
            # Clear existing vendor prices
            self.vetution_vendor_price_ids.unlink()
            # Create new ones
            for vp_data in scraped_data['vendor_prices']:
                self.env['vetution.vendor.price'].create({
                    'product_id': self.id,
                    'price': vp_data.get('price', 0),
                    'currency': vp_data.get('currency', 'EGP'),
                    'expiration_date': vp_data.get('expiration_date'),
                    'available': vp_data.get('available', True),
                    'vendor_name': vp_data.get('vendor_name', ''),
                })
        
        # Detailed sections
        if 'detailed_sections' in scraped_data:
            sections = scraped_data['detailed_sections']
            field_mapping = {
                'composition': 'vetution_composition',
                'indications': 'vetution_indications',
                'dose_and_administration': 'vetution_dose_administration',
                'precautions': 'vetution_precautions',
                'pregnancy': 'vetution_pregnancy',
                'side_effects': 'vetution_side_effects',
                'presentation': 'vetution_presentation',
                'storage': 'vetution_storage',
                'contraindications': 'vetution_contraindications',
                'warnings': 'vetution_warnings',
                'interactions': 'vetution_interactions',
                'overdose': 'vetution_overdose',
                'policy_of_ordering_shipping': 'vetution_policy_ordering_shipping',
                'delivery': 'vetution_delivery',
                'return': 'vetution_return',
            }
            for key, field_name in field_mapping.items():
                if key in sections:
                    setattr(self, field_name, sections[key])
        
        # Contact
        if 'whatsapp_contact' in scraped_data:
            self.vetution_whatsapp_contact = scraped_data['whatsapp_contact']
        
        # Update timestamps
        from datetime import datetime
        self.vetution_last_updated = datetime.now()
        if 'price' in scraped_data or 'vendor_prices' in scraped_data:
            self.vetution_last_price_update = datetime.now()
        if 'vendor_prices' in scraped_data:
            self.vetution_last_vendor_price_update = datetime.now()
        
        return True

