# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    """
    Product Extension for External Source Tracking
    
    Extends product.product with fields for tracking external source information,
    sync status, and generic external metadata.
    """
    _inherit = 'product.product'

    # Core External Source Fields
    external_source = fields.Selection(
        selection=[
            ('vetution', 'Vetution'),
            ('amin_petshop', 'Amin Petshop'),
            ('amazon', 'Amazon'),
            ('other', 'Other/Custom'),
            ('manual', 'Manual Entry'),
        ],
        string='External Source',
        index=True,
        help='Source system from which this product was imported'
    )
    
    external_product_id = fields.Char(
        string='External Product ID',
        index=True,
        help='Product ID/SKU from external system'
    )
    
    external_product_url = fields.Char(
        string='External Product URL',
        help='Direct link to product on external website'
    )
    
    external_category_id = fields.Char(
        string='External Category ID',
        help='Category ID from external source'
    )
    
    external_category_name = fields.Char(
        string='External Category Name',
        help='Category name from external source'
    )
    
    # Sync Status Fields
    external_last_sync = fields.Datetime(
        string='Last Sync',
        readonly=True,
        help='Timestamp of last successful sync with external source'
    )
    
    external_sync_status = fields.Selection(
        selection=[
            ('synced', 'Synced'),
            ('pending', 'Pending Update'),
            ('error', 'Sync Error'),
            ('manual', 'Manual Entry'),
            ('never', 'Never Synced'),
        ],
        string='Sync Status',
        default='never',
        help='Current synchronization status with external source'
    )
    
    external_sync_error = fields.Text(
        string='Sync Error Message',
        readonly=True,
        help='Error message from last failed sync attempt'
    )
    
    # Audit Fields
    external_data_json = fields.Text(
        string='External Data (JSON)',
        help='Raw JSON dump of last external data for debugging and audit'
    )
    
    external_import_date = fields.Datetime(
        string='First Import Date',
        readonly=True,
        help='Timestamp when product was first imported'
    )
    
    external_update_count = fields.Integer(
        string='Update Count',
        default=0,
        readonly=True,
        help='Number of times product has been updated from external source'
    )

    # Action Methods
    def action_open_external_link(self):
        """Open external product URL in browser"""
        self.ensure_one()
        
        if not self.external_product_url:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No External URL'),
                    'message': _('This product does not have an external URL configured'),
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        return {
            'type': 'ir.actions.act_url',
            'url': self.external_product_url,
            'target': 'new',
        }

    def action_sync_from_source(self):
        """Trigger re-import/sync of this product from external source"""
        self.ensure_one()
        
        # TODO: Implement in Phase 3 (Import Engine)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Sync Not Yet Implemented'),
                'message': _('Product sync functionality will be available in Phase 3'),
                'type': 'info',
                'sticky': False,
            }
        }

    def action_view_sync_history(self):
        """View import/sync history for this product"""
        self.ensure_one()
        
        # Find import history records related to this product's source
        if not self.external_source:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No External Source'),
                    'message': _('This product is not linked to an external source'),
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        # Find data sources for this source system
        data_sources = self.env['unified.data.source'].search([
            ('source_system', '=', self.external_source)
        ])
        
        return {
            'name': _('Import History'),
            'type': 'ir.actions.act_window',
            'res_model': 'unified.import.history',
            'view_mode': 'list,form',
            'domain': [('data_source_id', 'in', data_sources.ids)],
        }

    def action_clear_sync_error(self):
        """Clear sync error status"""
        self.ensure_one()
        
        self.write({
            'external_sync_status': 'pending',
            'external_sync_error': False,
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Error Cleared'),
                'message': _('Sync error has been cleared. Product is marked as pending update.'),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_view_vendor_prices(self):
        """View all vendor prices for this product"""
        self.ensure_one()
        return {
            'name': _('Vendor Prices'),
            'type': 'ir.actions.act_window',
            'res_model': 'unified.vendor.price',
            'view_mode': 'list,form',
            'domain': [('product_tmpl_id', '=', self.product_tmpl_id.id)],
            'context': {
                'default_product_tmpl_id': self.product_tmpl_id.id,
                'default_product_id': self.id,
                'default_source': self.external_source or 'other',
            },
        }

    # Helper Methods
    def mark_as_synced(self):
        """Mark product as successfully synced"""
        self.ensure_one()
        
        self.write({
            'external_last_sync': fields.Datetime.now(),
            'external_sync_status': 'synced',
            'external_sync_error': False,
            'external_update_count': self.external_update_count + 1,
        })

    def mark_sync_error(self, error_message):
        """Mark product sync as failed with error message"""
        self.ensure_one()
        
        self.write({
            'external_sync_status': 'error',
            'external_sync_error': error_message,
        })
        
        _logger.error(f"Sync error for product {self.name} (ID: {self.id}): {error_message}")

    def set_external_source_info(self, source, product_id, product_url):
        """
        Set external source information for product
        
        Args:
            source: Source system identifier
            product_id: External product ID/SKU
            product_url: External product URL
        """
        self.ensure_one()
        
        values = {
            'external_source': source,
            'external_product_id': product_id,
            'external_product_url': product_url,
        }
        
        # Set import date if this is first time
        if not self.external_import_date:
            values['external_import_date'] = fields.Datetime.now()
        
        self.write(values)

    # Search Methods
    @api.model
    def find_by_external_url(self, url, source=None):
        """
        Find product by external URL
        
        Args:
            url: External product URL
            source: Optional source system filter
            
        Returns:
            product.product recordset (may be empty)
        """
        domain = [('external_product_url', '=', url)]
        if source:
            domain.append(('external_source', '=', source))
        
        return self.search(domain, limit=1)

    @api.model
    def find_by_external_id(self, external_id, source=None):
        """
        Find product by external product ID
        
        Args:
            external_id: External product ID/SKU
            source: Optional source system filter
            
        Returns:
            product.product recordset (may be empty)
        """
        domain = [('external_product_id', '=', external_id)]
        if source:
            domain.append(('external_source', '=', source))
        
        return self.search(domain, limit=1)

    @api.model
    def get_products_needing_sync(self, source=None, limit=100):
        """
        Get products that need synchronization
        
        Args:
            source: Optional source system filter
            limit: Maximum number of products to return
            
        Returns:
            product.product recordset
        """
        domain = [
            ('external_sync_status', 'in', ['pending', 'error']),
            ('external_source', '!=', False),
            ('external_source', '!=', 'manual'),
        ]
        
        if source:
            domain.append(('external_source', '=', source))
        
        return self.search(domain, limit=limit, order='external_last_sync asc')

    # Computed Fields for Statistics
    @api.model
    def get_external_source_stats(self):
        """
        Get statistics about products by external source
        
        Returns:
            dict with source counts and sync status
        """
        stats = {}
        
        # Count by source
        for source in ['vetution', 'amin_petshop', 'amazon', 'other', 'manual']:
            count = self.search_count([('external_source', '=', source)])
            if count > 0:
                stats[source] = {
                    'total': count,
                    'synced': self.search_count([
                        ('external_source', '=', source),
                        ('external_sync_status', '=', 'synced')
                    ]),
                    'pending': self.search_count([
                        ('external_source', '=', source),
                        ('external_sync_status', '=', 'pending')
                    ]),
                    'error': self.search_count([
                        ('external_source', '=', source),
                        ('external_sync_status', '=', 'error')
                    ]),
                }
        
        return stats

