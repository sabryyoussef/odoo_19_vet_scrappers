#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Vetution variant extraction with login
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scrapers.vetution_scraper.scraper_playwright import VetutionScraper
import time

def test_vetution_variants():
    """Test Vetution scraper with variant extraction"""
    print("="*70)
    print(" " * 15 + "VETUTION VARIANT EXTRACTION TEST")
    print("="*70)
    print()
    
    # Initialize scraper with credentials
    scraper = VetutionScraper(
        email="vetdrughouse@gmail.com",
        password="Shabab28jan",
        phone="01000059085"
    )
    
    print("📝 Test Steps:")
    print("  1. Open browser (visible mode)")
    print("  2. Login manually to see prices")
    print("  3. Scrape 1 page with full details")
    print("  4. Extract variants for products")
    print()
    
    try:
        # Start browser in visible mode for login
        print("🌐 Starting browser...")
        scraper.start_browser(headless=False)
        
        # Navigate to homepage
        print("📍 Navigating to Vetution homepage...")
        scraper.page.goto("https://www.vetution.com", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)
        
        print()
        print("="*70)
        print(" " * 20 + "MANUAL LOGIN REQUIRED")
        print("="*70)
        print()
        print("⚠️  Prices are only visible to registered users!")
        print()
        print("Please login in the browser window using:")
        print("  📧 Email: vetdrughouse@gmail.com")
        print("  📱 Phone: 01000059085")
        print("  🔐 Password: Shabab28jan")
        print()
        print("After logging in, navigate to the products page:")
        print("  🔗 https://www.vetution.com/products?page=1&categories=pharmacy-vaccines")
        print()
        print("Make sure you can see product PRICES on the page!")
        print()
        print("="*70)
        input("Press Enter after logging in and seeing prices...")
        print()
        
        scraper.logged_in = True
        
        # Test with page 1
        print("📊 Scraping page 1 with details...")
        print("="*70)
        
        html_content = scraper.get_page(1, categories="pharmacy-vaccines")
        
        if html_content:
            products = scraper.extract_product_links(html_content)
            print(f"\n✓ Found {len(products)} products on page 1")
            
            # Check how many have prices
            with_prices = sum(1 for p in products if p.get('price'))
            print(f"✓ Products with prices: {with_prices}/{len(products)}")
            
            if with_prices == 0:
                print()
                print("⚠️  WARNING: No prices found!")
                print("   This means you're not logged in or prices aren't visible.")
                print("   Please ensure you're logged in and can see prices on the page.")
                print()
            
            # Fetch details for first 3 products (including variants)
            if products:
                print()
                print("="*70)
                print("FETCHING DETAILED INFO (including variants)")
                print("="*70)
                print()
                
                for i, product in enumerate(products[:3], 1):
                    print(f"\n[{i}/3] {product['name']}")
                    print("-" * 60)
                    
                    details = scraper.get_product_details(product['link'])
                    product.update(details)
                    
                    # Show results
                    if product.get('price'):
                        print(f"  💰 Price: {product['price']} {product.get('currency', 'EGP')}")
                    
                    if product.get('vendor_prices'):
                        print(f"  🏪 Vendor Prices: {len(product['vendor_prices'])} vendors")
                        for vp in product['vendor_prices'][:3]:
                            exp = f" (Exp: {vp.get('expiration_date')})" if vp.get('expiration_date') else ""
                            avail = "✓" if vp.get('available') else "✗"
                            print(f"     {avail} {vp['price']} {vp['currency']}{exp}")
                    
                    if product.get('variants'):
                        print(f"  📦 Variants: {len(product['variants'])}")
                        for v in product['variants']:
                            price_info = f" - {v.get('price')} {v.get('currency', 'EGP')}" if v.get('price') else ""
                            avail = "✓" if v.get('available', True) else "✗"
                            print(f"     {avail} {v.get('name')}{price_info}")
                    
                    if product.get('sizes'):
                        print(f"  📏 Sizes: {', '.join(product['sizes'])}")
                    
                    time.sleep(1)
                
                # Save test results
                print()
                print("="*70)
                print("SAVING TEST RESULTS")
                print("="*70)
                
                # Save only the 3 tested products
                scraper.products = products[:3]
                
                import os
                data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'vetution')
                os.makedirs(data_dir, exist_ok=True)
                
                json_file = os.path.join(data_dir, "variants_test.json")
                csv_file = os.path.join(data_dir, "variants_test.csv")
                
                scraper.save_to_json(json_file)
                scraper.save_to_csv(csv_file)
                
                print()
                print("="*70)
                print("TEST SUMMARY")
                print("="*70)
                print(f"✓ Products tested: 3")
                print(f"✓ Products with prices: {sum(1 for p in scraper.products if p.get('price'))}")
                print(f"✓ Products with vendors: {sum(1 for p in scraper.products if p.get('vendor_prices'))}")
                print(f"✓ Products with variants: {sum(1 for p in scraper.products if p.get('variants'))}")
                print()
                print(f"📁 Results saved to:")
                print(f"   {json_file}")
                print(f"   {csv_file}")
                print("="*70)
            
        else:
            print("✗ Failed to fetch page 1")
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n🔚 Closing browser...")
        scraper.close_browser()
        print("✓ Test complete!")

if __name__ == "__main__":
    test_vetution_variants()

