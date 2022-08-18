from odoo import models, fields


class RentDetails(models.Model):
    _inherit = "rent.details"

    payment_state = fields.Selection(
        related="invoice_id.payment_state",
        store=True,
    )
