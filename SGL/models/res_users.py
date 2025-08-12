from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    activity_column_preferences = fields.Text(
        string='Activity Column Preferences',
        help='User preferences for activity columns visibility'
    ) 