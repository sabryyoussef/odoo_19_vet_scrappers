# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
import sys
import os

_logger = logging.getLogger(__name__)


class ScraperConfig(models.Model):
    _name = 'scraper.config'
    _description = 'Web Scraper Configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'
    _rec_name = 'name'

    # Basic Information
    name = fields.Char(
        string='Configuration Name',
        required=True,
        tracking=True,
        help='Name for this scraper configuration'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of configurations in lists'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True,
        help='If unchecked, this configuration will be hidden'
    )
    
    # Scraper Settings
    url = fields.Char(
        string='Target URL',
        required=True,
        tracking=True,
        help='The URL to scrape (e.g., https://example.com/collections/all)'
    )
    platform_type = fields.Selection([
        ('shopify', 'Shopify'),
        ('woocommerce', 'WooCommerce'),
        ('magento', 'Magento'),
        ('odoo', 'Odoo E-commerce'),
        ('amazon', 'Amazon'),
        ('ebay', 'eBay'),
        ('generic', 'Generic/Auto-detect'),
    ], string='Platform Type', default='generic', required=True, tracking=True,
       help='E-commerce platform type (auto-detected if Generic)')
    
    max_pages = fields.Integer(
        string='Max Pages',
        default=3,
        required=True,
        help='Maximum number of pages to scrape'
    )
    fetch_details = fields.Boolean(
        string='Fetch Product Details',
        default=True,
        help='Visit each product page to get full details (slower but more accurate)'
    )
    headless = fields.Boolean(
        string='Headless Mode',
        default=True,
        help='Run browser in background (no visible window)'
    )
    max_workers = fields.Integer(
        string='Batch Size',
        default=5,
        help='Number of products to process in parallel (higher = faster but more resource intensive)'
    )
    
    # Authentication
    requires_login = fields.Boolean(
        string='Requires Login',
        default=False,
        help='Check if the site requires authentication'
    )
    login_email = fields.Char(
        string='Login Email',
        help='Email/username for authentication'
    )
    login_password = fields.Char(
        string='Login Password',
        help='Password for authentication (stored encrypted)'
    )
    manual_login = fields.Boolean(
        string='Manual Login',
        default=False,
        help='If checked, browser will open for manual login'
    )
    
    # Data Source for Unified Scrapper Integration
    data_source_id = fields.Many2one(
        comodel_name='unified.data.source',
        string='Unified Data Source',
        required=True,
        help='The data source in Unified Scrapper to associate scraped products with'
    )
    
    # Scheduling
    enable_cron = fields.Boolean(
        string='Enable Scheduled Scraping',
        default=False,
        tracking=True,
        help='Automatically run this scraper on schedule'
    )
    cron_interval = fields.Selection([
        ('hourly', 'Every Hour'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ], string='Scraping Frequency', default='daily',
       help='How often to run the scraper automatically')
    
    # Statistics
    last_run_date = fields.Datetime(
        string='Last Run',
        readonly=True,
        help='Last time this scraper was executed'
    )
    last_run_status = fields.Selection([
        ('success', 'Success'),
        ('partial', 'Partial Success'),
        ('failed', 'Failed'),
    ], string='Last Status', readonly=True)
    
    total_runs = fields.Integer(
        string='Total Runs',
        compute='_compute_statistics',
        store=True,
        help='Total number of times this scraper has been run'
    )
    total_products_scraped = fields.Integer(
        string='Total Products Scraped',
        compute='_compute_statistics',
        store=True,
        help='Total number of products scraped across all runs'
    )
    draft_count = fields.Integer(
        string='Draft Products',
        compute='_compute_draft_count',
        store=False,  # Not stored to avoid performance issues
        help='Number of scraped products in draft state'
    )
    
    # Relations
    job_ids = fields.One2many(
        comodel_name='scraper.job',
        inverse_name='config_id',
        string='Scraping Jobs',
        help='History of all scraping jobs for this configuration'
    )
    draft_product_ids = fields.One2many(
        comodel_name='scraped.product.draft',
        inverse_name='scraper_config_id',
        string='Draft Products',
        help='Products scraped but not yet imported'
    )
    
    @api.depends('job_ids', 'job_ids.status', 'job_ids.products_scraped')
    def _compute_statistics(self):
        for config in self:
            config.total_runs = len(config.job_ids)
            config.total_products_scraped = sum(config.job_ids.mapped('products_scraped'))
    
    @api.depends('draft_product_ids')
    def _compute_draft_count(self):
        for config in self:
            config.draft_count = len(config.draft_product_ids.filtered(lambda d: d.state == 'draft'))
    
    @api.constrains('max_pages')
    def _check_max_pages(self):
        for config in self:
            if config.max_pages < 1:
                raise ValidationError(_("Max pages must be at least 1"))
    
    @api.constrains('max_workers')
    def _check_max_workers(self):
        for config in self:
            if config.max_workers < 1 or config.max_workers > 20:
                raise ValidationError(_("Batch size must be between 1 and 20"))
    
    def action_run_scraper(self):
        """Run the scraper manually"""
        self.ensure_one()
        
        # Create a scraper job
        job = self.env['scraper.job'].create({
            'config_id': self.id,
            'status': 'running',
            'start_time': fields.Datetime.now(),
        })
        
        try:
            # Import the scraper (from the copied lib folder)
            scraper_path = os.path.join(os.path.dirname(__file__), '..', 'lib', 'unified_scraper')
            if scraper_path not in sys.path:
                sys.path.insert(0, scraper_path)
            
            from unified_scraper import UnifiedScraper
            
            # Initialize scraper
            scraper = UnifiedScraper()
            scraper.max_workers = self.max_workers
            
            # Start browser
            scraper.start_browser(headless=self.headless)
            
            # Handle login if required
            if self.requires_login:
                if self.manual_login:
                    scraper.login(manual=True)
                elif self.login_email and self.login_password:
                    scraper.credentials = {
                        'email': self.login_email,
                        'password': self.login_password
                    }
                    scraper.login(manual=False)
            
            # Run scraper
            _logger.info(f"Starting scraper for: {self.name} ({self.url})")
            products = scraper.scrape(
                url=self.url,
                max_pages=self.max_pages,
                fetch_details=self.fetch_details
            )
            
            # Close browser
            scraper.close_browser()
            
            # Save products to drafts
            products_created = self._save_to_drafts(products, job)
            
            # Update job status
            job.write({
                'status': 'success',
                'end_time': fields.Datetime.now(),
                'products_scraped': products_created,
                'log': f"Successfully scraped {products_created} products",
            })
            
            # Update config statistics
            self.write({
                'last_run_date': fields.Datetime.now(),
                'last_run_status': 'success',
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Scraped %s products successfully!') % products_created,
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            _logger.error(f"Scraper error for {self.name}: {e}", exc_info=True)
            
            # Update job status
            job.write({
                'status': 'failed',
                'end_time': fields.Datetime.now(),
                'log': f"Error: {str(e)}",
            })
            
            # Update config statistics
            self.write({
                'last_run_date': fields.Datetime.now(),
                'last_run_status': 'failed',
            })
            
            raise UserError(_("Scraping failed: %s") % str(e))
    
    def _save_to_drafts(self, products, job):
        """Save scraped products to draft records"""
        Draft = self.env['scraped.product.draft']
        products_created = 0
        
        for product_data in products:
            try:
                # Check if product already exists in drafts (by URL)
                existing_draft = Draft.search([
                    ('url', '=', product_data.get('link')),
                    ('scraper_config_id', '=', self.id),
                    ('state', '=', 'draft'),
                ], limit=1)
                
                if existing_draft:
                    # Update existing draft
                    existing_draft.write({
                        'name': product_data.get('name'),
                        'price': product_data.get('price', 0.0),
                        'currency': product_data.get('currency', 'EGP'),
                        'availability': product_data.get('availability', 'unknown'),
                        'image_url': product_data.get('image_url'),
                        'description': product_data.get('description'),
                        'brand': product_data.get('brand'),
                        'sku': product_data.get('sku'),
                        'category': product_data.get('main_category'),
                        'stock_quantity': product_data.get('stock_quantity'),
                        'raw_data': str(product_data),
                        'last_scraped': fields.Datetime.now(),
                    })
                else:
                    # Create new draft
                    Draft.create({
                        'name': product_data.get('name'),
                        'url': product_data.get('link'),
                        'price': product_data.get('price', 0.0),
                        'currency': product_data.get('currency', 'EGP'),
                        'availability': product_data.get('availability', 'unknown'),
                        'image_url': product_data.get('image_url'),
                        'description': product_data.get('description'),
                        'brand': product_data.get('brand'),
                        'sku': product_data.get('sku'),
                        'category': product_data.get('main_category'),
                        'stock_quantity': product_data.get('stock_quantity'),
                        'raw_data': str(product_data),
                        'scraper_config_id': self.id,
                        'scraper_job_id': job.id,
                        'state': 'draft',
                        'last_scraped': fields.Datetime.now(),
                    })
                    products_created += 1
                    
            except Exception as e:
                _logger.error(f"Error saving product {product_data.get('name')}: {e}")
                continue
        
        return products_created
    
    def action_view_drafts(self):
        """View draft products for this configuration"""
        self.ensure_one()
        return {
            'name': _('Draft Products'),
            'type': 'ir.actions.act_window',
            'res_model': 'scraped.product.draft',
            'view_mode': 'list,form',
            'domain': [('scraper_config_id', '=', self.id), ('state', '=', 'draft')],
            'context': {'default_scraper_config_id': self.id},
        }
    
    def action_view_jobs(self):
        """View scraping jobs for this configuration"""
        self.ensure_one()
        return {
            'name': _('Scraping Jobs'),
            'type': 'ir.actions.act_window',
            'res_model': 'scraper.job',
            'view_mode': 'list,form',
            'domain': [('config_id', '=', self.id)],
            'context': {'default_config_id': self.id},
        }
    
    @api.model
    def _cron_run_scheduled_scrapers(self):
        """Cron job to run scheduled scrapers"""
        _logger.info("Running scheduled scrapers cron job...")
        
        # Find all active configs with cron enabled
        configs = self.search([
            ('active', '=', True),
            ('enable_cron', '=', True),
        ])
        
        for config in configs:
            try:
                # Check if it's time to run based on interval
                should_run = False
                
                if not config.last_run_date:
                    # Never run before, run now
                    should_run = True
                else:
                    # Calculate time since last run
                    from datetime import timedelta
                    now = fields.Datetime.now()
                    time_since_last_run = now - config.last_run_date
                    
                    if config.cron_interval == 'hourly' and time_since_last_run >= timedelta(hours=1):
                        should_run = True
                    elif config.cron_interval == 'daily' and time_since_last_run >= timedelta(days=1):
                        should_run = True
                    elif config.cron_interval == 'weekly' and time_since_last_run >= timedelta(weeks=1):
                        should_run = True
                    elif config.cron_interval == 'monthly' and time_since_last_run >= timedelta(days=30):
                        should_run = True
                
                if should_run:
                    _logger.info(f"Running scheduled scraper: {config.name}")
                    
                    # Create a job with scheduled execution type
                    job = self.env['scraper.job'].create({
                        'config_id': config.id,
                        'status': 'running',
                        'start_time': fields.Datetime.now(),
                        'execution_type': 'scheduled',
                    })
                    
                    try:
                        # Import the scraper
                        scraper_path = os.path.join(os.path.dirname(__file__), '..', 'lib', 'unified_scraper')
                        if scraper_path not in sys.path:
                            sys.path.insert(0, scraper_path)
                        
                        from unified_scraper import UnifiedScraper
                        
                        # Initialize and run scraper
                        scraper = UnifiedScraper()
                        scraper.max_workers = config.max_workers
                        scraper.start_browser(headless=config.headless)
                        
                        # Handle login if required
                        if config.requires_login and config.login_email and config.login_password:
                            scraper.credentials = {
                                'email': config.login_email,
                                'password': config.login_password
                            }
                            scraper.login(manual=False)
                        
                        # Run scraper
                        products = scraper.scrape(
                            url=config.url,
                            max_pages=config.max_pages,
                            fetch_details=config.fetch_details
                        )
                        
                        scraper.close_browser()
                        
                        # Save products to drafts
                        products_created = config._save_to_drafts(products, job)
                        
                        # Update job status
                        job.write({
                            'status': 'success',
                            'end_time': fields.Datetime.now(),
                            'products_scraped': products_created,
                            'log': f"Successfully scraped {products_created} products (scheduled)",
                        })
                        
                        # Update config statistics
                        config.write({
                            'last_run_date': fields.Datetime.now(),
                            'last_run_status': 'success',
                        })
                        
                        _logger.info(f"Scheduled scraper '{config.name}' completed successfully: {products_created} products")
                        
                    except Exception as e:
                        _logger.error(f"Scheduled scraper '{config.name}' failed: {e}", exc_info=True)
                        
                        # Update job status
                        job.write({
                            'status': 'failed',
                            'end_time': fields.Datetime.now(),
                            'log': f"Error: {str(e)}",
                        })
                        
                        # Update config statistics
                        config.write({
                            'last_run_date': fields.Datetime.now(),
                            'last_run_status': 'failed',
                        })
                        
            except Exception as e:
                _logger.error(f"Error processing scheduled scraper '{config.name}': {e}", exc_info=True)
                continue
        
        _logger.info("Scheduled scrapers cron job completed")

