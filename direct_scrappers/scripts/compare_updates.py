#!/usr/bin/env python3
"""
Compare two product files to see what changed.
Useful for reviewing updates.
"""

import json
import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from _common import get_products_json

def load_products(filename):
    """Load products from JSON file"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def compare_products(old_file, new_file):
    """Compare two product files and show changes"""
    print("="*70)
    print("PRODUCT UPDATE COMPARISON")
    print("="*70)
    
    old_products = load_products(old_file)
    new_products = load_products(new_file)
    
    # Index by link
    old_dict = {p.get('link'): p for p in old_products if p.get('link')}
    new_dict = {p.get('link'): p for p in new_products if p.get('link')}
    
    # Find changes
    new_products_list = []
    removed_products_list = []
    price_changes = []
    availability_changes = []
    updated_products = []
    
    # Check for new products
    for link, product in new_dict.items():
        if link not in old_dict:
            new_products_list.append(product)
    
    # Check for removed products
    for link, product in old_dict.items():
        if link not in new_dict:
            removed_products_list.append(product)
    
    # Check for changes in existing products
    for link, new_product in new_dict.items():
        if link in old_dict:
            old_product = old_dict[link]
            changes = []
            
            # Check price changes
            old_price = old_product.get('price')
            new_price = new_product.get('price')
            if old_price != new_price:
                price_changes.append({
                    'name': new_product.get('name'),
                    'link': link,
                    'old_price': old_price,
                    'new_price': new_price,
                    'currency': new_product.get('currency', 'EGP')
                })
                changes.append(f"Price: {old_price} → {new_price}")
            
            # Check vendor prices
            old_vp = old_product.get('vendor_prices', [])
            new_vp = new_product.get('vendor_prices', [])
            if old_vp != new_vp:
                # Check availability
                old_avail = any(vp.get('available', False) for vp in old_vp)
                new_avail = any(vp.get('available', False) for vp in new_vp)
                if old_avail != new_avail:
                    availability_changes.append({
                        'name': new_product.get('name'),
                        'link': link,
                        'old_available': old_avail,
                        'new_available': new_avail
                    })
                    changes.append(f"Availability: {old_avail} → {new_avail}")
            
            if changes:
                updated_products.append({
                    'name': new_product.get('name'),
                    'link': link,
                    'changes': changes
                })
    
    # Print summary
    print(f"\nOld file: {old_file}")
    print(f"New file: {new_file}")
    print(f"\nOld products: {len(old_products)}")
    print(f"New products: {len(new_products)}")
    print(f"\n{'='*70}")
    print("CHANGES SUMMARY")
    print(f"{'='*70}")
    print(f"New products: {len(new_products_list)}")
    print(f"Removed products: {len(removed_products_list)}")
    print(f"Updated products: {len(updated_products)}")
    print(f"Price changes: {len(price_changes)}")
    print(f"Availability changes: {len(availability_changes)}")
    
    # Show new products
    if new_products_list:
        print(f"\n{'='*70}")
        print(f"NEW PRODUCTS ({len(new_products_list)})")
        print(f"{'='*70}")
        for product in new_products_list[:10]:  # Show first 10
            print(f"  - {product.get('name')}")
            print(f"    Link: {product.get('link')}")
            if product.get('price'):
                print(f"    Price: {product.get('price')} {product.get('currency', 'EGP')}")
        if len(new_products_list) > 10:
            print(f"  ... and {len(new_products_list) - 10} more")
    
    # Show price changes
    if price_changes:
        print(f"\n{'='*70}")
        print(f"PRICE CHANGES ({len(price_changes)})")
        print(f"{'='*70}")
        for change in price_changes[:20]:  # Show first 20
            print(f"  {change['name']}")
            print(f"    {change['old_price']} {change['currency']} → {change['new_price']} {change['currency']}")
        if len(price_changes) > 20:
            print(f"  ... and {len(price_changes) - 20} more")
    
    # Show availability changes
    if availability_changes:
        print(f"\n{'='*70}")
        print(f"AVAILABILITY CHANGES ({len(availability_changes)})")
        print(f"{'='*70}")
        for change in availability_changes[:20]:
            print(f"  {change['name']}")
            print(f"    {'Available' if change['old_available'] else 'Unavailable'} → {'Available' if change['new_available'] else 'Unavailable'}")
        if len(availability_changes) > 20:
            print(f"  ... and {len(availability_changes) - 20} more")
    
    # Show removed products
    if removed_products_list:
        print(f"\n{'='*70}")
        print(f"REMOVED PRODUCTS ({len(removed_products_list)})")
        print(f"{'='*70}")
        for product in removed_products_list[:10]:
            print(f"  - {product.get('name')}")
        if len(removed_products_list) > 10:
            print(f"  ... and {len(removed_products_list) - 10} more")
    
    print(f"\n{'='*70}")
    
    # Save detailed report
    report = {
        'comparison_date': datetime.now().isoformat(),
        'old_file': old_file,
        'new_file': new_file,
        'summary': {
            'old_count': len(old_products),
            'new_count': len(new_products),
            'new_products': len(new_products_list),
            'removed_products': len(removed_products_list),
            'updated_products': len(updated_products),
            'price_changes': len(price_changes),
            'availability_changes': len(availability_changes)
        },
        'new_products': new_products_list,
        'removed_products': removed_products_list,
        'price_changes': price_changes,
        'availability_changes': availability_changes,
        'all_updates': updated_products
    }
    
    report_file = f"update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"Detailed report saved to: {report_file}")
    
    return report


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python compare_updates.py <old_file> <new_file>")
        print("\nExample:")
        print("  python compare_updates.py backups/products_backup_20241204_020000.json products.json")
        sys.exit(1)
    
    old_file = sys.argv[1]
    new_file = sys.argv[2]
    
    if not os.path.exists(old_file):
        print(f"Error: {old_file} not found")
        sys.exit(1)
    
    if not os.path.exists(new_file):
        print(f"Error: {new_file} not found")
        sys.exit(1)
    
    compare_products(old_file, new_file)

