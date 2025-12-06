#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update image URLs for existing products in products.json and products.csv
"""

import json
import csv
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scrapers.vetution_scraper.scraper_playwright import VetutionScraper

def update_image_urls():
    """Update image URLs for all products"""
    
    # Load existing products
    print("Loading existing products...")
    from _common import get_products_json
    products_file = get_products_json('vetution')
    try:
        with open(products_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
    except FileNotFoundError:
        print("Error: products.json not found!")
        return
    
    print(f"Loaded {len(products)} products")
    
    # Count products that need image updates
    needs_update = []
    for i, product in enumerate(products):
        image_url = product.get('image_url', '')
        # Check if missing image or has placeholder
        if not image_url or 'user.png' in image_url.lower() or 'placeholder' in image_url.lower():
            needs_update.append(i)
    
    print(f"Products needing image update: {len(needs_update)}/{len(products)}")
    
    if not needs_update:
        print("All products already have image URLs!")
        return
    
    # Initialize scraper
    print("\nInitializing scraper...")
    scraper = VetutionScraper(
        email="vetdrughouse@gmail.com",
        password="Shabab28jan",
        phone="01000059085"
    )
    
    # Check for manual login flag
    import sys
    manual_mode = "--manual" in sys.argv or "-m" in sys.argv
    
    # Start browser
    print("Starting browser...")
    scraper.start_browser(headless=not manual_mode)
    
    # Login
    if manual_mode:
        print("\n" + "="*70)
        print("MANUAL LOGIN MODE")
        print("="*70)
        print("Please login to the website in the browser window using:")
        print("  - Email: vetdrughouse@gmail.com")
        print("  - OR Phone: 01000059085")
        print("  - Password: Shabab28jan")
        print("\nAfter logging in, make sure you can see products and images.")
        print("Then come back here and press Enter to start updating image URLs...")
        input()
        scraper.logged_in = True
        print("Continuing with image URL updates...\n")
    else:
        # Try automated login
        print("Attempting automated login...")
        if not scraper.login():
            print("\n" + "="*70)
            print("AUTOMATED LOGIN FAILED")
            print("="*70)
            print("The script will continue without login.")
            print("Note: Images should still be accessible without login.")
            print("If you encounter issues, run with manual login:")
            print("  python3 update_image_urls.py --manual")
            print("\nContinuing anyway...\n")
            scraper.logged_in = False
        else:
            print("Login successful!\n")
    
    # Update image URLs
    updated = 0
    failed = 0
    
    for idx, product_idx in enumerate(needs_update, 1):
        product = products[product_idx]
        product_name = product.get('name', 'Unknown')
        product_link = product.get('link', '')
        
        if not product_link:
            print(f"[{idx}/{len(needs_update)}] Skipping {product_name}: No link")
            continue
        
        print(f"[{idx}/{len(needs_update)}] Updating {product_name}...")
        
        try:
            # Get product details (which includes image)
            details = scraper.get_product_details(product_link)
            
            if details and details.get('image_url'):
                old_image = product.get('image_url', 'None')
                new_image = details['image_url']
                
                # Only update if it's not a placeholder
                if 'user.png' not in new_image.lower() and 'placeholder' not in new_image.lower():
                    product['image_url'] = new_image
                    updated += 1
                    print(f"    ✓ Updated: {old_image[:50]} -> {new_image[:50]}")
                else:
                    print(f"    - Still placeholder: {new_image[:50]}")
                    failed += 1
            else:
                print(f"    - No image found in details page")
                failed += 1
                
        except Exception as e:
            print(f"    ✗ Error: {e}")
            failed += 1
        
        # Small delay between requests
        time.sleep(0.5)
        
        # Save progress every 50 products
        if idx % 50 == 0:
            print(f"\nSaving progress... ({updated} updated, {failed} failed)")
            save_products(products)
    
    # Final save
    print(f"\nSaving final results...")
    save_products(products)
    
    # Close browser
    scraper.close_browser()
    
    # Summary
    print("\n" + "="*70)
    print("UPDATE SUMMARY")
    print("="*70)
    print(f"Total products: {len(products)}")
    print(f"Products needing update: {len(needs_update)}")
    print(f"Successfully updated: {updated}")
    print(f"Failed: {failed}")
    print(f"Remaining without images: {len(needs_update) - updated - failed}")
    print("="*70)

def save_products(products):
    """Save products to JSON and CSV"""
    from _common import get_products_json, get_products_csv
    
    # Save JSON
    products_file = get_products_json('vetution')
    with open(products_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    # Save CSV
    if not products:
        return
    
    # Get all possible fieldnames
    all_fields = set()
    for product in products:
        all_fields.update(product.keys())
    
    # Order fields: name, link, image_url first, then others alphabetically
    fieldnames = ['name', 'link', 'image_url']
    other_fields = sorted([f for f in all_fields if f not in fieldnames])
    fieldnames.extend(other_fields)
    
    csv_file = get_products_csv('vetution')
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(products)
    
    print(f"Products saved to {products_file} and {csv_file}")

if __name__ == "__main__":
    import sys
    
    if "--manual" in sys.argv or "-m" in sys.argv:
        print("Manual login mode not yet implemented for this script.")
        print("Please use automated login with credentials.")
        sys.exit(1)
    
    update_image_urls()

