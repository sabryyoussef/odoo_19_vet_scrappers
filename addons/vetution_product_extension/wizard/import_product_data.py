# -*- coding: utf-8 -*-

import json
import csv
import base64
import io
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class ImportProductDataWizard(models.TransientModel):
    """Wizard to import product data from JSON or CSV files"""
    _name = 'vetution.import.product.data'
    _description = 'Import Product Data Wizard'

    file_data = fields.Binary(
        string='File',
        required=True,
        help='Upload JSON or CSV file with product data'
    )
    file_name = fields.Char(
        string='File Name',
        help='Name of the uploaded file'
    )
    file_type = fields.Selection(
        [
            ('json', 'JSON'),
            ('csv', 'CSV'),
        ],
        string='File Type',
        default='json',
        required=True
    )
    import_mode = fields.Selection(
        [
            ('create', 'Create New Products'),
            ('update', 'Update Existing Products'),
            ('both', 'Create or Update'),
        ],
        string='Import Mode',
        default='both',
        required=True,
        help='Create new products, update existing, or both'
    )
    match_by = fields.Selection(
        [
            ('name', 'Product Name'),
            ('barcode', 'Barcode'),
            ('vetution_link', 'Vetution Link'),
        ],
        string='Match By',
        default='vetution_link',
        required=True,
        help='Field to use for matching existing products'
    )
    skip_duplicates = fields.Boolean(
        string='Skip Duplicates',
        default=True,
        help='Skip products that already exist (when match_by finds a match)'
    )
    log_message = fields.Text(
        string='Import Log',
        readonly=True,
        help='Log of import operations'
    )
    import_result = fields.Text(
        string='Import Result',
        readonly=True
    )

    def _parse_json_file(self, file_content):
        """Parse JSON file content"""
        try:
            if isinstance(file_content, bytes):
                file_content = file_content.decode('utf-8')
            data = json.loads(file_content)
            
            # Handle both single object and array of objects
            if isinstance(data, dict):
                return [data]
            elif isinstance(data, list):
                return data
            else:
                raise UserError(_('Invalid JSON format. Expected object or array of objects.'))
        except json.JSONDecodeError as e:
            raise UserError(_('Invalid JSON file: %s') % str(e))

    def _parse_csv_file(self, file_content):
        """Parse CSV file content"""
        try:
            if isinstance(file_content, bytes):
                file_content = file_content.decode('utf-8')
            
            csv_reader = csv.DictReader(io.StringIO(file_content))
            products = []
            for row in csv_reader:
                # Convert string values to appropriate types
                product = {}
                for key, value in row.items():
                    if not value or value.strip() == '':
                        continue
                    # Try to parse as JSON for list/dict fields
                    if key in ['ingredients', 'sizes', 'tags', 'species', 'vendor_prices', 'detailed_sections']:
                        try:
                            product[key] = json.loads(value)
                        except (json.JSONDecodeError, ValueError):
                            # If not JSON, treat as comma-separated string
                            product[key] = value.split(',') if ',' in value else [value]
                    elif key in ['express_delivery', 'cold_chain', 'available']:
                        product[key] = value.lower() in ('true', '1', 'yes', 'y')
                    elif key in ['review_count', 'total_reviews']:
                        try:
                            product[key] = int(value)
                        except ValueError:
                            product[key] = 0
                    elif key in ['price', 'min_price', 'max_price', 'rating']:
                        try:
                            product[key] = float(value)
                        except ValueError:
                            product[key] = 0.0
                    elif key == 'expiration_date':
                        try:
                            product[key] = datetime.strptime(value, '%Y-%m-%d').date()
                        except ValueError:
                            pass
                    else:
                        product[key] = value
                products.append(product)
            return products
        except Exception as e:
            raise UserError(_('Error parsing CSV file: %s') % str(e))

    def _convert_list_to_text(self, value):
        """Convert list to comma-separated string"""
        if isinstance(value, list):
            return ', '.join(str(item) for item in value if item)
        elif isinstance(value, str):
            return value
        return ''

    def _find_product(self, product_data):
        """Find existing product based on match_by field with improved duplicate detection"""
        ProductTemplate = self.env['product.template']
        ProductProduct = self.env['product.product']
        
        # Normalize link for comparison
        link = product_data.get('link', '').strip() if product_data.get('link') else ''
        name = product_data.get('name', '').strip() if product_data.get('name') else ''
        
        # First, try exact match by vetution_link (most reliable)
        if link:
            product = ProductProduct.search([
                ('vetution_link', '=', link)
            ], limit=1)
            if product:
                return product
        
        # Then try by name (exact match)
        if name:
            template = ProductTemplate.search([
                ('name', '=', name)
            ], limit=1)
            if template:
                return template.product_variant_id
        
        # Try barcode if available
        if product_data.get('barcode'):
            product = ProductProduct.search([
                ('barcode', '=', product_data['barcode'])
            ], limit=1)
            if product:
                return product
        
        # Try fuzzy name matching (case-insensitive, trimmed)
        if name:
            # Search for similar names (case-insensitive)
            products = ProductProduct.search([
                ('name', 'ilike', name)
            ])
            # Find exact match after normalization
            for product in products:
                if product.name.strip().lower() == name.lower():
                    return product
        
        return ProductProduct.browse()

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

    def _map_product_data(self, product_data):
        """Map scraped data to Odoo product fields"""
        mapped_data = {}
        
        # Direct mappings
        field_mappings = {
            'link': 'vetution_link',
            'brand': 'vetution_brand',
            'brand_link': 'vetution_brand_link',
            'image_url': 'vetution_image_url',
            'review_count': 'vetution_review_count',
            'total_reviews': 'vetution_total_reviews',
            'rating': 'vetution_rating',
            'price': 'vetution_price',
            'currency': 'vetution_currency',
            'min_price': 'vetution_min_price',
            'max_price': 'vetution_max_price',
            'express_delivery': 'vetution_express_delivery',
            'cold_chain': 'vetution_cold_chain',
            'whatsapp_contact': 'vetution_whatsapp_contact',
        }
        
        for source_key, target_field in field_mappings.items():
            if source_key in product_data:
                value = product_data[source_key]
                # Normalize URL fields
                if source_key in ['link', 'brand_link', 'image_url', 'whatsapp_contact']:
                    value = self._normalize_url(value)
                mapped_data[target_field] = value
        
        # List to text mappings
        list_fields = {
            'ingredients': 'vetution_ingredients',
            'sizes': 'vetution_sizes',
            'tags': 'vetution_tags',
            'species': 'vetution_species',
        }
        
        for source_key, target_field in list_fields.items():
            if source_key in product_data:
                mapped_data[target_field] = self._convert_list_to_text(product_data[source_key])
        
        # Dictionary to field mappings (detailed_sections)
        if 'detailed_sections' in product_data and isinstance(product_data['detailed_sections'], dict):
            detailed_mappings = {
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
            
            for source_key, target_field in detailed_mappings.items():
                value = product_data['detailed_sections'].get(source_key, '')
                if value:
                    mapped_data[target_field] = value
        
        return mapped_data

    def _create_vendor_prices(self, product, vendor_prices_data):
        """Create vendor price records"""
        VendorPrice = self.env['vetution.vendor.price']
        
        # Clear existing vendor prices if updating
        if product.vetution_vendor_price_ids:
            product.vetution_vendor_price_ids.unlink()
        
        created_prices = []
        for vp_data in vendor_prices_data:
            if isinstance(vp_data, dict):
                price = vp_data.get('price', 0.0)
                if price > 0:  # Only create if price is valid
                    created_prices.append(VendorPrice.create({
                        'product_id': product.id,
                        'price': price,
                        'currency': vp_data.get('currency', 'EGP'),
                        'expiration_date': vp_data.get('expiration_date'),
                        'available': vp_data.get('available', True),
                        'vendor_name': vp_data.get('vendor_name', ''),
                    }))
        
        # Trigger recomputation of average price
        if created_prices:
            product._compute_vetution_average_price()

    def _import_product(self, product_data):
        """Import a single product"""
        ProductTemplate = self.env['product.template']
        ProductProduct = self.env['product.product']
        
        # Find existing product by template or variant
        existing_product = self._find_product(product_data)
        existing_template = None
        
        if existing_product:
            existing_template = existing_product.product_tmpl_id
        elif self.match_by == 'vetution_link' and product_data.get('link'):
            # Try to find by template's variant
            existing_template = ProductTemplate.search([
                ('product_variant_ids.vetution_link', '=', product_data['link'])
            ], limit=1)
        elif self.match_by == 'name' and product_data.get('name'):
            existing_template = ProductTemplate.search([
                ('name', '=', product_data['name'])
            ], limit=1)
        
        # Handle skip duplicates
        if existing_template and self.skip_duplicates and self.import_mode == 'create':
            return {'status': 'skipped', 'product': existing_template.product_variant_id, 'message': 'Duplicate skipped'}
        
        # Map data - separate template fields from variant fields
        mapped_data = self._map_product_data(product_data)
        variant_data = {}
        template_data = {}
        
        # Separate fields: template fields vs variant (vetution) fields
        vetution_fields = [
            'vetution_link', 'vetution_brand', 'vetution_brand_link', 'vetution_image_url',
            'vetution_review_count', 'vetution_total_reviews', 'vetution_rating',
            'vetution_ingredients', 'vetution_sizes', 'vetution_tags', 'vetution_species',
            'vetution_express_delivery', 'vetution_cold_chain',
            'vetution_price', 'vetution_currency', 'vetution_min_price', 'vetution_max_price',
            'vetution_composition', 'vetution_indications', 'vetution_dose_administration',
            'vetution_precautions', 'vetution_pregnancy', 'vetution_side_effects',
            'vetution_presentation', 'vetution_storage', 'vetution_contraindications',
            'vetution_warnings', 'vetution_interactions', 'vetution_overdose',
            'vetution_policy_ordering_shipping', 'vetution_delivery', 'vetution_return',
            'vetution_whatsapp_contact'
        ]
        
        # Split data into template and variant
        for key, value in mapped_data.items():
            if key in vetution_fields:
                variant_data[key] = value
            else:
                template_data[key] = value
        
        # Set product name on template
        if 'name' in product_data:
            template_data['name'] = product_data['name']
        
        # Create or update product template
        if existing_template and self.import_mode in ('update', 'both'):
            existing_template.write(template_data)
            product = existing_template.product_variant_id
            # Write variant fields to the product variant
            if variant_data:
                product.write(variant_data)
            # Assign Vetution tag
            product._assign_vetution_tag()
            status = 'updated'
        elif self.import_mode in ('create', 'both'):
            # Set default type if not set (for product.template)
            # Valid values: 'consu' (consumable), 'service', 'product' (storable)
            if 'type' not in template_data:
                template_data['type'] = 'consu'  # consumable is the default in Odoo 19
            # Also set sale_ok and purchase_ok if not set
            if 'sale_ok' not in template_data:
                template_data['sale_ok'] = True
            if 'purchase_ok' not in template_data:
                template_data['purchase_ok'] = True
            template = ProductTemplate.create(template_data)
            product = template.product_variant_id
            # Write variant fields to the product variant
            if variant_data:
                product.write(variant_data)
            # Assign Vetution tag
            product._assign_vetution_tag()
            status = 'created'
        else:
            return {'status': 'skipped', 'message': 'No matching product found and create mode disabled'}
        
        # Handle vendor prices (on the variant)
        vendor_prices_data = product_data.get('vendor_prices') or product_data.get('all_prices')
        if vendor_prices_data:
            self._create_vendor_prices(product, vendor_prices_data)
        
        # Trigger recomputation of average price and cost update
        product._compute_vetution_average_price()
        
        return {'status': status, 'product': product, 'message': f'Product {status} successfully'}

    def action_import(self):
        """Main import action"""
        if not self.file_data:
            raise UserError(_('Please upload a file to import.'))
        
        # Decode file content
        file_content = base64.b64decode(self.file_data)
        
        # Parse file based on type
        if self.file_type == 'json':
            products_data = self._parse_json_file(file_content)
        else:
            products_data = self._parse_csv_file(file_content)
        
        if not products_data:
            raise UserError(_('No products found in the file.'))
        
        # Import products
        results = {
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0,
            'messages': []
        }
        
        for idx, product_data in enumerate(products_data, 1):
            try:
                result = self._import_product(product_data)
                status = result['status']
                results[status] = results.get(status, 0) + 1
                product_name = product_data.get('name', f'Product #{idx}')
                results['messages'].append(f"{idx}. {product_name}: {result.get('message', status)}")
                _logger.info(f"Imported product {idx}: {result}")
            except Exception as e:
                results['errors'] += 1
                error_msg = f"Error importing product {idx}: {str(e)}"
                results['messages'].append(error_msg)
                _logger.error(error_msg, exc_info=True)
        
        # Build result message
        result_text = f"""
Import Completed:
- Created: {results['created']}
- Updated: {results['updated']}
- Skipped: {results['skipped']}
- Errors: {results['errors']}

Details:
{chr(10).join(results['messages'])}
        """
        
        self.write({
            'log_message': result_text,
            'import_result': f"Created: {results['created']}, Updated: {results['updated']}, Skipped: {results['skipped']}, Errors: {results['errors']}"
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'vetution.import.product.data',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

