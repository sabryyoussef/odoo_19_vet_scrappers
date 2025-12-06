#!/usr/bin/env python3
"""
Simple script to scrape products with manual login for price extraction.
Run this and login when the browser opens.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scrapers.vetution_scraper.scraper_playwright import VetutionScraper

if __name__ == "__main__":
    print("="*70)
    print("VETUTION PRODUCT SCRAPER - MANUAL LOGIN MODE")
    print("="*70)
    print("\nThis script will:")
    print("1. Open a browser window")
    print("2. Wait for you to manually login")
    print("3. Scrape all products with prices")
    print("\n" + "="*70)
    
    # Initialize scraper with credentials (for reference, but we'll login manually)
    scraper = VetutionScraper(
        email="vetdrughouse@gmail.com",
        password="Shabab28jan",
        phone="01000059085"
    )
    
    # Start browser in non-headless mode
    print("\nOpening browser...")
    scraper.start_browser(headless=False)
    
    # Navigate to homepage first
    print("\nNavigating to homepage...")
    import time
    try:
        scraper.page.goto("https://www.vetution.com", wait_until="domcontentloaded", timeout=30000)
        print("Waiting for page to load...")
        time.sleep(5)  # Give more time for JavaScript to load
        
        # Check if page loaded
        page_title = scraper.page.title()
        page_url = scraper.page.url
        print(f"Page loaded: {page_title}")
        print(f"Current URL: {page_url}")
        
        # Check if page has content
        try:
            body_text = scraper.page.inner_text('body', timeout=5000)
            if not body_text or len(body_text) < 50:
                print("WARNING: Page appears to be blank or still loading.")
                print("Waiting additional 5 seconds...")
                time.sleep(5)
        except:
            print("Waiting for page content to load...")
            time.sleep(5)
        
        # Look for login link or user icon
        print("\nLooking for login option...")
        login_found = False
        
        # Try to find and click login/user icon
        login_selectors = [
            'a[href*="login"]',
            'a[href*="signin"]',
            'button:has-text("Login")',
            'a:has-text("Login")',
            '[class*="user"]',
            '[class*="profile"]',
            '[class*="account"]'
        ]
        
        for selector in login_selectors:
            try:
                element = scraper.page.query_selector(selector)
                if element:
                    print(f"Found login element, clicking...")
                    element.click()
                    time.sleep(2)
                    login_found = True
                    break
            except:
                continue
        
        if not login_found:
            print("Could not find login link automatically.")
            print("Please look for a 'Login' button or user icon in the browser and click it.")
        
    except Exception as e:
        print(f"Error navigating: {e}")
        print("\nIf the page is blank, please:")
        print("1. Check your internet connection")
        print("2. Manually navigate to https://www.vetution.com in the browser")
        print("3. Wait for the page to fully load")
    
    print("\n" + "="*70)
    print("MANUAL LOGIN INSTRUCTIONS")
    print("="*70)
    print("If the browser shows a blank page:")
    print("  1. Wait a few seconds for it to load")
    print("  2. Or manually type: https://www.vetution.com in the address bar")
    print("  3. Press Enter to load the page")
    print("\nOnce the website loads, please login using:")
    print("  - Email: vetdrughouse@gmail.com")
    print("  - OR Phone: 01000059085")
    print("  - Password: Shabab28jan")
    print("\nAfter logging in, navigate to the products page:")
    print("  https://www.vetution.com/products?page=1&categories=pharmacy-vaccines")
    print("\nMake sure you can see products and prices on the page.")
    print("Then come back here and press Enter to start scraping...")
    input()
    
    scraper.logged_in = True
    
    # Test with page 1 first
    print("\n" + "="*70)
    print("Testing extraction on page 1...")
    print("="*70)
    
    # Make sure we're on the products page
    try:
        current_url = scraper.page.url
        if "/products" not in current_url:
            print("Navigating to products page...")
            scraper.page.goto("https://www.vetution.com/products?page=1&categories=pharmacy-vaccines", 
                            wait_until="domcontentloaded", timeout=30000)
            import time
            time.sleep(3)
    except:
        pass
    
    test_html = scraper.get_page(1)
    
    if test_html:
        test_products = scraper.extract_product_links(test_html)
        with_prices = sum(1 for p in test_products if 'price' in p)
        
        print(f"\nFound {len(test_products)} products on test page")
        print(f"Products with prices: {with_prices}/{len(test_products)}")
        
        if test_products:
            print("\nSample products:")
            for product in test_products[:3]:
                price_info = ""
                if 'price' in product:
                    price_info = f" - {product['price']} {product.get('currency', 'EGP')}"
                print(f"  - {product['name']}{price_info}")
            
            if with_prices > len(test_products) * 0.5:  # More than 50% have prices
                print("\n" + "="*70)
                print("Great! Prices are being extracted. Starting full scrape...")
                print("="*70 + "\n")
                
                # Ask user if they want detailed information
                print("\n" + "="*70)
                print("DETAILED INFORMATION OPTION")
                print("="*70)
                print("Do you want to scrape detailed information from each product page?")
                print("This includes:")
                print("  - Product images")
                print("  - All vendor prices with expiration dates")
                print("  - Detailed sections (Composition, Indications, etc.)")
                print("  - Tags and species")
                print("  - Reviews")
                print("\nNote: This will take longer (visiting each product page)")
                print("Enter 'y' for yes, or press Enter to skip:")
                fetch_details = input().strip().lower() == 'y'
                
                # Run full scrape (browser is already started, so pass manual_login=True to skip browser start)
                scraper.scrape_all_pages(start_page=1, end_page=23, manual_login=True, fetch_details=fetch_details)
                scraper.save_to_json()
                scraper.save_to_csv()
                
                # Final statistics
                print("\n" + "="*70)
                print("SCRAPING COMPLETE!")
                print("="*70)
                total = len(scraper.products)
                with_prices_final = sum(1 for p in scraper.products if 'price' in p)
                print(f"Total products: {total}")
                print(f"Products with prices: {with_prices_final}/{total} ({with_prices_final/total*100:.1f}%)")
                if with_prices_final > 0:
                    prices = [p['price'] for p in scraper.products if 'price' in p]
                    print(f"Price range: {min(prices)} - {max(prices)} {scraper.products[0].get('currency', 'EGP')}")
            else:
                print("\n" + "="*70)
                print("WARNING: Not many prices found.")
                print("="*70)
                print("Make sure you're logged in and can see prices on the website.")
                print("You can try running the script again.")
        else:
            print("No products found. Please check if you're on the products page.")
    else:
        print("Failed to fetch products page.")
    
    # Don't close browser here - let the user see the results
    # Or close it if you want
    print("\nPress Enter to close the browser...")
    input()
    scraper.close_browser()
    print("\nDone!")

