# -*- coding: utf-8 -*-
###############################################################################
#
# Fortutech IMS Pvt. Ltd.
# Copyright (C) 2016-TODAY Fortutech IMS Pvt. Ltd.(<http://www.fortutechims.com>).
#
###############################################################################

from odoo import fields, models


class PropertyImages(models.Model):
    _name = "property.images"
    _description = "Property Images"

    image = fields.Binary("Image", required=True)
    property_id = fields.Many2one('property.details', string="Property")
