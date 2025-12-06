# -*- coding: utf-8 -*-

from odoo import models, fields, api
from urllib.parse import quote
import logging
import base64

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    """Extend product.product with veterinary product data fields"""
    _inherit = 'product.product'

    # Basic Information
    vetution_link = fields.Char(
        string='Vetution Link',
        help='Product URL from source website'
    )
    vetution_link_computed = fields.Char(
        string='Vetution Link (Clickable)',
        compute='_compute_vetution_link',
        readonly=True,
        help='Computed clickable link - uses stored link or generates from product name'
    )
    def action_open_vetution_link(self):
        """Open Vetution link in browser"""
        self.ensure_one()
        if self.vetution_link_computed:
            return {
                'type': 'ir.actions.act_url',
                'url': self.vetution_link_computed,
                'target': 'new',
            }
        return False
    
    @api.depends('vetution_link', 'name')
    def _compute_vetution_link(self):
        """Compute clickable Vetution link"""
        for record in self:
            if record.vetution_link:
                # If link is already a full query URL, use it
                if '?keywords=' in record.vetution_link or record.vetution_link.startswith('https://www.vetution.com/products?'):
                    record.vetution_link_computed = record._normalize_url(record.vetution_link)
                # If link is a slug, convert to query parameter format
                elif record.name:
                    # Extract product name from slug or use stored name
                    product_name = record.name
                    # URL encode the product name
                    encoded_name = quote(product_name)
                    record.vetution_link_computed = f'https://www.vetution.com/products?keywords={encoded_name}'
                else:
                    record.vetution_link_computed = record._normalize_url(record.vetution_link)
            elif record.name:
                # Generate URL from product name if no link stored
                encoded_name = quote(record.name)
                record.vetution_link_computed = f'https://www.vetution.com/products?keywords={encoded_name}'
            else:
                record.vetution_link_computed = False
    
    @api.model
    def _normalize_url(self, url):
        """Normalize URL to ensure it's a complete, clickable URL"""
        if not url:
            return url
        url = str(url).strip()
        # If URL doesn't start with http:// or https://, add https://
        if url and not url.startswith(('http://', 'https://')):
            # If it starts with //, add https:
            if url.startswith('//'):
                url = 'https:' + url
            # If it starts with www., add https://
            elif url.startswith('www.'):
                url = 'https://' + url
            # If it's a relative path, add the base domain
            elif url.startswith('/'):
                url = 'https://www.vetution.com' + url
            # Otherwise, assume it's a domain and add https://
            else:
                url = 'https://' + url
        return url
    
    @api.model_create_multi
    def create(self, vals_list):
        """Normalize URLs before creating"""
        for vals in vals_list:
            if 'vetution_link' in vals:
                vals['vetution_link'] = self._normalize_url(vals.get('vetution_link'))
            if 'vetution_brand_link' in vals:
                vals['vetution_brand_link'] = self._normalize_url(vals.get('vetution_brand_link'))
            if 'vetution_image_url' in vals:
                vals['vetution_image_url'] = self._normalize_url(vals.get('vetution_image_url'))
            if 'vetution_whatsapp_contact' in vals:
                vals['vetution_whatsapp_contact'] = self._normalize_url(vals.get('vetution_whatsapp_contact'))
        return super().create(vals_list)
    
    def write(self, vals):
        """Normalize URLs before writing"""
        if 'vetution_link' in vals:
            vals['vetution_link'] = self._normalize_url(vals.get('vetution_link'))
        if 'vetution_brand_link' in vals:
            vals['vetution_brand_link'] = self._normalize_url(vals.get('vetution_brand_link'))
        if 'vetution_image_url' in vals:
            vals['vetution_image_url'] = self._normalize_url(vals.get('vetution_image_url'))
        if 'vetution_whatsapp_contact' in vals:
            vals['vetution_whatsapp_contact'] = self._normalize_url(vals.get('vetution_whatsapp_contact'))
        
        result = super().write(vals)
        
        # Auto-update product image if vetution_image_url is set
        if 'vetution_image_url' in vals and vals.get('vetution_image_url'):
            self._update_product_image_from_url()
        
        return result
    
    def _update_product_image_from_url(self):
        """Download image from vetution_image_url and set it as product image"""
        for record in self:
            if not record.vetution_image_url:
                continue
            
            try:
                # Try to import requests, fallback to urllib if not available
                try:
                    import requests
                    # Download the image
                    response = requests.get(record.vetution_image_url, timeout=10, stream=True)
                    response.raise_for_status()
                    
                    # Check if it's an image
                    content_type = response.headers.get('content-type', '')
                    if not content_type.startswith('image/'):
                        _logger.warning(f"URL {record.vetution_image_url} is not an image (content-type: {content_type})")
                        continue
                    
                    # Read image data
                    image_data = response.content
                except ImportError:
                    # Fallback to urllib if requests is not available
                    from urllib.request import urlopen
                    from urllib.error import URLError
                    try:
                        with urlopen(record.vetution_image_url, timeout=10) as response:
                            image_data = response.read()
                    except URLError as e:
                        _logger.error(f"Error downloading image from {record.vetution_image_url}: {str(e)}")
                        continue
                
                # Encode to base64
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                
                # Update product template image
                if record.product_tmpl_id:
                    record.product_tmpl_id.write({
                        'image_1920': image_base64
                    })
                    _logger.info(f"Updated product image for {record.name} from {record.vetution_image_url}")
                
            except Exception as e:
                _logger.error(f"Error processing image for {record.name}: {str(e)}", exc_info=True)
    
    def action_update_image_from_url(self):
        """Action to manually update product image from vetution_image_url"""
        self.ensure_one()
        if not self.vetution_image_url:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Image URL',
                    'message': 'Please set the Vetution Image URL first.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        self._update_product_image_from_url()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Image Updated',
                'message': 'Product image has been updated from the Vetution Image URL.',
                'type': 'success',
                'sticky': False,
            }
        }
    vetution_brand = fields.Char(
        string='Brand',
        help='Brand name'
    )
    vetution_brand_link = fields.Char(
        string='Brand Link',
        help='Brand URL'
    )
    vetution_image_url = fields.Char(
        string='Image URL',
        help='External product image URL'
    )
    vetution_review_count = fields.Integer(
        string='Review Count',
        default=0,
        help='Number of reviews'
    )
    vetution_total_reviews = fields.Integer(
        string='Total Reviews',
        default=0,
        help='Total review count from detail page'
    )
    vetution_rating = fields.Float(
        string='Rating',
        digits=(2, 1),
        help='Product rating (0-5)'
    )

    # Product Attributes
    vetution_ingredients = fields.Text(
        string='Ingredients',
        help='List of active ingredients (comma-separated or JSON)'
    )
    vetution_sizes = fields.Text(
        string='Sizes',
        help='Available product sizes/variants (comma-separated or JSON)'
    )
    vetution_tags = fields.Text(
        string='Tags',
        help='Product tags (comma-separated or JSON)'
    )
    vetution_species = fields.Text(
        string='Species',
        help='Target species (Canine, Feline, Equine, Bovine, etc.) - comma-separated or JSON'
    )

    # Delivery & Storage
    vetution_express_delivery = fields.Boolean(
        string='Express Delivery',
        default=False,
        help='Express delivery available'
    )
    vetution_cold_chain = fields.Boolean(
        string='Cold Chain',
        default=False,
        help='Requires cold chain storage'
    )

    # Pricing
    vetution_price = fields.Float(
        string='Vetution Price',
        digits='Product Price',
        help='Primary price from source'
    )
    vetution_currency = fields.Char(
        string='Currency',
        default='EGP',
        size=3,
        help='Currency code (default: EGP)'
    )
    vetution_min_price = fields.Float(
        string='Min Price',
        digits='Product Price',
        help='Minimum price across all vendors'
    )
    vetution_max_price = fields.Float(
        string='Max Price',
        digits='Product Price',
        help='Maximum price across all vendors'
    )
    vetution_vendor_price_ids = fields.One2many(
        'vetution.vendor.price',
        'product_id',
        string='Vendor Prices',
        help='Multiple vendor prices for this product'
    )
    vetution_average_price = fields.Float(
        string='Average Vetution Price',
        compute='_compute_vetution_average_price',
        store=True,
        digits='Product Price',
        help='Average price from all vendor prices'
    )
    is_vetution_product = fields.Boolean(
        string='Is Vetution Product',
        compute='_compute_is_vetution_product',
        store=True,
        help='Indicates if this is a Vetution product'
    )
    
    @api.depends('vetution_vendor_price_ids.price', 'vetution_vendor_price_ids.available', 'vetution_price')
    def _compute_vetution_average_price(self):
        """Compute average price from vendor prices and update cost price"""
        for record in self:
            prices = []
            # Add vendor prices (only available ones)
            if record.vetution_vendor_price_ids:
                prices.extend([vp.price for vp in record.vetution_vendor_price_ids 
                              if vp.price > 0 and vp.available])
            # Add main vetution price if available
            if record.vetution_price and record.vetution_price > 0:
                prices.append(record.vetution_price)
            
            if prices:
                record.vetution_average_price = sum(prices) / len(prices)
                # Update standard_price (cost price) with average
                if record.product_tmpl_id and record.vetution_average_price > 0:
                    record.product_tmpl_id.standard_price = record.vetution_average_price
            else:
                record.vetution_average_price = 0.0
    
    @api.depends('vetution_link', 'vetution_brand', 'vetution_price')
    def _compute_is_vetution_product(self):
        """Compute if this is a Vetution product"""
        for record in self:
            record.is_vetution_product = bool(
                record.vetution_link or 
                record.vetution_brand or 
                record.vetution_price > 0
            )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Normalize URLs before creating and assign Vetution tag"""
        result = super().create(vals_list)
        result._assign_vetution_tag()
        return result
    
    def write(self, vals):
        """Normalize URLs before writing and update tag if needed"""
        result = super().write(vals)
        if 'vetution_link' in vals or 'vetution_brand' in vals or 'vetution_price' in vals:
            self._assign_vetution_tag()
        return result
    
    def _assign_vetution_tag(self):
        """Assign 'Vetution' product tag to products with Vetution data"""
        for record in self:
            if record.is_vetution_product and record.product_tmpl_id:
                # Get or create Vetution tag (Odoo 19 uses product.tag directly)
                tag = self.env['product.tag'].search([('name', '=', 'Vetution')], limit=1)
                
                if not tag:
                    tag = self.env['product.tag'].create({
                        'name': 'Vetution',
                        'color': 1,  # Blue color
                    })
                
                # Add tag to product template if not already present
                if tag.id not in record.product_tmpl_id.product_tag_ids.ids:
                    record.product_tmpl_id.product_tag_ids = [(4, tag.id)]

    # Detailed Information
    vetution_composition = fields.Text(
        string='Composition',
        help='Product composition details'
    )
    vetution_indications = fields.Text(
        string='Indications',
        help='Product indications'
    )
    vetution_dose_administration = fields.Text(
        string='Dose & Administration',
        help='Dose and administration instructions'
    )
    vetution_precautions = fields.Text(
        string='Precautions',
        help='Precautions information'
    )
    vetution_pregnancy = fields.Text(
        string='Pregnancy',
        help='Pregnancy-related information'
    )
    vetution_side_effects = fields.Text(
        string='Side Effects',
        help='Side effects information'
    )
    vetution_presentation = fields.Text(
        string='Presentation',
        help='Product presentation details'
    )
    vetution_storage = fields.Text(
        string='Storage',
        help='Storage requirements'
    )
    vetution_contraindications = fields.Text(
        string='Contraindications',
        help='Contraindications'
    )
    vetution_warnings = fields.Text(
        string='Warnings',
        help='Warnings'
    )
    vetution_interactions = fields.Text(
        string='Interactions',
        help='Drug interactions'
    )
    vetution_overdose = fields.Text(
        string='Overdose',
        help='Overdose information'
    )
    vetution_policy_ordering_shipping = fields.Text(
        string='Ordering & Shipping Policy',
        help='Ordering and shipping policy'
    )
    vetution_delivery = fields.Text(
        string='Delivery',
        help='Delivery information'
    )
    vetution_return = fields.Text(
        string='Return Policy',
        help='Return policy'
    )

    # Contact
    vetution_whatsapp_contact = fields.Char(
        string='WhatsApp Contact',
        help='WhatsApp contact link'
    )

    @api.constrains('vetution_rating')
    def _check_rating(self):
        """Ensure rating is between 0 and 5"""
        for record in self:
            if record.vetution_rating and (record.vetution_rating < 0 or record.vetution_rating > 5):
                raise models.ValidationError('Rating must be between 0 and 5.')

    @api.model
    def _convert_list_to_text(self, value):
        """Convert list to comma-separated string"""
        if isinstance(value, list):
            return ', '.join(str(item) for item in value if item)
        elif isinstance(value, str):
            return value
        return ''

    @api.model
    def _convert_dict_value(self, data_dict, key):
        """Safely get value from dictionary"""
        if isinstance(data_dict, dict):
            return data_dict.get(key, '') or ''
        return ''

