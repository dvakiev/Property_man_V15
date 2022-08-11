# -*- coding: utf-8 -*-
###############################################################################
#
# Fortutech IMS Pvt. Ltd.
# Copyright (C) 2016-TODAY Fortutech IMS Pvt. Ltd.(<http://www.fortutechims.com>).
#
###############################################################################

from odoo import fields, models, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    tenant_details_ids = fields.One2many('tenant.details', 'partner_id', string="Tenant Details")
