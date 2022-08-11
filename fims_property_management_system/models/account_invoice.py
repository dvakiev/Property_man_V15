# -*- coding: utf-8 -*-
###############################################################################
#
#    Fortutech IMS Pvt. Ltd.
#    Copyright (C) 2016-TODAY Fortutech IMS Pvt. Ltd.(<http://www.fortutechims.com>).
#
###############################################################################
from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    
    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        if self._context.get('from_rent_details'):
            rent_line = self.env['rent.details'].browse(self._context.get('active_id'))
            rent_line.invoice_id = res.id
        if self._context.get('from_property_sales'):
            prop_sales = self.env['property.sales'].browse(self._context.get('active_id'))
            prop_sales.invoice_id = res.id
        return res