#!/usr/bin/env python3
"""
Script to add detailed information to existing products.
Reads products.json, visits each product page, and adds detailed data.
"""

import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scrapers.vetution_scraper.scraper_playwright import VetutionScraper
from _common import get_products_json, get_products_csv

if __name__ == "__main__":
    print("="*70)
    print("ADD DETAILED PRODUCT INFORMATION")
    print("="*70)
    
    # Load existing products
    try:
        with open(get_products_json(), 'r') as f:
            products = json.load(f)
        print(f"\nLoaded {len(products)} products from products.json")
    except FileNotFoundError:
        print("Error: products.json not found!")
        print("Please run the main scraper first to create products.json")
        sys.exit(1)
    
    # Check how many already have details
    with_details = sum(1 for p in products if 'vendor_prices' in p or 'detailed_sections' in p)
    print(f"Products with details: {with_details}/{len(products)}")
    
    if with_details > 0:
        print(f"\n{with_details} products already have detailed information.")
        response = input("Do you want to update them anyway? (y/n): ").strip().lower()
        if response != 'y':
            print("Skipping products that already have details.")
            skip_existing = True
        else:
            skip_existing = False
    else:
        skip_existing = False
    
    # Initialize scraper
    scraper = VetutionScraper(
        email="vetdrughouse@gmail.com",
        password="Shabab28jan",
        phone="01000059085"
    )
    
    print("\n" + "="*70)
    print("BROWSER SETUP")
    print("="*70)
    print("Opening browser...")
    import time
    scraper.start_browser(headless=False)
    
    # Navigate to homepage first
    try:
        print("Navigating to website...")
        scraper.page.goto("https://www.vetution.com", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)
        print("Browser opened. Please login manually in the browser window.")
        print("\nLogin credentials:")
        print("  - Email: vetdrughouse@gmail.com")
        print("  - OR Phone: 01000059085")
        print("  - Password: Shabab28jan")
        print("\nWaiting 30 seconds for you to login...")
        print("(The script will continue automatically)")
        time.sleep(30)  # Give user time to login
        print("\nContinuing with scraping...")
    except Exception as e:
        print(f"Error navigating: {e}")
        print("Please ensure you're logged in in the browser.")
        time.sleep(10)
    
    scraper.logged_in = True
    
    # Process products
    updated = 0
    skipped = 0
    errors = 0
    
    for i, product in enumerate(products, 1):
        # Skip if already has details and skip_existing is True
        if skip_existing and ('vendor_prices' in product or 'detailed_sections' in product):
            skipped += 1
            continue
        
        print(f"\n[{i}/{len(products)}] Processing: {product.get('name', 'Unknown')}")
        print(f"  URL: {product.get('link', 'N/A')}")
        
        try:
            details = scraper.get_product_details(product.get('link', ''))
            if details:
                # Merge details into product
                product.update(details)
                updated += 1
                print(f"  ✓ Added details")
                
                # Show what was added
                if 'vendor_prices' in details:
                    print(f"    - {len(details['vendor_prices'])} vendor prices")
                if 'detailed_sections' in details:
                    print(f"    - {len(details['detailed_sections'])} detailed sections")
                if 'tags' in details:
                    print(f"    - {len(details['tags'])} tags")
            else:
                print(f"  ⚠ No details found")
                errors += 1
        except Exception as e:
            print(f"  ✗ Error: {e}")
            errors += 1
        
        # Save progress every 10 products
        if i % 10 == 0:
            print(f"\n  Saving progress... ({updated} updated, {skipped} skipped, {errors} errors)")
            with open(get_products_json(), 'w', encoding='utf-8') as f:
                json.dump(products, f, indent=2, ensure_ascii=False)
    
    # Final save
    print(f"\n{'='*70}")
    print("FINALIZING...")
    print(f"{'='*70}")
    with open(get_products_json(), 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    # Also update CSV
    import csv
    if products:
        all_fields = set()
        for product in products:
            all_fields.update(product.keys())
        fieldnames = ['name', 'link']
        other_fields = sorted([f for f in all_fields if f not in fieldnames])
        fieldnames.extend(other_fields)
        with open(get_products_csv(), 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(products)
    
    print(f"\n{'='*70}")
    print("COMPLETE!")
    print(f"{'='*70}")
    print(f"Updated: {updated}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {errors}")
    print(f"Total: {len(products)}")
    
    scraper.close_browser()
    print("\nDone!")

