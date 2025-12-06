# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ScraperJob(models.Model):
    _name = 'scraper.job'
    _description = 'Scraper Job History'
    _order = 'start_time desc'
    _rec_name = 'display_name'

    # Basic Information
    config_id = fields.Many2one(
        comodel_name='scraper.config',
        string='Scraper Configuration',
        required=True,
        ondelete='cascade',
        help='The scraper configuration used for this job'
    )
    display_name = fields.Char(
        string='Job Name',
        compute='_compute_display_name',
        store=True,
        help='Display name for the job'
    )
    
    # Execution Details
    start_time = fields.Datetime(
        string='Start Time',
        required=True,
        default=fields.Datetime.now,
        help='When the scraping job started'
    )
    end_time = fields.Datetime(
        string='End Time',
        help='When the scraping job finished'
    )
    duration = fields.Float(
        string='Duration (seconds)',
        compute='_compute_duration',
        store=True,
        help='How long the job took to complete'
    )
    
    # Status
    status = fields.Selection([
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('success', 'Success'),
        ('partial', 'Partial Success'),
        ('failed', 'Failed'),
    ], string='Status', default='pending', required=True,
       help='Current status of the scraping job')
    
    # Results
    products_scraped = fields.Integer(
        string='Products Scraped',
        default=0,
        help='Number of products successfully scraped'
    )
    products_failed = fields.Integer(
        string='Products Failed',
        default=0,
        help='Number of products that failed to scrape'
    )
    pages_scraped = fields.Integer(
        string='Pages Scraped',
        default=0,
        help='Number of pages processed'
    )
    
    # Logs
    log = fields.Text(
        string='Execution Log',
        help='Detailed log of the scraping process'
    )
    error_log = fields.Text(
        string='Error Log',
        help='Errors encountered during scraping'
    )
    
    # Relations
    draft_product_ids = fields.One2many(
        comodel_name='scraped.product.draft',
        inverse_name='scraper_job_id',
        string='Draft Products',
        help='Products scraped in this job'
    )
    draft_count = fields.Integer(
        string='Draft Count',
        compute='_compute_draft_count',
        store=True,
        help='Number of draft products from this job'
    )
    
    # Execution Type
    execution_type = fields.Selection([
        ('manual', 'Manual'),
        ('scheduled', 'Scheduled (Cron)'),
    ], string='Execution Type', default='manual',
       help='How this job was triggered')
    
    @api.depends('config_id.name', 'start_time')
    def _compute_display_name(self):
        for job in self:
            if job.config_id and job.start_time:
                job.display_name = f"{job.config_id.name} - {job.start_time.strftime('%Y-%m-%d %H:%M')}"
            else:
                job.display_name = _('Scraper Job')
    
    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for job in self:
            if job.start_time and job.end_time:
                delta = job.end_time - job.start_time
                job.duration = delta.total_seconds()
            else:
                job.duration = 0.0
    
    @api.depends('draft_product_ids')
    def _compute_draft_count(self):
        for job in self:
            job.draft_count = len(job.draft_product_ids)
    
    def action_view_drafts(self):
        """View draft products from this job"""
        self.ensure_one()
        return {
            'name': _('Draft Products'),
            'type': 'ir.actions.act_window',
            'res_model': 'scraped.product.draft',
            'view_mode': 'list,form',
            'domain': [('scraper_job_id', '=', self.id)],
            'context': {'default_scraper_job_id': self.id},
        }
    
    def action_rerun(self):
        """Rerun the scraper with the same configuration"""
        self.ensure_one()
        return self.config_id.action_run_scraper()

