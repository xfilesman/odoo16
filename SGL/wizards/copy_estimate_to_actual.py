from odoo import api, fields, models

class CopyEstimateToActualWizard(models.TransientModel):
    _name = 'sgl.file.cover.copy.estimate.to.actual'
    _description = 'Copy Estimate to Actual'

    activity_id = fields.Many2one('sgl.file.cover.activity', string='Activity', required=True)

    @api.multi
    def action_copy(self):
        self.ensure_one()
        if self.activity_id:
            self.activity_id.write({
                'actual_cost': self.activity_id.estimate_cost,
                'actual_revenue': self.activity_id.estimate_revenue,
                'actual_profit': self.activity_id.estimate_profit
            })
        return {'type': 'ir.actions.act_window_close'}
