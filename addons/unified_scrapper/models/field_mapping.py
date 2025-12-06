# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json
import logging

_logger = logging.getLogger(__name__)


class UnifiedFieldMapping(models.Model):
    """
    Field Mapping Model
    
    Defines how external data fields map to Odoo product fields,
    with optional transformations and validation rules.
    """
    _name = 'unified.field.mapping'
    _description = 'External Field to Odoo Field Mapping'
    _order = 'data_source_id, sequence, id'
    _rec_name = 'external_field_name'

    # Basic Information
    data_source_id = fields.Many2one(
        comodel_name='unified.data.source',
        string='Data Source',
        required=True,
        ondelete='cascade',
        help='Parent data source configuration'
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of mapping application (lower = earlier)'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Enable/disable this mapping'
    )
    
    # Source Field
    external_field_name = fields.Char(
        string='External Field Name',
        required=True,
        help='Field name in external data (e.g., "product_name", "price_egp")'
    )
    
    # Target Field
    target_model = fields.Selection(
        selection=[
            ('product.template', 'Product Template'),
            ('product.product', 'Product Variant'),
        ],
        string='Target Model',
        required=True,
        default='product.product',
        help='Target Odoo model for this mapping'
    )
    
    target_field = fields.Char(
        string='Target Field',
        required=True,
        help='Technical field name in Odoo (e.g., "name", "list_price", "default_code")'
    )
    
    field_type = fields.Selection(
        selection=[
            ('char', 'Text (Char)'),
            ('text', 'Long Text'),
            ('integer', 'Integer'),
            ('float', 'Float/Decimal'),
            ('boolean', 'Boolean'),
            ('date', 'Date'),
            ('datetime', 'Date & Time'),
            ('selection', 'Selection'),
            ('many2one', 'Many2one'),
            ('one2many', 'One2many'),
            ('many2many', 'Many2many'),
        ],
        string='Field Type',
        compute='_compute_field_type',
        store=True,
        help='Inferred field type from target field'
    )
    
    # Validation & Defaults
    is_required = fields.Boolean(
        string='Required',
        default=False,
        help='Fail import if external field is missing or empty'
    )
    
    default_value = fields.Char(
        string='Default Value',
        help='Default value if external field is empty (leave blank for no default)'
    )
    
    # Transformation Rules
    transformation_rule = fields.Selection(
        selection=[
            ('none', 'None (Direct Mapping)'),
            ('lowercase', 'Convert to Lowercase'),
            ('uppercase', 'Convert to Uppercase'),
            ('title_case', 'Convert to Title Case'),
            ('strip_html', 'Strip HTML Tags'),
            ('strip_whitespace', 'Strip Extra Whitespace'),
            ('price_conversion', 'Currency Conversion'),
            ('date_format', 'Parse Date Format'),
            ('boolean_convert', 'Convert to Boolean'),
            ('json_extract', 'Extract from JSON'),
            ('split_string', 'Split String to List'),
            ('custom_python', 'Custom Python Expression'),
        ],
        string='Transformation Rule',
        default='none',
        help='Optional transformation to apply to the value'
    )
    
    transformation_params = fields.Text(
        string='Transformation Parameters',
        help='JSON parameters for transformation (e.g., {"date_format": "%%Y-%%m-%%d", "currency_rate": 1.5})'
    )
    
    # Documentation
    notes = fields.Text(
        string='Notes',
        help='Mapping documentation and examples'
    )

    # Computed Fields
    @api.depends('target_model', 'target_field')
    def _compute_field_type(self):
        """Infer field type from target model and field"""
        for record in self:
            if record.target_model and record.target_field:
                try:
                    # Get the model
                    model = self.env[record.target_model]
                    # Check if field exists
                    if record.target_field in model._fields:
                        field_obj = model._fields[record.target_field]
                        record.field_type = field_obj.type
                    else:
                        record.field_type = 'char'  # Default
                except Exception as e:
                    _logger.warning(f"Could not infer field type for {record.target_field}: {e}")
                    record.field_type = 'char'
            else:
                record.field_type = 'char'

    # Constraints
    @api.constrains('transformation_params')
    def _check_transformation_params(self):
        """Validate transformation parameters are valid JSON"""
        for record in self:
            if record.transformation_params:
                try:
                    json.loads(record.transformation_params)
                except json.JSONDecodeError:
                    raise ValidationError(_('Transformation Parameters must be valid JSON'))

    @api.constrains('target_field', 'target_model')
    def _check_target_field_exists(self):
        """Validate that target field exists in target model"""
        for record in self:
            if record.target_model and record.target_field:
                try:
                    model = self.env[record.target_model]
                    if record.target_field not in model._fields:
                        raise ValidationError(
                            _('Field "%s" does not exist in model "%s"') % 
                            (record.target_field, record.target_model)
                        )
                except KeyError:
                    raise ValidationError(_('Model "%s" does not exist') % record.target_model)

    # Action Methods
    def action_test_mapping(self):
        """
        Test mapping with sample data
        Opens a wizard to input sample data and see the result
        """
        self.ensure_one()
        
        # TODO: Implement test wizard in Phase 3
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Test Mapping'),
                'message': _('Test wizard will be available in Phase 3'),
                'type': 'info',
                'sticky': False,
            }
        }

    # Transformation Methods
    def apply_transformation(self, value):
        """
        Apply configured transformation to a value
        
        Args:
            value: Input value from external data
            
        Returns:
            Transformed value ready for Odoo field
        """
        self.ensure_one()
        
        # Handle None/empty values
        if value is None or value == '':
            if self.default_value:
                return self.default_value
            elif self.is_required:
                raise ValidationError(
                    _('Required field "%s" is empty and has no default value') % 
                    self.external_field_name
                )
            else:
                return None
        
        # Apply transformation based on rule
        try:
            if self.transformation_rule == 'none':
                return value
            
            elif self.transformation_rule == 'lowercase':
                return str(value).lower()
            
            elif self.transformation_rule == 'uppercase':
                return str(value).upper()
            
            elif self.transformation_rule == 'title_case':
                return str(value).title()
            
            elif self.transformation_rule == 'strip_html':
                return self._strip_html(str(value))
            
            elif self.transformation_rule == 'strip_whitespace':
                return ' '.join(str(value).split())
            
            elif self.transformation_rule == 'price_conversion':
                return self._convert_price(value)
            
            elif self.transformation_rule == 'date_format':
                return self._parse_date(value)
            
            elif self.transformation_rule == 'boolean_convert':
                return self._convert_boolean(value)
            
            elif self.transformation_rule == 'json_extract':
                return self._extract_from_json(value)
            
            elif self.transformation_rule == 'split_string':
                return self._split_string(value)
            
            elif self.transformation_rule == 'custom_python':
                return self._execute_custom_python(value)
            
            else:
                _logger.warning(f"Unknown transformation rule: {self.transformation_rule}")
                return value
                
        except Exception as e:
            _logger.error(f"Transformation failed for {self.external_field_name}: {e}")
            if self.is_required:
                raise ValidationError(
                    _('Transformation failed for required field "%s": %s') % 
                    (self.external_field_name, str(e))
                )
            return None

    # Helper Methods for Transformations
    def _strip_html(self, value):
        """Remove HTML tags from string"""
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', value)

    def _convert_price(self, value):
        """Convert price with currency rate"""
        params = self._get_transformation_params()
        rate = params.get('currency_rate', 1.0)
        
        # Remove currency symbols and convert to float
        import re
        clean_value = re.sub(r'[^\d.]', '', str(value))
        return float(clean_value) * float(rate)

    def _parse_date(self, value):
        """Parse date string with custom format"""
        from datetime import datetime
        params = self._get_transformation_params()
        date_format = params.get('date_format', '%Y-%m-%d')
        
        parsed_date = datetime.strptime(str(value), date_format)
        
        if self.field_type == 'date':
            return parsed_date.date()
        else:
            return parsed_date

    def _convert_boolean(self, value):
        """Convert various formats to boolean"""
        if isinstance(value, bool):
            return value
        
        str_value = str(value).lower().strip()
        return str_value in ('true', '1', 'yes', 'y', 'on', 'active', 'enabled')

    def _extract_from_json(self, value):
        """Extract value from JSON using path"""
        params = self._get_transformation_params()
        json_path = params.get('json_path', '')
        
        if isinstance(value, str):
            value = json.loads(value)
        
        # Navigate JSON path (e.g., "data.product.name")
        for key in json_path.split('.'):
            if key:
                value = value.get(key) if isinstance(value, dict) else value
        
        return value

    def _split_string(self, value):
        """Split string into list"""
        params = self._get_transformation_params()
        delimiter = params.get('delimiter', ',')
        
        return [item.strip() for item in str(value).split(delimiter)]

    def _execute_custom_python(self, value):
        """Execute custom Python expression"""
        params = self._get_transformation_params()
        expression = params.get('expression', 'value')
        
        # Safe eval with limited scope
        safe_globals = {
            '__builtins__': {
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'len': len,
                'abs': abs,
                'round': round,
            }
        }
        safe_locals = {'value': value}
        
        try:
            return eval(expression, safe_globals, safe_locals)
        except Exception as e:
            _logger.error(f"Custom Python expression failed: {e}")
            raise ValidationError(_('Custom Python expression failed: %s') % str(e))

    def _get_transformation_params(self):
        """Parse and return transformation parameters as dict"""
        if self.transformation_params:
            try:
                return json.loads(self.transformation_params)
            except json.JSONDecodeError:
                _logger.warning(f"Invalid JSON in transformation_params for {self.external_field_name}")
                return {}
        return {}

    # Bulk Operations
    @api.model
    def create_default_mappings(self, data_source_id, source_system):
        """
        Create default field mappings for a data source based on source system
        
        Args:
            data_source_id: ID of the data source
            source_system: Source system identifier (vetution, amin_petshop, etc.)
        """
        mappings = []
        
        # Common mappings for all sources
        common_mappings = [
            {'external': 'name', 'target': 'name', 'model': 'product.template', 'required': True},
            {'external': 'description', 'target': 'description', 'model': 'product.template'},
            {'external': 'price', 'target': 'list_price', 'model': 'product.template'},
            {'external': 'cost', 'target': 'standard_price', 'model': 'product.template'},
            {'external': 'sku', 'target': 'default_code', 'model': 'product.product'},
            {'external': 'barcode', 'target': 'barcode', 'model': 'product.product'},
        ]
        
        for idx, mapping in enumerate(common_mappings):
            mappings.append({
                'data_source_id': data_source_id,
                'sequence': (idx + 1) * 10,
                'external_field_name': mapping['external'],
                'target_model': mapping['model'],
                'target_field': mapping['target'],
                'is_required': mapping.get('required', False),
            })
        
        # Source-specific mappings
        if source_system == 'vetution':
            vetution_mappings = [
                {'external': 'brand', 'target': 'vetution_brand', 'model': 'product.product'},
                {'external': 'brand_link', 'target': 'vetution_brand_link', 'model': 'product.product'},
                {'external': 'link', 'target': 'vetution_link', 'model': 'product.product'},
                {'external': 'image_url', 'target': 'vetution_image_url', 'model': 'product.product'},
                {'external': 'rating', 'target': 'vetution_rating', 'model': 'product.product'},
            ]
            for idx, mapping in enumerate(vetution_mappings):
                mappings.append({
                    'data_source_id': data_source_id,
                    'sequence': (len(common_mappings) + idx + 1) * 10,
                    'external_field_name': mapping['external'],
                    'target_model': mapping['model'],
                    'target_field': mapping['target'],
                })
        
        elif source_system == 'amin_petshop':
            amin_mappings = [
                {'external': 'link', 'target': 'amin_petshop_link', 'model': 'product.product'},
                {'external': 'sku', 'target': 'amin_petshop_sku', 'model': 'product.product'},
                {'external': 'brand', 'target': 'amin_petshop_brand', 'model': 'product.product'},
                {'external': 'image_url', 'target': 'amin_petshop_image_url', 'model': 'product.product'},
                {'external': 'price', 'target': 'amin_petshop_price', 'model': 'product.product'},
                {'external': 'regular_price', 'target': 'amin_petshop_regular_price', 'model': 'product.product'},
            ]
            for idx, mapping in enumerate(amin_mappings):
                mappings.append({
                    'data_source_id': data_source_id,
                    'sequence': (len(common_mappings) + idx + 1) * 10,
                    'external_field_name': mapping['external'],
                    'target_model': mapping['model'],
                    'target_field': mapping['target'],
                })
        
        # Create all mappings
        if mappings:
            self.create(mappings)
            _logger.info(f"Created {len(mappings)} default mappings for data source {data_source_id}")

