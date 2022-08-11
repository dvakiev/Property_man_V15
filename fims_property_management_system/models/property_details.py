# -*- coding: utf-8 -*-
###############################################################################
#
# Fortutech IMS Pvt. Ltd.
# Copyright (C) 2016-TODAY Fortutech IMS Pvt. Ltd.(<http://www.fortutechims.com>).
#
###############################################################################

from odoo import fields, models, api, _


class PropertyDetails(models.Model):
    _name = "property.details"
    _description = "Property"
    _inherit = ['mail.thread']
    _rec_name = 'name'

    name = fields.Char(string="Name", copy=False)
    code = fields.Char(string="Code", copy=False)
    image = fields.Binary(string="Image", copy=False)
    state = fields.Selection([('new', 'New'), ('booked', 'Booked'),
                              ('available', 'Available'), ('on_lease', 'On Lease'), ('sold', 'Sold')], 'State',
                             default="new", track_visibility='always')
    street = fields.Char(string="Street", copy=False)
    city = fields.Char(string="City", copy=False)
    state_id = fields.Many2one('res.country.state', string="State", copy=False)
    zip = fields.Char(string="Zip", copy=False)
    country_id = fields.Many2one('res.country', string="Country", copy=False)
    date = fields.Date(string="Date", copy=False)
    no_of_building = fields.Integer(string="No of Building", copy=False)
    name_of_area = fields.Char(string="Name of Area", copy=False)
    active = fields.Boolean('Active', default=True, copy=False,
                            help="If unchecked, it will allow you to hide the property without removing it.")
    furnishing = fields.Selection([('not_furnished', 'Not Furnished'), ('semi_furnished', 'Semi Furnished'),
                                   ('full_furnished', 'Full Furnished')], string='Furnishing', default="not_furnished",
                                  track_visibility='always')
    property_type_id = fields.Many2one('property.type', string="Property Type", copy=False)
    user_id = fields.Many2one('res.users', string="Property Manager", copy=False)
    facing = fields.Char(string="Facing", copy=False)
    bedrooms = fields.Integer(string="Bedrooms", copy=False)
    bathrooms = fields.Integer(string="Bathrooms", copy=False)
    carpet_area = fields.Char(string="Carpet Area (Sqft)", copy=False)
    video_url = fields.Char(string="Video URL", copy=False)
    note = fields.Text(string="Note", copy=False)
    currency_id = fields.Many2one("res.currency", string="Currency", required=True)
    property_value = fields.Monetary(string="Property Value", copy=False)
    image_ids = fields.One2many('property.images', 'property_id', string="Images")

    def property_book(self):
        self.state = 'booked'

    def property_available(self):
        self.state = 'available'

    def property_on_lease(self):
        self.state = 'on_lease'

    def property_sold(self):
        self.state = 'sold'

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('property.details')
        res = super(PropertyDetails, self).create(vals)
        return res
