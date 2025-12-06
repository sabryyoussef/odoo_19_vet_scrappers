# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class UnifiedImportHistory(models.Model):
    """
    Import History Model
    
    Tracks all import operations for auditing and debugging.
    Provides detailed logs of what was imported, updated, or failed.
    """
    _name = 'unified.import.history'
    _description = 'Import History Log'
    _order = 'import_date desc'
    _rec_name = 'display_name'

    # Basic Information
    data_source_id = fields.Many2one(
        comodel_name='unified.data.source',
        string='Data Source',
        required=True,
        ondelete='cascade',
        help='Source from which data was imported'
    )
    
    import_date = fields.Datetime(
        string='Import Date',
        required=True,
        default=fields.Datetime.now,
        help='Timestamp when import was executed'
    )
    
    import_duration = fields.Float(
        string='Duration (seconds)',
        help='Time taken to complete the import'
    )
    
    # Import Status
    status = fields.Selection(
        selection=[
            ('success', 'Success'),
            ('failed', 'Failed'),
            ('partial', 'Partial Success'),
        ],
        string='Status',
        required=True,
        default='success',
        help='Overall status of the import operation'
    )
    
    # Statistics
    products_created = fields.Integer(
        string='Products Created',
        default=0,
        help='Number of new products created'
    )
    
    products_updated = fields.Integer(
        string='Products Updated',
        default=0,
        help='Number of existing products updated'
    )
    
    products_skipped = fields.Integer(
        string='Products Skipped',
        default=0,
        help='Number of products skipped (duplicates or validation errors)'
    )
    
    products_failed = fields.Integer(
        string='Products Failed',
        default=0,
        help='Number of products that failed to import'
    )
    
    total_records = fields.Integer(
        string='Total Records',
        compute='_compute_total_records',
        store=True,
        help='Total number of records processed'
    )
    
    success_rate = fields.Float(
        string='Success Rate (%)',
        compute='_compute_success_rate',
        store=True,
        help='Percentage of successfully imported products'
    )
    
    # Logs
    import_log = fields.Text(
        string='Import Log',
        help='Detailed log of import operation'
    )
    
    error_log = fields.Text(
        string='Error Log',
        help='Detailed error messages for failed imports'
    )
    
    # File Information
    import_file_name = fields.Char(
        string='File Name',
        help='Name of imported file (if applicable)'
    )
    
    import_file = fields.Binary(
        string='Import File',
        help='Copy of imported file for reference',
        attachment=True
    )
    
    # User Information
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Imported By',
        default=lambda self: self.env.user,
        help='User who triggered the import'
    )
    
    # Import Settings (snapshot)
    match_strategy = fields.Char(
        string='Match Strategy Used',
        help='Snapshot of match strategy used during import'
    )
    
    duplicate_handling = fields.Char(
        string='Duplicate Handling Used',
        help='Snapshot of duplicate handling used during import'
    )
    
    # Computed Fields
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )

    @api.depends('data_source_id', 'import_date')
    def _compute_display_name(self):
        """Compute display name for the record"""
        for record in self:
            if record.data_source_id and record.import_date:
                date_str = fields.Datetime.to_string(record.import_date)
                record.display_name = f"{record.data_source_id.name} - {date_str}"
            else:
                record.display_name = _('Import History')

    @api.depends('products_created', 'products_updated', 'products_skipped', 'products_failed')
    def _compute_total_records(self):
        """Compute total number of records processed"""
        for record in self:
            record.total_records = (
                record.products_created + 
                record.products_updated + 
                record.products_skipped + 
                record.products_failed
            )

    @api.depends('products_created', 'products_updated', 'total_records')
    def _compute_success_rate(self):
        """Compute success rate percentage"""
        for record in self:
            if record.total_records > 0:
                successful = record.products_created + record.products_updated
                record.success_rate = (successful / record.total_records) * 100
            else:
                record.success_rate = 0.0

    # Action Methods
    def action_view_created_products(self):
        """View products created in this import"""
        self.ensure_one()
        
        # TODO: This requires tracking product IDs in import
        # For now, show all products from this source
        return {
            'name': _('Created Products'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'view_mode': 'list,form',
            'domain': [('external_source', '=', self.data_source_id.source_system)],
            'context': {'search_default_external_source': self.data_source_id.source_system},
        }

    def action_view_error_details(self):
        """View detailed error log"""
        self.ensure_one()
        
        return {
            'name': _('Import Errors'),
            'type': 'ir.actions.act_window',
            'res_model': 'unified.import.history',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': {'form_view_initial_mode': 'readonly'},
        }

    def action_retry_import(self):
        """Retry failed import with same settings"""
        self.ensure_one()
        
        # TODO: Implement in Phase 3
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Retry Import'),
                'message': _('Retry functionality will be available in Phase 3'),
                'type': 'info',
                'sticky': False,
            }
        }

    # Helper Methods
    def log_message(self, message, level='info'):
        """
        Add a message to the import log
        
        Args:
            message: Log message
            level: Log level (info, warning, error)
        """
        self.ensure_one()
        
        timestamp = fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level.upper()}] {message}\n"
        
        if level == 'error':
            self.error_log = (self.error_log or '') + log_entry
        
        self.import_log = (self.import_log or '') + log_entry

    def log_product_created(self, product_name):
        """Log successful product creation"""
        self.products_created += 1
        self.log_message(f"Created product: {product_name}", 'info')

    def log_product_updated(self, product_name):
        """Log successful product update"""
        self.products_updated += 1
        self.log_message(f"Updated product: {product_name}", 'info')

    def log_product_skipped(self, product_name, reason):
        """Log skipped product"""
        self.products_skipped += 1
        self.log_message(f"Skipped product: {product_name} - Reason: {reason}", 'warning')

    def log_product_failed(self, product_name, error):
        """Log failed product import"""
        self.products_failed += 1
        self.log_message(f"Failed to import product: {product_name} - Error: {error}", 'error')

    def finalize_import(self, status='success'):
        """
        Finalize import and update data source statistics
        
        Args:
            status: Final import status (success, failed, partial)
        """
        self.ensure_one()
        
        # Update status
        self.status = status
        
        # Update data source statistics
        if self.data_source_id:
            self.data_source_id.write({
                'last_import_date': self.import_date,
                'last_import_status': status,
                'last_import_log': self.import_log,
                'products_created': self.data_source_id.products_created + self.products_created,
                'products_updated': self.data_source_id.products_updated + self.products_updated,
            })
        
        # Log summary
        summary = (
            f"Import completed with status: {status}\n"
            f"Total records: {self.total_records}\n"
            f"Created: {self.products_created}\n"
            f"Updated: {self.products_updated}\n"
            f"Skipped: {self.products_skipped}\n"
            f"Failed: {self.products_failed}\n"
            f"Success rate: {self.success_rate:.2f}%\n"
            f"Duration: {self.import_duration:.2f} seconds"
        )
        self.log_message(summary, 'info')
        
        _logger.info(f"Import finalized: {self.display_name} - {summary}")

    # Cleanup Methods
    @api.model
    def cleanup_old_history(self, days=90):
        """
        Clean up old import history records
        
        Args:
            days: Keep records from last N days, delete older ones
        """
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        old_records = self.search([('import_date', '<', cutoff_date)])
        
        count = len(old_records)
        old_records.unlink()
        
        _logger.info(f"Cleaned up {count} import history records older than {days} days")
        
        return count

