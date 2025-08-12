from odoo import models, fields, api

class SGLFileCoverActivity(models.Model):
    _name = 'sgl.file.cover.activity'
    _description = 'File Cover Activity Line'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Sequence', default=10, help="Determines the display order")
    file_cover_id = fields.Many2one('sgl.file.cover', string='File Cover', required=True, ondelete='cascade')
    exchange_rate = fields.Float(string='Exchange Rate (EGP)', default=1.0, related='file_cover_id.exchange_rate', store=True)
    
    # Activity Information
    activity_type = fields.Selection([
        ('sea_freight', 'Sea Freight Charges'),
        ('air_freight', 'Air Freight Charges'),
        ('road_freight', 'Road Freight Charges'),
        ('truck_delays', 'Truck delays Charges'),
        ('customs_clearance', 'Customs Clearance Charges'),
        ('customs_approval', 'Customs approval Charges'),
        ('warehousing_inout', 'Warehousing- Pallet in/out Charges'),
        ('warehousing_storage', 'Warehousing- Pallet Storage Charges'),
        ('official_receipts', 'Official Receipts'),
        ('imp_delivery', 'IMP Delivery order Charges'),
        ('imp_release', 'IMP Release Letter Charges'),
        ('exp_booking', 'EXP Booking agent charges'),
        ('other', 'Other Logistics Services'),
    ], string='Activity Type', required=True)
    
    # Currency and Pricing
    currency = fields.Selection([
        ('egp', 'EGP'),
        ('eur', 'EUR'),
        ('usd', 'USD'),
    ], string='Currency', required=True, default='egp')
    
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Price/unit', digits=(16, 2))
    selling_price_unit = fields.Float(string='Selling price Unit', digits=(16, 2))
    
    # Estimate Fields
    estimate_cost = fields.Float(
        string='Estimate cost',
        compute='_compute_all_costs',
        store=True,
        digits=(16, 2)
    )
    estimate_revenue = fields.Float(
        string='Estimate revenue',
        compute='_compute_all_costs',
        store=True,
        digits=(16, 2)
    )
    estimate_profit = fields.Float(
        string='Estimate profit',
        compute='_compute_all_costs',
        store=True,
        digits=(16, 2)
    )
    
    # Actual Fields
    actual_cost = fields.Float(
        string='Actual cost',
        compute='_compute_all_costs',
        store=True,
        digits=(16, 2)
    )
    actual_revenue = fields.Float(
        string='Actual revenue',
        compute='_compute_all_costs',
        store=True,
        digits=(16, 2)
    )
    actual_profit = fields.Float(
        string='Actual profit',
        compute='_compute_all_costs',
        store=True,
        digits=(16, 2)
    )
    
    # Vendor Information
    vendor_name = fields.Char(string='Vendor name')
    vendor_invoice = fields.Char(string='Vendor invoice #')
    
    # EGP Amounts (Computed)
    estimate_cost_egp = fields.Float(
        string='Estimate Cost (EGP)', 
        compute='_compute_egp_amounts', 
        store=True,
        digits=(16, 2)
    )
    estimate_revenue_egp = fields.Float(
        string='Estimate Revenue (EGP)', 
        compute='_compute_egp_amounts', 
        store=True,
        digits=(16, 2)
    )
    estimate_profit_egp = fields.Float(
        string='Estimate Profit (EGP)', 
        compute='_compute_egp_amounts', 
        store=True,
        digits=(16, 2)
    )
    actual_cost_egp = fields.Float(
        string='Actual Cost (EGP)', 
        compute='_compute_egp_amounts', 
        store=True,
        digits=(16, 2)
    )
    actual_revenue_egp = fields.Float(
        string='Actual Revenue (EGP)', 
        compute='_compute_egp_amounts', 
        store=True,
        digits=(16, 2)
    )
    actual_profit_egp = fields.Float(
        string='Actual Profit (EGP)', 
        compute='_compute_egp_amounts', 
        store=True,
        digits=(16, 2)
    )

    # Status and Notes
    is_completed = fields.Boolean(string='Completed', default=False)
    notes = fields.Text(string='Notes')

    def copy_estimate_to_actual(self):
        """Copy estimate values to actual values"""
        for record in self:
            record.write({
                'actual_cost': record.estimate_cost,
                'actual_revenue': record.estimate_revenue,
            })
        return True

    @api.onchange('currency')
    def _onchange_currency(self):
        """تحديث سعر الصرف عند تغيير العملة"""
        for rec in self:
            if rec.currency == 'egp':
                rec.exchange_rate = 1.0
            elif rec.currency == 'usd':
                rec.exchange_rate = 50.0  # يمكن تحديثه حسب السعر الحالي
            elif rec.currency == 'eur':
                rec.exchange_rate = 55.0  # يمكن تحديثه حسب السعر الحالي
    
    @api.depends('quantity', 'price_unit', 'selling_price_unit')
    def _compute_all_costs(self):
        for rec in self:
            rec.estimate_cost = (rec.quantity or 0.0) * (rec.price_unit or 0.0)
            rec.estimate_revenue = (rec.quantity or 0.0) * (rec.selling_price_unit or 0.0)
            rec.estimate_profit = rec.estimate_revenue - rec.estimate_cost
            rec.actual_cost = (rec.quantity or 0.0) * (rec.price_unit or 0.0)
            rec.actual_revenue = (rec.quantity or 0.0) * (rec.selling_price_unit or 0.0)
            rec.actual_profit = rec.actual_revenue - rec.actual_cost

    @api.depends('estimate_revenue', 'estimate_cost')
    def _compute_estimate_profit(self):
        for rec in self:
            rec.estimate_profit = (rec.estimate_revenue or 0.0) - (rec.estimate_cost or 0.0)

    @api.depends('actual_revenue', 'actual_cost')
    def _compute_actual_profit(self):
        for rec in self:
            rec.actual_profit = (rec.actual_revenue or 0.0) - (rec.actual_cost or 0.0)

    @api.depends('quantity', 'price_unit')
    def _compute_actual_cost(self):
        """Calculate actual cost same as estimate cost for now"""
        for rec in self:
            rec.actual_cost = (rec.quantity or 0.0) * (rec.price_unit or 0.0)

    @api.depends('estimate_cost', 'estimate_revenue', 'estimate_profit',
                 'actual_cost', 'actual_revenue', 'actual_profit',
                 'currency', 'file_cover_id.usd_exchange_rate', 'file_cover_id.eur_exchange_rate')
    def _compute_egp_amounts(self):
        """حساب المبالغ بالجنيه المصري بناءً على سعر الصرف وعملة البند"""
        for rec in self:
            # تحديد سعر الصرف بناءً على العملة
            if rec.currency == 'egp':
                exchange_rate = 1.0
            elif rec.currency == 'usd':
                exchange_rate = rec.file_cover_id.usd_exchange_rate or 1.0
            elif rec.currency == 'eur':
                exchange_rate = rec.file_cover_id.eur_exchange_rate or 1.0
            else:
                exchange_rate = 1.0

            # حساب التكاليف المقدرة والفعلية بالجنيه المصري
            estimate_cost_base = rec.estimate_cost or 0.0
            actual_cost_base = rec.actual_cost or 0.0
            
            rec.estimate_cost_egp = estimate_cost_base * exchange_rate
            rec.actual_cost_egp = actual_cost_base * exchange_rate

            # حساب الإيرادات المقدرة والفعلية بالجنيه المصري
            estimate_revenue_base = rec.estimate_revenue or 0.0
            actual_revenue_base = rec.actual_revenue or 0.0
            
            rec.estimate_revenue_egp = estimate_revenue_base * exchange_rate
            rec.actual_revenue_egp = actual_revenue_base * exchange_rate

            # حساب الأرباح المقدرة والفعلية بالجنيه المصري
            rec.estimate_profit_egp = rec.estimate_revenue_egp - rec.estimate_cost_egp
            rec.actual_profit_egp = rec.actual_revenue_egp - rec.actual_cost_egp

    @api.onchange('file_cover_id.usd_exchange_rate', 'file_cover_id.eur_exchange_rate')
    def _onchange_exchange_rates(self):
        """Force recomputation of EGP amounts when exchange rates change"""
        for rec in self:
            rec._compute_egp_amounts()

    @api.onchange('quantity', 'price_unit')
    def _onchange_quantity_price(self):
        """Update estimate cost when quantity or price changes"""
        for rec in self:
            rec.estimate_cost = (rec.quantity or 0.0) * (rec.price_unit or 0.0)

    @api.onchange('estimate_revenue', 'estimate_cost')
    def _onchange_estimate_values(self):
        """Update estimate profit when revenue or cost changes"""
        for rec in self:
            rec.estimate_profit = (rec.estimate_revenue or 0.0) - (rec.estimate_cost or 0.0)

    @api.onchange('actual_revenue', 'actual_cost')
    def _onchange_actual_values(self):
        """Update actual profit when revenue or cost changes"""
        for rec in self:
            rec.actual_profit = (rec.actual_revenue or 0.0) - (rec.actual_cost or 0.0)