from odoo import models, fields


class Tenant(models.Model):
    _inherit = "tenant.details"

    sale_order_id_website = fields.Many2one(
        'sale.order'
    )
