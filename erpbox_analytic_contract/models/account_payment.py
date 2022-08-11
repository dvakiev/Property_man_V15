from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    contract_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Contract'
    )

