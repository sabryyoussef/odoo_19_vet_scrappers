# -*- coding: utf-8 -*-

import json
import csv
import base64
import io
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class AminPetshopImportWizard(models.TransientModel):
    _name = 'amin.petshop.import.wizard'
    _description = 'Amin Petshop Import Wizard'

    import_type = fields.Selection([
        ('json', 'JSON File'),
        ('csv', 'CSV File'),
    ], string='Import Type', required=True, default='json')

    data_file = fields.Binary(string='Data File', required=True)
    filename = fields.Char(string='Filename')

    match_by = fields.Selection([
        ('link', 'Amin Petshop Link'),
        ('sku', 'SKU'),
        ('name', 'Product Name'),
    ], string='Match Products By', default='link', required=True)

    create_new = fields.Boolean(string='Create New Products', default=True)
    update_existing = fields.Boolean(string='Update Existing Products', default=True)

    # Results
    products_found = fields.Integer(string='Products Found', readonly=True)
    products_created = fields.Integer(string='Products Created', readonly=True)
    products_updated = fields.Integer(string='Products Updated', readonly=True)
    errors = fields.Integer(string='Errors', readonly=True)
    log_message = fields.Text(string='Import Log', readonly=True)

    def _parse_json_file(self, file_content):
        """Parse JSON file content"""
        try:
            data = json.loads(file_content.decode('utf-8'))
            # Handle both single object and array
            if isinstance(data, dict):
                return [data]
            elif isinstance(data, list):
                return data
            else:
                raise UserError(_('Invalid JSON format. Expected object or array.'))
        except json.JSONDecodeError as e:
            raise UserError(_('Invalid JSON file: %s') % str(e))

    def _parse_csv_file(self, file_content):
        """Parse CSV file content"""
        try:
            csv_content = file_content.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            products = []
            for row in csv_reader:
                product = {}
                for key, value in row.items():
                    if not value or value.strip() == '':
                        continue
                    # Try to parse as JSON for complex fields
                    if key in ['variants']:
                        try:
                            product[key] = json.loads(value)
                        except (json.JSONDecodeError, ValueError):
                            product[key] = value
                    elif key in ['price', 'regular_price']:
                        try:
                            product[key] = float(value)
                        except ValueError:
                            product[key] = 0.0
                    elif key in ['available']:
                        product[key] = value.lower() in ('true', '1', 'yes', 'y')
                    else:
                        product[key] = value
                products.append(product)
            return products
        except Exception as e:
            raise UserError(_('Error parsing CSV file: %s') % str(e))

    def _find_product(self, product_data):
        """Find existing product based on match_by field"""
        ProductProduct = self.env['product.product']
        ProductTemplate = self.env['product.template']

        if self.match_by == 'link' and product_data.get('link'):
            product = ProductProduct.search([
                ('amin_petshop_link', '=', product_data['link'])
            ], limit=1)
            if product:
                return product
        elif self.match_by == 'sku' and product_data.get('sku'):
            product = ProductProduct.search([
                ('amin_petshop_sku', '=', product_data['sku'])
            ], limit=1)
            if product:
                return product
        elif self.match_by == 'name' and product_data.get('name'):
            # Try exact match first
            template = ProductTemplate.search([
                ('name', '=', product_data['name'])
            ], limit=1)
            if template:
                return template.product_variant_id
            # Try fuzzy match (case-insensitive)
            products = ProductProduct.search([
                ('name', 'ilike', product_data['name'])
            ])
            for product in products:
                if product.name.strip().lower() == product_data['name'].strip().lower():
                    return product

        return ProductProduct.browse()

    def _import_product(self, product_data):
        """Import a single product"""
        ProductTemplate = self.env['product.template']
        ProductProduct = self.env['product.product']

        # Find existing product
        existing_product = self._find_product(product_data)

        # Handle create/update logic
        if existing_product:
            if not self.update_existing:
                return {'status': 'skipped', 'message': 'Product exists and update disabled'}
            # Update existing product
            existing_product.update_from_amin_petshop_data(product_data)
            # Update product name if provided
            if product_data.get('name') and existing_product.product_tmpl_id:
                existing_product.product_tmpl_id.name = product_data['name']
            return {'status': 'updated', 'product': existing_product}
        else:
            if not self.create_new:
                return {'status': 'skipped', 'message': 'Product not found and create disabled'}
            # Create new product
            template_vals = {
                'name': product_data.get('name', 'New Product'),
                'type': 'consu',
                'sale_ok': True,
                'purchase_ok': True,
            }
            template = ProductTemplate.create(template_vals)
            product = template.product_variant_id
            # Update with Amin Petshop data
            product.update_from_amin_petshop_data(product_data)
            return {'status': 'created', 'product': product}

    def action_import(self):
        """Import products from file"""
        self.ensure_one()

        if not self.data_file:
            raise UserError(_('Please select a file to import.'))

        # Decode file
        try:
            file_content = base64.b64decode(self.data_file)
        except Exception as e:
            raise UserError(_('Error decoding file: %s') % str(e))

        # Parse file
        if self.import_type == 'json':
            products_data = self._parse_json_file(file_content)
        else:
            products_data = self._parse_csv_file(file_content)

        if not products_data:
            raise UserError(_('No products found in file.'))

        # Initialize counters
        self.products_found = len(products_data)
        self.products_created = 0
        self.products_updated = 0
        self.errors = 0
        log_messages = []

        # Import products
        for idx, product_data in enumerate(products_data, 1):
            try:
                result = self._import_product(product_data)
                if result['status'] == 'created':
                    self.products_created += 1
                    log_messages.append(f"✓ Created: {product_data.get('name', 'Unknown')}")
                elif result['status'] == 'updated':
                    self.products_updated += 1
                    log_messages.append(f"✓ Updated: {product_data.get('name', 'Unknown')}")
                else:
                    log_messages.append(f"⊘ Skipped: {product_data.get('name', 'Unknown')} - {result.get('message', '')}")
            except Exception as e:
                self.errors += 1
                error_msg = f"✗ Error importing {product_data.get('name', 'Unknown')}: {str(e)}"
                log_messages.append(error_msg)
                _logger.error(error_msg, exc_info=True)

            # Log progress every 50 products
            if idx % 50 == 0:
                _logger.info(f"Processed {idx}/{len(products_data)} products")

        # Set log message
        self.log_message = '\n'.join(log_messages[:100])  # Limit to first 100 messages
        if len(log_messages) > 100:
            self.log_message += f"\n... and {len(log_messages) - 100} more entries"

        # Show result message
        message = _(
            'Import completed!\n'
            'Products Found: %d\n'
            'Products Created: %d\n'
            'Products Updated: %d\n'
            'Errors: %d'
        ) % (self.products_found, self.products_created, self.products_updated, self.errors)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Import Complete'),
                'message': message,
                'type': 'success' if self.errors == 0 else 'warning',
                'sticky': False,
            }
        }

