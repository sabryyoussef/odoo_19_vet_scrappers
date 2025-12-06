#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export Vetution products with variants to flattened CSV
One row per variant instead of one row per product
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
import csv
from datetime import datetime

def export_variants_flat():
    """Export variants to flattened CSV format"""
    print("="*70)
    print(" " * 15 + "FLATTEN VARIANTS TO CSV")
    print("="*70)
    print()
    
    # Load products data
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'vetution')
    json_file = os.path.join(data_dir, 'products.json')
    
    # Also check in scrapers data folder
    if not os.path.exists(json_file):
        scraper_data_dir = os.path.join(os.path.dirname(__file__), '..', 'scrapers', 'vetution_scraper', 'data')
        json_file = os.path.join(scraper_data_dir, 'products.json')
    
    if not os.path.exists(json_file):
        print(f"✗ File not found: {json_file}")
        print("  Please run the scraper first to generate products.json")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"📊 Loaded {len(products)} products")
    
    # Flatten variants
    variants_list = []
    products_with_variants = 0
    total_variants = 0
    
    for product in products:
        base_info = {
            'product_name': product.get('name', ''),
            'product_link': product.get('link', ''),
            'product_image': product.get('image_url', ''),
            'product_category': product.get('main_category', ''),
            'product_brand': product.get('brand', ''),
        }
        
        # If product has variants, create row for each variant
        if product.get('variants'):
            products_with_variants += 1
            for variant in product['variants']:
                variant_row = base_info.copy()
                variant_row.update({
                    'variant_name': variant.get('name', ''),
                    'variant_type': variant.get('type', variant.get('option_type', 'variant')),
                    'variant_sku': variant.get('sku', ''),
                    'variant_price': variant.get('price', ''),
                    'currency': variant.get('currency', 'EGP'),
                    'available': 'Yes' if variant.get('available', True) else 'No',
                    'has_variants': 'Yes'
                })
                variants_list.append(variant_row)
                total_variants += 1
        else:
            # Product without variants - single row
            variant_row = base_info.copy()
            variant_row.update({
                'variant_name': 'Standard',
                'variant_type': 'default',
                'variant_sku': product.get('sku', ''),
                'variant_price': product.get('price', ''),
                'currency': product.get('currency', 'EGP'),
                'available': 'Yes',
                'has_variants': 'No'
            })
            variants_list.append(variant_row)
    
    print(f"✓ Products with variants: {products_with_variants}")
    print(f"✓ Total variants: {total_variants}")
    print(f"✓ Total rows to export: {len(variants_list)}")
    
    # Save to CSV
    output_file = os.path.join(data_dir, f'variants_flat_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    
    fieldnames = [
        'product_name', 'variant_name', 'variant_type', 'variant_sku',
        'variant_price', 'currency', 'available', 'has_variants',
        'product_link', 'product_image', 'product_category', 'product_brand'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(variants_list)
    
    print()
    print("="*70)
    print("EXPORT COMPLETE")
    print("="*70)
    print(f"✓ Saved to: {output_file}")
    print()
    print("📋 Sample rows:")
    for i, row in enumerate(variants_list[:5], 1):
        print(f"\n{i}. {row['product_name']}")
        print(f"   Variant: {row['variant_name']} - {row['variant_price']} {row['currency']}")
        print(f"   Available: {row['available']}")
    
    print()
    print("="*70)

if __name__ == "__main__":
    export_variants_flat()

