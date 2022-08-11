from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    origin_id = fields.Reference(
        lambda self: [(m.model, m.name) for m in self.env["ir.model"].search([])],
        string="Origin object",
    )
