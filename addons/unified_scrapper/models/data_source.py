# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging
import requests
import json

_logger = logging.getLogger(__name__)


class UnifiedDataSource(models.Model):
    """
    Data Source Configuration Model
    
    Defines and manages external data sources that provide product information.
    Supports CSV files, JSON files, and REST API endpoints.
    """
    _name = 'unified.data.source'
    _description = 'External Data Source Configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'
    _rec_name = 'name'

    # Basic Information
    name = fields.Char(
        string='Source Name',
        required=True,
        help='Human-readable name (e.g., "Vetution Products Feed")'
    )
    
    description = fields.Text(
        string='Description',
        help='Description of this data source'
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of display in lists'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Enable/disable this data source'
    )
    
    # Source Configuration
    source_system = fields.Selection(
        selection=[
            ('vetution', 'Vetution'),
            ('amin_petshop', 'Amin Petshop'),
            ('amazon', 'Amazon'),
            ('other', 'Other/Custom'),
        ],
        string='Source System',
        required=True,
        help='System identifier for the external marketplace'
    )
    
    source_type = fields.Selection(
        selection=[
            ('csv', 'CSV File'),
            ('json', 'JSON File'),
            ('api', 'REST API'),
        ],
        string='Source Type',
        required=True,
        default='json',
        help='Data format of the source'
    )
    
    source_url = fields.Char(
        string='Source URL/Path',
        help='URL or file path to data source (e.g., /mnt/data/products.json or https://api.example.com/products)'
    )
    
    # Import Settings
    auto_import = fields.Boolean(
        string='Auto Import',
        default=False,
        help='Enable automatic scheduled imports'
    )
    
    import_frequency = fields.Selection(
        selection=[
            ('manual', 'Manual Only'),
            ('hourly', 'Every Hour'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
        ],
        string='Import Frequency',
        default='manual',
        help='Frequency for automatic imports (requires Auto Import enabled)'
    )
    
    match_strategy = fields.Selection(
        selection=[
            ('url', 'By External URL'),
            ('sku', 'By SKU/Product Code'),
            ('name', 'By Product Name'),
            ('url_sku', 'URL then SKU'),
            ('url_sku_name', 'URL then SKU then Name'),
        ],
        string='Match Strategy',
        default='url_sku_name',
        help='Strategy for matching imported products to existing products'
    )
    
    duplicate_handling = fields.Selection(
        selection=[
            ('skip', 'Skip Duplicates'),
            ('update', 'Update Existing'),
            ('create', 'Create New (Allow Duplicates)'),
        ],
        string='Duplicate Handling',
        default='update',
        help='Action to take when a duplicate product is found'
    )
    
    # Authentication (for API sources)
    authentication_type = fields.Selection(
        selection=[
            ('none', 'None'),
            ('basic', 'Basic Auth'),
            ('token', 'Bearer Token'),
            ('api_key', 'API Key'),
            ('web_login', 'Website Login'),
        ],
        string='Authentication Type',
        default='none',
        help='Authentication method for API sources'
    )
    
    api_key = fields.Char(
        string='API Key/Token',
        help='API authentication key or bearer token'
    )
    
    api_username = fields.Char(
        string='API Username',
        help='Username for basic authentication'
    )
    
    api_password = fields.Char(
        string='API Password',
        help='Password for basic authentication'
    )
    
    # Website Login Credentials
    website_username = fields.Char(
        string='Username/Email/Phone',
        help='Username, email, or phone number for website login'
    )
    
    website_password = fields.Char(
        string='Website Password',
        help='Password for website login'
    )
    
    login_url = fields.Char(
        string='Login URL',
        help='URL of the login page or API endpoint (e.g., https://example.com/login or https://example.com/api/auth/login)'
    )
    
    login_method = fields.Selection(
        selection=[
            ('form', 'Standard Form Login'),
            ('api', 'API/AJAX Login'),
            ('browser', 'Browser Automation (for JS popups)'),
        ],
        string='Login Method',
        default='form',
        help='How the website handles login'
    )
    
    login_cookies = fields.Text(
        string='Session Cookies (JSON)',
        help='Paste cookies from browser as JSON. Format: {"cookie_name": "cookie_value", ...}'
    )
    
    cookie_import_help = fields.Html(
        string='How to Get Cookies',
        compute='_compute_cookie_help',
        help='Instructions for extracting cookies from browser'
    )
    
    api_login_endpoint = fields.Char(
        string='API Login Endpoint',
        help='API endpoint for login (e.g., /api/auth/login, /wp-json/jwt-auth/v1/token)'
    )
    
    username_field_name = fields.Char(
        string='Username Field Name',
        help='Optional: Specify the exact field name for username (e.g., "phone_number", "email"). Leave empty for auto-detection.'
    )
    
    password_field_name = fields.Char(
        string='Password Field Name',
        help='Optional: Specify the exact field name for password. Leave empty for auto-detection.'
    )
    
    login_status = fields.Selection(
        selection=[
            ('not_tested', 'Not Tested'),
            ('success', 'Login Success'),
            ('failed', 'Login Failed'),
        ],
        string='Login Status',
        default='not_tested',
        readonly=True,
        help='Status of last login test'
    )
    
    last_login_test = fields.Datetime(
        string='Last Login Test',
        readonly=True,
        help='Timestamp of last login test'
    )
    
    login_error_message = fields.Text(
        string='Last Login Error',
        readonly=True,
        help='Error message from last login attempt'
    )
    
    # Import Status (readonly)
    last_import_date = fields.Datetime(
        string='Last Import Date',
        readonly=True,
        help='Timestamp of last successful import'
    )
    
    last_import_status = fields.Selection(
        selection=[
            ('success', 'Success'),
            ('failed', 'Failed'),
            ('partial', 'Partial Success'),
            ('never', 'Never Imported'),
        ],
        string='Last Import Status',
        default='never',
        readonly=True,
        help='Status of last import operation'
    )
    
    last_import_log = fields.Text(
        string='Last Import Log',
        readonly=True,
        help='Log of last import operation'
    )
    
    products_created = fields.Integer(
        string='Products Created',
        readonly=True,
        default=0,
        help='Total products created from this source'
    )
    
    products_updated = fields.Integer(
        string='Products Updated',
        readonly=True,
        default=0,
        help='Total products updated from this source'
    )
    
    # Additional Configuration
    notes = fields.Text(
        string='Notes',
        help='Additional configuration notes and documentation'
    )
    
    # Relational Fields
    field_mapping_ids = fields.One2many(
        comodel_name='unified.field.mapping',
        inverse_name='data_source_id',
        string='Field Mappings',
        help='Field mappings for this data source'
    )
    
    import_history_ids = fields.One2many(
        comodel_name='unified.import.history',
        inverse_name='data_source_id',
        string='Import History',
        help='History of all imports from this source'
    )
    
    # Computed Fields
    field_mapping_count = fields.Integer(
        string='Mapping Count',
        compute='_compute_field_mapping_count',
        help='Number of field mappings configured'
    )
    
    import_history_count = fields.Integer(
        string='Import Count',
        compute='_compute_import_history_count',
        help='Number of import operations performed'
    )
    
    connection_status = fields.Selection(
        selection=[
            ('unknown', 'Unknown'),
            ('connected', 'Connected'),
            ('error', 'Connection Error'),
        ],
        string='Connection Status',
        default='unknown',
        help='Current connection status to data source'
    )

    # Compute Methods
    @api.depends('source_url')
    def _compute_cookie_help(self):
        """Provide instructions for cookie extraction"""
        for record in self:
            record.cookie_import_help = f"""
                <div style="padding: 10px; background: #f0f8ff; border-left: 4px solid #2196F3;">
                    <h4>📋 How to Get Cookies from Browser:</h4>
                    <ol>
                        <li><strong>Login</strong> to {record.source_url or 'the website'} in your browser</li>
                        <li>Press <strong>F12</strong> to open Developer Tools</li>
                        <li>Go to <strong>Console</strong> tab</li>
                        <li>Paste this code and press Enter:</li>
                    </ol>
                    <pre style="background: #263238; color: #aed581; padding: 10px; border-radius: 4px; overflow-x: auto;">
copy(JSON.stringify(Object.fromEntries(document.cookie.split('; ').map(c => c.split('=')))))
                    </pre>
                    <p>✅ Cookies are now copied to clipboard!</p>
                    <p>📝 Paste them in the "Session Cookies" field above</p>
                </div>
            """
    
    @api.depends('field_mapping_ids')
    def _compute_field_mapping_count(self):
        """Compute number of field mappings"""
        for record in self:
            record.field_mapping_count = len(record.field_mapping_ids)

    @api.depends('import_history_ids')
    def _compute_import_history_count(self):
        """Compute number of import history records"""
        for record in self:
            record.import_history_count = len(record.import_history_ids)

    # Constraints
    @api.constrains('source_url', 'auto_import')
    def _check_source_url(self):
        """Validate source URL is provided when needed"""
        for record in self:
            # Only require URL if auto_import is enabled
            if record.auto_import and not record.source_url:
                raise ValidationError(_('Source URL/Path is required when Auto Import is enabled'))

    @api.constrains('auto_import', 'import_frequency')
    def _check_auto_import_frequency(self):
        """Validate import frequency when auto import is enabled"""
        for record in self:
            if record.auto_import and record.import_frequency == 'manual':
                raise ValidationError(_('Import Frequency must be set when Auto Import is enabled'))

    # Action Methods
    def action_test_connection(self):
        """
        Test connection to data source
        Validates that the source URL is accessible
        """
        self.ensure_one()
        
        if not self.source_url:
            raise UserError(_('Please configure Source URL/Path before testing connection'))
        
        try:
            import os
            from urllib.parse import urlparse
            
            # Check if it's a URL or file path
            parsed = urlparse(self.source_url)
            is_url = parsed.scheme in ('http', 'https')
            
            if is_url:
                # Test web URL (works for both API and file URLs)
                headers = self._get_api_headers() if self.source_type == 'api' else {
                    'User-Agent': 'Odoo Unified Scrapper/1.0'
                }
                auth = self._get_api_auth() if self.authentication_type == 'basic' else None
                
                response = requests.get(self.source_url, headers=headers, auth=auth, timeout=10)
                
                if response.status_code == 200:
                    self.connection_status = 'connected'
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('Connection Successful'),
                            'message': _('Successfully connected to: %s\nStatus: %s') % (self.source_url, response.status_code),
                            'type': 'success',
                            'sticky': False,
                        }
                    }
                elif response.status_code in (301, 302, 307, 308):
                    self.connection_status = 'connected'
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('Connection Successful (Redirect)'),
                            'message': _('URL is accessible but redirects (Status: %s)') % response.status_code,
                            'type': 'warning',
                            'sticky': False,
                        }
                    }
                else:
                    self.connection_status = 'error'
                    raise UserError(_('Server returned status code: %s') % response.status_code)
                    
            else:
                # Test local file path
                if os.path.exists(self.source_url):
                    self.connection_status = 'connected'
                    file_size = os.path.getsize(self.source_url)
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('File Found'),
                            'message': _('File exists and is accessible\nPath: %s\nSize: %s bytes') % (self.source_url, file_size),
                            'type': 'success',
                            'sticky': False,
                        }
                    }
                else:
                    self.connection_status = 'error'
                    raise UserError(_('File not found: %s') % self.source_url)
                    
        except requests.exceptions.RequestException as e:
            self.connection_status = 'error'
            _logger.error(f"Connection test failed for {self.name}: {str(e)}")
            raise UserError(_('Connection failed: %s') % str(e))
        except Exception as e:
            self.connection_status = 'error'
            _logger.error(f"Connection test failed for {self.name}: {str(e)}")
            raise UserError(_('Connection test failed: %s') % str(e))

    def action_import_now(self):
        """
        Trigger manual import from this data source
        Opens the import wizard with this source pre-selected
        """
        self.ensure_one()
        
        # TODO: This will be implemented in Phase 3 (Import Engine)
        # For now, just show a notification
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Import Not Yet Implemented'),
                'message': _('Import functionality will be available in Phase 3'),
                'type': 'warning',
                'sticky': False,
            }
        }

    def action_test_login(self):
        """
        Test website login credentials
        Attempts to login to the website using provided credentials
        """
        self.ensure_one()
        
        if not self.website_username or not self.website_password:
            raise UserError(_('Please provide both username and password for login test'))
        
        try:
            import requests
            from bs4 import BeautifulSoup
            import json
            
            # Create a session to maintain cookies
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
            })
            
            # Handle different login methods
            if self.login_method == 'browser':
                # Browser automation (for JavaScript popups/modals)
                return self._test_browser_login()
            elif self.login_method == 'api' or self.api_login_endpoint:
                # API/AJAX Login (for popup/modal logins)
                return self._test_api_login(session)
            else:
                # Standard form login
                return self._test_form_login(session)
                
        except requests.exceptions.RequestException as e:
            self.login_status = 'failed'
            self.last_login_test = fields.Datetime.now()
            _logger.error(f"Login test failed for {self.name}: {str(e)}")
            raise UserError(_('Connection failed: %s') % str(e))
        except Exception as e:
            self.login_status = 'failed'
            self.last_login_test = fields.Datetime.now()
            _logger.error(f"Login test failed for {self.name}: {str(e)}")
            raise UserError(_('Login test failed: %s') % str(e))

    def _test_api_login(self, session):
        """Test API-based login (AJAX/JSON)"""
        import json
        
        # Determine the API endpoint
        api_endpoint = self.api_login_endpoint or self.login_url
        if not api_endpoint.startswith('http'):
            # Relative URL, combine with source_url
            from urllib.parse import urljoin
            api_endpoint = urljoin(self.source_url, api_endpoint)
        
        # Prepare login data for API
        login_data = {}
        
        if self.username_field_name and self.password_field_name:
            login_data[self.username_field_name] = self.website_username
            login_data[self.password_field_name] = self.website_password
        else:
            # Common API field names
            login_data = {
                'username': self.website_username,
                'password': self.website_password,
                'phone': self.website_username,
                'phone_number': self.website_username,
                'email': self.website_username,
            }
        
        # Try to get CSRF token from main page first
        try:
            main_page = session.get(self.source_url, timeout=10)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(main_page.content, 'html.parser')
            
            # Look for CSRF token in meta tags or hidden inputs
            csrf_meta = soup.find('meta', {'name': ['csrf-token', '_token']})
            if csrf_meta:
                csrf_token = csrf_meta.get('content')
                session.headers['X-CSRF-TOKEN'] = csrf_token
                _logger.info(f"Found CSRF token in meta tag")
        except Exception as e:
            _logger.warning(f"Could not get CSRF token: {str(e)}")
        
        # Set headers for JSON request
        session.headers.update({
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        })
        
        _logger.info(f"Attempting API login to: {api_endpoint}")
        _logger.info(f"Login data keys: {list(login_data.keys())}")
        
        # Attempt API login
        response = session.post(api_endpoint, json=login_data, timeout=10)
        
        _logger.info(f"API Response Status: {response.status_code}")
        _logger.info(f"API Response: {response.text[:500]}")
        
        # Update login status
        self.last_login_test = fields.Datetime.now()
        
        # Check response
        if response.status_code in (200, 201):
            try:
                response_data = response.json()
                # Common success indicators in API responses
                if (response_data.get('success') or 
                    response_data.get('token') or 
                    response_data.get('access_token') or
                    response_data.get('user') or
                    'error' not in response_data):
                    
                    self.login_status = 'success'
                    self.login_error_message = False
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('Login Successful! ✅'),
                            'message': _('API login successful to %s\nUsername: %s\nResponse: %s') % (
                                self.name, self.website_username, str(response_data)[:200]
                            ),
                            'type': 'success',
                            'sticky': False,
                        }
                    }
            except:
                pass
        
        # Login failed
        self.login_status = 'failed'
        error_msg = f"API login failed.\nEndpoint: {api_endpoint}\nStatus: {response.status_code}\nResponse: {response.text[:300]}"
        self.login_error_message = error_msg
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Login Failed ❌'),
                'message': _('API login failed.\n%s') % error_msg,
                'type': 'warning',
                'sticky': True,
            }
        }

    def _test_browser_login(self):
        """Test login using browser automation (Playwright)"""
        import asyncio
        import json
        
        async def do_browser_login():
            try:
                from playwright.async_api import async_playwright
            except ImportError:
                raise UserError(_('Playwright is not installed. Please install it first.'))
            
            async with async_playwright() as p:
                # Launch browser with proper options for Docker
                _logger.info(f"Launching browser for {self.name}")
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--disable-gpu',
                        '--window-size=1920x1080',
                    ]
                )
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                page = await context.new_page()
                
                try:
                    # Navigate to website
                    _logger.info(f"Navigating to {self.source_url}")
                    await page.goto(self.source_url, wait_until='domcontentloaded', timeout=60000)
                    await page.wait_for_timeout(3000)
                    
                    # Click login button
                    _logger.info("Looking for login button...")
                    login_clicked = False
                    login_selectors = [
                        'text="Log in"',
                        'text="Login"',
                        'text="Sign in"',
                        'button:has-text("Log")',
                        'a:has-text("Log")',
                    ]
                    
                    for selector in login_selectors:
                        try:
                            await page.click(selector, timeout=3000)
                            login_clicked = True
                            _logger.info(f"Clicked login button: {selector}")
                            break
                        except:
                            continue
                    
                    if not login_clicked:
                        raise Exception("Could not find login button")
                    
                    # Wait for login form
                    await page.wait_for_timeout(2000)
                    
                    # Fill username/phone
                    _logger.info("Filling username/phone...")
                    username_filled = False
                    username_selectors = [
                        'input[type="text"]:visible',
                        'input[type="tel"]:visible',
                        'input[name*="phone"]:visible',
                        'input[name*="user"]:visible',
                    ]
                    
                    for selector in username_selectors:
                        try:
                            await page.click(selector, timeout=2000)
                            await page.keyboard.type(self.website_username, delay=50)
                            username_filled = True
                            _logger.info(f"Filled username: {selector}")
                            break
                        except:
                            continue
                    
                    if not username_filled:
                        raise Exception("Could not fill username field")
                    
                    # Fill password
                    _logger.info("Filling password...")
                    await page.click('input[type="password"]:visible')
                    await page.keyboard.type(self.website_password, delay=50)
                    
                    # Click submit
                    _logger.info("Clicking submit...")
                    submit_clicked = False
                    submit_selectors = [
                        'button[type="submit"]:visible',
                        'button:has-text("Log"):visible',
                        'button:has-text("Sign"):visible',
                        'input[type="submit"]:visible',
                    ]
                    
                    for selector in submit_selectors:
                        try:
                            await page.click(selector, timeout=2000)
                            submit_clicked = True
                            _logger.info(f"Clicked submit: {selector}")
                            break
                        except:
                            continue
                    
                    if not submit_clicked:
                        # Try pressing Enter
                        await page.keyboard.press('Enter')
                    
                    # Wait for response
                    await page.wait_for_timeout(5000)
                    
                    # Check if logged in
                    current_url = page.url
                    content = await page.content()
                    
                    success_indicators = [
                        'account' in current_url.lower(),
                        'profile' in current_url.lower(),
                        'logout' in content.lower(),
                        'sign out' in content.lower(),
                    ]
                    
                    if any(success_indicators):
                        # Get cookies
                        cookies = await context.cookies()
                        cookie_dict = {c['name']: c['value'] for c in cookies}
                        
                        # Store cookies
                        self.login_cookies = json.dumps(cookie_dict)
                        self.login_status = 'success'
                        self.last_login_test = fields.Datetime.now()
                        self.login_error_message = False
                        
                        await browser.close()
                        
                        return {
                            'success': True,
                            'message': f'Login successful!\nURL: {current_url}\nCookies: {len(cookies)} stored',
                            'cookies': len(cookies)
                        }
                    else:
                        await browser.close()
                        raise Exception(f"Login verification failed. URL: {current_url}")
                        
                except Exception as e:
                    _logger.error(f"Browser login error: {str(e)}")
                    try:
                        await browser.close()
                    except:
                        pass
                    raise e
                finally:
                    # Ensure browser is closed
                    try:
                        if browser and browser.is_connected():
                            await browser.close()
                    except:
                        pass
        
        # Run async function
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(do_browser_login())
            loop.close()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Login Successful! ✅'),
                    'message': _(result['message']),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            self.login_status = 'failed'
            self.last_login_test = fields.Datetime.now()
            error_msg = str(e)
            self.login_error_message = error_msg
            _logger.error(f"Browser login failed for {self.name}: {error_msg}")
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Login Failed ❌'),
                    'message': _('Browser login failed:\n%s') % error_msg,
                    'type': 'warning',
                    'sticky': True,
                }
            }

    def _test_form_login(self, session):
        """Test standard form-based login"""
        from bs4 import BeautifulSoup
        
        if not self.login_url:
            raise UserError(_('Please provide the login URL'))
        
        # Get the login page first to extract CSRF tokens if needed
        login_page = session.get(self.login_url, timeout=10)
        
        if login_page.status_code != 200:
            raise UserError(_('Cannot access login page. Status: %s\n\nTip: Try using "API/AJAX Login" method instead.') % login_page.status_code)
            
            # Try to find common login form fields
            soup = BeautifulSoup(login_page.content, 'html.parser')
            login_form = soup.find('form')
            
            # Prepare login data - start empty
            login_data = {}
            
            # If custom field names are specified, use them directly
            if self.username_field_name and self.password_field_name:
                login_data[self.username_field_name] = self.website_username
                login_data[self.password_field_name] = self.website_password
                _logger.info(f"Using custom field names: {self.username_field_name}, {self.password_field_name}")
            else:
                # Auto-detect form fields
                # Find all input fields in the form
                if login_form:
                    all_inputs = login_form.find_all('input')
                else:
                    all_inputs = soup.find_all('input')
                
                # Map common field names to our credentials
                username_field_names = [
                    'username', 'user', 'email', 'login', 'user_login', 
                    'phone', 'phone_number', 'mobile', 'tel', 'telephone',
                    'account', 'user_email', 'user_name', 'phonenumber'
                ]
                password_field_names = [
                    'password', 'pass', 'pwd', 'user_password', 'user_pass'
                ]
                
                username_found = False
                password_found = False
                
                # Auto-detect and fill form fields
                for input_field in all_inputs:
                    field_name = input_field.get('name', '')
                    field_name_lower = field_name.lower()
                    field_type = input_field.get('type', '').lower()
                    field_placeholder = input_field.get('placeholder', '').lower()
                    field_id = input_field.get('id', '').lower()
                    
                    # Check if it's a username/phone field
                    if not username_found and any(name in field_name_lower or name in field_id or name in field_placeholder 
                           for name in username_field_names):
                        login_data[field_name] = self.website_username
                        username_found = True
                        _logger.info(f"Found username field: {field_name}")
                    
                    # Check if it's a password field
                    elif not password_found and (field_type == 'password' or any(name in field_name_lower or name in field_id 
                                                          for name in password_field_names)):
                        login_data[field_name] = self.website_password
                        password_found = True
                        _logger.info(f"Found password field: {field_name}")
                    
                    # Check for CSRF tokens
                    elif field_type == 'hidden' and any(token in field_name_lower 
                                                         for token in ['csrf', 'token', '_token', 'authenticity']):
                        token_value = input_field.get('value')
                        if token_value:
                            login_data[field_name] = token_value
                            _logger.info(f"Found CSRF token: {field_name}")
                    
                    # Include other hidden fields (may be required)
                    elif field_type == 'hidden' and input_field.get('value'):
                        login_data[field_name] = input_field.get('value')
                
                # Fallback: if no fields detected, use common names
                if not username_found or not password_found:
                    login_data.update({
                        'username': self.website_username,
                        'email': self.website_username,
                        'phone': self.website_username,
                        'phone_number': self.website_username,
                        'password': self.website_password,
                    })
                    _logger.warning("Could not auto-detect all fields, using fallback field names")
            
            _logger.info(f"Login data fields: {list(login_data.keys())}")
            
            # Attempt login
            response = session.post(self.login_url, data=login_data, timeout=10, allow_redirects=True)
            
            # Check if login was successful
            # Common indicators: redirect to dashboard, presence of logout button, absence of error messages
            success_indicators = [
                'logout' in response.text.lower(),
                'sign out' in response.text.lower(),
                'dashboard' in response.url.lower(),
                'account' in response.url.lower(),
                response.url != self.login_url,  # Redirected away from login page
            ]
            
            error_indicators = [
                'invalid' in response.text.lower(),
                'incorrect' in response.text.lower(),
                'wrong password' in response.text.lower(),
                'authentication failed' in response.text.lower(),
            ]
            
            # Update login status
            self.last_login_test = fields.Datetime.now()
            
            if any(success_indicators) and not any(error_indicators):
                self.login_status = 'success'
                self.login_error_message = False
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Login Successful! ✅'),
                        'message': _('Successfully logged in to %s\nUsername: %s\nRedirected to: %s') % (
                            self.name, self.website_username, response.url
                        ),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                self.login_status = 'failed'
                error_msg = f"Login verification failed.\nFinal URL: {response.url}\nStatus: {response.status_code}"
                if any(error_indicators):
                    error_msg += "\nError indicators found in response."
                self.login_error_message = error_msg
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Login Failed ❌'),
                        'message': _('Could not verify successful login.\n%s\n\nTip: Try specifying field names manually.') % error_msg,
                        'type': 'warning',
                        'sticky': True,
                    }
                }

    def action_view_import_history(self):
        """View import history for this data source"""
        self.ensure_one()
        
        return {
            'name': _('Import History: %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'unified.import.history',
            'view_mode': 'list,form',
            'domain': [('data_source_id', '=', self.id)],
            'context': {'default_data_source_id': self.id},
        }

    def action_view_field_mappings(self):
        """View field mappings for this data source"""
        self.ensure_one()
        
        return {
            'name': _('Field Mappings: %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'unified.field.mapping',
            'view_mode': 'list,form',
            'domain': [('data_source_id', '=', self.id)],
            'context': {'default_data_source_id': self.id},
        }

    def action_view_products(self):
        """View products imported from this data source"""
        self.ensure_one()
        
        return {
            'name': _('Products from: %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'view_mode': 'list,form',
            'domain': [('external_source', '=', self.source_system)],
            'context': {'search_default_external_source': self.source_system},
        }

    # Helper Methods
    def _get_api_headers(self):
        """
        Build HTTP headers for API authentication
        Returns dict of headers based on authentication type
        """
        self.ensure_one()
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        
        if self.authentication_type == 'token':
            headers['Authorization'] = f'Bearer {self.api_key}'
        elif self.authentication_type == 'api_key':
            headers['X-API-Key'] = self.api_key
        
        return headers

    def _get_api_auth(self):
        """
        Get authentication tuple for requests library
        Returns (username, password) for basic auth, or None
        """
        self.ensure_one()
        
        if self.authentication_type == 'basic':
            return (self.api_username, self.api_password)
        return None

    # Scheduled Actions (for auto-import)
    @api.model
    def cron_auto_import(self):
        """
        Scheduled action to run auto-imports
        Called by cron job to import from sources with auto_import=True
        """
        sources = self.search([
            ('active', '=', True),
            ('auto_import', '=', True),
            ('import_frequency', '!=', 'manual'),
        ])
        
        for source in sources:
            try:
                # Check if import is due based on frequency
                if source._is_import_due():
                    _logger.info(f"Auto-importing from source: {source.name}")
                    # TODO: Call import engine (Phase 3)
                    # source.action_import_now()
            except Exception as e:
                _logger.error(f"Auto-import failed for {source.name}: {str(e)}")

    def _is_import_due(self):
        """
        Check if import is due based on frequency and last import date
        Returns True if import should run now
        """
        self.ensure_one()
        
        if not self.last_import_date:
            return True
        
        from datetime import datetime, timedelta
        now = fields.Datetime.now()
        
        if self.import_frequency == 'hourly':
            return (now - self.last_import_date) >= timedelta(hours=1)
        elif self.import_frequency == 'daily':
            return (now - self.last_import_date) >= timedelta(days=1)
        elif self.import_frequency == 'weekly':
            return (now - self.last_import_date) >= timedelta(weeks=1)
        
        return False

