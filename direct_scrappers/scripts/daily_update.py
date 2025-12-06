#!/usr/bin/env python3
"""
Daily update script for Vetution products.
Updates prices, availability, and adds new products.
Optimized to only update what's changed.
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

class DailyUpdater:
    def __init__(self, products_file=None, backup_dir="backups"):
        self.products_file = products_file or get_products_json()
        self.backup_dir = backup_dir
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
        
        # Create backup directory
        os.makedirs(backup_dir, exist_ok=True)
    
    def load_existing_products(self):
        """Load existing products from JSON file"""
        if os.path.exists(self.products_file):
            with open(self.products_file, 'r', encoding='utf-8') as f:
                products = json.load(f)
            # Index by link for quick lookup
            for product in products:
                link = product.get('link', '')
                if link:
                    self.existing_products[link] = product
            print(f"Loaded {len(self.existing_products)} existing products")
            return len(self.existing_products)
        else:
            print("No existing products file found. Will create new one.")
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
            print(f"Created backup: {backup_file}")
            return backup_file
        return None
    
    def compare_prices(self, old_product, new_product):
        """Compare prices and return True if changed"""
        old_price = old_product.get('price')
        new_price = new_product.get('price')
        
        if old_price != new_price:
            return True
        
        # Compare vendor prices
        old_vendor_prices = old_product.get('vendor_prices', [])
        new_vendor_prices = new_product.get('vendor_prices', [])
        
        if len(old_vendor_prices) != len(new_vendor_prices):
            return True
        
        # Compare each vendor price
        for old_vp in old_vendor_prices:
            matching = False
            for new_vp in new_vendor_prices:
                if (old_vp.get('price') == new_vp.get('price') and
                    old_vp.get('expiration_date') == new_vp.get('expiration_date') and
                    old_vp.get('available') == new_vp.get('available')):
                    matching = True
                    break
            if not matching:
                return True
        
        return False
    
    def update_product(self, old_product, new_product):
        """Update existing product with new data, focusing on prices and availability"""
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
        
        # Update vendor prices (most important for availability)
        if 'vendor_prices' in new_product:
            old_product['vendor_prices'] = new_product['vendor_prices']
            old_product['last_vendor_price_update'] = datetime.now().isoformat()
            updated = True
            
            # Check if availability changed
            old_available = any(vp.get('available', False) for vp in old_product.get('vendor_prices', []))
            new_available = any(vp.get('available', False) for vp in new_product['vendor_prices'])
            if old_available != new_available:
                self.stats['availability_changes'] += 1
        
        # Update availability flags
        if 'express_delivery' in new_product:
            old_product['express_delivery'] = new_product['express_delivery']
        
        if 'cold_chain' in new_product:
            old_product['cold_chain'] = new_product['cold_chain']
        
        # Update review count (might change)
        if 'review_count' in new_product:
            old_product['review_count'] = new_product['review_count']
        
        if 'total_reviews' in new_product:
            old_product['total_reviews'] = new_product['total_reviews']
        
        # Update last update timestamp
        old_product['last_updated'] = datetime.now().isoformat()
        
        return updated
    
    def process_product(self, new_product):
        """Process a product: update existing or add new"""
        link = new_product.get('link', '')
        if not link:
            self.stats['errors'] += 1
            return None
        
        if link in self.existing_products:
            # Update existing product
            old_product = self.existing_products[link]
            updated = self.update_product(old_product, new_product)
            if updated:
                self.stats['updated'] += 1
                return old_product
            else:
                self.stats['unchanged'] += 1
                return old_product
        else:
            # New product
            new_product['first_seen'] = datetime.now().isoformat()
            new_product['last_updated'] = datetime.now().isoformat()
            self.existing_products[link] = new_product
            self.stats['new'] += 1
            return new_product
    
    def update_all_products(self, start_page=1, end_page=23, fetch_details=True):
        """Update all products from website"""
        print("\n" + "="*70)
        print("STARTING DAILY UPDATE")
        print("="*70)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Create backup first
        self.create_backup()
        
        # Load existing products
        existing_count = self.load_existing_products()
        
        # Start browser and login
        print("\nOpening browser and logging in...")
        self.scraper.start_browser(headless=False)
        print("Please login to the website in the browser window.")
        print("After logging in, press Enter to continue...")
        input()
        self.scraper.logged_in = True
        
        # Scrape all pages
        print(f"\nScraping pages {start_page} to {end_page}...")
        all_new_products = []
        
        for page_num in range(start_page, end_page + 1):
            print(f"\nPage {page_num}...")
            html = self.scraper.get_page(page_num)
            
            if html:
                page_products = self.scraper.extract_product_links(html)
                print(f"  Found {len(page_products)} products")
                
                # If fetch_details is True, get detailed info for each product
                if fetch_details:
                    print(f"  Fetching detailed information...")
                    for i, product in enumerate(page_products, 1):
                        print(f"    [{i}/{len(page_products)}] {product.get('name', 'Unknown')}")
                        details = self.scraper.get_product_details(product.get('link', ''))
                        if details:
                            product.update(details)
                        time.sleep(0.3)  # Small delay between requests
                
                all_new_products.extend(page_products)
                time.sleep(1)
            else:
                print(f"  Failed to fetch page {page_num}")
        
        # Process all products
        print(f"\nProcessing {len(all_new_products)} products...")
        for product in all_new_products:
            try:
                self.process_product(product)
            except Exception as e:
                print(f"  Error processing {product.get('name', 'Unknown')}: {e}")
                self.stats['errors'] += 1
        
        # Save updated products
        all_products = list(self.existing_products.values())
        with open(self.products_file, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, indent=2, ensure_ascii=False)
        
        # Also update CSV
        self.scraper.products = all_products
        self.scraper.save_to_csv()
        
        # Print summary
        self.print_summary()
        
        self.scraper.close_browser()
    
    def quick_price_update(self, start_page=1, end_page=23):
        """Quick update: only prices and availability, no detailed info"""
        print("\n" + "="*70)
        print("QUICK PRICE UPDATE")
        print("="*70)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Create backup
        self.create_backup()
        
        # Load existing products
        existing_count = self.load_existing_products()
        
        # Start browser and login
        print("\nOpening browser...")
        self.scraper.start_browser(headless=False)
        print("Please login to the website.")
        print("After logging in, press Enter to continue...")
        input()
        self.scraper.logged_in = True
        
        # Scrape all pages (without detailed info for speed)
        print(f"\nScraping pages {start_page} to {end_page} (quick mode)...")
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
        
        # For products that exist, get detailed prices
        print(f"\nUpdating prices for existing products...")
        products_to_update = [p for p in all_new_products if p.get('link') in self.existing_products]
        print(f"Found {len(products_to_update)} existing products to check")
        
        for i, product in enumerate(products_to_update, 1):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(products_to_update)}")
            
            try:
                # Get detailed info only for price/availability
                details = self.scraper.get_product_details(product.get('link', ''))
                if details:
                    # Only keep price-related fields
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
                time.sleep(0.3)
            except Exception as e:
                print(f"  Error: {e}")
                self.stats['errors'] += 1
        
        # Process new products (add them)
        new_products = [p for p in all_new_products if p.get('link') not in self.existing_products]
        if new_products:
            print(f"\nFound {len(new_products)} new products. Getting full details...")
            for product in new_products:
                try:
                    details = self.scraper.get_product_details(product.get('link', ''))
                    if details:
                        product.update(details)
                    self.process_product(product)
                    time.sleep(0.3)
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
        
        self.scraper.close_browser()
    
    def print_summary(self):
        """Print update summary"""
        print("\n" + "="*70)
        print("UPDATE SUMMARY")
        print("="*70)
        print(f"Total products: {len(self.existing_products)}")
        print(f"New products: {self.stats['new']}")
        print(f"Updated products: {self.stats['updated']}")
        print(f"Unchanged products: {self.stats['unchanged']}")
        print(f"Price changes: {self.stats['price_changes']}")
        print(f"Availability changes: {self.stats['availability_changes']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"\nUpdate completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)


if __name__ == "__main__":
    import sys
    
    updater = DailyUpdater()
    
    print("="*70)
    print("VETUTION DAILY UPDATE SCRIPT")
    print("="*70)
    print("\nChoose update mode:")
    print("1. Quick Update (prices and availability only - faster)")
    print("2. Full Update (all fields including detailed sections - slower)")
    print("\nEnter choice (1 or 2): ", end='')
    
    choice = input().strip()
    
    if choice == '1':
        updater.quick_price_update(start_page=1, end_page=23)
    elif choice == '2':
        updater.update_all_products(start_page=1, end_page=23, fetch_details=True)
    else:
        print("Invalid choice. Running quick update by default.")
        updater.quick_price_update(start_page=1, end_page=23)

