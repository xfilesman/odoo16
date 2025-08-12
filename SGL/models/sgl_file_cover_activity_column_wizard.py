from odoo import models, fields, api
import json

class SGLFileCoverActivityColumnWizard(models.TransientModel):
    _name = 'sgl.file.cover.activity.column.wizard'
    _description = 'Select File Cover Columns Wizard'

    # Default columns to show - only the most important ones
    col1 = fields.Boolean(string='Job-File No.', default=True)  # Always show
    col2 = fields.Boolean(string='Business Type', default=True)  # Always show
    col3 = fields.Boolean(string='Initial Date', default=True)  # Always show
    col4 = fields.Boolean(string='Origin Office', default=False)  # Hide by default
    col5 = fields.Boolean(string='Customer Name', default=True)  # Always show
    col6 = fields.Boolean(string='BL/AWB Numbers', default=False)  # Hide by default
    col7 = fields.Boolean(string='Liners Details', default=False)  # Hide by default
    col8 = fields.Boolean(string='Shipment Type', default=True)  # Always show
    col9 = fields.Boolean(string='Shipment Description', default=False)  # Hide by default
    col10 = fields.Boolean(string='Currency', default=True)  # Always show
    col11 = fields.Boolean(string='Estimate Cost', default=True)  # Always show
    col12 = fields.Boolean(string='Actual Cost', default=True)  # Always show
    col13 = fields.Boolean(string='Estimate Revenue', default=True)  # Always show
    col14 = fields.Boolean(string='Actual Revenue', default=True)  # Always show
    col15 = fields.Boolean(string='Estimate Profit', default=True)  # Always show
    col16 = fields.Boolean(string='Actual Profit', default=True)  # Always show
    col17 = fields.Boolean(string='Est. Cost (EGP)', default=True)  # Show by default
    col18 = fields.Boolean(string='Act. Cost (EGP)', default=True)  # Show by default
    col19 = fields.Boolean(string='Est. Revenue (EGP)', default=True)  # Show by default
    col20 = fields.Boolean(string='Act. Revenue (EGP)', default=True)  # Show by default
    col21 = fields.Boolean(string='Est. Profit (EGP)', default=True)  # Show by default
    col22 = fields.Boolean(string='Act. Profit (EGP)', default=True)  # Show by default
    col23 = fields.Boolean(string='All Invoice Numbers', default=False)  # Hide by default
    col24 = fields.Boolean(string='Final Date', default=True)  # Always show
    col25 = fields.Boolean(string='Job Status', default=True)  # Always show
    col26 = fields.Boolean(string='Invoice Number', default=False)  # Hide by default
    col27 = fields.Boolean(string='Comments', default=False)  # Hide by default

    @api.model
    def default_get(self, fields_list):
        """Load default values"""
        res = super().default_get(fields_list)
        return res

    def action_apply(self):
        """Apply column preferences"""
        try:
            # Return action to refresh the view
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        except Exception as e:
            return {'type': 'ir.actions.act_window_close'}

    def action_reset_defaults(self):
        """Reset all fields to default (True)"""
        try:
            for i in range(1, 28):
                field_name = f'col{i}'
                if hasattr(self, field_name):
                    setattr(self, field_name, True)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        except Exception as e:
            return {'type': 'ir.actions.act_window_close'}
