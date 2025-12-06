# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AminPetshopUpdateWizard(models.TransientModel):
    _name = 'amin.petshop.update.wizard'
    _description = 'Amin Petshop Update Wizard'

    product_ids = fields.Many2many(
        'product.product',
        string='Products',
        required=True,
        help='Products to update from Amin Petshop'
    )

    update_mode = fields.Selection([
        ('quick', 'Quick Update (Prices & Availability Only)'),
        ('full', 'Full Update (All Fields)'),
    ], string='Update Mode', default='quick', required=True)

    # Results
    products_updated = fields.Integer(string='Products Updated', readonly=True)
    price_changes = fields.Integer(string='Price Changes', readonly=True)
    errors = fields.Integer(string='Errors', readonly=True)
    log_message = fields.Text(string='Update Log', readonly=True)

    def action_update(self):
        """Update products from Amin Petshop"""
        self.ensure_one()

        if not self.product_ids:
            raise UserError(_('Please select at least one product to update.'))

        self.products_updated = 0
        self.price_changes = 0
        self.errors = 0
        log_messages = []

        for product in self.product_ids:
            try:
                if not product.amin_petshop_link:
                    log_messages.append(f"⊘ Skipped {product.name}: No Amin Petshop link")
                    continue

                # In a real implementation, you would fetch data from the scraper here
                # For now, this is a placeholder that shows the structure
                # scraped_data = self._fetch_from_scraper(product.amin_petshop_link)
                
                # Placeholder: You would replace this with actual scraper call
                scraped_data = {
                    'link': product.amin_petshop_link,
                    # Add other fields from scraper
                }

                # Track price change
                old_price = product.amin_petshop_price
                
                # Update product
                if self.update_mode == 'quick':
                    # Quick update: only prices and availability
                    quick_data = {
                        'price': scraped_data.get('price'),
                        'regular_price': scraped_data.get('regular_price'),
                        'available': scraped_data.get('available'),
                        'stock_status': scraped_data.get('stock_status'),
                    }
                    product.update_from_amin_petshop_data(quick_data)
                else:
                    # Full update: all fields
                    product.update_from_amin_petshop_data(scraped_data)

                # Check if price changed
                if old_price and product.amin_petshop_price and old_price != product.amin_petshop_price:
                    self.price_changes += 1
                    log_messages.append(
                        f"✓ Updated {product.name}: Price {old_price} → {product.amin_petshop_price}"
                    )
                else:
                    log_messages.append(f"✓ Updated {product.name}")

                self.products_updated += 1

            except Exception as e:
                self.errors += 1
                error_msg = f"✗ Error updating {product.name}: {str(e)}"
                log_messages.append(error_msg)
                _logger.error(error_msg, exc_info=True)

        # Set log message
        self.log_message = '\n'.join(log_messages)

        # Show result message
        message = _(
            'Update completed!\n'
            'Products Updated: %d\n'
            'Price Changes: %d\n'
            'Errors: %d'
        ) % (self.products_updated, self.price_changes, self.errors)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Update Complete'),
                'message': message,
                'type': 'success' if self.errors == 0 else 'warning',
                'sticky': False,
            }
        }

