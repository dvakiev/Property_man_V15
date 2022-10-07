from odoo import models, fields, _


class CarWithStateNumber(models.Model):
    _name = 'erpbox.car.partner.car.with.state.number'
    _description = 'Car With State Number'
    _rec_name = 'state_number_id'

    partner_id = fields.Many2one('res.partner', required=True)
    state_number_id = fields.Many2one('erpbox.car.partner.car.state.number', required=True)
    brand_id = fields.Many2one('product.brand', required=True)
    model_id = fields.Many2one('catalog.auto.model', required=True)
    vin_ids = fields.One2many(related='model_id.vin_ids')
    vin_id = fields.Many2one('catalog.auto.vin')
    engine_code_id = fields.Many2one('catalog.auto.engine.code')
    color_id = fields.Many2one('catalog.auto.color')
    mileage = fields.Char()

    _sql_constraints = [(
        'partner_state_number_uniq', 'unique (partner_id, state_number_id)',
        _('Combination of state number and partner must be unique!')
    )]
