from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    erpbox_car_ids = fields.One2many('erpbox.car.partner.car.with.state.number', 'partner_id')
