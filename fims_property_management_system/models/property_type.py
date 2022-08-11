# -*- coding: utf-8 -*-
###############################################################################
#
# Fortutech IMS Pvt. Ltd.
# Copyright (C) 2016-TODAY Fortutech IMS Pvt. Ltd.(<http://www.fortutechims.com>).
#
###############################################################################

from odoo import fields, models


class PropertyType(models.Model):
    _name = "property.type"
    _description = "Property Type"
    _rec_name = 'name'

    name = fields.Char(string="Name", copy=False)
