# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import base64
import csv
import json
import io
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class UnifiedImportWizard(models.TransientModel):
    """
    Import Wizard for Product Data
    
    Multi-step wizard for importing products from CSV/JSON files.
    Supports smart duplicate detection and vendor price creation.
    """
    _name = 'unified.import.wizard'
    _description = 'Product Import Wizard'

    # Step 1: File Upload
    data_source_id = fields.Many2one(
        comodel_name='unified.data.source',
        string='Data Source',
        help='Select configured data source (optional)'
    )
    
    category_filter = fields.Char(
        string='Category Filter',
        help='Filter products by category ID (from category mapping)'
    )
    
    category_name = fields.Char(
        string='Category Name',
        help='Display name of filtered category'
    )
    
    file_data = fields.Binary(
        string='Import File',
        required=True,
        help='Upload CSV or JSON file'
    )
    
    file_name = fields.Char(
        string='File Name',
        help='Name of uploaded file'
    )
    
    file_type = fields.Selection(
        selection=[
            ('csv', 'CSV File'),
            ('json', 'JSON File'),
        ],
        string='File Type',
        compute='_compute_file_type',
        store=True,
        help='Detected file type based on extension'
    )
    
    # Step 2: Import Options
    source_system = fields.Selection(
        selection=[
            ('vetution', 'Vetution'),
            ('amin_petshop', 'Amin Petshop'),
            ('amazon', 'Amazon'),
            ('other', 'Other/Custom'),
        ],
        string='Source System',
        required=True,
        default='other',
        help='Which external system is this data from?'
    )
    
    match_strategy = fields.Selection(
        selection=[
            ('url', 'By External URL (Recommended)'),
            ('sku', 'By SKU/External ID'),
            ('name', 'By Product Name'),
            ('url_or_sku', 'By URL or SKU'),
            ('url_or_name', 'By URL or Name'),
        ],
        string='Match Strategy',
        default='url_or_sku',
        required=True,
        help='How to match existing products'
    )
    
    duplicate_action = fields.Selection(
        selection=[
            ('skip', 'Skip (Keep Existing)'),
            ('update', 'Update (Merge Data)'),
            ('create_new', 'Create New Product'),
            ('add_vendor', 'Add as Vendor Price'),
        ],
        string='If Product Exists',
        default='add_vendor',
        required=True,
        help='What to do when product already exists'
    )
    
    update_cost_price = fields.Boolean(
        string='Update Cost Price',
        default=True,
        help='Update product cost price with average/lowest vendor price'
    )
    
    cost_price_strategy = fields.Selection(
        selection=[
            ('lowest', 'Use Lowest Vendor Price'),
            ('average', 'Use Average Vendor Price'),
            ('first', 'Use First Source Price'),
            ('manual', 'Keep Manual Price'),
        ],
        string='Cost Price Strategy',
        default='lowest',
        help='How to calculate product cost price from vendor prices'
    )
    
    create_vendor_prices = fields.Boolean(
        string='Create Vendor Prices',
        default=True,
        help='Create vendor price records for each product'
    )
    
    # Step 3: Preview
    preview_data = fields.Text(
        string='Data Preview',
        readonly=True,
        help='Preview of first 10 records'
    )
    
    total_records = fields.Integer(
        string='Total Records',
        readonly=True,
        help='Total number of records in file'
    )
    
    # Step 4: Results
    state = fields.Selection(
        selection=[
            ('upload', 'Upload File'),
            ('configure', 'Configure Import'),
            ('preview', 'Preview Data'),
            ('import', 'Importing...'),
            ('done', 'Import Complete'),
        ],
        string='State',
        default='upload',
        required=True
    )
    
    products_created = fields.Integer(
        string='Products Created',
        readonly=True,
        default=0
    )
    
    products_updated = fields.Integer(
        string='Products Updated',
        readonly=True,
        default=0
    )
    
    products_skipped = fields.Integer(
        string='Products Skipped',
        readonly=True,
        default=0
    )
    
    products_failed = fields.Integer(
        string='Products Failed',
        readonly=True,
        default=0
    )
    
    vendor_prices_created = fields.Integer(
        string='Vendor Prices Created',
        readonly=True,
        default=0
    )
    
    import_log = fields.Text(
        string='Import Log',
        readonly=True,
        help='Detailed log of import process'
    )
    
    error_log = fields.Text(
        string='Error Log',
        readonly=True,
        help='Errors encountered during import'
    )
    
    import_history_id = fields.Many2one(
        comodel_name='unified.import.history',
        string='Import History',
        readonly=True,
        help='Link to import history record'
    )

    @api.depends('file_name')
    def _compute_file_type(self):
        """Detect file type from extension"""
        for wizard in self:
            if wizard.file_name:
                if wizard.file_name.lower().endswith('.csv'):
                    wizard.file_type = 'csv'
                elif wizard.file_name.lower().endswith('.json'):
                    wizard.file_type = 'json'
                else:
                    wizard.file_type = False
            else:
                wizard.file_type = False

    def action_next_step(self):
        """Move to next wizard step"""
        self.ensure_one()
        
        if self.state == 'upload':
            # Validate file
            if not self.file_data:
                raise UserError(_('Please upload a file.'))
            if not self.file_type:
                raise UserError(_('Unsupported file type. Please upload CSV or JSON file.'))
            
            # Parse and preview data
            self._parse_and_preview()
            self.state = 'configure'
            
        elif self.state == 'configure':
            # Validate configuration
            if not self.source_system:
                raise UserError(_('Please select a source system.'))
            
            self.state = 'preview'
            
        elif self.state == 'preview':
            # Start import
            self.state = 'import'
            self._execute_import()
            self.state = 'done'
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'unified.import.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_previous_step(self):
        """Move to previous wizard step"""
        self.ensure_one()
        
        if self.state == 'configure':
            self.state = 'upload'
        elif self.state == 'preview':
            self.state = 'configure'
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'unified.import.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_import(self):
        """Execute import directly (skip preview)"""
        self.ensure_one()
        
        if not self.file_data:
            raise UserError(_('Please upload a file.'))
        
        self.state = 'import'
        self._execute_import()
        self.state = 'done'
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'unified.import.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _parse_and_preview(self):
        """Parse file and generate preview"""
        self.ensure_one()
        
        try:
            if self.file_type == 'csv':
                records = self._parse_csv()
            elif self.file_type == 'json':
                records = self._parse_json()
            else:
                raise UserError(_('Unsupported file type'))
            
            self.total_records = len(records)
            
            # Generate preview (first 10 records)
            preview_records = records[:10]
            preview_text = f"Total Records: {len(records)}\n\n"
            preview_text += "First 10 Records:\n"
            preview_text += "=" * 80 + "\n\n"
            
            for i, record in enumerate(preview_records, 1):
                preview_text += f"Record {i}:\n"
                for key, value in record.items():
                    preview_text += f"  {key}: {value}\n"
                preview_text += "\n"
            
            self.preview_data = preview_text
            
        except Exception as e:
            _logger.error(f"Error parsing file: {e}")
            raise UserError(_('Error parsing file: %s') % str(e))

    def _parse_csv(self):
        """Parse CSV file"""
        self.ensure_one()
        
        # Decode file data
        file_content = base64.b64decode(self.file_data)
        
        # Try different encodings
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                text_content = file_content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise UserError(_('Unable to decode file. Please check file encoding.'))
        
        # Parse CSV
        csv_file = io.StringIO(text_content)
        reader = csv.DictReader(csv_file)
        
        records = []
        for row in reader:
            # Clean empty values
            cleaned_row = {k: v.strip() if v else '' for k, v in row.items()}
            records.append(cleaned_row)
        
        _logger.info(f"Parsed {len(records)} records from CSV")
        return records

    def _parse_json(self):
        """Parse JSON file"""
        self.ensure_one()
        
        # Decode file data
        file_content = base64.b64decode(self.file_data)
        text_content = file_content.decode('utf-8')
        
        # Parse JSON
        data = json.loads(text_content)
        
        # Handle different JSON structures
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict):
            # Try common keys for product lists
            if 'products' in data:
                records = data['products']
            elif 'items' in data:
                records = data['items']
            elif 'data' in data:
                records = data['data']
            else:
                # Assume single product
                records = [data]
        else:
            raise UserError(_('Invalid JSON structure'))
        
        _logger.info(f"Parsed {len(records)} records from JSON")
        return records

    def _execute_import(self):
        """Execute the import process"""
        self.ensure_one()
        
        start_time = datetime.now()
        log_lines = []
        error_lines = []
        
        try:
            # Parse data
            if self.file_type == 'csv':
                records = self._parse_csv()
            elif self.file_type == 'json':
                records = self._parse_json()
            else:
                raise UserError(_('Unsupported file type'))
            
            log_lines.append(f"Starting import of {len(records)} records...")
            log_lines.append(f"Source: {self.source_system}")
            log_lines.append(f"Match Strategy: {self.match_strategy}")
            log_lines.append(f"Duplicate Action: {self.duplicate_action}")
            if self.category_filter:
                log_lines.append(f"Category Filter: {self.category_name or self.category_filter}")
            log_lines.append("=" * 80)
            
            # Create import history
            history_vals = {
                'data_source_id': self.data_source_id.id if self.data_source_id else False,
                'import_date': fields.Datetime.now(),
                'user_id': self.env.user.id,
                'status': 'in_progress',
                'total_products': len(records),
            }
            import_history = self.env['unified.import.history'].create(history_vals)
            self.import_history_id = import_history
            
            # Process each record
            for i, record in enumerate(records, 1):
                try:
                    # Apply category filter if specified
                    if self.category_filter:
                        record_category = record.get('external_category_id') or record.get('category_id') or record.get('category')
                        if record_category and str(record_category) != str(self.category_filter):
                            self.products_skipped += 1
                            log_lines.append(f"\nRecord {i}: Skipped (category filter: {record_category} != {self.category_filter})")
                            continue
                    
                    log_lines.append(f"\nProcessing record {i}/{len(records)}...")
                    result = self._import_product(record)
                    
                    if result['action'] == 'created':
                        self.products_created += 1
                        log_lines.append(f"  ✓ Created: {result['product'].name}")
                    elif result['action'] == 'updated':
                        self.products_updated += 1
                        log_lines.append(f"  ✓ Updated: {result['product'].name}")
                    elif result['action'] == 'skipped':
                        self.products_skipped += 1
                        log_lines.append(f"  - Skipped: {result.get('reason', 'Already exists')}")
                    elif result['action'] == 'vendor_added':
                        self.products_updated += 1
                        self.vendor_prices_created += 1
                        log_lines.append(f"  ✓ Added vendor price: {result['product'].name}")
                    
                except Exception as e:
                    self.products_failed += 1
                    error_msg = f"Record {i}: {str(e)}"
                    error_lines.append(error_msg)
                    log_lines.append(f"  ✗ Failed: {str(e)}")
                    _logger.error(f"Import error on record {i}: {e}", exc_info=True)
            
            # Update import history
            duration = (datetime.now() - start_time).total_seconds()
            status = 'success' if self.products_failed == 0 else 'partial' if (self.products_created + self.products_updated) > 0 else 'failed'
            
            import_history.write({
                'status': status,
                'products_created': self.products_created,
                'products_updated': self.products_updated,
                'products_skipped': self.products_skipped,
                'products_failed': self.products_failed,
                'duration': duration,
                'import_log': '\n'.join(log_lines),
                'error_log': '\n'.join(error_lines) if error_lines else False,
            })
            
            # Final summary
            log_lines.append("\n" + "=" * 80)
            log_lines.append("IMPORT COMPLETE")
            log_lines.append(f"Duration: {duration:.2f} seconds")
            log_lines.append(f"Created: {self.products_created}")
            log_lines.append(f"Updated: {self.products_updated}")
            log_lines.append(f"Skipped: {self.products_skipped}")
            log_lines.append(f"Failed: {self.products_failed}")
            log_lines.append(f"Vendor Prices Created: {self.vendor_prices_created}")
            
            self.import_log = '\n'.join(log_lines)
            self.error_log = '\n'.join(error_lines) if error_lines else False
            
        except Exception as e:
            error_msg = f"Fatal import error: {str(e)}"
            error_lines.append(error_msg)
            log_lines.append(f"\n✗ FATAL ERROR: {str(e)}")
            
            self.import_log = '\n'.join(log_lines)
            self.error_log = '\n'.join(error_lines)
            
            if self.import_history_id:
                self.import_history_id.write({
                    'status': 'failed',
                    'error_log': '\n'.join(error_lines),
                })
            
            _logger.error(f"Fatal import error: {e}", exc_info=True)
            raise

    def _import_product(self, record):
        """
        Import single product record
        
        Returns dict with:
            - action: 'created', 'updated', 'skipped', 'vendor_added'
            - product: product.template record
            - reason: skip reason (if skipped)
        """
        Product = self.env['product.template']
        VendorPrice = self.env['unified.vendor.price']
        
        # Extract product data from record
        product_data = self._extract_product_data(record)
        vendor_price_data = self._extract_vendor_price_data(record)
        
        # Find existing product
        existing_product = self._find_existing_product(product_data)
        
        if existing_product:
            # Product exists - handle based on duplicate_action
            if self.duplicate_action == 'skip':
                return {
                    'action': 'skipped',
                    'product': existing_product,
                    'reason': 'Product already exists (skipped by configuration)'
                }
            
            elif self.duplicate_action == 'update':
                # Update existing product
                self._update_product(existing_product, product_data)
                
                # Create/update vendor price if enabled
                if self.create_vendor_prices:
                    VendorPrice.find_or_create_vendor_price(
                        existing_product.id,
                        self.source_system,
                        vendor_price_data
                    )
                
                # Update cost price if enabled
                if self.update_cost_price:
                    self._update_cost_price(existing_product)
                
                return {
                    'action': 'updated',
                    'product': existing_product
                }
            
            elif self.duplicate_action == 'add_vendor':
                # Add as vendor price to existing product
                if self.create_vendor_prices:
                    VendorPrice.find_or_create_vendor_price(
                        existing_product.id,
                        self.source_system,
                        vendor_price_data
                    )
                
                # Update cost price if enabled
                if self.update_cost_price:
                    self._update_cost_price(existing_product)
                
                return {
                    'action': 'vendor_added',
                    'product': existing_product
                }
            
            elif self.duplicate_action == 'create_new':
                # Create new product (may cause duplicates)
                new_product = self._create_product(product_data)
                
                # Create vendor price if enabled
                if self.create_vendor_prices:
                    VendorPrice.find_or_create_vendor_price(
                        new_product.id,
                        self.source_system,
                        vendor_price_data
                    )
                
                return {
                    'action': 'created',
                    'product': new_product
                }
        
        else:
            # Product doesn't exist - create new
            new_product = self._create_product(product_data)
            
            # Create vendor price if enabled
            if self.create_vendor_prices:
                VendorPrice.find_or_create_vendor_price(
                    new_product.id,
                    self.source_system,
                    vendor_price_data
                )
            
            return {
                'action': 'created',
                'product': new_product
            }

    def _extract_product_data(self, record):
        """Extract product.template data from record"""
        # Map common field names
        field_mapping = {
            'name': ['name', 'product_name', 'title', 'product_title'],
            'default_code': ['default_code', 'sku', 'product_code', 'code', 'external_product_id'],
            'list_price': ['list_price', 'price', 'sale_price', 'selling_price'],
            'standard_price': ['standard_price', 'cost', 'cost_price'],
            'description': ['description', 'desc', 'product_description'],
            'description_sale': ['description_sale', 'short_description', 'summary'],
            'external_product_id': ['external_product_id', 'external_id', 'product_id', 'id'],
            'external_product_url': ['external_product_url', 'url', 'product_url', 'link'],
            'external_category_id': ['external_category_id', 'category_id', 'category'],
            'external_category_name': ['external_category_name', 'category_name', 'category_title'],
        }
        
        product_data = {
            'external_source': self.source_system,
            'external_sync_status': 'synced',
            'external_last_sync': fields.Datetime.now(),
        }
        
        # Extract fields using mapping
        for odoo_field, possible_names in field_mapping.items():
            for name in possible_names:
                if name in record and record[name]:
                    value = record[name]
                    # Convert to appropriate type
                    if odoo_field in ['list_price', 'standard_price']:
                        try:
                            product_data[odoo_field] = float(value)
                        except (ValueError, TypeError):
                            pass
                    else:
                        product_data[odoo_field] = str(value).strip()
                    break
        
        # Ensure required fields
        if 'name' not in product_data:
            raise ValidationError(_('Product name is required'))
        
        # Set default price if not provided
        if 'list_price' not in product_data:
            product_data['list_price'] = 0.0
        
        return product_data

    def _extract_vendor_price_data(self, record):
        """Extract vendor price data from record"""
        # Map common field names
        field_mapping = {
            'price': ['price', 'list_price', 'sale_price', 'selling_price'],
            'external_product_id': ['external_product_id', 'external_id', 'product_id', 'sku'],
            'external_url': ['external_product_url', 'url', 'product_url', 'link'],
            'availability': ['availability', 'stock_status', 'in_stock'],
            'stock_quantity': ['stock_quantity', 'quantity', 'qty', 'stock'],
            'vendor_name': ['vendor_name', 'vendor', 'seller', 'seller_name'],
        }
        
        vendor_data = {
            'data_source_id': self.data_source_id.id if self.data_source_id else False,
        }
        
        # Extract fields
        for vendor_field, possible_names in field_mapping.items():
            for name in possible_names:
                if name in record and record[name]:
                    value = record[name]
                    # Convert to appropriate type
                    if vendor_field in ['price', 'stock_quantity']:
                        try:
                            vendor_data[vendor_field] = float(value)
                        except (ValueError, TypeError):
                            pass
                    elif vendor_field == 'availability':
                        # Map common availability values
                        value_lower = str(value).lower()
                        if value_lower in ['in stock', 'instock', 'available', 'yes', 'true', '1']:
                            vendor_data[vendor_field] = 'in_stock'
                        elif value_lower in ['out of stock', 'outofstock', 'unavailable', 'no', 'false', '0']:
                            vendor_data[vendor_field] = 'out_of_stock'
                        elif value_lower in ['limited', 'low stock', 'lowstock']:
                            vendor_data[vendor_field] = 'limited'
                        else:
                            vendor_data[vendor_field] = 'unknown'
                    else:
                        vendor_data[vendor_field] = str(value).strip()
                    break
        
        # Ensure price is set
        if 'price' not in vendor_data:
            vendor_data['price'] = 0.0
        
        return vendor_data

    def _find_existing_product(self, product_data):
        """Find existing product based on match strategy"""
        Product = self.env['product.template']
        
        external_url = product_data.get('external_product_url')
        external_id = product_data.get('external_product_id')
        sku = product_data.get('default_code')
        name = product_data.get('name')
        
        # Try different match strategies
        if self.match_strategy == 'url':
            if external_url:
                return Product.search([('external_product_url', '=', external_url)], limit=1)
        
        elif self.match_strategy == 'sku':
            if sku:
                return Product.search([('default_code', '=', sku)], limit=1)
            elif external_id:
                return Product.search([('external_product_id', '=', external_id)], limit=1)
        
        elif self.match_strategy == 'name':
            if name:
                return Product.search([('name', '=', name)], limit=1)
        
        elif self.match_strategy == 'url_or_sku':
            # Try URL first
            if external_url:
                product = Product.search([('external_product_url', '=', external_url)], limit=1)
                if product:
                    return product
            # Then try SKU
            if sku:
                product = Product.search([('default_code', '=', sku)], limit=1)
                if product:
                    return product
            # Then try external ID
            if external_id:
                product = Product.search([('external_product_id', '=', external_id)], limit=1)
                if product:
                    return product
        
        elif self.match_strategy == 'url_or_name':
            # Try URL first
            if external_url:
                product = Product.search([('external_product_url', '=', external_url)], limit=1)
                if product:
                    return product
            # Then try name
            if name:
                product = Product.search([('name', '=', name)], limit=1)
                if product:
                    return product
        
        return False

    def _create_product(self, product_data):
        """Create new product"""
        Product = self.env['product.template']
        
        # Set import date
        product_data['external_import_date'] = fields.Datetime.now()
        
        # Create product
        product = Product.create(product_data)
        
        _logger.info(f"Created product: {product.name} (ID: {product.id})")
        return product

    def _update_product(self, product, product_data):
        """Update existing product"""
        # Remove fields that shouldn't be updated
        update_data = product_data.copy()
        update_data.pop('external_import_date', None)  # Don't change import date
        
        # Update sync info
        update_data['external_last_sync'] = fields.Datetime.now()
        update_data['external_sync_status'] = 'synced'
        update_data['external_update_count'] = product.external_update_count + 1
        
        # Update product
        product.write(update_data)
        
        _logger.info(f"Updated product: {product.name} (ID: {product.id})")

    def _update_cost_price(self, product):
        """Update product cost price based on vendor prices"""
        if not product.vendor_price_ids:
            return
        
        active_prices = product.vendor_price_ids.filtered(lambda p: p.active)
        if not active_prices:
            return
        
        prices = active_prices.mapped('price')
        
        if self.cost_price_strategy == 'lowest':
            new_cost = min(prices)
        elif self.cost_price_strategy == 'average':
            new_cost = sum(prices) / len(prices)
        elif self.cost_price_strategy == 'first':
            new_cost = prices[0] if prices else 0.0
        else:  # manual
            return  # Don't update
        
        # Update cost price
        product.write({'standard_price': new_cost})
        
        _logger.info(f"Updated cost price for {product.name}: {new_cost}")

    def action_view_imported_products(self):
        """View imported products"""
        self.ensure_one()
        
        return {
            'name': _('Imported Products'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'list,form',
            'domain': [('external_source', '=', self.source_system)],
            'context': {'search_default_external_products': 1},
        }

    def action_view_import_history(self):
        """View import history record"""
        self.ensure_one()
        
        if not self.import_history_id:
            raise UserError(_('No import history record found.'))
        
        return {
            'name': _('Import History'),
            'type': 'ir.actions.act_window',
            'res_model': 'unified.import.history',
            'res_id': self.import_history_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

