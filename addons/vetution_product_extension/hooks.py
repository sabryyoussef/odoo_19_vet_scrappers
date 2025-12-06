# -*- coding: utf-8 -*-

import json
import csv
import os
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def load_product_data(env):
    """Load product data from JSON and CSV files on module install/update"""
    # Try multiple possible paths (host path and container path)
    possible_paths = [
        '/home/sabry3/vetutions/products.json',  # Host path
        '/mnt/vetutions-data/products.json',      # Container mounted path
    ]
    json_path = None
    csv_path = None
    
    for path in possible_paths:
        if os.path.exists(path):
            json_path = path
            csv_path = path.replace('.json', '.csv')
            break
    
    if not json_path:
        _logger.info("Product data files not found. Use Import Product Data wizard to import data.")
        return
    
    # Load JSON file
    if os.path.exists(json_path):
        try:
            _logger.info(f"Loading products from JSON: {json_path}")
            with open(json_path, 'r', encoding='utf-8') as f:
                products_data = json.load(f)
            
            # Handle both single object and array
            if isinstance(products_data, dict):
                products_data = [products_data]
            elif not isinstance(products_data, list):
                _logger.warning(f"Invalid JSON format in {json_path}")
                return
            
            _import_products(env, products_data, 'JSON')
        except Exception as e:
            _logger.error(f"Error loading JSON file {json_path}: {str(e)}", exc_info=True)
    else:
        _logger.info(f"JSON file not found: {json_path}")
    
    # Load CSV file
    if os.path.exists(csv_path):
        try:
            _logger.info(f"Loading products from CSV: {csv_path}")
            products_data = []
            with open(csv_path, 'r', encoding='utf-8') as f:
                csv_reader = csv.DictReader(f)
                for row in csv_reader:
                    # Convert string values to appropriate types
                    product = {}
                    for key, value in row.items():
                        if not value or value.strip() == '':
                            continue
                        # Try to parse as JSON for list/dict fields
                        if key in ['ingredients', 'sizes', 'tags', 'species', 'vendor_prices', 'all_prices', 'detailed_sections']:
                            try:
                                product[key] = json.loads(value)
                            except (json.JSONDecodeError, ValueError):
                                # If not JSON, treat as comma-separated string (except for prices)
                                if key in ['vendor_prices', 'all_prices']:
                                    # Keep as string, will be parsed later
                                    product[key] = value
                                else:
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
                        else:
                            product[key] = value
                    products_data.append(product)
            
            _import_products(env, products_data, 'CSV')
        except Exception as e:
            _logger.error(f"Error loading CSV file {csv_path}: {str(e)}", exc_info=True)
    else:
        _logger.info(f"CSV file not found: {csv_path}")


def _import_products(env, products_data, source_type):
    """Import products using the same logic as the wizard"""
    ProductTemplate = env['product.template']
    ProductProduct = env['product.product']
    VendorPrice = env['vetution.vendor.price']
    
    created = 0
    updated = 0
    errors = 0
    
    for idx, product_data in enumerate(products_data, 1):
        try:
            # Map data
            mapped_data = _map_product_data(product_data)
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
            
            # Find existing product
            existing_template = None
            if product_data.get('link'):
                existing_template = ProductTemplate.search([
                    ('product_variant_ids.vetution_link', '=', product_data['link'])
                ], limit=1)
            elif product_data.get('name'):
                existing_template = ProductTemplate.search([
                    ('name', '=', product_data['name'])
                ], limit=1)
            
            # Create or update
            if existing_template:
                existing_template.write(template_data)
                product = existing_template.product_variant_id
                if variant_data:
                    product.write(variant_data)
                # Assign Vetution tag
                product._assign_vetution_tag()
                updated += 1
            else:
                # Set defaults
                if 'type' not in template_data:
                    template_data['type'] = 'consu'
                if 'sale_ok' not in template_data:
                    template_data['sale_ok'] = True
                if 'purchase_ok' not in template_data:
                    template_data['purchase_ok'] = True
                
                template = ProductTemplate.create(template_data)
                product = template.product_variant_id
                if variant_data:
                    product.write(variant_data)
                # Assign Vetution tag
                product._assign_vetution_tag()
                created += 1
            
            # Handle vendor prices (support both vendor_prices and all_prices)
            vendor_prices_data = product_data.get('vendor_prices') or product_data.get('all_prices')
            if vendor_prices_data:
                # Clear existing
                if product.vetution_vendor_price_ids:
                    product.vetution_vendor_price_ids.unlink()
                
                # Handle list of prices
                if isinstance(vendor_prices_data, list):
                    for vp_data in vendor_prices_data:
                        if isinstance(vp_data, dict):
                            VendorPrice.create({
                                'product_id': product.id,
                                'price': vp_data.get('price', 0.0),
                                'currency': vp_data.get('currency', 'EGP'),
                                'expiration_date': vp_data.get('expiration_date'),
                                'available': vp_data.get('available', True),
                                'vendor_name': vp_data.get('vendor_name', ''),
                            })
                elif isinstance(vendor_prices_data, str):
                    # Try to parse as JSON string (from CSV)
                    try:
                        parsed_prices = json.loads(vendor_prices_data)
                        if isinstance(parsed_prices, list):
                            for vp_data in parsed_prices:
                                if isinstance(vp_data, dict):
                                    VendorPrice.create({
                                        'product_id': product.id,
                                        'price': vp_data.get('price', 0.0),
                                        'currency': vp_data.get('currency', 'EGP'),
                                        'expiration_date': vp_data.get('expiration_date'),
                                        'available': vp_data.get('available', True),
                                        'vendor_name': vp_data.get('vendor_name', ''),
                                    })
                    except (json.JSONDecodeError, ValueError):
                        _logger.warning(f"Could not parse vendor_prices/all_prices for product {product_data.get('name', 'Unknown')}")
            
            # Trigger recomputation of average price and cost update
            product._compute_vetution_average_price()
            
            if idx % 100 == 0:
                _logger.info(f"Processed {idx}/{len(products_data)} products from {source_type}")
                
        except Exception as e:
            errors += 1
            _logger.error(f"Error importing product {idx} from {source_type}: {str(e)}", exc_info=True)
    
    _logger.info(f"Import from {source_type} completed: Created={created}, Updated={updated}, Errors={errors}")


def _normalize_url(url):
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


def _map_product_data(product_data):
    """Map scraped data to Odoo product fields (same as wizard)"""
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
                value = _normalize_url(value)
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
            if isinstance(product_data[source_key], list):
                mapped_data[target_field] = ', '.join(str(item) for item in product_data[source_key] if item)
            else:
                mapped_data[target_field] = str(product_data[source_key]) if product_data[source_key] else ''
    
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


def post_init_hook(cr, registry):
    """Hook called after module installation"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    load_product_data(env)


def uninstall_hook(cr, registry):
    """Hook called before module uninstallation"""
    # Optionally clean up data here if needed
    pass


def pre_init_hook(cr):
    """Hook called before module installation"""
    pass

