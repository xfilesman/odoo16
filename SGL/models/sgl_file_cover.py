from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class SGLFileCover(models.Model):
    _name = 'sgl.file.cover'
    _description = 'File Cover'

    name = fields.Char(string='Job-File No.', required=True, copy=False, readonly=True, default=lambda self: self._get_next_sequence())
    initial_file_cover_date = fields.Date(string='Initial file cover Date')
    final_file_cover_date = fields.Date(string='Final file cover Date')
    business_type = fields.Selection([
        ('air', 'AIR'),
        ('sea', 'SEA'),
        ('road', 'ROAD'),
        ('chb', 'CHB'),
        ('whs', 'WHS'),
    ], string='Business type')
    eg_customer_name = fields.Many2one('res.partner', string='EG Customer Name')
    customer_tax_details = fields.Text(string='Customer Tax details')
    customer_full_address = fields.Char(string='Full Address')
    customer_cr_no = fields.Char(string='CR no.')
    customer_tax_no = fields.Char(string='TAX no.')
    # Shipment details
    commodity = fields.Char(string='Commodity')
    weight_dimension = fields.Char(string='Weight & Dimension')
    container_count_type = fields.Char(string='Container Count & Type KGs')
    shipment_description = fields.Text(string='Shipment Description')
    origin_office = fields.Char(string='Origin Office')
    currency = fields.Selection([
        ('usd', 'USD'),
        ('eur', 'EUR'),
        ('egp', 'EGP'),
    ], string='Currency')
    exchange_rate = fields.Float(string='Exchange Rate (EGP)', default=1.0, help='سعر الصرف مقابل الجنيه المصري')
    linar_details = fields.Char(string='Linar Details')
    bl_awb_mawb_hawb_bks = fields.Char(string='BL - AWB- MAWB-HAWB - BKs')
    hbl_awb_no = fields.Char(string='HBL/AWB no.')
    invoice_date = fields.Date(string='Invoice Date')
    shipment_type = fields.Selection([
        ('exp', 'EXP'),
        ('imp', 'IMP'),
        ('transit', 'Transit'),
    ], string='Shipment type')
    pol = fields.Char(string='POL')
    pod = fields.Char(string='POD')
    eta_etd = fields.Date(string='ETA/ETD', help='Estimated Time of Arrival / Estimated Time of Departure')
    # Company reference and logo to display same logo as Odoo company logo
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, readonly=True)
    company_logo = fields.Binary(string='Company Logo', compute='_compute_company_logo', store=False)
    # One2many for activity lines
    activity_line_ids = fields.One2many('sgl.file.cover.activity', 'file_cover_id', string='Activity Lines')
    # Financial summary fields
    estimate_cost = fields.Float(string='Estimate cost', compute='_compute_totals', store=True)
    actual_cost = fields.Float(string='Actual Cost', compute='_compute_totals', store=True)
    estimate_revenue = fields.Float(string='Estimate Revenue', compute='_compute_totals', store=True)
    actual_revenue = fields.Float(string='Actual Revenue', compute='_compute_totals', store=True)
    estimate_profit = fields.Float(string='Estimate Profit', compute='_compute_totals', store=True)
    actual_profit = fields.Float(string='Actual Profit', compute='_compute_totals', store=True)
    
    # Financial summary fields in EGP
    estimate_cost_egp = fields.Float(string='Estimate Cost (EGP)', compute='_compute_totals_egp', store=True)
    actual_cost_egp = fields.Float(string='Actual Cost (EGP)', compute='_compute_totals_egp', store=True)
    estimate_revenue_egp = fields.Float(string='Estimate Revenue (EGP)', compute='_compute_totals_egp', store=True)
    actual_revenue_egp = fields.Float(string='Actual Revenue (EGP)', compute='_compute_totals_egp', store=True)
    estimate_profit_egp = fields.Float(string='Estimate Profit (EGP)', compute='_compute_totals_egp', store=True)
    actual_profit_egp = fields.Float(string='Actual Profit (EGP)', compute='_compute_totals_egp', store=True)
    
    # Total profits across all lines
    total_estimate_profit = fields.Float(string='Total Estimate Profit (All Lines)', compute='_compute_total_profits', store=True)
    total_actual_profit = fields.Float(string='Total Actual Profit (All Lines)', compute='_compute_total_profits', store=True)

    summary_currency = fields.Selection([
        ('usd', 'USD'),
        ('eur', 'EUR'),
    ], string='Summary Currency', default='usd')

    summary_exchange_rate = fields.Float(string='Summary Exchange Rate')

    summary_estimate_cost_egp = fields.Float(string='Estimate Cost (EGP)', compute='_compute_summary_egp', store=True)
    summary_actual_cost_egp = fields.Float(string='Actual Cost (EGP)', compute='_compute_summary_egp', store=True)
    summary_estimate_revenue_egp = fields.Float(string='Estimate Revenue (EGP)', compute='_compute_summary_egp', store=True)
    summary_actual_revenue_egp = fields.Float(string='Actual Revenue (EGP)', compute='_compute_summary_egp', store=True)
    summary_estimate_profit_egp = fields.Float(string='Estimate Profit (EGP)', compute='_compute_summary_egp', store=True)
    summary_actual_profit_egp = fields.Float(string='Actual Profit (EGP)', compute='_compute_summary_egp', store=True)

    usd_exchange_rate = fields.Float(string='USD Exchange Rate', default=1.0)
    eur_exchange_rate = fields.Float(string='EUR Exchange Rate', default=1.0)

    job_status = fields.Selection([
        ('opened', 'Opened'),
        ('in_progress', 'In Progress'),
        ('service_rendered', 'Service Rendered'),
        ('invoiced', 'Invoiced'),
        ('closed', 'Closed'),
    ], string='Job Status')
    invoice_number = fields.Char(string='Invoice #')
    all_invoice_numbers = fields.Text(string='All Invoice Numbers', help='جميع أرقام الفواتير المرتبطة بهذا الملف')
    comments = fields.Text(string='Comments')
    vendor_name = fields.Many2one('res.partner', string='Vendor')
    activity_currency_filter = fields.Selection([
        ('egp', 'EGP'),
        ('usd', 'USD'),
        ('eur', 'EUR'),
    ], string='Filter Activity Lines by Currency')
    file_currency = fields.Char(string='Currency', compute='_compute_file_currency', store=True)
    egp_currency_id = fields.Many2one('res.currency', string='EGP Currency', compute='_compute_egp_currency', store=False)

    @api.onchange('currency')
    def _onchange_currency(self):
        """تحديث سعر الصرف تلقائياً عند تغيير العملة"""
        for rec in self:
            if rec.currency == 'egp':
                rec.exchange_rate = 1.0
            elif rec.currency == 'usd':
                rec.exchange_rate = 50.0  # يمكن تغيير هذا الرقم حسب السعر الحالي
            elif rec.currency == 'eur':
                rec.exchange_rate = 55.0  # يمكن تغيير هذا الرقم حسب السعر الحالي

    @api.onchange('company_id')
    def _onchange_company_id(self):
        """تحديث شعار الشركة عند تغيير الشركة أو عند إنشاء سجل جديد"""
        for rec in self:
            if rec.company_id:
                rec.company_logo = rec.company_id.logo

    @api.model
    def default_get(self, fields_list):
        """Override default_get to ensure company logo is set for new records"""
        defaults = super().default_get(fields_list)
        if 'company_logo' in fields_list and not defaults.get('company_logo'):
            company = self.env.company
            if company and company.logo:
                defaults['company_logo'] = company.logo
        return defaults

    @api.onchange('usd_exchange_rate', 'eur_exchange_rate')
    def _onchange_exchange_rates(self):
        """Force recomputation of all activity lines when exchange rates change"""
        for rec in self:
            if rec.activity_line_ids:
                for line in rec.activity_line_ids:
                    line._compute_egp_amounts()


    # Removed @api.onchange('business_type') to prevent sequence consumption during form changes
    # The sequence will only be generated once during create()

    @api.onchange('eg_customer_name')
    def _onchange_eg_customer_name(self):
        for rec in self:
            partner = rec.eg_customer_name
            if partner:
                rec.customer_full_address = partner.contact_address or ''
                rec.customer_cr_no = partner.ref or ''
                rec.customer_tax_no = partner.vat or ''
            else:
                rec.customer_full_address = ''
                rec.customer_cr_no = ''
                rec.customer_tax_no = ''

    @api.depends('activity_line_ids.estimate_cost', 'activity_line_ids.actual_cost',
                 'activity_line_ids.estimate_revenue', 'activity_line_ids.actual_revenue',
                 'activity_line_ids.estimate_profit', 'activity_line_ids.actual_profit')
    def _compute_totals(self):
        for rec in self:
            rec.estimate_cost = sum(line.estimate_cost for line in rec.activity_line_ids)
            rec.actual_cost = sum(line.actual_cost for line in rec.activity_line_ids)
            rec.estimate_revenue = sum(line.estimate_revenue for line in rec.activity_line_ids)
            rec.actual_revenue = sum(line.actual_revenue for line in rec.activity_line_ids)
            rec.estimate_profit = sum(line.estimate_profit for line in rec.activity_line_ids)
            rec.actual_profit = sum(line.actual_profit for line in rec.activity_line_ids)

    @api.depends('activity_line_ids.estimate_profit_egp', 'activity_line_ids.actual_profit_egp')
    def _compute_total_profits(self):
        """Calculate total profits across all activity lines in EGP"""
        for rec in self:
            rec.total_estimate_profit = sum(line.estimate_profit_egp for line in rec.activity_line_ids)
            rec.total_actual_profit = sum(line.actual_profit_egp for line in rec.activity_line_ids)

    @api.depends('activity_line_ids.estimate_cost_egp', 'activity_line_ids.actual_cost_egp',
                 'activity_line_ids.estimate_revenue_egp', 'activity_line_ids.actual_revenue_egp',
                 'activity_line_ids.estimate_profit_egp', 'activity_line_ids.actual_profit_egp')
    def _compute_totals_egp(self):
        """حساب الإجماليات بالجنيه المصري"""
        for rec in self:
            rec.estimate_cost_egp = sum(line.estimate_cost_egp for line in rec.activity_line_ids)
            rec.actual_cost_egp = sum(line.actual_cost_egp for line in rec.activity_line_ids)
            rec.estimate_revenue_egp = sum(line.estimate_revenue_egp for line in rec.activity_line_ids)
            rec.actual_revenue_egp = sum(line.actual_revenue_egp for line in rec.activity_line_ids)
            rec.estimate_profit_egp = sum(line.estimate_profit_egp for line in rec.activity_line_ids)
            rec.actual_profit_egp = sum(line.actual_profit_egp for line in rec.activity_line_ids)

    @api.depends('activity_line_ids.estimate_cost_egp', 'activity_line_ids.actual_cost_egp',
                 'activity_line_ids.estimate_revenue_egp', 'activity_line_ids.actual_revenue_egp',
                 'activity_line_ids.estimate_profit_egp', 'activity_line_ids.actual_profit_egp',
                 'usd_exchange_rate', 'eur_exchange_rate')
    def _compute_summary_egp(self):
        """Calculate summary EGP amounts based on activity lines and exchange rates"""
        for rec in self:
            # Force recomputation of all activity lines first
            for line in rec.activity_line_ids:
                line._compute_egp_amounts()
            
            # Sum all EGP amounts from activity lines (they are already converted to EGP)
            rec.summary_estimate_cost_egp = sum(rec.activity_line_ids.mapped('estimate_cost_egp'))
            rec.summary_actual_cost_egp = sum(rec.activity_line_ids.mapped('actual_cost_egp'))
            rec.summary_estimate_revenue_egp = sum(rec.activity_line_ids.mapped('estimate_revenue_egp'))
            rec.summary_actual_revenue_egp = sum(rec.activity_line_ids.mapped('actual_revenue_egp'))
            rec.summary_estimate_profit_egp = sum(rec.activity_line_ids.mapped('estimate_profit_egp'))
            rec.summary_actual_profit_egp = sum(rec.activity_line_ids.mapped('actual_profit_egp'))

    @api.depends('activity_line_ids.currency', 'currency')
    def _compute_file_currency(self):
        for rec in self:
            line_codes = [c for c in rec.activity_line_ids.mapped('currency') if c]
            if not line_codes:
                rec.file_currency = rec.currency.upper() if rec.currency else False
                continue
            # Unique, ordered by a preferred order USD, EUR, EGP then others alphabetically
            preferred_order = ['usd', 'eur', 'egp']
            unique = []
            seen = set()
            for code in line_codes:
                if code not in seen:
                    seen.add(code)
                    unique.append(code)
            unique_sorted = sorted(unique, key=lambda x: (preferred_order.index(x) if x in preferred_order else 999, x))
            rec.file_currency = ' '.join(code.upper() for code in unique_sorted)

    def _compute_egp_currency(self):
        for rec in self:
            currency = self.env['res.currency'].search([('name', '=', 'EGP')], limit=1)
            if not currency:
                currency = rec.env.company.currency_id
            rec.egp_currency_id = currency

    @api.depends('company_id')
    def _compute_company_logo(self):
        """حساب شعار الشركة"""
        for rec in self:
            if rec.company_id and rec.company_id.logo:
                rec.company_logo = rec.company_id.logo
            elif self.env.company and self.env.company.logo:
                rec.company_logo = self.env.company.logo
            else:
                rec.company_logo = False

    def _get_next_sequence(self):
        """Generate next sequence number"""
        sequence_name = 'sgl.file.cover.unified'
        
        # Get next sequence number
        sequence_number = self.env['ir.sequence'].next_by_code(sequence_name)
        if not sequence_number:
            # If sequence doesn't exist, create it
            self.env['ir.sequence'].create({
                'name': 'SGL Unified Sequence',
                'code': sequence_name,
                'prefix': 'SGL',
                'padding': 5,
                'number_next': 1,
            })
            sequence_number = self.env['ir.sequence'].next_by_code(sequence_name)
        
        return sequence_number or 'SGL00001'

    @api.model
    def create(self, vals):
        # Always generate sequence for new records, regardless of name value
        if not vals.get('name') or vals.get('name') in ['New', '/']:
            # Use a single unified sequence for all business types
            sequence_name = 'sgl.file.cover.unified'
            
            # Get next sequence number
            sequence_number = self.env['ir.sequence'].next_by_code(sequence_name)
            if not sequence_number:
                # If sequence doesn't exist, create it
                self.env['ir.sequence'].create({
                    'name': 'SGL Unified Sequence',
                    'code': sequence_name,
                    'prefix': 'SGL',
                    'padding': 5,
                    'number_next': 1,
                })
                sequence_number = self.env['ir.sequence'].next_by_code(sequence_name)
            
            vals['name'] = sequence_number
            
        # Populate customer-related fields if a customer was selected
        partner_id = vals.get('eg_customer_name')
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            vals.setdefault('customer_full_address', partner.contact_address or '')
            vals.setdefault('customer_cr_no', partner.ref or '')
            vals.setdefault('customer_tax_no', partner.vat or '')

        return super().create(vals)



    def write(self, vals):
        """Override write to persist customer details"""
        # If customer changed, persist related readonly fields as well
        if 'eg_customer_name' in vals and vals['eg_customer_name']:
            partner = self.env['res.partner'].browse(vals['eg_customer_name'])
            # Copy to avoid mutating caller's dict
            vals = dict(vals)
            vals.update({
                'customer_full_address': partner.contact_address or '',
                'customer_cr_no': partner.ref or '',
                'customer_tax_no': partner.vat or '',
            })

        return super().write(vals)

    def action_create_vendor_bill(self):
        for rec in self:
            if not rec.activity_line_ids:
                raise UserError("No activity lines found to create invoice.")

            # Check if vendor bills already exist for this file cover
            existing_bills = self.env['account.move'].search([
                ('move_type', '=', 'in_invoice'),
                ('ref', 'ilike', f"{rec.name}-")
            ])
            
            # Generate unique reference number for this vendor bill
            if existing_bills:
                bill_sequence = len(existing_bills) + 1
                base_ref = f"{rec.name}-VB{bill_sequence:02d}"
            else:
                base_ref = f"{rec.name}-VB01"

            # اجمع البنود حسب اسم المورد والعملة
            vendor_currency_map = {}
            for line in rec.activity_line_ids:
                if not line.vendor_name:
                    continue
                key = (line.vendor_name, line.currency)
                vendor_currency_map.setdefault(key, []).append(line)

            if not vendor_currency_map:
                raise UserError("Vendor name must be specified in each activity line.")

            invoices = []
            base_invoice_number = None
            all_invoice_numbers = []
            
            for (vendor, currency), lines in vendor_currency_map.items():
                invoice_lines = []
                for line in lines:
                    invoice_lines.append((0, 0, {
                        'name': line.activity_type or 'Service',
                        'quantity': line.quantity or 1.0,
                        'price_unit': line.price_unit or 0.0,
                    }))
                
                # البحث عن المورد في res.partner أو استخدامه مباشرة إذا كان Many2one
                partner = vendor if getattr(vendor, 'id', False) else self.env['res.partner'].search([('name', '=', vendor)], limit=1)
                if not partner:
                    partner = self.env['res.partner'].create({
                        'name': vendor if not getattr(vendor, 'name', False) else vendor.name,
                        'supplier_rank': 1,
                    })
                
                # الحصول على العملة من res.currency
                currency_record = self.env['res.currency'].search([('name', '=', currency.upper())], limit=1)
                if not currency_record:
                    # إذا لم توجد العملة، استخدم العملة الافتراضية
                    currency_record = self.env.company.currency_id
                
                # إنشاء الفاتورة
                invoice = self.env['account.move'].create({
                    'move_type': 'in_invoice',
                    'partner_id': partner.id,
                    'currency_id': currency_record.id,  # تحديد العملة
                    'invoice_line_ids': invoice_lines,
                    'ref': f"{base_ref}-{currency.upper()}",  # ربط الفاتورة برقم Job-File والعملة مع رقم تسلسلي
                })
                
                # حفظ رقم الفاتورة الأساسي (الأولى) لربط باقي الفواتير
                if base_invoice_number is None:
                    base_invoice_number = invoice.name
                
                # إضافة رقم الفاتورة إلى القائمة
                all_invoice_numbers.append(f"{invoice.name} ({currency.upper()})")
                
                # تحديث رقم الفاتورة في Activity Lines مع إضافة العملة
                for line in lines:
                    line.write({'vendor_invoice': f"{invoice.name} ({currency.upper()})"})
                invoices.append(invoice.id)
                
                # إجبار تحديث الواجهة
                rec.activity_line_ids.invalidate_cache(['vendor_invoice'])
                rec.invalidate_cache(['activity_line_ids'])

            # عرض رسالة تأكيد
            currency_count = len(set(currency for _, currency in vendor_currency_map.keys()))
            vendor_count = len(set(vendor for vendor, _ in vendor_currency_map.keys()))
            message = f"Successfully created {len(invoices)} vendor bill(s) for {vendor_count} vendor(s) with {currency_count} different currency(ies)."
            
            # تحديث رقم الفاتورة في السجل الرئيسي (رقم الفاتورة الأساسي)
            if invoices:
                rec.write({
                    'invoice_number': base_invoice_number,
                    'all_invoice_numbers': '\n'.join(all_invoice_numbers)
                })
                rec.invalidate_cache(['invoice_number', 'all_invoice_numbers'])
                
                # إجبار حفظ التغييرات
                self.env.cr.commit()
            
            # عرض أول فاتورة تم إنشاؤها
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': invoices[0] if invoices else False,
                'context': {'default_move_type': 'in_invoice'},
            }

    def action_create_customer_invoice(self):
        for rec in self:
            if not rec.activity_line_ids:
                raise UserError("No activity lines found to create customer invoice.")

            # Ensure a customer is selected
            if not rec.eg_customer_name:
                raise UserError("Please select a customer before creating a customer invoice.")

            # Check if customer invoices already exist for this specific file cover and customer
            existing_cust_invoices = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('partner_id', '=', rec.eg_customer_name.id),
                ('ref', 'ilike', f"{rec.name}-")
            ])
            
            # Allow creating new invoices but with different reference numbers
            if existing_cust_invoices:
                # Generate a sequence number for multiple invoices
                invoice_sequence = len(existing_cust_invoices) + 1
                base_ref = f"{rec.name}-INV{invoice_sequence:02d}"
            else:
                base_ref = f"{rec.name}"

            # اجمع البنود حسب العملة
            currency_map = {}
            for line in rec.activity_line_ids:
                if line.estimate_revenue > 0:  # فقط البنود التي لها إيرادات
                    currency_map.setdefault(line.currency, []).append(line)

            if not currency_map:
                raise UserError("No activity lines with revenue found to create customer invoice.")

            invoices = []
            base_invoice_number = None
            all_invoice_numbers = []

            for currency, lines in currency_map.items():
                invoice_lines = []
                for line in lines:
                    invoice_lines.append((0, 0, {
                        'name': line.activity_type or 'Service',
                        'quantity': line.quantity or 1.0,
                        'price_unit': line.estimate_revenue / (line.quantity or 1.0),
                    }))

                # Use the selected customer directly
                customer = rec.eg_customer_name

                # الحصول على العملة من res.currency
                currency_record = self.env['res.currency'].search([('name', '=', currency.upper())], limit=1)
                if not currency_record:
                    # إذا لم توجد العملة، استخدم العملة الافتراضية
                    currency_record = self.env.company.currency_id
                
                # إنشاء فاتورة العميل لكل عملة
                customer_invoice = self.env['account.move'].create({
                    'move_type': 'out_invoice',
                    'partner_id': customer.id,
                    'currency_id': currency_record.id,  # تحديد العملة
                    'invoice_line_ids': invoice_lines,
                    'ref': f"{base_ref}-{currency.upper()}",  # ربط الفاتورة برقم Job-File والعملة مع رقم تسلسلي
                })

                # حفظ رقم الفاتورة الأساسي (الأولى) لربط باقي الفواتير
                if base_invoice_number is None:
                    base_invoice_number = customer_invoice.name

                # إضافة رقم الفاتورة إلى القائمة
                all_invoice_numbers.append(f"{customer_invoice.name} ({currency.upper()})")

                invoices.append(customer_invoice.id)

            # تحديث رقم فاتورة العميل في السجل الرئيسي (رقم الفاتورة الأساسي)
            if invoices:
                rec.write({
                    'invoice_number': base_invoice_number,
                    'all_invoice_numbers': '\n'.join(all_invoice_numbers)
                })
                rec.invalidate_cache(['invoice_number', 'all_invoice_numbers'])
                
                # إجبار حفظ التغييرات
                self.env.cr.commit()

            # عرض رسالة تأكيد
            currency_count = len(currency_map)
            message = f"Successfully created {len(invoices)} customer invoice(s) with {currency_count} different currency(ies)."

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': invoices[0] if invoices else False,
                'context': {'default_move_type': 'out_invoice'},
            }

    def action_open_activity_column_wizard(self):
        view = self.env.ref('SGL.view_sgl_file_cover_activity_column_wizard_form')
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sgl.file.cover.activity.column.wizard',
            'view_mode': 'form',
            'target': 'new',
            'view_id': view.id,
            'views': [(view.id, 'form')],
        }