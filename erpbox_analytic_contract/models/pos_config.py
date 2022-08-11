from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    pos_account_id = fields.Many2one(
        'account.account', string="Account",
        help='Whenever you close a session, one entry is generated in the following accounting id for all the orders not invoiced. Invoices are recorded in accounting separately.')
