from odoo import models, fields, _


class StateNumber(models.Model):
    _name = 'erpbox.car.partner.car.state.number'
    _description = 'Car State Number'

    name = fields.Char()

    _sql_constraints = [
        ('name_uniq', 'unique (name)', _('State number must be unique!'))
    ]
