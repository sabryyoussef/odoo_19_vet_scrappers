#!/usr/bin/env python3
"""
Automated daily update script (for cron/scheduled tasks).
Uses saved browser context to avoid manual login.
"""

import json
import os
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scrapers.vetution_scraper.scraper_playwright import VetutionScraper
from _common import get_products_json, get_products_csv
import time

class AutomatedDailyUpdater:
    def __init__(self, products_file=None, backup_dir="backups", context_dir="browser_context"):
        self.products_file = products_file or get_products_json()
        self.backup_dir = backup_dir
        self.context_dir = context_dir
        self.scraper = VetutionScraper(
            email="vetdrughouse@gmail.com",
            password="Shabab28jan",
            phone="01000059085"
        )
        self.existing_products = {}
        self.stats = {
            'updated': 0,
            'new': 0,
            'unchanged': 0,
            'errors': 0,
            'price_changes': 0,
            'availability_changes': 0
        }
        
        # Create directories
        os.makedirs(backup_dir, exist_ok=True)
        os.makedirs(context_dir, exist_ok=True)
    
    def load_existing_products(self):
        """Load existing products from JSON file"""
        if os.path.exists(self.products_file):
            with open(self.products_file, 'r', encoding='utf-8') as f:
                products = json.load(f)
            for product in products:
                link = product.get('link', '')
                if link:
                    self.existing_products[link] = product
            print(f"Loaded {len(self.existing_products)} existing products")
            return len(self.existing_products)
        return 0
    
    def create_backup(self):
        """Create backup of current products file"""
        if os.path.exists(self.products_file):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_dir, f"products_backup_{timestamp}.json")
            with open(self.products_file, 'r', encoding='utf-8') as f:
                data = f.read()
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(data)
            print(f"Backup created: {backup_file}")
            return backup_file
        return None
    
    def update_product(self, old_product, new_product):
        """Update existing product with new data"""
        updated = False
        
        # Update price information
        if 'price' in new_product:
            old_price = old_product.get('price')
            new_price = new_product.get('price')
            if old_price != new_price:
                old_product['price'] = new_price
                old_product['last_price_update'] = datetime.now().isoformat()
                updated = True
                self.stats['price_changes'] += 1
        
        if 'currency' in new_product:
            old_product['currency'] = new_product['currency']
        
        if 'min_price' in new_product:
            old_product['min_price'] = new_product['min_price']
        
        if 'max_price' in new_product:
            old_product['max_price'] = new_product['max_price']
        
        # Update vendor prices
        if 'vendor_prices' in new_product:
            old_product['vendor_prices'] = new_product['vendor_prices']
            old_product['last_vendor_price_update'] = datetime.now().isoformat()
            updated = True
            
            # Check availability changes
            old_available = any(vp.get('available', False) for vp in old_product.get('vendor_prices', []))
            new_available = any(vp.get('available', False) for vp in new_product['vendor_prices'])
            if old_available != new_available:
                self.stats['availability_changes'] += 1
        
        # Update flags
        if 'express_delivery' in new_product:
            old_product['express_delivery'] = new_product['express_delivery']
        
        if 'cold_chain' in new_product:
            old_product['cold_chain'] = new_product['cold_chain']
        
        if 'review_count' in new_product:
            old_product['review_count'] = new_product['review_count']
        
        if 'total_reviews' in new_product:
            old_product['total_reviews'] = new_product['total_reviews']
        
        old_product['last_updated'] = datetime.now().isoformat()
        
        return updated
    
    def process_product(self, new_product):
        """Process a product: update existing or add new"""
        link = new_product.get('link', '')
        if not link:
            self.stats['errors'] += 1
            return None
        
        if link in self.existing_products:
            old_product = self.existing_products[link]
            updated = self.update_product(old_product, new_product)
            if updated:
                self.stats['updated'] += 1
                return old_product
            else:
                self.stats['unchanged'] += 1
                return old_product
        else:
            new_product['first_seen'] = datetime.now().isoformat()
            new_product['last_updated'] = datetime.now().isoformat()
            self.existing_products[link] = new_product
            self.stats['new'] += 1
            return new_product
    
    def quick_price_update(self, start_page=1, end_page=23):
        """Quick update: prices and availability only"""
        print(f"\n{'='*70}")
        print("AUTOMATED DAILY UPDATE")
        print(f"{'='*70}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Create backup
        self.create_backup()
        
        # Load existing products
        existing_count = self.load_existing_products()
        
        # Start browser with saved context
        print("\nStarting browser...")
        try:
            # Try to use persistent context if available
            from playwright.sync_api import sync_playwright
            playwright = sync_playwright().start()
            
            # Use persistent context to save login state
            context_path = os.path.join(self.context_dir, "browser_context")
            browser = playwright.chromium.launch_persistent_context(
                context_path,
                headless=True,
                viewport={"width": 1920, "height": 1080}
            )
            
            # Check if we have pages (might need login)
            pages = browser.pages
            if pages:
                page = pages[0]
            else:
                page = browser.new_page()
            
            # Navigate and check if logged in
            page.goto("https://www.vetution.com/products?page=1&categories=pharmacy-vaccines", 
                     wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            
            # Check if we can see prices (indicates logged in)
            content = page.content()
            if 'price' in content.lower() or len(content) > 50000:
                print("Session appears to be logged in")
                logged_in = True
            else:
                print("WARNING: May need to login. Check browser context.")
                logged_in = True  # Assume logged in if context exists
            
            # Update scraper's page
            self.scraper.page = page
            self.scraper.browser = browser
            self.scraper.playwright = playwright
            self.scraper.logged_in = logged_in
            
        except Exception as e:
            print(f"Error with persistent context: {e}")
            print("Falling back to regular browser...")
            self.scraper.start_browser(headless=True)
            # Note: For automated runs, you may need to handle login differently
            # or use a pre-authenticated session
        
        # Scrape all pages
        print(f"\nScraping pages {start_page} to {end_page}...")
        all_new_products = []
        
        for page_num in range(start_page, end_page + 1):
            print(f"Page {page_num}...", end=' ')
            html = self.scraper.get_page(page_num)
            
            if html:
                page_products = self.scraper.extract_product_links(html)
                all_new_products.extend(page_products)
                print(f"{len(page_products)} products")
                time.sleep(0.5)
            else:
                print("Failed")
        
        # Update existing products with prices
        print(f"\nUpdating prices for {len(all_new_products)} products...")
        products_to_update = [p for p in all_new_products if p.get('link') in self.existing_products]
        new_products = [p for p in all_new_products if p.get('link') not in self.existing_products]
        
        print(f"  Existing: {len(products_to_update)}, New: {len(new_products)}")
        
        # Update existing products (sample first 50 for speed, or all if needed)
        for i, product in enumerate(products_to_update[:100], 1):  # Limit to 100 for speed
            if i % 20 == 0:
                print(f"  Progress: {i}/{min(len(products_to_update), 100)}")
            
            try:
                details = self.scraper.get_product_details(product.get('link', ''))
                if details:
                    price_details = {
                        'price': details.get('price'),
                        'currency': details.get('currency'),
                        'min_price': details.get('min_price'),
                        'max_price': details.get('max_price'),
                        'vendor_prices': details.get('vendor_prices'),
                        'express_delivery': details.get('express_delivery'),
                        'cold_chain': details.get('cold_chain')
                    }
                    product.update({k: v for k, v in price_details.items() if v is not None})
                
                self.process_product(product)
                time.sleep(0.2)
            except Exception as e:
                print(f"  Error: {e}")
                self.stats['errors'] += 1
        
        # Add new products
        if new_products:
            print(f"\nAdding {len(new_products)} new products...")
            for product in new_products:
                try:
                    details = self.scraper.get_product_details(product.get('link', ''))
                    if details:
                        product.update(details)
                    self.process_product(product)
                    time.sleep(0.2)
                except Exception as e:
                    print(f"  Error: {e}")
                    self.stats['errors'] += 1
        
        # Save updated products
        all_products = list(self.existing_products.values())
        with open(self.products_file, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, indent=2, ensure_ascii=False)
        
        # Update CSV
        self.scraper.products = all_products
        self.scraper.save_to_csv()
        
        # Print summary
        self.print_summary()
        
        # Close browser
        try:
            if hasattr(self.scraper, 'browser') and self.scraper.browser:
                self.scraper.browser.close()
            if hasattr(self.scraper, 'playwright') and self.scraper.playwright:
                self.scraper.playwright.stop()
        except:
            pass
    
    def print_summary(self):
        """Print update summary"""
        print(f"\n{'='*70}")
        print("UPDATE SUMMARY")
        print(f"{'='*70}")
        print(f"Total products: {len(self.existing_products)}")
        print(f"New products: {self.stats['new']}")
        print(f"Updated products: {self.stats['updated']}")
        print(f"Unchanged products: {self.stats['unchanged']}")
        print(f"Price changes: {self.stats['price_changes']}")
        print(f"Availability changes: {self.stats['availability_changes']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")


if __name__ == "__main__":
    updater = AutomatedDailyUpdater()
    updater.quick_price_update(start_page=1, end_page=23)

