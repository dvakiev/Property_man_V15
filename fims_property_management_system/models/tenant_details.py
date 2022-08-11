# -*- coding: utf-8 -*-
###############################################################################
#
# Fortutech IMS Pvt. Ltd.
# Copyright (C) 2016-TODAY Fortutech IMS Pvt. Ltd.(<http://www.fortutechims.com>).
#
###############################################################################

from odoo import fields, models, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning


class TenantDetails(models.Model):
    _name = "tenant.details"
    _description = "Tenant"
    _inherit = ['mail.thread']
    _rec_name = 'name'

    @api.depends('start_date', 'end_date', 'rent_type', 'rent')
    def compute_total_rent(self):
        if self.start_date and self.end_date and self.rent_type and self.rent > 0:
            month_diff = (self.end_date.year - self.start_date.year) * 12 + self.end_date.month - self.start_date.month
            if self.rent_type == 'quarterly':
                month_diff = int(month_diff / 3)
            if self.rent_type == 'semi_annual':
                month_diff = int(month_diff / 6)
            if self.rent_type == 'annual':
                month_diff = int(month_diff / 12)

            if month_diff > 0:
                self.total_rent = month_diff * self.rent
            else:
                self.total_rent = 0.0
        else:
            self.total_rent = 0.0

    name = fields.Char(string="Name", copy=False)
    code = fields.Char(string="Code", copy=False)
    state = fields.Selection([('new', 'New'), ('in_progress', 'In Progress'), ('closed', 'Closed')], 'State',
                             default="new", track_visibility='always')
    property_id = fields.Many2one('property.details', string="Property", copy=False, track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string="Tenant", copy=False, track_visibility='onchange')
    currency_id = fields.Many2one("res.currency", string="Currency", required=True)
    rent = fields.Float(string="Tenant Rent", copy=False, track_visibility='onchange')
    total_rent = fields.Float(string="Total Rent", compute='compute_total_rent')
    deposit = fields.Float(string="Deposit", copy=False)
    deposit_return = fields.Float(string="Deposit Return", copy=False)
    is_deposit_received = fields.Boolean(string="Deposit Received ?", copy=False)
    is_deposit_returned = fields.Boolean(string="Deposit Returned ?", copy=False)
    start_date = fields.Date(string="Start Date", copy=False)
    end_date = fields.Date(string="End Date", copy=False)
    rent_type = fields.Selection(
        [('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('semi_annual', 'Semi-Annual'), ('annual', 'Annual')],
        string='Rent Type', default="monthly", track_visibility='onchange')
    note = fields.Text(string="Note", copy=False)
    rent_details_ids = fields.One2many('rent.details', 'tenant_id', string="Rent Details")
    invoice_counter = fields.Integer(compute='compute_invoice_counter')

    @api.depends()
    def compute_invoice_counter(self):
        self.invoice_counter = len(self.rent_details_ids.mapped('invoice_id'))

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('tenant.details')
        res = super(TenantDetails, self).create(vals)
        return res

    def tenant_in_progress(self):
        self.state = 'in_progress'

    def tenant_closed(self):
        self.state = 'closed'

    def compute_rent(self):
        if self.rent > 0:
            if self.rent_details_ids:
                for rent_detail_id in self.rent_details_ids:
                    if rent_detail_id.state == 'unpaid':
                        rent_detail_id.unlink()

            month_diff = (self.end_date.year - self.start_date.year) * 12 + self.end_date.month - self.start_date.month
            tmp = 1
            if self.rent_type == 'quarterly':
                month_diff = int(month_diff / 3)
            if self.rent_type == 'semi_annual':
                month_diff = int(month_diff / 6)
            if self.rent_type == 'annual':
                month_diff = int(month_diff / 12)

            rent_details = []
            add_month = 0
            for m in range(month_diff):
                if self.rent_type == 'monthly':
                    add_month += 1
                if self.rent_type == 'quarterly':
                    add_month += 3
                if self.rent_type == 'semi_annual':
                    add_month += 6
                if self.rent_type == 'annual':
                    add_month += 12

                rent_details.append((0, 0, {'date': self.start_date + relativedelta(months=add_month),
                                            'rent_amount': self.rent}))

            if rent_details:
                self.rent_details_ids = rent_details

    def view_invoice(self):
        invoices = self.rent_details_ids.mapped('invoice_id')
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        action['views'] = [(self.env.ref('account.view_invoice_tree').id, 'tree'),
                           (self.env.ref('account.view_move_form').id, 'form')]
        action['domain'] = [('id', 'in', invoices.ids)]
        return action


class RentDetails(models.Model):
    _name = "rent.details"

    date = fields.Date(string="Date")
    rent_amount = fields.Float(string="Rent Amount")
    remaining_amount = fields.Float(string="Remaining Amount")
    note = fields.Char(string="Note")
    state = fields.Selection([('unpaid', 'Unpaid'), ('paid', 'Paid')], 'State', default="unpaid")
    tenant_id = fields.Many2one('tenant.details', string="Tenant")
    currency_id = fields.Many2one("res.currency", string="Currency", related='tenant_id.currency_id')
    invoice_id = fields.Many2one('account.move', string="Invoice")

    def create_new_invoice(self):
        action = self.env.ref('account.action_move_in_invoice_type')
        result = action.read()[0]
        other_account = self.env['ir.property']._get('property_account_expense_categ_id', 'product.category')
        result['context'] = {
            'default_move_type': 'out_invoice',
            'default_partner_id': self.tenant_id.partner_id.id,
            'default_invoice_date': fields.Date.today(),
            'default_line_ids': [(0, 0, {
                'name': self.tenant_id.code + " Rent for : " + str(self.date),
                'account_id': other_account and other_account.id or False,
                'price_unit': self.rent_amount,
                'quantity': 1,
                'exclude_from_invoice_tab': False,
            })],
        }
        res = self.env.ref('account.view_move_form', False)
        form_view = [(res and res.id or False, 'form')]
        if 'views' in result:
            result['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        self.state = 'paid'
        result['context']['from_rent_details'] = True
        return result

    def view_invoice(self):
        invoices = self.mapped('invoice_id')
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
        action['res_id'] = invoices.ids[0]
        return action
