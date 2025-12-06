#!/usr/bin/env python3
"""Monitor the progress of add_product_details.py"""

import json
import time
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from _common import get_products_json

def check_progress():
    products_file = get_products_json()
    if not os.path.exists(products_file):
        print(f"{products_file} not found")
        return
    
    with open(products_file, 'r') as f:
        products = json.load(f)
    
    total = len(products)
    with_details = sum(1 for p in products if 'vendor_prices' in p or 'detailed_sections' in p)
    with_vendor_prices = sum(1 for p in products if 'vendor_prices' in p)
    with_sections = sum(1 for p in products if 'detailed_sections' in p)
    with_images = sum(1 for p in products if 'image_url' in p)
    with_tags = sum(1 for p in products if 'tags' in p)
    
    print(f"\n{'='*60}")
    print(f"PROGRESS UPDATE")
    print(f"{'='*60}")
    print(f"Total products: {total}")
    print(f"Products with details: {with_details} ({with_details/total*100:.1f}%)")
    print(f"  - With vendor prices: {with_vendor_prices}")
    print(f"  - With detailed sections: {with_sections}")
    print(f"  - With images: {with_images}")
    print(f"  - With tags: {with_tags}")
    
    if with_details > 0:
        # Show a sample
        sample = next((p for p in products if 'vendor_prices' in p or 'detailed_sections' in p), None)
        if sample:
            print(f"\nSample: {sample.get('name', 'Unknown')}")
            if 'vendor_prices' in sample:
                print(f"  Prices: {len(sample['vendor_prices'])} vendors")
                for vp in sample['vendor_prices'][:2]:
                    print(f"    - {vp.get('price')} {vp.get('currency')} (Exp: {vp.get('expiration_date', 'N/A')})")
            if 'detailed_sections' in sample:
                sections = list(sample['detailed_sections'].keys())[:3]
                print(f"  Sections: {', '.join(sections)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--watch':
        # Continuous monitoring
        while True:
            os.system('clear')
            check_progress()
            print("\nPress Ctrl+C to stop monitoring...")
            time.sleep(5)
    else:
        check_progress()

