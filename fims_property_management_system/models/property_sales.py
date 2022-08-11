# -*- coding: utf-8 -*-
###############################################################################
#
# Fortutech IMS Pvt. Ltd.
# Copyright (C) 2016-TODAY Fortutech IMS Pvt. Ltd.(<http://www.fortutechims.com>).
#
###############################################################################

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class PropertySales(models.Model):
    _name = "property.sales"
    _description = "Property Sales"
    _inherit = ['mail.thread']
    _rec_name = 'name'

    name = fields.Char(string="Name")
    owner_id = fields.Many2one('res.partner', string="Property Owner")
    buyer_id = fields.Many2one('res.partner', string="Property Buyer")
    property_id = fields.Many2one('property.details', string="Property")
    property_cost = fields.Monetary(string="Property Cost", related="property_id.property_value")
    date = fields.Date(string="Date")
    currency_id = fields.Many2one("res.currency", string="Currency", related="property_id.currency_id")
    invoice_id = fields.Many2one('account.move', string="Invoice")
    deal_amount = fields.Monetary(string="Deal Amount")
    state = fields.Selection([('new', 'New'), ('in_progress', 'In Progress'), ('sold', 'Sold')], 'State', default="new",
                             track_visibility='always')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('property.sales')
        res = super(PropertySales, self).create(vals)
        return res

    def action_in_progress(self):
        self.state = 'in_progress'

    def action_closed(self):
        self.state = 'sold'
        self.property_id.state = 'sold'

    def create_invoice(self):
        action = self.env.ref('account.action_move_in_invoice_type')
        result = action.read()[0]
        other_account = self.env['ir.property']._get('property_account_expense_categ_id', 'product.category')
        if self.deal_amount == 0:
            amount = self.property_cost
        else:
            amount = self.deal_amount
        result['context'] = {
            'default_move_type': 'out_invoice',
            'default_partner_id': self.buyer_id.id,
            'default_invoice_date': self.date,
            'default_line_ids': [(0, 0, {
                'name': self.property_id.name + " : " + self.property_id.code,
                'account_id': other_account and other_account.id or False,
                'price_unit': amount,
                'quantity': 1,
                'exclude_from_invoice_tab': False,
            })],
        }
        res = self.env.ref('account.view_move_form', False)
        form_view = [(res and res.id or False, 'form')]
        if 'views' in result:
            result['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        result['context']['from_property_sales'] = True
        return result

    def view_invoice(self):
        if self.invoice_id:
            invoices = self.mapped('invoice_id')
            action = self.env.ref('account.action_move_out_invoice_type').read()[0]
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
            return action
        else:
            raise UserError(_("There is not invoice created yet...!"))
