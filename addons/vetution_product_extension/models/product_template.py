# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    """Extend product.template with veterinary product data fields"""
    _inherit = 'product.template'

    # Basic Information
    vetution_link = fields.Char(
        string='Vetution Link',
        help='Product URL from source website',
        related='product_variant_ids.vetution_link',
        readonly=False
    )
    vetution_link_computed = fields.Char(
        string='Vetution Link (Clickable)',
        compute='_compute_vetution_link',
        help='Computed clickable link - uses stored link or generates from product name',
        related='product_variant_ids.vetution_link_computed',
        readonly=True
    )
    
    @api.depends('product_variant_ids.vetution_link', 'product_variant_ids.name', 'name')
    def _compute_vetution_link(self):
        """Compute clickable Vetution link from variant"""
        for record in self:
            if record.product_variant_ids:
                record.vetution_link_computed = record.product_variant_ids[0].vetution_link_computed
            else:
                record.vetution_link_computed = False
    
    def action_open_vetution_link(self):
        """Open Vetution link in browser"""
        self.ensure_one()
        variant = self.product_variant_ids[0] if self.product_variant_ids else False
        if variant and variant.vetution_link_computed:
            return {
                'type': 'ir.actions.act_url',
                'url': variant.vetution_link_computed,
                'target': 'new',
            }
        return False
    
    def action_update_image_from_url(self):
        """Action to update product image from vetution_image_url"""
        self.ensure_one()
        variant = self.product_variant_ids[0] if self.product_variant_ids else False
        if variant:
            return variant.action_update_image_from_url()
        return False
    vetution_brand = fields.Char(
        string='Brand',
        help='Brand name',
        related='product_variant_ids.vetution_brand',
        readonly=False
    )
    vetution_brand_link = fields.Char(
        string='Brand Link',
        help='Brand URL',
        related='product_variant_ids.vetution_brand_link',
        readonly=False
    )
    vetution_image_url = fields.Char(
        string='Image URL',
        help='External product image URL',
        related='product_variant_ids.vetution_image_url',
        readonly=False
    )
    vetution_review_count = fields.Integer(
        string='Review Count',
        default=0,
        help='Number of reviews',
        related='product_variant_ids.vetution_review_count',
        readonly=False
    )
    vetution_total_reviews = fields.Integer(
        string='Total Reviews',
        default=0,
        help='Total review count from detail page',
        related='product_variant_ids.vetution_total_reviews',
        readonly=False
    )
    vetution_rating = fields.Float(
        string='Rating',
        digits=(2, 1),
        help='Product rating (0-5)',
        related='product_variant_ids.vetution_rating',
        readonly=False
    )

    # Product Attributes
    vetution_ingredients = fields.Text(
        string='Ingredients',
        help='List of active ingredients (comma-separated or JSON)',
        related='product_variant_ids.vetution_ingredients',
        readonly=False
    )
    vetution_sizes = fields.Text(
        string='Sizes',
        help='Available product sizes/variants (comma-separated or JSON)',
        related='product_variant_ids.vetution_sizes',
        readonly=False
    )
    vetution_tags = fields.Text(
        string='Tags',
        help='Product tags (comma-separated or JSON)',
        related='product_variant_ids.vetution_tags',
        readonly=False
    )
    vetution_species = fields.Text(
        string='Species',
        help='Target species (Canine, Feline, Equine, Bovine, etc.) - comma-separated or JSON',
        related='product_variant_ids.vetution_species',
        readonly=False
    )

    # Delivery & Storage
    vetution_express_delivery = fields.Boolean(
        string='Express Delivery',
        default=False,
        help='Express delivery available',
        related='product_variant_ids.vetution_express_delivery',
        readonly=False
    )
    vetution_cold_chain = fields.Boolean(
        string='Cold Chain',
        default=False,
        help='Requires cold chain storage',
        related='product_variant_ids.vetution_cold_chain',
        readonly=False
    )

    # Pricing
    vetution_price = fields.Float(
        string='Vetution Price',
        digits='Product Price',
        help='Primary price from source',
        related='product_variant_ids.vetution_price',
        readonly=False
    )
    vetution_currency = fields.Char(
        string='Currency',
        default='EGP',
        size=3,
        help='Currency code (default: EGP)',
        related='product_variant_ids.vetution_currency',
        readonly=False
    )
    vetution_min_price = fields.Float(
        string='Min Price',
        digits='Product Price',
        help='Minimum price across all vendors',
        related='product_variant_ids.vetution_min_price',
        readonly=False
    )
    vetution_max_price = fields.Float(
        string='Max Price',
        digits='Product Price',
        help='Maximum price across all vendors',
        related='product_variant_ids.vetution_max_price',
        readonly=False
    )
    vetution_vendor_price_ids = fields.One2many(
        'vetution.vendor.price',
        'product_id',
        string='Vendor Prices',
        help='Multiple vendor prices for this product',
        compute='_compute_vendor_prices',
        inverse='_inverse_vendor_prices'
    )

    # Detailed Information
    vetution_composition = fields.Text(
        string='Composition',
        help='Product composition details',
        related='product_variant_ids.vetution_composition',
        readonly=False
    )
    vetution_indications = fields.Text(
        string='Indications',
        help='Product indications',
        related='product_variant_ids.vetution_indications',
        readonly=False
    )
    vetution_dose_administration = fields.Text(
        string='Dose & Administration',
        help='Dose and administration instructions',
        related='product_variant_ids.vetution_dose_administration',
        readonly=False
    )
    vetution_precautions = fields.Text(
        string='Precautions',
        help='Precautions information',
        related='product_variant_ids.vetution_precautions',
        readonly=False
    )
    vetution_pregnancy = fields.Text(
        string='Pregnancy',
        help='Pregnancy-related information',
        related='product_variant_ids.vetution_pregnancy',
        readonly=False
    )
    vetution_side_effects = fields.Text(
        string='Side Effects',
        help='Side effects information',
        related='product_variant_ids.vetution_side_effects',
        readonly=False
    )
    vetution_presentation = fields.Text(
        string='Presentation',
        help='Product presentation details',
        related='product_variant_ids.vetution_presentation',
        readonly=False
    )
    vetution_storage = fields.Text(
        string='Storage',
        help='Storage requirements',
        related='product_variant_ids.vetution_storage',
        readonly=False
    )
    vetution_contraindications = fields.Text(
        string='Contraindications',
        help='Contraindications',
        related='product_variant_ids.vetution_contraindications',
        readonly=False
    )
    vetution_warnings = fields.Text(
        string='Warnings',
        help='Warnings',
        related='product_variant_ids.vetution_warnings',
        readonly=False
    )
    vetution_interactions = fields.Text(
        string='Interactions',
        help='Drug interactions',
        related='product_variant_ids.vetution_interactions',
        readonly=False
    )
    vetution_overdose = fields.Text(
        string='Overdose',
        help='Overdose information',
        related='product_variant_ids.vetution_overdose',
        readonly=False
    )
    vetution_policy_ordering_shipping = fields.Text(
        string='Ordering & Shipping Policy',
        help='Ordering and shipping policy',
        related='product_variant_ids.vetution_policy_ordering_shipping',
        readonly=False
    )
    vetution_delivery = fields.Text(
        string='Delivery',
        help='Delivery information',
        related='product_variant_ids.vetution_delivery',
        readonly=False
    )
    vetution_return = fields.Text(
        string='Return Policy',
        help='Return policy',
        related='product_variant_ids.vetution_return',
        readonly=False
    )

    # Contact
    vetution_whatsapp_contact = fields.Char(
        string='WhatsApp Contact',
        help='WhatsApp contact link',
        related='product_variant_ids.vetution_whatsapp_contact',
        readonly=False
    )

    @api.depends('product_variant_ids.vetution_vendor_price_ids')
    def _compute_vendor_prices(self):
        """Compute vendor prices from first variant"""
        for template in self:
            if template.product_variant_ids:
                template.vetution_vendor_price_ids = template.product_variant_ids[0].vetution_vendor_price_ids
            else:
                template.vetution_vendor_price_ids = False

    def _inverse_vendor_prices(self):
        """Inverse vendor prices to first variant"""
        for template in self:
            if template.product_variant_ids:
                template.product_variant_ids[0].vetution_vendor_price_ids = template.vetution_vendor_price_ids

