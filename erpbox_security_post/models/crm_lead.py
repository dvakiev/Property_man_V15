from odoo import models, fields


class Lead(models.Model):
    _inherit = "crm.lead"

    security_post_id = fields.Many2one(
        related="partner_id.security_post_id",
        store=True,
    )