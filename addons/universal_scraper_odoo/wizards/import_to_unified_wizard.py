# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import json
import base64
import io

_logger = logging.getLogger(__name__)


class ImportToUnifiedWizard(models.TransientModel):
    _name = 'import.to.unified.wizard'
    _description = 'Import Scraped Products to Unified Scrapper'

    draft_ids = fields.Many2many(
        comodel_name='scraped.product.draft',
        string='Products to Import',
        required=True,
        help='Approved scraped products to import'
    )
    
    data_source_id = fields.Many2one(
        comodel_name='unified.data.source',
        string='Data Source',
        required=True,
        help='The data source in Unified Scrapper'
    )
    
    match_strategy = fields.Selection([
        ('url', 'Match by URL (Recommended)'),
        ('sku', 'Match by SKU'),
        ('name', 'Match by Name'),
    ], string='Matching Strategy', default='url', required=True,
       help='How to identify existing products')
    
    duplicate_handling = fields.Selection([
        ('skip', 'Skip Duplicates'),
        ('update', 'Update Existing Products'),
        ('add_vendor_price', 'Add as Vendor Price'),
    ], string='Duplicate Handling', default='add_vendor_price', required=True,
       help='What to do when a product already exists')
    
    cost_price_strategy = fields.Selection([
        ('lowest', 'Use Lowest Vendor Price'),
        ('average', 'Use Average Vendor Price'),
        ('first', 'Use First Vendor Price'),
    ], string='Cost Price Strategy', default='lowest', required=True,
       help='How to calculate the main product cost price from vendor prices')
    
    create_vendor_prices = fields.Boolean(
        string='Create Vendor Prices',
        default=True,
        help='Create vendor price records for multi-source tracking'
    )
    
    product_count = fields.Integer(
        string='Products to Import',
        compute='_compute_product_count'
    )
    
    @api.depends('draft_ids')
    def _compute_product_count(self):
        for wizard in self:
            wizard.product_count = len(wizard.draft_ids)
    
    @api.model
    def default_get(self, fields_list):
        """Set default values from context"""
        res = super().default_get(fields_list)
        
        # Get draft IDs from context
        if 'draft_ids' in fields_list and self._context.get('active_ids'):
            draft_ids = self.env['scraped.product.draft'].browse(self._context.get('active_ids'))
            approved_drafts = draft_ids.filtered(lambda d: d.state == 'approved')
            res['draft_ids'] = [(6, 0, approved_drafts.ids)]
            
            # Set data source from first draft
            if approved_drafts:
                res['data_source_id'] = approved_drafts[0].data_source_id.id
        
        return res
    
    def action_import(self):
        """Import approved drafts to Unified Scrapper"""
        self.ensure_one()
        
        if not self.draft_ids:
            raise UserError(_("No products selected for import"))
        
        # Filter only approved drafts
        approved_drafts = self.draft_ids.filtered(lambda d: d.state == 'approved')
        
        if not approved_drafts:
            raise UserError(_("No approved products to import. Please approve products first."))
        
        # Convert drafts to JSON format for Unified Scrapper import wizard
        products_data = []
        for draft in approved_drafts:
            product_dict = {
                'name': draft.name,
                'default_code': draft.sku or '',
                'list_price': draft.price,
                'currency': draft.currency,
                'external_product_url': draft.url,
                'external_product_id': draft.sku or '',
                'availability': draft.availability,
                'brand': draft.brand or '',
                'description': draft.description or '',
                'image_url': draft.image_url or '',
                'category': draft.category or '',
                'stock_quantity': draft.stock_quantity or 0,
            }
            products_data.append(product_dict)
        
        # Create JSON file
        json_data = json.dumps(products_data, indent=2, ensure_ascii=False)
        json_bytes = json_data.encode('utf-8')
        json_base64 = base64.b64encode(json_bytes)
        
        # Create Unified Import Wizard
        import_wizard = self.env['unified.import.wizard'].create({
            'file_data': json_base64,
            'file_name': f'scraped_products_{fields.Datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            'file_type': 'json',
            'data_source_id': self.data_source_id.id,
            'match_strategy': self.match_strategy,
            'duplicate_handling': self.duplicate_handling,
            'cost_price_strategy': self.cost_price_strategy,
            'create_vendor_prices': self.create_vendor_prices,
            'state': 'upload',
        })
        
        # Advance to preview step
        import_wizard.action_next_step()
        
        # Mark drafts as imported
        for draft in approved_drafts:
            draft.write({
                'state': 'imported',
                'import_date': fields.Datetime.now(),
            })
        
        # Open the Unified Import Wizard
        return {
            'name': _('Import to Unified Scrapper'),
            'type': 'ir.actions.act_window',
            'res_model': 'unified.import.wizard',
            'view_mode': 'form',
            'res_id': import_wizard.id,
            'target': 'new',
            'context': self.env.context,
        }

